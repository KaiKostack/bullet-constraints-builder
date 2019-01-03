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
# Copyright (C) 2015-2018 Kai Kostack
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

import bpy, bmesh, mathutils, time, pickle, zlib, base64
from mathutils import Vector
from bpy.app.handlers import persistent
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *          # Contains file input & output functions

################################################################################

def build_fm(use_handler=0):

    ### Exports all constraint data to the Fracture Modifier (special Blender version required).
    time_start = time.time()

    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene

    ### Create new animation data and action if necessary
    if scene.animation_data == None:
        scene.animation_data_create()
    if scene.animation_data.action == None:
        scene.animation_data.action = bpy.data.actions.new(name="BCB")
    
    ### Set up warm up timer via gravity
    dna_animation_path = "gravity"; animation_index = 2
    curve = scene.animation_data.action.fcurves.find(data_path=dna_animation_path, index=animation_index)
    ### Delete previous animation while preserving the end value
    if curve != None:
        if len(curve.keyframe_points) > 0:
            curveP = curve.keyframe_points[-1]
            frame, value = curveP.co
            scene.animation_data.action.fcurves.remove(curve)  # Delete curve
            bpy.context.scene.gravity[2] = value  # Restore original value
    if props.warmUpPeriod:
        # Create new curve
        curve = scene.animation_data.action.fcurves.new(data_path=dna_animation_path, index=animation_index)  # Recreate curve  
        ### Create curve points
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

    ### Set up time scale period
    dna_animation_path = "rigidbody_world.time_scale"; animation_index = 0
    curve = scene.animation_data.action.fcurves.find(data_path=dna_animation_path, index=animation_index)
    ### Delete previous animation while preserving the end value
    if curve != None:
        if len(curve.keyframe_points) > 0:
            curveP = curve.keyframe_points[-1]
            frame, value = curveP.co
            scene.animation_data.action.fcurves.remove(curve)  # Delete curve
            scene.rigidbody_world.time_scale = value  # Restore original value
    if props.timeScalePeriod:
        # Create new curve
        curve = scene.animation_data.action.fcurves.new(data_path=dna_animation_path, index=animation_index)  # Recreate curve  
        ### Create curve points
        curve.keyframe_points.add(2)
        frame = scene.frame_start +props.timeScalePeriod
        curveP = curve.keyframe_points[0]; curveP.co = frame, props.timeScalePeriodValue
        #curveP.handle_left = curveP.co; curveP.handle_right = curveP.co
        frame += 1
        curveP = curve.keyframe_points[1]; curveP.co = frame, scene.rigidbody_world.time_scale
        #curveP.handle_left = curveP.co; curveP.handle_right = curveP.co
        ### Fix smooth curves as handles are not automatically being set correctly
        # Stupid Blender design hack, enforcing context to be accepted by operators
        #areaType_bak = bpy.context.area.type; bpy.context.area.type = 'GRAPH_EDITOR'
        #bpy.ops.graph.handle_type(type='AUTO_CLAMPED')
        # Alternative: bpy.ops.graph.clean(channels=True)
        #bpy.context.area.type = areaType_bak
    
    ### Create object to use the Fracture Modifier on
    bpy.ops.mesh.primitive_ico_sphere_add(size=1, view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
    ob = bpy.context.scene.objects.active
    #ob.data.use_auto_smooth = True
    ob.name = asciiExportName
    ob.data.name = asciiExportName
    ob.show_transparent = True

    layersBak = [int(q) for q in scene.layers]   # Backup scene layer settings
    scene.layers = [True for q in scene.layers]  # Activate all scene layers

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Disable objects (and search for parent)
    if use_handler:
        objParent = None

        ### Unpack BCB data from text file
        try: s = bpy.data.texts[asciiExportName +".txt"].as_string()
        except:
            print("Error: No export data found, couldn't build Fracture Modifier object.")
            return
        cDef, exData, exPairs, objNames = pickle.loads(zlib.decompress(base64.decodestring(s.encode())))

        ### Prepare objects list from names (using dictionary for faster item search)
        scnObjs = {}
        for obj in scene.objects: scnObjs[obj.name] = obj
        objs = []
        for name in objNames:
            try: objs.append(scnObjs[name])
            except: objs.append(None)

        for obj in objs:
            if obj.parent: objParent = obj.parent; break

        ### Remove from RigidBodyWorld (if enabled)
        grpRBWorld = bpy.data.groups["RigidBodyWorld"]
        for obj in objs:
            try: grpRBWorld.objects.unlink(obj)
            except: pass
        scene.update()  # Required to make RBs actually not participating in simulation anymore

        # Move to last layer
        for obj in objs: obj.select = 1
        bpy.ops.object.move_to_layer(layers=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, True))

    # Add Fracture Modifier
    bpy.ops.object.modifier_add(type='FRACTURE')
    md = ob.modifiers["Fracture"]

    # Change some FM settings
    md.fracture_mode = 'PREFRACTURED'
    md.use_constraint_collision = not props.disableCollision
    md.fracture_mode = 'EXTERNAL'

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Enable trigger possibility
    ob.select = 1
    bpy.ops.rigidbody.object_add()
    ob.rigid_body.use_kinematic_deactivation = 1  # "Triggered"

    # Start not being triggered but able to dissolve constraints by triggers (default)
    if 1:
        ob.rigid_body.kinematic = 0  # 0 | "Animated"
        ob.rigid_body.constraint_dissolve = 1
        ob.rigid_body.plastic_dissolve = 1
    # Start being triggered, requires a trigger to activate objects
    else:
        ob.rigid_body.kinematic = 1  # "Animated"
        ob.rigid_body.constraint_dissolve = 0 
        ob.rigid_body.plastic_dissolve = 0

    ob.select = 0
    
    ###### Preparing air drag simulation
    air(scene)

    ### Building FM object

    if not use_handler:
        md.fracture_mode = 'EXTERNAL'
        ###### Shards
        objParent = FM_shards(ob)
        ###### Constraints
        FM_constraints(ob)

    elif use_handler:
        md.fracture_mode = 'DYNAMIC'
        md.use_constraints = True
        md.dynamic_force = 20
        md.dynamic_new_constraints = 'NO_CONSTRAINTS'  # 'ALL_CONSTRAINTS', 'MIXED_CONSTRAINTS', 'NO_CONSTRAINTS'
        md.dynamic_percentage = 50
        md.shard_count = 2
        #md.point_source = set()
        md.frac_algorithm = 'BOOLEAN_FRACTAL'
        md.fractal_iterations = 3
        md.limit_impact = True
        md.is_dynamic_external = True  # Special flag to notify the FM that the source of the data is external and that it should never be changed even for dynamic mode
        # Remove old refresh handler from memory if loaded
        if len(bpy.app.handlers.fracture_refresh) > 0:
            bpy.app.handlers.fracture_refresh.clear()
        ###### Shards handler
        bpy.app.handlers.fracture_refresh.append(FM_shards)

    #bpy.ops.object.fracture_refresh()

    bpy.context.scene.objects.active = None
    ob.select = 0
    
    # Delete objects
    if not use_handler:
        bpy.ops.object.delete(use_global=True)

    ### Apply parent if found
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

    print()
    print('-- Time total: %0.2f s' %(time.time()-time_start))
    print('Done.')
    print()
    
