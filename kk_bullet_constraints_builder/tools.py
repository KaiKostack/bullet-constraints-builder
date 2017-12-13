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

import bpy, bmesh, os
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from builder_prep import *     # Contains preparation steps functions called by the builder

import kk_import_motion_from_text_file    # Contains earthquake motion import function
import kk_mesh_fracture                   # Contains boolean based discretization function
import kk_mesh_separate_loose             # Contains speed-optimized mesh island separation function
import kk_mesh_voxel_cell_grid_from_mesh  # Contains voxel based discretization function
import kk_select_intersecting_objects     # Contains intersection detection and resolving function

################################################################################

def tool_estimateClusterRadius(scene):
    
    objs, emptyObjs = gatherObjects(scene)
    
    if len(objs) > 0:        
        print("Estimating optimal cluster radius...")
        
        #objsDiameter = []
        diameterSum = 0
        for obj in objs:
            
            ### Calculate diameter for each object
            dim = list(obj.dimensions)
            dim.sort()
            diameter = dim[2]   # Use the largest dimension axis as diameter
            
            #objsDiameter.append(diameter)
            diameterSum += diameter
        
#        ### Sort all diameters, take the midst item and multiply it by 1 /sqrt(2)
#        objsDiameter.sort()
#        diameterEstimation = (objsDiameter[int(len(objsDiameter) /2)] /2) *0.707

        ### Alternative: Calculate average of all object diameters and multiply it by 1 /sqrt(2)
        diameterEstimation = ((diameterSum /2) /len(objs)) *0.707
        
        return diameterEstimation

    else:
        print("Selected objects required for cluster radius estimation.") 
        return 0

################################################################################

def tool_selectGroup(scene):
    
    ### Selects objects belonging to this element group in viewport.
    props = bpy.context.window_manager.bcb
    elemGrps = mem["elemGrps"]

    # Check if element group name corresponds to scene group
    grpName = elemGrps[props.menu_selectedElemGrp][EGSidxName]
    try: grp = bpy.data.groups[grpName]
    except: return
    
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')

    # Select all objects from that group       
    qFirst = 1
    for obj in grp.objects:
        if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene):
            obj.select = 1
            if qFirst:
                bpy.context.scene.objects.active = obj
                qFirst = 0

################################################################################

def tool_runPythonScript(scene, filename=""):

    print("\nExecuting user-defined Python script...")

    if len(filename) == 0: print("No script defined."); return

    try: s = bpy.data.texts[filename].as_string()
    except: print("Script not found."); return

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    result = exec(s)
    print("Finished and returned:", result)
    
################################################################################

def createElementGroup(grpName, presetNo=0):
    
    ### Create new element group
    props = bpy.context.window_manager.bcb
    elemGrps = mem["elemGrps"]
    # Check if group name is already in element group list
    qExists = 0
    for i in range(len(elemGrps)):
        if grpName == elemGrps[i][EGSidxName]:
            qExists = 1; break
    if not qExists:
        if len(elemGrps) < maxMenuElementGroupItems:
            # Add element group (syncing element group indices happens on execution)
            elemGrps.append(presets[presetNo].copy())
            # Update menu selection
            props.menu_selectedElemGrp = len(elemGrps) -1
        else:
            bpy.context.window_manager.bcb.message = "Maximum allowed element group count reached."
            bpy.ops.bcb.report('INVOKE_DEFAULT')  # Create popup message box
        ### Assign group name
        i = props.menu_selectedElemGrp
        elemGrps[i][EGSidxName] = grpName

########################################

def tool_createGroupsFromNames(scene):

    print("\nCreating groups from object names...")

    props = bpy.context.window_manager.bcb
    if len(props.preprocTools_grp_sep) == 0: return

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No mesh objects selected. Nothing done.")
        return
    
    ### Create one main group for all objects
    grpName = "BCB_Building"
    if grpName not in bpy.data.groups:
          grp = bpy.data.groups.new(grpName)
    else: grp = bpy.data.groups[grpName]
    for obj in objs:
        if obj.name not in grp.objects:
            grp.objects.link(obj)

    ### Create group data with objects
    grps = []
    grpsObjs = []
    for obj in objs:
        if props.preprocTools_grp_sep in obj.name:
            # grpName can also be ""
            if props.preprocTools_grp_occ:
                  grpName = obj.name.split(props.preprocTools_grp_sep)[0]
            else: grpName = obj.name.rsplit(props.preprocTools_grp_sep, 1)[0]
        # If name could not match the convention then add object to a default group
        else: grpName = ""
        # Actual linking into group happens here
        if grpName != "":
            if grpName not in grps:
                grps.append(grpName)
                grpsObjs.append([])
                grpIdx = len(grpsObjs)-1
            else: grpIdx = grps.index(grpName)
            grpsObjs[grpIdx].append(obj)
        
    ### Create actual object groups from data
    for k in range(len(grps)):
        grpName = grps[k]
        objs = grpsObjs[k]
        if grpName not in bpy.data.groups:
              grp = bpy.data.groups.new(grpName)
        else: grp = bpy.data.groups[grpName]
        for obj in objs:
            if obj.name not in grp.objects:
                grp.objects.link(obj)
         
    ### Create also element groups from data
    for k in range(len(grps)):
        grpName = grps[k]
        createElementGroup(grpName, presetNo=0)
    # Update menu related properties from global vars
    props.props_update_menu()
    
    print("Groups found:", len(grps))
    
################################################################################

def tool_applyAllModifiers(scene):

    print("\nApplying modifiers...")
    
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene)]
    if len(objs) == 0:
        print("No mesh objects selected. Nothing done.")
        return

    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    
    ### At first make all objects unique mesh objects (clear instancing) which have modifiers applied
    objsM = []
    for obj in objs:
        if len(obj.modifiers) > 0:
            obj.select = 1
            objsM.append(obj)
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)

    # Apply modifiers
    if len(objsM):
        bpy.context.scene.objects.active = objsM[0]
        bpy.ops.object.convert(target='MESH')

    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

