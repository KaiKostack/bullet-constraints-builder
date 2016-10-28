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

    scene["bcb_prop_preprocTools_grp"] = props.preprocTools_grp
    scene["bcb_prop_preprocTools_mod"] = props.preprocTools_mod
    scene["bcb_prop_preprocTools_sep"] = props.preprocTools_sep
    scene["bcb_prop_preprocTools_dis"] = props.preprocTools_dis
    scene["bcb_prop_preprocTools_rbs"] = props.preprocTools_rbs
    scene["bcb_prop_preprocTools_fix"] = props.preprocTools_fix

    scene["bcb_prop_preprocTools_grp_sep"] = props.preprocTools_grp_sep
    scene["bcb_prop_preprocTools_dis_siz"] = props.preprocTools_dis_siz
    scene["bcb_prop_preprocTools_dis_jus"] = props.preprocTools_dis_jus
    scene["bcb_prop_preprocTools_fix_gnd"] = props.preprocTools_fix_gnd
    scene["bcb_prop_preprocTools_fix_obj"] = props.preprocTools_fix_obj

    scene["bcb_prop_stepsPerSecond"] = props.stepsPerSecond
    scene["bcb_prop_constraintUseBreaking"] = props.constraintUseBreaking
    scene["bcb_prop_connectionCountLimit"] = props.connectionCountLimit
    scene["bcb_prop_searchDistance"] = props.searchDistance
    scene["bcb_prop_clusterRadius"] = props.clusterRadius
    scene["bcb_prop_alignVertical"] = props.alignVertical
    scene["bcb_prop_useAccurateArea"] = props.useAccurateArea 
    scene["bcb_prop_nonManifoldThickness"] = props.nonManifoldThickness 
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
    scene["bcb_prop_lowerBrkThresPriority"] = props.lowerBrkThresPriority
    
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    elemGrps = mem["elemGrps"]
    elemGrpsInverted = []
    for i in range(len(elemGrps[0])):
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

    warning = ""
    if "bcb_version" in scene.keys():
        versionCfg = scene["bcb_version"]
        version = bcb_version
        if versionCfg != version:
            if versionCfg[0] < version[0]:
                warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."
    else:   warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."

    if "bcb_prop_preprocTools_grp" in scene.keys():
        props.preprocTools_grp = scene["bcb_prop_preprocTools_grp"]
    if "bcb_prop_preprocTools_mod" in scene.keys():
        props.preprocTools_mod = scene["bcb_prop_preprocTools_mod"]
    if "bcb_prop_preprocTools_sep" in scene.keys():
        props.preprocTools_sep = scene["bcb_prop_preprocTools_sep"]
    if "bcb_prop_preprocTools_dis" in scene.keys():
        props.preprocTools_dis = scene["bcb_prop_preprocTools_dis"]
    if "bcb_prop_preprocTools_rbs" in scene.keys():
        props.preprocTools_rbs = scene["bcb_prop_preprocTools_rbs"]
    if "bcb_prop_preprocTools_fix" in scene.keys():
        props.preprocTools_fix = scene["bcb_prop_preprocTools_fix"]

    if "bcb_prop_preprocTools_grp_sep" in scene.keys():
        props.preprocTools_grp_sep = scene["bcb_prop_preprocTools_grp_sep"]
    if "bcb_prop_preprocTools_dis_siz" in scene.keys():
        props.preprocTools_dis_siz = scene["bcb_prop_preprocTools_dis_siz"]
    if "bcb_prop_preprocTools_dis_jus" in scene.keys():
        props.preprocTools_dis_jus = scene["bcb_prop_preprocTools_dis_jus"]
    if "bcb_prop_preprocTools_fix_gnd" in scene.keys():
        props.preprocTools_fix_gnd = scene["bcb_prop_preprocTools_fix_gnd"]
    if "bcb_prop_preprocTools_fix_obj" in scene.keys():
        props.preprocTools_fix_obj = scene["bcb_prop_preprocTools_fix_obj"]

    if "bcb_prop_stepsPerSecond" in scene.keys():
        props.stepsPerSecond = scene["bcb_prop_stepsPerSecond"]
    if "bcb_prop_constraintUseBreaking" in scene.keys():
        props.constraintUseBreaking = scene["bcb_prop_constraintUseBreaking"]
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
    if "bcb_prop_nonManifoldThickness" in scene.keys():
        props.nonManifoldThickness = scene["bcb_prop_nonManifoldThickness"]
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
    if "bcb_prop_lowerBrkThresPriority" in scene.keys():
        props.lowerBrkThresPriority = scene["bcb_prop_lowerBrkThresPriority"]
        
    if len(warning): return warning
            
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
            for j in range(len(elemGrpsProp)):
                if j != EGSidxAsst:
                      column.append(elemGrpsProp[j][i])
                else: column.append(dict(elemGrpsProp[j][i]).copy())
            missingColumns = len(elemGrps[0]) -len(column)
            if missingColumns:
                print("Error: elemGrp property missing, BCB scene settings are probably outdated.")
                print("Clear all BCB data, double-check your settings and rebuild constraints.")
                # Find default group or use first one
                k = 0
                for l in range(grpCnt):
                    if elemGrps[l][EGSidxName] == '': k = l
                # Fill in missing data from found group
                ofs = len(column)
                for j in range(missingColumns):
                    column.append(elemGrps[k][ofs +j])
            elemGrpsInverted.append(column)
        mem["elemGrps"] = elemGrpsInverted

        if debug:
            print("LOADED:", len(mem["elemGrps"]), len(mem["elemGrps"][0]))
            for i in range(grpPropCnt):
                print(i, mem["elemGrps"][i][0], mem["elemGrps"][i][20])
                
