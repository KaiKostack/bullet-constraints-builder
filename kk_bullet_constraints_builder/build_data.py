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

import bpy, time
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from file_io import *          # Contains file input & output functions

################################################################################

def storeConfigDataInScene(scene):

    ### Store menu config data in scene
    print("Storing menu config data in scene...")
    
    props = bpy.context.window_manager.bcb
    scene["bcb_version"] = bcb_version

    ### Preprocessing Tools
    scene["bcb_prop_preprocTools_aut"] = props.preprocTools_aut

    scene["bcb_prop_preprocTools_rps"] = props.preprocTools_rps
    scene["bcb_prop_preprocTools_rps_nam"] = props.preprocTools_rps_nam

    scene["bcb_prop_preprocTools_grp"] = props.preprocTools_grp
    scene["bcb_prop_preprocTools_grp_sep"] = props.preprocTools_grp_sep
    scene["bcb_prop_preprocTools_grp_occ"] = props.preprocTools_grp_occ

    scene["bcb_prop_preprocTools_mod"] = props.preprocTools_mod

    scene["bcb_prop_preprocTools_ctr"] = props.preprocTools_ctr

    scene["bcb_prop_preprocTools_sep"] = props.preprocTools_sep

    scene["bcb_prop_preprocTools_dis"] = props.preprocTools_dis
    scene["bcb_prop_preprocTools_dis_siz"] = props.preprocTools_dis_siz
    scene["bcb_prop_preprocTools_dis_cel"] = props.preprocTools_dis_cel
    scene["bcb_prop_preprocTools_dis_jus"] = props.preprocTools_dis_jus

    scene["bcb_prop_preprocTools_rbs"] = props.preprocTools_rbs

    scene["bcb_prop_preprocTools_int"] = props.preprocTools_int
    scene["bcb_prop_preprocTools_int_bol"] = props.preprocTools_int_bol

    scene["bcb_prop_preprocTools_fix"] = props.preprocTools_fix
    scene["bcb_prop_preprocTools_fix_nam"] = props.preprocTools_fix_nam
    scene["bcb_prop_preprocTools_fix_cac"] = props.preprocTools_fix_cac
    scene["bcb_prop_preprocTools_fix_rng"] = props.preprocTools_fix_rng
    scene["bcb_prop_preprocTools_fix_axp"] = props.preprocTools_fix_axp
    scene["bcb_prop_preprocTools_fix_axn"] = props.preprocTools_fix_axn
    scene["bcb_prop_preprocTools_fix_ayp"] = props.preprocTools_fix_ayp
    scene["bcb_prop_preprocTools_fix_ayn"] = props.preprocTools_fix_ayn
    scene["bcb_prop_preprocTools_fix_azp"] = props.preprocTools_fix_azp
    scene["bcb_prop_preprocTools_fix_azn"] = props.preprocTools_fix_azn

    scene["bcb_prop_preprocTools_gnd"] = props.preprocTools_gnd
    scene["bcb_prop_preprocTools_gnd_obj"] = props.preprocTools_gnd_obj
    scene["bcb_prop_preprocTools_gnd_obm"] = props.preprocTools_gnd_obm
    scene["bcb_prop_preprocTools_gnd_nac"] = props.preprocTools_gnd_nac
    scene["bcb_prop_preprocTools_gnd_nap"] = props.preprocTools_gnd_nap
    scene["bcb_prop_preprocTools_gnd_nfq"] = props.preprocTools_gnd_nfq
    scene["bcb_prop_preprocTools_gnd_ndu"] = props.preprocTools_gnd_ndu
    scene["bcb_prop_preprocTools_gnd_nsd"] = props.preprocTools_gnd_nsd
    scene["bcb_prop_preprocTools_gnd_nam"] = props.preprocTools_gnd_nam

    ### Postprocessing Tools
    scene["bcb_prop_postprocTools_aut"] = props.postprocTools_aut

    scene["bcb_prop_postprocTools_lox"] = props.postprocTools_lox
    scene["bcb_prop_postprocTools_lox_elm"] = props.postprocTools_lox_elm
    scene["bcb_prop_postprocTools_lox_nam"] = props.postprocTools_lox_nam

    scene["bcb_prop_postprocTools_fcx"] = props.postprocTools_fcx
    scene["bcb_prop_postprocTools_fcx_con"] = props.postprocTools_fcx_con
    scene["bcb_prop_postprocTools_fcx_nam"] = props.postprocTools_fcx_nam

    scene["bcb_prop_postprocTools_fcv"] = props.postprocTools_fcv
    scene["bcb_prop_postprocTools_fcv_con"] = props.postprocTools_fcv_con
    scene["bcb_prop_postprocTools_fcv_frm"] = props.postprocTools_fcv_frm
    scene["bcb_prop_postprocTools_fcv_nbt"] = props.postprocTools_fcv_nbt
    scene["bcb_prop_postprocTools_fcv_max"] = props.postprocTools_fcv_max
    scene["bcb_prop_postprocTools_fcv_pas"] = props.postprocTools_fcv_pas

    scene["bcb_prop_postprocTools_cav"] = props.postprocTools_cav
    scene["bcb_prop_postprocTools_cav_siz"] = props.postprocTools_cav_siz

    scene["bcb_prop_postprocTools_rps"] = props.postprocTools_rps
    scene["bcb_prop_postprocTools_rps_nam"] = props.postprocTools_rps_nam
    
    ### General
    scene["bcb_prop_stepsPerSecond"] = props.stepsPerSecond
    scene["bcb_prop_constraintUseBreaking"] = props.constraintUseBreaking
    scene["bcb_prop_passiveUseBreaking"] = props.passiveUseBreaking
    scene["bcb_prop_connectionCountLimit"] = props.connectionCountLimit
    scene["bcb_prop_searchDistance"] = props.searchDistance
    scene["bcb_prop_clusterRadius"] = props.clusterRadius
    scene["bcb_prop_alignVertical"] = props.alignVertical
    scene["bcb_prop_useAccurateArea"] = props.useAccurateArea 
    scene["bcb_prop_rebarMesh"] = props.rebarMesh
    scene["bcb_prop_surfaceThickness"] = props.surfaceThickness 
    scene["bcb_prop_surfaceForced"] = props.surfaceForced 
    scene["bcb_prop_minimumElementSize"] = props.minimumElementSize 
    scene["bcb_prop_automaticMode"] = props.automaticMode 
    scene["bcb_prop_saveBackups"] = props.saveBackups 
    scene["bcb_prop_timeScalePeriod"] = props.timeScalePeriod
    scene["bcb_prop_timeScalePeriodValue"] = props.timeScalePeriodValue 
    scene["bcb_prop_warmUpPeriod"] = props.warmUpPeriod
    scene["bcb_prop_progrWeak"] = props.progrWeak
    scene["bcb_prop_progrWeakLimit"] = props.progrWeakLimit
    scene["bcb_prop_progrWeakStartFact"] = props.progrWeakStartFact
    scene["bcb_prop_snapToAreaOrient"] = props.snapToAreaOrient
    scene["bcb_prop_disableCollision"] = props.disableCollision
    scene["bcb_prop_disableCollisionPerm"] = props.disableCollisionPerm
    scene["bcb_prop_lowerBrkThresPriority"] = props.lowerBrkThresPriority
    scene["bcb_prop_detonatorObj"] = props.detonatorObj
    
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    elemGrps = mem["elemGrps"]
    elemGrpsInverted = []
    for i in range(len(presets[0])):
        column = []
        for j in range(len(elemGrps)):
            column.append(elemGrps[j][i])
        elemGrpsInverted.append(column)
    scene["bcb_prop_elemGrps"] = elemGrpsInverted
    