################################################################################

def tool_centerModel(scene):
    
    print("\nCentering model...")
    
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    # Remove instances
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)

    ### Calculate boundary boxes for all objects
    qFirst = 1
    for obj in objs:
        # Calculate boundary box corners
        bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
        if qFirst:
            bbMin_all = bbMin.copy(); bbMax_all = bbMax.copy()
            qFirst = 0
        else:
            if bbMax_all[0] < bbMax[0]: bbMax_all[0] = bbMax[0]
            if bbMin_all[0] > bbMin[0]: bbMin_all[0] = bbMin[0]
            if bbMax_all[1] < bbMax[1]: bbMax_all[1] = bbMax[1]
            if bbMin_all[1] > bbMin[1]: bbMin_all[1] = bbMin[1]
            if bbMax_all[2] < bbMax[2]: bbMax_all[2] = bbMax[2]
            if bbMin_all[2] > bbMin[2]: bbMin_all[2] = bbMin[2]
    center = (bbMin_all +bbMax_all) /2
    # Set cursor to X and Y location of the center, and Z of the bottom boundary of the structure
    bpy.context.scene.cursor_location = Vector((center[0], center[1], bbMin_all[2]))
    # Set mesh origins to cursor location
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    # Reset locations to center of world space
    bpy.ops.object.location_clear(clear_delta=False)
    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

################################################################################

def tool_separateLoose(scene):
    
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Remove rigid body settings because of the unlinking optimization in the external module they will be lost anyway (while the RBW group remains)
    bpy.ops.rigidbody.objects_remove()

    ###### External function
    kk_mesh_separate_loose.run()

    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

################################################################################

def updateObjList(scene, objs):
    
    ### Add new objects and selected objects to the object list and remove deleted ones
    for objTemp in scene.objects:
        if objTemp.select:
            if objTemp not in objs:
                if objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(scene):
                    objs.append(objTemp)
    for idx in reversed(range(len(objs))):
        if objs[idx].name not in scene.objects:
            del objs[idx]
                
########################################

def tool_discretize(scene):

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    props = bpy.context.window_manager.bcb

    ###### Junction splitting and preparation for boolean halving
    
    if not props.preprocTools_dis_cel or props.preprocTools_dis_jus:
        # Create cutting plane to be used by external module
        bpy.ops.mesh.primitive_plane_add(radius=100, view_align=False, enter_editmode=False, location=Vector((0, 0, 0)))
        objC = bpy.context.scene.objects.active
        objC.name = "BCB_CuttingPlane"
        objC.select = 0

        # Select mesh objects
        for obj in objs: obj.select = 1
        bpy.context.scene.objects.active = selectionActive
        
        # Remove rigid body settings because the second scene optimization in the external module can produce ghost objects in RBW otherwise
        bpy.ops.rigidbody.objects_remove()
        # Remove instances
        bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)

        ###### External function
        # Set object centers to geometry origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        # Parameters: [qSplitAtJunctions, minimumSizeLimit, qTriangulate, halvingCutter]
        if props.preprocTools_dis_jus:
            print("\nDiscretization - Junction pass:")
            kk_mesh_fracture.run('BCB', ['JUNCTION', 0, 1, 'BCB_CuttingPlane'], None)
            
    ###### Voxel cell based discretization

    if props.preprocTools_dis_cel:
        print("\nDiscretization:")

        ###### External function
        size = props.preprocTools_dis_siz
        kk_mesh_voxel_cell_grid_from_mesh.run('BCB', [Vector((size, size, size))])

        # We have to repeat separate loose here
        tool_separateLoose(scene)

    ###### Boolean based discretization

    elif not props.preprocTools_dis_cel:

        print("\nDiscretization - Halving pass:")
        ###### External function
        kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 1, 'BCB_CuttingPlane'], None)
        ### Add new objects to the object list and remove deleted ones
        updateObjList(scene, selection)
        updateObjList(scene, objs)
        
        ### From now on do multiple passes until either now non-discretized objects are found or the passes limit is reached
        passes = 5  # Maximum number of passes
        passNum = 0
        while 1:
            ### Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations),
            ### deselect all others and try discretization again
            cnt = 0
            failed = []
            for obj in objs:
                ### Calculate diameter for each object
                dim = list(obj.dimensions)
                dim.sort()
                diameter = dim[2]   # Use the largest dimension axis as diameter
                if diameter <= props.preprocTools_dis_siz:
                    cnt += 1
                else: failed.append(obj)
            count = len(objs) -cnt
            
            # Stop condition
            passNum += 1
            if count == 0 or passNum > passes: break
            
            if count > 0:
                print("\nDiscretization - Pass %d (%d elements left):" %(passNum, count))
                # Deselect all objects.
                bpy.ops.object.select_all(action='DESELECT')
                failedExt = []
                for obj in failed:
                    obj.select = 1
                    bpy.context.scene.objects.active = obj
                    bpy.context.tool_settings.mesh_select_mode = False, True, False
                    # Enter edit mode              
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass 
                    me = obj.data
                    bm = bmesh.from_edit_mesh(me)

                    # Select all elements
                    try: bpy.ops.mesh.select_all(action='SELECT')
                    except: pass
                    # Remove doubles
                    bpy.ops.mesh.remove_doubles(threshold=0.0001)
                    # Smooth vertices slightly so overlapping geometry will shift a bit increasing possibility for successful next splitting attempt
                    bpy.ops.mesh.vertices_smooth(factor=0.0001)

                    ### Check if mesh has non-manifolds
                    # Deselect all elements
                    try: bpy.ops.mesh.select_all(action='DESELECT')
                    except: pass 
                    # Select non-manifold elements
                    bpy.ops.mesh.select_non_manifold()
                    # Check mesh if there are selected elements found
                    qNonManifolds = 0
                    for edge in bm.edges:
                        if edge.select: qNonManifolds = 1; break
                    bm.verts.ensure_lookup_table()
                    
                    ### Rip all vertices belonging to non-manifold edges
                    if qNonManifolds:
                        bpy.context.tool_settings.mesh_select_mode = True, False, False
                        vertCos = []
                        start = -1
                        for i in range(len(bm.verts)):
                            vert = bm.verts[i]
                            if vert.select:
                                vertCos.append(vert.co)
                                if start < 0: start = i
                        found = 1
                        while found > 0:
                            found = 0
                            i = start
                            while i < len(bm.verts):
                                vert = bm.verts[i]
                                if vert.co in vertCos:
                                    # Deselect all elements
                                    bpy.ops.mesh.select_all(action='DESELECT')
                                    vert.select = 1
                                    # Rip selection
                                    try: bpy.ops.mesh.rip('INVOKE_DEFAULT')                        
                                    except: pass
                                    else: i -= 1; found += 1
                                    bm.verts.ensure_lookup_table()
                                i += 1
                    # Separate loose
                    try: bpy.ops.mesh.separate(type='LOOSE')
                    except: pass
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass
                # Set object centers to geometry origin
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                ###### External function
                kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 1, 'BCB_CuttingPlane'], None)
                ### Add new objects to the object list and remove deleted ones
                updateObjList(scene, selection)
                updateObjList(scene, objs)

        ### If there are still objects larger than minimumSizeLimit left (due to failed boolean operations)
        ### print warning message together with a list of the problematic objects
        if count > 0:
            print("\nWarning: Following %d objects couldn't be discretized sufficiently:" %count)
            for obj in failed:
                print(obj.name)
        else: print("\nDiscretization verified and successful!")
        print("Final element count:", len(objs))

    ###### Clean-up for junction splitting and boolean halving
    
    # Update selection list if voxel cells together with junction search is used
    if props.preprocTools_dis_cel and props.preprocTools_dis_jus:
        ### Add new objects to the object list and remove deleted ones
        updateObjList(scene, selection)

    if not props.preprocTools_dis_cel or props.preprocTools_dis_jus:

        # Delete cutting plane object
        bpy.context.scene.objects.unlink(objC)

        # Revert to start selection
        for obj in selection: obj.select = 1
        bpy.context.scene.objects.active = selectionActive

    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

