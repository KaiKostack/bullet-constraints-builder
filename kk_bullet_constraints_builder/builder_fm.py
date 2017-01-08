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

    ### Set up warm up timer via gravity (not exactly the way it works via BCB build but it helps to stabilize the simulation anyway)
    scene.animation_data_create()
    scene.animation_data.action = bpy.data.actions.new(name="Gravity")
    curve = scene.animation_data.action.fcurves.new(data_path="gravity", index=2)  
    curve.keyframe_points.add(2)
    frame = scene.frame_start
    curveP = curve.keyframe_points[0]; curveP.co = frame, 0
    curveP.handle_left = curveP.co; curveP.handle_right = curveP.co; curveP.handle_left_type = 'AUTO_CLAMPED'; curveP.handle_right_type = 'AUTO_CLAMPED'
    frame = scene.frame_start +props.warmUpPeriod
    curveP = curve.keyframe_points[1]; curveP.co = frame, -9.81
    curveP.handle_left = curveP.co; curveP.handle_right = curveP.co; curveP.handle_left_type = 'AUTO_CLAMPED'; curveP.handle_right_type = 'AUTO_CLAMPED'
    ### Fix smooth curves as handles are not automatically being set correctly
    # Stupid Blender design hack, enforcing context to be accepted by operators
    areaType_bak = bpy.context.area.type; bpy.context.area.type = 'GRAPH_EDITOR'
    bpy.ops.graph.handle_type(type='AUTO_CLAMPED')
    #bpy.ops.graph.clean(channels=True)
    bpy.context.area.type = areaType_bak
        
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
    indexmap = dict()
    j = 0
    for i in range(len(consts)):
        objN1 = consts[i][2]
        objN2 = consts[i][3]
        if not objN1 in objsName:
            try: obj1 = bpy.context.scene.objects[objN1]
            except: pass
            else:
                objs.append(obj1)
                objsName.append(objN1)
                
        if not objN2 in objsName:
            try: obj2 = bpy.context.scene.objects[objN2]
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
    for i in range(len(objs)):
        obj = objs[i]
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
    
    ### Create constraints
    plastic_on = 0
    plastic_off = 0
    noplastic = 0
    for i in range(len(consts)):
        cProp_index = 0
        j = 0
        name = consts[i][j]
        j += 1
        
        # 0 - empty.location
        pos = mathutils.Vector(consts[i][j])
        j += 1
        
        # 1 - obj1.name
        # 2 - obj2.name
        ob1 = consts[i][j]
        ob2 = consts[i][j+1]
        j += 2
        
        # 3 - [ ["TOLERANCE", tol1dist, tol1rot] ]
        if consts[i][j] is not None and len(consts[i][j]) == 3 and consts[i][j][0] in {"TOLERANCE"}:
            breaking_distance = consts[i][j][1]
            breaking_angle = consts[i][j][2]
        else:
            breaking_distance = -1
            breaking_angle = -1
        j += 1
        
        # 4 - [ ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot] ]
        if consts[i][j] is not None and len(consts[i][j]) == 3 and consts[i][j][0] in {"PLASTIC", "PLASTIC_OFF"}: #ugh, variable length ?
            plastic_distance = consts[i][j][1]
            plastic_angle = consts[i][j][2]
            
            if consts[i][j][0] == "PLASTIC": 
                plastic = True
                plastic_on += 1
            else:
                plastic = False
                plastic_off += 1
        else:
            plastic_distance = -1
            plastic_angle = -1
            plastic = False
            noplastic += 1
        j += 1    
        
        # 5 - [empty.rotation_mode]
        # 6 - [empty.rotation_quaternion]
        if consts[i][j] == "QUATERNION":  # If no quaternion exists we assume no rotation is available
            rot = mathutils.Quaternion(consts[i][j+1])
        else:  # If None or EULER then no rotation is available
            rot = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
        j += 2
                
        # 7 - empty.rigid_body_constraint (dictionary of attributes)
        cProps = consts[i][j]
        cProp_index = j
        
        # Peek the type...
        type = cProps["type"]
        if type != "GENERIC_SPRING":
            noplastic -= 1
        
        # OK, first check whether the mi exists via is object in group (else it's double)
        try: con = md.mesh_constraints.new(indexmap[ob1], indexmap[ob2], type)
        except: pass
        else:
            con.location = pos # ob.matrix_world *pos
            #rot.rotate(ob.matrix_world)
            con.rotation = rot
            con.plastic = plastic
            con.breaking_distance = breaking_distance
            con.breaking_angle = breaking_angle
            con.plastic_distance = plastic_distance
            con.plastic_angle = plastic_angle
            con.name = name
               
            for p in cProps.items():
                if p[0] not in {"type", "object1", "object2"}:
                    attr = getattr(con, p[0])
                    if attr != p[1]:
                        #print("Set: ", p[0], p[1])
                        setattr(con, p[0], p[1])
                
            #con.id = cProps["name"]
            #if con.type == 'GENERIC_SPRING':
            #    con.spring_stiffness_x = 1000000
            #    con.spring_stiffness_y = 1000000
            #    con.spring_stiffness_z = 1000000
            #con.enabled = True
            
            #con.breaking_threshold = con.breaking_threshold * 150.0 / 200.0 
            #con.breaking_angle = math.radians(con.breaking_angle)
            #con.plastic_angle = math.radians(con.plastic_angle)
            #con.plastic_angle *= 0.5
            #con.breaking_angle *= 0.5
            #con.breaking_threshold *= 0.5
            #con.breaking_angle = math.radians(5.0)
            #con.breaking_distance = 0.1
            #con.plastic = False
            
    #        ind = cProp_index+1
    #        if len(consts[i][ind]) == 3 and consts[i][ind][0] == "BREAK":
    #            con.breaking_distance = consts[i][ind][1] # this is normed to 0...1, odd... why not absolute ?
    #            con.breaking_angle = consts[i][ind][2] * math.pi

    # Clumsy, but could work: disable plastic globally, when no plastic has been found at all
    #if plastic_on == 0 and plastic_off == 0:
    #    for i in range(len(consts)):
    #        md.mesh_constraints[i].plastic_angle = -1
    #        md.mesh_constraints[i].plastic_distance = -1
    
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
    print('Imported: %d Plastic ON,  %d Plastic OFF,  %d NOPLASTIC' % (plastic_on, plastic_off, noplastic))
    print('Done.')
    print()
