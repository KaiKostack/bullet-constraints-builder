##############################
# Bullet Constraints Builder #
##############################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# This version is developed at the Laurea University of Applied Sciences, Finland
# Copyright (C) 2015-2017 Kai Kostack
#
# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

################################################################################

import bpy, mathutils, sys, math
from mathutils import Vector
from math import *
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

def initGeneralRigidBodyWorldSettings(scene):

    ### Set general rigid body world settings
    props = bpy.context.window_manager.bcb
    # Set FPS rate for rigid body simulation (from Blender preset)
    scene.render.fps = 25
    scene.render.fps_base = 1
    # Set Steps Per Second for rigid body simulation
    scene.rigidbody_world.steps_per_second = props.stepsPerSecond
    # Set Split Impulse for rigid body simulation
    #scene.rigidbody_world.use_split_impulse = True

################################################################################   

def createElementGroupIndex(objs):

    ### Create a list about which object belongs to which element group
    elemGrps = mem["elemGrps"]
    objsEGrp = []
    cnt = 0
    for obj in objs:
        objGrpsTmp = []
        for elemGrp in elemGrps:
            elemGrpName = elemGrp[EGSidxName]
            if elemGrpName in bpy.data.groups:
                if obj != None:
                    try: bpy.data.groups[elemGrpName].objects[obj.name]
                    except: pass
                    else: objGrpsTmp.append(elemGrps.index(elemGrp))
        if len(objGrpsTmp) > 1:
            sys.stdout.write("Warning: Object %s belongs to more than one element group, defaults are used. Element groups:" %obj.name)
            for idx in objGrpsTmp: sys.stdout.write(" #%d %s" %(idx, elemGrps[idx][EGSidxName]))
            print()
            q = 1
        elif len(objGrpsTmp) == 0: q = 1
        else: q = 0
        ### If selected object is not part of any scene group try to find an element group with empty name to use (default group)
        if q:
            for elemGrp in elemGrps:
                elemGrpName = elemGrp[EGSidxName]
                if elemGrpName == '':
                    objGrpsTmp = [elemGrps.index(elemGrp)]
                    break
        # If empty name is found assign object to it
        if len(objGrpsTmp) > 0:
              objsEGrp.append(objGrpsTmp[0])
              cnt += 1
        # If not even a default group is available then use element group 0 as fallback
        # (Todo: flag the group as -1 and deal with it later, but that's also complex)
        else: objsEGrp.append(0)

    return objsEGrp, cnt

########################################

def gatherObjects(scene):

    ### Create object lists of selected objects
    print("Creating object lists of selected objects...")
    
    objs = []
    emptyObjs = []
    for obj in scene.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            # Clear object properties
            #for key in obj.keys(): del obj[key]
            # Detect if mesh or empty (constraint)
            if obj.type == 'MESH' and obj.rigid_body != None and len(obj.data.vertices) > 0:
                objs.append(obj)
            elif obj.type == 'EMPTY' and obj.rigid_body_constraint != None:
                sys.stdout.write('\r' +"%s      " %obj.name)
                emptyObjs.append(obj)
    
    return objs, emptyObjs

################################################################################   

def prepareObjects(objs):

    ### Prepare objects (make unique, apply transforms etc.)
    # Select objects
    for obj in objs: obj.select = 1
    # Remove instancing from objects
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True, material=False, texture=False, animation=False)
    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ### Apply scale factor depending on object's collision shape to make sure volume and mass calculation are correct (not all need this)
    for obj in objs:
        if obj.rigid_body != None:
            if obj.rigid_body.collision_shape == 'CONVEX_HULL' or obj.rigid_body.collision_shape == 'MESH':  # Not needed: SPHERE, CAPSULE, CYLINDER, CONE
                obj["Scale"] = obj.scale  # Backup original scale
                obj.select = 1
            else:
                obj.select = 0
        else:
            # Add rigid body status if not already present
            bpy.context.scene.objects.active = obj
            bpy.ops.rigidbody.object_add()
            obj.select = 1
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

################################################################################   

def boundaryBox(obj, qGlobalSpace):

    ### Calculate boundary box corners and center from given object
    me = obj.data
    verts = me.vertices
    if qGlobalSpace:
        # Multiply local coordinates by world matrix to get global coordinates
        mat = obj.matrix_world
        bbMin = mat *verts[0].co
        bbMax = mat *verts[0].co
    else:
        bbMin = verts[0].co.copy()
        bbMax = verts[0].co.copy()
    for vert in verts:
        if qGlobalSpace: loc = mat *vert.co
        else:            loc = vert.co.copy()
        if bbMax[0] < loc[0]: bbMax[0] = loc[0]
        if bbMin[0] > loc[0]: bbMin[0] = loc[0]
        if bbMax[1] < loc[1]: bbMax[1] = loc[1]
        if bbMin[1] > loc[1]: bbMin[1] = loc[1]
        if bbMax[2] < loc[2]: bbMax[2] = loc[2]
        if bbMin[2] > loc[2]: bbMin[2] = loc[2]
    bbCenter = (bbMin +bbMax) /2
    
    return bbMin, bbMax, bbCenter

################################################################################   