########################################

def air(scene):

    ### Storing geometry data for air drag simulation
    try: grp = bpy.data.groups["Air_Enabled"]
    except: return
    else: objs = grp.objects
    try: grp = bpy.data.groups["Air_Pressure"]
    except: objsPres = []
    else: objsPres = grp.objects
    try: grp = bpy.data.groups["Air_Fixed"]
    except: objsFixed = []
    else: objsFixed = grp.objects
   
    areas = []; normals = []
    for obj in objs:
        # Cross sectional area
        dim = obj.dimensions; dimAxis = [0, 1, 2]
        dim, dimAxis = zip(*sorted(zip(dim, dimAxis)))
        areaMax = dim[1] *dim[2]  # Maximum approx. cross sectional area
        areaMin = dim[0] *dim[1]  # Minimum approx. cross sectional area

        ### Derive average normal for element from mesh faces
        me = obj.data
        areaTot = 0
        normal = Vector((0, 0, 0)) 
        for face in me.polygons:
            normal += face.normal *face.area
            areaTot += face.area
        normal /= areaTot

        ### If no valid normal could be found then generate one from dimensions
        if normal.length == 0:
            smallestAxis = dimAxis[0]
            if smallestAxis == 0:   vecAxis = Vector((1, 0, 0))
            elif smallestAxis == 1: vecAxis = Vector((0, 1, 0))
            else:                   vecAxis = Vector((0, 0, 1))
            if obj.rotation_mode == 'EULER':
                  matInv = obj.rotation_euler.to_matrix().inverted()
            else: matInv = obj.rotation_quaternion.to_matrix().inverted()
            normal = vecAxis *matInv

        normal = normal.normalized()

        areas.append([areaMax, areaMin])
        normals.append(normal)

    scene["air_objsName"] = [ob.name for ob in objs]
    scene["air_objsPresName"] = [ob.name for ob in objsPres]
    scene["air_objsFixedName"] = [ob.name for ob in objsFixed]
    scene["air_areas"] = areas
    scene["air_normals"] = normals