################################################################################   

def storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, constsConnect):
    
    ### Store build data in scene
    print("Storing build data in scene...")
    
    if objs != None:
        scene["bcb_objs"] = [obj.name for obj in objs]
    if objsEGrp != None:
        scene["bcb_objsEGrp"] = objsEGrp
    if emptyObjs != None:
        scene["bcb_emptyObjs"] = [obj.name for obj in emptyObjs]
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
        try: objs.append(scnObjs[name])
        except: print("Error: Object %s missing, rebuilding constraints is required." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Error: bcb_emptyObjs property not found, rebuilding constraints is required.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: print("Error: Object %s missing, rebuilding constraints is required." %name)

    try: names = scene["bcb_childObjs"]
    except: names = []; print("Error: bcb_childObjs property not found, rebuilding constraints is required.")
    childObjs = []
    for name in names:
        try: childObjs.append(scnObjs[name])
        except: print("Error: Object %s missing, rebuilding constraints is required." %name)

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
        log.append(makeListsPickleFriendly(constsConnect))
        dataToFile(log, logPath +r"\log_bcb_keys.txt")
        log = []
        log.append([obj.name for obj in bpy.context.scene.objects])
        dataToFile(log, logPath +r"\log_bcb_scene.txt")
        
    return objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, constsConnect

################################################################################   

def clearAllDataFromScene(scene):
    
    ### Clear all data related to Bullet Constraints Builder from scene
    print("\nStarting to clear all data related to Bullet Constraints Builder from scene...")
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
        try: objs.append(scnObjs[name])
        except: print("Warning: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Warning: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: print("Warning: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_childObjs"]
    except: names = []; print("Warning: bcb_childObjs property not found, cleanup may be incomplete.")
    childObjs = []
    for name in names:
        try: childObjs.append(scnObjs[name])
        except: print("Warning: Object %s missing, cleanup may be incomplete." %name)

    try: connectsPairParent = scene["bcb_connectsPairParent"]
    except: connectsPairParent = []; print("Warning: bcb_connectsPairParent property not found, cleanup may be incomplete.")

    ### Backup layer settings and activate all layers
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(1)
    scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
    
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
        try: objs.append(scnObjs[name])
        except: pass #print("Warning: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Warning: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: pass #print("Warning: Object %s missing, cleanup may be incomplete." %name)

    ### Revert element scaling
    for k in range(len(objs)):
        try: scale = mem["elemGrps"][objsEGrp[k]][EGSidxScal]  # Try in case elemGrps is from an old BCB version
        except: pass
        else:
            obj = objs[k]
            if scale != 0 and scale != 1:
                obj.scale /= scale

    print("Removing ID properties...")
    
    ### Clear object properties
    for obj in objs:
        for key in obj.keys():
            if "bcb_" in key: del obj[key]

    ### Remove ID property build data (leaves menu props in place)
    for key in scene.keys():
        if "bcb_" in key: del scene[key]

    print("Deleting objects...")

    ### Select modified elements for deletion from scene 
    for parentObj in parentTmpObjs: parentObj.select = 1
    ### Select constraint empty objects for deletion from scene
    for emptyObj in emptyObjs: emptyObj.select = 1
    
    if props.automaticMode and props.saveBackups:
        ### Quick and dirty delete function (faster but can cause problems on immediate rebuilding, requires saving and reloading first)
        # Delete (unlink) modified elements from scene 
        for parentObj in parentTmpObjs: scene.objects.unlink(parentObj)
        # Delete (unlink) constraint empty objects from scene
        for emptyObj in emptyObjs: scene.objects.unlink(emptyObj)
        # Save file
        bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        print("Bake blend saved. (You can terminate Blender now if you don't want to wait for")
        print("the slow Depsgraph to finish, just reloading the blend file can be faster.)") 
        ### Bring back unlinked objects for regular deletion now
        # Link modified elements back to scene
        for parentObj in parentTmpObjs: scene.objects.link(parentObj)
        # Link constraint empty objects back to scene
        for emptyObj in emptyObjs: scene.objects.link(emptyObj)

    ### Delete all selected objects
    bpy.ops.object.delete(use_global=True)
            
    # Set layers as in original scene
    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)

    ### Revert selection back to original state and clear ID properties from objects
    for obj in objs:
        obj.select = 1

    print('-- Time: %0.2f s' %(time.time()-time_start))
    print()
    print('Done.')