################################################################################

def tool_removeIntersections(scene, mode=1):
    
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    ###### External function
    props = bpy.context.window_manager.bcb
    # [encaseTol, qSelectByVertCnt, qSelectSmallerVol, qSelectA, qSelectB, qDelete, qBool]
    if mode == 1:  # Resolve intersections
        if props.preprocTools_int_bol:
              count = kk_select_intersecting_objects.run('BCB', [0,    0, 0, 1, 1, 0, 1])
        else: count = kk_select_intersecting_objects.run('BCB', [0.02, 1, 1, 0, 0, 1, 0])
    elif mode == 2 or mode == 4:  # Selection of all intersections
              count = kk_select_intersecting_objects.run('BCB', [0,    0, 0, 1, 1, 0, 0])
    elif mode == 3:  # Selection for intersections which require booleans
              count = kk_select_intersecting_objects.run('BCB', [0.02, 1, 1, 0, 0, 0, 0])
    
    if mode == 1 and count > 0:
        # For now disabled because overall simulations behave more stable without it:
        ### Switch found intersecting objects to 'Mesh' collision shape
        ### (some might have only overlapping boundary boxes while the geometry could still not intersecting)
#        objs = [obj for obj in bpy.context.scene.objects if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
#        if len(objs) > 0:
#            obj = objs[0]
#            if obj.rigid_body != None:
#                bpy.ops.rigidbody.shape_change(type='MESH')
#                for obj in objs:
#                    obj.rigid_body.collision_margin = 0
        # Set object centers to geometry origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                
    if mode == 1 or (mode == 4 and count == 0):
        # Revert to start selection
        for obj in selection: obj.select = 1
        bpy.context.scene.objects.active = selectionActive

    return count
    
################################################################################

def tool_enableRigidBodies(scene):

    print("\nEnabling rigid body settings...")

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    # Find non-mesh objects in selection
    objsNoMesh = [obj for obj in selection if obj.type != 'MESH']
    # Select only meshes
    for obj in objsNoMesh: obj.select = 0
    # Make sure there is an active object
    bpy.context.scene.objects.active = objs[0]
    # Apply rigid body settings
    bpy.ops.rigidbody.objects_add()
    # Set friction for all to 1.0
    for obj in objs:
        obj.rigid_body.friction = 1
    
    # Set rigid bodies which are members of some specific groups to passive
    # (Todo: Each Preprocessing Tool removing RB information like Separate Loose should backup those for all objects and refresh it after operation, then this can be removed)   
    for obj in objs:
        for grpName in ["Fixed", "Passive", "Base"]:
            if grpName in bpy.data.groups:
                if obj.name in bpy.data.groups[grpName].objects:
                    obj.rigid_body.type = 'PASSIVE'
    
    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive
    
################################################################################

def createBoxData(verts, edges, faces, corner1, corner2):
    
    ### Create box geometry from boundaries
    x1 = corner1[0]; x2 = corner2[0]
    y1 = corner1[1]; y2 = corner2[1]
    z1 = corner1[2]; z2 = corner2[2]
    i = len(verts)
    # Create the vertices for the box corners
    verts.append(Vector([x1, y1, z1]))
    verts.append(Vector([x2, y1, z1]))
    verts.append(Vector([x2, y2, z1]))
    verts.append(Vector([x1, y2, z1]))
    verts.append(Vector([x1, y1, z2]))
    verts.append(Vector([x2, y1, z2]))
    verts.append(Vector([x2, y2, z2]))
    verts.append(Vector([x1, y2, z2]))
