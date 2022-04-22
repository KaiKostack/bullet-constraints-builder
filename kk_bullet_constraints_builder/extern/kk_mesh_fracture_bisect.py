#############################################
# Mesh Bisect Fracture v1.73 by Kai Kostack #
#############################################

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
 
import bpy, sys, random, time, mathutils
from mathutils import *

################################################################################   

def run(sceneOriginal, objsSource, crackOrigin, qDynSecondScnOpt):
    
    ### Vars
    qFill = 1                       #      | Enables filling of the holes after fracture
    objectCountLimit = 5            # 10   | Shard count to be generated per selected object (might be less because of other limits)
    bisectErrorRetryLimit = 3       # 3    | How often to retry if bisect operation fails
    minimumSizeLimit = 0.5          # 0.3  | Minimum dimension for a shard to be still considered for fracturing, at least two dimension axis must be above this size

    materialPreset = 'Concrete'     # See Blender rigid body tools for a list of available presets
    materialDensity = 0             # Custom density value (kg/m^3) to use instead of material preset (0 = disabled)

    qSeparateLoose = 1              # 1    | Perform Separate Loose on all shards at start
    qSeparateLooseStep = 1          # 1    | Perform Separate Loose on shards after each fracture step

    ### Vars for halving
    qUseHalving = 0                 # 0    | Enables special mode for subdividing meshes into halves until either minimumSizeLimit or objectCountLimit is reached (sets bisectErrorRetryLimit = 0)
                                    #      | It's recommended to set the latter to a very high count to get a universal shard size. This is incompatible with Dynamic Fracture because object centers are changed.
    qSplitAtJunctions = 0           # 1    | Try to split cornered walls at the corner rather than splitting based on object space to generate more clean shapes
    junctionTol = .001              # .001 | Tolerance for junction detection to avoid cutting off of very thin geometry slices (requires normals consistently pointing outside)
    junctionTolMargin = .01         # .01  | Margin inside the object boundary box borders to skip junction detection (helps to avoid cutting of similar faces which can lead to hundreds of thin mesh slices, should be larger than junctionTol) 
    junctionTolRect = .001          # .001 | Tolerance to enforce rectangular shapes in radian, larger values will allow more diagonal cuts (0 = no restriction)
    junctionMaxFaceCnt = 0          # 0    | Sets a limit to skip search for junctions after this many faces have been checked (helps to skip very dense meshes more quickly, 0 = disabled)

    ### Vars for system (should have no influence on result)
    qSecondScnOpt = 1               # 1    | Use an empty new scene for object creation, improves performance only for huge amounts of objects in scene and is incompatible with the Dynamic Fracture script (will be disabled when in use)
    qDebugVerbose = 0               # 0    | Shows verbose output in console like function names
    qSilentVerbose = 0              # 0    | Reduces text output to a minimum

    ### Custom BCB parameter handling
    if objsSource == 'BCB':
        parameters = crackOrigin  # BCB data is passed through this variable for compatibility reasons (could be improved)
        # For halving cuts
        if parameters[0] == 'HALVING':
            qUseHalving = 1
            qSplitAtJunctions = 0
            minimumSizeLimit = parameters[1]
        # For junction cuts
        elif parameters[0] == 'JUNCTION':
            qUseHalving = 1
            qSplitAtJunctions = 1
        qTriangulate = parameters[2]
        objectCountLimit = 100000000
        qSeparateLoose = 0
        qSeparateLooseStep = 0
        qSilentVerbose = 1
        objsSource = None
        crackOrigin = None
    
    ### Corrections
    if objsSource != None: qSecondScnOpt = 0
    if qUseHalving: bisectErrorRetryLimit = 1
    
    ### Constants
    pi = 3.1415927
    pi2 = pi /2

    print("\nStarting splitting process...")

    scene = bpy.context.scene
    bpy.context.tool_settings.mesh_select_mode = False, True, False
    #random.seed(0)
    time_start = time.time()

    # Blender version handling
    if bpy.app.version <= (2, 79, 0) or hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'): version_carve = 1
    else:                                                                                 version_carve = 0

    try: grpRBWorld = bpy.data.groups["RigidBodyWorld"]
    except: grpRBWorld = None
        
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    ###### Create main object list
    if objsSource == None:
        ### Create object list of selected objects
        ### (because we add more objects with following function we need a separate list)
        objs = []
        for obj in scene.objects:
            if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene):
                objs.append(obj)
        print("%d objects found." %len(objs))
    else:
        ### This part allows to fracture objects from database even from a different empty scene (optimization for Dynamic Fracture)
        if qDynSecondScnOpt:
            # Link also objects from objsSource to current scene
            objs = objsSource
            for obj in objs:
                try: bpy.context.screen.scene.objects.link(obj)
                except: pass
        # If no second scene optimization is used in dynamic handler
        else:
            objs = objsSource

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    if qSeparateLoose:
        # Select objects to fracture
        for obj in objs: obj.select = 1
        ### perform separate loose on start objects
        i = 1
        for obj in objs:
            if not qSilentVerbose: sys.stdout.write('\r' +"%d " %i)
            i += 1
            bpy.context.scene.objects.active = obj
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass 
            # Separate Loose
            bpy.ops.mesh.separate(type='LOOSE')
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass
        print()
        # Set object centers to geometry origin
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        ### Create again an object list of selected objects since selection might have change
        objs = []
        for obj in bpy.data.objects:
            if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene):
                objs.append(obj)
    
    if qSecondScnOpt:
        ### Create new scene for faster object creation
        # Store layer settings
        layers = []
        for i in range(20): layers.append(int(scene.layers[i]))
        ### Create new scene if not already existing (see Dynamic Fracture)
        qExists = 0
        for scn in bpy.data.scenes:
            if "Scene Temp (can be deleted)" == scn.name:
                qExists = 1
                sceneCreate = scn
                break
        if not qExists:
            sceneCreate = bpy.data.scenes.new("Scene Temp (can be deleted)")
        # Link camera because in second scene is none and when coming back camera view will losing focus
        for objTemp in scene.objects:
            if objTemp.type == 'CAMERA':
                sceneCreate.objects.link(objTemp)
        # Set layers as in original scene
        for i in range(20): sceneCreate.layers[i] = layers[i]
        # Switch to new scene
        bpy.context.screen.scene = sceneCreate
                       
    ### Calculate new mass in case rigid body simulation is enabled
    if grpRBWorld != None:
        for obj in objs:
            if obj.rigid_body != None:
                obj.select = 1
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
           
    ### Main loop
    objsHistoryList = []
    objsNewList = objs
    objectCount = objectCountOld = len(objs)
    objectCountLimit += objectCount
    while objectCount < objectCountLimit:
        
        objsHistoryList.extend(objsNewList)
        objs = objsNewList
        objsNewList = []
        qNoObjectsLeft = 1
        for obj in objs:

            dim = obj.dimensions
            splitAtJunction_face = 0
            if dim.x > minimumSizeLimit or dim.y > minimumSizeLimit or dim.z > minimumSizeLimit \
            or (qSplitAtJunctions and splitAtJunction_face < len(obj.data.polygons) and (not junctionMaxFaceCnt or splitAtJunction_face <= junctionMaxFaceCnt)):
               
                if not qSilentVerbose: print(objectCount, '/', objectCountLimit, ':', obj.name)
                else: sys.stdout.write('\r' +"%d " %objectCount)
                # Debug: Save file now and then
                #if random.randint(0, 10) == 0:
                #    bpy.ops.wm.save_mainfile()
                
                if qSecondScnOpt:
                    ### Link selection to new scene
                    if qDebugVerbose: print("## MF: Link selection to new scene")
                    # Clear second scene
                    for ob in sceneCreate.objects:
                        if ob.type != 'CAMERA':
                            sceneCreate.objects.unlink(ob)
                    # Link base object and cutter to second scene
                    sceneCreate.objects.link(obj)
                            
                bpy.context.scene.objects.active = obj
                me = obj.data
                
                #####################################################
                ###### Non-manifold mesh - surface fracture algorithm
                if not qSilentVerbose: print('Starting bisect operation...')
                qNoObjectsLeft = 0

                bisectErrorCount = 0
                while (bisectErrorCount < bisectErrorRetryLimit and not qSplitAtJunctions) \
                or (qSplitAtJunctions and splitAtJunction_face < len(obj.data.polygons) and (not junctionMaxFaceCnt or splitAtJunction_face <= junctionMaxFaceCnt)):
                    
                    # Redraw Blenders viewport while script is running
                    #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                    
                    if not qUseHalving:
                        ### Move cooky cutter to random position within the obj range
                        if qDebugVerbose: print("## MF: Move cooky cutter to random position within the obj range")
                        if crackOrigin != None: objC_location = crackOrigin
                        else:                   objC_location = [obj.location.x +random.uniform(0,dim.x/2)-dim.x/4, obj.location.y +random.uniform(0,dim.y/2)-dim.y/4, obj.location.z +random.uniform(0,dim.z/2)-dim.z/4]
                        objC_rotation_euler = mathutils.Euler((random.uniform(-pi,pi), random.uniform(-pi,pi), random.uniform(-pi,pi)))
                        objC_normal = Vector((0.0, 0.0, 1.0))
                        objC_normal.rotate(objC_rotation_euler)
                    else:
                        if qSplitAtJunctions:
                            ### Move halving cutter to next face for junction cutting and align to face normal
                            face = obj.data.polygons[splitAtJunction_face]
                            splitAtJunction_face += 1
                            # Remove scale from face normal to avoid malformed vector
                            normal = face.normal *obj.matrix_world.inverted()
                            normal = normal.normalized()
                            objC_normal = normal
                            if normal.length > 0 and (not junctionTolRect or (abs(normal.angle(Vector((1,0,0)))-pi2) > pi2-junctionTolRect \
                            or abs(normal.angle(Vector((0,1,0)))-pi2) > pi2-junctionTolRect or abs(normal.angle(Vector((0,0,1)))-pi2) > pi2-junctionTolRect)):
                                ### Calculate boundary box including tolerance
                                bbMin, bbMax, bbCenter = boundaryBox(obj, 0)
                                face_center = face.center
                                tol = (1 /obj.matrix_world.to_scale().length) *junctionTolMargin  # Compensate margin by local scale
                                vecTol = tol *normal
                                vecTol = Vector((abs(vecTol[0]), abs(vecTol[1]), abs(vecTol[2])))
                                bbMin_tol = bbMin +vecTol
                                bbMax_tol = bbMax -vecTol
                                if face_center[0] > bbMin_tol[0] and face_center[0] < bbMax_tol[0] \
                                and face_center[1] > bbMin_tol[1] and face_center[1] < bbMax_tol[1] \
                                and face_center[2] > bbMin_tol[2] and face_center[2] < bbMax_tol[2]:
                                    ### Calculate rotation based on face normal
                                    z = Vector((0,0,1))
                                    angle = normal.angle(z)
                                    axis = z.cross(normal)
                                    objC_matrix_world = Matrix.Rotation(angle, 4, axis)  # Set rotation matrix
                                    ### Calculate location with offset from surface
                                    normal_world = Vector((0.0, 0.0, 1.0))
                                    eul = objC_matrix_world.to_euler()
                                    normal_world.rotate(eul)
                                    loc_world = obj.matrix_world *face_center  # Face center in world space
                                    objC_location = loc_world +(normal_world *junctionTol)  # Set halving cutter slightly above surface
                                else: continue
                            else: continue
                        else:
                            ### Move halving cutter to center of obj and align with largest dim axis
                            if qDebugVerbose: print("## MF: Move halving cutter to center of obj and align with largest dim axis")
                            objC_location = obj.location
                            dimL = Vector((abs(dim.x), abs(dim.y), abs(dim.z)))  
                            dimLsorted = [[dimL.x, 'X'], [dimL.y, 'Y'], [dimL.z, 'Z']]
                            dimLsorted.sort(reverse=True)
                            longestAxis = dimLsorted[0][1]  # Copy axis name from first item
                            if longestAxis == 'X':   objC_rotation_euler = mathutils.Euler((0, pi2, 0))
                            elif longestAxis == 'Y': objC_rotation_euler = mathutils.Euler((pi2, 0, 0))
                            else:                    objC_rotation_euler = mathutils.Euler((0, 0, 0))
                            objC_rotation_euler.rotate(obj.rotation_euler)
                            objC_normal = Vector((0.0, 0.0, 1.0))
                            objC_normal.rotate(objC_rotation_euler)
                                            
                    ### Prepare first object
                    if qDebugVerbose: print("## MF: Prepare first object")
                    obj.select = 1
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.duplicate(linked=False)
                    objA = bpy.context.scene.objects.active
                    objA.select = 0
                    objA.scale = obj.scale.copy()
                    objA.location = obj.location.copy()
                    objA.rotation_euler = obj.rotation_euler.copy()
                    # Enter edit mode
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass
                    # Select all elements
                    try: bpy.ops.mesh.select_all(action='SELECT')
                    except: pass
                    # Split
                    bpy.ops.mesh.bisect(plane_co=objC_location, plane_no=objC_normal, use_fill=qFill, clear_inner=1, clear_outer=0, threshold=0.0001)
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT') 
                    except: pass
                    # Copy ID properties
                    for key in obj.keys(): objA[key] = obj[key]
                    
                    ### Prepare second object
                    if qDebugVerbose: print("## MF: Prepare second object")
                    obj.select = 1
                    bpy.context.scene.objects.active = obj
                    bpy.ops.object.duplicate(linked=False)
                    objB = bpy.context.scene.objects.active
                    objB.select = 0
                    objB.scale = obj.scale.copy()
                    objB.location = obj.location.copy()
                    objB.rotation_euler = obj.rotation_euler.copy()
                    # Enter edit mode
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass
                    # Select all elements
                    try: bpy.ops.mesh.select_all(action='SELECT')
                    except: pass
                    # Split
                    bpy.ops.mesh.bisect(plane_co=objC_location, plane_no=objC_normal, use_fill=qFill, clear_inner=0, clear_outer=1, threshold=0.0001)
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT') 
                    except: pass
                    # Copy ID properties
                    for key in obj.keys(): objB[key] = obj[key]

                    ### Check mesh results for sanity (evaluation)
                    if qDebugVerbose: print("## MF: Check mesh results for sanity (evaluation)")
                    # Continue only when both new meshes contain data
                    if len(objA.data.vertices) == 0 or len(objB.data.vertices) == 0:
                        if not qSilentVerbose: print('Bad result on bisect operation, retrying with different location and angle...')
                        bisectErrorCount += 1
                        ### Remove duplicate objects for new retry
                        objA.select = 1
                        objB.select = 1
                        # Clear mesh datablock from database
                        bpy.data.meshes.remove(objA.data, do_unlink=1)
                        bpy.data.meshes.remove(objB.data, do_unlink=1)
                        # Remove object from all groups
                        for grpTemp in bpy.data.groups:
                            try: grpTemp.objects.unlink(objA)
                            except: pass
                            try: grpTemp.objects.unlink(objB)
                            except: pass
                        bpy.ops.object.delete(use_global=False)
                        continue
                    
                    ### After successful bisect operation
                    if qDebugVerbose: print("## MF: After successful bisect operation")

                    if qSplitAtJunctions:
                        ### Apply boundary box alignment to cutting orientation
                        objA.select = 1; objB.select = 1
                        loc = obj.location  # Backup location because setting rotation matrix will overwrite it
                        mat_rot = objC_matrix_world.to_4x4().normalized()  # Get the rotation matrix from world
                        mat_rotInv = mat_rot.inverted()
                        objA.matrix_world = mat_rotInv *obj.matrix_world  # Reverse rotation for A and B
                        objB.matrix_world = objA.matrix_world
                        objA.location = objB.location = loc
                        objA.rotation_euler = objB.rotation_euler = (0, 0, 0)
                        # Apply new rotation so that the boundary box is aligned
                        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
                        # Restore original transforms (should be the same for both A and B)
                        objA.matrix_world = objB.matrix_world = obj.matrix_world
                        objA.select = 0; objB.select = 0

                    if objsSource == None:
                        ### Apply new centers
                        objA.select = 1; objB.select = 1
                        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                        objA.select = 0; objB.select = 0

                    if qDynSecondScnOpt:
                        ### Dynamic Fracture: If using two scenes remove objects in original scene first otherwise Blender will crash due to "access violation"
                        if grpRBWorld != None:
                            ### Copy rigid body data to new object (if enabled)
                            if qDebugVerbose: print("## MF: Copy rigid body data to new object")
                            ### If using two scenes make sure both are using the same RigidBodyWorld group (important when copying RB settings, otherwise a new group is being created)
                            bpy.ops.rigidbody.world_add()
                            scene.rigidbody_world.group = grpRBWorld
                            bpy.context.scene.objects.active = obj
                            objA.select = 1; objB.select = 1
                            try: bpy.ops.rigidbody.object_settings_copy()
                            except: pass
                            objA.select = 0; objB.select = 0
                            bpy.ops.rigidbody.world_remove()
                        # Remove empty original object from original scene
                        try: sceneOriginal.objects.unlink(obj)
                        except: pass
                                            
                    if grpRBWorld != None:
                        ### Copy rigid body data to new object (if enabled)
                        if qDebugVerbose: print("## MF: Copy rigid body data to new object")
                        ### If using two scenes make sure both are using the same RigidBodyWorld group (important when copying RB settings, otherwise a new group is being created)
                        bpy.context.scene.objects.active = obj
                        objA.select = 1; objB.select = 1
                        try: bpy.ops.rigidbody.object_settings_copy()
                        except: pass
                        objA.select = 0; objB.select = 0
                    
                    ### Clear source object and unlink it from active scene
                    if qDebugVerbose: print("## MF: Clear source object and unlink it from active scene")
                    bpy.context.scene.objects.active = obj
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass 
                    # Clear old mesh
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.delete(type='VERT')
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass 
                    if grpRBWorld != None:
                        ### Remove from RigidBodyWorld (if enabled)
                        bpy.context.scene.objects.active = obj
                        try: bpy.ops.rigidbody.object_remove()
                        except: pass
                        try: grpRBWorld.objects.unlink(obj)
                        except: pass
                    # Finally unlink original object from scenes
                    if qSecondScnOpt:
                        sceneCreate.objects.unlink(obj)
                        scene.objects.unlink(obj)
                    else:
                        bpy.context.scene.objects.unlink(obj)
                    # Remove object from all groups (so it won't stick in the .blend file forever)
                    for grp in bpy.data.groups:
                        try: grp.objects.unlink(obj)
                        except: pass
                    
                    ### Add new objects to the list
                    objectCount -= 1   # Remove original object
                    objA.select = 1
                    objB.select = 1
                    if qSeparateLooseStep:
                        ### Perform separate loose on new objects
                        for objTemp in bpy.context.scene.objects:
                            if objTemp.select and objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(bpy.context.scene):
                                bpy.context.scene.objects.active = objTemp
                                # Enter edit mode              
                                try: bpy.ops.object.mode_set(mode='EDIT')
                                except: pass 
                                # Separate Loose
                                bpy.ops.mesh.separate(type='LOOSE')
                                # Leave edit mode
                                try: bpy.ops.object.mode_set(mode='OBJECT')
                                except: pass
                    ### Add new objects to the list
                    for objTemp in bpy.context.scene.objects:
                        if objTemp.select and objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(bpy.context.scene):
                            if qSecondScnOpt:
                                scene.objects.link(objTemp)  # Link object back to original scene
                            objsNewList.append(objTemp)
                            objTemp.select = 0
                            objectCount += 1
                    break                        
                
                if bisectErrorCount == bisectErrorRetryLimit:
                    if not qSilentVerbose: print('Bool error limit reached, skipping this object...')
                
                if objectCount > objectCountLimit: break

            else:
                if not qSilentVerbose: print('Shard size below minimum limit, skipping...')
        
        if qNoObjectsLeft:
            if not qSilentVerbose: print('No meshes left or shards already too small, stopping now...')
            break
    
    if qSilentVerbose: print()
    
    ### Remove new scene again
    if qSecondScnOpt:
        # Make sure we're in original scene again
        bpy.context.screen.scene = scene
        # Clear second scene
        for ob in sceneCreate.objects:
            if ob.type != 'CAMERA':
                sceneCreate.objects.unlink(ob)
        # Delete second scene
        try:    bpy.data.scenes.remove(sceneCreate, do_unlink=1)
        except: bpy.data.scenes.remove(sceneCreate)
    
    ### Calculate new masses for new objects in case rigid body simulation is enabled
    if grpRBWorld != None:
        for obj in objsNewList:
            if obj.rigid_body != None:
                obj.select = 1
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
    # Select all objects in fracture history
    for obj in objsHistoryList:
        try: obj.select = 1
        except: pass
    
    print('Done. -- Time: %0.2f s' %(time.time() -time_start))
    
    # return if new objects have been created
    # secondly return list with all objects created and deleted
    objsHistoryList.extend(objsNewList)
    if objectCount > objectCountOld: qNewShards = 1
    else: qNewShards = 0
    return qNewShards, objsHistoryList
                 
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
                   
if __name__ == "__main__":
    run(None, None, None, None)