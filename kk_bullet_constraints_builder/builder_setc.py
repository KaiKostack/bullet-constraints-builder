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

import bpy, mathutils, sys
from mathutils import Vector
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *          # Contains file input & output functions

################################################################################

def addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsConsts, connectsLoc, constsConnect, exData):
    
    ### Add base constraint settings to empties
    print("Adding base constraint settings to empties... (%d)" %len(emptyObjs))
    
    props = bpy.context.window_manager.bcb

    ### Add further settings
    for k in range(len(emptyObjs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(emptyObjs))

        l = constsConnect[k]
        if not props.asciiExport:
            objConst = emptyObjs[k]
            objConst.location = connectsLoc[l]
            objConst.rigid_body_constraint.object1 = objs[connectsPair[l][0]]
            objConst.rigid_body_constraint.object2 = objs[connectsPair[l][1]]
        else:
            export(exData, loc=connectsLoc[l].to_tuple(), obj1=objs[connectsPair[l][0]].name, obj2=objs[connectsPair[l][1]].name)
              
    ### Naming of the constraints according to their connection participation
    for k in range(len(connectsPair)):
        i = 1
        for cIdx in connectsConsts[k]:
            name = "Con.%03d.%d" %(k, i)
            if not props.asciiExport: emptyObjs[cIdx].name = name
            else:               export(exData, idx=cIdx, name=name)
            i += 1
            
    print()
                
################################################################################

def setConstParams(objConst, axs=None,e=None,bt=None,ub=None,dc=None,ct=None,
    ullx=None,ully=None,ullz=None, llxl=None,llxu=None,llyl=None,llyu=None,llzl=None,llzu=None,
    ulax=None,ulay=None,ulaz=None, laxl=None,laxu=None,layl=None,layu=None,lazl=None,lazu=None,
    usx=None,usy=None,usz=None, sdx=None,sdy=None,sdz=None, ssx=None,ssy=None,ssz=None):

    # setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)

    constData = objConst.rigid_body_constraint
    
    # Draw size
    #objConst.object.empty_draw_type = 'CUBE'  # This is set before duplication for performance reasons
    if axs != None:
        objConst.empty_draw_size = .502  # Scale size slightly larger to make lines visible over solid elements
        objConst.scale = axs  # Scale the cube to the dimensions of the connection area

    # s,e,bt,ub,dc,ct
    if e != None: constData.enabled = e
    if bt != None: constData.breaking_threshold = bt
    if ub != None: constData.use_breaking = ub
    if dc != None: constData.disable_collisions = dc
    if ct != None: constData.type = ct

    # Limits Linear
    # ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu
    if ullx != None: constData.use_limit_lin_x = ullx
    if ully != None: constData.use_limit_lin_y = ully
    if ullz != None: constData.use_limit_lin_z = ullz
    if llxl != None: constData.limit_lin_x_lower = llxl
    if llxu != None: constData.limit_lin_x_upper = llxu
    if llyl != None: constData.limit_lin_y_lower = llyl
    if llyu != None: constData.limit_lin_y_upper = llyu
    if llzl != None: constData.limit_lin_z_lower = llzl
    if llzu != None: constData.limit_lin_z_upper = llzu

    # Limits Angular
    # ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu
    if ulax != None: constData.use_limit_ang_x = ulax
    if ulay != None: constData.use_limit_ang_y = ulay
    if ulaz != None: constData.use_limit_ang_z = ulaz
    if laxl != None: constData.limit_ang_x_lower = laxl
    if laxu != None: constData.limit_ang_x_upper = laxu
    if layl != None: constData.limit_ang_y_lower = layl
    if layu != None: constData.limit_ang_y_upper = layu
    if lazl != None: constData.limit_ang_z_lower = lazl
    if lazu != None: constData.limit_ang_z_upper = lazu

    # Spring
    # usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz
    if usx != None: constData.use_spring_x = usx
    if usy != None: constData.use_spring_y = usy
    if usz != None: constData.use_spring_z = usz
    if sdx != None: constData.spring_damping_x = sdx
    if sdy != None: constData.spring_damping_y = sdy
    if sdz != None: constData.spring_damping_z = sdz
    if ssx != None: constData.spring_stiffness_x = ssx
    if ssy != None: constData.spring_stiffness_y = ssy
    if ssz != None: constData.spring_stiffness_z = ssz

########################################
    
def setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsGeo, connectsConsts, constsConnect, exData):
    
    ### Set constraint settings
    print("Adding main constraint settings... (%d)" %len(connectsPair))
    
    props = bpy.context.window_manager.bcb
    scene = bpy.context.scene
    elemGrps = mem["elemGrps"]
    
    if props.asciiExport:
        ### Create temporary empty object (will only be used for exporting constraint settings)
        objConst = bpy.data.objects.new('Constraint', None)
        bpy.context.scene.objects.link(objConst)
        objConst.empty_draw_type = 'SPHERE'
        bpy.context.scene.objects.active = objConst
        bpy.ops.rigidbody.constraint_add()
        constSettingsBak = getAttribsOfConstraint(objConst)

    count = 0
    for k in range(len(connectsPair)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(connectsPair))
        
        consts = connectsConsts[k]
        # Geometry array: [area, height, width, surfThick, axisNormal, axisHeight, axisWidth]
        # Height is always smaller than width
        geoContactArea = connectsGeo[k][0]
        geoHeight = connectsGeo[k][1]
        geoWidth = connectsGeo[k][2]
        geoSurfThick = connectsGeo[k][3]
        geoAxisNormal = connectsGeo[k][4]
        geoAxisHeight = connectsGeo[k][5]
        geoAxisWidth = connectsGeo[k][6]
        ax = [geoAxisNormal, geoAxisHeight, geoAxisWidth]

        ### Postponed geoContactArea calculation step from calculateContactAreaBasedOnBoundaryBoxesForPair() is being done now (update hack, could be better organized)
        if props.useAccurateArea:
            if geoSurfThick > 0:
                geoContactArea *= geoSurfThick

        ### Prepare expression variables and convert m to mm
        a = geoContactArea *1000000
        h = geoHeight *1000
        w = geoWidth *1000
        s = geoSurfThick *1000
                
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        elemGrpA = objsEGrp[objs.index(objA)]
        elemGrpB = objsEGrp[objs.index(objB)]
        _elemGrps_elemGrpA = elemGrps[elemGrpA]
        _elemGrps_elemGrpB = elemGrps[elemGrpB]

        ###### Decision of which material settings from both groups will be used for connection

        CT_A = _elemGrps_elemGrpA[EGSidxCTyp]
        CT_B = _elemGrps_elemGrpB[EGSidxCTyp]

        # A is active group
        if CT_A != 0:
            ### Prepare expression strings
            brkThresExprC_A = _elemGrps_elemGrpA[EGSidxBTC]
            brkThresExprT_A = _elemGrps_elemGrpA[EGSidxBTT]
            brkThresExprS_A = _elemGrps_elemGrpA[EGSidxBTS]
            brkThresExprS9_A = _elemGrps_elemGrpA[EGSidxBTS9]
            brkThresExprB_A = _elemGrps_elemGrpA[EGSidxBTB]
            brkThresExprB9_A = _elemGrps_elemGrpA[EGSidxBTB9]
            ### Add surface variable
            if len(brkThresExprC_A): brkThresExprC_A += "*a"
            if len(brkThresExprT_A): brkThresExprT_A += "*a"
            if len(brkThresExprS_A): brkThresExprS_A += "*a"
            if len(brkThresExprS9_A): brkThresExprS9_A += "*a"
            if len(brkThresExprB_A): brkThresExprB_A += "*a"
            if len(brkThresExprB9_A): brkThresExprB9_A += "*a"

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

        # B is active group
        if CT_B != 0:
            ### Prepare expression strings
            brkThresExprC_B = _elemGrps_elemGrpB[EGSidxBTC]
            brkThresExprT_B = _elemGrps_elemGrpB[EGSidxBTT]
            brkThresExprS_B = _elemGrps_elemGrpB[EGSidxBTS]
            brkThresExprS9_B = _elemGrps_elemGrpB[EGSidxBTS9]
            brkThresExprB_B = _elemGrps_elemGrpB[EGSidxBTB]
            brkThresExprB9_B = _elemGrps_elemGrpB[EGSidxBTB9]
            ### Add surface variable
            if len(brkThresExprC_B): brkThresExprC_B += "*a"
            if len(brkThresExprT_B): brkThresExprT_B += "*a"
            if len(brkThresExprS_B): brkThresExprS_B += "*a"
            if len(brkThresExprS9_B): brkThresExprS9_B += "*a"
            if len(brkThresExprB_B): brkThresExprB_B += "*a"
            if len(brkThresExprB9_B): brkThresExprB9_B += "*a"

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

        # Both A and B are active groups
        if CT_A != 0 and CT_B != 0:
            # Area correction calculation for cylinders (*pi/4)
            if _elemGrps_elemGrpA[EGSidxCyln] or _elemGrps_elemGrpB[EGSidxCyln]: a *= 0.7854

            ### Use the connection type with the smaller count of constraints for connection between different element groups
            ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
            if connectTypes[_elemGrps_elemGrpA[EGSidxCTyp]][1] <= connectTypes[_elemGrps_elemGrpB[EGSidxCTyp]][1]:
                CT = CT_A
                elemGrp = elemGrpA
            else:
                CT = CT_B
                elemGrp = elemGrpB
                        
            if props.lowerBrkThresPriority:
                ### Use the weaker of both breaking thresholds for every degree of freedom
                if brkThresValueC_A <= brkThresValueC_B: brkThresValueC = brkThresValueC_A
                else:                                  brkThresValueC = brkThresValueC_B

                if brkThresValueT_A <= brkThresValueT_B: brkThresValueT = brkThresValueT_A
                else:                                  brkThresValueT = brkThresValueT_B

                if brkThresValueS_A <= brkThresValueS_B: brkThresValueS = brkThresValueS_A
                else:                                  brkThresValueS = brkThresValueS_B

                if brkThresValueS9_A == -1 or brkThresValueS9_B == -1: brkThresValueS9 = -1
                else:    
                    if brkThresValueS9_A <= brkThresValueS9_B: brkThresValueS9 = brkThresValueS9_A
                    else:                                    brkThresValueS9 = brkThresValueS9_B

                if brkThresValueB_A <= brkThresValueB_B: brkThresValueB = brkThresValueB_A
                else:                                  brkThresValueB = brkThresValueB_B

                if brkThresValueB9_A == -1 or brkThresValueB9_B == -1: brkThresValueB9 = -1
                else:    
                    if brkThresValueB9_A <= brkThresValueB9_B: brkThresValueB9 = brkThresValueB9_A
                    else:                                    brkThresValueB9 = brkThresValueB9_B
            else:
                ### Use the stronger of both breaking thresholds for every degree of freedom
                if brkThresValueC_A > brkThresValueC_B: brkThresValueC = brkThresValueC_A
                else:                                  brkThresValueC = brkThresValueC_B

                if brkThresValueT_A > brkThresValueT_B: brkThresValueT = brkThresValueT_A
                else:                                  brkThresValueT = brkThresValueT_B

                if brkThresValueS_A > brkThresValueS_B: brkThresValueS = brkThresValueS_A
                else:                                  brkThresValueS = brkThresValueS_B

                if brkThresValueS9_A == -1 or brkThresValueS9_B == -1: brkThresValueS9 = -1
                else:    
                    if brkThresValueS9_A > brkThresValueS9_B: brkThresValueS9 = brkThresValueS9_A
                    else:                                    brkThresValueS9 = brkThresValueS9_B

                if brkThresValueB_A > brkThresValueB_B: brkThresValueB = brkThresValueB_A
                else:                                  brkThresValueB = brkThresValueB_B

                if brkThresValueB9_A == -1 or brkThresValueB9_B == -1: brkThresValueB9 = -1
                else:    
                    if brkThresValueB9_A > brkThresValueB9_B: brkThresValueB9 = brkThresValueB9_A
                    else:                                    brkThresValueB9 = brkThresValueB9_B
            
        # Only A is active and B is passive group
        elif CT_A != 0 and CT_B == 0:
            # Area correction calculation for cylinders (*pi/4)
            if _elemGrps_elemGrpA[EGSidxCyln]: a *= 0.7854
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
 
        # Only B is active and A is passive group
        elif CT_A == 0 and CT_B != 0:
            # Area correction calculation for cylinders (*pi/4)
            if _elemGrps_elemGrpB[EGSidxCyln]: a *= 0.7854
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

        # Both A and B are passive groups
        elif CT_A == 0 and CT_B == 0:
            CT = 0            

        ######
        
        if CT > 0:
            _elemGrps_elemGrp = elemGrps[elemGrp]

            springStiff = _elemGrps_elemGrp[EGSidxSStf]

            if not props.asciiExport:
                # Store value as ID property for debug purposes
                for idx in consts: emptyObjs[idx]['ContactArea'] = geoContactArea
                ### Check if full update is necessary (optimization)
                objConst0 = emptyObjs[consts[0]]
                if 'ConnectType' in objConst0.keys() and objConst0['ConnectType'] == CT: qUpdateComplete = 0
                else: objConst0['ConnectType'] = CT; qUpdateComplete = 1
            else:
                tol1dist = _elemGrps_elemGrp[EGSidxTl1D]
                tol1rot = _elemGrps_elemGrp[EGSidxTl1R]
                tol2dist = _elemGrps_elemGrp[EGSidxTl2D]
                tol2rot = _elemGrps_elemGrp[EGSidxTl2R]

                objConst0 = objConst
                qUpdateComplete = 1
                objConst.rotation_mode = 'XYZ'  # Overwrite temporary object to default (Euler)
                
                cIdx = consts[0]
                objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                # This is not nice as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
            centerLoc = objConst0.location.copy()

            ### Calculate orientation between the two elements
            # Center to center orientation
            dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
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
                    
        ### Set constraints by connection type preset
        ### Also convert real world breaking threshold to bullet breaking threshold and take simulation steps into account (Threshold = F / Steps)
        # Overview:

        # Basic CTs:
        #   if CT == 1 or CT == 9 or CT == 10:
        #       1x FIXED; Linear omni-directional + bending breaking threshold
        #   if CT == 2:
        #       1x POINT; Linear omni-directional breaking threshold
        #   if CT == 3:
        #       1x POINT + 1x FIXED; Linear omni-directional, bending breaking thresholds

        # Compressive:
        #   if CT == 4 or CT == 5 or CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
        #       1x GENERIC; Compressive threshold

        # Tensile + Shearing:
        #   if CT == 4:
        #       1x GENERIC; Tensile + bending (3D)
        #   if CT == 5:
        #       2x GENERIC; Tensile + shearing (3D), bending (3D) breaking thresholds
        #   if CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
        #       3x GENERIC; Tensile constraint (1D) breaking thresholds
        #   if CT == 6 or CT == 11 or CT == 12:
        #       1x GENERIC; Shearing (2D), bending (2D) breaking thresholds
        #   if CT == 15 or CT == 16 or CT == 17 or CT == 18:
        #       2x GENERIC; Shearing (1D) breaking thresholds
        #   if CT == 15 or CT == 17:
        #       2x GENERIC; Bending + torsion (1D) breaking thresholds
        #   if CT == 16 or CT == 18:
        #       3x GENERIC; Bending (1D), torsion (1D) breaking thresholds
        
        # Springs (additional):
        #   if CT == 7 or CT == 9 or CT == 11 or CT == 17 or CT == 18:
        #       3x SPRING; Circular placed for plastic deformability
        #   if CT == 8 or CT == 10 or CT == 12:
        #       4x SPRING; Circular placed for plastic deformability
        
        # Springs only CTs
        #   if CT == 13:
        #       3 x 3x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        #   if CT == 14:
        #       3 x 4x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
            
        cInc = 0

        ### 1x FIXED; Linear omni-directional + bending breaking threshold
        if CT == 1 or CT == 9 or CT == 10:
            correction = 1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='FIXED')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
                
        ### 1x POINT; Linear omni-directional breaking threshold
        if CT == 2:
            correction = 1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='POINT')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
        
        ### 1x POINT + 1x FIXED; Linear omni-directional, bending breaking thresholds    
        if CT == 3:
            correction = 1 /2   # As both constraints bear all load and forces are evenly distributed among them the breaking thresholds need to be divided by their count to compensate

            ### First constraint
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='POINT')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Second constraint
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueB
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision, ct='FIXED')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
        
        ### 1x GENERIC; Compressive threshold
        if CT == 4 or CT == 5 or CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
            ### First constraint
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock all directions for the compressive force
                ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                ### Also rotational forces should only be carried by the tensile constraint
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=0,llxu=99999, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation to that vector
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 1x GENERIC; Tensile (3D)
        if CT == 4:
            ### Second constraint
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock all directions for the tensile force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=0,llyl=0,llyu=0,llzl=0,llzu=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 2x GENERIC; Tensile + shearing (3D), bending (3D) breaking thresholds
        if CT == 5:
            ### Tensile + shearing constraint (3D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for shearing force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=0,llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending constraint (3D)
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueS
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for bending force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 3x GENERIC; Tensile constraint (1D) breaking threshold
        if CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
            ### Tensile constraint (1D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock direction for tensile force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 3x GENERIC; Shearing constraint (2D), bending constraint (3D) breaking thresholds
        if CT == 6 or CT == 11 or CT == 12:
            ### Shearing constraint (2D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueS
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for shearing force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=1,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending constraint (3D)
            correction = 1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueB
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for bending force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 2x GENERIC; Shearing (1D) breaking thresholds
        if CT == 15 or CT == 16 or CT == 17 or CT == 18:
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            ### Shearing constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueS
            if brkThresValueS9 != -1:
                value1 = value
                value = brkThresValueS9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = objConst.rotation_quaternion.to_matrix().inverted()
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
                    dirEul = dirVec.to_track_quat('X','Z').to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 2:   setConstParams(objConst, ct='GENERIC', ully=1,ullz=0, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
                elif constAxisToLock == 3: setConstParams(objConst, ct='GENERIC', ully=0,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Shearing constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresValueS9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ully=1,ullz=0, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ully=0,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 2x GENERIC; Bending + torsion (1D) breaking thresholds
        if CT == 15 or CT == 17:
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library

            ### Bending with torsion constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueB
            if brkThresValueB9 != -1:
                value1 = value
                value = brkThresValueB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = objConst.rotation_quaternion.to_matrix().inverted()
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
                    dirEul = dirVec.to_track_quat('X','Z').to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 2:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 3: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending with torsion constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresValueB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 3x GENERIC; Bending (1D), torsion (1D) breaking thresholds
        if CT == 16 or CT == 18:
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library

            ### Bending without torsion constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresValueB
            if brkThresValueB9 != -1:
                value1 = value
                value = brkThresValueB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Find constraint axis which is closest to the height (h) orientation of the detected contact area  
                matInv = objConst.rotation_quaternion.to_matrix().inverted()
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
                    dirEul = dirVec.to_track_quat('X','Z').to_euler()
                    if abs(dirEul[1]) > abs(dirEul[2]): constAxisToLock = 3
                    else: constAxisToLock = 2
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 2:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 3: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending without torsion constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresValueB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Torsion constraint
            cIdx = consts[cInc]; cInc += 1
            if not props.asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings

            try: value = values[0]  # Use the smaller value from either standard or 90n° bending thresholds as base for torsion
            except: pass
            value *= .5  # Use 50% of the bending thresholds for torsion (we really need a formula for that)

#            value = brkThresValueS
#            if brkThresValueS9 != -1:
#                value1 = value
#                value = brkThresValueS9
#                value2 = value
#                values = [value1, value2]
#                values.sort()
#                value = values[0]  # Find and use smaller value (to be used along h axis)
#            value /= 2  # Use half of the smaller shearing breaking thresholds for torsion

            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if props.asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, rot=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ###### Springs (additional)

        ### 3x SPRING; Circular placed for plastic deformability
        if CT == 7 or CT == 9 or CT == 11 or CT == 17 or CT == 18:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ### Loop through all constraints of this connection
            for i in range(3):
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   i == 0: vec = Vector((0, radius, radius))
                    elif i == 1: vec = Vector((0, radius, -radius))
                    elif i == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                if CT != 7:
                    # Disable springs on start (requires plastic activation during simulation)
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, e=0)
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    if CT == 7:
                           export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])
                    else:  export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC_OFF", tol2dist, tol2rot])
                
        ### 4x SPRING; Circular placed for plastic deformability
        if CT == 8 or CT == 10 or CT == 12:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresValueC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ### Loop through all constraints of this connection
            for i in range(4):
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   i == 0: vec = Vector((0, radius, radius))
                    elif i == 1: vec = Vector((0, radius, -radius))
                    elif i == 2: vec = Vector((0, -radius, -radius))
                    elif i == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                if CT != 8:
                    # Disable springs on start (requires plastic activation during simulation)
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, e=0)
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    if CT == 8:
                           export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])
                    else:  export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC_OFF", tol2dist, tol2rot])
                
        ###### Springs only CTs

        ### 3 x 3x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 13:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresValueC
            brkThres1 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresValueT
            brkThres2 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresValueS
            brkThres3 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # Loop through all constraints of this connection
            for j in range(3):

                ### First constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres1, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock direction for compressive force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=0,llxu=99999, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation to that vector
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Second constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres2, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock direction for tensile force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=0, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Third constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres3, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, 0))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock directions for shearing force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=0,ully=1,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

        ### 3 x 4x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 14:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresValueC
            brkThres1 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresValueT
            brkThres2 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresValueS
            brkThres3 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # Loop through all constraints of this connection
            for j in range(4):

                ### First constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres1, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock direction for compressive force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=0,llxu=99999, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation to that vector
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Second constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres2, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock direction for tensile force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=0, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Third constraint
                cIdx = consts[cInc]; cInc += 1
                if not props.asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if props.asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres3, ub=props.constraintUseBreaking, dc=props.disableCollision)
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    ### Rotate constraint matrix
                    if   j == 0: vec = Vector((0, radius, radius))
                    elif j == 1: vec = Vector((0, radius, -radius))
                    elif j == 2: vec = Vector((0, -radius, -radius))
                    elif j == 3: vec = Vector((0, -radius, radius))
                    vec.rotate(objConst.rotation_quaternion)
                    objConst.location = centerLoc +vec
                    ### Lock directions for shearing force and enable linear spring
                    ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                    setConstParams(objConst, ct='GENERIC_SPRING', ullx=0,ully=1,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0, usx=1,usy=1,usz=1, sdx=1,sdy=1,sdz=1)
                # Set stiffness
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ssx=springStiff,ssy=springStiff,ssz=springStiff)
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if props.asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, rot=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

        if not props.asciiExport:
            if CT > 3:
                ### Calculate settings for drawing of directional constraints
                yl = 0; zl = 0; ya = 0; za = 0
                for cIdx in consts:
                    constData = emptyObjs[cIdx].rigid_body_constraint
                    if constData.type == 'GENERIC' or constData.type == 'GENERIC_SPRING':
                        # Use shearing thresholds as base for empty scaling
                        if constData.use_limit_lin_y: yl = constData.breaking_threshold
                        if constData.use_limit_lin_z: zl = constData.breaking_threshold
                        # Use bending thresholds as base for empty scaling (reminder: axis swapped)
                        if constData.use_limit_ang_y: za = constData.breaking_threshold
                        if constData.use_limit_ang_z: ya = constData.breaking_threshold
                if yl > 0 and zl > 0: aspect = yl /zl
                else: aspect = 1
                if aspect == 1:
                    if ya > 0 and za > 0: aspect = ya /za
                    else: aspect = 1
                if aspect < 1: aspect = (h /w)
                if aspect > 1: aspect = (w /h)
                #if aspect >= 1: aspect = (w /h)  # Alternative for CTs without differentiated shearing/bending axis: can lead to flipped orientations
                side = (a /aspect)**.5  # Calculate original dimensions from actual contact area
                side /= 1000  # mm to m
                axs = Vector((0.000001, side *aspect, side))  # Should never be 0 otherwise orientation will be discarded by Blender to Bullet conversion
            else:
                # Use standard size for drawing of non-directional constraints
                axs = Vector((emptyDrawSize, emptyDrawSize, emptyDrawSize))
            # Add settings for drawing    
            for cIdx in consts:
                objConst = emptyObjs[cIdx]
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, axs=axs)

    if props.asciiExport:
        # Remove constraint settings from temporary empty object
        bpy.ops.rigidbody.constraint_remove()
        # Delete temporary empty object
        scene.objects.unlink(objConst)
        
    print()