#    # Generate 12 edges from the 8 vertices
#    edges.append([i, i+1])
#    edges.append([i+1, i+2])
#    edges.append([i+2, i+3])
#    edges.append([i+3, i])
#    edges.append([i+4, i+5])
#    edges.append([i+5, i+6])
#    edges.append([i+6, i+7])
#    edges.append([i+7, i+4])
#    edges.append([i, i+4])
#    edges.append([i+1, i+5])
#    edges.append([i+2, i+6])
#    edges.append([i+3, i+7])
    # Generate the corresponding face
    faces.append([i+3, i+2, i+1, i])
    faces.append([i+4, i+5, i+6, i+7])
    faces.append([i, i+1, i+5, i+4])
    faces.append([i+1, i+2, i+6, i+5])
    faces.append([i+2, i+3, i+7, i+6])
    faces.append([i+3, i, i+4, i+7])

########################################

def tool_fixFoundation(scene):

    print("\nSearching foundation elements...")

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body != None and obj.rigid_body.type == 'ACTIVE' and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No active rigid body objects selected.")
        return

    props = bpy.context.window_manager.bcb
    
    ### Foundation detection based on name
    if not props.preprocTools_fix_cac:
        if len(props.preprocTools_fix_nam) > 0:
            cnt = 0
            for obj in objs:
                if props.preprocTools_fix_nam in obj.name:
                    cnt += 1
                    obj.rigid_body.type = 'PASSIVE'
            if cnt == 0: print("No object with '%s' in its name found." %props.preprocTools_fix_nam)
        else: print("No foundation object name defined in user interface.")

    ### Foundation generation 
    else:
        if len(props.preprocTools_fix_nam) > 0:
              foundationName = props.preprocTools_fix_nam
        else: foundationName = "Foundation"

        ### Calculate boundary boxes for all objects
        verts = []; edges = []; faces = []  # Active buffer mesh object
        verts2 = []; edges2 = []; faces2 = []  # Passive mesh object
        objsBB = []
        qFirst = 1
        for obj in objs:
            # Calculate boundary box corners
            bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
            objsBB.append([bbMin, bbMax])
            if qFirst:
                bbMin_all = bbMin.copy(); bbMax_all = bbMax.copy()
                qFirst = 0
            else:
                if bbMax_all[0] < bbMax[0]: bbMax_all[0] = bbMax[0]
                if bbMin_all[0] > bbMin[0]: bbMin_all[0] = bbMin[0]
                if bbMax_all[1] < bbMax[1]: bbMax_all[1] = bbMax[1]
                if bbMin_all[1] > bbMin[1]: bbMin_all[1] = bbMin[1]
                if bbMax_all[2] < bbMax[2]: bbMax_all[2] = bbMax[2]
                if bbMin_all[2] > bbMin[2]: bbMin_all[2] = bbMin[2]

        ### Calculate geometry for adjacent foundation geometry for all sides
        for bb in objsBB:
            bbMin = bb[0]
            bbMax = bb[1]

            # X+
            if props.preprocTools_fix_axp:
                if bbMax[0] >= bbMax_all[0] -props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMax[0]+props.preprocTools_fix_rng, bbMin[1], bbMin[2] ))
                    createBoxData(verts, edges, faces, bbMax, newCorner)
                    newCorner2 = Vector(( 2*bbMax[0]-bbMin[0]+props.preprocTools_fix_rng, bbMax[1], bbMax[2] ))
                    createBoxData(verts2, edges2, faces2, newCorner, newCorner2)
            # X-
            if props.preprocTools_fix_axn:
                if bbMin[0] <= bbMin_all[0] +props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMin[0]-props.preprocTools_fix_rng, bbMax[1], bbMax[2] ))
                    createBoxData(verts, edges, faces, newCorner, bbMin)
                    newCorner2 = Vector(( 2*bbMin[0]-bbMax[0]-props.preprocTools_fix_rng, bbMin[1], bbMin[2] ))
                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
            # Y+
            if props.preprocTools_fix_ayp:
                if bbMax[1] >= bbMax_all[1] -props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMin[0], bbMax[1]+props.preprocTools_fix_rng, bbMin[2] ))
                    createBoxData(verts, edges, faces, bbMax, newCorner)
                    newCorner2 = Vector(( bbMax[0], 2*bbMax[1]-bbMin[1]+props.preprocTools_fix_rng, bbMax[2] ))
                    createBoxData(verts2, edges2, faces2, newCorner, newCorner2)
            # Y-
            if props.preprocTools_fix_ayn:
                if bbMin[1] <= bbMin_all[1] +props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMax[0], bbMin[1]-props.preprocTools_fix_rng, bbMax[2] ))
                    createBoxData(verts, edges, faces, newCorner, bbMin)
                    newCorner2 = Vector(( bbMin[0], 2*bbMin[1]-bbMax[1]-props.preprocTools_fix_rng, bbMin[2] ))
                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
            # Z+
            if props.preprocTools_fix_azp:
                if bbMax[2] >= bbMax_all[2] -props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMin[0], bbMin[1], bbMax[2]+props.preprocTools_fix_rng ))
                    createBoxData(verts, edges, faces, bbMax, newCorner)
                    newCorner2 = Vector(( bbMax[0], bbMax[1], 2*bbMax[2]-bbMin[2]+props.preprocTools_fix_rng ))
                    createBoxData(verts2, edges2, faces2, newCorner, newCorner2)
            # Z-
            if props.preprocTools_fix_azn:
                if bbMin[2] <= bbMin_all[2] +props.preprocTools_fix_rng:
                    newCorner = Vector(( bbMax[0], bbMax[1], bbMin[2]-props.preprocTools_fix_rng ))
                    createBoxData(verts, edges, faces, newCorner, bbMin)
                    newCorner2 = Vector(( bbMin[0], bbMin[1], 2*bbMin[2]-bbMax[2]-props.preprocTools_fix_rng ))
                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)

