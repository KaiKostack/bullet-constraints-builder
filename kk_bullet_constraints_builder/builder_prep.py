##############################
# Bullet Constraints Builder #
##############################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# Versions 1 & 2 were developed at the Laurea University of Applied Sciences,
# Finland. Later versions are independently developed.
# Copyright (C) 2015-2021 Kai Kostack
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

import bpy, mathutils, sys, math, bmesh, array, random
from mathutils import Vector
from math import *
import global_vars

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *       # Contains build data access functions

################################################################################

def initGeneralRigidBodyWorldSettings(scene):

    ### Set general rigid body world settings
    props = bpy.context.window_manager.bcb

    # Automatically correct the FPS rate or Solver Steps as the FPS must be multiples of the Solver Steps to avoid stuttering
    if props.stepsPerSecond %scene.render.fps != 0 or scene.render.fps_base != 1:
        print("Warning: Solver Steps should be multiples of the Frame Rate, trying to fix it...")
        fps = props.stepsPerSecond /int(props.stepsPerSecond /scene.render.fps)
        if fps %int(fps) == 0:
            scene.render.fps = fps
            scene.render.fps_base = 1
            print("New Frame Rate set to:", scene.render.fps)
        else:
            props.update_lock = 1  # Suppress automatic updating to set a new property value
            props.stepsPerSecond = scene.render.fps *int(props.stepsPerSecond /scene.render.fps)
            props.update_lock = 0
            print("New Solver Steps set to:", props.stepsPerSecond)
            if props.stepsPerSecond %scene.render.fps != 0 or scene.render.fps_base != 1:
                fps = props.stepsPerSecond /int(props.stepsPerSecond /scene.render.fps)
                if fps %int(fps) == 0:
                    print("New Frame Rate set to:", scene.render.fps)
                    scene.render.fps = fps
                    scene.render.fps_base = 1
                
    # Set Steps Per Second for rigid body simulation
    scene.rigidbody_world.steps_per_second = props.stepsPerSecond
    scene.rigidbody_world.solver_iterations = props.solverIterations
    # Set the length of the point cache to match the scene length
    scene.rigidbody_world.point_cache.frame_end = scene.frame_end
    # Set Split Impulse for rigid body simulation
    #scene.rigidbody_world.use_split_impulse = True

################################################################################   

def createElementGroupIndex(objs):

    ### Create a list about which object belongs to which element group
    elemGrps = global_vars.elemGrps
    objsEGrps = []
    errorsShown = 1
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
            if errorsShown < 2:
                sys.stdout.write("Warning: Object %s belongs to more than one element group, only first group is used. Element groups:" %obj.name)
                for idx in objGrpsTmp: sys.stdout.write(" #%d %s" %(idx, elemGrps[idx][EGSidxName]))
                print()
                errorsShown += 1
            elif errorsShown == 2:
                print("There are further warnings, only the first one is shown here.")
                print()
                errorsShown += 1
        # If selected object is not part of any scene group try to find an element group with empty name to use (default group)
        elif len(objGrpsTmp) == 0:
            for k in range(len(elemGrps)):
                elemGrpName = elemGrps[k][EGSidxName]
                if elemGrpName == '':
                    objGrpsTmp.append(k)
        # Assign all found groups to object
        if len(objGrpsTmp) > 0:
            objsEGrps.append(objGrpsTmp)
        # If not even a default group is available then use element group 0 as fallback
        # (Todo: flag the group as -1 and deal with it later, but that's also complex)
        else: objsEGrps.append([0])
        
    ### Taking only first item of the element group lists per object into account (the BCB can only manage one element group per object)
    ### Earlier idea was to expand objs array for objects being member of multiple element groups (item duplication allowed)
    ### but this is not feasible since all the other functions within the BCB would need to respect these.
    #objsNew = []
    objsEGrp = []
    objsEGrps_iter = iter(objsEGrps)
    cnt = 0
    for obj in objs:
        eGrps = next(objsEGrps_iter)
        #for eGrp in eGrps:
        #    objsEGrp.append(eGrp)
        #    objsNew.append(obj)
        if len(eGrps) > 0:
            objsEGrp.append(eGrps[0])
            cnt += 1
    
    return objsEGrp, cnt

################################################################################   

def gatherObjects(scene):

    print("Creating object lists of selected objects...")

    props = bpy.context.window_manager.bcb
    elemGrps = global_vars.elemGrps

#    ### Check if unspecified (empty name) element group is present, only then consider user selection
#    qUserSelection = 0
#    for i in range(len(elemGrps)):
#        grpName = elemGrps[i][EGSidxName]
#        if grpName == "": qUserSelection = 1; break
#    if not qUserSelection:
#        # Deselect all objects.
#        bpy.ops.object.select_all(action='DESELECT')
#
#    ### Check which element group names correspond to scene groups and select those
#    for i in range(len(elemGrps)):
#        grpName = elemGrps[i][EGSidxName]
#        try: grp = bpy.data.groups[grpName]
#        except: continue
#        # Select all objects from that group       
#        for obj in grp.objects:
#            if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene):
#                obj.select = 1

    ### Deselect possible ground objects
    try: objGnd = scene.objects[props.preprocTools_gnd_obj]
    except: pass
    else: objGnd.select = 0
    try: objMot = scene.objects[props.preprocTools_gnd_obm]
    except: pass
    else: objGnd.select = 0
    
    ### Prepare scene object dictionary for empties to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj
    ### Get previous constraint objects list from BCB data
    try: names = scene["bcb_emptyObjs"]
    except: pass
    else:
        emptyObjs = []
        for name in names:
            if len(name):
                try: emptyObjs.append(scnEmptyObjs[name])
                except: emptyObjs.append(None); print("Error: Object %s missing, rebuilding constraints is required." %name)
            else: emptyObjs.append(None)
        # Select constraint (empty) objects that might exist from earlier simulations
        for obj in emptyObjs:
            if obj != None: obj.select = 1
    
    ### Create main object lists from selection
    objs = []
    emptyObjs = []
    objsID = []
    for obj in scene.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            # Look for a component ID property
            try: ID = obj["ID"]
            except: objsID.append(0)
            else: objsID.append(ID)
            # Clear object properties
            #for key in obj.keys(): del obj[key]
            # Detect if mesh or empty (constraint)
            if obj.type == 'MESH' and obj.rigid_body != None and len(obj.data.vertices) > 1:
                objs.append(obj)
            elif obj.type == 'EMPTY' and obj.rigid_body_constraint != None:
                emptyObjs.append(obj)
    
    return objs, emptyObjs, objsID

################################################################################   

def prepareObjects(objs):

    print("Preparing objects...")

    bpy.context.scene.objects.active = objs[0]

    ### Create one main group for all objects
    grpName = grpNameBuilding
    try: grp = bpy.data.groups[grpName]
    except: grp = bpy.data.groups.new(grpName)
    for obj in objs:
        if obj.name not in grp.objects:
            grp.objects.link(obj)

    ### Backup scale factor depending on object's collision shape to make sure volume and mass calculation are correct (not all need this)
    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objs:
        if obj.rigid_body != None:
            if obj.rigid_body.collision_shape == 'CONVEX_HULL' or \
               obj.rigid_body.collision_shape == 'BOX' or \
               obj.rigid_body.collision_shape == 'MESH':  # Not needed: SPHERE, CAPSULE, CYLINDER, CONE
                obj["Scale"] = obj.scale  # Backup original scale
            obj.select = 0
        else:
            obj.select = 1
    ### Add rigid body status if not already present
    bpy.ops.rigidbody.objects_add()
            
    ### Prepare objects (make unique, apply transforms etc.)
    # Select objects
    for obj in objs: obj.select = 1
    # Remove instancing from objects
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True, material=False, texture=False, animation=False)
    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    ### Flip face normals for objects with negative scaling (will be reverted again when scaling is applied)
    bpy.context.tool_settings.mesh_select_mode = False, False, True
    for obj in objs:
        if obj.scale[0] < 0 or obj.scale[1] < 0 or obj.scale[2] < 0:
            bpy.context.scene.objects.active = obj
            # Enter edit mode              
            bpy.ops.object.mode_set(mode='EDIT')
            # Select all elements
            bpy.ops.mesh.select_all(action='SELECT')
            # Flip normals
            bpy.ops.mesh.flip_normals()
            # Leave edit mode
            bpy.ops.object.mode_set(mode='OBJECT')
    ### Converting mesh scale to 1
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
################################################################################   