def findConnectionsByVertexPairs(objs, objsEGrp):
    
    ### Find connections by vertex pairs
    print("Searching connections by vertex pairs... (%d)" %len(objs))
    
    props = bpy.context.window_manager.bcb
    elemGrps = mem["elemGrps"]

    ### Build kd-tree for object locations
    kdObjs = mathutils.kdtree.KDTree(len(objs))
    for i, obj in enumerate(objs):
        kdObjs.insert(obj.location, i)
    kdObjs.balance()
    
    ### Build kd-trees for every object's vertices
    kdsMeComp = []
    for obj in objs:
        me = obj.data
        mat = obj.matrix_world
        
        kd = mathutils.kdtree.KDTree(len(me.vertices))
        for i, v in enumerate(me.vertices):
            loc = mat *v.co    # Multiply matrix by vertex coordinates to get global coordinates
            kd.insert(loc, i)
        kd.balance()
        kdsMeComp.append(kd)
                        
    ### Find connections by vertex pairs
    connectsPair = []          # Stores both connected objects indices per connection
    connectsPairDist = []      # Stores distance between both elements
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        qNextObj = 0
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []; aDist = [] #; aCo = [] 
        if props.connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, props.connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index); aDist.append(dist) #; aCo.append(co)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index); aDist.append(dist) #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:] # Remove first item because it's the same as co_find (zero distance)
        
        ### Walk through current object vertices
        for m in range(len(me.vertices)):
            vert = me.vertices[m]
            co_find = mat *vert.co     # Multiply matrix by vertex coordinates to get global coordinates
                        
            # Loop through comparison object found
            for j in range(len(aIndex)):
                l = aIndex[j]
                
                # Skip same object index
                if k != l:
                    # Use object specific vertex kd-tree
                    kdMeComp = kdsMeComp[l]
                    
                    ### Find closest vertices via kd-tree in comparison object
                    if len(kdMeComp.find_range(co_find, props.searchDistance)) > 0:   # If vert is within search range add connection to sublist
                        coComp = kdMeComp.find(co_find)[0]    # Find coordinates of the closest vertex
                        co = (co_find +coComp) /2             # Calculate center of both vertices
                        
                        ### Store connection if not already existing
                        connectCnt = 0
                        pair = [k, l]
                        pair.sort()
                        if pair not in connectsPair:
                            connectsPair.append(pair)
                            connectsPairDist.append(aDist[j])
                            connectCnt += 1
                            if connectCnt == props.connectionCountLimit:
                                if elemGrps[objsEGrp[k]][EGSidxRqVP] <= 1:
                                    qNextObj = 1
                                    break
                            
            if qNextObj: break
        
    print()
    return connectsPair, connectsPairDist

################################################################################   

def findConnectionsByBoundaryBoxIntersection(objs):
    
    ### Find connections by boundary box intersection
    print("Searching connections by boundary box intersection... (%d)" %len(objs))
    
    props = bpy.context.window_manager.bcb
    
    ### Build kd-tree for object locations
    kdObjs = mathutils.kdtree.KDTree(len(objs))
    for i, obj in enumerate(objs):
        kdObjs.insert(obj.location, i)
    kdObjs.balance()
    
    ### Precalculate boundary boxes for all objects
    bboxes = []
    for obj in objs:
        # Calculate boundary box corners
        bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
        # Extend boundary box dimensions by searchDistance
        searchDistanceHalf = props.searchDistance /2
        bbMin -= Vector((searchDistanceHalf, searchDistanceHalf, searchDistanceHalf))
        bbMax += Vector((searchDistanceHalf, searchDistanceHalf, searchDistanceHalf))
        bboxes.append([bbMin, bbMax])
    
    ### Find connections by intersecting boundary boxes
    connectsPair = []          # Stores both connected objects indices per connection
    connectsPairDist = []      # Stores distance between both elements
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []; aDist = [] #; aCo = [] 
        if props.connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, props.connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index); aDist.append(dist) #; aCo.append(co)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index); aDist.append(dist) #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:]  # Remove first item because it's the same as co_find (zero distance)
    
        # Loop through comparison objects found
        for j in range(len(aIndex)):
            l = aIndex[j]
            
            # Skip same object index
            if k != l:
                bbAMin, bbAMax = bboxes[k]
                bbBMin, bbBMax = bboxes[l]
                ### Calculate overlap per axis of both intersecting boundary boxes
                overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
                overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
                overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
                # Calculate volume
                volume = overlapX *overlapY *overlapZ
                if volume > 0:                
                    ### Store connection if not already existing
                    connectCnt = 0
                    pair = [k, l]
                    pair.sort()
                    if pair not in connectsPair:
                        connectsPair.append(pair)
                        connectsPairDist.append(aDist[j])
                        connectCnt += 1
                        if connectCnt == props.connectionCountLimit: break
    
    print("\nPossible connections found:", len(connectsPair))
    return connectsPair, connectsPairDist

################################################################################   

def deleteConnectionsWithTooSmallElementsAndParentThemInstead(objs, connectsPair, connectsPairDist):
    
    ### Delete connections whose elements are too small and make them parents instead
    print("Make parents for too small elements and remove them as connections...")
    
    props = bpy.context.window_manager.bcb
    connectsPairTmp = []
    connectsPairParent = []
    connectsPairParentDist = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for k in range(len(connectsPair)):
        objA_idx = connectsPair[k][0]
        objB_idx = connectsPair[k][1]
        dist = connectsPairDist[k]
        objA = objs[objA_idx]
        objB = objs[objB_idx]
        objA_dim = list(objA.dimensions)
        objA_dim.sort()
        objA_dim = objA_dim[2]   # Use largest dimension axis as size
        objB_dim = list(objB.dimensions)
        objB_dim.sort()
        objB_dim = objB_dim[2]   # Use largest dimension axis as size
        if (objA_dim > props.minimumElementSize and objB_dim > props.minimumElementSize) \
        or (objA_dim <= props.minimumElementSize and objB_dim <= props.minimumElementSize):
            connectsPairTmp.append(connectsPair[k])
            connectCnt += 1
        elif objA_dim <= props.minimumElementSize:
            connectsPairParent.append([objA_idx, objB_idx])  # First child, second parent
            connectsPairParentDist.append(dist)
        elif objB_dim <= props.minimumElementSize:
            connectsPairParent.append([objB_idx, objA_idx])  # First child, second parent
            connectsPairParentDist.append(dist)
    connectsPair = connectsPairTmp
    
    # Sort list into the order of distance between elements
    if len(connectsPairParent) > 1:
        connectsPairParentDist, connectsPairParent = zip(*sorted(zip(connectsPairParentDist, connectsPairParent)))
    
    ### Filter out children doubles because each children can only have one parent, other connections are discarded
    checkList = []
    connectsPairParentTmp = []
    for item in connectsPairParent:
        if item[0] not in checkList:
            connectsPairParentTmp.append(item)
            checkList.append(item[0])
    connectsPairParent = connectsPairParentTmp
    
    print("Connections converted and removed:", len(connectsPairParent))
    return connectsPair, connectsPairParent

################################################################################   