#            ### Old method with equal sizes for foundation objects 
#            # X+
#            if props.preprocTools_fix_axp:
#                if bbMax[0] >= bbMax_all[0] -props.preprocTools_fix_rng:
#                    newCorner = Vector(( 2*bbMax[0]-bbMin[0], bbMin[1], bbMin[2] ))
#                    createBoxData(verts, edges, faces, bbMax, newCorner)
#                    newCorner2 = Vector(( 3*bbMax[0]-2*bbMin[0], bbMax[1], bbMax[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
#            # X-
#            if props.preprocTools_fix_axn:
#                if bbMin[0] <= bbMin_all[0] +props.preprocTools_fix_rng:
#                    newCorner = Vector(( 2*bbMin[0]-bbMax[0], bbMax[1], bbMax[2] ))
#                    createBoxData(verts, edges, faces, newCorner, bbMin)
#                    newCorner2 = Vector(( 3*bbMin[0]-2*bbMax[0], bbMin[1], bbMin[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
#            # Y+
#            if props.preprocTools_fix_ayp:
#                if bbMax[1] >= bbMax_all[1] -props.preprocTools_fix_rng:
#                    newCorner = Vector(( bbMin[0], 2*bbMax[1]-bbMin[1], bbMin[2] ))
#                    createBoxData(verts, edges, faces, bbMax, newCorner)
#                    newCorner2 = Vector(( bbMax[0], 3*bbMax[1]-2*bbMin[1], bbMax[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
#            # Y-
#            if props.preprocTools_fix_ayn:
#                if bbMin[1] <= bbMin_all[1] +props.preprocTools_fix_rng:
#                    newCorner = Vector(( bbMax[0], 2*bbMin[1]-bbMax[1], bbMax[2] ))
#                    createBoxData(verts, edges, faces, newCorner, bbMin)
#                    newCorner2 = Vector(( bbMin[0], 3*bbMin[1]-2*bbMax[1], bbMin[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
#            # Z+
#            if props.preprocTools_fix_azp:
#                if bbMax[2] >= bbMax_all[2] -props.preprocTools_fix_rng:
#                    newCorner = Vector(( bbMin[0], bbMin[1], 2*bbMax[2]-bbMin[2] ))
#                    createBoxData(verts, edges, faces, bbMax, newCorner)
#                    newCorner2 = Vector(( bbMax[0], bbMax[1], 3*bbMax[2]-2*bbMin[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)
#            # Z-
#            if props.preprocTools_fix_azn:
#                if bbMin[2] <= bbMin_all[2] +props.preprocTools_fix_rng:
#                    newCorner = Vector(( bbMax[0], bbMax[1], 2*bbMin[2]-bbMax[2] ))
#                    createBoxData(verts, edges, faces, newCorner, bbMin)
#                    newCorner2 = Vector(( bbMin[0], bbMin[1], 3*bbMin[2]-2*bbMax[2] ))
#                    createBoxData(verts2, edges2, faces2, newCorner2, newCorner)

        ### Create actual geometry for passive and active buffer object
        # Create empty mesh object
        me = bpy.data.meshes.new(foundationName)
        me2 = bpy.data.meshes.new(foundationName)
        # Add mesh data to new object
        me.from_pydata(verts, [], faces)
        me2.from_pydata(verts2, [], faces2)
        obj = bpy.data.objects.new(foundationName, me)
        obj2 = bpy.data.objects.new(foundationName, me2)
        scene.objects.link(obj)
        scene.objects.link(obj2)
        
        ### Add to main group
        grpName = "BCB_Building"
        if grpName in bpy.data.groups:
            grp = bpy.data.groups[grpName]
            grp.objects.link(obj)
            grp.objects.link(obj2)

        ### Create a new group for the foundation object if not already existing
        grpName = foundationName
        if grpName not in bpy.data.groups:
              grp = bpy.data.groups.new(grpName)
        else: grp = bpy.data.groups[grpName]
        # Add new object to group
        grp.objects.link(obj)
        grp.objects.link(obj2)

        ### Create also element group from data and use passive preset for it
        createElementGroup(grpName, presetNo=1)
        # Update menu related properties from global vars
        props.props_update_menu()

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')
        
        # Apply rigid body settings to foundation
        obj.select = 1
        obj2.select = 1
        bpy.context.scene.objects.active = obj
        bpy.ops.rigidbody.objects_add()
        # Set fixed object to passive (but not buffer)
        obj2.rigid_body.type = 'PASSIVE'
        # Set friction to 1.0
        obj.rigid_body.friction = 1
        obj2.rigid_body.friction = 1
        
        ### Split both objects into individual parts
        bpy.context.tool_settings.mesh_select_mode = False, True, False
        for ob in [obj, obj2]:
            bpy.context.scene.objects.active = ob
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass
            # Recalculate normals
            bpy.ops.mesh.normals_make_consistent(inside=False)
            # Separate loose
            try: bpy.ops.mesh.separate(type='LOOSE')
            except: pass
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass

        # Set object centers to geometry origin
        obj.select = 1
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
         
    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

################################################################################

