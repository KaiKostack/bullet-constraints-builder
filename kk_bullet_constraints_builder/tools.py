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

import bpy, bmesh
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from builder_prep import *     # Contains preparation steps functions called by the builder

import kk_mesh_separate_loose
import kk_mesh_fracture

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
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene)]
    if len(objs) == 0:
        print("No mesh objects selected. Nothing done.")
        return
    
    ### Create group data with objects
    grps = []
    grpsObjs = []
    for obj in objs:
        if props.preprocTools_grp_sep in obj.name:
            grpName = obj.name.split(props.preprocTools_grp_sep)[0]
            if len(grpName) > 0:
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
    elemGrps = mem["elemGrps"]
    for k in range(len(grps)):
        grpName = grps[k]
        # Check if group name is already in element group list
        qExists = 0
        for i in range(len(elemGrps)):
            if grpName == elemGrps[i][EGSidxName]:
                qExists = 1; break
        if not qExists:
            ### Create new element group
            if len(elemGrps) < maxMenuElementGroupItems:
                # Add element group (syncing element group indices happens on execution)
                j = 0  # Use preset 0 as dummy data 
                elemGrps.append(presets[j].copy())
                # Update menu selection
                props.menu_selectedElemGrp = len(elemGrps) -1
            else:
                bpy.context.window_manager.bcb.message = "Maximum allowed element group count reached."
                bpy.ops.bcb.report('INVOKE_DEFAULT')  # Create popup message box
            ### Assign group name
            i = props.menu_selectedElemGrp
            elemGrps[i][EGSidxName] = grpName
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
    for obj in objs:
        if len(obj.modifiers) > 0:
            obj.select = 1
    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=True, obdata=True, material=False, texture=False, animation=False)
    
    # Apply modifiers
    count = 0
    for obj in objs:
        #MeshObject.to_mesh(scene=bpy.context.scene, apply_modifiers=True, settings='PREVIEW')
        bpy.context.scene.objects.active = obj
        if len(obj.modifiers) > 0: count += 1
        for mod in obj.modifiers:
            # Skip edgesplit modifiers to avoid to create more sperata meshes than necessary
            #if not "EdgeSplit" in mod.name:
                try: bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                except: bpy.ops.object.modifier_remove(modifier=mod.name)

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
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene)]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    ### Calculate boundary boxes for all objects
    qFirst = 1
    for obj in objs:
        # Calculate boundary box corners
        bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
        if qFirst:
            bbMin_all = bbMin; bbMax_all = bbMax
            qFirst = 0
        else:
            if bbMax_all[0] < bbMax[0]: bbMax_all[0] = bbMax[0]
            if bbMin_all[0] > bbMin[0]: bbMin_all[0] = bbMin[0]
            if bbMax_all[1] < bbMax[1]: bbMax_all[1] = bbMax[1]
            if bbMin_all[1] > bbMin[1]: bbMin_all[1] = bbMin[1]
            if bbMax_all[2] < bbMax[2]: bbMax_all[2] = bbMax[2]
            if bbMin_all[2] > bbMin[2]: bbMin_all[2] = bbMin[2]
    center = (bbMin_all +bbMax_all) /2
    # Set cursor at X and Y location but keep height unchanged
    bpy.context.scene.cursor_location = Vector((center[0], center[1], 0))
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
    
    ### Add new objects to the object list and remove deleted ones
    for objTemp in scene.objects:
        if objTemp.select and objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(scene):
            if objTemp not in objs:
                objs.append(objTemp)
    for objTemp in objs:
        if objTemp.name not in scene.objects:
            objs.remove(objTemp)

########################################