########################################

@persistent
def FM_shards(ob):

    print()
    print("Creating Fracture Modifier mesh from BCB data...")
    time_start = time.time()

    scene = bpy.context.scene

    md = ob.modifiers["Fracture"]
    fmode_bak = md.fracture_mode
    md.fracture_mode = 'EXTERNAL'

    ### Unpack BCB data from text file
    try: s = bpy.data.texts[asciiExportName +".txt"].as_string()
    except:
        print("Error: No export data found, couldn't build Fracture Modifier object.")
        return
    cDef, exData, exPairs, objNames = pickle.loads(zlib.decompress(base64.decodestring(s.encode())))

    ### Prepare objects list (using dictionaries for faster item search)
    scnObjs = {}
    for obj in scene.objects: scnObjs[obj.name] = obj
    objs = []
    for name in objNames:
        try: objs.append(scnObjs[name])
        except: objs.append(None)

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
    
    md.fracture_mode = fmode_bak
    
    print('Time mesh islands: %0.2f s' %(time.time()-time_start))
    print('Imported: %d shards' %len(md.mesh_islands))

    ###### Constraints handler (run only when this function is loaded as handler, too)
    if len(bpy.app.handlers.fracture_refresh) > 0:
        bpy.app.handlers.fracture_constraint_refresh.append(FM_constraints)
    
    return objParent

########################################

@persistent
def FM_constraints(ob):

    # Pseudo code for special constraint treatment:
    #
    # If tol1dist or tol1rot is exceeded:
    #     If normal constraint: It will be detached
    #     If spring constraint: It will be set to active
    # If tol2dist or tol2rot is exceeded:
    #     If spring constraint: It will be detached

    print()
    print("Creating Fracture Modifier constraints from BCB data...")
    time_const = time.time()

    scene = bpy.context.scene

    md = ob.modifiers["Fracture"]
    fmode_bak = md.fracture_mode
    md.fracture_mode = 'EXTERNAL'

    ### Create dict of FM mesh islands (speed optimization)
    mesh_islands = {}
    for mi in md.mesh_islands:
        mesh_islands[mi.name] = mi

    ### Unpack BCB data from text file
    try: s = bpy.data.texts[asciiExportName +".txt"].as_string()
    except:
        print("Error: No export data found, couldn't build Fracture Modifier object.")
        return
    cDef, exData, exPairs, objNames = pickle.loads(zlib.decompress(base64.decodestring(s.encode())))

    ### Overwrite mesh island settings with those from the original RBs (FM overwrites this state)
#    # Remove refresh handler from memory (required to overwrite settings)
#    if len(bpy.app.handlers.fracture_refresh) > 0:
#        bpy.app.handlers.fracture_refresh.clear()
#        qHandler = 1
#    else: qHandler = 0
    # Overwrite mesh island settings
    for mi in md.mesh_islands:
        obj_rb = scene.objects[mi.name].rigid_body
        #print("mass", mi.rigidbody.mass, mi.name)
        mi.rigidbody.type = obj_rb.type
        mi.rigidbody.kinematic = obj_rb.kinematic
        mi.rigidbody.collision_shape = obj_rb.collision_shape
        mi.rigidbody.mass = obj_rb.mass
        mi.rigidbody.friction = obj_rb.friction
        mi.rigidbody.restitution = obj_rb.restitution
        mi.rigidbody.use_margin = obj_rb.use_margin
        mi.rigidbody.collision_margin = obj_rb.collision_margin
        
