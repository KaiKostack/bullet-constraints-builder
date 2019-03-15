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

import bpy, sys, time, os, math
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from builder import *          # Contains constraints builder function
from build_data import *       # Contains build data access functions

################################################################################

def monitor_eventHandler(scene):

    props = bpy.context.window_manager.bcb

    ### Render part
    if qRenderAnimation:
        # Need to disable handlers while rendering, otherwise Blender crashes
        bpy.app.handlers.frame_change_pre.remove(monitor_eventHandler)
        bpy.app.handlers.frame_change_pre.remove(monitor_stop_eventHandler)
        
        filepathOld = bpy.context.scene.render.filepath
        bpy.context.scene.render.filepath += "%04d" %(scene.frame_current -1)
        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.quality = 75
        
        # Stupid Blender design hack, enforcing context to be accepted by operators (at this point copy() even throws a warning but works anyway, funny Blender)
        contextFix = bpy.context.copy()
        print("Note: Please ignore above copy warning, it's a false alarm.")
        contextFix["area"] = None     
        # Render single frame with render settings
        if qRenderAnimation == 1: bpy.ops.render.render(contextFix, write_still=True)
        # Render single frame in OpenGL mode
        elif qRenderAnimation == 2: bpy.ops.render.opengl(contextFix, write_still=True)
        
        bpy.context.scene.render.filepath = filepathOld
        
        # Append handlers again
        bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
        bpy.app.handlers.frame_change_pre.append(monitor_stop_eventHandler)

    # Only evaluate monitor when official Blender and not Fracture Modifier is in use
    if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE') or not asciiExportName in scene.objects:
        
        #############################
        ### What to do on start frame
        if not "bcb_monitor" in bpy.app.driver_namespace.keys():
            print('Init BCB monitor event handler.')
            
            # Store frame time
            bpy.app.driver_namespace["bcb_time"] = time.time()
            
            ###### Function
            monitor_initBuffers(scene)

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

            ### Time scale correction with rebuild
            if props.timeScalePeriod:
                # Backup original time scale
                bpy.app.driver_namespace["bcb_monitor_originalTimeScale"] = scene.rigidbody_world.time_scale
                bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"] = scene.rigidbody_world.solver_iterations
                if scene.rigidbody_world.time_scale != props.timeScalePeriodValue:
                    ### Decrease precision for solver at extreme scale differences towards high-speed,
                    ### as high step and iteration rates on multi-constraint connections make simulation more instable
                    ratio = scene.rigidbody_world.time_scale /props.timeScalePeriodValue
                    if ratio >= 50: scene.rigidbody_world.solver_iterations /= 10
                    if ratio >= 500: scene.rigidbody_world.solver_iterations /= 10
                    if ratio >= 5000: scene.rigidbody_world.solver_iterations /= 10
                    ### Set new time scale
                    scene.rigidbody_world.time_scale = props.timeScalePeriodValue
                    ###### Execute update of all existing constraints with new time scale
                    build()

            ### Init weakening
            if props.progrWeak:
                bpy.app.driver_namespace["bcb_progrWeakCurrent"] = 1
                bpy.app.driver_namespace["bcb_progrWeakTmp"] = props.progrWeak
            if props.progrWeakStartFact != 1:
                progressiveWeakening(scene, props.progrWeakStartFact)
                                                
        ################################
        ### What to do AFTER start frame
        elif "bcb_monitor" in bpy.app.driver_namespace.keys() and scene.frame_current > scene.frame_start:   # Check this to skip the last run when jumping back to start frame
            time_last = bpy.app.driver_namespace["bcb_time"]
            sys.stdout.write("Frm: %d - T: %0.2f s" %(scene.frame_current, time.time() -time_last))
            bpy.app.driver_namespace["bcb_time"] = time.time()
            if props.progrWeak and bpy.app.driver_namespace["bcb_progrWeakTmp"]:
                progrWeakCurrent = bpy.app.driver_namespace["bcb_progrWeakCurrent"]
                sys.stdout.write(" - Wk: %0.3fx" %(progrWeakCurrent *props.progrWeakStartFact))
        
            ###### Function
            cntBroken = monitor_checkForChange(scene)
            
            # Debug: Stop on first broken connection
            #if cntBroken > 0: bpy.ops.screen.animation_play()
                
            ### Apply progressive weakening factor
            if props.progrWeak and bpy.app.driver_namespace["bcb_progrWeakTmp"] \
            and (not props.timeScalePeriod or (props.timeScalePeriod and scene.frame_current > scene.frame_start +props.timeScalePeriod)) \
            and (not props.warmUpPeriod or (props.warmUpPeriod and scene.frame_current > scene.frame_start +props.warmUpPeriod)):
                if cntBroken < props.progrWeakLimit:
                    # Weaken further only if no new connections are broken
                    if cntBroken == 0:
                        progrWeakTmp = bpy.app.driver_namespace["bcb_progrWeakTmp"]
                        ###### Weakening function
                        progressiveWeakening(scene, 1 -progrWeakTmp)
                        progrWeakCurrent -= progrWeakCurrent *progrWeakTmp
                        bpy.app.driver_namespace["bcb_progrWeakCurrent"] = progrWeakCurrent
                else:
                    print("Weakening limit exceeded, weakening disabled from now on.")
                    bpy.app.driver_namespace["bcb_progrWeakTmp"] = 0
            
            ### Check if intial time period frame is reached then switch time scale and update all constraint settings
            if props.timeScalePeriod:
                if scene.frame_current == scene.frame_start +props.timeScalePeriod:
                    # Set original time scale
                    scene.rigidbody_world.time_scale = bpy.app.driver_namespace["bcb_monitor_originalTimeScale"]
                    # Set original solver precision
                    scene.rigidbody_world.solver_iterations = bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"]
                    ###### Execute update of all existing constraints with new time scale
                    build()
                    ### Move detonator force fields to other layer to deactivate influence (Todo: Detonator not yet part of BCB)
                    if "Detonator" in bpy.data.groups:
                        for obj in bpy.data.groups["Detonator"].objects:
                            obj["Layers_BCB"] = obj.layers
                            obj.layers = [False,False,False,False,False, False,False,False,False,False, False,False,False,False,False, False,False,False,False,True]
                
