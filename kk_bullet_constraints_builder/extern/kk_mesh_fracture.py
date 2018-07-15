######################################
# Mesh Fracture v1.72 by Kai Kostack #
######################################

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
 
import bpy, sys, random, time
from mathutils import *

################################################################################   

def run(objsSource, crackOrigin, qDynSecondScnOpt):
    """"""
    ### Vars
    cookyCutterPlane = 'Plane'      #      | The "knife" object, can be arbitrary geometry like a subdivided plane with displacement
    objectCountLimit = 5            # 10   | Shard count to be generated per selected object (might be less because of other limits)
    boolErrorRetryLimit = 10        # 30   | How often to retry if boolean operation fails
    qTriangulate = 0                # 0    | Perform triangulation on all objects before doing boolean operations
    minimumSizeLimit = 0.5          # 0.3  | Minimum dimension for a shard to be still considered for fracturing, at least two dimension axis must be above this size

    qUseHoleCutter = 0              # 1    | Enables punching holes into larger objects instead of fracturing them as a whole
    cookyCutterHole = 'Sphere'      #      | The "knife" object for holes, to be used only if the fracture object is larger than the cutter plane.
                                    #      | Should be a closed volume like a sphere and smaller than the cutter plane.

    materialPreset = 'Concrete'     # See Blender rigid body tools for a list of available presets
    materialDensity = 0             # Custom density value (kg/m^3) to use instead of material preset (0 = disabled)

    qSeparateLoose = 1              # 1    | Perform Separate Loose on all shards at start
    qSeparateLooseStep = 1          # 1    | Perform Separate Loose on shards after each fracture step

    ### Vars for halving
    qUseHalving = 0                 # 0    | Enables special mode for subdividing meshes into halves until either minimumSizeLimit or objectCountLimit is reached (sets boolErrorRetryLimit = 0)
                                    #      | It's recommended to set the latter to a very high count to get a universal shard size. This is incompatible with Dynamic Fracture because object centers are changed.
    qSplitAtJunctions = 0           # 1    | Try to split cornered walls at the corner rather than splitting based on object space to generate more clean shapes
    junctionTol = .001              # .001 | Tolerance for junction detection to avoid cutting off of very thin geometry slices (requires normals consistently pointing outside)
    junctionTolMargin = .01         # .01  | Margin inside the object boundary box borders to skip junction detection (helps to avoid cutting of similar faces which can lead to hundreds of thin mesh slices, should be larger than junctionTol) 
    junctionTolRect = .001          # .001 | Tolerance to enforce rectangular shapes in radian, larger values will allow more diagonal cuts (0 = no restriction)
    junctionMaxFaceCnt = 0          # 0    | Sets a limit to skip search for junctions after this many faces have been checked (helps to skip very dense meshes more quickly, 0 = disabled)
    halvingCutter = 'Plane'         #      | The "knife" object for halving, a larger flat plane is recommended but can be an arbitrary geometry as well

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
        halvingCutter = cookyCutterPlane = parameters[3]  # Object name
        objectCountLimit = 100000000
        qSeparateLoose = 0
        qSeparateLooseStep = 1
        qSilentVerbose = 1
        objsSource = None
        crackOrigin = None
    
    ### Corrections
    if objsSource != None: qSecondScnOpt = 0
    if qUseHalving: boolErrorRetryLimit = 1
    
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
        
    objCP = bpy.data.objects[cookyCutterPlane]
    if qUseHoleCutter: objCH = bpy.data.objects[cookyCutterHole]
    if qUseHalving: objCS = bpy.data.objects[halvingCutter]
    locCold = objCP.location.copy()
    rotCold = objCP.rotation_euler.copy()
    
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
            # Remember scene where cookyCutterPlane is linked to
            for scn in bpy.data.scenes:
                for obj in scn.objects:
                    if cookyCutterPlane == obj.name:
                        sceneOriginal = scn
                        break
            # Link cookyCutterPlane to current scene
            try: bpy.context.screen.scene.objects.link(bpy.data.objects[cookyCutterPlane])
            except: pass
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
                
                if not qUseHalving:
                    ### Only use plane cutter if its diameter is larger than object otherwise use hole cutter 
                    if objCP.dimensions > obj.dimensions or not qUseHoleCutter:
                          objC = objCP
                    else: objC = objCH
                else:
                    objC = objCS
                        
                if qSecondScnOpt:
                    ### Link selection to new scene
                    if qDebugVerbose: print("## MF: Link selection to new scene")
                    # Clear second scene
                    for ob in sceneCreate.objects:
                        if ob.type != 'CAMERA':
                            sceneCreate.objects.unlink(ob)
                    # Link base object and cutter to second scene
                    sceneCreate.objects.link(obj)
                    try: sceneCreate.objects.link(objC)
                    except: pass
                            
                bpy.context.scene.objects.active = obj
                me = obj.data
                
                ### Check if mesh is water tight (non-manifold), if not, issue a warning and skip fracturing
                # Enter edit mode              
                try: bpy.ops.object.mode_set(mode='EDIT')
                except: pass 
                if qTriangulate:
                    # Select all elements
                    try: bpy.ops.mesh.select_all(action='SELECT')
                    except: pass 
                    # Triangulate selection
                    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
                # Deselect all elements
                try: bpy.ops.mesh.select_all(action='DESELECT')
                except: pass 
                # Select non-manifold elements
                bpy.ops.mesh.select_non_manifold()
                # Leave edit mode
                try: bpy.ops.object.mode_set(mode='OBJECT')
                except: pass 
                # check mesh if there are selected elements found
                qNonManifolds = 0
                for edge in me.edges:
                    if edge.select: qNonManifolds = 1; break
                
                #####################################################
                ###### Non-manifold mesh - surface fracture algorithm
                if qNonManifolds:
                    if not qSilentVerbose: print('Mesh not water tight, non-manifolds found. Starting surface boolean...')
                    qNoObjectsLeft = 0
                    
                    boolErrorCount = 0
                    while (boolErrorCount < boolErrorRetryLimit and not qSplitAtJunctions) \
                    or (qSplitAtJunctions and splitAtJunction_face < len(obj.data.polygons) and (not junctionMaxFaceCnt or splitAtJunction_face <= junctionMaxFaceCnt)):
                        
                        # Redraw Blenders viewport while script is running
                        #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        
                        if not qUseHalving:
                            ### Move cooky cutter to random position within the obj range
                            if qDebugVerbose: print("## MF: Move cooky cutter to random position within the obj range")
                            if crackOrigin != None: objC.location = crackOrigin
                            else:                   objC.location = [obj.location.x +random.uniform(0,dim.x/2)-dim.x/4, obj.location.y +random.uniform(0,dim.y/2)-dim.y/4, obj.location.z +random.uniform(0,dim.z/2)-dim.z/4]
                            objC.rotation_euler = [random.uniform(-pi,pi), random.uniform(-pi,pi), random.uniform(-pi,pi)]
                        else:
                            if qSplitAtJunctions:
                                ### Move halving cutter to next face for junction cutting and align to face normal
                                face = obj.data.polygons[splitAtJunction_face]
                                splitAtJunction_face += 1
                                # Remove scale from face normal to avoid malformed vector
                                normal = face.normal *obj.matrix_world.inverted()
                                normal = normal.normalized()
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
                                        scale = objC.scale.copy()  # Need to backup scale because applying rotation matrix on our object will reset the scale
                                        ### Calculate rotation based on face normal
                                        z = Vector((0,0,1))
                                        angle = normal.angle(z)
                                        axis = z.cross(normal)
                                        objC.matrix_world = Matrix.Rotation(angle, 4, axis)  # Set rotation matrix
                                        ### Calculate location with offset from surface
                                        normal_world = Vector((0.0, 0.0, 1.0))
                                        eul = objC.matrix_world.to_euler()
                                        normal_world.rotate(eul)
                                        loc_world = obj.matrix_world *face_center  # Face center in world space
                                        objC.location = loc_world +(normal_world *junctionTol)  # Set halving cutter slightly above surface
                                        objC.scale = scale
                                    else: continue
                                else: continue
                            else:
                                ### Move halving cutter to center of obj and align with largest dim axis
                                if qDebugVerbose: print("## MF: Move halving cutter to center of obj and align with largest dim axis")
                                objC.location = obj.location
                                dimL = Vector((abs(dim.x), abs(dim.y), abs(dim.z)))  
                                dimLsorted = [[dimL.x, 'X'], [dimL.y, 'Y'], [dimL.z, 'Z']]
                                dimLsorted.sort(reverse=True)
                                longestAxis = dimLsorted[0][1]  # Copy axis name from first item
                                if longestAxis == 'X':   objC.rotation_euler = [0, pi2, 0]
                                elif longestAxis == 'Y': objC.rotation_euler = [pi2, 0, 0]
                                else:                    objC.rotation_euler = [0, 0, 0]
                                objC.rotation_euler.rotate(obj.rotation_euler)
                        
                        ### Prepare cutter plane copy (required to invert normals for second object after that)
                        if qDebugVerbose: print("## MF: Prepare cutter plane copy")
                        meC = objC.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                        objCdup = bpy.data.objects.new(objC.name, meC)
                        bpy.context.scene.objects.link(objCdup)
                        objCdup.scale = objC.scale
                        objCdup.location = objC.location
                        objCdup.rotation_euler = objC.rotation_euler

                        if qTriangulate:
                            objCdup.modifiers.new(name="Triangulate", type='TRIANGULATE')

                        bpy.context.scene.update()
                        
                        ### Prepare first object
                        if qDebugVerbose: print("## MF: Prepare first object")
                        obj.modifiers.new(name="Boolean", type='BOOLEAN')
                        mod = obj.modifiers["Boolean"]
                        mod.operation = 'UNION'
                        if version_carve:
                            try: mod.solver = 'CARVE'
                            except: pass
                        mod.object = objCdup
                        meA = obj.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                        # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
                        qBadResult = meA.validate(verbose=False, clean_customdata=False)
                        # Calculate object's surfaces
                        me = obj.data
                        surf = 0
                        for poly in me.polygons: surf += poly.area
                        surfA = 0
                        for poly in meA.polygons: surfA += poly.area
                        if qBadResult or (surfA > surf -.001 and surfA < surf +.001):
                            if not qSilentVerbose: print('Error on boolean operation, mesh problems detected. Retrying...')
                            boolErrorCount += 1
                            # Remove other object already linked to scene for new retry
                            bpy.context.scene.objects.unlink(objCdup)
                            # Clear modifier from original object after that
                            obj.modifiers.clear()
                            continue
                        objA = bpy.data.objects.new(obj.name, meA)
                        bpy.context.scene.objects.link(objA)
                        objA.scale = obj.scale.copy()
                        objA.location = obj.location.copy()
                        objA.rotation_euler = obj.rotation_euler.copy()
                        
                        ### Prepare second object
                        if qDebugVerbose: print("## MF: Prepare second object")
                        ### Inverted normals of the cutter plane
                        bpy.context.scene.objects.active = objCdup
                        # Enter edit mode              
                        try: bpy.ops.object.mode_set(mode='EDIT')
                        except: pass 
                        # Deselect all elements
                        try: bpy.ops.mesh.select_all(action='SELECT')
                        except: pass 
                        # invert normals
                        bpy.ops.mesh.flip_normals()
                        # Leave edit mode
                        try: bpy.ops.object.mode_set(mode='OBJECT')
                        except: pass
                        ### Finalize second object
                        meB = obj.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                        # Clear modifier from original object after that
                        obj.modifiers.clear()
                        # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
                        qBadResult = meB.validate(verbose=False, clean_customdata=False)
                        # Calculate object's surfaces
                        me = obj.data
                        surf = 0
                        for poly in me.polygons: surf += poly.area
                        surfB = 0
                        for poly in meB.polygons: surfB += poly.area
                        if qBadResult or (surfB > surf -.001 and surfB < surf +.001):
                            if not qSilentVerbose: print('Error on boolean operation, mesh problems detected. Retrying...')
                            boolErrorCount += 1
                            # Remove other object already linked to scene for new retry
                            bpy.context.scene.objects.unlink(objA)
                            bpy.context.scene.objects.unlink(objCdup)
                            continue
                        objB = bpy.data.objects.new(obj.name, meB)
                        bpy.context.scene.objects.link(objB)
                        objB.scale = obj.scale.copy()
                        objB.location = obj.location.copy()
                        objB.rotation_euler = obj.rotation_euler.copy()

                        ### Check mesh results for sanity (evaluation)
                        if qDebugVerbose: print("## MF: Check mesh results for sanity (evaluation)")
                        # 1 Continue only when both new meshes contain data
                        # 2 Continue only if both meshes have in sum almost the same surface area as the original object,
                        #   just then we can expect a successful boolean attempt
                        if len(meA.vertices) == 0 or len(meB.vertices) == 0 \
                        or abs(surf -(surfA +surfB)) > .01:
                            if not qSilentVerbose: print('Bad result on boolean operation, retrying with different location and angle...')
                            boolErrorCount += 1
                            # Remove duplicate objects for new retry
                            bpy.context.scene.objects.unlink(objA)
                            bpy.context.scene.objects.unlink(objB)
                            bpy.context.scene.objects.unlink(objCdup)
                            continue
                        
                        ### After successful boolean operation
                        if qDebugVerbose: print("## MF: After successful boolean operation")

                        if qSplitAtJunctions:
                            ### Apply boundary box alignment to cutting orientation
                            objA.select = 1; objB.select = 1
                            loc = obj.location  # Backup location because setting rotation matrix will overwrite it
                            mat_rot = objC.matrix_world.to_4x4().normalized()  # Get the rotation matrix from world
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

                        ### Link new objects to every group the original is linked to
                        for grp in bpy.data.groups:
                            for objG in grp.objects:
                                if objG.name == obj.name:
                                    grp.objects.link(objA)
                                    grp.objects.link(objB)
                        
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
                            
                        ### Cutter object can be removed
                        bpy.context.scene.objects.active = objCdup
                        try: bpy.ops.object.mode_set(mode='EDIT')
                        except: pass 
                        # Clear old mesh
                        bpy.ops.mesh.select_all(action='SELECT')
                        bpy.ops.mesh.delete(type='VERT')
                        try: bpy.ops.object.mode_set(mode='OBJECT')
                        except: pass 
                        # Finally unlink object from scene
                        bpy.context.scene.objects.unlink(objCdup)
                        
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
                    
                    if boolErrorCount == boolErrorRetryLimit:
                        if not qSilentVerbose: print('Bool error limit reached, skipping this object...')
                    
                    if objectCount > objectCountLimit: break
           
                #####################################################
                ###### Manifold mesh - solid fracture algorithm
                else:
                    if not qSilentVerbose: print('Mesh water tight and manifold. Starting solid boolean...')
                    qNoObjectsLeft = 0
                    
                    boolErrorCount = 0
                    while (boolErrorCount < boolErrorRetryLimit and not qSplitAtJunctions) \
                    or (qSplitAtJunctions and splitAtJunction_face < len(obj.data.polygons) and (not junctionMaxFaceCnt or splitAtJunction_face <= junctionMaxFaceCnt)):
                        
                        # Redraw Blenders viewport while script is running
                        #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
                        
                        if not qUseHalving:
                            ### Move cooky cutter to random position within the obj range or to predefined location
                            if qDebugVerbose: print("## MF: Move cooky cutter to random position within the obj range")
                            if crackOrigin != None: objC.location = crackOrigin
                            else:                   objC.location = [obj.location.x +random.uniform(0,dim.x/2)-dim.x/4, obj.location.y +random.uniform(0,dim.y/2)-dim.y/4, obj.location.z +random.uniform(0,dim.z/2)-dim.z/4]
                            objC.rotation_euler = [random.uniform(-pi,pi), random.uniform(-pi,pi), random.uniform(-pi,pi)]
                        else:
                            if qSplitAtJunctions:
                                ### Move halving cutter to next face for junction cutting and align to face normal
                                face = obj.data.polygons[splitAtJunction_face]
                                splitAtJunction_face += 1
                                # Remove scale from face normal to avoid malformed vector
                                normal = face.normal *obj.matrix_world.inverted()
                                normal = normal.normalized()
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
                                        scale = objC.scale.copy()  # Need to backup scale because applying rotation matrix on our object will reset the scale
                                        ### Calculate rotation based on face normal
                                        z = Vector((0,0,1))
                                        angle = normal.angle(z)
                                        axis = z.cross(normal)
                                        objC.matrix_world = Matrix.Rotation(angle, 4, axis)  # Set rotation matrix
                                        ### Calculate location with offset from surface
                                        normal_world = Vector((0.0, 0.0, 1.0))
                                        eul = objC.matrix_world.to_euler()
                                        normal_world.rotate(eul)
                                        loc_world = obj.matrix_world *face_center  # Face center in world space
                                        objC.location = loc_world +(normal_world *junctionTol)  # Set halving cutter slightly above surface
                                        objC.scale = scale
                                    else: continue
                                else: continue
                            else:
                                ### Move halving cutter to center of obj and align with largest dim axis
                                if qDebugVerbose: print("## MF: Move halving cutter to center of obj and align with largest dim axis")
                                objC.location = obj.location
                                dimL = Vector((abs(dim.x), abs(dim.y), abs(dim.z)))  
                                dimLsorted = [[dimL.x, 'X'], [dimL.y, 'Y'], [dimL.z, 'Z']]
                                dimLsorted.sort(reverse=True)
                                longestAxis = dimLsorted[0][1]  # Copy axis name from first item
                                if longestAxis == 'X':   objC.rotation_euler = [0, pi2, 0]
                                elif longestAxis == 'Y': objC.rotation_euler = [pi2, 0, 0]
                                else:                    objC.rotation_euler = [0, 0, 0]
                                objC.rotation_euler.rotate(obj.rotation_euler)
                            
                        if qTriangulate:
                            objC.modifiers.new(name="Triangulate", type='TRIANGULATE')

                        bpy.context.scene.update()
                        
                        ### Prepare first object
                        if qDebugVerbose: print("## MF: Prepare first object")
                        obj.modifiers.new(name="Boolean", type='BOOLEAN')
                        mod = obj.modifiers["Boolean"]
                        mod.operation = 'INTERSECT'
                        if version_carve:
                            try: mod.solver = 'CARVE'
                            except: pass
                        mod.object = objC
                        meA = obj.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                        # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
                        qBadResult = meA.validate(verbose=False, clean_customdata=False)
                        # Calculate object's surfaces
                        me = obj.data
                        surf = 0
                        for poly in me.polygons: surf += poly.area
                        surfA = 0
                        for poly in meA.polygons: surfA += poly.area
                        if qBadResult or (surfA > surf -.001 and surfA < surf +.001):
                            if not qSilentVerbose: print('Error on boolean operation, mesh problems detected. Retrying...')
                            boolErrorCount += 1
                            # Clear modifier from original object
                            obj.modifiers.clear()
                            if qTriangulate:
                                # Remove triangulation modifier
                                objC.modifiers.remove(objC.modifiers["Triangulate"])
                            continue
                        objA = bpy.data.objects.new(obj.name, meA)
                        bpy.context.scene.objects.link(objA)
                        objA.scale = obj.scale.copy()
                        objA.location = obj.location.copy()
                        objA.rotation_euler = obj.rotation_euler.copy()
                        
                        ### Prepare second object
                        if qDebugVerbose: print("## MF: Prepare second object")
                        mod.operation = 'DIFFERENCE'
                        meB = obj.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                        # Clear modifier from original object
                        obj.modifiers.clear()
                        if qTriangulate:
                            # Remove triangulation modifier
                            objC.modifiers.remove(objC.modifiers["Triangulate"])
                        # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
                        qBadResult = meB.validate(verbose=False, clean_customdata=False)
                        # Calculate object's surfaces
                        me = obj.data
                        surf = 0
                        for poly in me.polygons: surf += poly.area
                        surfB = 0
                        for poly in meB.polygons: surfB += poly.area
                        if qBadResult or (surfB > surf -.001 and surfB < surf +.001):
                            if not qSilentVerbose: print('Error on boolean operation, mesh problems detected. Retrying...')
                            boolErrorCount += 1
                            # Remove other object already linked to scene for new retry
                            bpy.context.scene.objects.unlink(objA)
                            continue
                        objB = bpy.data.objects.new(obj.name, meB)
                        bpy.context.scene.objects.link(objB)
                        objB.scale = obj.scale.copy()
                        objB.location = obj.location.copy()
                        objB.rotation_euler = obj.rotation_euler.copy()
                                                                
                        ### Check mesh results for sanity (preparation)
                        if qDebugVerbose: print("## MF: Check mesh results for sanity (preparation)")
                        ### Check for non-manifolds on both new meshes
                        bpy.context.scene.objects.active = objA
                        try: bpy.ops.object.mode_set(mode='EDIT')
                        except: pass
                        if not version_carve:
                            try: bpy.ops.mesh.select_all(action='SELECT')
                            except: pass
                            # Recalculate normals outside
                            bpy.ops.mesh.normals_make_consistent(inside=False)
                        try: bpy.ops.mesh.select_all(action='DESELECT')
                        except: pass
                        # Select non-manifolds
                        bpy.ops.mesh.select_non_manifold()
                        bpy.ops.mesh.delete(type='EDGE')    # Wild try to fix loose triangles
                        bpy.ops.mesh.select_non_manifold()
                        try: bpy.ops.object.mode_set(mode='OBJECT')
                        except: pass 
                        meA = objA.data
                        qNonManifoldsA = 0
                        for edge in meA.edges:
                            if edge.select: qNonManifoldsA = 1; break
                        ### Second one starts here
                        bpy.context.scene.objects.active = objB
                        try: bpy.ops.object.mode_set(mode='EDIT')
                        except: pass 
                        if not version_carve:
                            try: bpy.ops.mesh.select_all(action='SELECT')
                            except: pass
                            # Recalculate normals outside
                            bpy.ops.mesh.normals_make_consistent(inside=False)
                        try: bpy.ops.mesh.select_all(action='DESELECT')
                        except: pass
                        # Select non-manifolds
                        bpy.ops.mesh.select_non_manifold()
                        bpy.ops.mesh.delete(type='EDGE')    # Wild try to fix loose triangles
                        bpy.ops.mesh.select_non_manifold()
                        try: bpy.ops.object.mode_set(mode='OBJECT')
                        except: pass 
                        meB = objB.data
                        qNonManifoldsB = 0
                        for edge in meB.edges:
                            if edge.select: qNonManifoldsB = 1; break
                        # Calculate dimension difference for sanity check
                        dimA = objA.dimensions -obj.dimensions
                        dimB = objB.dimensions -obj.dimensions
                        
                        ### Check mesh results for sanity (evaluation)
                        if qDebugVerbose: print("## MF: Check mesh results for sanity (evaluation)")
                        # 1 Continue only when both new meshes contain data
                        # 2 Continue only when meshes are manifold
                        # 3 Continue only if dimensions of the new objects are smaller,
                        #   just then we can expect a successful boolean attempt
                        if len(meA.vertices) == 0 or len(meB.vertices) == 0 \
                        or qNonManifoldsA or qNonManifoldsB \
                        or (((dimA.x >= 0 and dimA.y >= 0 and dimA.z >= 0) \
                        and (dimB.x >= 0 and dimB.y >= 0 and dimB.z >= 0)) and objC == objCP):  
                            if not qSilentVerbose: print('Error on boolean operation, retrying with different location and angle...')
                            boolErrorCount += 1
                            # Remove both objects for new retry
                            bpy.context.scene.objects.unlink(objA)
                            bpy.context.scene.objects.unlink(objB)
                            continue
                        
                        ### After successful boolean operation
                        if qDebugVerbose: print("## MF: After successful boolean operation")

                        if qSplitAtJunctions:
                            ### Apply boundary box alignment to cutting orientation
                            objA.select = 1; objB.select = 1
                            loc = obj.location  # Backup location because setting rotation matrix will overwrite it
                            mat_rot = objC.matrix_world.to_4x4().normalized()  # Get the rotation matrix from world
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

                        ### Link new objects to every group the original is linked to
                        for grp in bpy.data.groups:
                            for objG in grp.objects:
                                if objG.name == obj.name:
                                    grp.objects.link(objA)
                                    grp.objects.link(objB)
                        
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
                  
                    if boolErrorCount == boolErrorRetryLimit:
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
            
    objCP.location = locCold
    objCP.rotation_euler = rotCold
    if qUseHoleCutter:
        objCH.location = locCold
        objCH.rotation_euler = rotCold
    if qUseHalving:
        objCS.location = locCold
        objCS.rotation_euler = rotCold
    
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
    # Deselect all objects
    #bpy.ops.object.select_all(action='DESELECT')
                                                            
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
    """"""
    run(None, None, None)