#    # Reload refresh handler
#    if qHandler:
#        bpy.app.handlers.fracture_refresh.append(FM_shards)

    ### Copy custom (not BCB generated) constraints between original shards to the FM
    try: emptyObjs = bpy.data.groups["RigidBodyConstraints"].objects
    except: emptyObjs = []
    emptyObjs = [obj for obj in emptyObjs if obj.type == 'EMPTY' and not obj.hide and obj.is_visible(bpy.context.scene) and obj.rigid_body_constraint != None]
    for objConst in emptyObjs:
        if "BCB_FM" not in objConst.keys():
            objA = objConst.rigid_body_constraint.object1
            objB = objConst.rigid_body_constraint.object2
            if objA != None and objB != None \
            and objA.name in objNames and objB.name in objNames:
                cProps = getAttribsOfConstraint(objConst.rigid_body_constraint)
                ### Add settings to constraint
                try: con = md.mesh_constraints.new(mesh_islands[objA.name], mesh_islands[objB.name], cProps["type"])
                except: pass
                else:
                    objConst["BCB_FM"] = 1  # Mark empty as used in FM
                    con.name = objConst.name
                    con.location = objConst.location
                    if objConst.rotation_mode == "QUATERNION": con.rotation = objConst.rotation_quaternion
                    else: con.rotation = objConst.rotation_euler.to_quaternion()
                    ### Write constraint parameters
                    for p in cProps.items():
                        if p[0] not in {"object1", "object2"}:
                            try: attr = getattr(con, p[0])  # Current value
                            except:
                                if p[0] not in missingAttribs: missingAttribs.append(p[0])
                            else:
                                if p[1] != attr:           # Overwrite only when different
                                    #print("Set: ", p[0], p[1])
                                    setattr(con, p[0], p[1])

    ### Create BCB constraints
    cnt = 0
    missingAttribs = []
    for pair in exPairs:
        ### Get data that is only stored once per connection
        ob1    = pair[0]
        ob2    = pair[1]
        consts = pair[2]
        
        for const in consts:
            cProps, cDatb = exData[const]
                 
            ### Get data that can be individual for each constraint
            name = cDatb[0]  # A name is not mandatory, mainly for debugging purposes
            loc  = cDatb[1]
            tol1 = cDatb[4]
            tol2 = cDatb[5]
            rotm = cDatb[6]
            rot  = cDatb[7]
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
            try: con = md.mesh_constraints.new(mesh_islands[ob1], mesh_islands[ob2], type)
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
                    
                ### Obsolete since FM now uses Blender defaults for constraints:
                ### Write constraint defaults first (FM doesn't set constraint to Blender defaults)
                for p in cDef.items():
                    if p[0] not in {"object1", "object2"}:
                        try: attr = getattr(con, p[0])  # Current value
                        except:
                            if p[0] not in missingAttribs: missingAttribs.append(p[0])
                        else:
                            if p[1] != attr:           # Overwrite only when different
                                #print("attr", p[0], p[1], attr)
                                setattr(con, p[0], p[1])
                ### Write own changed parameters (because it's a diff based on defaults)
                for p in cProps.items():
                    if p[0] not in {"object1", "object2"}:
                        try: attr = getattr(con, p[0])  # Current value
                        except:
                            if p[0] not in missingAttribs: missingAttribs.append(p[0])
                        else:
                            if p[1] != attr:           # Overwrite only when different
                                #print("Set: ", p[0], p[1])
                                setattr(con, p[0], p[1])
                cnt += 1

    if len(missingAttribs):
        print("Warning: Following constraint attribute(s) missing:")
        print("(This is a bug in FM, branch seems not to be up to date with Blender.)")
        for attr in missingAttribs: print(attr)

    md.fracture_mode = fmode_bak
    md.refresh = False

    print('Time constraints: %0.2f s' %(time.time()-time_const))
    print('Imported: %d constraints (%d shards)' %(cnt, len(md.mesh_islands)))

    # Remove this handler from memory (will be reloaded on FM_shards())
    bpy.app.handlers.fracture_constraint_refresh.clear()