################################################################################

def automaticModeAfterStop():

    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene
    if props.saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
    ###### Clear all data from scene and delete also constraint empty objects
    if "bcb_prop_elemGrps" in scene.keys(): clearAllDataFromScene(scene, qKeepBuildData=1)
    props.menu_gotData = 0
    ###### Store menu config data in scene (again)
    storeConfigDataInScene(scene)
    props.menu_gotConfig = 1
    if props.saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('_BCB-bake.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        
########################################

def monitor_stop_eventHandler(scene):

    props = bpy.context.window_manager.bcb

    # Store start time if not available
    if not "bcb_time_start" in bpy.app.driver_namespace.keys():
        bpy.app.driver_namespace["bcb_time_start"] = time.time()

    ### Check if last frame is reached
    if scene.frame_current == scene.frame_end or os.path.isfile(commandStop):
        if bpy.context.screen.is_animation_playing:
            # Stop animation playback
            bpy.ops.screen.animation_play()
            if os.path.isfile(commandStop):
                print("Baking stopped by user through external file command.")
                os.remove(commandStop)

    ### If animation playback has stopped (can also be done by user) then free all monitor data and unload the event handler 
    if not bpy.context.screen.is_animation_playing:
        try: bpy.app.handlers.frame_change_pre.remove(monitor_eventHandler)
        except: pass
        else: print("Removed event handler: monitor_eventHandler")
        try: bpy.app.handlers.frame_change_pre.remove(monitor_stop_eventHandler)
        except: pass
        else: print("Removed event handler: monitor_stop_eventHandler")
        # Convert animation point cache to fixed bake data 
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.bake_from_cache(contextFix)
        # Free all monitor related data
        monitor_freeBuffers(scene)
        # Go back to start frame
        #scene.frame_current = scene.frame_start

        time_start = bpy.app.driver_namespace["bcb_time_start"]
        del bpy.app.driver_namespace["bcb_time_start"]
        print('-- Time total: %0.2f s' %(time.time()-time_start))

        # Continue with further automatic mode steps
        if props.automaticMode:
            automaticModeAfterStop()
        else:
            print()
            print('Done.')
            print()
        bpy.context.screen.scene = scene  # Hack to update other event handlers once again to finish their clean up
            
################################################################################

def monitor_initBuffers(scene):
    
    if debug: print("Calling initBuffers")
    
    props = bpy.context.window_manager.bcb
    elemGrps = mem["elemGrps"]
    connects = bpy.app.driver_namespace["bcb_monitor"] = []
    
    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj
    
    ###### Get data from scene

    try: objsEGrp = scene["bcb_objsEGrp"]
    except: objsEGrp = []; print("Error: bcb_objsEGrp property not found, cleanup may be incomplete.")

    try: names = scene["bcb_objs"]
    except: names = []; print("Error: bcb_objs property not found, rebuilding constraints is required.")
    objs = []
    for name in names:
        if len(name):
            try: objs.append(scnObjs[name])
            except: objs.append(None); print("Error: Object %s missing, rebuilding constraints is required." %name)
        else: objs.append(None)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Error: bcb_emptyObjs property not found, rebuilding constraints is required.")
    emptyObjs = []
    for name in names:
        if len(name):
            try: emptyObjs.append(scnEmptyObjs[name])
            except: emptyObjs.append(None); print("Error: Object %s missing, rebuilding constraints is required." %name)
        else: emptyObjs.append(None)
        
    try: connectsPair = scene["bcb_connectsPair"]
    except: connectsPair = []; print("Error: bcb_connectsPair property not found, rebuilding constraints is required.")

    try: connectsConsts = scene["bcb_connectsConsts"]
    except: connectsConsts = []; print("Error: bcb_connectsConsts property not found, rebuilding constraints is required.")
    
    try: connectsTol = scene["bcb_connectsTol"]
    except: connectsTol = []; print("Error: bcb_connectsTol property not found, rebuilding constraints is required.")
    
    ### Create original transform data array
    connectsTol_iter = iter(connectsTol)
    cCnt = 1; d = 0
    qWarning = 0
    for pair in connectsPair:
        if not qWarning:
            sys.stdout.write('\r' +"%d " %cCnt)
        
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        tol = next(connectsTol_iter)

        if objA != None and objB != None:
            # Calculate distance between both elements of the connection
            dist = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
            # Calculate angle between two elements
            quat0 = objA.matrix_world.to_quaternion()
            quat1 = objB.matrix_world.to_quaternion()
            angl = quat0.rotation_difference(quat1).angle
            consts = []
            constsEnabled = []
            constsUseBrk = []
            constsBrkThres = []
            mode = 1
            if props.disableCollisionPerm: conConsts = connectsConsts[d][:-1]  # For permanent collision suppression the last constraint should be ignored
            else: conConsts = connectsConsts[d]
            for const in conConsts:
                emptyObj = emptyObjs[const]
                consts.append(emptyObj)
                if emptyObj != None:
                    if emptyObj.rigid_body_constraint != None and emptyObj.rigid_body_constraint.object1 != None:
                        # Backup original settings
                        constsEnabled.append(emptyObj.rigid_body_constraint.enabled)
                        constsUseBrk.append(emptyObj.rigid_body_constraint.use_breaking)
                        constsBrkThres.append(emptyObj.rigid_body_constraint.breaking_threshold)
                        # Disable breakability for warm up time
                        #if props.warmUpPeriod: emptyObj.rigid_body_constraint.use_breaking = 0
                        # Set initial mode state if plastic or not (activate plastic mode only if the connection constists exclusively of springs)
                        if emptyObj.rigid_body_constraint.type != 'GENERIC_SPRING': mode = 0
                    else:
                        if not qWarning:
                            qWarning = 1
                            print("\rWarning: Element has lost its constraint references or the corresponding empties their constraint properties respectively, rebuilding constraints is recommended.")
                        print("(%s)" %emptyObj.name)
                        constsEnabled.append(0)
                        constsUseBrk.append(0)
                        constsBrkThres.append(0)
                else:
                    constsEnabled.append(0)
                    constsUseBrk.append(0)
                    constsBrkThres.append(0)
            #                0                1                2     3     4       5              6             7 (unused) 8       9       10      11      12    13              14 15
            connects.append([[objA, pair[0]], [objB, pair[1]], dist, angl, consts, constsEnabled, constsUseBrk, None,      tol[0], tol[1], tol[2], tol[3], mode, constsBrkThres, 0, 0])
            cCnt += 1
        d += 1
        
    print("connections")
        
################################################################################

def monitor_checkForChange(scene):

    if debug: print("Calling checkForDistanceChange")
    
    props = bpy.context.window_manager.bcb
    connects = bpy.app.driver_namespace["bcb_monitor"]
    rbw_steps_per_second = scene.rigidbody_world.steps_per_second
    rbw_time_scale = scene.rigidbody_world.time_scale

    d = 0; e = 0; cntP = 0; cntB = 0
    for connect in connects:
        conMode = connect[12]

        ### If connection is in fixed mode then check if first tolerance is reached
        if conMode == 0:
            d += 1
            consts = connect[4]
            if consts[0].rigid_body_constraint.use_breaking:
                objA = connect[0][0]
                objB = connect[1][0]
                distOrig = connect[2]
                anglOrig = connect[3]
                tolDist = connect[8]
                tolRot = connect[9]
                distDifLast = connect[14]
                anglDifLast = connect[15]
                
                # Calculate distance between both elements of the connection
                dist = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
                if dist > 0: distDif = abs(1 -(distOrig /dist))
                else: distDif = 1

                # Calculate angle between two elements
                quatA = objA.matrix_world.to_quaternion()
                quatB = objB.matrix_world.to_quaternion()
                anglDif = math.asin(math.sin( abs(anglOrig -quatA.rotation_difference(quatB).angle) /2))   # The construct "asin(sin(x))" is a triangle function to achieve a seamless rotation loop from input

                # If change in relative distance is larger than tolerance plus change in angle (angle is involved here to allow for bending and buckling)
                if (tolDist != -1 and distDif > tolDist +(anglDif /pi)) \
                or (tolRot != -1 and anglDif > tolRot):
                    qPlastic = 0
                    for const in consts:
                        # Enable spring constraints for this connection by setting its stiffness
                        if const.rigid_body_constraint.type == 'GENERIC_SPRING':
                            const.rigid_body_constraint.enabled = 1
                            qPlastic = 1
                        # Disable non-spring constraints for this connection
                        else: const.rigid_body_constraint.enabled = 0
                    if qPlastic:
                        # Update distance in comparison list so we use the last elastic deformation
                        connect[2] = dist
                        # Flag connection as being in plastic mode
                        connect[12] += 1
                        cntP += 1
                    else:
                        # Flag connection as being disconnected
                        connect[12] += 2
                        cntB += 1

#                # When no breaking or mode change happens but connection is breakable
#                else:

#                    ### Modify limits from applied forces
#                    strainDist = .001 # Maximum linear strain for the given breaking threshold
#                    strainAngl = .002 # Maximum angular strain for the given breaking threshold
#                    for const in consts:
#                        con = const.rigid_body_constraint
#                        force = con.appliedImpulse() *rbw_steps_per_second /rbw_time_scale  # Conversion from impulses to forces
#                        brkThres = con.breaking_threshold *rbw_steps_per_second /rbw_time_scale
#                        strainLin = strainDist *(abs(force) /brkThres)  # Normalized to breaking threshold
#                        strainAng = strainAngl *(abs(force) /brkThres)
#                        # Limits Linear
#                        if con.use_limit_lin_x:
#                            if con.limit_lin_x_lower > -1: con.limit_lin_x_lower -= strainLin
#                            if con.limit_lin_x_upper < 1: con.limit_lin_x_upper += strainLin
#                        if con.use_limit_lin_y:
#                            if con.limit_lin_y_lower > -1: con.limit_lin_y_lower -= strainLin
#                            if con.limit_lin_y_upper < 1: con.limit_lin_y_upper += strainLin
#                        if con.use_limit_lin_z:
#                            if con.limit_lin_z_lower > -1: con.limit_lin_z_lower -= strainLin
#                            if con.limit_lin_z_upper < 1: con.limit_lin_z_upper += strainLin
#                        # Limits Angular
#                        if con.use_limit_ang_x:
#                            if con.limit_ang_x_lower > -1: con.limit_ang_x_lower -= strainAng
#                            if con.limit_ang_x_upper < 1: con.limit_ang_x_upper += strainAng
#                        if con.use_limit_ang_y:
#                            if con.limit_ang_y_lower > -1: con.limit_ang_y_lower -= strainAng
#                            if con.limit_ang_y_upper < 1: con.limit_ang_y_upper += strainAng
#                        if con.use_limit_ang_z:
#                            if con.limit_ang_z_lower > -1: con.limit_ang_z_lower -= strainAng
#                            if con.limit_ang_z_upper < 1: con.limit_ang_z_upper += strainAng

#                    ### Calculate fatigue from the change in distance between last frame and current one
#                    fatigueDist = 0.002  # [%/mm]
#                    if fatigueDist:
#                        facDist = max(0, 1 -(abs(distDif -distDifLast) *1000) *fatigueDist)
#                        connect[14] = distDif
#                    fatigueAngl = 0.2  # [%/rad]
#                    if fatigueAngl:
#                        facAngl = max(0, 1 -abs(anglDif -anglDifLast) *fatigueAngl)
#                        connect[15] = anglDif
#                    fac = facDist *facAngl
#                    if fac < 1:
#                        for const in consts:
#                            const.rigid_body_constraint.breaking_threshold *= fac

#            ### Adaptive change of constraint solver iterations depending on acting force
#            iterMin = 100     # Minimum iterations when acting force is 0
#            iterMax = 100000  # Maximum iterations when acting force is equal to the breaking threshold
#            # Find the maximum strain of the compressive constraints in connection
#            strainMax = 0
#            for const in consts:
#                con = const.rigid_body_constraint
#                if con.use_limit_lin_x:  # Compressive constraints - Comment this line out to include all constraints 
#                    force = con.appliedImpulse() *rbw_steps_per_second /rbw_time_scale  # Conversion from impulses to forces
#                    brkThres = con.breaking_threshold *rbw_steps_per_second /rbw_time_scale
#                    strain = abs(force) /brkThres  # Normalized to breaking threshold
#                    if strain > strainMax: strainMax = strain
#            strainIters = iterMin +(iterMax -iterMin) *strainMax  # Compute iterations from strain
#            # Set override only to shear connections in connection
#            for const in consts:
#                con = const.rigid_body_constraint
#                if con.use_limit_lin_y or con.use_limit_lin_z:  # Shear constraints - Comment this line out to include all constraints
#                    if not con.use_override_solver_iterations: con.use_override_solver_iterations = 1
#                    con.solver_iterations = strainIters

        ### If connection is in plastic mode then check if second tolerance is reached
        if conMode == 1:
            e += 1
            consts = connect[4]
            if len(consts) and consts[0].rigid_body_constraint.use_breaking:
                objA = connect[0][0]
                objB = connect[1][0]
                distOrig = connect[2]
                anglOrig = connect[3]
                tolDist = connect[10]
                tolRot = connect[11]
                
                # Calculate distance between both elements of the connection
                dist = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
                if dist > 0: distDif = abs(1 -(distOrig /dist))
                else: distDif = 1

                # Calculate angle between two elements
                quatA = objA.matrix_world.to_quaternion()
                quatB = objB.matrix_world.to_quaternion()
                anglDif = math.asin(math.sin( abs(anglOrig -quatA.rotation_difference(quatB).angle) /2))   # The construct "asin(sin(x))" is a triangle function to achieve a seamless rotation loop from input

                # If change in relative distance is larger than tolerance plus change in angle (angle is involved here to allow for bending and buckling)
                if (tolDist != -1 and distDif > tolDist +(anglDif /pi)) \
                or (tolRot != -1 and anglDif > tolRot):
                    # Disable plastic constraints for this connection
                    for const in consts:
                        if const.rigid_body_constraint.type == 'GENERIC_SPRING':
                            const.rigid_body_constraint.enabled = 0
                    # Flag connection as being disconnected
                    connect[12] += 1
                    cntB += 1

        ### Enable original breakability for all constraints when warm up time is over
#        if props.warmUpPeriod:
#            if scene.frame_current == scene.frame_start +props.warmUpPeriod:
#                consts = connect[4]
#                constsUseBrk = connect[6]
#                for i in range(len(consts)):
#                    const = consts[i]
#                    const.rigid_body_constraint.use_breaking = constsUseBrk[i]
           
    sys.stdout.write(" - Con: %di & %dp" %(d, e))
    if cntP > 0: sys.stdout.write(" | Plst: %d" %cntP)
    if cntB > 0: sys.stdout.write(" | Brk: %d" %cntB)
    print()

    return cntB
                
################################################################################

def progressiveWeakening(scene, progrWeakVar):

    if debug: print("Calling progressiveWeakening")

    connects = bpy.app.driver_namespace["bcb_monitor"]
    i = 0
    for connect in connects:
        sys.stdout.write("\r%d" %i)
        consts = connect[4]
        for const in consts:
            const.rigid_body_constraint.breaking_threshold *= progrWeakVar
        i += 1
    sys.stdout.write("\r")
            
################################################################################

def monitor_freeBuffers(scene):
    
    if debug: print("Calling freeBuffers")
    
    if "bcb_monitor" in bpy.app.driver_namespace.keys():
        props = bpy.context.window_manager.bcb
        connects = bpy.app.driver_namespace["bcb_monitor"]

        ### Restore original constraint and element data
        qWarning = 0
        for connect in connects:
            consts = connect[4]
            constsEnabled = connect[5]
            constsUseBrk = connect[6]
            constsBrkThres = connect[13]
            for i in range(len(consts)):
                const = consts[i]
                if const.rigid_body_constraint != None and const.rigid_body_constraint.object1 != None:
                    # Restore original settings
                    const.rigid_body_constraint.enabled = constsEnabled[i]
                    const.rigid_body_constraint.use_breaking = constsUseBrk[i]
                    const.rigid_body_constraint.breaking_threshold = constsBrkThres[i]
                else:
                    if not qWarning:
                        qWarning = 1
                        print("\rWarning: Element has lost its constraint references or the corresponding empties their constraint properties respectively, rebuilding constraints is recommended.")
                    print("(%s)" %const.name)
                
        if props.timeScalePeriod:
            # Set original time scale
            scene.rigidbody_world.time_scale = bpy.app.driver_namespace["bcb_monitor_originalTimeScale"]
            # Set original solver precision
            scene.rigidbody_world.solver_iterations = bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"]
                
        ### Move detonator force fields back to original layer(s) (Todo: Detonator not yet part of BCB)
        if "Detonator" in bpy.data.groups:
            for obj in bpy.data.groups["Detonator"].objects:
                if "Layers_BCB" in obj.keys():
                    layers = obj["Layers_BCB"]
                    obj.layers = [bool(i) for i in layers]  # Properties are automatically converted from original bool to int but .layers only accepts bool *shaking head*
                    del obj["Layers_BCB"]

        # Clear monitor properties
        del bpy.app.driver_namespace["bcb_monitor"]
        if props.timeScalePeriod:
            del bpy.app.driver_namespace["bcb_monitor_originalTimeScale"]
            del bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"]