def tool_discretize(scene):

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene)]
    if len(objs) == 0:
        print("No mesh objects selected.")
        return

    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

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

    ###### External function
    props = bpy.context.window_manager.bcb
    # Parameters: [qSplitAtJunctions, minimumSizeLimit, qTriangulate, halvingCutter]
    if props.preprocTools_dis_jus:
        print("\nDiscretization - Junction pass:")
        kk_mesh_fracture.run('BCB', ['JUNCTION', 0, 0, 'BCB_CuttingPlane'], None)
        ### Add new objects to the object list and remove deleted ones
        updateObjList(scene, selection)
        updateObjList(scene, objs)
    print("\nDiscretization - Halving pass:")
    kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 0, 'BCB_CuttingPlane'], None)
    ### Add new objects to the object list and remove deleted ones
    updateObjList(scene, selection)
    updateObjList(scene, objs)

    ### 1. Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations),
    ### deselect all others and try discretization again with triangulation
    cnt = 0
    failed = []
    for obj in objs:
        ### Calculate diameter for each object
        dim = list(obj.dimensions)
        dim.sort()
        diameter = dim[2]   # Use the largest dimension axis as diameter
        if diameter <= props.preprocTools_dis_siz:
            obj.select = 0
            cnt += 1
        else: failed.append(obj)
    count = len(objs) -cnt
    if count > 0:
        print("\nDiscretization - Triangulation pass (%d left):" %count)
        if props.preprocTools_dis_jus:
            kk_mesh_fracture.run('BCB', ['JUNCTION', 0, 0, 'BCB_CuttingPlane'], None)
            ### Add new objects to the object list and remove deleted ones
            updateObjList(scene, selection)
            updateObjList(scene, objs)
        kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 1, 'BCB_CuttingPlane'], None)
        ### Add new objects to the object list and remove deleted ones
        updateObjList(scene, selection)
        updateObjList(scene, objs)

    ### 2. Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations),
    ### deselect all others and try discretization again with triangulation
    cnt = 0
    failed = []
    for obj in objs:
        ### Calculate diameter for each object
        dim = list(obj.dimensions)
        dim.sort()
        diameter = dim[2]   # Use the largest dimension axis as diameter
        if diameter <= props.preprocTools_dis_siz:
            obj.select = 0
            cnt += 1
        else: failed.append(obj)
    count = len(objs) -cnt
    if count > 0:
        print("\nDiscretization - Non-manifolds pass (%d left):" %count)
        failedExt = []
        for obj in failed:
            # Deselect all objects.
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.scene.objects.active = obj
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass 
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            ### Check if mesh has non-manifolds
            bpy.context.tool_settings.mesh_select_mode = False, True, False
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
            obj.select = 1
            ### Add new objects to the object list and remove deleted ones
            updateObjList(scene, selection)
            updateObjList(scene, objs)
            # Set object centers to geometry origin
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            ### Remove doubles for new objects
            for objTemp in scene.objects:
                if objTemp.select and objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(scene):
                    bpy.context.scene.objects.active = objTemp
                    # Enter edit mode              
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass
                    # Select all elements
                    try: bpy.ops.mesh.select_all(action='SELECT')
                    except: continue
                    # Remove doubles
                    bpy.ops.mesh.remove_doubles(threshold=0.0000000001)
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass 
        if props.preprocTools_dis_jus:
            kk_mesh_fracture.run('BCB', ['JUNCTION', 0, 0, 'BCB_CuttingPlane'], None)
            ### Add new objects to the object list and remove deleted ones
            updateObjList(scene, selection)
            updateObjList(scene, objs)
        kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 1, 'BCB_CuttingPlane'], None)
        ### Add new objects to the object list and remove deleted ones
        updateObjList(scene, selection)
        updateObjList(scene, objs)
    
    ### 3. Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations)
    ### print warning message together with a list of the problematic objects
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
    if count > 0:
        print("\nWarning: Following %d objects couldn't be discretized sufficiently:" %count)
        for obj in failed:
            print(obj.name)
    else: print("\nDiscretization verified and successful!")
    print("Final element count:", len(objs))
            
    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

    # Delete cutting plane object
    bpy.context.scene.objects.unlink(objC)

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
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene)]
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

    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive
    
################################################################################

def tool_fixFoundation(scene):

    print("\nSearching foundation elements...")

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body != None]
    if len(objs) == 0:
        print("No rigid body objects selected.")
        return

    props = bpy.context.window_manager.bcb
    
    ### Foundation detection based on ground level 
    if len(props.preprocTools_fix_nam) == 0:
        for obj in objs:
            if obj.location.z < props.preprocTools_fix_lev:
                obj.rigid_body.type = 'PASSIVE'

    ### Foundation detection based on name
    else:
        for obj in objs:
            if props.preprocTools_fix_nam in obj.name:
                obj.rigid_body.type = 'PASSIVE'

################################################################################

def tool_groundMotion(scene):

    print("\nApplying ground motion...")

    props = bpy.context.window_manager.bcb
    q = 0
    if len(props.preprocTools_gnd_obj) == 0: q = 1
    try: objGnd = scene.objects[props.preprocTools_gnd_obj]
    except: q = 1
    if q:
        print("No ground object defined.")
        return

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass

    # Backup selection
    selection = [obj for obj in bpy.context.scene.objects if obj.select]
    selectionActive = bpy.context.scene.objects.active
    # Find mesh objects in selection
    objs = [obj for obj in selection if obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body != None and obj.rigid_body.type == 'PASSIVE']
    if len(objs) == 0:
        print("No passive rigid body mesh objects selected.")
        return

    ###### Parenting to ground object
    
    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    # Select passive mesh objects
    for obj in objs: obj.select = 1

    ### Make obj parent for selected objects
    bpy.context.scene.objects.active = objGnd  # Parent
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # Apply rigid body settings to ground object
    if objGnd.rigid_body == None:
        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')
        # Apply rigid body settings
        objGnd.select = 1
        bpy.context.scene.objects.active = objGnd
        bpy.ops.rigidbody.objects_add()
        objGnd.select = 0
    objGnd.rigid_body.type = 'PASSIVE'
    
    # Enable animated flag for all passive rigid bodies so that Bullet takes their motion into account
    for obj in objs: obj.rigid_body.kinematic = True
    objGnd.rigid_body.kinematic = True

    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

    ###### Creating artificial earthquak motion curves for ground object

    if not props.preprocTools_gnd_nac: return
    
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
    fmod.strength = amplitude *4
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
    fmod.strength = amplitude *4
    fmod.depth = 1
    fmod.use_restricted_range = True
    fmod.frame_start = 1
    fmod.frame_end = duration *fps_rate
    fmod.blend_in = (duration *fps_rate) /2
    fmod.blend_out = (duration *fps_rate) /2

    # Z axis
    fmod = curveLocZ.modifiers.new(type='NOISE')
    fmod.scale = fps_rate /frequency
    fmod.phase = seed +2000
    fmod.strength = amplitude
    fmod.depth = 1
    fmod.use_restricted_range = True
    fmod.frame_start = 1
    fmod.frame_end = duration *fps_rate
    fmod.blend_in = (duration *fps_rate) /2
    fmod.blend_out = (duration *fps_rate) /2