def makeParentsForTooSmallElementsReal(objs, connectsPairParent):
    
    ### Create actual parents for too small elements
    print("Creating actual parents for too small elements... (%d)" %len(connectsPairParent))
    
    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    objCameras = []
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            sceneTemp.objects.link(objTemp)
            objCameras.append(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    ### Make parents
    for k in range(len(connectsPairParent)):
        sys.stdout.write('\r' +"%d" %k)
        
        objChild = objs[connectsPairParent[k][0]]
        objParent = objs[connectsPairParent[k][1]]

        # Link objects we're working on to second scene (we try because of the object unlink workaround)
        try: sceneTemp.objects.link(objChild)
        except: pass
        try: sceneTemp.objects.link(objParent)
        except: pass

        ### Make parent
        objParent.select = 1
        objChild.select = 1
        bpy.context.scene.objects.active = objParent   # Parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        objParent.select = 0
        objChild.select = 0

#        # Unlink objects from second scene (leads to loss of rigid body settings, bug in Blender)
#        sceneTemp.objects.unlink(objChild)
#        sceneTemp.objects.unlink(objParent)
        # Workaround: Delete second scene and recreate it (deleting objects indirectly without the loss of rigid body settings)
        if k %200 == 0:   # Only delete scene every now and then so we have lower overhead from the relatively slow process
            try:    bpy.data.scenes.remove(sceneTemp, do_unlink=1)
            except: bpy.data.scenes.remove(sceneTemp)
            sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
            # Link cameras because in second scene is none and when coming back camera view will losing focus
            for obj in objCameras:
                sceneTemp.objects.link(obj)
            # Switch to new scene
            bpy.context.screen.scene = sceneTemp
    
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    try:    bpy.data.scenes.remove(sceneTemp, do_unlink=1)
    except: bpy.data.scenes.remove(sceneTemp)

    ### Remove child object from rigid body world (should not be simulated anymore)
    for k in range(len(connectsPairParent)):
        objChild = objs[connectsPairParent[k][0]].select = 1
    bpy.ops.rigidbody.objects_remove()
        
    print()

################################################################################   

def deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair):
    
    ### Delete connections with too few connected vertices
    if debug: print("Deleting connections with too few connected vertices...")
    
    elemGrps = mem["elemGrps"]
    connectsPairTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        vertPairCnt = len(connectsPair[i]) /2
        reqVertexPairsObjA = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][EGSidxRqVP]
        reqVertexPairsObjB = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][EGSidxRqVP]
        if vertPairCnt >= reqVertexPairsObjA and vertPairCnt >= reqVertexPairsObjB:
            connectsPairTmp.append(pair)
            connectCnt += 1
    connectsPair = connectsPairTmp
    
    print("Connections skipped due to too few connecting vertices:", connectCntOld -connectCnt)
    return connectsPair
        
################################################################################   

def calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, qNonManifold=0):

    ###### Calculate contact area for a single pair of objects
    props = bpy.context.window_manager.bcb

    ### Calculate boundary box corners
    bbAMin, bbAMax, bbACenter = boundaryBox(objA, 1)
    bbBMin, bbBMax, bbBCenter = boundaryBox(objB, 1)
    
    ### Calculate contact surface area from boundary box projection
    ### Project along all axis'
    overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
    overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
    overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
    
    ### Calculate area based on either the sum of all axis surfaces...
    # Formula only valid if we have overlap for all 3 axis
    # (This line is commented out because of the earlier connection pair check which ensured contact including a margin.)
    #if overlapX > 0 and overlapY > 0 and overlapZ > 0:  
    if 1:
        
        if not qNonManifold:
            overlapAreaX = overlapY *overlapZ
            overlapAreaY = overlapX *overlapZ
            overlapAreaZ = overlapX *overlapY
            # Add up all contact areas
            geoContactArea = overlapAreaX +overlapAreaY +overlapAreaZ
                
        ### Or calculate contact area based on predefined custom thickness
        else:
            geoContactArea = (overlapX +overlapY +overlapZ) *props.surfaceThickness
            
    else: geoContactArea = 0
            
    ### Find out element thickness to be used for bending threshold calculation 
    geo = [overlapX, overlapY, overlapZ]
    geoAxis = [1, 2, 3]
    geo, geoAxis = zip(*sorted(zip(geo, geoAxis)))
    geoHeight = geo[1]  # First item = mostly 0, second item = thickness/height, third item = width 
    geoWidth = geo[2]

    # Add custom thickness to contact area (only for manifolds as it is already included in non-manifolds)
    if not qNonManifold:
        geoContactArea += geoWidth *props.surfaceThickness

    ### Use center of contact area boundary box as constraints location
    centerX = max(bbAMin[0],bbBMin[0]) +(overlapX /2)
    centerY = max(bbAMin[1],bbBMin[1]) +(overlapY /2)
    centerZ = max(bbAMin[2],bbBMin[2]) +(overlapZ /2)
    center = Vector((centerX, centerY, centerZ))
    #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon

    return geoContactArea, geoHeight, geoWidth, center, geoAxis

########################################

def calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    connectsGeo = []
    connectsLoc = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        
        ###### Calculate contact area for a single pair of objects
        geoContactArea, geoHeight, geoWidth, center, geoAxis = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB)
                    
        # Geometry array: [area, height, width, axisNormal, axisHeight, axisWidth]
        connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2]])
        connectsLoc.append(center)
        
    return connectsGeo, connectsLoc

################################################################################   

def calculateContactAreaBasedOnBooleansForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections... (%d)" %len(connectsPair))

    props = bpy.context.window_manager.bcb

    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    objCameras = []
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            sceneTemp.objects.link(objTemp)
            objCameras.append(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    ### Main calculation loop
    connectsGeo = []
    connectsLoc = []
    connectsPair_len = len(connectsPair)
    for k in range(connectsPair_len):
        sys.stdout.write('\r' +"%d " %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /connectsPair_len)

        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        objA.select = 0
        objB.select = 0
            
        # Link objects we're working on to second scene (we try because of the object unlink workaround)
        try: sceneTemp.objects.link(objA)
        except: pass
        try: sceneTemp.objects.link(objB)
        except: pass
        
        ### Check if meshes are water tight (non-manifold)
        qNonManifolds = 0
        for obj in [objA, objB]:
            bpy.context.scene.objects.active = obj
            me = obj.data
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass 
            # Deselect all elements
            try: bpy.ops.mesh.select_all(action='DESELECT')
            except: pass 
            # Select non-manifold elements
            bpy.ops.mesh.select_non_manifold()
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass 
            # check mesh if there are selected elements found
            for edge in me.edges:
                if edge.select: qNonManifolds = 1; break

        ###### If non-manifold then calculate a contact area estimation based on boundary boxes intersection and a user defined thickness
        if qNonManifolds:

            #print('Warning: Mesh not water tight, non-manifolds found:', obj.name)

            ###### Calculate contact area for a single pair of objects
            geoContactArea, geoHeight, geoWidth, center, geoAxis = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, qNonManifold=1)
            
            # Geometry array: [area, height, width, axisNormal, axisHeight, axisWidth]
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2]])
            connectsLoc.append(center)

        ###### If both meshes are manifold continue with regular boolean based approach
        else:

            ### Add displacement modifier to objects to take search distance into account
            objA.modifiers.new(name="Displace_BCB", type='DISPLACE')
            modA_disp = objA.modifiers["Displace_BCB"]
            modA_disp.mid_level = 0
            modA_disp.strength = props.searchDistance /2
            objB.modifiers.new(name="Displace_BCB", type='DISPLACE')
            modB_disp = objB.modifiers["Displace_BCB"]
            modB_disp.mid_level = 0
            modB_disp.strength = props.searchDistance /2
            meA_disp = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
            meB_disp = objB.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                
            ### Add boolean modifier to object
            objA.modifiers.new(name="Boolean_BCB", type='BOOLEAN')
            modA_bool = objA.modifiers["Boolean_BCB"]
            ### Create a boolean intersection mesh (for center point calculation)
            modA_bool.operation = 'INTERSECT'
            try: modA_bool.solver = 'CARVE'
            except: pass
#            try: modA_bool.solver = 'BMESH'  # Try to enable bmesh based boolean if possible
#            except: pass
#            else:
#                try: modA_bool.use_bmesh_connect_regions = 0  # Disable this for bmesh to avoid long malformed faces
#                except: pass
#                try: modA_bool.threshold = 0.2  # Not sure what kind of threshold this is but 0 or 1 led to bad results including the full original mesh
#                except: pass                    # (If connection centers are lying on element centers, that's a sign for a bad boolean operation)
            modA_bool.object = objB
            ### Perform boolean operation and in case result is corrupt try again with small changes in displacement size
            searchDistanceMinimum = props.searchDistance /2 *0.9   # Lowest limit for retrying until we accept that no solution can be found
            qNoSolution = 0
            while 1:
                me_intersect = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                qBadResult = me_intersect.validate(verbose=False, clean_customdata=False)
                if qBadResult == 0: break
                modA_disp.strength *= 0.99
                sceneTemp.update()
                if modA_disp.strength < searchDistanceMinimum: qNoSolution = 1; break
            if qNoSolution: print('Error on boolean operation, mesh problems detected:', objA.name, objB.name); halt
                
            # If intersection mesh has geometry then continue calculation
            if len(me_intersect.vertices) > 0:
                
#                ### Create a boolean union mesh (for contact area calculation)
#                modA_bool.operation = 'UNION'
#                me_union = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
#                # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
#                qBadResult = me_union.validate(verbose=False, clean_customdata=False)
#                if qBadResult: print('Error on boolean operation, mesh problems detected:', objA.name, objB.name)
                
                ### Calculate center point for the intersection mesh
                # Create a new object for the mesh
                objIntersect = bpy.data.objects.new("BCB Temp Object", me_intersect)
                bpy.context.scene.objects.link(objIntersect)
                objIntersect.matrix_world = objA.matrix_world
                # Apply transforms so that local axes are matching world space axes (important for constraint orientation)
                objIntersect.select = 1
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                
                ### Calculate center of intersection mesh based on its boundary box (throws ugly "group # is unclassified!" warnings)
#                objIntersect.select = 1
#                #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
#                center = objIntersect.matrix_world.to_translation()
                ### Calculate center of intersection mesh based on its boundary box (alternative code, slower but no warnings)
                bbMin, bbMax, center = boundaryBox(objIntersect, 1)
                
                ### Find out element thickness to be used for bending threshold calculation (the diameter of the intersection mesh should be sufficient for now)
                geo = list(objIntersect.dimensions)
                geoAxis = [1, 2, 3]
                geo, geoAxis = zip(*sorted(zip(geo, geoAxis)))
                geoHeight = geo[1]   # First item = mostly 0, second item = thickness/height, third item = width 
                geoWidth = geo[2]
                
                ### Add displacement modifier to intersection mesh
                objIntersect.modifiers.new(name="Displace_BCB", type='DISPLACE')
                modIntersect_disp = objIntersect.modifiers["Displace_BCB"]
                modIntersect_disp.mid_level = 0
                modIntersect_disp.strength = -props.searchDistance /4
                me_intersect_remDisp = objIntersect.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                
                ### Calculate surface area for both original elements
                surface = 0
                meA = objA.data
                meB = objB.data
                for poly in meA.polygons: surface += poly.area
                for poly in meB.polygons: surface += poly.area
                ### Calculate surface area for displaced versions of both original elements
                surfaceDisp = 0
                for poly in meA_disp.polygons: surfaceDisp += poly.area
                for poly in meB_disp.polygons: surfaceDisp += poly.area
                # Calculate ratio of original to displaced surface area for later contact area correction
                correction = surface /surfaceDisp
#                ### Calculate surface area for the unified mesh
#                surfaceBoolUnion = 0
#                for poly in me_union.polygons: surfaceBoolUnion += poly.area
                ### Calculate surface area for the intersection mesh
                surfaceBoolIntersect = 0
                for poly in me_intersect.polygons: surfaceBoolIntersect += poly.area
                ### Calculate surface area for the intersection mesh with removed displacement
                surfaceBoolIntersectRemDisp = 0
                for poly in me_intersect_remDisp.polygons: surfaceBoolIntersectRemDisp += poly.area