def createOrReuseObjectAndMesh(scene, objName="Mesh"):

    ### Create a fresh object and delete old one, the complexity is needed to avoid pollution with old mesh datablocks
    ### Further, we cannot use the same mesh datablock that has already been used with from_pydata() so there is a workaround for this, too
    objEmptyName = "$Temp$"
    try:    obj = bpy.data.objects[objName]
    except:
            try:    me = bpy.data.meshes[objName]
            except: 
                    me = bpy.data.meshes.new(objName)
                    obj = bpy.data.objects.new(objName, me)
            else:
                    obj = bpy.data.objects.new(objName, me)
                    try:    meT = bpy.data.meshes[objEmptyName]
                    except: meT = bpy.data.meshes.new(objEmptyName)
                    obj.data = meT
                    bpy.data.meshes.remove(me, do_unlink=1)
                    me = bpy.data.meshes.new(objName)
                    obj.data = me
            scene.objects.link(obj)
    else:
            #obj = bpy.data.objects[objName]
            me = obj.data
            try:    meT = bpy.data.meshes[objEmptyName]
            except: meT = bpy.data.meshes.new(objEmptyName)
            obj.data = meT
            bpy.data.meshes.remove(me, do_unlink=1)
            me = bpy.data.meshes.new(objName)
            obj.data = me
            try: scene.objects.link(obj)
            except: pass
            
    return obj

########################################

def tool_groundMotion(scene):

    print("\nApplying ground motion...")

    props = bpy.context.window_manager.bcb
    q = 0
    if len(props.preprocTools_gnd_obj) == 0:
        print("No ground object name defined in user interface.")
        return
    if props.preprocTools_gnd_obj in scene.objects:
        objGnd = scene.objects[props.preprocTools_gnd_obj]
        qCreateGroundObj = 0
    else: qCreateGroundObj = 1
    if props.preprocTools_gnd_obm in scene.objects:
        objMot = scene.objects[props.preprocTools_gnd_obm]
    else: objMot = None
        
    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active

    if qCreateGroundObj:
        print("Ground object not found, creating new one...")
        # Find active mesh objects in selection
        objsA = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body != None and obj.rigid_body.type == 'ACTIVE' and len(obj.data.vertices) > 0]
        if len(objsA) > 0:
            ### Calculate boundary boxes for all active objects with connection type > 0
            qFirst = 1
            for obj in objsA:
                # Calculate boundary box corners
                bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
                if qFirst:
                    bbMin_all = bbMin.copy()
                    qFirst = 0
                else:
                    if bbMin_all[2] > bbMin[2]: bbMin_all[2] = bbMin[2]
            height = bbMin_all[2]
        else: height = 0
        ### Create ground object data
        verts = []; edges = []; faces = []
        corner1 = Vector((-500,-500,-10))
        corner2 = Vector((500, 500, 0))
        createBoxData(verts, edges, faces, corner1, corner2)
        # Create empty mesh object
        #me = bpy.data.meshes.new(props.preprocTools_gnd_obj)
        #objGnd = bpy.data.objects.new(props.preprocTools_gnd_obj, me)
        #scene.objects.link(objGnd)
        objGnd = createOrReuseObjectAndMesh(scene, objName=props.preprocTools_gnd_obj)
        me = objGnd.data
        # Add mesh data to new object
        me.from_pydata(verts, [], faces)
        # Set ground to the height of the lowest active rigid body
        objGnd.location[2] = height

    ###### Parenting to ground object
    
    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')

    # Find passive mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body != None and obj.rigid_body.type == 'PASSIVE' and len(obj.data.vertices) > 0]
    if len(objs) == 0:
        print("No passive rigid body elements selected, nothing attached to the ground.")
    else:
        # Select passive mesh objects
        for obj in objs: obj.select = 1

        ### Make object parent for selected objects
        bpy.context.scene.objects.active = objGnd  # Parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        
        if objGnd.is_visible(bpy.context.scene):

            # Apply rigid body settings to ground object
            if objGnd.rigid_body == None:
                # Deselect all objects.
                bpy.ops.object.select_all(action='DESELECT')
                # Apply rigid body settings
                objGnd.select = 1
                bpy.context.scene.objects.active = objGnd
                bpy.ops.rigidbody.objects_add()
                objGnd.select = 0
                # Set friction for all to 1.0
                objGnd.rigid_body.friction = 1

            objGnd.rigid_body.type = 'PASSIVE'
        
            # Enable animated flag for all passive rigid bodies so that Bullet takes their motion into account
            objGnd.rigid_body.kinematic = True
        
        for obj in objs: obj.rigid_body.kinematic = True
        
    ###### Parenting ground object to motion object

    if objMot != None:
        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')
        
        ### Make object parent for selected objects
        objGnd.select = 1  # Child
        bpy.context.scene.objects.active = objMot  # Parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        objGnd.select = 0
        
        # Use given motion object for creating artificial earthquake motion from now on
        objGnd = objMot

    ###### Creating artificial earthquake motion curves for ground object

    if props.preprocTools_gnd_nac:
        
        ### Create animation curve with one keyframe as base
        obj = objGnd
        obj.animation_data_create()
        # If current action is already a "Motion" one then output a hint
        if obj.animation_data.action != None and "Motion" in obj.animation_data.action.name:
            print("There is already a Motion action, creating a new one...")
        obj.animation_data.action = bpy.data.actions.new(name="Motion")
        curveLocX = obj.animation_data.action.fcurves.new(data_path="delta_location", index=0)  
        curveLocY = obj.animation_data.action.fcurves.new(data_path="delta_location", index=1)  
        curveLocZ = obj.animation_data.action.fcurves.new(data_path="delta_location", index=2)  
        curveLocX.keyframe_points.add(1)
        curveLocY.keyframe_points.add(1)
        curveLocZ.keyframe_points.add(1)

        ### Creating noise function modifier
        fps_rate = scene.render.fps
        amplitude = props.preprocTools_gnd_nap
        frequency = props.preprocTools_gnd_nfq
        duration = props.preprocTools_gnd_ndu
        seed = props.preprocTools_gnd_nsd
        
        # X axis
        fmod = curveLocX.modifiers.new(type='NOISE')
        fmod.scale = fps_rate /frequency
        fmod.phase = seed
        fmod.strength = amplitude *6
        fmod.depth = 1
        fmod.use_restricted_range = True
        fmod.frame_start = 1
        fmod.frame_end = duration *fps_rate
        fmod.blend_in = (duration *fps_rate) /2
        fmod.blend_out = (duration *fps_rate) /2

        # Y axis
        fmod = curveLocY.modifiers.new(type='NOISE')
        fmod.scale = fps_rate /frequency
        fmod.phase = seed +1000
        fmod.strength = amplitude *6
        fmod.depth = 1
        fmod.use_restricted_range = True
        fmod.frame_start = 1
        fmod.frame_end = duration *fps_rate
        fmod.blend_in = (duration *fps_rate) /2
        fmod.blend_out = (duration *fps_rate) /2

        # Z axis