################################################################################   

def getConfigDataFromScene(scene):
    
    ### Get menu config data from scene
    print("Getting menu config data from scene...")

    props = bpy.context.window_manager.bcb

    version = bcb_version
    warning = ""
    if "bcb_version" in scene.keys():
        versionCfg = scene["bcb_version"]
        if versionCfg != version:
            if versionCfg[0] < version[0]:
                warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."
    else:
        versionCfg = (0, 0, 0)
        warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."

    ### Preprocessing Tools

    if "bcb_prop_preprocTools_aut" in scene.keys():
        props.preprocTools_aut = scene["bcb_prop_preprocTools_aut"]

    if "bcb_prop_preprocTools_rps" in scene.keys():
        props.preprocTools_rps = scene["bcb_prop_preprocTools_rps"]
    if "bcb_prop_preprocTools_rps_nam" in scene.keys():
        props.preprocTools_rps_nam = scene["bcb_prop_preprocTools_rps_nam"]

    if "bcb_prop_preprocTools_grp" in scene.keys():
        props.preprocTools_grp = scene["bcb_prop_preprocTools_grp"]
    if "bcb_prop_preprocTools_grp_sep" in scene.keys():
        props.preprocTools_grp_sep = scene["bcb_prop_preprocTools_grp_sep"]
    if "bcb_prop_preprocTools_grp_occ" in scene.keys():
        props.preprocTools_grp_occ = scene["bcb_prop_preprocTools_grp_occ"]

    if "bcb_prop_preprocTools_mod" in scene.keys():
        props.preprocTools_mod = scene["bcb_prop_preprocTools_mod"]

    if "bcb_prop_preprocTools_ctr" in scene.keys():
        props.preprocTools_ctr = scene["bcb_prop_preprocTools_ctr"]

    if "bcb_prop_preprocTools_sep" in scene.keys():
        props.preprocTools_sep = scene["bcb_prop_preprocTools_sep"]

    if "bcb_prop_preprocTools_dis" in scene.keys():
        props.preprocTools_dis = scene["bcb_prop_preprocTools_dis"]
    if "bcb_prop_preprocTools_dis_siz" in scene.keys():
        props.preprocTools_dis_siz = scene["bcb_prop_preprocTools_dis_siz"]
    if "bcb_prop_preprocTools_dis_cel" in scene.keys():
        props.preprocTools_dis_cel = scene["bcb_prop_preprocTools_dis_cel"]
    if "bcb_prop_preprocTools_dis_jus" in scene.keys():
        props.preprocTools_dis_jus = scene["bcb_prop_preprocTools_dis_jus"]

    if "bcb_prop_preprocTools_rbs" in scene.keys():
        props.preprocTools_rbs = scene["bcb_prop_preprocTools_rbs"]

    if "bcb_prop_preprocTools_int" in scene.keys():
        props.preprocTools_int = scene["bcb_prop_preprocTools_int"]
    if "bcb_prop_preprocTools_int_bol" in scene.keys():
        props.preprocTools_int_bol = scene["bcb_prop_preprocTools_int_bol"]

    if "bcb_prop_preprocTools_fix" in scene.keys():
        props.preprocTools_fix = scene["bcb_prop_preprocTools_fix"]
    if "bcb_prop_preprocTools_fix_nam" in scene.keys():
        props.preprocTools_fix_nam = scene["bcb_prop_preprocTools_fix_nam"]
    if "bcb_prop_preprocTools_fix_cac" in scene.keys():
        props.preprocTools_fix_cac = scene["bcb_prop_preprocTools_fix_cac"]
    if "bcb_prop_preprocTools_fix_rng" in scene.keys():
        props.preprocTools_fix_rng = scene["bcb_prop_preprocTools_fix_rng"]
    if "bcb_prop_preprocTools_fix_axp" in scene.keys():
        props.preprocTools_fix_axp = scene["bcb_prop_preprocTools_fix_axp"]
    if "bcb_prop_preprocTools_fix_axn" in scene.keys():
        props.preprocTools_fix_axn = scene["bcb_prop_preprocTools_fix_axn"]
    if "bcb_prop_preprocTools_fix_ayp" in scene.keys():
        props.preprocTools_fix_ayp = scene["bcb_prop_preprocTools_fix_ayp"]
    if "bcb_prop_preprocTools_fix_ayn" in scene.keys():
        props.preprocTools_fix_ayn = scene["bcb_prop_preprocTools_fix_ayn"]
    if "bcb_prop_preprocTools_fix_azp" in scene.keys():
        props.preprocTools_fix_azp = scene["bcb_prop_preprocTools_fix_azp"]
    if "bcb_prop_preprocTools_fix_azn" in scene.keys():
        props.preprocTools_fix_azn = scene["bcb_prop_preprocTools_fix_azn"]

    if "bcb_prop_preprocTools_gnd" in scene.keys():
        props.preprocTools_gnd = scene["bcb_prop_preprocTools_gnd"]
    if "bcb_prop_preprocTools_gnd_obj" in scene.keys():
        props.preprocTools_gnd_obj = scene["bcb_prop_preprocTools_gnd_obj"]
    if "bcb_prop_preprocTools_gnd_obm" in scene.keys():
        props.preprocTools_gnd_obm = scene["bcb_prop_preprocTools_gnd_obm"]
    if "bcb_prop_preprocTools_gnd_nac" in scene.keys():
        props.preprocTools_gnd_nac = scene["bcb_prop_preprocTools_gnd_nac"]
    if "bcb_prop_preprocTools_gnd_nap" in scene.keys():
        props.preprocTools_gnd_nap = scene["bcb_prop_preprocTools_gnd_nap"]
    if "bcb_prop_preprocTools_gnd_nfq" in scene.keys():
        props.preprocTools_gnd_nfq = scene["bcb_prop_preprocTools_gnd_nfq"]
    if "bcb_prop_preprocTools_gnd_ndu" in scene.keys():
        props.preprocTools_gnd_ndu = scene["bcb_prop_preprocTools_gnd_ndu"]
    if "bcb_prop_preprocTools_gnd_nsd" in scene.keys():
        props.preprocTools_gnd_nsd = scene["bcb_prop_preprocTools_gnd_nsd"]
    if "bcb_prop_preprocTools_gnd_nam" in scene.keys():
        props.preprocTools_gnd_nam = scene["bcb_prop_preprocTools_gnd_nam"]

    ### Postprocessing Tools

    if "bcb_prop_postprocTools_aut" in scene.keys():
        props.postprocTools_aut = scene["bcb_prop_postprocTools_aut"]

    if "bcb_prop_postprocTools_lox" in scene.keys():
        props.postprocTools_lox = scene["bcb_prop_postprocTools_lox"]
    if "bcb_prop_postprocTools_lox_elm" in scene.keys():
        props.postprocTools_lox_elm = scene["bcb_prop_postprocTools_lox_elm"]
    if "bcb_prop_postprocTools_lox_nam" in scene.keys():
        props.postprocTools_lox_nam = scene["bcb_prop_postprocTools_lox_nam"]

    if "bcb_prop_postprocTools_fcx" in scene.keys():
        props.postprocTools_fcx = scene["bcb_prop_postprocTools_fcx"]
    if "bcb_prop_postprocTools_fcx_con" in scene.keys():
        props.postprocTools_fcx_con = scene["bcb_prop_postprocTools_fcx_con"]
    if "bcb_prop_postprocTools_fcx_nam" in scene.keys():
        props.postprocTools_fcx_nam = scene["bcb_prop_postprocTools_fcx_nam"]

    if "bcb_prop_postprocTools_fcv" in scene.keys():
        props.postprocTools_fcv = scene["bcb_prop_postprocTools_fcv"]
    if "bcb_prop_postprocTools_fcv_con" in scene.keys():
        props.postprocTools_fcv_con = scene["bcb_prop_postprocTools_fcv_con"]
    if "bcb_prop_postprocTools_fcv_frm" in scene.keys():
        props.postprocTools_fcv_frm = scene["bcb_prop_postprocTools_fcv_frm"]
    if "bcb_prop_postprocTools_fcv_nbt" in scene.keys():
        props.postprocTools_fcv_nbt = scene["bcb_prop_postprocTools_fcv_nbt"]
    if "bcb_prop_postprocTools_fcv_max" in scene.keys():
        props.postprocTools_fcv_max = scene["bcb_prop_postprocTools_fcv_max"]
    if "bcb_prop_postprocTools_fcv_pas" in scene.keys():
        props.postprocTools_fcv_pas = scene["bcb_prop_postprocTools_fcv_pas"]

    if "bcb_prop_postprocTools_cav" in scene.keys():
        props.postprocTools_cav = scene["bcb_prop_postprocTools_cav"]
    if "bcb_prop_postprocTools_cav_siz" in scene.keys():
        props.postprocTools_cav_siz = scene["bcb_prop_postprocTools_cav_siz"]

    if "bcb_prop_postprocTools_rps" in scene.keys():
        props.postprocTools_rps = scene["bcb_prop_postprocTools_rps"]
    if "bcb_prop_postprocTools_rps_nam" in scene.keys():
        props.postprocTools_rps_nam = scene["bcb_prop_postprocTools_rps_nam"]

    ### General

    if "bcb_prop_stepsPerSecond" in scene.keys():
        props.stepsPerSecond = scene["bcb_prop_stepsPerSecond"]
    if "bcb_prop_constraintUseBreaking" in scene.keys():
        props.constraintUseBreaking = scene["bcb_prop_constraintUseBreaking"]
    if "bcb_prop_passiveUseBreaking" in scene.keys():
        props.passiveUseBreaking = scene["bcb_prop_passiveUseBreaking"]
    if "bcb_prop_connectionCountLimit" in scene.keys():
        props.connectionCountLimit = scene["bcb_prop_connectionCountLimit"]
    if "bcb_prop_searchDistance" in scene.keys():
        props.searchDistance = scene["bcb_prop_searchDistance"]
    if "bcb_prop_clusterRadius" in scene.keys():
        props.clusterRadius = scene["bcb_prop_clusterRadius"]
    if "bcb_prop_alignVertical" in scene.keys():
        props.alignVertical = scene["bcb_prop_alignVertical"]
    if "bcb_prop_useAccurateArea" in scene.keys():
        props.useAccurateArea = scene["bcb_prop_useAccurateArea"]
    if "bcb_prop_rebarMesh" in scene.keys():
        props.rebarMesh = scene["bcb_prop_rebarMesh"]
    if "bcb_prop_surfaceThickness" in scene.keys():
        props.surfaceThickness = scene["bcb_prop_surfaceThickness"]
    if "bcb_prop_surfaceForced" in scene.keys():
        props.surfaceForced = scene["bcb_prop_surfaceForced"]
    if "bcb_prop_minimumElementSize" in scene.keys():
        props.minimumElementSize = scene["bcb_prop_minimumElementSize"]
    if "bcb_prop_automaticMode" in scene.keys():
        props.automaticMode = scene["bcb_prop_automaticMode"]
    if "bcb_prop_saveBackups" in scene.keys():
        props.saveBackups = scene["bcb_prop_saveBackups"]
    if "bcb_prop_timeScalePeriod" in scene.keys():
        props.timeScalePeriod = scene["bcb_prop_timeScalePeriod"]
    if "bcb_prop_timeScalePeriodValue" in scene.keys():
        props.timeScalePeriodValue = scene["bcb_prop_timeScalePeriodValue"]
    if "bcb_prop_warmUpPeriod" in scene.keys():
        props.warmUpPeriod = scene["bcb_prop_warmUpPeriod"]
    if "bcb_prop_progrWeak" in scene.keys():
        props.progrWeak = scene["bcb_prop_progrWeak"]
    if "bcb_prop_progrWeakLimit" in scene.keys():
        props.progrWeakLimit = scene["bcb_prop_progrWeakLimit"]
    if "bcb_prop_progrWeakStartFact" in scene.keys():
        props.progrWeakStartFact = scene["bcb_prop_progrWeakStartFact"]
    if "bcb_prop_snapToAreaOrient" in scene.keys():
        props.snapToAreaOrient = scene["bcb_prop_snapToAreaOrient"]
    if "bcb_prop_disableCollision" in scene.keys():
        props.disableCollision = scene["bcb_prop_disableCollision"]
    if "bcb_prop_disableCollisionPerm" in scene.keys():
        props.disableCollisionPerm = scene["bcb_prop_disableCollisionPerm"]
    if "bcb_prop_lowerBrkThresPriority" in scene.keys():
        props.lowerBrkThresPriority = scene["bcb_prop_lowerBrkThresPriority"]
    if "bcb_prop_detonatorObj" in scene.keys():
        props.detonatorObj = scene["bcb_prop_detonatorObj"]
        
    #if len(warning): return warning
            
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    if "bcb_prop_elemGrps" in scene.keys():
        elemGrps = mem["elemGrps"]
        try: elemGrpsProp = scene["bcb_prop_elemGrps"]
        except: pass
        elemGrpsInverted = []
        grpCnt = len(elemGrps)
        grpPropCnt = len(elemGrpsProp[0])
        for i in range(grpPropCnt):
            column = []
            for j in range(min(len(elemGrpsProp), len(presets[0]))):  # Use the smaller sized array in case some different BCB version is used to prevent error
                if j != EGSidxAsst:
                    # Check if stored types are identical then copy stored data, otherwise fall back to preset default data.
                    # But do this only if one is a string type as numeric values can have different types, because they would convert like int to float.
                    # Next line means: if not type(elemGrpsProp[j][i]) == type("") xor type(presets[i][j]) == type(""):
                    if not bool(type(elemGrpsProp[j][i]) == type("")) != bool(type(presets[0][j]) == type("")):
                          column.append(elemGrpsProp[j][i])
                    else: column.append(presets[0][j])
                else:
                    column.append(dict(elemGrpsProp[j][i]).copy())
                    ### Check if formula assistant settings are complete and if not fill in missing vars from assistant defaults
                    asst = column[-1]
                    items = [item[0] for item in asst.items()]  # Make separate list of attribute names
                    for asstDef in formulaAssistants:
                        if asst['ID'] == asstDef['ID']:
                            for item in asstDef.items():
                                if item[0] not in items:
                                    print("Warning: FA property '%s' missing, BCB scene settings are probably outdated." %item[0])
                                    asst[item[0]] = item[1]
                            break
            missingColumns = len(presets[0]) -len(column)
            if missingColumns:
                print("Warning: elemGrp property missing, BCB scene settings are probably outdated.")
                # Find default group or use first one
                k = 0
                for l in range(grpCnt):
                    if elemGrps[l][EGSidxName] == '': k = l
                # Fill in missing data from preset default data
                ofs = len(column)
                for j in range(missingColumns):
                    column.append(presets[0][ofs+j])
            elemGrpsInverted.append(column)
        mem["elemGrps"] = elemGrpsInverted

        if debug:
            print("LOADED:", len(mem["elemGrps"]), len(mem["elemGrps"][0]))
            for i in range(grpPropCnt):
                print(i, mem["elemGrps"][i][0], mem["elemGrps"][i][20])
                