def prepareMaterials(objs, objsEGrp):

    print("Preparing materials...")

    elemGrps = global_vars.elemGrps
            
    ### Prepare dictionary of element indices for faster item search (optimization)
    objsDict = {}
    for i in range(len(objs)):
        objsDict[objs[i]] = i
    
    ### Create group index with their respective objects
    grpsObjs = {}
    for elemGrp in elemGrps:
        grpName = elemGrp[EGSidxName]
        grpObjs = []
        for obj in objs:
            if elemGrp == elemGrps[objsEGrp[objsDict[obj]]]:
                grpObjs.append(obj)
        grpsObjs[grpName] = grpObjs
    
    ### Create and add individual materials to objects based on element groups if not already present
    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    for elemGrp in elemGrps:
        # Select objects by element group if no material present
        grpName = elemGrp[EGSidxName]
        grpNoMat = []
        for obj in grpsObjs[grpName]:
            if len(obj.material_slots) == 0:
                obj.select = 1
                grpNoMat.append(obj)

        # Create and add new material to the found objects
        if len(grpNoMat):
            bpy.context.scene.objects.active = grpNoMat[0]
            
            # Create material slot with material
            bpy.ops.object.material_slot_add()
            try: mat = bpy.data.materials[grpName]
            except: mat = bpy.data.materials.new(grpName)
            bpy.context.scene.objects.active.material_slots[-1].material = mat

            # Link new material to entire selection
            bpy.ops.object.make_links_data(type='MATERIAL')
            # Revert selection
            for obj in grpNoMat:
                obj.select = 0
                
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
    elemGrps = global_vars.elemGrps

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
    connectsVpairCnt = []      # Stores vertex pair count per connection
    connectsLoc = []           # Stores connection locations
    objsConnectCnt = [0]*len(objs)   # Stores the connection count per object
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []; aDist = []  #; aCo = [] 
        for (co, index, dist) in kdObjs.find_range(co_find, 999999):
            aIndex.append(index); aDist.append(dist)  #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:]  # Remove first item because it's the same as co_find (zero distance)
        
        ### Walk through current object vertices
        for m in range(len(me.vertices)):
            vert = me.vertices[m]
            co_find = mat *vert.co     # Multiply matrix by vertex coordinates to get global coordinates
                        
            # Loop through comparison objects found
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
                        pair = [k, l]
                        pair.sort()
                        if pair not in connectsPair:
                            connectsPair.append(pair)
                            connectsPairDist.append(aDist[j])
                            objsConnectCnt[k] += 1
                            objsConnectCnt[l] += 1
                            connectsVpairCnt.append(1)
                            connectsLoc.append(co)
                        else:
                            idx = connectsPair.index(pair)
                            connectsVpairCnt[idx] += 1
                            connectsLoc[idx] = connectsLoc[idx] *(1 -(1 /connectsVpairCnt[idx])) +co *(1 /connectsVpairCnt[idx])  # Average all locs
    print()
                            
    # Vertex pair count correction because we counted every pair twice 
    connectsVpairCnt = [int(cnt /2) for cnt in connectsVpairCnt]
    
    ### Filter for vertex pair count condition
    connectsPairNew = []
    connectsPairDistNew = []
    connectsLocNew = []
    connectsPair_iter = iter(connectsPair)
    connectsPairDist_iter = iter(connectsPairDist)
    connectsLoc_iter = iter(connectsLoc)
    connectsVpairCnt_iter = iter(connectsVpairCnt)
    for k in range(len(connectsPair)):
        pair = next(connectsPair_iter)
        vPairCnt = next(connectsVpairCnt_iter)
        pairDist = next(connectsPairDist_iter)   
        loc = next(connectsLoc_iter)
        Prio_A = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][EGSidxPrio]
        Prio_B = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][EGSidxPrio]
        reqVertexPairsObjA = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][EGSidxRqVP]
        reqVertexPairsObjB = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][EGSidxRqVP]
        if vertPairCnt >= reqVertexPairsObjA and vertPairCnt >= reqVertexPairsObjB and Prio_A == Prio_B \
        or vertPairCnt >= reqVertexPairsObjA and Prio_A > Prio_B \
        or vertPairCnt >= reqVertexPairsObjB and Prio_A < Prio_B:
            connectsPairNew.append(pair)
            connectsPairDistNew.append(pairDist)
            connectsLocNew.append(loc)
        else:
            # Connections count correction
            objsConnectCnt[pair[0]] -= 1
            objsConnectCnt[pair[1]] -= 1
    connectsPair = connectsPairNew
    connectsPairDist = connectsPairDistNew
    connectsLoc = connectsLocNew

    ### Filter for connection count condition
    connectsPairNew = []
    connectsPairDistNew = []
    connectsLocNew = []
    connectsPair_iter = iter(connectsPair)
    connectsPairDist_iter = iter(connectsPairDist)
    connectsLoc_iter = iter(connectsLoc)
    for k in range(len(connectsPair)):
        pair = next(connectsPair_iter)
        pairDist = next(connectsPairDist_iter)   
        loc = next(connectsLoc_iter)
        if max(objsConnectCnt[pair[0]], objsConnectCnt[pair[1]]) <= props.connectionCountLimit:
            connectsPairNew.append(pair)
            connectsPairDistNew.append(pairDist)
            connectsLocNew.append(loc)
        else:
            # Connections count correction
            objsConnectCnt[pair[0]] -= 1
            objsConnectCnt[pair[1]] -= 1
    connectsPair = connectsPairNew
    connectsPairDist = connectsPairDistNew
    connectsLoc = connectsLocNew

    return connectsPair, connectsPairDist, connectsLoc

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
        aIndex = []; aDist = []  #; aCo = [] 
        if props.connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, props.connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index); aDist.append(dist)  #; aCo.append(co)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index); aDist.append(dist)  #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:]  # Remove first item because it's the same as co_find (zero distance)
    
        # Loop through comparison objects found
        connectCnt = 0
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
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
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

def boundaryBoxFaces(obj, qGlobalSpace, selMin=None, selMax=None):

    ### Calculate boundary box corners and center from given object
    me = obj.data
    verts = me.vertices
    faces = me.polygons
    
    ### Only consider faces within a user defined boundary box
    if selMin != None and selMax != None:
        selVerts = []
        selArea = 0
        for face in faces:
            if qGlobalSpace:
                # Multiply local coordinates by world matrix to get global coordinates
                mat = obj.matrix_world
                loc = mat *face.center
            else:
                loc = face.center.copy()
            if  selMax[0] > loc[0] and selMin[0] < loc[0] \
            and selMax[1] > loc[1] and selMin[1] < loc[1] \
            and selMax[2] > loc[2] and selMin[2] < loc[2]:
                selVerts.extend(face.vertices)
                selArea += face.area
        # Update vertex list to include only selected face vertices
        vertsNew = []
        selVerts = list(set(selVerts))  # Eliminate duplicated indices
        for idx in selVerts:
            vertsNew.append(verts[idx])
        verts = vertsNew

        # Debug code
#        for idx in range(len(me.vertices)):
#            if idx in selVerts:
#                  me.vertices[idx].select = 1
#            else: me.vertices[idx].select = 0    
                
    ### Calculate boundary box corners
    if len(verts) > 0:
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
        
        return bbMin, bbMax, bbCenter, selArea

    else: 
        return None, None, None, 0

################################################################################

def calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, sDistFallb, qNonManifold=0, qAccurate=0):

    ###### Calculate contact area for a single pair of objects
    props = bpy.context.window_manager.bcb
    searchDist = props.searchDistance
    searchDistMesh = props.searchDistanceMesh

    ### Calculate boundary box corners
    bbAMin, bbAMax, bbACenter = boundaryBox(objA, 1)
    bbBMin, bbBMax, bbBCenter = boundaryBox(objB, 1)
    halfSize = ((bbAMax-bbAMin) +(bbBMax-bbBMin)) /4
    bbAMinOrig, bbAMaxOrig, bbACenterOrig = bbAMin, bbAMax, bbACenter
    bbBMinOrig, bbBMaxOrig, bbBCenterOrig = bbBMin, bbBMax, bbBCenter

    ### Determine faces within search range of both objects and return their surface area
    geoContactAreaF = 0
    qSkipConnect = 0
    if qAccurate:
        # Create new faces bbox for A for faces within searchDistMesh range of bbox B
        bbBMinSDM = Vector((bbBMin[0]-searchDistMesh, bbBMin[1]-searchDistMesh, bbBMin[2]-searchDistMesh))
        bbBMaxSDM = Vector((bbBMax[0]+searchDistMesh, bbBMax[1]+searchDistMesh, bbBMax[2]+searchDistMesh))
        bbAMinF, bbAMaxF, bbACenterF, areaA = boundaryBoxFaces(objA, 1, selMin=bbBMinSDM, selMax=bbBMaxSDM)
        # Create new faces bbox for B for faces within searchDistMesh range of bbox A
        bbAMinSDM = Vector((bbAMin[0]-searchDistMesh, bbAMin[1]-searchDistMesh, bbAMin[2]-searchDistMesh))
        bbAMaxSDM = Vector((bbAMax[0]+searchDistMesh, bbAMax[1]+searchDistMesh, bbAMax[2]+searchDistMesh))
        bbBMinF, bbBMaxF, bbBCenterF, areaB = boundaryBoxFaces(objB, 1, selMin=bbAMinSDM, selMax=bbAMaxSDM)
        # Create new faces bbox for A for faces within searchDist range of bbox B
        bbBMinSD = Vector((bbBMin[0]-searchDist, bbBMin[1]-searchDist, bbBMin[2]-searchDist))
        bbBMaxSD = Vector((bbBMax[0]+searchDist, bbBMax[1]+searchDist, bbBMax[2]+searchDist))
        bbAMinF2, bbAMaxF2, bbACenterF2, areaA2 = boundaryBoxFaces(objA, 1, selMin=bbBMinSD, selMax=bbBMaxSD)
        # Create new faces bbox for B for faces within searchDist range of bbox A
        bbAMinSD = Vector((bbAMin[0]-searchDist, bbAMin[1]-searchDist, bbAMin[2]-searchDist))
        bbAMaxSD = Vector((bbAMax[0]+searchDist, bbAMax[1]+searchDist, bbAMax[2]+searchDist))
        bbBMinF2, bbBMaxF2, bbBCenterF2, areaB2 = boundaryBoxFaces(objB, 1, selMin=bbAMinSD, selMax=bbAMaxSD)

        ### Check if detected contact area is implausible high compared to the total surface area of the objects
        areaAtot = 0; areaBtot = 0
        for face in objA.data.polygons: areaAtot += face.area
        for face in objB.data.polygons: areaBtot += face.area
        if areaA >= areaAtot /2 or areaB >= areaBtot /2: 
            if areaA > 0:
                if areaA < areaAtot /2: geoContactAreaF = areaA
                bbAMin, bbAMax, bbACenter = bbAMinF, bbAMaxF, bbACenterF
            if areaB > 0:
                if areaB < areaBtot /2: geoContactAreaF = areaB
                bbBMin, bbBMax, bbBCenter = bbBMinF, bbBMaxF, bbBCenterF
        # Use the smallest detected area of both objects as contact area
        elif areaA > 0 and areaB > 0:
            geoContactAreaF = min(areaA, areaB)
            bbAMin, bbAMax, bbACenter = bbAMinF, bbAMaxF, bbACenterF
            bbBMin, bbBMax, bbBCenter = bbBMinF, bbBMaxF, bbBCenterF
        # Or if only one area is greater zero then use that one
        elif areaA > 0:
            geoContactAreaF = areaA
            bbAMin, bbAMax, bbACenter = bbAMinF, bbAMaxF, bbACenterF
        elif areaB > 0:
            geoContactAreaF = areaB
            bbBMin, bbBMax, bbBCenter = bbBMinF, bbBMaxF, bbBCenterF
        ### Alternatively use regular search distance face areas to derive locations from (but not for contact area as it may be too inaccurate)
        # Use the smallest detected area of both objects as contact area
        elif sDistFallb and areaA2 > 0 and areaB2 > 0:
            bbAMin, bbAMax, bbACenter = bbAMinF2, bbAMaxF2, bbACenterF2
            bbBMin, bbBMax, bbBCenter = bbBMinF2, bbBMaxF2, bbBCenterF2
        # Or if only one area is greater zero then use that one
        elif sDistFallb and areaA2 > 0:
            bbAMin, bbAMax, bbACenter = bbAMinF2, bbAMaxF2, bbACenterF2
        elif sDistFallb and areaB2 > 0:
            bbBMin, bbBMax, bbBCenter = bbBMinF2, bbBMaxF2, bbBCenterF2
        elif not sDistFallb: qSkipConnect = 1

        ### Calculate overlap of face based boundary boxes rather than simple boundary box overlap
        if areaA > 0 and areaB > 0:
            overlapXF = min(bbAMaxF[0],bbBMaxF[0]) -max(bbAMinF[0],bbBMinF[0])
            overlapYF = min(bbAMaxF[1],bbBMaxF[1]) -max(bbAMinF[1],bbBMinF[1])
            overlapZF = min(bbAMaxF[2],bbBMaxF[2]) -max(bbAMinF[2],bbBMinF[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDistMesh or overlapYF < -searchDistMesh or overlapZF < -searchDistMesh:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        if areaA > 0:
            overlapXF = min(bbAMaxF[0],bbBMax[0]) -max(bbAMinF[0],bbBMin[0])
            overlapYF = min(bbAMaxF[1],bbBMax[1]) -max(bbAMinF[1],bbBMin[1])
            overlapZF = min(bbAMaxF[2],bbBMax[2]) -max(bbAMinF[2],bbBMin[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDistMesh or overlapYF < -searchDistMesh or overlapZF < -searchDistMesh:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        if areaB > 0:
            overlapXF = min(bbAMax[0],bbBMaxF[0]) -max(bbAMin[0],bbBMinF[0])
            overlapYF = min(bbAMax[1],bbBMaxF[1]) -max(bbAMin[1],bbBMinF[1])
            overlapZF = min(bbAMax[2],bbBMaxF[2]) -max(bbAMin[2],bbBMinF[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDistMesh or overlapYF < -searchDistMesh or overlapZF < -searchDistMesh:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        ### Alternatively use overlap of face based boundary boxes based on regular search distance
        elif sDistFallb and areaA2 > 0 and areaB2 > 0:
            overlapXF = min(bbAMaxF2[0],bbBMaxF2[0]) -max(bbAMinF2[0],bbBMinF2[0])
            overlapYF = min(bbAMaxF2[1],bbBMaxF2[1]) -max(bbAMinF2[1],bbBMinF2[1])
            overlapZF = min(bbAMaxF2[2],bbBMaxF2[2]) -max(bbAMinF2[2],bbBMinF2[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDist or overlapYF < -searchDist or overlapZF < -searchDist:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        elif sDistFallb and areaA2 > 0:
            overlapXF = min(bbAMaxF2[0],bbBMax[0]) -max(bbAMinF2[0],bbBMin[0])
            overlapYF = min(bbAMaxF2[1],bbBMax[1]) -max(bbAMinF2[1],bbBMin[1])
            overlapZF = min(bbAMaxF2[2],bbBMax[2]) -max(bbAMinF2[2],bbBMin[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDist or overlapYF < -searchDist or overlapZF < -searchDist:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        elif sDistFallb and areaB2 > 0:
            overlapXF = min(bbAMax[0],bbBMaxF2[0]) -max(bbAMin[0],bbBMinF2[0])
            overlapYF = min(bbAMax[1],bbBMaxF2[1]) -max(bbAMin[1],bbBMinF2[1])
            overlapZF = min(bbAMax[2],bbBMaxF2[2]) -max(bbAMin[2],bbBMinF2[2])
            # If one axis is out of search distance range then fall back to simple boundary box based overlap
            if overlapXF < -searchDist or overlapYF < -searchDist or overlapZF < -searchDist:
                  qSkipConnect = 1
            else: overlapX, overlapY, overlapZ = max(0,overlapXF), max(0,overlapYF), max(0,overlapZF)
        elif not sDistFallb: qSkipConnect = 1
                
    if not qAccurate or qSkipConnect or sDistFallb:
        ### Calculate simple overlap of boundary boxes for contact area calculation (project along all axis')
        overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
        overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
        overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
    
    if not qSkipConnect or props.surfaceForced:

        ### Calculate area based on either the sum of all axis surfaces...
        if not qNonManifold:
            overlapAreaX = overlapY *overlapZ
            overlapAreaY = overlapX *overlapZ
            overlapAreaZ = overlapX *overlapY
            # Add up all contact areas
            geoContactAreaB = overlapAreaX +overlapAreaY +overlapAreaZ
                
        ### Or calculate contact area based on predefined custom thickness
        elif props.surfaceForced:
            geoContactAreaB = (overlapX +overlapY +overlapZ) *props.surfaceThickness
        else:
            geoContactAreaB = 0

        ### Calculate alternative contact area from object dimensions
        dimA = objA.dimensions
        dimB = objB.dimensions
        # We use the surface area of the smallest side since we don't want to artificially strengthen the structure in case later sanity check fails
        areaA = min(min(dimA[0]*dimA[1], dimA[0]*dimA[2]), dimA[1]*dimA[2])
        areaB = min(min(dimB[0]*dimB[1], dimB[0]*dimB[2]), dimB[1]*dimB[2])
        geoContactAreaD = min(areaA, areaB)

        ### Sanity check: in case no boundary box intersection is found use element dimensions based contact area as fallback 
        if geoContactAreaB > 0: geoContactArea = geoContactAreaB
        else:                   geoContactArea = geoContactAreaD

        # Sanity check: contact area based on faces is expected to be smaller than boundary box and dimensions contact area, only then use face based contact area
        qVolCorrect = 0
        if geoContactAreaF < geoContactArea and geoContactAreaF > 0:
            geoContactArea = geoContactAreaF
        elif not qNonManifold:
            qVolCorrect = 1
        
        ### Find out element thickness to be used for bending threshold calculation 
        if geoContactAreaB > 0:
            geo = [overlapX, overlapY, overlapZ]
            geoAxis = [1, 2, 3]
            geo, geoAxis = zip(*sorted(zip(geo, geoAxis)))
            geoHeight = geo[1]  # First item = mostly 0, second item = thickness/height, third item = width 
            geoWidth = geo[2]
        else:
            geoAxis = [0, 0, 0]
            geoHeight = geoContactArea**0.5
            geoWidth = geoHeight
        
        # Add custom thickness to contact area (only for manifolds as it is already included in non-manifolds)
        if not qNonManifold:
            geoContactArea += geoWidth *props.surfaceThickness
        
        ### Use center of contact area boundary box as constraints location
        centerX = (max(bbAMin[0],bbBMin[0]) + min(bbAMax[0],bbBMax[0])) /2
        centerY = (max(bbAMin[1],bbBMin[1]) + min(bbAMax[1],bbBMax[1])) /2
        centerZ = (max(bbAMin[2],bbBMin[2]) + min(bbAMax[2],bbBMax[2])) /2
        
        center = Vector((centerX, centerY, centerZ))
        #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon

        return geoContactArea, geoHeight, geoWidth, center, geoAxis, qVolCorrect

    return 0, 0, 0, Vector((0,0,0)), [1,2,3], 0  # Dummy data, connection will be remove later because of zero area anyway

########################################

def calculateContactAreaBasedOnBoundaryBoxesForAll(objs, objsEGrp, connectsPair, qAccurate):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    props = bpy.context.window_manager.bcb
    elemGrps = global_vars.elemGrps

    ### Prepare dictionary of element indices for faster item search (optimization)
    objsDict = {}
    for i in range(len(objs)):
        objsDict[objs[i]] = i
    
    connectsGeo = []
    connectsLoc = []
    connectsPair_iter = iter(connectsPair)
    for i in range(len(connectsPair)):
        pair = next(connectsPair_iter)   
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        
        ### Get Search Distance Fallback setting
        if not props.searchDistanceFallback:
            elemGrpA = objsEGrp[objsDict[objA]] 
            elemGrpB = objsEGrp[objsDict[objB]]
            elemGrps_elemGrpA = elemGrps[elemGrpA]
            elemGrps_elemGrpB = elemGrps[elemGrpB]
            Prio_A = elemGrps_elemGrpA[EGSidxPrio]
            Prio_B = elemGrps_elemGrpB[EGSidxPrio]
            if Prio_A == Prio_B:  # Priority is the same for both element groups
                sDistFallb_A = elemGrps_elemGrpA[EGSidxSDFl]
                sDistFallb_B = elemGrps_elemGrpB[EGSidxSDFl]
                sDistFallb = sDistFallb_A or sDistFallb_B
            if Prio_A > Prio_B:  # Priority is higher for A
                sDistFallb = elemGrps_elemGrpA[EGSidxSDFl]
            elif Prio_A < Prio_B:  # Priority is higher for B
                sDistFallb = elemGrps_elemGrpB[EGSidxSDFl]
        else:
            sDistFallb = 1
        
        ### Check if meshes are water tight (non-manifold)
        nonManifolds = []
        for obj in [objA, objB]:
            bpy.context.scene.objects.active = obj
            me = obj.data
            # Find non-manifold elements
            bm = bmesh.new()
            bm.from_mesh(me)
            nonManifolds.extend([i for i, ele in enumerate(bm.edges) if not ele.is_manifold])
            bm.free()

        ###### Calculate contact area for a single pair of objects
        geoContactArea, geoHeight, geoWidth, center, geoAxis, qVolCorrect = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, sDistFallb, qAccurate=qAccurate, qNonManifold=len(nonManifolds))
                    
        # Geometry array: [area, height, width, axisNormal, axisHeight, axisWidth, qVolCorrect]
        connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2], qVolCorrect])
        connectsLoc.append(center)
        
    return connectsGeo, connectsLoc

################################################################################   

def calculateContactAreaBasedOnBooleansForAll(objs, objsEGrp, connectsPair):
    
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
        nonManifolds = []
        for obj in [objA, objB]:
            bpy.context.scene.objects.active = obj
            me = obj.data
            # Find non-manifold elements
            bm = bmesh.new()
            bm.from_mesh(me)
            nonManifolds.extend([i for i, ele in enumerate(bm.edges) if not ele.is_manifold])
            bm.free()

        ###### If non-manifold then calculate a contact area estimation based on boundary boxes intersection and a user defined thickness
        if len(nonManifolds):

            #print('Warning: Mesh not water tight, non-manifolds found:', obj.name)

            ###### Calculate contact area for a single pair of objects
            geoContactArea, geoHeight, geoWidth, center, geoAxis, qVolCorrect = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, sDistFallb, qNonManifold=1)
            
            # Geometry array: [area, height, width, axisNormal, axisHeight, axisWidth]
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2], qVolCorrect])
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
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoAxis[0], geoAxis[1], geoAxis[2], 0])
            connectsLoc.append(center)
                
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    try:    bpy.data.scenes.remove(sceneTemp, do_unlink=1)
    except: bpy.data.scenes.remove(sceneTemp)
    
    print()
    return connectsGeo, connectsLoc