#        fmod = curveLocZ.modifiers.new(type='NOISE')
#        fmod.scale = fps_rate /frequency
#        fmod.phase = seed +2000
#        fmod.strength = amplitude *1.5
#        fmod.depth = 1
#        fmod.use_restricted_range = True
#        fmod.frame_start = 1
#        fmod.frame_end = duration *fps_rate
#        fmod.blend_in = (duration *fps_rate) /2
#        fmod.blend_out = (duration *fps_rate) /2

    ######  Import ground motion from text file

    elif len(props.preprocTools_gnd_nam) > 0:
    
        # Select ground object as expected by the script
        bpy.context.scene.objects.active = objGnd
        objGnd.select = 1
        # Set frame rate as expected by the script
        scene.render.fps = 25
    
        ###### External function
        kk_import_motion_from_text_file.importData(props.preprocTools_gnd_nam)

        objGnd.select = 0
        
    else: print("No text file defined.");

    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

################################################################################

def stopPlaybackAndReturnToStart(scene):

    bpy.app.handlers.frame_change_pre.pop()   # Remove event handler
    bpy.ops.screen.animation_play()           # Stop animation playback
    scene.frame_current = scene.frame_start  # Reset to start frame

########################################

def tool_exportLocationHistory_eventHandler(scene):
    
    ### Vars
    qRelativeCoordinates = 0   # Enables logging of relative coordinates instead of absolute

    props = bpy.context.window_manager.bcb
    filenamePath = props.postprocTools_lox_nam
    logPath = os.path.dirname(filenamePath)
    name = props.postprocTools_lox_elm

    ###### Get data

    ### Official Blender
    if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE') or not asciiExportName in scene.objects:
        try: ob = scene.objects[name]
        except:
            print('Error: Defined object not found. Removing event handler.')
            stopPlaybackAndReturnToStart(scene); return
        else:
            data = ob.matrix_world.to_translation()  # Get actual Bullet object's position as .location only returns its simulation starting position

    ### Fracture Modifier
    else:
        try: ob = scene.objects[asciiExportName]
        except:
            print('Error: Fracture Modifier object not found. Removing event handler.')
            stopPlaybackAndReturnToStart(scene); return
        else:
            md = ob.modifiers["Fracture"]
            try: ob = md.mesh_islands[name]
            except:
                print('Error: Defined object not found. Removing event handler.')
                stopPlaybackAndReturnToStart(scene); return
            else:
                data = ob.centroid.copy()  # Get actual Bullet object's position as .location only returns its simulation starting position
    
    # If filepath is empty then print data into console
    if len(filenamePath) == 0:
        print("Data:", data)

    else:

        ###### Export data
        
        ### On first run
        if "log_files_open" not in bpy.app.driver_namespace.keys():
            # Create object list of selected objects
            objNames = [name]
            if len(objNames) > 0:
                bpy.app.driver_namespace["log_objNames"] = objNames
            files = []
            for objName in objNames:
                # Stupid Windows interprets "Con." in path as system variable and writes into console
                filename = objName.replace(".", "_") +".csv"
                filename = os.path.join(logPath, filename)
                print("Creating file:", filename)
                # Remove old log file at start frame
                try: os.remove(filename)
                except: pass
                # Create new log file
                try: f = open(filename, "w")
                except:
                    print('Error: Could not open file.')
                    stopPlaybackAndReturnToStart(scene); return
                else:
                    line = "X; Y; Z; Name: %s\n" %objName
                    f.write(line)
                    files.append(f)
            bpy.app.driver_namespace["log_files_open"] = files
        
        ### For every frame
        if "log_objNames" in bpy.app.driver_namespace.keys():
            objNames = bpy.app.driver_namespace["log_objNames"]
            files = bpy.app.driver_namespace["log_files_open"]
            for k in range(len(objNames)):
                objName = objNames[k]
                if qRelativeCoordinates:
                    if "log_data_start_" +objName not in bpy.app.driver_namespace.keys():
                        bpy.app.driver_namespace["log_data_start_" +objName] = data
                        data = (0, 0, 0)
                    else:
                        data -= bpy.app.driver_namespace["log_data_start_" +objName]
                line = "%0.6f, %0.6f, %0.6f\n" %(data[0], data[1], data[2])
                files[k].write(line)

    ### Check if last frame is reached
    if scene.frame_current == scene.frame_end:
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()  # Stop animation playback

    ### If animation playback has stopped (can also be done by user) then unload the event handler and free all monitor data
    if not bpy.context.screen.is_animation_playing:
        print('Removing event handler.')
        bpy.app.handlers.frame_change_pre.pop()  # Remove event handler
        scene.frame_current == scene.frame_start  # Reset to start frame
        ### Close log files
        try: files = bpy.app.driver_namespace["log_files_open"]
        except: pass
        else:
            for f in files: f.close()
        ### Delete keys
        keys = [key for key in bpy.app.driver_namespace.keys()]
        for key in keys:
            if "log_" in key:
                del bpy.app.driver_namespace[key]

