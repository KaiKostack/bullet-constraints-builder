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

import bpy, mathutils, math, sys, copy, random
from mathutils import Vector
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *          # Contains file input & output functions
from tools import *            # Contains smaller independently working tools
                            
################################################################################

def setConstParams(cData,cDatb,cDef, name=None,loc=None,obj1=None,obj2=None,tol1=None,tol2=None,rotm=None,rot=None,
    e=None,bt=None,ub=None,dc=None,ct=None,so=None,si=None,
    ullx=None,ully=None,ullz=None,llxl=None,llxu=None,llyl=None,llyu=None,llzl=None,llzu=None,
    ulax=None,ulay=None,ulaz=None,laxl=None,laxu=None,layl=None,layu=None,lazl=None,lazu=None,
    uslx=None,usly=None,uslz=None,sdlx=None,sdly=None,sdlz=None,sslx=None,ssly=None,sslz=None,
    usax=None,usay=None,usaz=None,sdax=None,sday=None,sdaz=None,ssax=None,ssay=None,ssaz=None):

    # setConstParams(cData,cDatb,cDef, name,loc,obj1,obj2,tol1,tol2,rotm,rot, e,bt,ub,dc,ct,so,si, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, uslx,usly,uslz, sdlx,sdly,sdlz, sslx,ssly,sslz, usax,usay,usaz, sdax,sday,sdaz, ssax,ssay,ssaz)

    ### Base parameters (BCB specific)
    if len(cDatb) == 0:  # Initialize when empty
        for i in range(8): cDatb.append(None)
    if name != None: cDatb[0] = name
    if loc  != None: cDatb[1] = loc
    if obj1 != None: cDatb[2] = obj1
    if obj2 != None: cDatb[3] = obj2
    if tol1 != None: cDatb[4] = tol1  # Should always get data
    if tol2 != None: cDatb[5] = tol2  # Should always get data
    if rotm != None: cDatb[6] = rotm
    if rot  != None: cDatb[7] = rot

    ### Constraint attributes (compatible with Blender class)
    # s,e,bt,ub,dc,ct
    if e  != None and e  != cDef["enabled"]:            cData["enabled"] = e
    if bt != None and bt != cDef["breaking_threshold"]: cData["breaking_threshold"] = bt  # *(1-random.random()/2)
    if ub != None and ub != cDef["use_breaking"]:       cData["use_breaking"] = ub
    if dc != None and dc != cDef["disable_collisions"]: cData["disable_collisions"] = dc
    if ct != None and ct != cDef["type"]:               cData["type"] = ct
    if so != None and so != cDef["use_override_solver_iterations"]: cData["use_override_solver_iterations"] = so
    if si != None and si != cDef["solver_iterations"]:              cData["solver_iterations"] = si
    
    # Limits Linear
    # ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu
    if ullx != None and ullx != cDef["use_limit_lin_x"]:   cData["use_limit_lin_x"] = ullx
    if ully != None and ully != cDef["use_limit_lin_y"]:   cData["use_limit_lin_y"] = ully
    if ullz != None and ullz != cDef["use_limit_lin_z"]:   cData["use_limit_lin_z"] = ullz
    if llxl != None and llxl != cDef["limit_lin_x_lower"]: cData["limit_lin_x_lower"] = llxl
    if llxu != None and llxu != cDef["limit_lin_x_upper"]: cData["limit_lin_x_upper"] = llxu
    if llyl != None and llyl != cDef["limit_lin_y_lower"]: cData["limit_lin_y_lower"] = llyl
    if llyu != None and llyu != cDef["limit_lin_y_upper"]: cData["limit_lin_y_upper"] = llyu
    if llzl != None and llzl != cDef["limit_lin_z_lower"]: cData["limit_lin_z_lower"] = llzl
    if llzu != None and llzu != cDef["limit_lin_z_upper"]: cData["limit_lin_z_upper"] = llzu

    # Limits Angular
    # ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu
    if ulax != None and ulax != cDef["use_limit_ang_x"]:   cData["use_limit_ang_x"] = ulax
    if ulay != None and ulay != cDef["use_limit_ang_y"]:   cData["use_limit_ang_y"] = ulay
    if ulaz != None and ulaz != cDef["use_limit_ang_z"]:   cData["use_limit_ang_z"] = ulaz
    if laxl != None and laxl != cDef["limit_ang_x_lower"]: cData["limit_ang_x_lower"] = laxl
    if laxu != None and laxu != cDef["limit_ang_x_upper"]: cData["limit_ang_x_upper"] = laxu
    if layl != None and layl != cDef["limit_ang_y_lower"]: cData["limit_ang_y_lower"] = layl
    if layu != None and layu != cDef["limit_ang_y_upper"]: cData["limit_ang_y_upper"] = layu
    if lazl != None and lazl != cDef["limit_ang_z_lower"]: cData["limit_ang_z_lower"] = lazl
    if lazu != None and lazu != cDef["limit_ang_z_upper"]: cData["limit_ang_z_upper"] = lazu

    # Spring Linear
    # uslx,usly,uslz, sdlx,sdly,sdlz, sslx,ssly,sslz
    if uslx != None and uslx != cDef["use_spring_x"]:       cData["use_spring_x"] = uslx
    if usly != None and usly != cDef["use_spring_y"]:       cData["use_spring_y"] = usly
    if uslz != None and uslz != cDef["use_spring_z"]:       cData["use_spring_z"] = uslz
    if sdlx != None and sdlx != cDef["spring_damping_x"]:   cData["spring_damping_x"] = sdlx
    if sdly != None and sdly != cDef["spring_damping_y"]:   cData["spring_damping_y"] = sdly
    if sdlz != None and sdlz != cDef["spring_damping_z"]:   cData["spring_damping_z"] = sdlz
    if sslx != None and sslx != cDef["spring_stiffness_x"]: cData["spring_stiffness_x"] = sslx
    if ssly != None and ssly != cDef["spring_stiffness_y"]: cData["spring_stiffness_y"] = ssly
    if sslz != None and sslz != cDef["spring_stiffness_z"]: cData["spring_stiffness_z"] = sslz
    
    # Spring Angular
    # usax,usay,usaz, sdax,sday,sdaz, ssax,ssay,ssaz
    if usax != None and usax != cDef["use_spring_ang_x"]:       cData["use_spring_ang_x"] = usax
    if usay != None and usay != cDef["use_spring_ang_y"]:       cData["use_spring_ang_y"] = usay
    if usaz != None and usaz != cDef["use_spring_ang_z"]:       cData["use_spring_ang_z"] = usaz
    if sdax != None and sdax != cDef["spring_damping_ang_x"]:   cData["spring_damping_ang_x"] = sdax
    if sday != None and sday != cDef["spring_damping_ang_y"]:   cData["spring_damping_ang_y"] = sday
    if sdaz != None and sdaz != cDef["spring_damping_ang_z"]:   cData["spring_damping_ang_z"] = sdaz
    if ssax != None and ssax != cDef["spring_stiffness_ang_x"]: cData["spring_stiffness_ang_x"] = ssax
    if ssay != None and ssay != cDef["spring_stiffness_ang_y"]: cData["spring_stiffness_ang_y"] = ssay
    if ssaz != None and ssaz != cDef["spring_stiffness_ang_z"]: cData["spring_stiffness_ang_z"] = ssaz

########################################
    
def setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsGeo, connectsConsts, constsConnect):
    
    ### Set constraint settings
    print("Generating main constraint settings... (%d)" %len(connectsPair))
    
    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene
    elemGrps = mem["elemGrps"]
    rbw_steps_per_second = scene.rigidbody_world.steps_per_second
    rbw_time_scale = scene.rigidbody_world.time_scale

    # Blender version handling
    if bpy.app.version <= (2, 79, 0) or hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'): version_spring = 1
    else:                                                                                 version_spring = 2

    exData = None
    connectsTol = []  # Create new array to store individual tolerances per connection
    ### Prepare dictionary of element indices for faster item search (optimization)
    objsDict = {}
    for i in range(len(objs)):
        objsDict[objs[i]] = i

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
    
    ### Get detonator object
    if len(props.detonatorObj):
        try: detonatorObj = scene.objects[props.detonatorObj]
        except: detonatorObj = None

    ### Generate settings and prepare the attributes but only store those which are different from the defaults
    llxl=-.000; llxu=.000; llyl=-.000; llyu=.000; llzl=-.000; llzu=.000  # Limits constraint room linear (x = normal direction)
    laxl=-.000; laxu=.000; layl=-.000; layu=.000; lazl=-.000; lazu=.000  # Limits constraint room angular
    constsData = []
    connectsConsts_iter = iter(connectsConsts)
    connectsLoc_iter = iter(connectsLoc)
    connectsGeo_iter = iter(connectsGeo)
    connectsPair_iter = iter(connectsPair)
    for k in range(len(connectsPair)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(connectsPair))
        
        pair = next(connectsPair_iter)   
        consts = next(connectsConsts_iter)
        loc = Vector(next(connectsLoc_iter))
        geo = next(connectsGeo_iter)
        connectsTol.append([0, 0, 0, 0])
        if version_spring == 1: springDamp = 1   # Later versions use "spring2" which need
        else:                   springDamp = 20  # different values to achieve the same behavior

        objA = objs[pair[0]]
        objB = objs[pair[1]]
        # If objects are missing fill in empty data and skip rest
        if objA == None or objB == None or len(consts) == 0:
            cData = {}; cDatb = []
            for cIdx in consts:
                setConstParams(cData,cDatb,cDef)
                constsData.append([cData, cDatb])
            continue
        
        geoContactArea = geo[0]

        # Initially check for valid contact area (zero check can invalidate connections for collision suppression instead of removing them)
        if props.disableCollisionPerm and not geoContactArea > 0:
            CT = -2  # Will only allow for the extra constraint

        else:

            # Geometry array: [area, height, width, surfThick, axisNormal, axisHeight, axisWidth]
            # Height is always smaller than width
            geoHeight = geo[1]
            geoWidth = geo[2]
            geoAxisNormal = geo[3]
            geoAxisHeight = geo[4]
            geoAxisWidth = geo[5]
            ax = [geoAxisNormal, geoAxisHeight, geoAxisWidth]

            # Calculate breaking threshold multiplier from explosion gradient of detonator object (-1 = center .. 1 = boundary, clamped to [0..1])
            if detonatorObj != None and detonatorObj.scale[0] > 0:
                btMultiplier = min(1, max(0, 2 *((loc -detonatorObj.location).length /detonatorObj.scale[0]) -1))
            else: btMultiplier = 1

            ### Prepare expression variables and convert m to mm
            a = geoContactArea *1000000
            h = geoHeight *1000
            w = geoWidth *1000
            
            x = loc[0]; y = loc[1]; z = loc[2]
            
            elemGrpA = objsEGrp[objsDict[objA]] 
            elemGrpB = objsEGrp[objsDict[objB]]
            elemGrps_elemGrpA = elemGrps[elemGrpA]
            elemGrps_elemGrpB = elemGrps[elemGrpB]
            NoHoA = elemGrps_elemGrpA[EGSidxNoHo]
            NoHoB = elemGrps_elemGrpB[EGSidxNoHo]
            NoCoA = elemGrps_elemGrpA[EGSidxNoCo]
            NoCoB = elemGrps_elemGrpB[EGSidxNoCo]

            ### Element length approximation (center to center vector)
            dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
            dirVecN = dirVec.normalized()
            geoLengthApprox = dirVec.length

            ### Check if connection between different groups is not allowed and remove them
            elemGrp = None
            CT = -1
            if (NoCoA or NoCoB) and elemGrpA != elemGrpB: CT = 0
            else:
                ### Check if horizontal connection between different groups and remove them (e.g. for masonry walls touching a framing structure)
                ### This code is used 3x, keep changes consistent in: builder_prep.py, builder_setc.py, and tools.py
                dirVecA = loc -objA.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
                dirVecAN = dirVecA.normalized()
                if abs(dirVecAN[2]) > 0.7: qA = 1
                else: qA = 0
                dirVecB = loc -objB.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
                dirVecBN = dirVecB.normalized()
                if abs(dirVecBN[2]) > 0.7: qB = 1
                else: qB = 0
                if qA == 0 and qB == 0 and (NoHoA or NoHoB) and elemGrpA != elemGrpB: CT = 0
            
            ###### Decision on which material settings from both groups will be used for connection
            if CT != 0:
                CT_A = elemGrps_elemGrpA[EGSidxCTyp]
                CT_B = elemGrps_elemGrpB[EGSidxCTyp]
                Prio_A = elemGrps_elemGrpA[EGSidxPrio]
                Prio_B = elemGrps_elemGrpB[EGSidxPrio]

                # A is active group
                if CT_A != 0:
                    ### Prepare expression strings
                    brkThresExprC_A = elemGrps_elemGrpA[EGSidxBTC]
                    brkThresExprT_A = elemGrps_elemGrpA[EGSidxBTT]
                    brkThresExprS_A = elemGrps_elemGrpA[EGSidxBTS]
                    brkThresExprS9_A = elemGrps_elemGrpA[EGSidxBTS9]
                    brkThresExprB_A = elemGrps_elemGrpA[EGSidxBTB]
                    brkThresExprB9_A = elemGrps_elemGrpA[EGSidxBTB9]
                    brkThresExprP_A = elemGrps_elemGrpA[EGSidxBTP]
                    brkThresValuePL_A = elemGrps_elemGrpA[EGSidxBTPL]
                    mul = elemGrps_elemGrpA[EGSidxBTX]
                    # Area correction calculation for cylinders (*pi/4)
                    if elemGrps_elemGrpA[EGSidxCyln]: mulCyl = 0.7854
                    else:                             mulCyl = 1
                    # Increase threshold for boundary condition case
                    if CT_B == 0: mul *= 2
                    ### Add surface variable and multipliers
                    if len(brkThresExprC_A): brkThresExprC_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprT_A): brkThresExprT_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprS_A): brkThresExprS_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprS9_A): brkThresExprS9_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprB_A): brkThresExprB_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprB9_A): brkThresExprB9_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprP_A): brkThresExprP_A += "*a" +"*%f"%mul +"*%f"%mulCyl
                    
                    ### Evaluate the breaking thresholds expressions of both elements for every degree of freedom
                    try: brkThresValueC_A = eval(brkThresExprC_A)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprC_A); brkThresValueC_A = 0
                    try: brkThresValueT_A = eval(brkThresExprT_A)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprT_A); brkThresValueT_A = 0
                    try: brkThresValueS_A = eval(brkThresExprS_A)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprS_A); brkThresValueS_A = 0

                    if len(brkThresExprS9_A):  # Can also have zero-size string if not used
                        try: brkThresValueS9_A = eval(brkThresExprS9_A)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprS9_A); brkThresValueS9_A = 0
                    else: brkThresValueS9_A = -1

                    try: brkThresValueB_A = eval(brkThresExprB_A)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprB_A); brkThresValueB_A = 0

                    if len(brkThresExprB9_A):  # Can also have zero-size string if not used
                        try: brkThresValueB9_A = eval(brkThresExprB9_A)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprB9_A); brkThresValueB9_A = 0
                    else: brkThresValueB9_A = -1

                    if len(brkThresExprP_A):  # Can also have zero-size string if not used
                        try: brkThresValueP_A = eval(brkThresExprP_A)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprP_A); brkThresValueP_A = 0
                    else: brkThresValueP_A = -1

                # B is active group
                if CT_B != 0:
                    ### Prepare expression strings
                    brkThresExprC_B = elemGrps_elemGrpB[EGSidxBTC]
                    brkThresExprT_B = elemGrps_elemGrpB[EGSidxBTT]
                    brkThresExprS_B = elemGrps_elemGrpB[EGSidxBTS]
                    brkThresExprS9_B = elemGrps_elemGrpB[EGSidxBTS9]
                    brkThresExprB_B = elemGrps_elemGrpB[EGSidxBTB]
                    brkThresExprB9_B = elemGrps_elemGrpB[EGSidxBTB9]
                    brkThresExprP_B = elemGrps_elemGrpB[EGSidxBTP]
                    brkThresValuePL_B = elemGrps_elemGrpB[EGSidxBTPL]
                    mul = elemGrps_elemGrpB[EGSidxBTX]
                    # Area correction calculation for cylinders (*pi/4)
                    if elemGrps_elemGrpB[EGSidxCyln]: mulCyl = 0.7854
                    else:                             mulCyl = 1
                    # Increase threshold for boundary condition case
                    if CT_A == 0: mul *= 2
                    ### Add surface variable and multipliers
                    if len(brkThresExprC_B): brkThresExprC_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprT_B): brkThresExprT_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprS_B): brkThresExprS_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprS9_B): brkThresExprS9_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprB_B): brkThresExprB_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprB9_B): brkThresExprB9_B += "*a" +"*%f"%mul +"*%f"%mulCyl
                    if len(brkThresExprP_B): brkThresExprP_B += "*a" +"*%f"%mul +"*%f"%mulCyl

                    ### Evaluate the breaking thresholds expressions of both elements for every degree of freedom
                    try: brkThresValueC_B = eval(brkThresExprC_B)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprC_B); brkThresValueC_B = 0
                    try: brkThresValueT_B = eval(brkThresExprT_B)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprT_B); brkThresValueT_B = 0
                    try: brkThresValueS_B = eval(brkThresExprS_B)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprS_B); brkThresValueS_B = 0

                    if len(brkThresExprS9_B):  # Can also have zero-size string if not used
                        try: brkThresValueS9_B = eval(brkThresExprS9_B)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprS9_B); brkThresValueS9_B = 0
                    else: brkThresValueS9_B = -1

                    try: brkThresValueB_B = eval(brkThresExprB_B)
                    except: print("\rError: Expression could not be evaluated:", brkThresExprB_B); brkThresValueB_B = 0

                    if len(brkThresExprB9_B):  # Can also have zero-size string if not used
                        try: brkThresValueB9_B = eval(brkThresExprB9_B)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprB9_B); brkThresValueB9_B = 0
                    else: brkThresValueB9_B = -1

                    if len(brkThresExprP_B):  # Can also have zero-size string if not used
                        try: brkThresValueP_B = eval(brkThresExprP_B)
                        except: print("\rError: Expression could not be evaluated:", brkThresExprP_B); brkThresValueP_B = 0
                    else: brkThresValueP_B = -1

                # Both A and B are active groups and priority is the same
                if CT_A != 0 and CT_B != 0 and Prio_A == Prio_B:
                    ### Use the connection type with the smaller count of constraints for connection between different element groups
                    ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
                    if connectTypes[CT_A][1] <= connectTypes[CT_B][1]:
                        CT = CT_A
                        elemGrp = elemGrpA
                    else:
                        CT = CT_B
                        elemGrp = elemGrpB
                                
                    if props.lowerBrkThresPriority:
                        ### Use the weaker of both breaking thresholds for every degree of freedom
                        if brkThresValueC_A <= brkThresValueC_B: brkThresValueC = brkThresValueC_A
                        else:                                    brkThresValueC = brkThresValueC_B

                        if brkThresValueT_A <= brkThresValueT_B: brkThresValueT = brkThresValueT_A
                        else:                                    brkThresValueT = brkThresValueT_B

                        if brkThresValueS_A <= brkThresValueS_B: brkThresValueS = brkThresValueS_A
                        else:                                    brkThresValueS = brkThresValueS_B

                        if brkThresValueS9_A == -1 or brkThresValueS9_B == -1: brkThresValueS9 = -1
                        else:    
                            if brkThresValueS9_A <= brkThresValueS9_B: brkThresValueS9 = brkThresValueS9_A
                            else:                                      brkThresValueS9 = brkThresValueS9_B

                        if brkThresValueB_A <= brkThresValueB_B: brkThresValueB = brkThresValueB_A
                        else:                                    brkThresValueB = brkThresValueB_B

                        if brkThresValueB9_A == -1 or brkThresValueB9_B == -1: brkThresValueB9 = -1
                        else:    
                            if brkThresValueB9_A <= brkThresValueB9_B: brkThresValueB9 = brkThresValueB9_A
                            else:                                      brkThresValueB9 = brkThresValueB9_B

                        if brkThresValueP_A == -1 or brkThresValueP_B == -1: brkThresValueP = -1
                        else:    
                            if brkThresValueP_A <= brkThresValueP_B: brkThresValueP = brkThresValueP_A
                            else:                                    brkThresValueP = brkThresValueP_B

                        if brkThresValuePL_A <= brkThresValuePL_B: brkThresValuePL = brkThresValuePL_A
                        else:                                      brkThresValuePL = brkThresValuePL_B

                    else:
                        ### Use the stronger of both breaking thresholds for every degree of freedom
                        if brkThresValueC_A > brkThresValueC_B: brkThresValueC = brkThresValueC_A
                        else:                                   brkThresValueC = brkThresValueC_B

                        if brkThresValueT_A > brkThresValueT_B: brkThresValueT = brkThresValueT_A
                        else:                                   brkThresValueT = brkThresValueT_B

                        if brkThresValueS_A > brkThresValueS_B: brkThresValueS = brkThresValueS_A
                        else:                                   brkThresValueS = brkThresValueS_B

                        if brkThresValueS9_A == -1 or brkThresValueS9_B == -1: brkThresValueS9 = -1
                        else:    
                            if brkThresValueS9_A > brkThresValueS9_B: brkThresValueS9 = brkThresValueS9_A
                            else:                                     brkThresValueS9 = brkThresValueS9_B

                        if brkThresValueB_A > brkThresValueB_B: brkThresValueB = brkThresValueB_A
                        else:                                   brkThresValueB = brkThresValueB_B

                        if brkThresValueB9_A == -1 or brkThresValueB9_B == -1: brkThresValueB9 = -1
                        else:    
                            if brkThresValueB9_A > brkThresValueB9_B: brkThresValueB9 = brkThresValueB9_A
                            else:                                     brkThresValueB9 = brkThresValueB9_B

                        if brkThresValueP_A == -1 or brkThresValueP_B == -1: brkThresValueP = -1
                        else:    
                            if brkThresValueP_A > brkThresValueP_B: brkThresValueP = brkThresValueP_A
                            else:                                   brkThresValueP = brkThresValueP_B

                        if brkThresValuePL_A > brkThresValuePL_B: brkThresValuePL = brkThresValuePL_A
                        else:                                     brkThresValuePL = brkThresValuePL_B
                    
                # Only A is active and B is passive group or priority is higher for A
                elif CT_A != 0 and CT_B == 0 or (CT_A != 0 and CT_B != 0 and Prio_A > Prio_B):
                    CT = CT_A
                    elemGrp = elemGrpA
                    brkThresValueC = brkThresValueC_A
                    brkThresValueT = brkThresValueT_A
                    brkThresValueS = brkThresValueS_A
                    if brkThresValueS9_A == -1: brkThresValueS9 = -1
                    else: brkThresValueS9 = brkThresValueS9_A
                    brkThresValueB = brkThresValueB_A
                    if brkThresValueB9_A == -1: brkThresValueB9 = -1
                    else: brkThresValueB9 = brkThresValueB9_A
                    brkThresValueP = brkThresValueP_A
                    brkThresValuePL = brkThresValuePL_A
         
                # Only B is active and A is passive group or priority is higher for B
                elif CT_A == 0 and CT_B != 0 or (CT_A != 0 and CT_B != 0 and Prio_A < Prio_B):
                    CT = CT_B
                    elemGrp = elemGrpB
                    brkThresValueC = brkThresValueC_B
                    brkThresValueT = brkThresValueT_B
                    brkThresValueS = brkThresValueS_B
                    if brkThresValueS9_B == -1: brkThresValueS9 = -1
                    else: brkThresValueS9 = brkThresValueS9_B
                    brkThresValueB = brkThresValueB_B
                    if brkThresValueB9_B == -1: brkThresValueB9 = -1
                    else: brkThresValueB9 = brkThresValueB9_B
                    brkThresValueP = brkThresValueP_B
                    brkThresValuePL = brkThresValuePL_B

                # Both A and B are in passive group but either one is actually an active RB (A xor B)
                elif bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
                    CT = -1  # Only one fixed constraint is used to connect these (buffer special case)

                # Both A and B are in passive group and both are passive RBs
                else:
                    CT = 0            

                # For unbreakable passive connections above settings can be overwritten
                if not props.passiveUseBreaking:
                    # Both A and B are in passive group but either one is actually an active RB (A xor B)
                    if bool(objA.rigid_body.type == 'ACTIVE') != bool(objB.rigid_body.type == 'ACTIVE'):
                        CT = -1  # Only one fixed constraint is used to connect these (buffer special case)

                ###### CT is now known and we can prepare further settings accordingly
                
                if elemGrp != None:
                    elemGrps_elemGrp = elemGrps[elemGrp]
                    disColPerm = elemGrps_elemGrp[EGSidxDClP]
                else:
                    disColPerm = 0

                if CT > 0:
                    ### Get spring length to be used later for stiffness calculation
                    if brkThresValuePL > 0: springLength = brkThresValuePL
                    else:                   springLength = geoLengthApprox
                    if springLength == 0: springLength = 0.1  # Fallback to avoid division by 0 in case geometry of length 0 is found
                    ### Calculate orientation between the two elements
                    # Recalculate directional vector for better constraint alignment
                    if props.snapToAreaOrient:
                        # Use contact area for orientation (axis closest to thickness)
                        if geoAxisNormal == 1:   dirVecNew = Vector((1, 0, 0))
                        elif geoAxisNormal == 2: dirVecNew = Vector((0, 1, 0))
                        elif geoAxisNormal == 3: dirVecNew = Vector((0, 0, 1))
                        # Take direction into account too and negate axis if necessary
                        if dirVec[0] < 0: dirVecNew[0] = -dirVecNew[0]
                        if dirVec[1] < 0: dirVecNew[1] = -dirVecNew[1]
                        if dirVec[2] < 0: dirVecNew[2] = -dirVecNew[2]
                        dirVec = dirVecNew
                    else:
                        if props.alignVertical:
                            # Reduce X and Y components by factor of props.alignVertical (should be < 1 to make horizontal connections still possible)
                            dirVec = Vector((dirVec[0] *(1 -props.alignVertical), dirVec[1] *(1 -props.alignVertical), dirVec[2]))
                    # Align constraint rotation to that vector
                    rotN = dirVec.to_track_quat('X','Z')
                    
                    ### Calculate tolerances and store them for the monitor
                    tol1dist = elemGrps_elemGrp[EGSidxTl1D]
                    tol1rot = elemGrps_elemGrp[EGSidxTl1R]
                    tol2dist = elemGrps_elemGrp[EGSidxTl2D]
                    tol2rot = elemGrps_elemGrp[EGSidxTl2R]
                    asst = elemGrps_elemGrp[EGSidxAsst]
                    ### Calculate tolerance from Formula Assistant settings
                    if tol2dist == 0:
                        # Only try to use FA settings if there is a valid one active
                        if asst['ID'] == "con_rei_beam" or asst['ID'] == "con_rei_wall":
                              tol2dist = asst['elu'] /100
                        else: tol2dist = presets[0][EGSidxTl2D]  # Use tolerance from preset #0 as last resort
                    if tol2rot == 0:
                        # Only try to use FA settings if there is a valid one active
                        if (asst['ID'] == "con_rei_beam" or asst['ID'] == "con_rei_wall") and h > 0:
                              tol2rot = math.atan(((asst['elu']/100) *geoLengthApprox) /(geoHeight/2))
                              #tol2rot = math.atan(((asst['elu']/100) *((asst['w']/1000)/asst['n'])) /(geoHeight/2))
                        else: tol2rot = presets[0][EGSidxTl2R]  # Use tolerance from preset #0 as last resort
                    # Add new tolerances to build data array
                    connectsTol[-1] = [tol1dist, tol1rot, tol2dist, tol2rot]
                    
                    ### Other settings
                    so = bool(elemGrps_elemGrp[EGSidxIter])
                    si = elemGrps_elemGrp[EGSidxIter]

                    ### Check if full update is necessary (optimization)
                    if not props.asciiExport:
                        objConst0 = emptyObjs[consts[0]]
                        if 'ConnectType' in objConst0.keys() and objConst0['ConnectType'] == CT: qUpdateComplete = 0
                        else: objConst0['ConnectType'] = CT; qUpdateComplete = 1
                        ### Store value as ID property for debug purposes
                        objConst0['Contact Area'] = geoContactArea
                        damage = (1 -btMultiplier) *100
                        if btMultiplier < 1:
                            for idx in consts: emptyObjs[idx]['Damage %'] = damage
                    else:
                        qUpdateComplete = 1
            
        ### Set constraints by connection type preset
        ### Also convert real world breaking threshold to bullet breaking threshold and take simulation steps into account (Threshold = F / Steps)
        
        # Overview:
        
        # Special CTs:
        #   if CT == -2 
        #       None; Only extra constraint for permanent collision suppression is allowed 
        #   if CT == -1 
        #       1x FIXED; Indestructible buffer between passive and active foundation elements
        
        # Basic CTs:
        #   if CT == 1 or CT == 9 or CT == 10 or CT == 19:
        #       1x FIXED; Linear omni-directional + bending breaking threshold
        #   if CT == 2 or CT == 25:
        #       1x POINT; Linear omni-directional breaking threshold
        #   if CT == 3 or CT == 20:
        #       1x POINT + 1x FIXED; Linear omni-directional, bending breaking thresholds

        # Compressive:
        #   if CT == 4 or CT == 5 or CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 21 or CT == 22 or CT == 23:
        #       1x GENERIC; Compressive threshold

        # Tensile + Shearing:
        #   if CT == 4:
        #       1x GENERIC; Tensile + bending (3D)
        #   if CT == 5:
        #       2x GENERIC; Tensile + shearing (3D), bending (3D) breaking thresholds
        #   if CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 21 or CT == 22 or CT == 23:
        #       3x GENERIC; Tensile constraint (1D) breaking thresholds
        #   if CT == 6 or CT == 11 or CT == 12 or CT == 21:
        #       1x GENERIC; Shearing (2D), bending (2D) breaking thresholds
        #   if CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 22 or CT == 23:
        #       2x GENERIC; Shearing (1D) breaking thresholds
        #   if CT == 15 or CT == 17 or CT == 22:
        #       2x GENERIC; Bending + torsion (1D) breaking thresholds
        #   if CT == 16 or CT == 18 or CT == 23:
        #       3x GENERIC; Bending (1D), torsion (1D) breaking thresholds
        
        # Springs:
        #   if CT == 24:
        #       1x SPRING; All degrees of freedom with plastic deformability
        #   if CT == 25:
        #       1x SPRING; Bending + torsion (1D) breaking thresholds with plastic deformability
        
        # Springs (2nd mode):
        #   if CT == 7 or CT == 9 or CT == 11 or CT == 17 or CT == 18:
        #       3x SPRING; Circular placed for plastic deformability
        #   if CT == 8 or CT == 10 or CT == 12:
        #       4x SPRING; Circular placed for plastic deformability
        #   if CT == 9 or CT == 11 or CT == 17 or CT == 18:
        #       1x SPRING; Now with angular limits circular placement is not required for plastic deformability anymore

        # Springs only CTs
        #   if CT == 13:
        #       3 x 3x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        #   if CT == 14:
        #       3 x 4x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
            
        cInc = 0

        ### 1x FIXED; Indestructible buffer between passive and active foundation elements
        if CT == -1:
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            setConstParams(cData,cDatb,cDef, loc=loc, ub=0, dc=1, ct='FIXED', so=props.passiveUseBreaking,si=1)
            constsData.append([cData, cDatb])

        ### 1x FIXED; Linear omni-directional + bending breaking threshold
        if CT == 1 or CT == 9 or CT == 10 or CT == 19:
            constCount = 1; correction = 1  # No correction required for this constraint type
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueC
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, loc=loc, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='FIXED', so=so,si=si)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])

        ### 1x POINT; Linear omni-directional breaking threshold
        if CT == 2 or CT == 25:
            constCount = 1; correction = 1  # No correction required for this constraint type
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueC
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, loc=loc, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='POINT', so=so,si=si)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])
        
        ### 1x POINT + 1x FIXED; Linear omni-directional, bending breaking thresholds    
        if CT == 3 or CT == 20:
            constCount = 2; correction = 1  # No correction required for this constraint type
            
            ### First constraint
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueC
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, loc=loc, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='POINT', so=so,si=si)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])

            ### Second constraint
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueB
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, loc=loc, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='FIXED', so=so,si=si)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])
        
        ### 1x GENERIC; Compressive threshold
        if CT == 4 or CT == 5 or CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 21 or CT == 22 or CT == 23:
            ### First constraint
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueC
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock all directions for the compressive force
                ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                ### Also rotational forces should only be carried by the tensile constraint
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=llxl,llxu=99999, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])

        ### 1x GENERIC; Tensile (3D)
        if CT == 4:
            ### Second constraint
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueT
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock all directions for the tensile force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=llxu,llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=1,ulay=1,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])
            
        ### 2x GENERIC; Tensile + shearing (3D), bending (3D) breaking thresholds
        if CT == 5:
            ### Tensile + shearing constraint (3D)
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueT
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions for shearing force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=llxu,llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot])
            constsData.append([cData, cDatb])

            ### Bending constraint (3D)
            constCount = 1; correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueS
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions for bending force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])
            
        ### 3x GENERIC; Tensile constraint (1D) breaking threshold
        if CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 21 or CT == 22 or CT == 23:
            ### Tensile constraint (1D)
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueT
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock direction for tensile force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=llxu, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

        ### 3x GENERIC; Shearing constraint (2D), bending constraint (3D) breaking thresholds
        if CT == 6 or CT == 11 or CT == 12 or CT == 21:
            ### Shearing constraint (2D)
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueS
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions for shearing force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=1,ullz=1, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

            ### Bending constraint (3D)
            constCount = 1; correction = 1
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueB
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions for bending force
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

        ### 2x GENERIC; Shearing (1D) breaking thresholds
        if CT == 15 or CT == 16 or CT == 17 or CT == 18 or CT == 22 or CT == 23:
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            
            ### Shearing constraint #1
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            btRatio = 1
            value = brkThresValueS
            if brkThresValueS9 != -1:
                value1 = value
                value = brkThresValueS9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            elif brkThresValueB9 == -1:  # Only use btRatio if neither shear nor bend have a 90° value
                if geoHeight > props.searchDistance and geoWidth > props.searchDistance:
                      btRatio = geoHeight /geoWidth
                else: btRatio = 1
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = rot.to_matrix().inverted()
                if geoAxisHeight == 1:   vecAxis = Vector((1, 0, 0))
                elif geoAxisHeight == 2: vecAxis = Vector((0, 1, 0))
                else:                    vecAxis = Vector((0, 0, 1))
                # Leave out x axis as we know it is only for compressive and tensile force
                vec = Vector((0, 1, 0)) *matInv
                angY = vecAxis.angle(vec, 0)
                vec = Vector((0, 0, 1)) *matInv
                angZ = vecAxis.angle(vec, 0)
                if angY != angZ:
                    angSorted = [[pi2 -abs(angY -pi2), 2], [pi2 -abs(angZ -pi2), 3]]
                    angSorted.sort(reverse=False)
                    constAxisToLock = angSorted[0][1]  # Result: 1 = X, 2 = Y, 3 = Z
                else:  # Gimbal lock special case when normal X axis aligns to global Z axis, not nice but will do for now
                    dirEul = rotN.to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                if constAxisToLock == 2:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ully=1,ullz=0, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
                elif constAxisToLock == 3: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ully=0,ullz=1, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

            ### Shearing constraint #2
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            if brkThresValueS9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
            if btRatio != 1: btRatio = 1 /btRatio
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions accordingly to axis
                if constAxisToLock == 3:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ully=1,ullz=0, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
                elif constAxisToLock == 2: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ully=0,ullz=1, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])
            
        ### 2x GENERIC; Bending + torsion (1D) breaking thresholds
        if CT == 15 or CT == 17 or CT == 22:
            constCount = 1; correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library
            
            ### Bending with torsion constraint #1
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            btRatio = 1
            value = brkThresValueB
            if brkThresValueB9 != -1:
                value1 = value
                value = brkThresValueB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            elif brkThresValueS9 == -1:  # Only use btRatio if neither shear nor bend have a 90° value
                if geoHeight > props.searchDistance and geoWidth > props.searchDistance:
                      btRatio = geoHeight /geoWidth
                else: btRatio = 1
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = rot.to_matrix().inverted()
                if geoAxisHeight == 1:   vecAxis = Vector((1, 0, 0))
                elif geoAxisHeight == 2: vecAxis = Vector((0, 1, 0))
                else:                    vecAxis = Vector((0, 0, 1))
                # Leave out x axis as we know it is only for compressive and tensile force
                vec = Vector((0, 1, 0)) *matInv
                angY = vecAxis.angle(vec, 0)
                vec = Vector((0, 0, 1)) *matInv
                angZ = vecAxis.angle(vec, 0)
                if angY != angZ:
                    angSorted = [[pi2 -abs(angY -pi2), 2], [pi2 -abs(angZ -pi2), 3]]
                    angSorted.sort(reverse=False)
                    constAxisToLock = angSorted[0][1]  # Result: 1 = X, 2 = Y, 3 = Z
                else:  # Gimbal lock special case when normal X axis aligns to global Z axis, not nice but will do for now
                    dirEul = rotN.to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                if constAxisToLock == 2:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                elif constAxisToLock == 3: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

            ### Bending with torsion constraint #2
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            if brkThresValueB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
            if btRatio != 1: btRatio = 1 /btRatio
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions accordingly to axis
                if constAxisToLock == 3:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                elif constAxisToLock == 2: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

        ### 3x GENERIC; Bending (1D), torsion (1D) breaking thresholds
        if CT == 16 or CT == 18 or CT == 23:
            constCount = 1; correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library
            
            ### Bending without torsion constraint #1
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            btRatio = 1
            value = brkThresValueB
            if brkThresValueB9 != -1:
                value1 = value
                value = brkThresValueB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            elif brkThresValueS9 == -1:  # Only use btRatio if neither shear nor bend have a 90° value
                if geoHeight > props.searchDistance and geoWidth > props.searchDistance:
                      btRatio = geoHeight /geoWidth
                else: btRatio = 1
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = rot.to_matrix().inverted()
                if geoAxisHeight == 1:   vecAxis = Vector((1, 0, 0))
                elif geoAxisHeight == 2: vecAxis = Vector((0, 1, 0))
                else:                    vecAxis = Vector((0, 0, 1))
                # Leave out x axis as we know it is only for compressive and tensile force
                vec = Vector((0, 1, 0)) *matInv
                angY = vecAxis.angle(vec, 0)
                vec = Vector((0, 0, 1)) *matInv
                angZ = vecAxis.angle(vec, 0)
                if angY != angZ:
                    angSorted = [[pi2 -abs(angY -pi2), 2], [pi2 -abs(angZ -pi2), 3]]
                    angSorted.sort(reverse=False)
                    constAxisToLock = angSorted[0][1]  # Result: 1 = X, 2 = Y, 3 = Z
                else:  # Gimbal lock special case when normal X axis aligns to global Z axis, not nice but will do for now
                    dirEul = rotN.to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                if constAxisToLock == 2:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=0,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                elif constAxisToLock == 3: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=1,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

            ### Bending without torsion constraint #2
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            if brkThresValueB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
            if btRatio != 1: btRatio = 1 /btRatio
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions accordingly to axis
                if constAxisToLock == 3:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=0,ulaz=1, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                elif constAxisToLock == 2: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=1,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

            ### Torsion constraint
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            try: value = values[0]  # Use the smaller value from either standard or 90n
            except: pass
            btRatio = 1