################################################################################   

def applyDisplacementCorrection(objs, objsEGrp, connectsPair, connectsLoc):

    elemGrps = global_vars.elemGrps

    ### Prepare dictionary of element indices for faster item search (optimization)
    objsDict = {}
    for i in range(len(objs)):
        objsDict[objs[i]] = i
    
    ### Create group index with their respective objects
    grpsObjs = {}
    for elemGrp in elemGrps:
        grpName = elemGrp[EGSidxName]
        grpObjs = []
        for obj in objs:
            if elemGrp == elemGrps[objsEGrp[objsDict[obj]]]:
                grpObjs.append(obj)
        grpsObjs[grpName] = grpObjs
    
    vLocDataCnt = 0
    for elemGrp in elemGrps:
        grpDCor = elemGrp[EGSidxDCor]
        if grpDCor:
            grpName = elemGrp[EGSidxName]
            for obj in grpsObjs[grpName]:
                for vert in obj.data.vertices:
                    vLocDataCnt += 1

    # Import data from file
    if vLocDataCnt:
        filePath = os.path.join(logPath, "bcb-diff-%d.cfg" %vLocDataCnt)
        if os.path.exists(filePath):
            print("Displacement correction vertices: %d" %vLocDataCnt)
            print("Importing displacement correction data from:", filePath)
            vLocData = dataFromFile(filePath, qPickle=True, qCompressed=True)
            
            if vLocData != 1 and len(vLocData):

                ### Build kd-trees for every object's vertices
                objsKd = []
                for obj in objs:
                    me = obj.data
                    mat = obj.matrix_world
                    
                    kd = mathutils.kdtree.KDTree(len(me.vertices))
                    for i, v in enumerate(me.vertices):
                        loc = mat *v.co    # Multiply matrix by vertex coordinates to get global coordinates
                        kd.insert(loc, i)
                    kd.balance()
                    objsKd.append(kd)
                                    
                ### Apply differences to the vertices of the input meshes
                vIdx = 0
                for elemGrp in elemGrps:
                    grpDCor = elemGrp[EGSidxDCor]
                    if grpDCor:
                        grpName = elemGrp[EGSidxName]
                        for obj in grpsObjs[grpName]:
                            for vert in obj.data.vertices:
                                vert.co -= Vector(vLocData[vIdx])
                                vIdx += 1
                                
                # If changes have been made
                if vIdx > 0:
                    # Set object centers to geometry origin (again after prepareObjects())
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

                    ### Apply corrections also on connection locations
                    connectsPair_iter = iter(connectsPair)
                    connectsLoc_iter = iter(connectsLoc)
                    for k in range(len(connectsPair)):
                        pair = next(connectsPair_iter)   
                        loc = next(connectsLoc_iter)
                        objA = objs[pair[0]]
                        objB = objs[pair[1]]
                        objKdA = objsKd[pair[0]]
                        objKdB = objsKd[pair[1]]
                        
                        # Find closest vertices via kd-tree in comparison objects A and B
                        vertAco, vertAidx = objKdA.find(loc)[:2]
                        vertBco, vertBidx = objKdB.find(loc)[:2]
                        coClosestAidx = objKdA.find(loc)[0]
                        coClosestB = objKdB.find(loc)[0]
                        center = (vertAco +vertBco) /2   # Calculate center of both original vertices
                        
                        vertAcoNew = objA.matrix_world *objA.data.vertices[vertAidx].co
                        vertBcoNew = objB.matrix_world *objB.data.vertices[vertBidx].co
                        centerNew = (vertAcoNew +vertBcoNew) /2   # Calculate center of both corrected vertices
                        
                        # Apply the difference of the closest vertices of both objects to the location of the connection
                        diff = center -centerNew
                        connectsLoc[k] = loc -diff
       
    return connectsLoc
       
################################################################################   