#                ### The contact area is half the difference of both surface areas
#                geoContactArea = (surfaceDisp -surfaceBoolUnion) /2
                ### The contact area is half the surface area of the intersection mesh without displacement
                geoContactArea = surfaceBoolIntersectRemDisp /2
                geoContactArea *= correction
                if geoContactArea < 0: print('Error on boolean operation, contact area negative:', objA.name, objB.name)
                
                # Unlink new object from second scene
                sceneTemp.objects.unlink(objIntersect)
                
            # If intersection mesh has no geometry then invalidate connection
            else:
                geoContactArea = 0
                geoHeight = 0
                geoWidth = 0
                geoAxis = [1, 2, 3]
                center = Vector((0, 0, 0))
            
            # Remove modifiers from original object again
            objA.modifiers.remove(modA_bool)
            objA.modifiers.remove(modA_disp)
            objB.modifiers.remove(modB_disp)
            
#            # Unlink objects from second scene (leads to loss of rigid body settings, bug in Blender)
#            sceneTemp.objects.unlink(objA)
#            sceneTemp.objects.unlink(objB)
            # Workaround: Delete second scene and recreate it (deleting objects indirectly without the loss of rigid body settings)
            if k %200 == 0:   # Only delete scene every now and then so we have lower overhead from the relatively slow process
                try:    bpy.data.scenes.remove(sceneTemp, do_unlink=1)
                except: bpy.data.scenes.remove(sceneTemp)
                sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
                # Link cameras because in second scene is none and when coming back camera view will losing focus
                for obj in objCameras:
                    sceneTemp.objects.link(obj)
                # Switch to new scene
                bpy.context.screen.scene = sceneTemp
            
            # Geometry array: [area, height, width, axisNormal, axisHeight, axisWidth]
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2]])
            connectsLoc.append(center)
                
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    try:    bpy.data.scenes.remove(sceneTemp, do_unlink=1)
    except: bpy.data.scenes.remove(sceneTemp)
    
    print()
    return connectsGeo, connectsLoc

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsGeo, connectsLoc):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")

    props = bpy.context.window_manager.bcb    
    connectsPairTmp = []
    connectsGeoTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        if connectsGeo[i][0] > minimumContactArea:
            connectsPairTmp.append(connectsPair[i])
            connectsGeoTmp.append(connectsGeo[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsGeo = connectsGeoTmp
    connectsLoc = connectsLocTmp
    
    print("Connections skipped due to zero contact area:", connectCntOld -connectCnt)
    return connectsPair, connectsGeo, connectsLoc

################################################################################   

def createConnectionData(objs, objsEGrp, connectsPair):
    
    ### Create connection data
    if debug: print("Creating connection data...")
    
    props = bpy.context.window_manager.bcb    
    elemGrps = mem["elemGrps"]
    connectsConsts = []
    constsConnect = []
    constCntOfs = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]

        ### Count constraints by connection type preset
        elemGrpA = objsEGrp[pair[0]]
        elemGrpB = objsEGrp[pair[1]]
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        CT_A = elemGrps[elemGrpA][EGSidxCTyp]
        CT_B = elemGrps[elemGrpB][EGSidxCTyp]

        ### Check for passive groups and decide which group settings should be used
        constCnt = 0
        if CT_A != 0:  # A is active group
            try: constCntA = connectTypes[CT_A][1]  # Check if CT is valid
            except: constCntA = 0
        if CT_B != 0:  # B is active group
            try: constCntB = connectTypes[CT_B][1]  # Check if CT is valid
            except: constCntB = 0
        if CT_A != 0 and CT_B != 0:  # Both A and B are active groups
            ### Use the connection type with the smaller count of constraints for connection between different element groups
            ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
            if constCntA <= constCntB:
                  constCnt = constCntA
            else: constCnt = constCntB
        elif CT_A != 0 and CT_B == 0:  # Only A is active and B is passive group
            constCnt = constCntA
        elif CT_A == 0 and CT_B != 0:  # Only B is active and A is passive group
            constCnt = constCntB
        # Both A and B are in passive group but either one is actually an active RB (a xor b)
        elif bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
            constCnt = 1  # Only one fixed constraint is used to connect these (buffer special case)
        else:  # Both A and B are in passive group and both are passive RBs
            constCnt = 0
        # For unbreakable passive connections above settings can be overwritten
        if not props.passiveUseBreaking:
            # Both A and B are in passive group but either one is actually an active RB (a xor b)
            if bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
                constCnt = 1  # Only one fixed constraint is used to connect these (buffer special case)
        
        # In case the connection type is passive or unknown reserve no space for constraints
        if constCnt == 0: connectsConsts.append([])
        # Otherwise reserve space for the predefined constraints count
        else:
            # Add one extra slot for a possible constraint for permanent collision suppression
            if props.disableCollisionPerm: constCnt += 1
            # Reserve constraint slots
            items = []
            for j in range(constCnt):
                items.append(constCntOfs +j)
                constsConnect.append(i)
            connectsConsts.append(items)
            constCntOfs += len(items)
            
    return connectsPair, connectsConsts, constsConnect

################################################################################   

def backupLayerSettingsAndActivateNextEmptyLayer(scene):

    ### Activate the first empty layer
    print("Activating the first empty layer...")
    
    ### Backup layer settings
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(0)
    ### Find and activate the first empty layer
    qFound = 0
    for i in range(20):
        objsOnLayer = [obj for obj in scene.objects if obj.layers[i]]
        if len(objsOnLayer) == 0:
            layersNew[i] = 1
            qFound = 1
            break
    if qFound:
        # Set new layers
        scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
        
    # Return old layers state
    return layersBak
    
########################################

def backupLayerSettingsAndActivateNextLayerWithObj(scene, objToFind):

    ### Activating the first layer with constraint empty object
    print("Activating the first layer with constraint empty object...")
    
    ### Backup layer settings
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(0)
    ### Find and activate the first empty layer
    qFound = 0
    for i in range(20):
        objsOnLayer = [obj for obj in scene.objects if obj.layers[i]]
        if objToFind in objsOnLayer:
            layersNew[i] = 1
            qFound = 1
            break
    if qFound:
        # Set new layers
        scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
        
    # Return old layers state
    return layersBak

########################################

def backupLayerSettingsAndActivateAllLayers(scene):

    ### Activate all layers
    print("Activating all layers...")
    
    ### Backup layer settings
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(0)
    # Activate all layers
    scene.layers = [True for q in scene.layers]
       
    # Return old layers state
    return layersBak
    
################################################################################   

def createEmptyObjs(scene, constCnt):
    
    ### Create empty objects
    print("Creating empty objects... (%d)" %constCnt)

    # Use second scene optimization (enabling this is not recommended, as there are limitations in Blender related to RBs on multiple scenes)
    useSecondScene = 0
    
    ### Create first object
    objConst = bpy.data.objects.new('Constraint', None)
    bpy.context.scene.objects.link(objConst)
    objConst.empty_draw_type = 'CUBE'
    bpy.context.scene.objects.active = objConst
    bpy.ops.rigidbody.constraint_add()

    if useSecondScene:
        constCntPerScene = 1024
        scenesTemp = []
    else:
        constCntPerScene = 0
    emptyObjsGlobal = [objConst]
    # Repeat until desired object count is reached
    while len(emptyObjsGlobal) < constCnt:
        
        if useSecondScene:
            ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
            sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
            scenesTemp.append(sceneTemp)
            # Set layers to same state as original scene
            sceneTemp.layers = scene.layers
            # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
            bpy.context.screen.scene = scene
            # Link cameras because in second scene is none and when coming back camera view will losing focus
            objCameras = []
            for objTemp in scene.objects:
                if objTemp.type == 'CAMERA':
                    sceneTemp.objects.link(objTemp)
                    objCameras.append(objTemp)
            # Switch to new scene
            bpy.context.screen.scene = sceneTemp
            # If using two scenes make sure both are using the same RigidBodyWorld and RigidBodyConstraints groups
            bpy.ops.rigidbody.world_add()
            bpy.context.scene.rigidbody_world.group = bpy.data.groups["RigidBodyWorld"]
            bpy.context.scene.rigidbody_world.constraints = bpy.data.groups["RigidBodyConstraints"]
            # Link first empty into new scene
            bpy.context.scene.objects.link(objConst)
            
        ### Duplicate empties as long as we got the desired count   
        emptyObjs = [objConst]
        while len(emptyObjs) < (constCnt -(len(emptyObjsGlobal) -1)) and (constCntPerScene == 0 or len(emptyObjs) <= constCntPerScene):
            if constCntPerScene != 0:
                sys.stdout.write("%d " %len(emptyObjs))
            else:
                if len(emptyObjs) <= 1024: sys.stdout.write("%d " %len(emptyObjs))
                else:                      sys.stdout.write("\r%d - " %len(emptyObjs))
            # Update progress bar
            bpy.context.window_manager.progress_update(len(emptyObjsGlobal) /constCnt)
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            # Select empties already in list
            c = 0
            for obj in emptyObjs:
                if c < (constCnt -(len(emptyObjsGlobal) -1)) -len(emptyObjs):
                    obj.select = 1
                    c += 1
                else: break
            # Duplicate them
            bpy.ops.object.duplicate(linked=False)
            # Add duplicates to list again
            for obj in scene.objects:
                if obj.select and obj.is_visible(scene):
                    if obj.type == 'EMPTY':
                        emptyObjs.append(obj)
         
        emptyObjsGlobal.extend(emptyObjs[1:])
        sys.stdout.write("\r%d - " %len(emptyObjsGlobal))
        
    emptyObjs = emptyObjsGlobal

    if useSecondScene:
        ### Link new object back into original scene
        for scn in scenesTemp:
            # Switch through temp scenes
            bpy.context.screen.scene = scn
            # Select all objects
            bpy.ops.object.select_all(action='SELECT')
            # Link objects to original scene
            bpy.ops.object.make_links_scene(scene=scene.name)
            # Remove constraint data (otherwise it would cause undesired side effects later in the simulation)
            bpy.ops.rigidbody.constraints_remove()
            # Delete objects from temp scene (required to get rid of the duplicate rigid body world data, which later would have influence on the simulation)
            bpy.ops.object.delete(use_global=False)

        # Switch back to original scene
        bpy.context.screen.scene = scene
        # Delete second scene
        for scn in scenesTemp:
            try:    bpy.data.scenes.remove(scn, do_unlink=1)
            except: bpy.data.scenes.remove(scn)
        print()

        # Turn empties into constraints (extremely slow but there is no faster way when using temp scenes)
        print("Turning empties into constraints...")
        for i in range(len(emptyObjs)):
            sys.stdout.write("\r%d" %i)
            obj = emptyObjs[i]
            bpy.context.scene.objects.active = obj
            bpy.ops.rigidbody.constraint_add()
    print()
    
#    ### Sort empty objects by database order (old slower code)
#    objsSorted = []
#    #for objDB in bpy.data.objects:  # Sort by bpy.data order
#    for objDB in bpy.data.groups["RigidBodyConstraints"].objects:  # Sort by RigidBodyConstraints group order
#        for obj in emptyObjs:
#            if obj.name == objDB.name:
#                objsSorted.append(obj)
#                del emptyObjs[emptyObjs.index(obj)]
#                break
    ### Sort empty objects by database order
    objsSource = emptyObjs
    objsDB = bpy.data.groups["RigidBodyConstraints"].objects
    # Generate dictionary index by DB order
    objsIndex = {}
    for i in range(len(objsDB)): objsIndex[objsDB[i].name] = i
    # Sort objects by index
    objsSorted = [None for i in range(len(objsDB))]
    for obj in objsSource:
        objsSorted[objsIndex[obj.name]] = obj
    # Filter unused objects
    objsSortedFiltered = []
    for obj in objsSorted:
        if obj != None: objsSortedFiltered.append(obj)
#    print("EMPTIES (original, DB):")
#    for i in range(len(objsSource)):
#        obj = objsSource[i]
#        objSorted = objsSortedFiltered[i]
#        print(obj.name, objSorted.name)
    emptyObjs = objsSortedFiltered
    
    return emptyObjs        

################################################################################   

def bundlingEmptyObjsToClusters(connectsLoc, connectsConsts):
    
    ### Bundling close empties into clusters, merge locations and count connections per cluster
    print("Bundling close empties into clusters...")
    
    props = bpy.context.window_manager.bcb
    m = 1
    qChanged = 1
    while qChanged:   # Repeat until no more constraints are moved
        qChanged = 0
        
        sys.stdout.write('\r' +"Pass %d" %m)
        # Update progress bar
        bpy.context.window_manager.progress_update(1 -(1 /m))
        m += 1
        
        ### Build kd-tree for constraint locations
        kdObjs = mathutils.kdtree.KDTree(len(connectsLoc))
        for i, loc in enumerate(connectsLoc):
            kdObjs.insert(loc, i)
        kdObjs.balance()
        
        clustersConnects = []  # Stores all constraints indices per cluster
        clustersLoc = []       # Stores the location of each cluster
        for i in range(len(connectsLoc)):
            
            ### Find closest connection location via kd-tree (zero distance start item included)
            co_find = connectsLoc[i]
            aIndex = []; aCo = []#; aDist = [];
            j = 0
            for (co, index, dist) in kdObjs.find_range(co_find, props.clusterRadius):   # Find constraint object within search range
                if j == 0 or co != lastCo:   # Skip constraints that already share the same location (caused by earlier loops)
                    aIndex.append(index); aCo.append(co)#; aDist.append(dist)
                    lastCo = co
                    # Stop after second different constraint is found
                    j += 1
                    if j == 2: qChanged = 1; break
                        
            ### Calculate average location of the two constraints found within cluster radius
            ### We merge them pairwise instead of all at once for improved and more even distribution
            if len(aCo) == 2:
                loc = (aCo[0] +aCo[1]) /2
                clustersLoc.append(loc)
                clustersConnects.append([aIndex[0], aIndex[1]])
                ### Also move all other constraints with the same locations because we can assume they already have been merged earlier
                for i in range(len(connectsLoc)):
                    if aCo[0] == connectsLoc[i] or aCo[1] == connectsLoc[i]:
                        clustersConnects[-1:][0].append(i)
                  
        ### Apply cluster locations to constraints
        for l in range(len(clustersConnects)):
            for k in clustersConnects[l]:
                connectsLoc[k] = clustersLoc[l]
    
    print()
    
    ### Count clusters (only for status print)
    clusters = set()
    for loc in connectsLoc:
        clusters.add(tuple(loc))
    print("Cluster count:", len(clusters))

################################################################################

def createParentsIfRequired(scene, objs, objsEGrp, childObjs):

    ### Create parents if required
    print("Creating invisible parent / visible child elements...")
    
    elemGrps = mem["elemGrps"]

    ### Store selection
    selectionOld = []
    for k in range(len(objs)):
        if objs[k].select:
            selectionOld.append(k)
                
    ### Selecting objects without parent
    q = 0
    for k in range(len(objs)):
        obj = objs[k]
        facing = elemGrps[objsEGrp[k]][EGSidxFacg]
        if facing:
            q = 1
            if obj.select:
                if not "bcb_child" in obj.keys():
                    obj["bcb_parent"] = obj.name
                else: obj.select = 0
        else: obj.select = 0
        
    if q:
        # Duplicate selected objects            
        bpy.ops.object.duplicate(linked=False)
        ### Add newly created objects to parent object list and make them actual parents
        childObjsNew = []
        for obj in scene.objects:
            if obj.select:
                childObjsNew.append(obj)
                obj.select = 0
        childObjs.extend(childObjsNew)
        
        ### Make parent relationship
        for k in range(len(childObjsNew)):
            sys.stdout.write('\r' +"%d" %k)
            
            childObj = childObjsNew[k]
            parentObj = scene.objects[childObj["bcb_parent"]]
            del parentObj["bcb_parent"]
            parentObj["bcb_child"] = childObj.name
            ### Make parent
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = parentObj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            parentObj.select = 0
            childObj.select = 0
            if len(childObjsNew) > 0: print()
        ### Remove child object from rigid body world (should not be simulated anymore)
        for k in range(len(childObjsNew)):
            childObjsNew[k].select
        bpy.ops.rigidbody.objects_remove()
        
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    ### Revert back to original selection
    for idx in selectionOld:
        objs[idx].select = 1       
        
################################################################################

def applyScale(scene, objs, objsEGrp, childObjs):
    
    ### Scale elements by custom scale factor and make separate collision object for that
    print("Applying scale...")
    
    elemGrps = mem["elemGrps"]

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    obj = None
    ### Select objects in question
    for k in range(len(objs)):
        obj = objs[k]
        scale = elemGrps[objsEGrp[k]][EGSidxScal]
        if scale != 0 and scale != 1:
            obj.select = 1
    
    if obj != None:
        ###### Create parents if required
        createParentsIfRequired(scene, objs, objsEGrp, childObjs)
        ### Apply scale
        for k in range(len(objs)):
            obj = objs[k]
            if obj.select:
                scale = elemGrps[objsEGrp[k]][EGSidxScal]
                obj.scale *= scale
                # For children invert scaling to compensate for indirect scaling through parenting
                if "bcb_child" in obj.keys():
                    scene.objects[obj["bcb_child"]].scale /= scale
                    
################################################################################   

def applyBevel(scene, objs, objsEGrp, childObjs):
    
    ### Bevel elements and make separate collision object for that
    print("Applying bevel...")
    
    elemGrps = mem["elemGrps"]

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    obj = None
    ### Select objects in question
    for k in range(len(objs)):
        qBevel = elemGrps[objsEGrp[k]][EGSidxBevl]
        if qBevel:
            obj = objs[k]
            obj.select = 1
    
    ### Add only one bevel modifier and copy that to the other selected objects (Todo: Should be done for each object individually but is slower)
    if obj != None:
        ###### Create parents if required
        createParentsIfRequired(scene, objs, objsEGrp, childObjs)
        ### Apply bevel
        bpy.context.scene.objects.active = obj
        if "Bevel_bcb" not in obj.modifiers:
            bpy.ops.object.modifier_add(type='BEVEL')
            obj.modifiers["Bevel"].name = "Bevel_bcb"
            obj.modifiers["Bevel_bcb"].width = 10.0
            bpy.ops.object.make_links_data(type='MODIFIERS')
    
    ### Make modifiers real (required to be taken into account by Bullet physics)
    for k in range(len(objs)):
        obj = objs[k]
        if obj.select:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bevel_bcb")
       
################################################################################   

def calculateMass(scene, objs, objsEGrp, childObjs):
    
    ### Calculate a mass for all mesh objects according to element groups settings
    print("Calculating masses from preset material... (Children: %d)" %len(childObjs))
     
    elemGrps = mem["elemGrps"]

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    ### Create new rigid body settings for children with the data from its parent (so mass can be calculated on children)
    i = 0
    for childObj in childObjs:
        parentObj = scene.objects[childObj["bcb_parent"]]
        if parentObj.rigid_body != None:
            sys.stdout.write('\r' +"%d  " %i)
            i += 1
            
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_add()
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = parentObj
            bpy.ops.rigidbody.object_settings_copy()
            parentObj.select = 0
            childObj.select = 0
    if len(childObjs) > 0: sys.stdout.write('\r        ')

    ### Update masses
    
    objsTotal = []; objsScale = []
    for j in range(len(elemGrps)):
        elemGrp = elemGrps[j]
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        objsSelected = []
        for k in range(len(objs)):
            obj = objs[k]
            if obj != None and obj.rigid_body != None:
                CT = elemGrps[objsEGrp[k]][EGSidxCTyp]
                if CT == 0:
                    # The foundation buffer objects need a large mass so they won't pushed away
                    obj.rigid_body.mass = 1000
                else:
                    try: scale = elemGrps[objsEGrp[k]][EGSidxScal]  # Try in case elemGrps is from an old BCB version
                    except: qScale = 0
                    else: qScale = 1
                    if j == objsEGrp[k]:
                        if obj != None:
                            if "bcb_child" in obj.keys():
                                obj = scene.objects[obj["bcb_child"]]
                            obj.select = 1
                            # Temporarily revert element scaling for mass calculation
                            if qScale:
                                if scale != 0 and scale != 1:
                                    obj.scale /= scale
                                    objsSelected.append(obj)
                                    objsTotal.append(obj)
                                    objsScale.append(scale)

        ### Calculating and applying material masses
        materialPreset = elemGrp[EGSidxMatP]
        materialDensity = elemGrp[EGSidxDens]
        if not materialDensity:
            if materialPreset != "": bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material="Custom", density=materialDensity)
                
        ### Adding live load to masses
        liveLoad = elemGrp[EGSidxLoad]
        for obj in objsSelected:
            dims = obj.dimensions
            floorArea = dims[0] *dims[1]  # Simple approximation by assuming rectangular floor area (x *y)
            if liveLoad > 0: obj.rigid_body.mass += floorArea *liveLoad
            obj["Floor Area"] = floorArea  # Only needed for the diagnostic prints below

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Reapply element scaling after mass calculation
    for k in range(len(objsTotal)):
        obj = objsTotal[k]
        scale = objsScale[k]
        obj.scale *= scale
    
    ### Calculate total and element group masses for diagnostic purposes
    print()
    groupsMass = {}; groupsArea = {}
    for obj in objs:
        if obj != None and obj.rigid_body != None and obj.rigid_body.type == 'ACTIVE':
            for group in bpy.data.groups:
                try: obj = group.objects[obj.name]
                except: pass
                else:
                    try: groupsMass[group.name] += obj.rigid_body.mass
                    except:
                        try: groupsMass[group.name] = obj.rigid_body.mass
                        except: pass
                    try: groupsArea[group.name] += obj["Floor Area"]
                    except:
                        try: groupsArea[group.name] = obj["Floor Area"]
                        except: pass
    for groupName in groupsMass.keys():
        try: mass = groupsMass[groupName]
        except: mass = 0
        try: area = groupsArea[groupName]
        except: area = 0
        if mass != groupsMass["RigidBodyWorld"]:  # Filter all groups that contain the complete structure
            print("Group '%s' mass: %0.0f t and %0.0f kg / Floor area: %0.2f m^2" %(groupName, floor(mass/1000), mass%1000, area))
    try: mass = groupsMass["RigidBodyWorld"]
    except: mass = 0
    try: area = groupsArea["RigidBodyWorld"]
    except: area = 0
    print("Total mass: %0.0f t and %0.0f kg / Total floor area: %0.2f m^2" %(floor(mass/1000), mass%1000, area))
    print()
    
    ### Copy rigid body settings (and mass) from children back to their parents and remove children from rigid body world
    i = 0
    for childObj in childObjs:
        parentObj = scene.objects[childObj["bcb_parent"]]
        if parentObj.rigid_body != None:
            sys.stdout.write('\r' +"%d  " %i)
            i += 1
            
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_settings_copy()
            parentObj.select = 0
            childObj.select = 0

    ### Remove child objects from rigid body world (should not be simulated anymore)
    for childObj in childObjs:
        childObj.select
    bpy.ops.rigidbody.objects_remove()
            
    if len(childObjs) > 0: print()