#            value = brkThresValueS
#            if brkThresValueS9 != -1:
#                value1 = value
#                value = brkThresValueS9
#                value2 = value
#                values = [value1, value2]
#                values.sort()
#                value = values[0]  # Find and use smaller value (to be used along h axis)
#            elif brkThresValueB9 == -1:  # Only use btRatio if neither shear nor bend have a 90° value
#                if geoHeight > props.searchDistance and geoWidth > props.searchDistance:
#                      btRatio = geoHeight /geoWidth
#                else: btRatio = 1
            value *= .5  # Use 50% of the bending thresholds for torsion (we really need a formula for that)
            brkThres = value *btRatio *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock directions accordingly to axis
                if constAxisToLock == 3:   setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                elif constAxisToLock == 2: setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=laxl,laxu=laxu,layl=layl,layu=layu,lazl=lazl,lazu=lazu)
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot],rotm=rotm)
            constsData.append([cData, cDatb])

        ###### Springs (additional)

        ### 3x SPRING; Circular placed for plastic deformability
        if CT == 7 or CT == 9 or CT == 11 or CT == 17 or CT == 18:
            constCount = 3; correction = 2  # Generic constraints detach already when less force than the breaking threshold is applied (the factor for springs without locks is 0.5) so we multiply our threshold by this correctional value
            radius = geoHeight /2
            value = brkThresValueP
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            ### Loop through all constraints of this connection
            for i in range(3):
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   i == 0: vec = Vector((0, radius, radius))
                    elif i == 1: vec = Vector((0, radius, -radius))
                    elif i == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING')
                if CT != 7:
                    # Disable springs on start (requires plastic activation during simulation)
                    setConstParams(cData,cDatb,cDef, e=0)
                if props.asciiExport:
                    if CT == 7:
                          setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                    else: setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC_OFF",tol2dist,tol2rot])
                constsData.append([cData, cDatb])
                          
                
        ### 4x SPRING; Circular placed for plastic deformability
        if CT == 8 or CT == 10 or CT == 12:
            constCount = 4; correction = 2   # Generic constraints detach already when less force than the breaking threshold is applied (the factor for springs without locks is 0.5) so we multiply our threshold by this correctional value
            radius = geoHeight /2
            value = brkThresValueP
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            ### Loop through all constraints of this connection
            for i in range(4):
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   i == 0: vec = Vector((0, radius, radius))
                    elif i == 1: vec = Vector((0, radius, -radius))
                    elif i == 2: vec = Vector((0, -radius, -radius))
                    elif i == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING')
                if CT != 8:
                    # Disable springs on start (requires plastic activation during simulation)
                    setConstParams(cData,cDatb,cDef, e=0)
                if props.asciiExport:
                    if CT == 8:
                          setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                    else: setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC_OFF",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

        ### 1x SPRING; Now with angular limits circular placement is not required for plastic deformability anymore
        if CT == 19 or CT == 20 or CT == 21 or CT == 22 or CT == 23:
            constCount = 1; correction = 2   # Generic constraints detach already when less force than the breaking threshold is applied (the factor for springs without locks is 0.5) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueP
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp, usax=1,usay=1,usaz=1, ssax=springStiff,ssay=springStiff,ssaz=springStiff, sdax=springDamp,sday=springDamp,sdaz=springDamp)
            if qUpdateComplete:
                ### Enable linear and angular spring
                setConstParams(cData,cDatb,cDef, loc=loc, ct='GENERIC_SPRING')
            # Disable springs on start (requires plastic activation during simulation, comment out if not required)
            setConstParams(cData,cDatb,cDef, e=0)
            if props.asciiExport:
                # Enable springs on start (if this spring is not for plastic deformation, comment out if not required)
                #setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                # Disable springs on start (requires plastic activation during simulation, comment out if not required)
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC_OFF",tol2dist,tol2rot])
            constsData.append([cData, cDatb])

        ###### Springs only CTs

        ### 3 x 3x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 13:
            constCount = 3; correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            radius = geoHeight /2
            value = brkThresValueC
            brkThres1 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueT
            brkThres2 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueS
            brkThres3 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueP
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            # Loop through all constraints of this connection
            for j in range(3):

                ### First constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres1, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp, usax=1,usay=1,usaz=1, ssax=springStiff,ssay=springStiff,ssaz=springStiff, sdax=springDamp,sday=springDamp,sdaz=springDamp)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock direction for compressive force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=llxl,llxu=99999, ulax=0,ulay=0,ulaz=0)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])
                    
                ### Second constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres2, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, sslx=springStiff,ssly=springStiff,sslz=springStiff)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock direction for tensile force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=llxu, ulax=0,ulay=0,ulaz=0, uslx=1,usly=1,uslz=1, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

                ### Third constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres3, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, sslx=springStiff,ssly=springStiff,sslz=springStiff)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock directions for shearing force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=0,ully=1,ullz=1, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0, uslx=1,usly=1,uslz=1, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

        ### 3 x 4x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 14:
            constCount = 4; correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            radius = geoHeight /2
            value = brkThresValueC
            brkThres1 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueT
            brkThres2 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueS
            brkThres3 = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            value = brkThresValueP
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            # Loop through all constraints of this connection
            for j in range(4):

                ### First constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres1, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp, usax=1,usay=1,usaz=1, ssax=springStiff,ssay=springStiff,ssaz=springStiff, sdax=springDamp,sday=springDamp,sdaz=springDamp)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock direction for compressive force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=llxl,llxu=99999, ulax=0,ulay=0,ulaz=0)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

                ### Second constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres2, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, sslx=springStiff,ssly=springStiff,sslz=springStiff)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock direction for tensile force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=llxu, ulax=0,ulay=0,ulaz=0, uslx=1,usly=1,uslz=1, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

                ### Third constraint
                cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
                setConstParams(cData,cDatb,cDef, bt=brkThres3, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, sslx=springStiff,ssly=springStiff,sslz=springStiff)
                if qUpdateComplete:
                    rotm = 'QUATERNION'
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(rotN)
                    locN = loc +vec
                    ### Lock directions for shearing force and enable linear spring
                    setConstParams(cData,cDatb,cDef, loc=locN,rotm=rotm, ct='GENERIC_SPRING', ullx=0,ully=1,ullz=1, llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=0,ulaz=0, uslx=1,usly=1,uslz=1, sdlx=springDamp,sdly=springDamp,sdlz=springDamp)
                if props.asciiExport:
                    setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                constsData.append([cData, cDatb])

        ### 1x SPRING; All degrees of freedom with plastic deformability
        if CT == 24:
            constCount = 1; correction = 2   # Generic constraints detach already when less force than the breaking threshold is applied (the factor for springs without locks is 0.5) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueP
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, uslx=1,usly=1,uslz=1, sslx=springStiff,ssly=springStiff,sslz=springStiff, sdlx=springDamp,sdly=springDamp,sdlz=springDamp, usax=1,usay=1,usaz=1, ssax=springStiff,ssay=springStiff,ssaz=springStiff, sdax=springDamp,sday=springDamp,sdaz=springDamp)
            if qUpdateComplete:
                ### Enable linear and angular spring
                setConstParams(cData,cDatb,cDef, loc=loc, ct='GENERIC_SPRING')
            # Disable springs on start (requires plastic activation during simulation, comment out if not required)
            #setConstParams(cData,cDatb,cDef, e=0)
            if props.asciiExport:
                # Enable springs on start (if this spring is not for plastic deformation, comment out if not required)
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                # Disable springs on start (requires plastic activation during simulation, comment out if not required)
                #setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC_OFF",tol2dist,tol2rot])
            constsData.append([cData, cDatb])

        ### 1x SPRING; Bending + torsion (1D) breaking thresholds with plastic deformability
        if CT == 25:
            constCount = 1; correction = 2   # Generic constraints detach already when less force than the breaking threshold is applied (the factor for springs without locks is 0.5) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueP
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            if version_spring == 1:
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount
            else:  # Later versions use "spring2" which need different formulas to achieve the same behavior
                springStiff = value *btMultiplier /(springLength *tol2dist) *correction /constCount /2
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si, uslx=0,usly=0,uslz=0, usax=1,usay=1,usaz=1, ssax=springStiff,ssay=springStiff,ssaz=springStiff, sdax=springDamp,sday=springDamp,sdaz=springDamp)
            if qUpdateComplete:
                ### Enable linear and angular spring
                setConstParams(cData,cDatb,cDef, loc=loc, ct='GENERIC_SPRING')
            # Disable springs on start (requires plastic activation during simulation, comment out if not required)
            #setConstParams(cData,cDatb,cDef, e=0)
            if props.asciiExport:
                # Enable springs on start (if this spring is not for plastic deformation, comment out if not required)
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC",tol2dist,tol2rot])
                # Disable springs on start (requires plastic activation during simulation, comment out if not required)
                #setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,tol1rot], tol2=["PLASTIC_OFF",tol2dist,tol2rot])
            constsData.append([cData, cDatb])

        ### 1x HINGE; Linear omni-directional + bending XY breaking threshold
        if CT == 26:
            ### First constraint
            constCount = 1; correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            value = brkThresValueC
            brkThres = value *btMultiplier /rbw_steps_per_second *rbw_time_scale *correction /constCount
            setConstParams(cData,cDatb,cDef, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, rot=rotN, so=so,si=si)
            if qUpdateComplete:
                rotm = 'QUATERNION'
                ### Lock all directions for the compressive force
                ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                ### Also rotational forces should only be carried by the tensile constraint
                setConstParams(cData,cDatb,cDef, loc=loc,rotm=rotm, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=llxl,llxu=llxu,llyl=llyl,llyu=llyu,llzl=llzl,llzu=llzu, ulax=0,ulay=1,ulaz=1, layl=layl,layu=layu,lazl=lazl,lazu=lazu)
                # Disable angular tolerances in build data array (required for monitor)
                connectsTol[-1] = [tol1dist, -1, tol2dist, -1]
            if props.asciiExport:
                setConstParams(cData,cDatb,cDef, tol1=["TOLERANCE",tol1dist,-1])
            constsData.append([cData, cDatb])

        ###### Special CTs
        
        ### 1x GENERIC; Constraint for permanent collision suppression and no influence otherwise
        if CT != 0 and (props.disableCollisionPerm or disColPerm):
            cData = {}; cDatb = []; cIdx = consts[cInc]; cInc += 1
            constCount = 1; correction = 1  # No correction required for this constraint type
            setConstParams(cData,cDatb,cDef, loc=loc, bt=-1, ub=0, dc=1, ct='GENERIC')
            constsData.append([cData, cDatb])

    print()
    if len(emptyObjs) != len(constsData):
        print("WARNING: Size mismatch: emptyObjs, constsData;", len(emptyObjs), len(constsData))
    if len(connectsPair) != len(connectsTol):
        print("WARNING: Size mismatch: connectsPair, connectsTol;", len(connectsPair), len(connectsTol))

    ### Debug: Naming of the constraints according to their connection participation and storage of object names
    connectsPair_iter = iter(connectsPair)
    connectsConsts_iter = iter(connectsConsts)
    for k in range(len(connectsPair)):
        consts = next(connectsConsts_iter)
        pair = next(connectsPair_iter)   
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        i = 1
        for cIdx in consts:
            cData, cDatb = constsData[cIdx]
            name = "Con.%03d.%d" %(k, i)
            # Store names and objects
            setConstParams(cData,cDatb,cDef, name=name, obj1=objA, obj2=objB)
            i += 1

    if not props.asciiExport:

        ### Write constraint settings into constraint objects
        print("Writing constraint settings into empty objects... (%d)" %len(emptyObjs))
        emptyObjs_iter = iter(emptyObjs)
        constsData_iter = iter(constsData)
        for k in range(len(emptyObjs)):
            sys.stdout.write('\r' +"%d" %k)
            # Update progress bar
            bpy.context.window_manager.progress_update(k /len(emptyObjs))
            
            objConst = next(emptyObjs_iter)
            cData, cDatb = next(constsData_iter)
            
            ### Write empty object parameters (BCB specific attributes, commented out lines are defined elsewhere)
            if cDatb != None and objConst != None:
                if cDatb[0] != None: objConst.name                          = cDatb[0]
                if cDatb[1] != None: objConst.location                      = cDatb[1]
                if cDatb[2] != None: objConst.rigid_body_constraint.object1 = cDatb[2]
                if cDatb[3] != None: objConst.rigid_body_constraint.object2 = cDatb[3]
                if cDatb[6] != None: objConst.rotation_mode                 = cDatb[6]
                if cDatb[7] != None: objConst.rotation_quaternion           = cDatb[7]
            
            ### Overwrite default constraint settings with new and different settings
            if objConst != None:
                setAttribsOfConstraint(objConst.rigid_body_constraint, cData)
        print()

        # Update names in database in case they were changed
        scene["bcb_emptyObjs"] = [obj.name for obj in emptyObjs if obj != None]

        ### Calculating constraint widgets for drawing
        print("Calculating constraint widgets for drawing... (%d)" %len(connectsPair))
        connectsConsts_iter = iter(connectsConsts)
        connectsGeo_iter = iter(connectsGeo)
        for k in range(len(connectsPair)):
            sys.stdout.write('\r' +"%d" %k)
            # Update progress bar
            bpy.context.window_manager.progress_update(k /len(connectsPair))
            
            consts = next(connectsConsts_iter)            
            geo = next(connectsGeo_iter)
            geoContactArea = geo[0]
            geoHeight = geo[1]
            geoWidth = geo[2]
            a = geoContactArea *1000000
            h = geoHeight *1000
            w = geoWidth *1000

            ### Gather values from constraints
            yl = 0; zl = 0; ya = 0; za = 0
            for cIdx in consts:
                objConst = emptyObjs[cIdx]
                if objConst != None:
                    constData = objConst.rigid_body_constraint
                    if constData.type == 'GENERIC' or (constData.type == 'GENERIC_SPRING' and constData.enabled):
                        # Use shearing thresholds as base for empty scaling
                        if constData.use_limit_lin_y: yl = constData.breaking_threshold
                        if constData.use_limit_lin_z: zl = constData.breaking_threshold
                        # Use bending thresholds as base for empty scaling (reminder: axis swapped)
                        if constData.use_limit_ang_y: za = constData.breaking_threshold
                        if constData.use_limit_ang_z: ya = constData.breaking_threshold
            ### Calculate new scaling from values
            if yl > 0 and zl > 0: aspect = yl /zl
            else: aspect = 1
            if aspect == 1:
                if ya > 0 and za > 0: aspect = ya /za
                else: aspect = 1
            if aspect < 1 and w > 0: aspect = (h /w)
            if aspect > 1 and h > 0: aspect = (w /h)
            if w == 0 or h == 0: aspect = 1  # Can be true if Surface Thickness > 0 is used
            #if aspect >= 1: aspect = (w /h)  # Alternative for CTs without differentiated shearing/bending axis: can lead to flipped orientations
            side = (a /aspect)**.5  # Calculate original dimensions from actual contact area
            side /= 1000  # mm to m
            # New axis scaling
            axs = Vector((0.000001, side *aspect, side))  # Should never be 0 otherwise orientation will be discarded by Blender to Bullet conversion
            # Use standard scaling for drawing of non-directional constraints
            axs_s = Vector((emptyDrawSize, emptyDrawSize, emptyDrawSize))
            ### Add new scale settings for drawing
            constCnt = len(consts)
            idxLast = constCnt -1
            for idx in range(constCnt):
                cIdx = consts[idx]
                objConst = emptyObjs[cIdx]
                if objConst != None:
                    constData = objConst.rigid_body_constraint
                    #objConst.object.empty_draw_type = 'CUBE'  # This is set before duplication for performance reasons
                    objConst.empty_draw_size = .502  # Scale size slightly larger to make lines visible over solid elements
                    if props.disableCollisionPerm and idx == idxLast:  # Use simple if constraint is for permanent collision suppression
                        objConst.scale = axs_s
                    else:
                        # Scale the cube to the dimensions of the connection area
                        if constCnt > 1 and (constData.type == 'GENERIC' or (constData.type == 'GENERIC_SPRING' and constData.enabled)):
                              objConst.scale = axs
                        else: objConst.scale = axs_s
        print()
        
    elif props.asciiExport:

        ### Fill empty constraint list with names of the objects for later use in Postprocessing Tools
        constsData_iter = iter(constsData)
        for k in range(len(emptyObjs)):
            cData, cDatb = next(constsData_iter)
            if cDatb != None:
                if cDatb[0] != None: emptyObjs[k] = cDatb[0]

        ### Export constraint settings
        print("Exporting constraint settings... (%d)" %len(emptyObjs))
        # Data structure of exData is basically an array of empty.rigid_body_constraint (a diff of attributes)
        # together with some BCB specific custom properties which have to be interpreted accordingly.
        exData = []
        constsData_iter = iter(constsData)
        for k in range(len(emptyObjs)):
            sys.stdout.write('\r' +"%d" %k)
            # Update progress bar
            bpy.context.window_manager.progress_update(k /len(emptyObjs))
            
            cData, cDatb = next(constsData_iter)
            ### Prepare data to be packed
            if cDatb != None and objConst != None:
                if cDatb[1] != None: cDatb[1] = cDatb[1].to_tuple()          # loc
                if cDatb[2] != None: cDatb[2] = cDatb[2].name                # obj1
                if cDatb[3] != None: cDatb[3] = cDatb[3].name                # obj2
                if cDatb[6] != None: cDatb[6] = str(cDatb[6])                # rotm
                if cDatb[7] != None: cDatb[7] = Vector(cDatb[7]).to_tuple()  # rot
            exData.append([cData, cDatb])
        print()

        ### Create an extra array based on connection data for optimization purposes (to avoid unnecessary variable access in exporter)
        ### Data that is only used once per connection: obj1, obj2, tol1, tol2
        exPairs = []
        connectsPair_iter = iter(connectsPair)
        connectsConsts_iter = iter(connectsConsts)
        for k in range(len(connectsPair)):
            sys.stdout.write('\r' +"%d" %k)
            consts = next(connectsConsts_iter)
            pair = next(connectsPair_iter)   
            objA = objs[pair[0]]
            objB = objs[pair[1]]
            exPairs.append([objA.name, objB.name, consts])
        print()

        objNames = [obj.name for obj in objs]
        exData = [cDef, exData, exPairs, objNames]
        
    ### Creating reinforcement mesh
    if props.rebarMesh:
        print("Creating reinforcement mesh... (%d)" %len(connectsPair))
        n_minimum = 4  # Minimum reinforcement bars per element (can be changed, sometimes one bar just doesn't look right)
        corner1 = Vector((0, 0, 0))
        corner2 = Vector((0, 0, 0))
        for k in range(len(objs)):
            sys.stdout.write('\r' +"%d" %k)
            # Update progress bar
            bpy.context.window_manager.progress_update(k /len(connectsPair))

            obj = objs[k]
            elemGrp = objsEGrp[objsDict[obj]] 
            elemGrps_elemGrp = elemGrps[elemGrp]
            dims = obj.dimensions /2
            # Compensate BCB rescaling
            scale = elemGrps_elemGrp[EGSidxScal]
            dims = dims /scale

            ### Create mesh data
            verts = []; edges = []; faces = []
            asst = elemGrps_elemGrp[EGSidxAsst]
            # Only try to use FA settings if there is a valid one active
            if asst['ID'] == "con_rei_beam" or asst['ID'] == "con_rei_wall":
                # Get settings from Formula Assistant
                h_def = asst['h']/1000  # Height of element (mm)
                w_def = asst['w']/1000  # Width of element (mm)
                c = asst['c']/1000    # Concrete cover thickness above reinforcement (mm)
                s = asst['s']/1000    # Distance between stirrups (mm)
                ds = asst['ds']/1000  # Diameter of steel stirrup bar (mm)
                dl = asst['dl']/1000  # Diameter of steel longitudinal bar (mm)
                n = asst['n']         # Number of longitudinal steel bars
                
                # Reduce dimension precision by rounding at a specific decimal to avoid arbitrary orientation flipping caused by extremely small float variations
                prec = 10000
                dims = (round(dims[0]*prec)/prec, round(dims[1]*prec)/prec, round(dims[2]*prec)/prec)
                dim = sorted(zip(dims, [0, 1, 2]))
                w = dim[0]   # Use the shortest dimension axis as width
                h = dim[1]   # Use the mid-size dimension axis as height
                l = dim[2]   # Use the largest dimension axis as length
                a_def = h_def *w_def  # Calculate definition contact area
                a = h[0] *w[0]        # Calculate actual contact area
                a_ratio = a /a_def    # Calculate ratio from both
                n = max(round(n *a_ratio), n_minimum)  # Normalize steel bar count to actual contact area of the element with a minimum
                
                ######
                if asst['ID'] == "con_rei_beam":
                    n1 = math.ceil(n /2)  # Divide n by 2 because we assume two rows of irons for beams
                    n2 = int(n /2)  # Use floor() here to take also odd n numbers into account
                    ### Longitudinal bars
                    if n > 1:  # Only do two layers (top and bottom for h bars) for more than 1 bar
                        for j in range(2):
                            if j == 0: nu = n2  # Special handling for odd n numbers,
                            else:      nu = n1  # then both numbers can be different
                            if nu > 1:  # Multiple w bars
                                for i in range(nu):
                                    jm = j*2-1  # Calculate multiplier for height (0 => -1, 1 => 1)
                                    corner1[h[1]] = jm *(h[0]-c) -dl/2
                                    corner1[w[1]] = i *((w[0]-c)*2/(nu-1)) -(w[0]-c) -dl/2
                                    corner1[l[1]] = -l[0]
                                    corner2[h[1]] = jm *(h[0]-c) +dl/2
                                    corner2[w[1]] = i *((w[0]-c)*2/(nu-1)) -(w[0]-c) +dl/2
                                    corner2[l[1]] = l[0]
                                    createBoxData(verts, edges, faces, corner1, corner2)
                            else:  # Only one w bar
                                    jm = j*2-1  # Calculate multiplier for height (0 => -1, 1 => 1)
                                    corner1[h[1]] = jm *(h[0]-c) -dl/2
                                    corner1[w[1]] = -dl/2
                                    corner1[l[1]] = -l[0]
                                    corner2[h[1]] = jm *(h[0]-c) +dl/2
                                    corner2[w[1]] = dl/2
                                    corner2[l[1]] = l[0]
                                    createBoxData(verts, edges, faces, corner1, corner2)                            
                    else:  # Only one h bar
                            corner1[h[1]] = -dl/2
                            corner1[w[1]] = -dl/2
                            corner1[l[1]] = -l[0]
                            corner2[h[1]] = dl/2
                            corner2[w[1]] = dl/2
                            corner2[l[1]] = l[0]
                            createBoxData(verts, edges, faces, corner1, corner2)                            
                    ### Stirrups
                    if n > 1:
                        qReverse = 0
                        pos = 0  # Start at center of element for first stirrup
                        while pos >= -(l[0]-c):
                            # h positive
                            corner1[h[1]] = (h[0]-c) +dl/2
                            corner1[w[1]] = -(w[0]-c) -ds -dl/2
                            corner1[l[1]] = pos -ds/2
                            corner2[h[1]] = (h[0]-c) +ds +dl/2
                            corner2[w[1]] = (w[0]-c) +ds +dl/2
                            corner2[l[1]] = pos +ds/2
                            createBoxData(verts, edges, faces, corner1, corner2)
                            # h negative
                            corner1[h[1]] = -(h[0]-c) -ds -dl/2
                            corner1[w[1]] = -(w[0]-c) -ds -dl/2
                            corner1[l[1]] = pos -ds/2
                            corner2[h[1]] = -(h[0]-c) -dl/2
                            corner2[w[1]] = (w[0]-c) +ds +dl/2
                            corner2[l[1]] = pos +ds/2
                            createBoxData(verts, edges, faces, corner1, corner2)
                            # w positive
                            corner1[h[1]] = -(h[0]-c) -dl/2
                            corner1[w[1]] = (w[0]-c) +dl/2
                            corner1[l[1]] = pos -ds/2
                            corner2[h[1]] = (h[0]-c) +dl/2
                            corner2[w[1]] = (w[0]-c) +ds +dl/2
                            corner2[l[1]] = pos +ds/2
                            createBoxData(verts, edges, faces, corner1, corner2)
                            # w negative
                            corner1[h[1]] = -(h[0]-c) -dl/2
                            corner1[w[1]] = -(w[0]-c) -ds -dl/2
                            corner1[l[1]] = pos -ds/2
                            corner2[h[1]] = (h[0]-c) +dl/2
                            corner2[w[1]] = -(w[0]-c) -dl/2
                            corner2[l[1]] = pos +ds/2
                            createBoxData(verts, edges, faces, corner1, corner2)
                            if not qReverse:
                                pos += s
                                if pos > l[0]-c:  # Reverse direction and start again from center after reaching edge of element
                                    pos = -s; qReverse = 1
                            else: pos -= s
                ######    
                elif asst['ID'] == "con_rei_wall":
                    if n > 1:
                        step = ((h[0]-c)*2/(n-1))
                        qReverse = 0
                        pos = 0  # Start at center of element for first bar
                        while pos >= -(h[0]-c):
                            corner1[h[1]] = pos -dl/2
                            corner1[w[1]] = -dl
                            corner1[l[1]] = -l[0]
                            corner2[h[1]] = pos +dl/2
                            corner2[w[1]] = 0
                            corner2[l[1]] = l[0]
                            createBoxData(verts, edges, faces, corner1, corner2)
                            if not qReverse:
                                pos += step
                                if pos > h[0]-c:  # Reverse direction and start again from center after reaching edge of element
                                    pos = -step; qReverse = 1
                            else: pos -= step
                        # h and l swapped:
                        qReverse = 0
                        pos = 0  # Start at center of element for first bar
                        while pos >= -(l[0]-c):
                            corner1[h[1]] = -h[0]
                            corner1[w[1]] = 0
                            corner1[l[1]] = pos -dl/2
                            corner2[h[1]] = h[0]
                            corner2[w[1]] = dl
                            corner2[l[1]] = pos +dl/2
                            createBoxData(verts, edges, faces, corner1, corner2)
                            if not qReverse:
                                pos += step
                                if pos > l[0]-c:  # Reverse direction and start again from center after reaching edge of element
                                    pos = -step; qReverse = 1
                            else: pos -= step
                    else:  # Only one h bar
                            corner1[h[1]] = -dl/2
                            corner1[w[1]] = -dl/2
                            corner1[l[1]] = -l[0]
                            corner2[h[1]] = dl/2
                            corner2[w[1]] = dl/2
                            corner2[l[1]] = l[0]
                            createBoxData(verts, edges, faces, corner1, corner2)                            

                ### Create actual mesh object from data
                if len(verts) > 0:
                    objN = createOrReuseObjectAndMesh(scene, objName=obj.name +'_R')
                    meN = objN.data
                    # Create final mesh from lists
                    meN.from_pydata(verts, edges, faces)
                    # Copy original transforms to new object
                    objN.matrix_world = obj.matrix_world
                    # Deselect to prevent inclusion in building process
                    objN.select = 0
                    
                    # Add to group
                    grpReinfName = "BCB_Reinforcement"
                    try: grp = bpy.data.groups[grpReinfName]
                    except: grp = bpy.data.groups.new(grpReinfName)
                    try: grp.objects.link(objN)
                    except: pass
                    ### Link new object to every group the original is linked to except for grpNameBuilding and RBW,
                    ### the latter because FM-Blender seems to enable RBs automatically for objects which are parts of this group
                    for grp in bpy.data.groups:
                        if grp.name != grpNameBuilding and grp.name != "RigidBodyWorld":
                            for objG in grp.objects:
                                if objG.name == obj.name:
                                    try: grp.objects.link(objN)
                                    except: pass

        print()
        
    return connectsTol, exData