def deleteConnectionsWithZeroContactArea(objs, objsEGrp, connectsPair, connectsGeo, connectsLoc):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")

    props = bpy.context.window_manager.bcb
    elemGrps = global_vars.elemGrps
    connectCntOld = len(connectsPair)
    connectCnt = 0
    
    ### Prepare dictionary of element indices for faster item search (optimization)
    objsDict = {}
    for i in range(len(objs)):
        objsDict[objs[i]] = i

    connectsPairTmp = []
    connectsGeoTmp = []
    connectsLocTmp = []
    connectsPair_iter = iter(connectsPair)
    for i in range(len(connectsPair)):
        pair = next(connectsPair_iter)   
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        elemGrpA = objsEGrp[objsDict[objA]] 
        elemGrpB = objsEGrp[objsDict[objB]]
        elemGrps_elemGrpA = elemGrps[elemGrpA]
        elemGrps_elemGrpB = elemGrps[elemGrpB]
        CT_A = elemGrps_elemGrpA[EGSidxCTyp]
        CT_B = elemGrps_elemGrpB[EGSidxCTyp]
        Prio_A = elemGrps_elemGrpA[EGSidxPrio]
        Prio_B = elemGrps_elemGrpB[EGSidxPrio]
        geoContactArea = connectsGeo[i][0]
        
        # Both A and B are active groups and priority is the same
        if CT_A != 0 and CT_B != 0 and Prio_A == Prio_B:
            ### Use the connection type with the smaller count of constraints for connection between different element groups
            ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
            if connectTypes[CT_A][1] <= connectTypes[CT_B][1]:
                  CT = CT_A; elemGrp = elemGrpA
            else: CT = CT_B; elemGrp = elemGrpB
            elemGrps_elemGrp = elemGrps[elemGrp]
            disColPerm = elemGrps_elemGrp[EGSidxDClP]
        else: disColPerm = 0
        
        ### Keep connection with non-zero contact area or if collision suppression connection
        if geoContactArea >= minimumContactArea or props.disableCollisionPerm or disColPerm:
            # Mark as zero (special case for collision suppression connections)
            if geoContactArea < minimumContactArea:
                connectsGeo[i][0] = 0
            # Copy connection data
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

