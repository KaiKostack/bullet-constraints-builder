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

import bpy
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
    props = bpy.context.window_manager.bcb
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
                elemGrps.append(elemGrps[props.menu_selectedElemGrp].copy())
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
        print("No mesh objects selected. Nothing done.")
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
    print("\nDiscretization - Halving pass:")
    kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 0, 'BCB_CuttingPlane'], None)

    ### Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations),
    ### deselect all others and try discretization again with triangulation
    cnt = 0
    for obj in objs:
        ### Calculate diameter for each object
        dim = list(obj.dimensions)
        dim.sort()
        diameter = dim[2]   # Use the largest dimension axis as diameter
        if diameter <= props.preprocTools_dis_siz:
            obj.select = 0
            cnt += 1
    if len(objs) -cnt > 0:
        print("\nDiscretization - Triangulation pass:")
        kk_mesh_fracture.run('BCB', ['HALVING', props.preprocTools_dis_siz, 1, 'BCB_CuttingPlane'], None)
    
    ### Check if there are still objects larger than minimumSizeLimit left (due to failed boolean operations)
    cnt = 0
    failed = []
    for obj in objs:
        ### Calculate diameter for each object
        dim = list(obj.dimensions)
        dim.sort()
        diameter = dim[2]   # Use the largest dimension axis as diameter
        if diameter <= props.preprocTools_dis_siz:
            cnt += 1
        else: failed.append(obj.name)
    if len(objs) -cnt > 0:
        print("\nWarning: Following %d objects couldn't be discretized sufficiently:" %(len(objs) -cnt))
        for name in failed:
            print(name)
        
    # Revert to start selection
    for obj in selection: obj.select = 1
    bpy.context.scene.objects.active = selectionActive

    # Delete cutting plane object
    bpy.context.scene.objects.unlink(objC)

################################################################################

def tool_enableRigidBodies(scene):

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

    # Leave edit mode to make sure next operator works in object mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