################################################################################   

def storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, connectsTol, constsConnect):
    
    ### Store build data in scene
    print("Storing build data in scene...")
    
    if objs != None:
        scene["bcb_objs"] = [obj.name for obj in objs]
    if objsEGrp != None:
        scene["bcb_objsEGrp"] = objsEGrp
    if emptyObjs != None:
        data = []
        for obj in emptyObjs:
            if obj != None:
                if hasattr(obj, 'name'): data.append(obj.name)
                else: data.append(obj)  # When empties are not build for FM export we also expect just names
            else: data.append("")
        scene["bcb_emptyObjs"] = data
    if childObjs != None:
        scene["bcb_childObjs"] = [obj.name for obj in childObjs]
    if connectsPair != None:
        scene["bcb_connectsPair"] = connectsPair
    if connectsPairParent != None:
        scene["bcb_connectsPairParent"] = connectsPairParent
    if connectsLoc != None:
        scene["bcb_connectsLoc"] = connectsLoc
    if connectsGeo != None:
        scene["bcb_connectsGeo"] = connectsGeo
    if connectsConsts != None:
        scene["bcb_connectsConsts"] = connectsConsts
    if connectsTol != None:
        scene["bcb_connectsTol"] = connectsTol
    if constsConnect != None:
        scene["bcb_constsConnect"] = constsConnect    
                    