########################################

def tool_exportLocationHistory(scene):

    print("\nExporting location time history...")

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    print('Init event handler.')
    bpy.app.handlers.frame_change_pre.append(tool_exportLocationHistory_eventHandler)
    # Start animation playback
    bpy.ops.screen.animation_play()

################################################################################

def tool_constraintForceHistory_getData(scene, name):
    
    props = bpy.context.window_manager.bcb

    ###### Get data

    ### Official Blender
    if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE') or not asciiExportName in scene.objects:
        ### Try to find first constraint for the connection
        try: ob = scene.objects[name +'.1']
        except:
            print('Error: Defined object not found. Removing event handler.')
            stopPlaybackAndReturnToStart(scene); return None
        else:
            try: cons = [ob.rigid_body_constraint]
            except:
                print('Error: Defined object no constraint. Removing event handler.')
                stopPlaybackAndReturnToStart(scene); return None
            else:
                ### Try to find more constraints for the connection
                i = 1; qEnd = 0
                while not qEnd:
                    i += 1
                    nameNew = name +'.%d' %i
                    try: ob = scene.objects[nameNew]
                    except: qEnd = 1
                    else: cons.append(ob.rigid_body_constraint)

    ### Fracture Modifier
    else:
        ### Try to find first constraint for the connection
        try: ob = scene.objects[asciiExportName]
        except:
            print('Error: Fracture Modifier object not found. Removing event handler.')
            stopPlaybackAndReturnToStart(scene); return None
        else:
            md = ob.modifiers["Fracture"]
            try: cons = [md.mesh_constraints[name +'.1']]
            except:
                print('Error: Defined object not found. Removing event handler.')
                stopPlaybackAndReturnToStart(scene); return None
            else:
                ### Try to find more constraints for the connection
                i = 1; qEnd = 0
                while not qEnd:
                    i += 1
                    nameNew = name +'.%d' %i
                    try: cons.append(md.mesh_constraints[nameNew])
                    except: qEnd = 1

    try: data = [con.appliedImpulse() for con in cons]
    except:
        print("Error: Data could not be read, Blender version with Fracture Modifier required!")
        stopPlaybackAndReturnToStart(scene); return None
    
    return data, cons

########################################

def tool_constraintForceHistory_eventHandler(scene):

    props = bpy.context.window_manager.bcb
    name = props.postprocTools_fcx_con
    result = tool_constraintForceHistory_getData(scene, name)

    if result != None:
        data = result[0]  # (data, cons)

        filenamePath = props.postprocTools_fcx_nam
        logPath = os.path.dirname(filenamePath)

        # If filepath is empty then print data into console
        if len(filenamePath) == 0:
            print("Data:", data)

        else:

            ###### Export data
            
            ### On first run
            if "log_files_open" not in bpy.app.driver_namespace.keys():
                # Create object list of selected objects
                objNames = [name]
                if len(objNames) > 0:
                    bpy.app.driver_namespace["log_objNames"] = objNames
                files = []
                for objName in objNames:
                    # Stupid Windows interprets "Con." in path as system variable and writes into console
                    filename = objName.replace(".", "_") +".csv"
                    filename = os.path.join(logPath, filename)
                    print("Creating file:", filename)
                    # Remove old log file at start frame
                    try: os.remove(filename)
                    except: pass
                    # Create new log file
                    try: f = open(filename, "w")
                    except:
                        print('Error: Could not open file.')
                        stopPlaybackAndReturnToStart(scene); return
                    else:
                        line = "1: Fmax for connection; Rest: F for individual constraints; Name: %s\n" %objName
                        f.write(line)
                        files.append(f)
                bpy.app.driver_namespace["log_files_open"] = files
            
    ### For every frame
    if "log_objNames" in bpy.app.driver_namespace.keys():
        objNames = bpy.app.driver_namespace["log_objNames"]
        files = bpy.app.driver_namespace["log_files_open"]
        for k in range(len(objNames)):
            fmax = data[0]
            for val in data: fmax = max(fmax, abs(val))
            line = "%0.6f" %fmax
            for val in data:
                line += " %0.6f" %val
            line += "\n"
            files[k].write(line)

    ### Check if last frame is reached
    if scene.frame_current == scene.frame_end:
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()  # Stop animation playback

    ### If animation playback has stopped (can also be done by user) then unload the event handler and free all monitor data
    if not bpy.context.screen.is_animation_playing:
        print('Removing event handler.')
        bpy.app.handlers.frame_change_pre.pop()  # Remove event handler
        scene.frame_current == scene.frame_start  # Reset to start frame
        ### Close log files
        try: files = bpy.app.driver_namespace["log_files_open"]
        except: pass
        else:
            for f in files: f.close()
        ### Delete keys
        keys = [key for key in bpy.app.driver_namespace.keys()]
        for key in keys:
            if "log_" in key:
                del bpy.app.driver_namespace[key]

########################################

def tool_constraintForceHistory(scene):

    print("\nExporting constraint force time history...")

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    ### Free previous bake data
    contextFix = bpy.context.copy()
    contextFix['point_cache'] = scene.rigidbody_world.point_cache
    bpy.ops.ptcache.free_bake(contextFix)
    ### Invalidate point cache to enforce a full bake without using previous cache data
    if "RigidBodyWorld" in bpy.data.groups:
        try: obj = bpy.data.groups["RigidBodyWorld"].objects[0]
        except: pass
        else: obj.location = obj.location

    print('Init event handler.')
    bpy.app.handlers.frame_change_pre.append(tool_constraintForceHistory_eventHandler)
    # Start animation playback
    bpy.ops.screen.animation_play()