def deleteConnectionsWithReferences(objs, emptyObjs, connectsPair, connectsGeo, connectsLoc):
    
    ### Delete connections with references from predefined constraints
    if debug: print("Deleting connections with predefined constraints...")

    props = bpy.context.window_manager.bcb    
    connectsPairTmp = []
    connectsGeoTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    connectsPair_iter = iter(connectsPair)
    for i in range(len(connectsPair)):
        pair = next(connectsPair_iter)   
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        qKeep = 1
        for objConst in emptyObjs:
            objAc = objConst.rigid_body_constraint.object1
            objBc = objConst.rigid_body_constraint.object2
            if (objA == objAc and objB == objBc) or (objA == objBc and objB == objAc):
                qKeep = 0; break
        if qKeep:
            connectsPairTmp.append(connectsPair[i])
            connectsGeoTmp.append(connectsGeo[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsGeo = connectsGeoTmp
    connectsLoc = connectsLocTmp
    
    print("Connections skipped due to predefined constraints:", connectCntOld -connectCnt)
    return connectsPair, connectsGeo, connectsLoc

################################################################################   

def createConnectionData(objs, objsEGrp, connectsPair, connectsLoc, connectsGeo):
    
    ### Create connection data
    if debug: print("Creating connection data...")
    
    props = bpy.context.window_manager.bcb    
    elemGrps = global_vars.elemGrps
    connectsConsts = []
    constsConnect = []
    constCntOfs = 0
    for i in range(len(connectsPair)):
        geoContactArea = connectsGeo[i][0]
        elemGrp = None
        
        ### Count constraints by connection type preset

        pair = connectsPair[i]
        loc = connectsLoc[i]

        elemGrpA = objsEGrp[pair[0]]
        elemGrpB = objsEGrp[pair[1]]
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        elemGrps_elemGrpA = elemGrps[elemGrpA]
        elemGrps_elemGrpB = elemGrps[elemGrpB]
        CT_A = elemGrps_elemGrpA[EGSidxCTyp]
        CT_B = elemGrps_elemGrpB[EGSidxCTyp]
        Prio_A = elemGrps_elemGrpA[EGSidxPrio]
        Prio_B = elemGrps_elemGrpB[EGSidxPrio]
        NoHoA = elemGrps_elemGrpA[EGSidxNoHo]
        NoHoB = elemGrps_elemGrpB[EGSidxNoHo]
        NoCoA = elemGrps_elemGrpA[EGSidxNoCo]
        NoCoB = elemGrps_elemGrpB[EGSidxNoCo]

        ### Check if connection between different groups is not allowed and remove them
        qNoCon = 0
        if elemGrpA != elemGrpB:
            if (NoCoA or NoCoB) and CT_A != 0 and CT_B != 0 and Prio_A == Prio_B: qNoCon = 1
            ### Check if horizontal connection between different groups and remove them (e.g. for masonry walls touching a framing structure)
            ### This code is used 3x, keep changes consistent in: builder_prep.py, builder_setc.py, and tools.py
            elif NoHoA or NoHoB:
                dirVecA = Vector(loc) -objA.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
                dirVecAN = dirVecA.normalized()
                if abs(dirVecAN[2]) > 0.7: qA = 1
                else: qA = 0
                dirVecB = Vector(loc) -objB.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
                dirVecBN = dirVecB.normalized()
                if abs(dirVecBN[2]) > 0.7: qB = 1
                else: qB = 0
                if qA == 0 and qB == 0: qNoCon = 1

        ### Decision on which material settings from both groups will be used for connection
        if not qNoCon:
            # Both A and B are active groups and priority is the same
            if CT_A != 0 and CT_B != 0 and Prio_A == Prio_B:
                ### Use the connection type with the smaller count of constraints for connection between different element groups
                ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
                if connectTypes[CT_A][1] <= connectTypes[CT_B][1]:
                      CT = CT_A; elemGrp = elemGrpA
                else: CT = CT_B; elemGrp = elemGrpB
            # Only A is active and B is passive group or priority is higher for A
            elif CT_A != 0 and CT_B == 0 or (CT_A != 0 and CT_B != 0 and Prio_A > Prio_B):
                CT = CT_A; elemGrp = elemGrpA
            # Only B is active and A is passive group or priority is higher for B
            elif CT_A == 0 and CT_B != 0 or (CT_A != 0 and CT_B != 0 and Prio_A < Prio_B):
                CT = CT_B; elemGrp = elemGrpB
            # Both A and B are in passive group but either one is actually an active RB (a xor b)
            elif CT_A == 0 and CT_B == 0 and bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
                CT = -1; elemGrp = elemGrpA  # Only one fixed constraint is used to connect these (buffer special case)
            # Both A and B are in passive group and both are an active RB (connections for buffer elements)
            elif CT_A == 0 and CT_B == 0 and (objA.rigid_body.type == 'ACTIVE' and objB.rigid_body.type == 'ACTIVE'):
                disColPerm = elemGrps[elemGrpA][EGSidxDClP]
                if disColPerm: CT = -1; elemGrp = elemGrpA  # Exception to enable collision suppression connections between buffer elements
            else:  # Both A and B are in passive group and both are passive RBs
                CT = 0
            # For unbreakable passive connections above settings can be overwritten
            if not props.passiveUseBreaking:
                # Both A and B are in passive group but either one is actually an active RB (a xor b)
                if CT_A == 0 and CT_B == 0 and bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
                    CT = -1; elemGrp = elemGrpA  # Only one fixed constraint is used to connect these (buffer special case)
                # Both A and B are in passive group and both are an active RB (connections for buffer elements)
                elif CT_A == 0 and CT_B == 0 and (objA.rigid_body.type == 'ACTIVE' and objB.rigid_body.type == 'ACTIVE'):
                    disColPerm = elemGrps[elemGrpA][EGSidxDClP]
                    if disColPerm: CT = -1; elemGrp = elemGrpA  # Exception to enable collision suppression connections between buffer elements

        elif qNoCon: CT = 0

        ### CT is now known and we can prepare further settings accordingly

        if CT > 0: constCnt = connectTypes[CT][1]
        elif CT == 0: constCnt = 0
        elif CT < 0: constCnt = 1

        if elemGrp != None:
            elemGrps_elemGrp = elemGrps[elemGrp]
            disColPerm = elemGrps_elemGrp[EGSidxDClP]
        
        elif elemGrp == None:
            constCnt = 0    
            disColPerm = 0

        ### If invalid contact area
        if geoContactArea == 0:
            constCnt = 0    
            # Both A and B are active groups and priority is the same
            if CT_A != 0 and CT_B != 0 and Prio_A == Prio_B:
                ### Use the connection type with the smaller count of constraints for connection between different element groups
                ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
                if connectTypes[CT_A][1] <= connectTypes[CT_B][1]:
                      CT = CT_A; elemGrp = elemGrpA
                else: CT = CT_B; elemGrp = elemGrpB
                elemGrps_elemGrp = elemGrps[elemGrp]
                disColPerm = elemGrps_elemGrp[EGSidxDClP]
            else: disColPerm = 0

        # Add one extra slot for a possible constraint for permanent collision suppression
        if props.disableCollisionPerm or disColPerm: constCnt += 1

        # In case the connection type is passive or unknown reserve no space for constraints (connectsConsts needs to stay in sync with connectsPair)
        if constCnt == 0: connectsConsts.append([])
        # Otherwise reserve space for the predefined constraints count
        else:
            # Reserve constraint slots
            items = []
            for j in range(constCnt):
                items.append(constCntOfs +j)
                constsConnect.append(i)
            connectsConsts.append(items)
            constCntOfs += len(items)
    
    return connectsConsts, constsConnect

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
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
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
            if sceneTemp.rigidbody_world == None:
                bpy.ops.rigidbody.world_add()
            for grp in bpy.data.groups:
                if "RigidBodyWorld" == grp.name and not grp.is_library_indirect:
                    bpy.context.scene.rigidbody_world.group = grp; break
            for grp in bpy.data.groups:
                if "RigidBodyConstraints" == grp.name and not grp.is_library_indirect:
                    bpy.context.scene.rigidbody_world.constraints = grp; break
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
            aIndex = []; aCo = []  #; aDist = [];
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
    
    elemGrps = global_vars.elemGrps

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
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
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
    
    elemGrps = global_vars.elemGrps

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
    
    elemGrps = global_vars.elemGrps

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
    print("Calculating masses from preset materials... (Children: %d)" %len(childObjs))
     
    props = bpy.context.window_manager.bcb
    elemGrps = global_vars.elemGrps

    ### Prepare objects index lookup dictionary for faster access
    objsIndex = {}
    for k in range(len(objs)):
        objsIndex[objs[k].name] = k

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Find non-manifold meshes (not suited for volume based mass calculation)
    objsNonMan = []
    if props.surfaceThickness:
        objsAll = objs
        objsAll.extend(childObjs)
        for obj in objsAll:
            bpy.context.scene.objects.active = obj
            me = obj.data
            # Find non-manifold elements
            bm = bmesh.new()
            bm.from_mesh(me)
            nonManifolds = [i for i, ele in enumerate(bm.edges) if not ele.is_manifold]
            bm.free()
            if len(nonManifolds): objsNonMan.append(obj)
        print("Non-manifold elements found:", len(objsNonMan))

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
            if objsEGrp[k] == j:  # If object is in current element group
                obj = objs[k]
                if obj != None and obj.rigid_body != None:
                    CT = elemGrps[j][EGSidxCTyp]
                    if CT == 0:
                        # The foundation buffer objects need a large mass so they won't pushed away
                        materialDensity = elemGrp[EGSidxDens]
                        if materialDensity > 1: obj.rigid_body.mass = materialDensity
                        else: obj.rigid_body.mass = 1000  # Backward compatibility for older settings
                    else:
                        try: scale = elemGrps[j][EGSidxScal]  # Try in case elemGrps is from an old BCB version
                        except: qScale = 0
                        else: qScale = 1
                        if obj != None:
                            if "bcb_child" in obj.keys():
                                obj = scene.objects[obj["bcb_child"]]
                            if (props.surfaceForced == 0 or props.surfaceThickness == 0) and (props.surfaceThickness == 0 or obj not in objsNonMan):
                                obj.select = 1
                                objsSelected.append(obj)
                                # Temporarily revert element scaling for mass calculation
                                if qScale:
                                    if scale != 0 and scale != 1:
                                        obj.scale /= scale
                                        objsTotal.append(obj)
                                        objsScale.append(scale)

        ### Calculating and applying material masses based on volume
        materialPreset = elemGrp[EGSidxMatP]
        materialDensity = elemGrp[EGSidxDens]
        if not materialDensity:
            if materialPreset != "":
                try: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
                except: print("Warning: Density of 0 set and material preset not found for '%s', can't compute mass and leaving it as is." %elemGrp[EGSidxName])
            else: print("Warning: Density of 0 set and no material preset defined for '%s', can't compute mass and leaving it as is." %elemGrp[EGSidxName])
        else: bpy.ops.rigidbody.mass_calculate(material="Custom", density=materialDensity)

        ### Calculating and applying material masses based on surface area * thickness
        if (props.surfaceForced and props.surfaceThickness) or (props.surfaceThickness and len(objsNonMan)):
            # Find out density of the element group
            if not materialDensity:
                materialPreset = elemGrp[EGSidxMatP]
                if materialPreset != "":
                    try: materialDensity = materialPresets[materialPreset]
                    except:
                        print("Warning: Density of 0 set and material preset not found for '%s', a density of 1000 kg/m^3 is used." %elemGrp[EGSidxName])
                        materialDensity = 1000
                else:
                    print("Warning: Density of 0 set and no material preset defined for '%s', a density of 1000 kg/m^3 is used." %elemGrp[EGSidxName])
                    materialDensity = 1000
            
            if props.surfaceForced: objsNonMan = objs
                
            objsNonManSelected = []
            for n in range(len(objsNonMan)):
                obj = objsNonMan[n]
                k = objsIndex[obj.name]
                if objsEGrp[k] == j:  # If object is in current element group
                    # Calculate object surface area and volume
                    me = obj.data
                    area = sum(f.area for f in me.polygons)
                    volume = area *props.surfaceThickness
                    # Calculate mass
                    obj.rigid_body.mass = volume *materialDensity
                    objsNonManSelected.append(obj)
                                                
        ### Adding live load to masses
        liveLoad = elemGrp[EGSidxLoad]
        for obj in objsSelected:
            dims = obj.dimensions
            floorArea = dims[0] *dims[1]  # Simple approximation by assuming rectangular floor area (x *y)
            if liveLoad > 0: obj.rigid_body.mass += floorArea *liveLoad
            obj["Floor Area"] = floorArea  # Only needed for the diagnostic prints below

        ### Setting friction if we are at it already (could be separate function but not because of 3 lines)
        friction = elemGrp[EGSidxFric]
        for obj in objsSelected:
            obj.rigid_body.friction = friction

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
    for groupName in sorted(groupsMass.keys()):
        try: mass = groupsMass[groupName]
        except: mass = 0
        try: area = groupsArea[groupName]
        except: area = 0
        #if mass != groupsMass["RigidBodyWorld"]:  # Filter all groups that contain the complete structure
        print("Group '%s' mass: %0.0f t and %0.0f kg / Floor area: %0.2f m^2" %(groupName, floor(mass/1000), floor(mass)%1000, area))
    try: mass = groupsMass["RigidBodyWorld"]
    except: mass = 0
    try: area = groupsArea["RigidBodyWorld"]
    except: area = 0
    print("Total mass: %0.0f t and %0.0f kg / Total floor area: %0.2f m^2" %(floor(mass/1000), floor(mass)%1000, area))
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

def correctContactAreaByVolume(objs, objsEGrp, connectsPair, connectsGeo):
    
    ### Correct the preliminary calculated boundary box based contact areas by considering the element volumes
    print("Correcting contact areas...")

    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene
    elemGrps = global_vars.elemGrps

    for j in range(len(elemGrps)):
        elemGrp = elemGrps[j]
        liveLoad = elemGrp[EGSidxLoad]

        ### Find out density of the element group
        materialDensity = elemGrp[EGSidxDens]
        if not materialDensity:
            materialPreset = elemGrp[EGSidxMatP]
            if materialPreset != "":
                try: materialDensity = materialPresets[materialPreset]
                except:
                    print("Warning: Density of 0 set and material preset not found for '%s', can't compute mass and leaving it as is." %elemGrp[EGSidxName])
                    materialDensity = 1
            else:
                print("Warning: Density of 0 set and no material preset defined for '%s', can't compute mass and leaving it as is." %elemGrp[EGSidxName])
                materialDensity = 1

        ### Calculate volumes from densities and derive correctional factors for contact areas
        for k in range(len(objs)):
            if objsEGrp[k] == j:  # If object is in current element group
                obj = objs[k]

                mass = obj.rigid_body.mass

                ### Remove live load from mass if present
                if liveLoad > 0:
                    dims = obj.dimensions
                    floorArea = dims[0] *dims[1]  # Simple approximation by assuming rectangular floor area (x *y) for live load
                    mass -= floorArea *liveLoad

                volume = mass /materialDensity
                
                ### Find out element thickness to be used for bending threshold calculation 
                dim = obj.dimensions; dimAxis = [1, 2, 3]
                dim, dimAxis = zip(*sorted(zip(dim, dimAxis)))
                dimHeight = dim[0]; dimWidth = dim[1]; dimLength = dim[2]

                # Derive contact area correction factor from geometry section area divided by bbox section area
                if dimLength != 0: sectionArea = volume /dimLength  # Full geometry section area of element
                else:              sectionArea = volume**.5         # Assume cube as fallback if length is zero

                ### Compensate section area for rescaling
                try: scale = elemGrp[EGSidxScal]  # Try in case elemGrps is from an old BCB version
                except: pass
                else:
                    if obj != None and scale != 0 and scale != 1:
                        sectionArea *= scale**3  # Cubic instead of square because dimLength is included as well

                ### Determine contact area correction factor
                if dimHeight *dimWidth != 0 and mass != materialDensity:  # Special case: mass = materialDensity only for foundation elements
                    corFac = sectionArea / (dimHeight *dimWidth)
                else: corFac = 1

                obj["CA Corr.Fac."] = corFac
                obj["Density"] = materialDensity
                obj["Volume"] = volume
                    
################################################################################   

def generateDetonator(objs, connectsPair, objsEGrp):
            
    scene = bpy.context.scene
    props = bpy.context.window_manager.bcb
    elemGrps = global_vars.elemGrps

    print("\nPreprocessing detonation simulation...")

    connectsBtMul = [1 for i in connectsPair]

    ### Get detonator objects
    detonatorObjs = []
    if props.detonAdvanced:
        if len(props.detonatorObj):
            for obj in scene.objects:
                if props.detonatorObj in obj.name and "_Push" not in obj.name and "_Pull" not in obj.name:
                    detonatorObjs.append(obj)
    if len(detonatorObjs) == 0:
        if props.detonAdvanced:
            print("Warning: No detonator object found, skipping advanced blast wave simulation.")
        return connectsBtMul

    ### Sort out user-defined objects (members of a specific group)
    grpName = "bcb_noDetonator"
    objsDetonSkip = []
    for grp in bpy.data.groups:
        if grpName in grp.name:
            for obj in objs:
                if obj.name in grp.objects:
                    objsDetonSkip.append(obj)
            if len(objsDetonSkip): print("Elements skipped by '%s' group:" %grp.name, len(objsDetonSkip))

    ### Count average element data per element for the entire structure
    elemArea = 0
    elemVolume = 0
    elemMass = 0
    for idx in range(len(objs)):
        obj = objs[idx]
        # Area
        dim = obj.dimensions; dimAxis = [1, 2, 3]
        dim, dimAxis = zip(*sorted(zip(dim, dimAxis)))
        elemArea += dim[1] *dim[2]
        # Volume
        elemGrp = objsEGrp[idx]
        elemGrps_elemGrp = elemGrps[elemGrp]
        materialDensity = elemGrps_elemGrp[EGSidxDens]
        if materialDensity > 0: elemVolume += obj.rigid_body.mass /materialDensity
        # Mass
        elemMass += obj.rigid_body.mass
    objsCnt = len(objs)
    if objsCnt:
        elemArea /= objsCnt
        elemVolume /= objsCnt
        elemMass /= objsCnt
    if elemVolume > 0: elemDensity = elemMass /elemVolume
    else: elemDensity = 0
    print("Average element stats for detonation simulation:")
    print("  Area: %0.3f m^2 (%0.3f m)" %(elemArea, elemArea**0.5))  # Not used
    print("  Volume: %0.3f m^3" %elemVolume)                         # Not used
    print("  Mass: %0.3f kg" %elemMass)                              # Not used
    print("  Density: %0.3f kg/m^3" %elemDensity)                    # Not used

    ###### Detect the confined/open space ratio at each element using ray casting
    print("Searching confined spaces for detonation simulation... (%d)" %objsCnt)

    ### Vars
    if objsCnt <= 4000: raySamples = 1      # Number of random rays per element to be used for ray casting
    else:                 raySamples = 1      # (1 = enables a faster normal estimation based method instead of brute force sampling)
    TNTequivalent = 1                         # TNT equivalent Qexplosive/Qtnt, where Q are energies of explosion
    qClampLowest  = 0                         # Enables clamping of the lowest outliers to ensure simulation stability using a non-linear gradient (experimental)
    qDirectImpact = 1                         # Enables directional blast impact (experimental)
    objsRatioMerge = 5                        # Merge the open space ratios for that many objects withing ray length distance to smooth out results (0 = off)
    rayDist       = props.detonRayDist        # Maximum distance in m for ray casting for confined space detection
    deflection    = props.detonDeflection     # Detonation deflection multiplier for open/confined spaces. Larger values will increase the blast wave impact on revealed structures such as outside walls compared to protected elements inside of buildings (0 = no difference)

    if raySamples > 1: print("Ray sampling method: Accurate")
    else:              print("Ray sampling method: Optimized")

    random.seed(0)

    for detonatorObj in detonatorObjs:
        objsDetonRatio = []
        objsCoLen = [0] *objsCnt
        objsCoIdxs = [[]] *objsCnt
        for i in range(objsCnt):
            sys.stdout.write('\r' +"%d" %i)
            obj = objs[i]
            raySamplesOpen = 0
            co_len = 0
            
            ### Use brute force sampling if enough samples are available
            for raySample in range(raySamples):
                rayObj = rayObjLast = obj
                rayLoc = rayObj.location

                qRayCast = 1
                if raySample == 0:
                    ### Build kd-tree for object locations
                    kdObjs = mathutils.kdtree.KDTree(objsCnt)
                    for j, ob in enumerate(objs):
                        kdObjs.insert(ob.location, j)
                    kdObjs.balance()
                    ### Find closest objects via kd-tree
                    co_find = obj.location
                    aIndex = []; aCo = []  #; aDist = []
                    for (co, index, dist) in kdObjs.find_range(co_find, rayDist):
                        aIndex.append(index); aCo.append(co)  #; aDist.append(dist)
                    aIndex = aIndex[1:]; aCo = aCo[1:]  # Remove first item because it's the same as co_find (zero distance)
                    ### Average all found elements locations
                    co_aver = Vector((0, 0, 0))
                    for co in aCo: co_aver += co
                    co_len = len(aCo)
                    if co_len == 0: rayObjLast = 0  # Skip ray cast
                    else:
                        co_aver /= co_len
                        rayDir = rayDir0 = (rayLoc -co_aver).normalized()
                        objsCoLen[i] = co_len
                        objsCoIdxs[i] = aIndex
                else:
                    rayDir = Vector((random.random()*2-1, random.random()*2-1, random.random())).normalized()
                    
                ### Walk along ray until leaving original element and find the next one within range
                while rayObj == rayObjLast:
                    rayObjLast = rayObj
                    rayRes, rayLoc, rayNor, rayIdx, rayObj, rayMtx = scene.ray_cast(rayLoc+rayDir/1000, rayDir, distance=rayDist)
                if not rayRes: raySamplesOpen += 1  # No other object found within range
                # Debug:
                #if rayRes: bpy.ops.mesh.primitive_ico_sphere_add(size=.5, view_align=False, enter_editmode=False, location=rayLoc)

            if raySamples == 1:
                if co_len == 0:   openSpaceRatio = 1
                elif co_len == 1: openSpaceRatio = raySamplesOpen *.75
                elif co_len >= 2: openSpaceRatio = raySamplesOpen *.5
            else:
                openSpaceRatio = raySamplesOpen /raySamples
                
            ### Directional blast impact
            if qDirectImpact:
                if co_len > 0:
                    detonDir = detonatorObj.location -obj.location
                    angle = rayDir0.angle(detonDir, -1)
                    if angle >= 0:                                            # Front, side, back
                        #openSpaceRatio *= 1 -(angle /3.14159)                # 1, 0.5, 0
                        #openSpaceRatio *= min(1, 1.5 -(angle /3.14159))      # 1, 1, 0.5
                        openSpaceRatio *= min(1, 2 -(angle /3.14159) *2)     # 1, 1, 0
                        #openSpaceRatio *= min(1, 3 -(angle /3.14159) *3)      # 1, 1, 1, 0
                        #openSpaceRatio *= min(1, 2 -(angle /3.14159) *1.5)   # 1, 1, 1, 0.5
                        #openSpaceRatio *= min(1, 2.5 -(angle /3.14159) *2)   # 1, 1, 1, 1, 0.5

            if obj not in objsDetonSkip: obj['DetonRatio'] = openSpaceRatio
            objsDetonRatio.append(openSpaceRatio)
        print()

        ### Merging of open space ratios for objects withing ray length distance to smooth out results
        if objsRatioMerge:
            for i in range(objsCnt):
                co_len = objsCoLen[i]
                if co_len > 0:
                    obj = objs[i]
                    idxs = objsCoIdxs[i]
                    openSpaceRatio = 0
                    idxCnt = 1
                    for idx in idxs:
                        #openSpaceRatio += objsDetonRatio[idx]          # Equally balanced samples
                        openSpaceRatio += objsDetonRatio[idx] /idxCnt  # Balanced by importance
                        if idxCnt == min(co_len, objsRatioMerge): break
                        idxCnt += 1
                    #openSpaceRatio /= min(co_len, objsRatioMerge)        # Equally balanced samples
                    openSpaceRatio /= 2 -1 /min(co_len, objsRatioMerge)  # Balanced by importance
                    if obj not in objsDetonSkip: obj['DetonRatioMerge'] = openSpaceRatio
                    objsDetonRatio[i] = openSpaceRatio
            
        ###### Transfer data to related constraints
        connectsBtMulNew = []
        connectsPair_iter = iter(connectsPair)
        cntBtMulZero = 0
        btMultiplierAver = 0; btMultiplierAverCnt = 0
        for k in range(len(connectsPair)):
            pair = next(connectsPair_iter)
            objA = objs[pair[0]]
            objB = objs[pair[1]]
            if objA not in objsDetonSkip or objB not in objsDetonSkip:
                objAratio = objsDetonRatio[pair[0]]
                objBratio = objsDetonRatio[pair[1]]
                # Use average confined/open space ratio for connection
                openSpaceRatio = (objAratio +objBratio) /2
                # Value will be considered in breaking threshold multiplier as we only have homogenous strength force fields in Blender.
                # The force field magnitude will be rescaled accordingly, so that the pressure wave won't produce more damage than to be expected.
                btMultiplier = max(0, 1 -(openSpaceRatio *deflection))
            else:
                btMultiplier = 1
            if btMultiplier == 0:
                btMultiplier = 0.001  # Minimum multiplier, could be a setting in UI but leaving it hard-coded for now 
                cntBtMulZero += 1
            connectsBtMulNew.append(btMultiplier)
            if btMultiplier < 1:
                btMultiplierAver += btMultiplier
                btMultiplierAverCnt += 1
        if cntBtMulZero:
            print("Warning: Blast wave correction weakened %d connection(s) to very low strength! Deflection Multiplier likely too high." %cntBtMulZero)

        if btMultiplierAverCnt > 0:
            openSpaceCorrect = btMultiplierAver /btMultiplierAverCnt
            print("Blast wave correction: %0.3f" %openSpaceCorrect)    

            ### Clamp lowest outliers to ensure simulation stability using a non-linear gradient
            if qClampLowest:
                for idx in range(len(connectsBtMulNew)):
                    correctRef = openSpaceCorrect /2
                    if connectsBtMulNew[idx] < correctRef:
                        x = correctRef -connectsBtMulNew[idx]
                        connectsBtMulNew[idx] = correctRef -(1-1/(x+1))

        else: openSpaceCorrect = 1

        # Merge multipliers of multiple detonators
        for idx in range(len(connectsBtMul)):
            connectsBtMul[idx] *= connectsBtMulNew[idx]

        ### Vars
        explosiveMass = props.detonExplosiveMass  # Mass of the explosive in kg
        blastWaveVel  = props.detonBlastWaveVel   # Velocity with which the blast wave is traveling in m/s (depends on frame rate)
        pullBackDelay = props.detonPullBackDelay  # Delay in frames until the negative pressure wave follows the positive one (pressure will be divided by this value to keep overall pressure consistent)
        groundReflect = props.detonGroundReflect  # Enables reflection of the blast wave from the ground by adding duplicate force fields beneath the surface
        startFr = scene.frame_start               # Start frame of the detonation
        endFr = props.timeScalePeriod -pullBackDelay  # Endframe of the effect
        timeScale = props.timeScalePeriodValue    # Pressure wave propagation time scale (depends on frame rate)
        
        # User definitions as possible property of the detonator object
        if "detonExplosiveMass" in detonatorObj.keys():
              explosiveMass = detonatorObj["detonExplosiveMass"]
        if "detonBlastWaveVel" in detonatorObj.keys():
              blastWaveVel = detonatorObj["detonBlastWaveVel"]
        if "detonPullBackDelay" in detonatorObj.keys():
              pullBackDelay = detonatorObj["detonPullBackDelay"]
        if "detonGroundReflect" in detonatorObj.keys():
              groundReflect = bool(detonatorObj["detonGroundReflect"])
        if "detonFrameStart" in detonatorObj.keys():
              startFr = detonatorObj["detonFrameStart"]  

        # Create surface reflection by duplicating the entire emitter
        for isReflection in range(groundReflect +1):
            
            # Create two Empties with only a few settings different
            for typeIdx in range(2):
                
                ### Special handling for different Empties
                if typeIdx == 0:
                    if not isReflection: objName = detonatorObj.name +"_Main_Push"
                    else:                objName = detonatorObj.name +"_Refl_Push"
                    frameOffset = 0
                    sign = 1
                else:
                    if not isReflection: objName = detonatorObj.name +"_Main_Pull"
                    else:                objName = detonatorObj.name +"_Refl_Pull"
                    frameOffset = pullBackDelay
                    sign = -1
                
                ###### Create Empty object
                if objName not in scene.objects:
                    obj = bpy.data.objects.new(objName, None)
                    bpy.context.scene.objects.link(obj)
                    obj.name = objName  # Enforce name even in case it's a duplicate (to avoid '.001')
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.forcefield_toggle()
                else:
                    obj = scene.objects[objName]
                    bpy.context.scene.objects.active = obj

                obj.select = 1
                obj.location = detonatorObj.location  # Use location of detonator object
                if isReflection and obj.location[2] > 1: obj.location[2] = -obj.location[2]
                obj.empty_draw_type = 'SPHERE'
                obj.field.use_min_distance = True
                obj.field.use_max_distance = True
                obj.field.flow = 0  # Flow needs to be disabled as it limits the acting force
                # These vars will be animated
                #obj.field.strength = 0
                #obj.field.distance_min = 0
                #obj.field.distance_max = 0
                
                ### Create new animation curves
                obj.animation_data_create()
                # If current action is already a "Motion" one then output a hint
                if obj.animation_data.action != None and "Detonator" in obj.animation_data.action.name:
                    print("There is already a Detonator action, creating one more...")
                obj.animation_data.action = bpy.data.actions.new(name="Detonator")
                curveStr = obj.animation_data.action.fcurves.new(data_path="field.strength", index=0)  
                curveMin = obj.animation_data.action.fcurves.new(data_path="field.distance_min", index=0)  
                curveMax = obj.animation_data.action.fcurves.new(data_path="field.distance_max", index=0)  
                
                ### Add points to empty animation curves for strength
                pIndex = 0
                for frame in range(startFr-1, endFr+1):
                    if frame >= startFr and frame < endFr:
                        ### TNT peak pressure formula (result in bar, standard formula by Kinney)
                        x = ((frame -startFr) /scene.render.fps) *blastWaveVel *timeScale
                        eq = TNTequivalent *explosiveMass
                        str = ((808*(1+((x /eq**(1/3))/4.5)**2)) / (((1+((x /eq**(1/3))/0.048)**2) *(1+((x /eq**(1/3))/0.32)**2) *(1+((x /eq**(1/3))/1.35)**2))**0.5))
                        # str value in bar
                        str /= 10               # Conversion bar to N/mm^2 (or MPa)
                        str *= 1000000          # Conversion N/mm^2 to N/m^2
                        str *= 2.358            # Conversion N into force field strength (forceFieldStr = f *elemMass *9.81 *correction; correction = 2.358)
                        str /= timeScale
                        # str value in force field strength
                        str *= sign             # Consider if push or pull force field
                        str *= openSpaceCorrect
                        if groundReflect: str /= 2
                    else:
                        str = 0
                        
                    if typeIdx == 1:  # Avoid setting strength > 0 after duration of push field has ended
                        if frame >= endFr -frameOffset:
                            str = 0
                    
                    ### Add keyframe
                    curveStr.keyframe_points.add(1)
                    curvePoint = curveStr.keyframe_points[pIndex]; curvePoint.co = frame +frameOffset, str
                    curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co
                    #curvePoint.handle_left_type = curveType; curvePoint.handle_right_type = curveType
                    pIndex += 1

                    if typeIdx == 1:  # Only write this last keyframe after duration of push field has ended
                        if frame > endFr -frameOffset:
                            break

                ### Add points to empty animation curves of minimum and maximum ranges
                pIndex = 0
                for keyframe in range(3):
                    if keyframe == 0:
                        frame = startFr
                        pos = 0
                    elif keyframe == 1:
                        frame = endFr
                        pos = ((endFr -startFr) /scene.render.fps) *blastWaveVel *timeScale
                    elif keyframe == 2:
                        frame = endFr +(endFr -startFr)
                        pos += ((endFr -startFr) /scene.render.fps) *blastWaveVel
                    
                    ### Add keyframe
                    curveMin.keyframe_points.add(1)
                    curveMax.keyframe_points.add(1)
                    curvePoint = curveMin.keyframe_points[pIndex]; curvePoint.co = frame +frameOffset, pos
                    curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co
                    curvePoint.handle_left_type = 'VECTOR'; curvePoint.handle_right_type = 'VECTOR'
                    curvePoint = curveMax.keyframe_points[pIndex]; curvePoint.co = frame +frameOffset, pos
                    curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co
                    curvePoint.handle_left_type = 'VECTOR'; curvePoint.handle_right_type = 'VECTOR'
                    pIndex += 1

                # Switch curves to linear extrapolation
                curveMin.extrapolation = 'LINEAR'
                curveMax.extrapolation = 'LINEAR'

    return connectsBtMul