################################################################################   

def getBuildDataFromScene(scene):
    
    ### Get build data from scene
    print("Getting build data from scene...")

    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ###### Get data from scene

    #try: objsEGrp = scene["bcb_objsEGrp"]    # Not required for building only for clearAllDataFromScene(), index will be renewed on update
    #except: objsEGrp = []; print("Error: bcb_objsEGrp property not found, rebuilding constraints is required.")

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
        
    try: names = scene["bcb_childObjs"]
    except: names = []; print("Error: bcb_childObjs property not found, rebuilding constraints is required.")
    childObjs = []
    for name in names:
        if len(name):
            try: childObjs.append(scnObjs[name])
            except: childObjs.append(None); print("Error: Object %s missing, rebuilding constraints is required." %name)
        else: childObjs.append(None)
        
    try: connectsPair = scene["bcb_connectsPair"]
    except: connectsPair = []; print("Error: bcb_connectsPair property not found, rebuilding constraints is required.")

    try: connectsPairParent = scene["bcb_connectsPairParent"]
    except: connectsPairParent = []; print("Error: bcb_connectsPairParent property not found, rebuilding constraints is required.")

    try: connectsLoc = scene["bcb_connectsLoc"]
    except: connectsLoc = []; print("Error: bcb_connectsLoc property not found, rebuilding constraints is required.")

    try: connectsGeo = scene["bcb_connectsGeo"]
    except: connectsGeo = []; print("Error: bcb_connectsGeo property not found, rebuilding constraints is required.")

    try: connectsConsts = scene["bcb_connectsConsts"]
    except: connectsConsts = []; print("Error: bcb_connectsConsts property not found, rebuilding constraints is required.")

    try: connectsTol = scene["bcb_connectsTol"]
    except: connectsTol = []; #print("Error: bcb_connectsTol property not found, rebuilding constraints is required.")
    # Silenced this error since we needed to postpone storage of connectsTol and this function is called once before the data becomes available 

    try: constsConnect = scene["bcb_constsConnect"]
    except: constsConnect = []; print("Error: bcb_constsConnect property not found, rebuilding constraints is required.")
    
    ### Debug: Log all data to ASCII file
    if debug:
        log = []
        log.append([obj.name for obj in objs])
        log.append([obj.name for obj in emptyObjs])
        log.append([obj.name for obj in childObjs])
        log.append(makeListsPickleFriendly(connectsPair))
        log.append(makeListsPickleFriendly(connectsPairParent))
        log.append(makeListsPickleFriendly(connectsLoc))
        log.append(makeListsPickleFriendly(connectsGeo))
        log.append(makeListsPickleFriendly(connectsConsts))
        log.append(makeListsPickleFriendly(connectsTol))
        log.append(makeListsPickleFriendly(constsConnect))
        dataToFile(log, logPath +r"\log_bcb_keys.txt")
        log = []
        log.append([obj.name for obj in bpy.context.scene.objects])
        dataToFile(log, logPath +r"\log_bcb_scene.txt")
        
    return objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, connectsTol, constsConnect