################################################################################   

def correctContactAreaByVolume(objs, connectsPair, connectsGeo):
    
    ### Correct the preliminary calculated boundary box based contact areas by considering the element volumes
    print("Correcting contact areas...")

    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene
    elemGrps = mem["elemGrps"]

    for j in range(len(elemGrps)):
        elemGrp = elemGrps[j]

        ### Find out density of the element group
        materialDensity = elemGrp[EGSidxDens]
        if not materialDensity:
            materialPreset = elemGrp[EGSidxMatP]
            if materialPreset != "": materialDensity = materialPresets[materialPreset]

        ### Calculate volumes from densities and derive correctional factors for contact areas
        for obj in objs:
            volume = obj.rigid_body.mass /materialDensity

            # Find out element thickness to be used for bending threshold calculation 
            dim = obj.dimensions; dimAxis = [1, 2, 3]
            dim, dimAxis = zip(*sorted(zip(dim, dimAxis)))
            dimHeight = dim[0]; dimWidth = dim[1]; dimLength = dim[2]
            # Derive contact area correction factor from geometry section area divided by bbox section area
            sectionArea = volume /dimLength  # Full geometry section area of element
            if dimHeight *dimWidth != 0:
                corFac = sectionArea / (dimHeight *dimWidth)
            else: corFac = 1
            obj["CA Corr.Fac."] = corFac
            obj["Density"] = materialDensity
            obj["Volume"] = volume
        
        ### Apply corrections to geometry lists  
        connectsPair_iter = iter(connectsPair)
        connectsGeo_iter = iter(connectsGeo)
        for k in range(len(connectsGeo)):
            pair = next(connectsPair_iter)   
            geo = next(connectsGeo_iter)
            objA = objs[pair[0]]
            objB = objs[pair[1]]

            corFacA = objA["CA Corr.Fac."]
            corFacB = objB["CA Corr.Fac."]
            geo[0] *= corFacA *corFacB  # = geoContactArea
        