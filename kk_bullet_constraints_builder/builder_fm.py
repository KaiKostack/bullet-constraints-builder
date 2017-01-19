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

import bpy, mathutils, time, pickle, zlib, base64
from mathutils import Vector
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *          # Contains file input & output functions

################################################################################

def build_fm():

    props = bpy.context.window_manager.bcb

    ### Exports all constraint data to the Fracture Modifier (special Blender version required).
    print()
    print("Creating fracture modifier mesh from BCB data...")
    time_start = time.time()

    scene = bpy.context.scene

    try: s = bpy.data.texts["BCB_export.txt"].as_string()
    except:
        print("Error: No export data found, couldn't build fracture modifier object.")
        return
    consts = pickle.loads(zlib.decompress(base64.decodestring(s.encode())))

    ### Set up warm up timer via gravity
    if "Gravity" in bpy.data.actions.keys() and scene.animation_data.action != None:
        # Delete previous gravity animation while preserving the end value
        curve = scene.animation_data.action.fcurves.find(data_path="gravity", index=2)  
        curveP = curve.keyframe_points[-1]
        frame, value = curveP.co
        #curve.keyframe_points.remove(curveP, fast=False)
        bpy.data.actions.remove(bpy.data.actions["Gravity"], do_unlink=True)
        bpy.context.scene.gravity[2] = value
    if props.warmUpPeriod:
        ### Create new gravity animation curve 0 to full strength
        scene.animation_data_create()
        scene.animation_data.action = bpy.data.actions.new(name="Gravity")
        curve = scene.animation_data.action.fcurves.new(data_path="gravity", index=2)  
        curve.keyframe_points.add(2)
        frame = scene.frame_start
        curveP = curve.keyframe_points[0]; curveP.co = frame, 0
        curveP.handle_left = frame -props.warmUpPeriod/2, 0
        curveP.handle_right = frame +props.warmUpPeriod/2, 0
        #curveP.handle_left = curveP.co; curveP.handle_right = curveP.co
        frame = scene.frame_start +props.warmUpPeriod
        curveP = curve.keyframe_points[1]; curveP.co = frame, bpy.context.scene.gravity[2]
        curveP.handle_left = frame -props.warmUpPeriod/2, bpy.context.scene.gravity[2]
        curveP.handle_right = frame +props.warmUpPeriod/2, bpy.context.scene.gravity[2]
        #curveP.handle_left = curveP.co; curveP.handle_right = curveP.co
        ### Fix smooth curves as handles are not automatically being set correctly
        # Stupid Blender design hack, enforcing context to be accepted by operators
        #areaType_bak = bpy.context.area.type; bpy.context.area.type = 'GRAPH_EDITOR'
        #bpy.ops.graph.handle_type(type='AUTO_CLAMPED')
        # Alternative: bpy.ops.graph.clean(channels=True)
        #bpy.context.area.type = areaType_bak
    
    ### Create object to use the fracture modifier on
    bpy.ops.mesh.primitive_ico_sphere_add(size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
    ob = bpy.context.scene.objects.active
    ob.data.use_auto_smooth = True
    ob.name = "BCB_export"
    ob.data.name = "BCB_export"

    layersBak = [int(q) for q in scene.layers]   # Backup scene layer settings
    scene.layers = [True for q in scene.layers]  # Activate all scene layers

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Add fracture modifier
    bpy.ops.object.modifier_add(type='FRACTURE')
    ob.modifiers["Fracture"].fracture_mode = 'EXTERNAL'
    md = ob.modifiers["Fracture"]

    objs = []; objsName = []
    j = 0
    for i in range(len(consts)):
        objN1 = consts[i]["bcb_obj1"]
        objN2 = consts[i]["bcb_obj2"]
        if not objN1 in objsName:
            try: obj1 = scene.objects[objN1]
            except: pass
            else:
                objs.append(obj1)
                objsName.append(objN1)
        if not objN2 in objsName:
            try: obj2 = scene.objects[objN2]
            except: pass
            else:
                objs.append(obj2)
                objsName.append(objN2)

#    ### Sort mesh objects by database order (old slower code)
#    objsSorted = []
#    #for objDB in bpy.data.objects:  # Sort by bpy.data order
#    for objDB in bpy.data.groups["RigidBodyWorld"].objects:  # Sort by RigidBodyWorld group order
#        for obj in objs:
#            if obj.name == objDB.name:
#                objsSorted.append(obj)
#                del objs[objs.index(obj)]
#                break
    ### Sort mesh objects by database order
    objsSource = objs
    objsDB = bpy.context.scene.objects
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
#    print("MESHES (original, DB):")
#    for i in range(len(objsSource)):
#        obj = objsSource[i]
#        objSorted = objsSortedFiltered[i]
#        print(obj.name, objSorted.name)
    objs = objsSortedFiltered

    ### Create mesh islands    
    objParent = None
    indexmap = dict()
    for obj in objs:
        if obj.name not in indexmap.keys():
            indexmap[obj.name] = md.mesh_islands.new(obj)
            #indexmap[objFM].rigidbody.use_margin = True
            #if obj.rigid_body.type == 'PASSIVE':
            #    indexmap[objFM].rigidbody.kinematic=True
            #    indexmap[objFM].rigidbody.type='ACTIVE'
            if objParent == None and obj.parent: objParent = obj.parent
            obj.select = True
    
    print('Time mesh islands: %0.2f s' %(time.time()-time_start))
    time_const = time.time()
    
    ###### Constraints

    # Pseudo code for special constraint treatment:
    #
    # If tol1dist or tol1rot is exceeded:
    #     If normal constraint: It will be detached
    #     If spring constraint: It will be set to active
    # If tol2dist or tol2rot is exceeded:
    #     If spring constraint: It will be detached

    ### Create temporary empty object to get the default attributes
    objConst = bpy.data.objects.new('Constraint', None)
    bpy.context.scene.objects.link(objConst)
    bpy.context.scene.objects.active = objConst
    bpy.ops.rigidbody.constraint_add()
    cDef = getAttribsOfConstraint(objConst.rigid_body_constraint)
    rot = objConst.rotation_quaternion
    # Remove constraint settings and delete temporary empty object again
    bpy.ops.rigidbody.constraint_remove()
    scene.objects.unlink(objConst)

    ### Create constraints
    cnt = 0
    for i in range(len(consts)):
        cProps = consts[i]
        
        ### Get custom BCB attributes
        name = cProps["bcb_name"]
        loc  = cProps["bcb_loc"]
        ob1  = cProps["bcb_obj1"]
        ob2  = cProps["bcb_obj2"]
        try:    tol1 = cProps["bcb_tol1"]
        except: tol1 = None
        try:    tol2 = cProps["bcb_tol2"]
        except: tol2 = None
        try:    rotm = cProps["bcb_rotm"]
        except: rotm = None
        try:    rot  = cProps["bcb_rot"]
        except: rot  = None
        try:    type = cProps["type"]
        except: type = cDef["type"]
        
        ### Decode custom BCB attributes
        # 1st tolerances (elastic -> plastic)
        # ["TOLERANCE", tol1dist, tol1rot]
        if tol1 is not None and tol1[0] in {"TOLERANCE"}:
            tol1dist = tol1[1]
            tol1rot = tol1[2]
        else:
            tol1dist = -1
            tol1rot = -1
        # 2nd tolerances (plastic -> broken)
        # ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot]
        if tol2 is not None and tol2[0] in {"PLASTIC", "PLASTIC_OFF"}:
            tol2dist = tol2[1]
            tol2rot = tol2[2]
            if tol2[0] == "PLASTIC": plastic = True
            else: plastic = False
        else:
            tol2dist = -1
            tol2rot = -1
            plastic = False
        # Rotation
        if rotm == "QUATERNION":  # If no quaternion exists we assume no rotation is available
            rot = mathutils.Quaternion(rot)
        else:  # If None or EULER then no rotation is available
            rot = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
        
        ### Add settings to constraint
        # OK, first check whether the mi exists via is object in group (else it's double)
        try: con = md.mesh_constraints.new(indexmap[ob1], indexmap[ob2], type)
        except: pass
        else:
            con.name = name
            con.location = loc
            con.rotation = rot
            con.plastic = plastic
            con.breaking_distance = tol1dist
            con.breaking_angle = tol1rot
            con.plastic_distance = tol2dist
            con.plastic_angle = tol2rot

            ### Write constraint defaults first (FM doesn't set constraint to Blender defaults)
            for p in cDef.items():
                if p[0] not in {"object1", "object2"} \
                and "bcb_" not in p[0]:        # Filter also custom BCB attributes
                    attr = getattr(con, p[0])  # Current value
                    if p[1] != attr:           # Overwrite only when different
                        setattr(con, p[0], p[1])
            ### Write own changed parameters (because it's a diff based on defaults)
            for p in cProps.items():
                if p[0] not in {"object1", "object2"} \
                and "bcb_" not in p[0]:        # Filter also custom BCB attributes
                    attr = getattr(con, p[0])  # Current value
                    if p[1] != attr:           # Overwrite only when different
                        #print("Set: ", p[0], p[1])
                        setattr(con, p[0], p[1])
            cnt += 1

    print('Time constraints: %0.2f s' %(time.time()-time_const))
    
    #bpy.ops.object.fracture_refresh()
    bpy.context.scene.objects.active = None
    ob.select = False
    
    bpy.ops.object.delete(use_global=True)

    # Apply parent if one has been found earlier
    if objParent != None:
        ob.select = 1
        objParent.select = 1
        bpy.context.scene.objects.active = objParent
        print("Parenting", ob.name, "to", objParent.name, "...")
        try: bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        except:
            print("Error: Parenting failed. This can happen when not only the structure")
            print("was selected but also the ground.")
        objParent.select = 0
        bpy.context.scene.objects.active = ob

    scene.layers = [bool(q) for q in layersBak]  # Revert scene layer settings from backup

    print('-- Time total: %0.2f s' %(time.time()-time_start))
    print()
    print('Imported: %d constraints' %cnt)
    print('Done.')
    print()