################################################################################   

def clearAllDataFromScene(scene, qKeepBuildData=0):
    
    ### Clear all data related to Bullet Constraints Builder from scene

    if hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE') and asciiExportName in scene.objects:
        print("\nWarning: Clearing scene of BCB data for Fracture Modifier not yet implemented.")
        return

    print("\nStarting to clear data related to Bullet Constraints Builder from scene...")
    time_start = time.time()

    props = bpy.context.window_manager.bcb
    
    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ###### Get data from scene
    print("Getting data from scene...")

    try: objsEGrp = scene["bcb_objsEGrp"]
    except: objsEGrp = []; print("Warning: bcb_objsEGrp property not found, cleanup may be incomplete.")

    try: names = scene["bcb_objs"]
    except: names = []; print("Warning: bcb_objs property not found, cleanup may be incomplete.")
    objs = []
    for name in names:
        if len(name):
            try: objs.append(scnObjs[name])
            except: objs.append(None); print("Warning: Object %s missing, cleanup may be incomplete." %name)
        else: objs.append(None)
        
    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Warning: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        if len(name):
            try: emptyObjs.append(scnEmptyObjs[name])
            except: emptyObjs.append(None); print("Warning: Object %s missing, cleanup may be incomplete." %name)
        else: emptyObjs.append(None)
        
    try: names = scene["bcb_childObjs"]
    except: names = []; print("Warning: bcb_childObjs property not found, cleanup may be incomplete.")
    childObjs = []
    for name in names:
        if len(name):
            try: childObjs.append(scnObjs[name])
            except: childObjs.append(None); print("Warning: Object %s missing, cleanup may be incomplete." %name)
        else: childObjs.append(None)
        
    try: connectsPairParent = scene["bcb_connectsPairParent"]
    except: connectsPairParent = []; print("Warning: bcb_connectsPairParent property not found, cleanup may be incomplete.")

    ### Backup layer settings and activate all layers
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(1)
    scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
    
    ###### Removing data from scene
    
    try: del scene["bcb_valid"]  # Removing flag for valid data first
    except: pass

    ### Remove parents for too small elements 
    for k in range(len(connectsPairParent)):
        objChild = objs[connectsPairParent[k][0]]
        objChild.parent = None
        ### Reactivate rigid body settings (with defaults though, TODO: Use an actual backup of the original settings)
        #if objChild.rigid_body == None:
        #    bpy.context.scene.objects.active = objChild
        #    bpy.ops.rigidbody.object_add()

    ### Replace modified elements with their child counterparts (the original meshes) 
    print("Replacing modified elements with their original meshes...")
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    parentTmpObjs = []
    childTmpObjs = []
    ### Make lists first to avoid confusion with renaming
    for childObj in childObjs:
        parentObj = scene.objects[childObj["bcb_parent"]]
        del childObj["bcb_parent"]
        parentTmpObjs.append(parentObj)
        childTmpObjs.append(childObj)
    ### Revert names and scaling back to original
    for i in range(len(parentTmpObjs)):
        parentObj = parentTmpObjs[i]
        childObj = childTmpObjs[i]
        name = parentObj.name
        scene.objects[parentObj.name].name = "temp"     # Sometimes renaming fails due to the name being blocked, then it helps to rename it differently first
        childObj.name = name
        childObj.data.name = parentObj.data.name
        ### Add rigid body settings back to child element again
        if parentObj.rigid_body != None:
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_add()
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = parentObj
            bpy.ops.rigidbody.object_settings_copy()
            parentObj.select = 0
            childObj.select = 0
            
    ### Prepare scene object dictionaries again after we changed obj names (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ###### Get data again from scene after we changed obj names
    print("Getting updated data from scene...")
        
    try: names = scene["bcb_objs"]
    except: names = []; print("Warning: bcb_objs property not found, cleanup may be incomplete.")
    objs = []
    for name in names:
        if len(name):
            try: objs.append(scnObjs[name])
            except: objs.append(None) #; print("Warning: Object %s missing, cleanup may be incomplete." %name)
        else: objs.append(None)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Warning: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        if len(name):
            try: emptyObjs.append(scnEmptyObjs[name])
            except: emptyObjs.append(None) #; print("Warning: Object %s missing, cleanup may be incomplete." %name)
        else: emptyObjs.append(None)
        
    ### Revert element scaling
    for k in range(len(objs)):
        try: scale = mem["elemGrps"][objsEGrp[k]][EGSidxScal]  # Try in case elemGrps is from an old BCB version
        except: pass
        else:
            obj = objs[k]
            if obj != None and scale != 0 and scale != 1:
                obj.scale /= scale

    ######

    if not qKeepBuildData:
        
        print("Removing ID properties...")
    
        ### Clear object properties
        for obj in objs:
            if obj != None:
                for key in obj.keys():
                    if "bcb_" in key: del obj[key]

        ### Remove ID property build data (leaves menu props in place)
        for key in scene.keys():
            if "bcb_" in key: del scene[key]

    ######

    print("Deleting objects...")

    ### Select modified elements for deletion from scene 
    for parentObj in parentTmpObjs:
        if parentObj != None:
            try: scene.objects[parentObj.name]  # Check if object is still linked to scene (can crash otherwise on deletion)
            except: pass
            else: parentObj.select = 1
    ### Select constraint empty objects for deletion from scene
    for emptyObj in emptyObjs:
        if emptyObj != None:
            try: scene.objects[emptyObj.name]  # Check if object is still linked to scene (can crash otherwise on deletion)
            except: pass
            else: emptyObj.select = 1
    
    if props.automaticMode and props.saveBackups:
        ### Quick and dirty delete function (faster but can cause problems on immediate rebuilding, requires saving and reloading first)
        # Delete (unlink) modified elements from scene 
        for parentObj in parentTmpObjs: scene.objects.unlink(parentObj)
        # Delete (unlink) constraint empty objects from scene
        for emptyObj in emptyObjs: scene.objects.unlink(emptyObj)
        # Unlink 'RigidBodyConstraints' group from scene so that the unlinked empties have no more users and will be discarted on saving
        bpy.data.groups.remove(bpy.data.groups["RigidBodyConstraints"], do_unlink=True)
        # Save file
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        if len(objs) +len(emptyObjs) < 4000:
            print("Bake blend saved. (You can terminate Blender now if you don't want to wait for")
            print("the slow Depsgraph to finish, just reloading the blend file can be faster.)") 
            ### Bring back unlinked objects for regular deletion now
            # Link modified elements back to scene
            for parentObj in parentTmpObjs: scene.objects.link(parentObj)
            # Link constraint empty objects back to scene
            for emptyObj in emptyObjs: scene.objects.link(emptyObj)

    if len(objs) +len(emptyObjs) < 4000:
        ### Delete all selected objects
        bpy.ops.object.delete(use_global=True)
    else:
        print("You have a large amount of objects which can take very long to delete,")
        print("to reduce waiting time they will just be marked for deletion (unlinked).")
        print("Please save and reload the blend file so that the database can clean up.")
        print("(Doing not so can cause problems on immediate rebuild and simulation.)")
        ### Quick and dirty delete function (faster but can cause problems on immediate rebuilding, requires saving and reloading first)
        # Delete (unlink) modified elements from scene 
        for parentObj in parentTmpObjs:
            try: scene.objects.unlink(parentObj)
            except: pass
        # Delete (unlink) constraint empty objects from scene
        for emptyObj in emptyObjs:
            try: scene.objects.unlink(emptyObj)
            except: pass
        # Unlink 'RigidBodyConstraints' group from scene so that the unlinked empties have no more users and will be discarted on saving
        try: bpy.data.groups.remove(bpy.data.groups["RigidBodyConstraints"], do_unlink=True)
        except: pass
            
    # Set layers as in original scene
    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)

    ### Revert selection back to original state and clear ID properties from objects
    for obj in objs:
        if obj != None:
            obj.select = 1

    print('-- Time: %0.2f s' %(time.time()-time_start))
    print()
    print('Done.')
