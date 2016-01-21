####################################
# Bullet Constraints Builder v1.81 #
####################################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# This version is developed at the Laurea University of Applied Sciences, Finland
# Copyright (C) 2015, 2016 Kai Kostack
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
   
### Vars for constraint distribution (directly accessible from GUI)
stepsPerSecond = 200         # 200   | Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable)
constraintUseBreaking = 1    # 1     | Enables breaking for all constraints
connectionCountLimit = 100   # 0     | Maximum count of connections per object pair (0 = disabled)
searchDistance = 0.02        # 0.02  | Search distance to neighbor geometry
clusterRadius = 0            # 0.4   | Radius for bundling close constraints into clusters (0 = clusters disabled)
alignVertical = 0            # 0.0   | Uses a vertical alignment multiplier for connection type 4 instead of using unweighted center to center orientation (0 = disabled)
                             #       | Internally X and Y components of the directional vector will be reduced by this factor, should always be < 1 to make horizontal connections still possible.
useAccurateArea = 0          # 1     | Enables accurate contact area calculation using booleans for the cost of an slower building process. This only works correct with solids i.e. watertight and manifold objects and is therefore recommended for truss structures or steel constructions in general.
                             #       | If disabled a simpler boundary box intersection approach is used which is only recommended for rectangular constructions without diagonal elements.
nonManifoldThickness = 0.1   # 0.01  | Thickness for non-manifold elements (surfaces) when using accurate contact area calculation.
minimumElementSize = 0       # 0.2   | Deletes connections whose elements are below this diameter and makes them parents instead. This can be helpful for increasing performance on models with unrelevant geometric detail such as screwheads.
automaticMode = 0            # 0     | Enables a fully automated workflow for extremely large simulations (object count-wise) were Blender is prone to not being responsive anymore
                             #       | After clicking Build these steps are being done automatically: Building of constraints, baking simulation, clearing constraint and BCB data from scene
saveBackups = 0              # 0     | Enables saving of a backup .blend file after each step for automatic mode, whereby the name of the new .blend ends with `_BCB´
initPeriod = 0               # 0     | For baking: Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled)
initPeriodTimeScale = 0.001  # 0.001 | For baking: Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime

### Vars not directly accessible from GUI
asciiExport = 0              # 0     | Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment).

# Customizable element groups list (for elements of different conflicting groups priority is defined by the list's order)
elemGrps = [
# 0          1    2           3        4   5    6    7    8    9       10   11   12   13    14   15    16
# Name       RVP  Mat.preset  Density  CT  BTC  BTT  BTS  BTB  Stiff.  TPD. TPR. TBD. TBR.  Bev. Scale facing
[ "",        1,   "Concrete", 0,       6,  30,  9,   9,   3,   10**6,  .05, .1,  .1,  .4,   0,   .95,  0      ],   # Defaults to be used when element is not part of any element group
[ "Columns", 1,   "Concrete", 0,       6,  30,  9,   9,   3,   10**6,  .05, .1,  .1,  .4,   0,   .95,  0      ],
[ "Girders", 1,   "Concrete", 0,       6,  30,  9,   9,   3,   10**6,  .05, .1,  .1,  .4,   0,   .95,  0      ],
[ "Walls",   1,   "Concrete", 0,       6,  30,  9,   9,   3,   10**6,  .05, .1,  .1,  .4,   0,   .95,  0      ],
[ "Slabs",   1,   "Concrete", 0,       6,  30,  9,   9,   3,   10**6,  .05, .1,  .1,  .4,   0,   .95,  0      ]
]

# Column descriptions (in order from left to right):
#
# 1.  Required Vertex Pairs     | How many vertex pairs between two elements are required to generate a connection.
#     (Depreciated)             | This can help to ensure there is an actual surface to surface connection between both elements (for at least 3 verts you can expect a shared surface).
#                               | For two elements from different groups with different RVPs the lower number is decisive.
# 2.  Material Preset           | Preset name of the physical material to be used from Blender's internal database.
#                               | See Blender's Rigid Body Tools for a list of available presets.
# 3.  Material Density          | Custom density value (kg/m^3) to use instead of material preset (0 = disabled).
# 4.  Connection Type           | Connection type ID for the constraint presets defined by this script, see list below.
# 5.  Break.Thresh.Compres.     | Real world material compressive breaking threshold in N/mm^2.
# 6.  Break.Thresh.Tensile      | Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).
# 7.  Break.Thresh.Shear        | Real world material shearing breaking threshold in N/mm^2.
# 8.  Break.Thresh.Bend         | Real world material bending breaking threshold in N/mm^2.
# 9.  Spring Stiffness          | Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.
# 10. Tolerance Plast.Def.Dist. | For baking: Allowed tolerance for distance change in percent for plastic deformation (1.00 = 100 %)
# 11. Tolerance Plast.Def.Rot.  | For baking: Allowed tolerance for angular change in radian for plastic deformation
# 12. Tolerance Break.Def.Dist. | For baking: Allowed tolerance for distance change in percent for connection removal (1.00 = 100 %)
# 13. Tolerance Break.Def.Rot.  | For baking: Allowed tolerance for angular change in radian for connection removal
# 14. Bevel                     | Use beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes)
# 15. Scale                     | Apply scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes)
# 16. Facing                    | Generate an addional layer of elements only for display (will only be used together with bevel and scale option)
#
# To add further settings each reference to elemGrps should be checked because indices may shift

# Connection types:
connectTypes = [          # Cnt C T S B S T T T T      CT
[ "UNDEFINED",              0, [0,0,0,0,0,1,1,0,0]], # 0. Undefined (reserved)
[ "1x FIXED",               1, [1,0,0,0,0,1,1,0,0]], # 1. Linear omni-directional + bending breaking threshold
[ "1x POINT",               1, [1,0,0,0,0,1,1,0,0]], # 2. Linear omni-directional breaking threshold
[ "1x FIXED + 1x POINT",    2, [1,0,0,1,0,1,1,0,0]], # 3. Linear omni-directional and bending breaking thresholds
[ "2x GENERIC",             2, [1,1,0,0,0,1,1,0,0]], # 4. Compressive and tensile breaking thresholds
[ "3x GENERIC",             3, [1,1,0,1,0,1,1,0,0]], # 5. Compressive, tensile + shearing and bending breaking thresholds
[ "4x GENERIC",             4, [1,1,1,1,0,1,1,0,0]], # 6. Compressive, tensile, shearing and bending breaking thresholds
[ "3x SPRING",              3, [1,0,0,0,1,0,0,1,1]], # 7. Linear omni-directional breaking threshold with plastic deformability
[ "4x SPRING",              4, [1,0,0,0,1,0,0,1,1]], # 8. Linear omni-directional breaking threshold with plastic deformability
[ "1x FIXED + 3x SPRING",   4, [1,0,0,0,1,1,1,1,1]], # 9. Linear omni-directional + bending breaking threshold with plastic deformability
[ "1x FIXED + 4x SPRING",   5, [1,0,0,0,1,1,1,1,1]], # 10. Linear omni-directional + bending breaking threshold with plastic deformability
[ "4x GENERIC + 3x SPRING", 7, [1,1,1,1,1,1,1,1,1]], # 11. Compressive, tensile, shearing and bending breaking thresholds with plastic deformability
[ "4x GENERIC + 4x SPRING", 8, [1,1,1,1,1,1,1,1,1]], # 12. Compressive, tensile, shearing and bending breaking thresholds with plastic deformability
[ "3 x 3x SPRING",          9, [1,1,1,0,1,0,0,1,1]], # 13. Compressive, tensile and shearing breaking thresholds with plastic deformability
[ "3 x 4x SPRING",         12, [1,1,1,0,1,0,0,1,1]]  # 14. Compressive, tensile and shearing breaking thresholds with plastic deformability
]
# To add further connection types changes to following functions are necessary:
# setConstraintSettings() and bcb_panel() for the UI

### Vars for developers
debug = 0                            # 0     | Enables verbose console output for debugging purposes
withGUI = 1                          # 1     | Enable graphical user interface, after pressing the "Run Script" button the menu panel should appear
logPath = r"/tmp"                    #       | Path to log files if debugging is enabled
maxMenuElementGroupItems = 100       # 100   | Maximum allowed element group entries in menu 
emptyDrawSize = 0.25                 # 0.25  | Display size of constraint empty objects as radius in meters
asciiExportName = "BCB_export.txt"   #       | Name of ASCII text file to be exported
    
# For monitor event handler
qRenderAnimation = 0                 # 0     | Render animation by using render single image function for each frame (doesn't support motion blur, keep it disabled), 1 = regular, 2 = OpenGL

########################################

elemGrpsBak = elemGrps.copy()

################################################################################   

bl_info = {
    "name": "Bullet Constraints Builder",
    "author": "Kai Kostack",
    "version": (1, 8, 1),
    "blender": (2, 7, 5),
    "location": "View3D > Toolbar",
    "description": "Tool to connect rigid bodies via constraints in a physical plausible way.",
    "wiki_url": "http://www.inachus.eu",
    "tracker_url": "http://kaikostack.com",
    "category": "Animation"}

import bpy, sys, mathutils, time, copy, math, pickle, base64, zlib
from mathutils import Vector
#import os
#os.system("cls")

################################################################################
################################################################################

def logDataToFile(data, pathName):
    try: f = open(pathName, "wb")
    except:
        print('Error: Could not write log file:', pathName)
        return 1
    else:
        pickle.dump(data, f, 0)
        f.close()

########################################

def makeListsPickleFriendly(listOld):
    listNew = []
    for sub in listOld:
        # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
        try: test = len(sub)
        # If it fails it is no list
        except: listNew.append(sub)
        # If it is a list
        else:
            sublistNew = []
            for item in sub:
                sublistNew.append(item)
            listNew.append(sublistNew)
    return listNew

################################################################################

def storeConfigDataInScene(scene):

    ### Store menu config data in scene
    if debug: print("Storing menu config data in scene...")
    
    scene["bcb_prop_stepsPerSecond"] = stepsPerSecond
    scene["bcb_prop_constraintUseBreaking"] = constraintUseBreaking
    scene["bcb_prop_connectionCountLimit"] = connectionCountLimit
    scene["bcb_prop_searchDistance"] = searchDistance
    scene["bcb_prop_clusterRadius"] = clusterRadius
    scene["bcb_prop_alignVertical"] = alignVertical
    scene["bcb_prop_useAccurateArea"] = useAccurateArea 
    scene["bcb_prop_nonManifoldThickness"] = nonManifoldThickness 
    scene["bcb_prop_minimumElementSize"] = minimumElementSize 
    scene["bcb_prop_automaticMode"] = automaticMode 
    scene["bcb_prop_saveBackups"] = saveBackups 
    scene["bcb_prop_initPeriod"] = initPeriod
    scene["bcb_prop_initPeriodTimeScale"] = initPeriodTimeScale 
    
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    #scene["bcb_prop_elemGrps"] = elemGrps
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
    if "bcb_prop_stepsPerSecond" in scene.keys():
        global stepsPerSecond
        try: stepsPerSecond = props.prop_stepsPerSecond = scene["bcb_prop_stepsPerSecond"]
        except: pass
    if "bcb_prop_constraintUseBreaking" in scene.keys():
        global constraintUseBreaking
        try: constraintUseBreaking = props.prop_constraintUseBreaking = scene["bcb_prop_constraintUseBreaking"]
        except: pass
    if "bcb_prop_connectionCountLimit" in scene.keys():
        global connectionCountLimit
        try: connectionCountLimit = props.prop_connectionCountLimit = scene["bcb_prop_connectionCountLimit"]
        except: pass
    if "bcb_prop_searchDistance" in scene.keys():
        global searchDistance
        try: searchDistance = props.prop_searchDistance = scene["bcb_prop_searchDistance"]
        except: pass
    if "bcb_prop_clusterRadius" in scene.keys():
        global clusterRadius
        try: clusterRadius = props.prop_clusterRadius = scene["bcb_prop_clusterRadius"]
        except: pass
    if "bcb_prop_alignVertical" in scene.keys():
        global alignVertical
        try: alignVertical = props.prop_alignVertical = scene["bcb_prop_alignVertical"]
        except: pass
    if "bcb_prop_useAccurateArea" in scene.keys():
        global useAccurateArea
        try: useAccurateArea = props.prop_useAccurateArea = scene["bcb_prop_useAccurateArea"]
        except: pass
    if "bcb_prop_nonManifoldThickness" in scene.keys():
        global nonManifoldThickness
        try: nonManifoldThickness = props.prop_nonManifoldThickness = scene["bcb_prop_nonManifoldThickness"]
        except: pass
    if "bcb_prop_minimumElementSize" in scene.keys():
        global minimumElementSize
        try: minimumElementSize = props.prop_minimumElementSize = scene["bcb_prop_minimumElementSize"]
        except: pass
    if "bcb_prop_automaticMode" in scene.keys():
        global automaticMode
        try: automaticMode = props.prop_automaticMode = scene["bcb_prop_automaticMode"]
        except: pass
    if "bcb_prop_saveBackups" in scene.keys():
        global saveBackups
        try: saveBackups = props.prop_saveBackups = scene["bcb_prop_saveBackups"]
        except: pass
    if "bcb_prop_initPeriod" in scene.keys():
        global initPeriod
        try: initPeriod = props.prop_initPeriod = scene["bcb_prop_initPeriod"]
        except: pass
    if "bcb_prop_initPeriodTimeScale" in scene.keys():
        global initPeriodTimeScale
        try: initPeriodTimeScale = props.prop_initPeriodTimeScale = scene["bcb_prop_initPeriodTimeScale"]
        except: pass
            
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    if "bcb_prop_elemGrps" in scene.keys():
        global elemGrps
        try: elemGrpsProp = scene["bcb_prop_elemGrps"]
        except: pass
        elemGrpsInverted = []
        for i in range(len(elemGrpsProp[0])):
            column = []
            for j in range(len(elemGrpsProp)):
                column.append(elemGrpsProp[j][i])
            missingColumns = len(elemGrps[0]) -len(column)
            if missingColumns:
                print("Error: elemGrp property missing, BCB scene settings are probably outdated.")
                print("Clear all BCB data, double-check your settings and rebuild constraints.")
                ofs = len(column)
                for j in range(missingColumns):
                    column.append(elemGrps[i][ofs +j])
            elemGrpsInverted.append(column)
        elemGrps = elemGrpsInverted
    
################################################################################   

def storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsArea, connectsConsts, constsConnect):
    
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
    if connectsArea != None:
        scene["bcb_connectsArea"] = connectsArea
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

    try: connectsArea = scene["bcb_connectsArea"]
    except: connectsArea = []; print("Error: bcb_connectsArea property not found, rebuilding constraints is required.")

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
        log.append(makeListsPickleFriendly(connectsArea))
        log.append(makeListsPickleFriendly(connectsConsts))
        log.append(makeListsPickleFriendly(constsConnect))
        logDataToFile(log, logPath +r"\log_bcb_keys.txt")
        log = []
        log.append([obj.name for obj in bpy.context.scene.objects])
        logDataToFile(log, logPath +r"\log_bcb_scene.txt")
        
    return objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsArea, connectsConsts, constsConnect

################################################################################   

def clearAllDataFromScene(scene):
    
    ### Clear all data related to Bullet Constraints Builder from scene
    print("\nStarting to clear all data related to Bullet Constraints Builder from scene...")
    time_start = time.time()
    
    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ###### Get data from scene
    print("Getting data from scene...")

    try: objsEGrp = scene["bcb_objsEGrp"]
    except: objsEGrp = []; print("Error: bcb_objsEGrp property not found, cleanup may be incomplete.")

    try: names = scene["bcb_objs"]
    except: names = []; print("Error: bcb_objs property not found, cleanup may be incomplete.")
    objs = []
    for name in names:
        try: objs.append(scnObjs[name])
        except: print("Error: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Error: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: print("Error: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_childObjs"]
    except: names = []; print("Error: bcb_childObjs property not found, cleanup may be incomplete.")
    childObjs = []
    for name in names:
        try: childObjs.append(scnObjs[name])
        except: print("Error: Object %s missing, cleanup may be incomplete." %name)

    try: connectsPairParent = scene["bcb_connectsPairParent"]
    except: connectsPairParent = []; print("Error: bcb_connectsPairParent property not found, cleanup may be incomplete.")
    
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
    except: names = []; print("Error: bcb_objs property not found, cleanup may be incomplete.")
    objs = []
    for name in names:
        try: objs.append(scnObjs[name])
        except: pass #print("Error: Object %s missing, cleanup may be incomplete." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Error: bcb_emptyObjs property not found, cleanup may be incomplete.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: pass #print("Error: Object %s missing, cleanup may be incomplete." %name)

    ### Revert element scaling
    for k in range(len(objs)):
        obj = objs[k]
        scale = elemGrps[objsEGrp[k]][15]
        if scale != 0 and scale != 1:
            obj.scale /= scale

    print("Deleting objects...")
### Original code for object removal (slower):            
#    ### Select modified elements for deletion from scene 
#    for parentObj in parentTmpObjs: parentObj.select = 1
#    ### Select constraint empty objects for deletion from scene
#    for emptyObj in emptyObjs: emptyObj.select = 1
#    
#    ### Delete all selected objects
#    bpy.ops.object.delete(use_global=True)

#    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
#    scene = bpy.context.scene
#    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
#    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
#    bpy.context.screen.scene = scene
#    # Link cameras because in second scene is none and when coming back camera view will losing focus
#    objCameras = []
#    for objTemp in scene.objects:
#        if objTemp.type == 'CAMERA':
#            sceneTemp.objects.link(objTemp)
#            objCameras.append(objTemp)
#    # Switch to new scene
#    bpy.context.screen.scene = sceneTemp

    ### Delete (unlink) modified elements from scene 
    for parentObj in parentTmpObjs: scene.objects.unlink(parentObj)
    ### Delete (unlink) constraint empty objects from scene
    for emptyObj in emptyObjs: scene.objects.unlink(emptyObj)
    
#    # Switch back to original scene
#    bpy.context.screen.scene = scene
#    # Delete second scene
#    bpy.data.scenes.remove(sceneTemp)

    print("Removing ID properties...")
    
    ### Revert selection back to original state and clear ID properties from objects
    for obj in objs:
        obj.select = 1
        # Clear object properties
        for key in obj.keys(): del obj[key]
    
    ### Finally remove ID property build data (leaves menu props in place)
    for key in scene.keys():
        if "bcb_" in key and not "bcb_prop" in key: del scene[key]
   
    # Set layers as in original scene
    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)

    print('\nTime: %0.2f s' %(time.time()-time_start))
    print('Done.')
        
################################################################################   
################################################################################

def monitor_eventHandler(scene):

    ### Check if last frame is reached then stop animation playback
    if scene.frame_current == scene.frame_end:
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_play()
            print('\nTime: %0.2f s' %(time.time()-time_start))
            
    ### Render part
    if qRenderAnimation:
        # Need to disable handler while rendering, otherwise Blender crashes
        bpy.app.handlers.frame_change_pre.pop()
        
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
        
        # Append handler again
        bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)

    #############################
    ### What to do on start frame
    if not "bcb_monitor" in bpy.app.driver_namespace:
        print("Initializing buffers...")
        
        ###### Function
        monitor_initBuffers(scene)

        if initPeriod:
            # Backup original time scale
            bpy.app.driver_namespace["bcb_monitor_originalTimeScale"] = scene.rigidbody_world.time_scale
            bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"] = scene.rigidbody_world.solver_iterations
            if scene.rigidbody_world.time_scale != initPeriodTimeScale:
                ### Decrease precision for solver at extreme scale differences towards high-speed,
                ### as high step and iteration rates on multi-constraint connections make simulation more instable
                ratio = scene.rigidbody_world.time_scale /initPeriodTimeScale
                if ratio >= 50: scene.rigidbody_world.solver_iterations /= 10
                if ratio >= 500: scene.rigidbody_world.solver_iterations /= 10
                if ratio >= 5000: scene.rigidbody_world.solver_iterations /= 10
                ### Set new time scale
                scene.rigidbody_world.time_scale = initPeriodTimeScale
                ###### Execute update of all existing constraints with new time scale
                build()
                        
    ################################
    ### What to do AFTER start frame
    else:
        print("Frame:", scene.frame_current, " ")
        
        ###### Function
        monitor_checkForChange()

        ### Check if intial time period frame is reached then switch time scale and update all constraint settings
        if initPeriod:
            if scene.frame_current == scene.frame_start +initPeriod:
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

def monitor_initBuffers(scene):
    
    if debug: print("Calling initBuffers")
    
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
        try: objs.append(scnObjs[name])
        except: print("Error: Object %s missing, rebuilding constraints is required." %name)

    try: names = scene["bcb_emptyObjs"]
    except: names = []; print("Error: bcb_emptyObjs property not found, rebuilding constraints is required.")
    emptyObjs = []
    for name in names:
        try: emptyObjs.append(scnEmptyObjs[name])
        except: print("Error: Object %s missing, rebuilding constraints is required." %name)

    try: connectsPair = scene["bcb_connectsPair"]
    except: connectsPair = []; print("Error: bcb_connectsPair property not found, rebuilding constraints is required.")

    try: connectsConsts = scene["bcb_connectsConsts"]
    except: connectsConsts = []; print("Error: bcb_connectsConsts property not found, rebuilding constraints is required.")
    
    ### Create original transform data array
    d = 0
    qWarning = 0
    for pair in connectsPair:
        d += 1
        if not qWarning:
            sys.stdout.write('\r' +"%d " %d)
        
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        elemGrpA = objsEGrp[pair[0]]
        elemGrpB = objsEGrp[pair[1]]
        
        # Element group order defines priority for connection type (first preferred over latter) 
        if elemGrpA <= elemGrpB: elemGrp = elemGrpA
        else:                    elemGrp = elemGrpB
        springStiff = elemGrps[elemGrp][9]
        tol1dist = elemGrps[elemGrp][10]
        tol1rot = elemGrps[elemGrp][11]
        tol2dist = elemGrps[elemGrp][12]
        tol2rot = elemGrps[elemGrp][13]
        
        # Calculate distance between both elements of the connection
        distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
        # Calculate angle between two elements
        quat0 = objA.matrix_world.to_quaternion()
        quat1 = objB.matrix_world.to_quaternion()
        angle = quat0.rotation_difference(quat1).angle
        consts = []
        constsBrkTs = []
        constsSprSt = []
        for const in connectsConsts[d -1]:
            emptyObj = emptyObjs[const]
            consts.append(emptyObj)
            if emptyObj.rigid_body_constraint != None and emptyObj.rigid_body_constraint.object1 != None:
                # Backup original breaking thresholds
                constsBrkTs.append(emptyObj.rigid_body_constraint.breaking_threshold)
                # Backup original spring stiffness
                constsSprSt.append([emptyObj.rigid_body_constraint.spring_stiffness_x, emptyObj.rigid_body_constraint.spring_stiffness_y, emptyObj.rigid_body_constraint.spring_stiffness_z])
            else:
                if not qWarning:
                    qWarning = 1
                    print("\rWarning: Element has lost its constraint references or the corresponding empties their constraint properties respectively, rebuilding constraints is recommended.")
                print("(%s)" %emptyObj.name)
                constsBrkTs.append(0)
                constsSprSt.append([0, 0, 0])
        #                0                1                2         3      4       5            6            7            8            9             10            11           12
        connects.append([[objA, pair[0]], [objB, pair[1]], distance, angle, consts, constsBrkTs, constsSprSt, springStiff, tol1dist, tol1rot, tol2dist, tol2rot, 0])

    print("Connections")
        
################################################################################

def monitor_checkForChange():

    if debug: print("Calling checkForDistanceChange")
    
    connects = bpy.app.driver_namespace["bcb_monitor"]
    d = 0; e = 0; cntP = 0; cntB = 0
    for connect in connects:
        sys.stdout.write('\r' +"%d & %d" %(d, e))
        
        ### If connection is in fixed mode then check if plastic tolerance is reached
        if connect[12] == 0:
            d += 1
            objA = connect[0][0]
            objB = connect[1][0]
            springStiff = connect[7]
            toleranceDist = connect[8]
            toleranceRot = connect[9]
            
            # Calculate distance between both elements of the connection
            distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
            if distance > 0: distanceDif = abs(1 -(connect[2] /distance))
            else: distanceDif = 1
            # Calculate angle between two elements
            quatA = objA.matrix_world.to_quaternion()
            quatB = objB.matrix_world.to_quaternion()
            angleDif = math.asin(math.sin( abs(connect[3] -quatA.rotation_difference(quatB).angle) /2))   # The construct "asin(sin(x))" is a triangle function to achieve a seamless rotation loop from input
            # If change in relative distance is larger than tolerance plus change in angle (angle is involved here to allow for bending and buckling)
            if distanceDif > toleranceDist +(angleDif /3.1416) \
            or angleDif > toleranceRot:
                consts = connect[4]
                for const in consts:
                    # Enable spring constraints for this connection by setting its stiffness
                    if const.rigid_body_constraint.type == 'GENERIC_SPRING':
                        const.rigid_body_constraint.spring_stiffness_x = springStiff
                        const.rigid_body_constraint.spring_stiffness_y = springStiff
                        const.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Disable non-spring constraints for this connection by setting breaking threshold to 0
                    else:
                        const.rigid_body_constraint.breaking_threshold = 0
                # Switch connection to plastic mode
                connect[12] += 1
                cntP += 1

        ### If connection is in plastic mode then check if breaking tolerance is reached
        if connect[12] == 1:
            e += 1
            objA = connect[0][0]
            objB = connect[1][0]
            toleranceDist = connect[10]
            toleranceRot = connect[11]
            
            # Calculate distance between both elements of the connection
            distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
            if distance > 0: distanceDif = abs(1 -(connect[2] /distance))
            else: distanceDif = 1
            # Calculate angle between two elements
            quatA = objA.matrix_world.to_quaternion()
            quatB = objB.matrix_world.to_quaternion()
            angleDif = math.asin(math.sin( abs(connect[3] -quatA.rotation_difference(quatB).angle) /2))   # The construct "asin(sin(x))" is a triangle function to achieve a seamless rotation loop from input
            # If change in relative distance is larger than tolerance plus change in angle (angle is involved here to allow for bending and buckling)
            if distanceDif > toleranceDist +(angleDif /3.1416) \
            or angleDif > toleranceRot:
                # Disable all constraints for this connection by setting breaking threshold to 0
                consts = connect[4]
                for const in consts:
                    const.rigid_body_constraint.breaking_threshold = 0
                # Flag connection as being disconnected
                connect[12] += 1
                cntB += 1
        
    sys.stdout.write(" connections (intact & plastic)")
    if cntP > 0: sys.stdout.write(" | Plastic: %d" %cntP)
    if cntB > 0: sys.stdout.write(" | Broken: %d" %cntB)
    print()
                
################################################################################

def monitor_freeBuffers(scene):
    
    if debug: print("Calling freeBuffers")
    
    connects = bpy.app.driver_namespace["bcb_monitor"]
    ### Restore original constraint and element data
    qWarning = 0
    for connect in connects:
        consts = connect[4]
        constsBrkTs = connect[5]
        constsSprSt = connect[6]
        for i in range(len(consts)):
            emptyObj = consts[i]
            if emptyObj.rigid_body_constraint != None and emptyObj.rigid_body_constraint.object1 != None:
                # Restore original breaking thresholds
                emptyObj.rigid_body_constraint.breaking_threshold = constsBrkTs[i]
                # Restore original spring settings
                if emptyObj.rigid_body_constraint.type == 'GENERIC_SPRING':
                    emptyObj.rigid_body_constraint.spring_stiffness_x = constsSprSt[i][0]
                    emptyObj.rigid_body_constraint.spring_stiffness_y = constsSprSt[i][1]
                    emptyObj.rigid_body_constraint.spring_stiffness_z = constsSprSt[i][2]
            else:
                if not qWarning:
                    qWarning = 1
                    print("\rWarning: Element has lost its constraint references or the corresponding empties their constraint properties respectively, rebuilding constraints is recommended.")
                print("(%s)" %emptyObj.name)
            
    if initPeriod:
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
    if initPeriod:
        del bpy.app.driver_namespace["bcb_monitor_originalTimeScale"]
        del bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"]

################################################################################

def estimateClusterRadius(scene):
    
    objs, emptyObjs = gatherObjects(scene)
    
    if len(objs) > 0:        
        print("Estimating optimal cluster radius...")
        
        #objsDiameter = []
        diameterSum = 0
        for obj in objs:
            
            ### Calculate diameter for each object
            dim = list(obj.dimensions)
            dim.sort()
            diameter = dim[2]   # Use the largest dimension axis as diameter
            
            #objsDiameter.append(diameter)
            diameterSum += diameter
        
#        ### Sort all diameters, take the midst item and multiply it by 1 /sqrt(2)
#        objsDiameter.sort()
#        diameterEstimation = (objsDiameter[int(len(objsDiameter) /2)] /2) *0.707

        ### Alternative: Calculate average of all object diameters and multiply it by 1 /sqrt(2)
        diameterEstimation = ((diameterSum /2) /len(objs)) *0.707
        
        return diameterEstimation

    else:
        print("Selected objects required for cluster radius estimation.") 
        return 0
 
################################################################################
################################################################################

class bcb_props(bpy.types.PropertyGroup):
    int = bpy.props.IntProperty 
    float = bpy.props.FloatProperty
    bool = bpy.props.BoolProperty
    string = bpy.props.StringProperty
    
    prop_menu_gotConfig = int(0)
    prop_menu_gotData = int(0)
    prop_menu_selectedItem = int(0)
    prop_menu_advancedG = bool(0)
    prop_menu_advancedE = bool(0)

    prop_stepsPerSecond = int(name="Steps Per Second", default=stepsPerSecond, min=1, max=32767, description="Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable).")
    prop_constraintUseBreaking = bool(name="Enable Breaking", default=constraintUseBreaking, description="Enables breaking for all constraints.")
    prop_connectionCountLimit = int(name="Con. Count Limit", default=connectionCountLimit, min=0, max=10000, description="Maximum count of connections per object pair (0 = disabled).")
    prop_searchDistance = float(name="Search Distance", default=searchDistance, min=0.0, max=1000, description="Search distance to neighbor geometry.")
    prop_clusterRadius = float(name="Cluster Radius", default=clusterRadius, min=0.0, max=1000, description="Radius for bundling close constraints into clusters (0 = clusters disabled).")
    prop_alignVertical = float(name="Vertical Alignment", default=alignVertical, min=0.0, max=1.0, description="Enables a vertical alignment multiplier for connection type 4 or above instead of using unweighted center to center orientation (0 = disabled, 1 = fully vertical).")
    prop_useAccurateArea = bool(name="Accur. Contact Area Calculation", default=useAccurateArea , description="Enables accurate contact area calculation using booleans for the cost of an slower building process. This only works correct with solids i.e. watertight and manifold objects and is therefore recommended for truss structures or steel constructions in general.")
    prop_nonManifoldThickness = float(name="Non-solid Thickness", default=nonManifoldThickness, min=0.0, max=10, description="Thickness for non-manifold elements (surfaces) when using accurate contact area calculation.")
    prop_minimumElementSize = float(name="Min. Element Size", default=minimumElementSize, min=0.0, max=10, description="Deletes connections whose elements are below this diameter and makes them parents instead. This can be helpful for increasing performance on models with unrelevant geometric detail such as screwheads.")
    prop_automaticMode = bool(name="Automatic Mode", default=automaticMode, description="Enables a fully automated workflow for extremely large simulations (object count-wise) were Blender is prone to not being responsive anymore. After clicking Build these steps are being done automatically: Building of constraints, baking simulation, clearing constraint and BCB data from scene.")
    prop_saveBackups = bool(name="Backup", default=saveBackups, description="Enables saving of a backup .blend file after each step for automatic mode, whereby the name of the new .blend ends with `_BCB´.")
    prop_initPeriod = int(name="Initial Time Period", default=initPeriod, min=0, max=10000, description="For baking: Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled).")
    prop_initPeriodTimeScale = float(name="Initial Time Scale", default=initPeriodTimeScale, min=0.0, max=100, description="For baking: Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime.")
    
    for i in range(maxMenuElementGroupItems):
        if i < len(elemGrps): j = i
        else: j = 0
        exec("prop_elemGrp_%d_0" %i +" = string(name='Grp. Name', default=elemGrps[j][0], description='The name of the element group.')")
        exec("prop_elemGrp_%d_4" %i +" = int(name='Connection Type', default=elemGrps[j][4], min=1, max=1000, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code.')")
        exec("prop_elemGrp_%d_5" %i +" = float(name='Compressive', default=elemGrps[j][5], min=0.0, max=10000, description='Real world material compressive breaking threshold in N/mm^2.')")
        exec("prop_elemGrp_%d_6" %i +" = float(name='Tensile', default=elemGrps[j][6], min=0.0, max=10000, description='Real world material tensile breaking threshold in N/mm^2.')")
        exec("prop_elemGrp_%d_7" %i +" = float(name='Shear', default=elemGrps[j][7], min=0.0, max=10000, description='Real world material shearing breaking threshold in N/mm^2.')")
        exec("prop_elemGrp_%d_8" %i +" = float(name='Bend', default=elemGrps[j][8], min=0.0, max=10000, description='Real world material bending breaking threshold in N/mm^2.')")
        exec("prop_elemGrp_%d_9" %i +" = float(name='Spring Stiffness', default=elemGrps[j][9], min=0.0, max=10**20, description='Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.')")
        exec("prop_elemGrp_%d_1" %i +" = int(name='Req. Vertex Pairs', default=elemGrps[j][1], min=0, max=100, description='How many vertex pairs between two elements are required to generate a connection.')")
        exec("prop_elemGrp_%d_2" %i +" = string(name='Mat. Preset', default=elemGrps[j][2], description='Preset name of the physical material to be used from BlenderJs internal database. See Blenders Rigid Body Tools for a list of available presets.')")
        exec("prop_elemGrp_%d_3" %i +" = float(name='Density', default=elemGrps[j][3], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("prop_elemGrp_%d_10" %i +" = float(name='Dist. Tol. Plastic', default=elemGrps[j][10], min=0.0, max=10.0, description='For baking: Allowed tolerance for distance change in percent for plastic deformation (1.00 = 100 %).')")
        exec("prop_elemGrp_%d_11" %i +" = float(name='Rot. Tol. Plastic', default=elemGrps[j][11], min=0.0, max=3.14159, description='For baking: Allowed tolerance for angular change in radian for plastic deformation.')")
        exec("prop_elemGrp_%d_12" %i +" = float(name='Dist. Tol. Break', default=elemGrps[j][12], min=0.0, max=10.0, description='For baking: Allowed tolerance for distance change in percent for connection removal (1.00 = 100 %).')")
        exec("prop_elemGrp_%d_13" %i +" = float(name='Rot. Tol. Break', default=elemGrps[j][13], min=0.0, max=3.14159, description='For baking: Allowed tolerance for angular change in radian for connection removal.')")
        exec("prop_elemGrp_%d_14" %i +" = bool(name='Bevel', default=elemGrps[j][14], description='Enables beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_15" %i +" = float(name='Rescale Factor', default=elemGrps[j][15], min=0.0, max=1, description='Applies scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_16" %i +" = bool(name='Facing', default=elemGrps[j][16], description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation).')")

    def props_update_menu(self):
        ### Update menu related properties from global vars
        for i in range(len(elemGrps)):
            exec("self.prop_elemGrp_%d_0" %i +" = elemGrps[i][0]")
            exec("self.prop_elemGrp_%d_1" %i +" = elemGrps[i][1]")
            exec("self.prop_elemGrp_%d_2" %i +" = elemGrps[i][2]")
            exec("self.prop_elemGrp_%d_3" %i +" = elemGrps[i][3]")
            exec("self.prop_elemGrp_%d_4" %i +" = elemGrps[i][4]")
            exec("self.prop_elemGrp_%d_5" %i +" = elemGrps[i][5]")
            exec("self.prop_elemGrp_%d_6" %i +" = elemGrps[i][6]")
            exec("self.prop_elemGrp_%d_7" %i +" = elemGrps[i][7]")
            exec("self.prop_elemGrp_%d_8" %i +" = elemGrps[i][8]")
            exec("self.prop_elemGrp_%d_9" %i +" = elemGrps[i][9]")
            exec("self.prop_elemGrp_%d_10" %i +" = elemGrps[i][10]")
            exec("self.prop_elemGrp_%d_11" %i +" = elemGrps[i][11]")
            exec("self.prop_elemGrp_%d_12" %i +" = elemGrps[i][12]")
            exec("self.prop_elemGrp_%d_13" %i +" = elemGrps[i][13]")
            exec("self.prop_elemGrp_%d_14" %i +" = elemGrps[i][14]")
            exec("self.prop_elemGrp_%d_15" %i +" = elemGrps[i][15]")
            exec("self.prop_elemGrp_%d_16" %i +" = elemGrps[i][16]")
           
    def props_update_globals(self):
        ### Update global vars from menu related properties
        global stepsPerSecond; stepsPerSecond = self.prop_stepsPerSecond
        global constraintUseBreaking; constraintUseBreaking = self.prop_constraintUseBreaking
        global connectionCountLimit; connectionCountLimit = self.prop_connectionCountLimit
        global searchDistance; searchDistance = self.prop_searchDistance
        global clusterRadius; clusterRadius = self.prop_clusterRadius
        global alignVertical; alignVertical = self.prop_alignVertical
        global useAccurateArea; useAccurateArea = self.prop_useAccurateArea
        global nonManifoldThickness; nonManifoldThickness = self.prop_nonManifoldThickness
        global minimumElementSize; minimumElementSize = self.prop_minimumElementSize
        global automaticMode; automaticMode = self.prop_automaticMode
        global saveBackups; saveBackups = self.prop_saveBackups
        global initPeriod; initPeriod = self.prop_initPeriod
        global initPeriodTimeScale; initPeriodTimeScale = self.prop_initPeriodTimeScale
        global elemGrps
        for i in range(len(elemGrps)):
            elemGrpNew = []
            for j in range(len(elemGrps[i])):
                elemGrpNew.append(eval("self.prop_elemGrp_%d_%d" %(i, j)))
            elemGrps[i] = elemGrpNew

           
class bcb_panel(bpy.types.Panel):
    bl_label = "Bullet Constraints Builder"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" 

    def icon(self, bool):
        if bool: return 'TRIA_DOWN'
        else: return 'TRIA_RIGHT'

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.bcb
        obj = context.object
        scene = bpy.context.scene
        
        row = layout.row()
        if not props.prop_menu_gotData: 
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.build", icon="MOD_SKIN")
            split2 = split.split(align=False)
            if not props.prop_menu_gotConfig:
                if "bcb_prop_elemGrps" in scene.keys():
                      split2.operator("bcb.get_config", icon="FILE_REFRESH")
                else: split2.operator("bcb.set_config", icon="NEW")
            else:
                split2.operator("bcb.set_config", icon="NEW")
        else:
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split.operator("bcb.clear", icon="CANCEL")
        row = layout.row()
        split = row.split(percentage=.50, align=False)
        split.operator("bcb.bake", icon="REC")
        split.prop(props, "prop_stepsPerSecond")
        
        layout.separator()
        row = layout.row(); row.prop(props, "prop_constraintUseBreaking")
        row = layout.row()
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_searchDistance")
        
        row = layout.row()
        split = row.split(percentage=.85, align=False)
        if props.prop_menu_gotData: split.enabled = 0
        split.prop(props, "prop_clusterRadius")
        split.operator("bcb.estimate_cluster_radius", icon="AUTO")
        
        ###### Advanced main settings box
        
        layout.separator()
        box = layout.box()
        box.prop(props, "prop_menu_advancedG", text="Advanced Global Settings", icon=self.icon(props.prop_menu_advancedG), emboss = False)

        if props.prop_menu_advancedG:
            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "prop_automaticMode")
            split.prop(props, "prop_saveBackups")
            
            row = box.row(); row.prop(props, "prop_alignVertical")
            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_connectionCountLimit")
            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_minimumElementSize")

            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_useAccurateArea")
#            row = box.row()
#            if not props.prop_useAccurateArea: row.enabled = 0
#            row.prop(props, "prop_nonManifoldThickness")

            row = box.row(); row.prop(props, "prop_initPeriod")
            row = box.row(); row.prop(props, "prop_initPeriodTimeScale")
            if props.prop_initPeriod == 0: row.enabled = 0
            
            box.separator()
            row = box.row(); row.operator("bcb.export_ascii", icon="EXPORT")
        
        ###### Element groups box
        
        layout.separator()
        row = layout.row(); row.label(text="Element Groups", icon="MOD_BUILD")
        box = layout.box()
        row = box.split(align=False)
        row.operator("bcb.add", icon="ZOOMIN")
        row.operator("bcb.del", icon="X")
        row.operator("bcb.reset", icon="CANCEL")
        row.operator("bcb.move_up", icon="TRIA_UP")
        row.operator("bcb.move_down", icon="TRIA_DOWN")
        row = box.row()
        split = row.split(percentage=.25, align=False)
        split.label(text="GRP")
        split2 = split.split(align=False)
        split2.label(text="CT")
        split2.label(text="CPR")
        split2.label(text="TNS")
        split2.label(text="SHR")
        split2.label(text="BND")
        for i in range(len(elemGrps)):
            if i == props.prop_menu_selectedItem:
                  row = box.box().row()
            else: row = box.row()
            elemGrp0 = eval("props.prop_elemGrp_%d_0" %i)
            elemGrp4 = ct = eval("props.prop_elemGrp_%d_4" %i)
            try: connectType = connectTypes[ct]
            except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
            if not connectType[2][0]: elemGrp5 = "-"
            else: elemGrp5 = eval("props.prop_elemGrp_%d_5" %i)
            if not connectType[2][1]: elemGrp6 = "-"
            else: elemGrp6 = eval("props.prop_elemGrp_%d_6" %i)
            if not connectType[2][2]: elemGrp7 = "-"
            else: elemGrp7 = eval("props.prop_elemGrp_%d_7" %i)
            if not connectType[2][3]: elemGrp8 = "-"
            else: elemGrp8 = eval("props.prop_elemGrp_%d_8" %i)
            split = row.split(percentage=.25, align=False)
            if elemGrp0 == "": split.label(text="[Def.]")
            else:              split.label(text=str(elemGrp0))
            split2 = split.split(align=False)
            split2.label(text=str(elemGrp4))
            split2.label(text=str(elemGrp5))
            split2.label(text=str(elemGrp6))
            split2.label(text=str(elemGrp7))
            split2.label(text=str(elemGrp8))
        row = box.row()
        row.operator("bcb.up", icon="TRIA_UP")
        row.operator("bcb.down", icon="TRIA_DOWN")
        
        ###### Element group setting
        
        layout.separator()
        i = props.prop_menu_selectedItem
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_0" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_4" %i)
        if props.prop_menu_gotData: row.enabled = 0
            
        ct = eval("props.prop_elemGrp_%d_4" %i)
        try: connectType = connectTypes[ct]
        except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
        box = layout.box();
        box.label(text=connectType[0])
        
        row = layout.row(); row.label(text="Breaking Thresholds:")
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_5" %i)
        if not connectType[2][0]: row.active = 0
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_6" %i)
        if not connectType[2][1]: row.active = 0
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_7" %i)
        if not connectType[2][2]: row.active = 0
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_8" %i)
        if not connectType[2][3]: row.active = 0

        layout.separator()
        #row = layout.row(); row.prop(props, "prop_elemGrp_%d_1" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_2" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_3" %i)
        
        layout.separator()
        row = layout.row()
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_15" %i)
        row = layout.row()
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_14" %i)
        elemGrp14 = eval("props.prop_elemGrp_%d_14" %i)
        elemGrp16 = eval("props.prop_elemGrp_%d_16" %i)
        if elemGrp14 and not elemGrp16: row.alert = 1
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_16" %i)
        
        if elemGrp14 and not elemGrp16:
            row = layout.row(); row.label(text="Warning: Disabled facing")
            row = layout.row(); row.label(text="makes bevel permanent!")
            
        ###### Advanced element group settings box
        
        box = layout.box()
        box.prop(props, "prop_menu_advancedE", text="Advanced Element Settings", icon=self.icon(props.prop_menu_advancedE), emboss = False)

        if props.prop_menu_advancedE:
            elemGrp9 = eval("props.prop_elemGrp_%d_9" %i)
            elemGrp10 = eval("props.prop_elemGrp_%d_10" %i)
            elemGrp11 = eval("props.prop_elemGrp_%d_11" %i)
            elemGrp12 = eval("props.prop_elemGrp_%d_12" %i)
            elemGrp13 = eval("props.prop_elemGrp_%d_13" %i)
            
            row = box.row(); row.prop(props, "prop_elemGrp_%d_9" %i)
            if not connectType[2][4]: row.active = 0
            row = box.row(); row.label(text="Plastic & Breaking Tolerances:")
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "prop_elemGrp_%d_10" %i)
            split.prop(props, "prop_elemGrp_%d_11" %i)
            if not connectType[2][5]: split.active = 0
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "prop_elemGrp_%d_12" %i)
            split.prop(props, "prop_elemGrp_%d_13" %i)
            if not connectType[2][7]: split.active = 0
            
        # Update global vars from menu related properties
        props.props_update_globals()
 
         
class OBJECT_OT_bcb_set_config(bpy.types.Operator):
    bl_idname = "bcb.set_config"
    bl_label = ""
    bl_description = "Stores actual config data in current scene."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Store menu config data in scene
        storeConfigDataInScene(scene)
        props.prop_menu_gotConfig = 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_get_config(bpy.types.Operator):
    bl_idname = "bcb.get_config"
    bl_label = ""
    bl_description = "Loads previous config data from current scene."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        if "bcb_prop_elemGrps" in scene.keys():
            ###### Get menu config data from scene
            getConfigDataFromScene(scene)
            # Update menu related properties from global vars
            props.props_update_menu()
            props.prop_menu_gotConfig = 1
        if "bcb_objs" in scene.keys():
            ###### Get menu config data from scene
            getBuildDataFromScene(scene)
            props.prop_menu_gotData = 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_clear(bpy.types.Operator):
    bl_idname = "bcb.clear"
    bl_label = ""
    bl_description = "Clears constraints from scene and revert back to original state (required to rebuild constraints from scratch)."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Clear all data from scene and delete also constraint empty objects
        if "bcb_objs" in scene.keys(): clearAllDataFromScene(scene)
        props.prop_menu_gotData = 0
        return{'FINISHED'} 
        
class OBJECT_OT_bcb_build(bpy.types.Operator):
    bl_idname = "bcb.build"
    bl_label = "Build"
    bl_description = "Starts building process and adds constraints to selected elements."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        # Go to start frame for cache data removal
        scene.frame_current = scene.frame_start
        ### Free previous bake data
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.free_bake(contextFix)
        ### Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            obj.location = obj.location
        ###### Execute main building process from scratch
        build()
        props.prop_menu_gotData = 1
        ### For automatic mode autorun the next step
        if automaticMode:
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
            OBJECT_OT_bcb_bake.execute(self, context)
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
            OBJECT_OT_bcb_clear.execute(self, context)
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        return{'FINISHED'} 

class OBJECT_OT_bcb_update(bpy.types.Operator):
    bl_idname = "bcb.update"
    bl_label = "Update"
    bl_description = "Updates constraints generated from a previous built."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        # Go to start frame for cache data removal
        scene.frame_current = scene.frame_start
        ### Free previous bake data
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.free_bake(contextFix)
        ### Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            obj.location = obj.location
        ###### Execute update of all existing constraints with new settings
        build()
        # Update menu related properties from global vars
        props.props_update_menu()
        ### For automatic mode autorun the next step
        if automaticMode:
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
            OBJECT_OT_bcb_bake.execute(self, context)
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
            OBJECT_OT_bcb_clear.execute(self, context)
            if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        return{'FINISHED'} 

class OBJECT_OT_bcb_export_ascii(bpy.types.Operator):
    bl_idname = "bcb.export_ascii"
    bl_label = "Build & export to text file"
    bl_description = "Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment)."
    def execute(self, context):
        global asciiExport
        asciiExport = 1
        ###### Execute main building process from scratch
        build()
        asciiExport = 0
        return{'FINISHED'} 

class OBJECT_OT_bcb_bake(bpy.types.Operator):
    bl_idname = "bcb.bake"
    bl_label = "Bake"
    bl_description = "Bakes simulation. Use of this button is crucial if connection type 4 or above is used, because then constraints require monitoring on per frame basis during simulation."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ### Only start baking when we have constraints set
        if props.prop_menu_gotData:
            print('Init BCB monitor event handler.')
            bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
            ### Free previous bake data
            contextFix = bpy.context.copy()
            contextFix['point_cache'] = scene.rigidbody_world.point_cache
            bpy.ops.ptcache.free_bake(contextFix)
            ### Invalidate point cache to enforce a full bake without using previous cache data
            if "RigidBodyWorld" in bpy.data.groups:
                obj = bpy.data.groups["RigidBodyWorld"].objects[0]
                obj.location = obj.location
            # Invoke baking
            bpy.ops.ptcache.bake(contextFix, bake=True)
            print('Removing BCB monitor event handler.')
            for i in range( len( bpy.app.handlers.frame_change_pre ) ):
                 bpy.app.handlers.frame_change_pre.pop()
            monitor_freeBuffers(scene)
        ### Otherwise build constraints if required
        else:
            OBJECT_OT_bcb_build.execute(self, context)
            # Skip baking for automatic mode as it is already called in bcb.build
            if not automaticMode: OBJECT_OT_bcb_bake.execute(self, context)
        return{'FINISHED'} 

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = ""
    bl_description = "Adds element group to list."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        if len(elemGrps) < maxMenuElementGroupItems:
            # Add element group (syncing element group indices happens on execution)
            elemGrps.append(elemGrps[props.prop_menu_selectedItem])
            # Update menu selection
            props.prop_menu_selectedItem = len(elemGrps) -1
        else: self.report({'ERROR'}, "Maximum allowed element group count reached.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_del(bpy.types.Operator):
    bl_idname = "bcb.del"
    bl_label = ""
    bl_description = "Deletes element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        if len(elemGrps) > 1:
            # Remove element group (syncing element group indices happens on execution)
            elemGrps.remove(elemGrps[props.prop_menu_selectedItem])
            # Update menu selection
            if props.prop_menu_selectedItem >= len(elemGrps):
                props.prop_menu_selectedItem = len(elemGrps) -1
        else: self.report({'ERROR'}, "At least one element group is required.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_move_up(bpy.types.Operator):
    bl_idname = "bcb.move_up"
    bl_label = ""
    bl_description = "Moves element group in list (the order defines priority for conflicting connection settings)."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        if props.prop_menu_selectedItem > 0:
            swapItem = props.prop_menu_selectedItem -1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.prop_menu_selectedItem] = elemGrps[props.prop_menu_selectedItem], elemGrps[swapItem]
            # Also move menu selection
            props.prop_menu_selectedItem -= 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_move_down(bpy.types.Operator):
    bl_idname = "bcb.move_down"
    bl_label = ""
    bl_description = "Moves element group in list (the order defines priority for conflicting connection settings)."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        if props.prop_menu_selectedItem < len(elemGrps) -1:
            swapItem = props.prop_menu_selectedItem +1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.prop_menu_selectedItem] = elemGrps[props.prop_menu_selectedItem], elemGrps[swapItem]
            # Also move menu selection
            props.prop_menu_selectedItem += 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_up(bpy.types.Operator):
    bl_idname = "bcb.up"
    bl_label = " Previous"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedItem > 0:
            props.prop_menu_selectedItem -= 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_down(bpy.types.Operator):
    bl_idname = "bcb.down"
    bl_label = " Next"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedItem < len(elemGrps) -1:
            props.prop_menu_selectedItem += 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_reset(bpy.types.Operator):
    bl_idname = "bcb.reset"
    bl_label = ""
    bl_description = "Resets element group list to defaults."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        # Overwrite element group with original backup (syncing element group indices happens on execution)
        elemGrps = elemGrpsBak.copy()
        # Update menu selection
        props.prop_menu_selectedItem = 0
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_estimate_cluster_radius(bpy.types.Operator):
    bl_idname = "bcb.estimate_cluster_radius"
    bl_label = ""
    bl_description = "Estimate optimal cluster radius from selected objects in scene (even if you already have built a BCB structure only selected objects are considered)."
    def execute(self, context):
        scene = bpy.context.scene
        result = estimateClusterRadius(scene)
        if result > 0:
            props = context.window_manager.bcb
            props.prop_clusterRadius = result
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'}

classes = [ \
    bcb_props,
    bcb_panel,
    OBJECT_OT_bcb_set_config,
    OBJECT_OT_bcb_get_config,
    OBJECT_OT_bcb_clear,
    OBJECT_OT_bcb_build,
    OBJECT_OT_bcb_update,
    OBJECT_OT_bcb_export_ascii,
    OBJECT_OT_bcb_bake,
    OBJECT_OT_bcb_add,
    OBJECT_OT_bcb_del,
    OBJECT_OT_bcb_move_up,
    OBJECT_OT_bcb_move_down,
    OBJECT_OT_bcb_up,
    OBJECT_OT_bcb_down,
    OBJECT_OT_bcb_reset,
    OBJECT_OT_bcb_estimate_cluster_radius
    ]      
          
################################################################################   
################################################################################   

def initGeneralRigidBodyWorldSettings(scene):

    ### Set general rigid body world settings
    # Set FPS rate for rigid body simulation (from Blender preset)
    scene.render.fps = 25
    scene.render.fps_base = 1
    # Set Steps Per Second for rigid body simulation
    scene.rigidbody_world.steps_per_second = stepsPerSecond
    # Set Split Impulse for rigid body simulation
    #scene.rigidbody_world.use_split_impulse = True

################################################################################   

def createElementGroupIndex(objs):

    ### Create a list about which object belongs to which element group
    objsEGrp = []
    for obj in objs:
        objGrpsTmp = []
        for elemGrp in elemGrps:
            elemGrpName = elemGrp[0]
            if elemGrpName in bpy.data.groups:
                if obj.name in bpy.data.groups[elemGrpName].objects:
                    objGrpsTmp.append(elemGrps.index(elemGrp))
        if len(objGrpsTmp) > 1:
            print("\nWarning: Object %s belongs to more than one element group, defaults are used." %obj.name)
            q = 1
        elif len(objGrpsTmp) == 0: q = 1
        else: q = 0
        if q:
            for elemGrp in elemGrps:
                elemGrpName = elemGrp[0]
                if elemGrpName == '':
                    objGrpsTmp = [elemGrps.index(elemGrp)]
                    break
        objsEGrp.append(objGrpsTmp[0])
        
    return objsEGrp

########################################

def gatherObjects(scene):

    ### Create object lists of selected objects
    print("Creating object lists of selected objects...")
    
    objs = []
    emptyObjs = []
    for obj in bpy.data.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            # Clear object properties
            #for key in obj.keys(): del obj[key]
            # Detect if mesh or empty (constraint)
            if obj.type == 'MESH' and len(obj.data.vertices) > 0:  # obj.rigid_body != None
                objs.append(obj)
            elif obj.type == 'EMPTY' and obj.rigid_body_constraint != None:
                sys.stdout.write('\r' +"%s      " %obj.name)
                emptyObjs.append(obj)
    
    return objs, emptyObjs

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

def findConnectionsByVertexPairs(objs, objsEGrp):
    
    ### Find connections by vertex pairs
    print("Searching connections by vertex pairs... (%d)" %len(objs))
    
    ### Build kd-tree for object locations
    kdObjs = mathutils.kdtree.KDTree(len(objs))
    for i, obj in enumerate(objs):
        kdObjs.insert(obj.location, i)
    kdObjs.balance()
    
    ### Build kd-trees for every object's vertices
    kdsMeComp = []
    for obj in objs:
        me = obj.data
        mat = obj.matrix_world
        
        kd = mathutils.kdtree.KDTree(len(me.vertices))
        for i, v in enumerate(me.vertices):
            loc = mat *v.co    # Multiply matrix by vertex coordinates to get global coordinates
            kd.insert(loc, i)
        kd.balance()
        kdsMeComp.append(kd)
                        
    ### Find connections by vertex pairs
    connectsPair = []          # Stores both connected objects indices per connection
    connectsPairDist = []      # Stores distance between both elements
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        qNextObj = 0
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []; aDist = [] #; aCo = [] 
        if connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index); aDist.append(dist) #; aCo.append(co)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index); aDist.append(dist) #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:] # Remove first item because it's the same as co_find (zero distance)
        
        ### Walk through current object vertices
        for m in range(len(me.vertices)):
            vert = me.vertices[m]
            co_find = mat *vert.co     # Multiply matrix by vertex coordinates to get global coordinates
                        
            # Loop through comparison object found
            for j in range(len(aIndex)):
                l = aIndex[j]
                
                # Skip same object index
                if k != l:
                    # Use object specific vertex kd-tree
                    kdMeComp = kdsMeComp[l]
                    
                    ### Find closest vertices via kd-tree in comparison object
                    if len(kdMeComp.find_range(co_find, searchDistance)) > 0:   # If vert is within search range add connection to sublist
                        coComp = kdMeComp.find(co_find)[0]    # Find coordinates of the closest vertex
                        co = (co_find +coComp) /2             # Calculate center of both vertices
                        
                        ### Store connection if not already existing
                        connectCnt = 0
                        pair = [k, l]
                        pair.sort()
                        if pair not in connectsPair:
                            connectsPair.append(pair)
                            connectsPairDist.append(aDist[j])
                            connectCnt += 1
                            if connectCnt == connectionCountLimit:
                                if elemGrps[objsEGrp[k]][1] <= 1:
                                    qNextObj = 1
                                    break
                            
            if qNextObj: break
        
    print()
    return connectsPair, connectsPairDist

################################################################################   

def findConnectionsByBoundaryBoxIntersection(objs):
    
    ### Find connections by boundary box intersection
    print("Searching connections by boundary box intersection... (%d)" %len(objs))
    
    ### Build kd-tree for object locations
    kdObjs = mathutils.kdtree.KDTree(len(objs))
    for i, obj in enumerate(objs):
        kdObjs.insert(obj.location, i)
    kdObjs.balance()
    
    ### Precalculate boundary boxes for all objects
    bboxes = []
    for obj in objs:
        # Calculate boundary box corners
        bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
        # Extend boundary box dimensions by searchDistance
        bbMin -= Vector((searchDistance, searchDistance, searchDistance))
        bbMax += Vector((searchDistance, searchDistance, searchDistance))
        bboxes.append([bbMin, bbMax])
    
    ### Find connections by vertex pairs
    connectsPair = []          # Stores both connected objects indices per connection
    connectsPairDist = []      # Stores distance between both elements
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []; aDist = [] #; aCo = [] 
        if connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index); aDist.append(dist) #; aCo.append(co)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index); aDist.append(dist) #; aCo.append(co) 
        aIndex = aIndex[1:]; aDist = aDist[1:]  # Remove first item because it's the same as co_find (zero distance)
    
        # Loop through comparison objects found
        for j in range(len(aIndex)):
            l = aIndex[j]
            
            # Skip same object index
            if k != l:
                bbAMin, bbAMax = bboxes[k]
                bbBMin, bbBMax = bboxes[l]
                ### Calculate overlap per axis of both intersecting boundary boxes
                overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
                overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
                overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
                # Calculate volume
                volume = overlapX *overlapY *overlapZ
                if volume > 0:                
                    ### Store connection if not already existing
                    connectCnt = 0
                    pair = [k, l]
                    pair.sort()
                    if pair not in connectsPair:
                        connectsPair.append(pair)
                        connectsPairDist.append(aDist[j])
                        connectCnt += 1
                        if connectCnt == connectionCountLimit: break
    
    print("\nPossible connections found:", len(connectsPair))
    return connectsPair, connectsPairDist

################################################################################   

def deleteConnectionsWithTooSmallElementsAndParentThemInstead(objs, connectsPair, connectsPairDist):
    
    ### Delete connections whose elements are too small and make them parents instead
    print("Make parents for too small elements and remove them as connections...")
    
    connectsPairTmp = []
    connectsPairParent = []
    connectsPairParentDist = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for k in range(len(connectsPair)):
        objA_idx = connectsPair[k][0]
        objB_idx = connectsPair[k][1]
        dist = connectsPairDist[k]
        objA = objs[objA_idx]
        objB = objs[objB_idx]
        objA_dim = list(objA.dimensions)
        objA_dim.sort()
        objA_dim = objA_dim[2]   # Use largest dimension axis as size
        objB_dim = list(objB.dimensions)
        objB_dim.sort()
        objB_dim = objB_dim[2]   # Use largest dimension axis as size
        if (objA_dim > minimumElementSize and objB_dim > minimumElementSize) \
        or (objA_dim <= minimumElementSize and objB_dim <= minimumElementSize):
            connectsPairTmp.append(connectsPair[k])
            connectCnt += 1
        elif objA_dim <= minimumElementSize:
            connectsPairParent.append([objA_idx, objB_idx])  # First child, second parent
            connectsPairParentDist.append(dist)
        elif objB_dim <= minimumElementSize:
            connectsPairParent.append([objB_idx, objA_idx])  # First child, second parent
            connectsPairParentDist.append(dist)
    connectsPair = connectsPairTmp
    
    # Sort list into the order of distance between elements
    if len(connectsPairParent) > 1:
        connectsPairParentDist, connectsPairParent = zip(*sorted(zip(connectsPairParentDist, connectsPairParent)))
    
    ### Filter out children doubles because each children can only have one parent, other connections are discarded
    checkList = []
    connectsPairParentTmp = []
    for item in connectsPairParent:
        if item[0] not in checkList:
            connectsPairParentTmp.append(item)
            checkList.append(item[0])
    connectsPairParent = connectsPairParentTmp
    
    print("Connections converted and removed:", len(connectsPairParent))
    return connectsPair, connectsPairParent

################################################################################   

def makeParentsForTooSmallElementsReal(objs, connectsPairParent):
    
    ### Create actual parents for too small elements
    print("Creating actual parents for too small elements... (%d)" %len(connectsPairParent))
    
    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    objCameras = []
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            sceneTemp.objects.link(objTemp)
            objCameras.append(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    ### Make parents
    for k in range(len(connectsPairParent)):
        sys.stdout.write('\r' +"%d" %k)
        
        objChild = objs[connectsPairParent[k][0]]
        objParent = objs[connectsPairParent[k][1]]

        # Link objects we're working on to second scene (we try because of the object unlink workaround)
        try: sceneTemp.objects.link(objChild)
        except: pass
        try: sceneTemp.objects.link(objParent)
        except: pass

        ### Make parent
        objParent.select = 1
        objChild.select = 1
        bpy.context.scene.objects.active = objParent   # Parent
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        objParent.select = 0
        objChild.select = 0

#        # Unlink objects from second scene (leads to loss of rigid body settings, bug in Blender)
#        sceneTemp.objects.unlink(objChild)
#        sceneTemp.objects.unlink(objParent)
        # Workaround: Delete second scene and recreate it (deleting objects indirectly without the loss of rigid body settings)
        if k %200 == 0:   # Only delete scene every now and then so we have lower overhead from the relatively slow process
            bpy.data.scenes.remove(sceneTemp)
            sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
            # Link cameras because in second scene is none and when coming back camera view will losing focus
            for obj in objCameras:
                sceneTemp.objects.link(obj)
            # Switch to new scene
            bpy.context.screen.scene = sceneTemp
    
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    bpy.data.scenes.remove(sceneTemp)

    ### Remove child object from rigid body world (should not be simulated anymore)
    for k in range(len(connectsPairParent)):
        objChild = objs[connectsPairParent[k][0]].select = 1
    bpy.ops.rigidbody.objects_remove()
        
    print()

################################################################################   

def deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair):
    
    ### Delete connections with too few connected vertices
    if debug: print("Deleting connections with too few connected vertices...")
    
    connectsPairTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        vertPairCnt = len(connectsPair[i]) /2
        reqVertexPairsObjA = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][1]
        reqVertexPairsObjB = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][1]
        if vertPairCnt >= reqVertexPairsObjA and vertPairCnt >= reqVertexPairsObjB:
            connectsPairTmp.append(pair)
            connectCnt += 1
    connectsPair = connectsPairTmp
    
    print("Connections skipped due to too few connecting vertices:", connectCntOld -connectCnt)
    return connectsPair
        
################################################################################   

def calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, customThickness=0):

    ###### Calculate contact area for a single pair of objects
    
    ### Calculate boundary box corners
    bbAMin, bbAMax, bbACenter = boundaryBox(objA, 1)
    bbBMin, bbBMax, bbBCenter = boundaryBox(objB, 1)
    
    ### Calculate contact surface area from boundary box projection
    ### Project along all axis'
    overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
    overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
    overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
    
    ### Calculate area based on either the sum of all axis surfaces...
    # Formula only valid if we have overlap for all 3 axis
    # (This line is commented out because of the earlier connection pair check which ensured contact including a margin.)
    #if overlapX > 0 and overlapY > 0 and overlapZ > 0:  
    if 1:
        
        if not customThickness:
            overlapAreaX = overlapY *overlapZ
            overlapAreaY = overlapX *overlapZ
            overlapAreaZ = overlapX *overlapY
            # Add up all contact areas
            contactArea = overlapAreaX +overlapAreaY +overlapAreaZ

        ### Or calculate contact area based on predefined custom thickness
        else:
            contactArea = overlapX +overlapY +overlapZ
            # This should actually be:
            # contactArea = (overlapX +overlapY +overlapZ) *nonManifoldThickness
            # For updating possibility this last operation is postponed to setConstraintSettings()

    else: contactArea = 0
            
    ### Find out element thickness to be used for bending threshold calculation 
    bendingThickness = [overlapX, overlapY, overlapZ]
    bendingThickness.sort()
    bendingThickness = bendingThickness[1]   # First item = mostly 0, second item = thickness, third item = width 
    
    ### Use center of contact area boundary box as constraints location
    centerX = max(bbAMin[0],bbBMin[0]) +(overlapX /2)
    centerY = max(bbAMin[1],bbBMin[1]) +(overlapY /2)
    centerZ = max(bbAMin[2],bbBMin[2]) +(overlapZ /2)
    center = Vector((centerX, centerY, centerZ))
    #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon

    return contactArea, bendingThickness, center 

########################################

def calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    connectsArea = []
    connectsLoc = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        
        ###### Calculate contact area for a single pair of objects
        contactArea, bendingThickness, center = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB)
        
        connectsArea.append([contactArea, bendingThickness, 0])
        connectsLoc.append(center)
        
    return connectsArea, connectsLoc

################################################################################   

def calculateContactAreaBasedOnBooleansForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections... (%d)" %len(connectsPair))

    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    objCameras = []
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            sceneTemp.objects.link(objTemp)
            objCameras.append(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    ### Main calculation loop
    connectsArea = []
    connectsLoc = []
    connectsPair_len = len(connectsPair)
    for k in range(connectsPair_len):
        sys.stdout.write('\r' +"%d " %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /connectsPair_len)

        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        objA.select = 0
        objB.select = 0
            
        # Link objects we're working on to second scene (we try because of the object unlink workaround)
        try: sceneTemp.objects.link(objA)
        except: pass
        try: sceneTemp.objects.link(objB)
        except: pass
        
        ### Check if meshes are water tight (non-manifold)
        qNonManifolds = 0
        for obj in [objA, objB]:
            bpy.context.scene.objects.active = obj
            me = obj.data
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass 
            # Deselect all elements
            try: bpy.ops.mesh.select_all(action='DESELECT')
            except: pass 
            # Select non-manifold elements
            bpy.ops.mesh.select_non_manifold()
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass 
            # check mesh if there are selected elements found
            for edge in me.edges:
                if edge.select: qNonManifolds = 1; break

        ###### If non-manifold then calculate a contact area estimation based on boundary boxes intersection and a user defined thickness
        if qNonManifolds:

            #print('Warning: Mesh not water tight, non-manifolds found:', obj.name)

            ###### Calculate contact area for a single pair of objects
            contactArea, bendingThickness, center = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, customThickness=1)
            surfaceThickness = nonManifoldThickness
            
            connectsArea.append([contactArea, bendingThickness, surfaceThickness])
            connectsLoc.append(center)

        ###### If both meshes are manifold continue with regular boolean based approach
        else:

            ### Add displacement modifier to objects to take search distance into account
            objA.modifiers.new(name="Displace_BCB", type='DISPLACE')
            modA_disp = objA.modifiers["Displace_BCB"]
            modA_disp.mid_level = 0
            modA_disp.strength = searchDistance
            objB.modifiers.new(name="Displace_BCB", type='DISPLACE')
            modB_disp = objB.modifiers["Displace_BCB"]
            modB_disp.mid_level = 0
            modB_disp.strength = searchDistance
            meA_disp = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
            meB_disp = objB.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                
            ### Add boolean modifier to object
            objA.modifiers.new(name="Boolean_BCB", type='BOOLEAN')
            modA_bool = objA.modifiers["Boolean_BCB"]
            ### Create a boolean intersection mesh (for center point calculation)
            modA_bool.operation = 'INTERSECT'
            modA_bool.object = objB
            ### Perform boolean operation and in case result is corrupt try again with small changes in displacement size
            searchDistanceMinimum = searchDistance *0.9   # Lowest limit for retrying until we accept that no solution can be found
            qNoSolution = 0
            while 1:
                me_intersect = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                qBadResult = me_intersect.validate(verbose=False, clean_customdata=False)
                if qBadResult == 0: break
                modA_disp.strength *= 0.99
                sceneTemp.update()
                if modA_disp.strength < searchDistanceMinimum: qNoSolution = 1; break
            if qNoSolution: print('Error on boolean operation, mesh problems detected:', objA.name, objB.name); halt
            
            # If intersection mesh has geometry then continue calculation
            if len(me_intersect.vertices) > 0:
                
#                ### Create a boolean union mesh (for contact area calculation)
#                modA_bool.operation = 'UNION'
#                me_union = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
#                # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
#                qBadResult = me_union.validate(verbose=False, clean_customdata=False)
#                if qBadResult: print('Error on boolean operation, mesh problems detected:', objA.name, objB.name)
                
                ### Calculate center point for the intersection mesh
                # Create a new object for the mesh
                objIntersect = bpy.data.objects.new("BCB Temp Object", me_intersect)
                bpy.context.scene.objects.link(objIntersect)
                objIntersect.matrix_world = objA.matrix_world
                
                ### Calculate center of intersection mesh based on its boundary box (throws ugly "group # is unclassified!" warnings)
#                objIntersect.select = 1
#                #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
#                center = objIntersect.matrix_world.to_translation()
                ### Calculate center of intersection mesh based on its boundary box (alternative code, slower but no warnings)
                bbMin, bbMax, center = boundaryBox(objIntersect, 1)
                
                ### Find out element thickness to be used for bending threshold calculation (the diameter of the intersection mesh should be sufficient for now)
                bendingThickness = list(objIntersect.dimensions)
                bendingThickness.sort()
                bendingThickness = bendingThickness[1]   # First item = mostly 0, second item = thickness, third item = width 
                
                ### Add displacement modifier to intersection mesh
                objIntersect.modifiers.new(name="Displace_BCB", type='DISPLACE')
                modIntersect_disp = objIntersect.modifiers["Displace_BCB"]
                modIntersect_disp.mid_level = 0
                modIntersect_disp.strength = -searchDistance /2
                me_intersect_remDisp = objIntersect.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
                
                ### Calculate surface area for both original elements
                surface = 0
                meA = objA.data
                meB = objB.data
                for poly in meA.polygons: surface += poly.area
                for poly in meB.polygons: surface += poly.area
                ### Calculate surface area for displaced versions of both original elements
                surfaceDisp = 0
                for poly in meA_disp.polygons: surfaceDisp += poly.area
                for poly in meB_disp.polygons: surfaceDisp += poly.area
                # Calculate ratio of original to displaced surface area for later contact area correction
                correction = surface /surfaceDisp
#                ### Calculate surface area for the unified mesh
#                surfaceBoolUnion = 0
#                for poly in me_union.polygons: surfaceBoolUnion += poly.area
                ### Calculate surface area for the intersection mesh
                surfaceBoolIntersect = 0
                for poly in me_intersect.polygons: surfaceBoolIntersect += poly.area
                ### Calculate surface area for the intersection mesh with removed displacement
                surfaceBoolIntersectRemDisp = 0
                for poly in me_intersect_remDisp.polygons: surfaceBoolIntersectRemDisp += poly.area
#                ### The contact area is half the difference of both surface areas
#                contactArea = (surfaceDisp -surfaceBoolUnion) /2
                ### The contact area is half the surface area of the intersection mesh without displacement
                contactArea = surfaceBoolIntersectRemDisp /2
                contactArea *= correction
                if contactArea < 0: print('Error on boolean operation, contact area negative:', objA.name, objB.name)
                
                # Unlink new object from second scene
                sceneTemp.objects.unlink(objIntersect)
                
            # If intersection mesh has no geometry then invalidate connection
            else:
                contactArea = 0
                bendingThickness = 0
                center = Vector((0, 0, 0))
            
            # Remove modifiers from original object again
            objA.modifiers.remove(modA_bool)
            objA.modifiers.remove(modA_disp)
            objB.modifiers.remove(modB_disp)
            
#            # Unlink objects from second scene (leads to loss of rigid body settings, bug in Blender)
#            sceneTemp.objects.unlink(objA)
#            sceneTemp.objects.unlink(objB)
            # Workaround: Delete second scene and recreate it (deleting objects indirectly without the loss of rigid body settings)
            if k %200 == 0:   # Only delete scene every now and then so we have lower overhead from the relatively slow process
                bpy.data.scenes.remove(sceneTemp)
                sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
                # Link cameras because in second scene is none and when coming back camera view will losing focus
                for obj in objCameras:
                    sceneTemp.objects.link(obj)
                # Switch to new scene
                bpy.context.screen.scene = sceneTemp
        
            connectsArea.append([contactArea, bendingThickness, 0])
            connectsLoc.append(center)
                
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    bpy.data.scenes.remove(sceneTemp)
                
    print()
    return connectsArea, connectsLoc

################################################################################   

def calculateContactAreaBasedOnMaskingForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections... (%d)" %len(connectsPair))
        
    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    objCameras = []
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            sceneTemp.objects.link(objTemp)
            objCameras.append(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    ### Main calculation loop
    connectsArea = []
    connectsLoc = []
    connectsPair_len = len(connectsPair)
    for k in range(connectsPair_len):
        sys.stdout.write('\r' +"%d " %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /connectsPair_len)

        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        objA.select = 0
        objB.select = 0
            
        # Link objects we're working on to second scene (we try because of the object unlink workaround)
        try: sceneTemp.objects.link(objA)
        except: pass
        try: sceneTemp.objects.link(objB)
        except: pass

        contactAreas = []
        bendingThicknesses = []
        centers = []
        
        # Do this for both elements of the pair
        for obj in [objA, objB]:
            bpy.context.scene.objects.active = obj
            if obj == objA: objPartner = objB
            else:           objPartner = objA
                        
            ### Create vertex group for masking
            bpy.context.scene.objects.active = obj
            bpy.ops.object.vertex_group_add()
            vgrp = bpy.context.scene.objects.active.vertex_groups[-1:][0]
            vgrp.name = "Distance_Mask"
            # Set vertex weights to 1 
            vgrp.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')

            ### Add Vertex Weight Proximity modifier
            bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_PROXIMITY')
            mod = bpy.context.scene.objects.active.modifiers[-1:][0]
            mod.name = "VertexWeightProximity_BCB"
            mod.vertex_group = "Distance_Mask"
            mod.proximity_mode = 'GEOMETRY'
            mod.proximity_geometry = {'FACE'}
            mod.falloff_type = 'STEP'
            mod.max_dist = 0
            mod.min_dist = searchDistance
            mod.target = objPartner
            
            ### Add Mask modifier
            bpy.ops.object.modifier_add(type='MASK')
            mod = bpy.context.scene.objects.active.modifiers[-1:][0]
            mod.name = "Mask_BCB"
            mod.vertex_group = "Distance_Mask"

            # Make modified mesh real
            me_intersect = bpy.context.scene.objects.active.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)

            # Remove BCB modifiers from original object
            bpy.context.scene.objects.active.modifiers.remove(bpy.context.scene.objects.active.modifiers[-1:][0])
            bpy.context.scene.objects.active.modifiers.remove(bpy.context.scene.objects.active.modifiers[-1:][0])
            # Remove BCB vertex group from all original objects
            bpy.ops.object.vertex_group_remove()
           
            # If intersection mesh has geometry then continue calculation
            if len(me_intersect.vertices) > 0:
                
                ### Calculate center point for the intersection mesh
                # Create a new object for the mesh
                objIntersect = bpy.data.objects.new("BCB Temp Object", me_intersect)
                bpy.context.scene.objects.link(objIntersect)
                objIntersect.matrix_world = bpy.context.scene.objects.active.matrix_world
                
                ### Calculate center of intersection mesh based on its boundary box (throws ugly "group # is unclassified!" warnings)
                objIntersect.select = 1
                bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
                center = objIntersect.matrix_world.to_translation()
#                ### Calculate center of intersection mesh based on its boundary box (alternative code, slower but no warnings)
#                bbMin, bbMax, center = boundaryBox(objIntersect, 1)
                
                ### Find out element thickness to be used for bending threshold calculation (the diameter of the intersection mesh should be sufficient for now)
                bendingThickness = list(objIntersect.dimensions)
                bendingThickness.sort()
                bendingThickness = bendingThickness[1]   # First item = mostly 0, second item = thickness, third item = width 
                                
                ### Calculate surface area
                contactArea = 0
                for poly in me_intersect.polygons: contactArea += poly.area
                
                # Unlink new object from second scene
                sceneTemp.objects.unlink(objIntersect)
            
            # If intersection mesh has no geometry then invalidate connection
            if len(me_intersect.vertices) == 0 or contactArea == 0:
                contactArea = 0
                bendingThickness = 0
                center = Vector((0, 0, 0))
            
            contactAreas.append(contactArea)
            bendingThicknesses.append(bendingThickness)
            centers.append(center)
            
        # Use the larger value as contact area because it is likely to be the cross-section of one element, overlapping surfaces of the partner element will most likely being masked out
        if contactAreas[0] >= contactAreas[1]: idx = 0
        if contactAreas[0] < contactAreas[1]: idx = 1
        contactArea = contactAreas[idx]
        bendingThickness = bendingThicknesses[idx]
        center = centers[idx]

        ###### If both intersection meshes have no geometry then calculate a contact area estimation based on boundary boxes intersection and a user defined thickness
        if contactArea == 0:
            # Todo: Here the boolean approach could be used as a fallback, for now surfaceThickness is not used
            ###### Calculate contact area for a single pair of objects
            contactArea, bendingThickness, center = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB)
        
        connectsArea.append([contactArea, bendingThickness, 0])
        connectsLoc.append(center)

#        # Unlink objects from second scene (leads to loss of rigid body settings, bug in Blender)
#        sceneTemp.objects.unlink(objA)
#        sceneTemp.objects.unlink(objB)
        # Workaround: Delete second scene and recreate it (deleting objects indirectly without the loss of rigid body settings)
        if k %200 == 0:   # Only delete scene every now and then so we have lower overhead from the relatively slow process
            bpy.data.scenes.remove(sceneTemp)
            sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
            # Link cameras because in second scene is none and when coming back camera view will losing focus
            for obj in objCameras:
                sceneTemp.objects.link(obj)
            # Switch to new scene
            bpy.context.screen.scene = sceneTemp

    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    bpy.data.scenes.remove(sceneTemp)
                
    print()
    return connectsArea, connectsLoc

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsArea, connectsLoc):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")
    
    connectsPairTmp = []
    connectsAreaTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    minimumArea = searchDistance**2
    for i in range(len(connectsPair)):
        if connectsArea[i][0] > minimumArea:
            connectsPairTmp.append(connectsPair[i])
            connectsAreaTmp.append(connectsArea[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsArea = connectsAreaTmp
    connectsLoc = connectsLocTmp
    
    print("Connections skipped due to zero contact area:", connectCntOld -connectCnt)
    return connectsPair, connectsArea, connectsLoc

################################################################################   

def createConnectionData(objsEGrp, connectsPair):
    
    ### Create connection data
    if debug: print("Creating connection data...")
    
    connectsConsts = []
    constsConnect = []
    constCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        ### Count constraints by connection type preset
        elemGrpA = objsEGrp[pair[0]]
        elemGrpB = objsEGrp[pair[1]]
        # Element group order defines priority for connection type (first preferred over latter) 
        if elemGrpA <= elemGrpB: elemGrp = elemGrpA
        else:                    elemGrp = elemGrpB
        connectTypeIdx = elemGrps[elemGrp][4]
        try: connectType = connectTypes[connectTypeIdx]
        except: connectsConsts.append([])  # In case the connection type is unknown (no constraints)
        else:
            items = []
            for j in range(connectType[1]):
                items.append(constCnt +j)
                constsConnect.append(i)
            connectsConsts.append(items)
            constCnt += len(items)
            
    return connectsPair, connectsConsts, constsConnect

################################################################################   

def BackupLayerSettingsAndActivateNextEmptyLayer(scene):

    ### Find and activate the first empty layer
    print("Find and activate the first empty layer...")
    
    ### Backup layer settings
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(0)
    ### Find and activate the first empty layer
    qFound = 0
    for i in range(20):
        objsOnLayer = [obj for obj in scene.objects if obj.layers[i]]
        if len(objsOnLayer) == 0:
            layersNew[i] = 1
            qFound = 1
            break
    if qFound:
        # Set new layers
        scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
        
    # Return old layers state
    return layersBak
    
################################################################################   

def createEmptyObjs(scene, constCnt):
    
    ### Create empty objects
    print("Creating empty objects... (%d)" %constCnt)

    ### Create first object
    objConst = bpy.data.objects.new('Constraint', None)
    bpy.context.scene.objects.link(objConst)
    objConst.empty_draw_type = 'SPHERE'
    bpy.context.scene.objects.active = objConst
    bpy.ops.rigidbody.constraint_add()

    constCntPerScene = 1024
    scenesTemp = []
    emptyObjsGlobal = [objConst]
    # Repeat until desired object count is reached
    while len(emptyObjsGlobal) < constCnt:
        
        ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
        sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
        scenesTemp.append(sceneTemp)
        # Set layers to same state as original scene
        sceneTemp.layers = scene.layers
        # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
        bpy.context.screen.scene = scene
        # Link cameras because in second scene is none and when coming back camera view will losing focus
        objCameras = []
        for objTemp in scene.objects:
            if objTemp.type == 'CAMERA':
                sceneTemp.objects.link(objTemp)
                objCameras.append(objTemp)
        # Switch to new scene
        bpy.context.screen.scene = sceneTemp
        # If using two scenes make sure both are using the same RigidBodyWorld and RigidBodyConstraints groups
        bpy.ops.rigidbody.world_add()
        bpy.context.scene.rigidbody_world.group = bpy.data.groups["RigidBodyWorld"]
        bpy.context.scene.rigidbody_world.constraints = bpy.data.groups["RigidBodyConstraints"]
        # Link first empty into new scene
        bpy.context.scene.objects.link(objConst)
        
        ### Duplicate empties as long as we got the desired count   
        emptyObjs = [objConst]
        while len(emptyObjs) < (constCnt -(len(emptyObjsGlobal) -1)) and len(emptyObjs) <= constCntPerScene:
            sys.stdout.write("%d " %len(emptyObjs))
            # Update progress bar
            bpy.context.window_manager.progress_update(len(emptyObjsGlobal) /constCnt)
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            # Select empties already in list
            c = 0
            for obj in emptyObjs:
                if c < (constCnt -(len(emptyObjsGlobal) -1)) -len(emptyObjs):
                    obj.select = 1
                    c += 1
                else: break
            # Duplicate them
            bpy.ops.object.duplicate(linked=False)
            # Add duplicates to list again
            for obj in bpy.data.objects:
                if obj.select and obj.is_visible(scene):
                    if obj.type == 'EMPTY':
                        emptyObjs.append(obj)
        
        emptyObjsGlobal.extend(emptyObjs[1:])
        sys.stdout.write("\r%d - " %len(emptyObjsGlobal))
        
    emptyObjs = emptyObjsGlobal

    ### Link new object back into original scene
    for scn in scenesTemp:
        # Switch through temp scenes
        bpy.context.screen.scene = scn
        # Select all objects
        bpy.ops.object.select_all(action='SELECT')
        # Link objects to original scene
        bpy.ops.object.make_links_scene(scene=scene.name)

#    # Link new object back into original scene
#    for obj in emptyObjs[1:]:
#        scene.objects.link(obj)
        
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    for scn in scenesTemp:
        bpy.data.scenes.remove(scn)

    print()
    return emptyObjs        

################################################################################   

def bundlingEmptyObjsToClusters(connectsLoc, connectsConsts):
    
    ### Bundling close empties into clusters, merge locations and count connections per cluster
    print("Bundling close empties into clusters...")
    
    m = 1
    qChanged = 1
    while qChanged:   # Repeat until no more constraints are moved
        qChanged = 0
        
        sys.stdout.write('\r' +"Pass %d" %m)
        # Update progress bar
        bpy.context.window_manager.progress_update(1 -(1 /m))
        m += 1
        
        ### Build kd-tree for constraint locations
        kdObjs = mathutils.kdtree.KDTree(len(connectsLoc))
        for i, loc in enumerate(connectsLoc):
            kdObjs.insert(loc, i)
        kdObjs.balance()
        
        clustersConnects = []  # Stores all constraints indices per cluster
        clustersLoc = []       # Stores the location of each cluster
        for i in range(len(connectsLoc)):
            
            ### Find closest connection location via kd-tree (zero distance start item included)
            co_find = connectsLoc[i]
            aIndex = []; aCo = []#; aDist = [];
            j = 0
            for (co, index, dist) in kdObjs.find_range(co_find, clusterRadius):   # Find constraint object within search range
                if j == 0 or co != lastCo:   # Skip constraints that already share the same location (caused by earlier loops)
                    aIndex.append(index); aCo.append(co)#; aDist.append(dist)
                    lastCo = co
                    # Stop after second different constraint is found
                    j += 1
                    if j == 2: qChanged = 1; break
                        
            ### Calculate average location of the two constraints found within cluster radius
            ### We merge them pairwise instead of all at once for improved and more even distribution
            if len(aCo) == 2:
                loc = (aCo[0] +aCo[1]) /2
                clustersLoc.append(loc)
                clustersConnects.append([aIndex[0], aIndex[1]])
                ### Also move all other constraints with the same locations because we can assume they already have been merged earlier
                for i in range(len(connectsLoc)):
                    if aCo[0] == connectsLoc[i] or aCo[1] == connectsLoc[i]:
                        clustersConnects[-1:][0].append(i)
                  
        ### Apply cluster locations to constraints
        for l in range(len(clustersConnects)):
            for k in clustersConnects[l]:
                connectsLoc[k] = clustersLoc[l]
    
    print()
        
################################################################################   

def addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect, exportData):
    
    ### Add base constraint settings to empties
    print("Adding base constraint settings to empties... (%d)" %len(emptyObjs))
    
    for k in range(len(emptyObjs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(emptyObjs))
                
        l = constsConnect[k]
        if not asciiExport:
            objConst = emptyObjs[k]
            objConst.location = connectsLoc[l]
            objConst.rigid_body_constraint.object1 = objs[connectsPair[l][0]]
            objConst.rigid_body_constraint.object2 = objs[connectsPair[l][1]]
        else:
            exportData[k].append(connectsLoc[l].to_tuple())
            exportData[k].append(objs[connectsPair[l][0]].name)
            exportData[k].append(objs[connectsPair[l][1]].name)
             
    print()
                
################################################################################   

def getAttribsOfConstraint(objConst):

    ### Create a dictionary of all attributes with values from the given constraint empty object    
    con = bpy.context.object.rigid_body_constraint
    props = {}
    for prop in con.bl_rna.properties:
        if not prop.is_hidden:
            if prop.type == 'POINTER':
                attr = getattr(con, prop.identifier)
                props[prop.identifier] = None
                if attr is not None:
                    props[prop.identifier] = attr.name    
            else:   props[prop.identifier] = getattr(con, prop.identifier)
    return props
        
########################################

def setAttribsOfConstraint(objConst, props):

    ### Overwrite all attributes of the given constraint empty object with the values of the dictionary provided    
    for prop in props:
        try: setattr(con, prop.identifier, props[prop.identifier])
        except: pass
        
########################################
    
def setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsArea, connectsConsts, constsConnect, exportData):
    
    ### Set constraint settings
    print("Adding main constraint settings... (%d)" %len(connectsPair))
    
    scene = bpy.context.scene
    
    if asciiExport:
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
        contactArea = connectsArea[k][0]
        bendingThickness = connectsArea[k][1]
        if not asciiExport:
            # Store value as ID property for debug purposes
            for idx in consts: emptyObjs[idx]['ContactArea'] = contactArea
        
        # Postponed contactArea calculation step from calculateContactAreaBasedOnBoundaryBoxesForPair() is being done now (update hack, could be better organized)
        if useAccurateArea:
            surfaceThickness = connectsArea[k][2]
            if surfaceThickness > 0:
                contactArea *= surfaceThickness
        
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        elemGrpA = objsEGrp[objs.index(objA)]
        elemGrpB = objsEGrp[objs.index(objB)]
        # Element group order defines priority for connection type (first preferred over latter) 
        if elemGrpA <= elemGrpB: elemGrp = elemGrpA
        else:                    elemGrp = elemGrpB
        
        connectType = elemGrps[elemGrp][4]
        breakThres1 = elemGrps[elemGrp][5]
        breakThres2 = elemGrps[elemGrp][6]
        breakThres3 = elemGrps[elemGrp][7]
        breakThres4 = elemGrps[elemGrp][8]
        springStiff = elemGrps[elemGrp][9]
        tol1dist = elemGrps[elemGrp][10]
        tol1rot = elemGrps[elemGrp][11]
        tol2dist = elemGrps[elemGrp][12]
        tol2rot = elemGrps[elemGrp][13]
        
        if not asciiExport:
            ### Check if full update is necessary (optimization)
            objConst0 = emptyObjs[consts[0]]
            if 'ConnectType' in objConst0.keys() and objConst0['ConnectType'] == connectType: qUpdateComplete = 0
            else: objConst0['ConnectType'] = connectType; qUpdateComplete = 1
        else:
            objConst0 = objConst
            qUpdateComplete = 1
            objConst.rotation_mode = 'XYZ'  # Overwrite temporary object to default (Euler)
                
        ### Set constraints by connection type preset
        ### Also convert real world breaking threshold to bullet breaking threshold and take simulation steps into account (Threshold = F / Steps)
        
        # For initial time scale period update: Skips recalculation of breaking thresholds if set to zero instead of default of 10
        if objConst0.rigid_body_constraint.breaking_threshold:

            if   connectType == 1 or connectType == 9 or connectType == 10:
                correction = 1
                # Obsolete code (before plastic mode):
                #if connectType == 9: correction /= 1 +3     # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 10: correction /= 1 +4  # Divided by the count of constraints which are sharing the same degree of freedom
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.type = 'FIXED'
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                objConst.empty_draw_size = emptyDrawSize
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    
            elif connectType == 2:
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.type = 'POINT'
                objConst.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale
                objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                objConst.empty_draw_size = emptyDrawSize
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                
            elif connectType == 3:
                correction = 1 /2   # As both constraints bear all load and forces are evenly distributed among them the breaking thresholds need to be divided by their count to compensate
                ### First constraint
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.type = 'FIXED'
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres4 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres1'] = breakThres4   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                objConst.empty_draw_size = emptyDrawSize
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Second constraint
                cIdx = consts[1]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.type = 'POINT'
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres2'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                objConst.empty_draw_size = emptyDrawSize
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
            
            elif connectType == 4:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                ### First constraint
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock all directions for the compressive force
                    ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                    ### Also rotational forces should only be carried by the tensile constraint
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.limit_lin_x_lower = 0
                    objConst.rigid_body_constraint.limit_lin_x_upper = 99999
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                # Align constraint rotation to that vector
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Second constraint
                cIdx = consts[1]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres2 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres2'] = breakThres2   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock all directions for the tensile force
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 1
                    objConst.rigid_body_constraint.use_limit_lin_z = 1
                    objConst.rigid_body_constraint.limit_lin_x_lower = -99999
                    objConst.rigid_body_constraint.limit_lin_x_upper = 0
                    objConst.rigid_body_constraint.limit_lin_y_lower = 0
                    objConst.rigid_body_constraint.limit_lin_y_upper = 0
                    objConst.rigid_body_constraint.limit_lin_z_lower = 0
                    objConst.rigid_body_constraint.limit_lin_z_upper = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 1
                    objConst.rigid_body_constraint.use_limit_ang_y = 1
                    objConst.rigid_body_constraint.use_limit_ang_z = 1
                    objConst.rigid_body_constraint.limit_ang_x_lower = 0
                    objConst.rigid_body_constraint.limit_ang_x_upper = 0
                    objConst.rigid_body_constraint.limit_ang_y_lower = 0
                    objConst.rigid_body_constraint.limit_ang_y_upper = 0
                    objConst.rigid_body_constraint.limit_ang_z_lower = 0
                    objConst.rigid_body_constraint.limit_ang_z_upper = 0
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                
            elif connectType == 5:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                ### First constraint
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock direction for compressive force
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.limit_lin_x_lower = 0
                    objConst.rigid_body_constraint.limit_lin_x_upper = 99999
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation to that vector
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Second constraint
                cIdx = consts[1]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres2 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres2'] = breakThres2   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock directions for shearing force
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 1
                    objConst.rigid_body_constraint.use_limit_lin_z = 1
                    objConst.rigid_body_constraint.limit_lin_x_lower = -99999
                    objConst.rigid_body_constraint.limit_lin_x_upper = 0
                    objConst.rigid_body_constraint.limit_lin_y_lower = 0
                    objConst.rigid_body_constraint.limit_lin_y_upper = 0
                    objConst.rigid_body_constraint.limit_lin_z_lower = 0
                    objConst.rigid_body_constraint.limit_lin_z_upper = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Third constraint
                cIdx = consts[2]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( (contactArea *bendingThickness) *1000000 *breakThres4 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres3'] = breakThres4   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock directions for bending force
                    objConst.rigid_body_constraint.use_limit_lin_x = 0
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 1
                    objConst.rigid_body_constraint.use_limit_ang_y = 1
                    objConst.rigid_body_constraint.use_limit_ang_z = 1
                    objConst.rigid_body_constraint.limit_ang_x_lower = 0 
                    objConst.rigid_body_constraint.limit_ang_x_upper = 0 
                    objConst.rigid_body_constraint.limit_ang_y_lower = 0
                    objConst.rigid_body_constraint.limit_ang_y_upper = 0
                    objConst.rigid_body_constraint.limit_ang_z_lower = 0
                    objConst.rigid_body_constraint.limit_ang_z_upper = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                
            elif connectType == 6 or connectType == 11 or connectType == 12:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value, divided by the count of constraints which are sharing the same degree of freedom
                # Obsolete code (before plastic mode):
                #if connectType == 11: correction /= 1 +3    # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 12: correction /= 1 +4  # Divided by the count of constraints which are sharing the same degree of freedom
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                ### First constraint
                cIdx = consts[0]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock direction for compressive force
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.limit_lin_x_lower = 0
                    objConst.rigid_body_constraint.limit_lin_x_upper = 99999
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation to that vector
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Second constraint
                cIdx = consts[1]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres2 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres2'] = breakThres2   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock direction for tensile force
                    objConst.rigid_body_constraint.use_limit_lin_x = 1
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.limit_lin_x_lower = -99999
                    objConst.rigid_body_constraint.limit_lin_x_upper = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Third constraint
                cIdx = consts[2]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( contactArea *1000000 *breakThres3 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres3'] = breakThres3   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock directions for shearing force
                    objConst.rigid_body_constraint.use_limit_lin_x = 0
                    objConst.rigid_body_constraint.use_limit_lin_y = 1
                    objConst.rigid_body_constraint.use_limit_lin_z = 1
                    objConst.rigid_body_constraint.limit_lin_y_lower = 0
                    objConst.rigid_body_constraint.limit_lin_y_upper = 0
                    objConst.rigid_body_constraint.limit_lin_z_lower = 0
                    objConst.rigid_body_constraint.limit_lin_z_upper = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 0
                    objConst.rigid_body_constraint.use_limit_ang_y = 0
                    objConst.rigid_body_constraint.use_limit_ang_z = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                ### Fourth constraint
                cIdx = consts[3]
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                objConst.rigid_body_constraint.breaking_threshold = ((( (contactArea *bendingThickness) *1000000 *breakThres4 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                objConst['BrkThres4'] = breakThres4   # Store value as ID property for debug purposes
                objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                if qUpdateComplete:
                    objConst.rotation_mode = 'QUATERNION'
                    objConst.rigid_body_constraint.type = 'GENERIC'
                    objConst.empty_draw_size = emptyDrawSize
                    ### Lock directions for bending force
                    objConst.rigid_body_constraint.use_limit_lin_x = 0
                    objConst.rigid_body_constraint.use_limit_lin_y = 0
                    objConst.rigid_body_constraint.use_limit_lin_z = 0
                    objConst.rigid_body_constraint.use_limit_ang_x = 1
                    objConst.rigid_body_constraint.use_limit_ang_y = 1
                    objConst.rigid_body_constraint.use_limit_ang_z = 1
                    objConst.rigid_body_constraint.limit_ang_x_lower = 0 
                    objConst.rigid_body_constraint.limit_ang_x_upper = 0 
                    objConst.rigid_body_constraint.limit_ang_y_lower = 0
                    objConst.rigid_body_constraint.limit_ang_y_upper = 0
                    objConst.rigid_body_constraint.limit_ang_z_lower = 0
                    objConst.rigid_body_constraint.limit_ang_z_upper = 0
                    #objConst.rigid_body_constraint.disable_collisions = False
                # Align constraint rotation like above
                objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                if asciiExport:
                    exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                    exportData[cIdx].append(objConst.rotation_mode)
                    exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                    exportData[cIdx].append(getAttribsOfConstraint(objConst))
                
            if connectType == 7 or connectType == 9 or connectType == 11:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
                # Obsolete code (before plastic mode):
                #if connectType == 7: correction /= 3        # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 9: correction /= 3 +1   # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 11: correction /= 3 +4  # Divided by the count of constraints which are sharing the same degree of freedom
                radius = bendingThickness /2
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                constBreakThres = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                # Some connection types are designed to use a combination of multiple presets, then an index offset for accessing the right constraints is required
                if connectType == 9: conIdxOfs = connectTypes[1][1]
                elif connectType == 11: conIdxOfs = connectTypes[6][1]
                else: conIdxOfs = 0
                # Loop through all constraints of this connection
                for i in range(3):
                    cIdx = consts[i +conIdxOfs]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres
                    objConst['BrkThres'] = breakThres1   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   i == 0: vec = Vector((0, radius, radius))
                        elif i == 1: vec = Vector((0, radius, -radius))
                        elif i == 2: vec = Vector((0, -radius, 0))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        #objConst.rigid_body_constraint.disable_collisions = False
                    if connectType == 7:  # If spring-only connection type then activate springs from start (no extra plastic activation required)
                        objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                        objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                        objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    else:  # Disable springs on start (requires plastic activation during simulation)
                        objConst.rigid_body_constraint.spring_stiffness_x = 0
                        objConst.rigid_body_constraint.spring_stiffness_y = 0
                        objConst.rigid_body_constraint.spring_stiffness_z = 0
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        if connectType == 7:
                              exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        else: exportData[cIdx].append(["PLASTIC_OFF", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    
            elif connectType == 8 or connectType == 10 or connectType == 12:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
                # Obsolete code (before plastic mode):
                #if connectType == 8: correction /= 4        # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 10: correction /= 4 +1  # Divided by the count of constraints which are sharing the same degree of freedom
                #elif connectType == 12: correction /= 4 +4  # Divided by the count of constraints which are sharing the same degree of freedom
                radius = bendingThickness /2
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                constBreakThres = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                # Some connection types are designed to use a combination of multiple presets, then an index offset for accessing the right constraints is required
                if connectType == 10: conIdxOfs = connectTypes[1][1]
                elif connectType == 12: conIdxOfs = connectTypes[6][1]
                else: conIdxOfs = 0
                # Loop through all constraints of this connection
                for i in range(4):
                    cIdx = consts[i +conIdxOfs]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres
                    objConst['BrkThres'] = breakThres1   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   i == 0: vec = Vector((0, radius, radius))
                        elif i == 1: vec = Vector((0, radius, -radius))
                        elif i == 2: vec = Vector((0, -radius, -radius))
                        elif i == 3: vec = Vector((0, -radius, radius))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        #objConst.rigid_body_constraint.disable_collisions = False
                    if connectType == 8:  # If spring-only connection type then activate springs from start (no extra plastic activation required)
                        objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                        objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                        objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    else:  # Disable springs on start (requires plastic activation during simulation)
                        objConst.rigid_body_constraint.spring_stiffness_x = 0
                        objConst.rigid_body_constraint.spring_stiffness_y = 0
                        objConst.rigid_body_constraint.spring_stiffness_z = 0
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        if connectType == 8:
                              exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        else: exportData[cIdx].append(["PLASTIC_OFF", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    
            if connectType == 13:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
                radius = bendingThickness /2
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                constBreakThres1 = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres2 = ((( contactArea *1000000 *breakThres2 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres3 = ((( contactArea *1000000 *breakThres3 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres4 = ((( (contactArea *bendingThickness) *1000000 *breakThres4 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                # Loop through all constraints of this connection
                i = -3
                for j in range(3):
                    i += 3
                    ### First constraint
                    cIdx = consts[i]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres1
                    objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, 0))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock direction for compressive force
                        objConst.rigid_body_constraint.use_limit_lin_x = 1
                        objConst.rigid_body_constraint.use_limit_lin_y = 0
                        objConst.rigid_body_constraint.use_limit_lin_z = 0
                        objConst.rigid_body_constraint.limit_lin_x_lower = 0
                        objConst.rigid_body_constraint.limit_lin_x_upper = 99999
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation to that vector
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    ### Second constraint
                    cIdx = consts[i+1]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres2
                    objConst['BrkThres2'] = breakThres2   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, 0))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock direction for tensile force
                        objConst.rigid_body_constraint.use_limit_lin_x = 1
                        objConst.rigid_body_constraint.use_limit_lin_y = 0
                        objConst.rigid_body_constraint.use_limit_lin_z = 0
                        objConst.rigid_body_constraint.limit_lin_x_lower = -99999
                        objConst.rigid_body_constraint.limit_lin_x_upper = 0
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation like above
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    ### Third constraint
                    cIdx = consts[i+2]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres3
                    objConst['BrkThres3'] = breakThres3   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, 0))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock directions for shearing force
                        objConst.rigid_body_constraint.use_limit_lin_x = 0
                        objConst.rigid_body_constraint.use_limit_lin_y = 1
                        objConst.rigid_body_constraint.use_limit_lin_z = 1
                        objConst.rigid_body_constraint.limit_lin_y_lower = 0
                        objConst.rigid_body_constraint.limit_lin_y_upper = 0
                        objConst.rigid_body_constraint.limit_lin_z_lower = 0
                        objConst.rigid_body_constraint.limit_lin_z_upper = 0
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation like above
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))

            elif connectType == 14:
                # Correction multiplier for breaking thresholds
                # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
                # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
                correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
                correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
                radius = bendingThickness /2
                ### Calculate orientation between the two elements, imagine a line from center to center
                dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
                if alignVertical:
                    # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                    dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                constBreakThres1 = ((( contactArea *1000000 *breakThres1 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres2 = ((( contactArea *1000000 *breakThres2 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres3 = ((( contactArea *1000000 *breakThres3 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                constBreakThres4 = ((( (contactArea *bendingThickness) *1000000 *breakThres4 ) /scene.rigidbody_world.steps_per_second) *scene.rigidbody_world.time_scale) *correction
                # Loop through all constraints of this connection
                i = -3
                for j in range(4):
                    i += 3
                    ### First constraint
                    cIdx = consts[i]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres1
                    objConst['BrkThres1'] = breakThres1   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, -radius))
                        elif j == 3: vec = Vector((0, -radius, radius))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock direction for compressive force
                        objConst.rigid_body_constraint.use_limit_lin_x = 1
                        objConst.rigid_body_constraint.use_limit_lin_y = 0
                        objConst.rigid_body_constraint.use_limit_lin_z = 0
                        objConst.rigid_body_constraint.limit_lin_x_lower = 0
                        objConst.rigid_body_constraint.limit_lin_x_upper = 99999
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation to that vector
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    ### Second constraint
                    cIdx = consts[i+1]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres2
                    objConst['BrkThres2'] = breakThres2   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, -radius))
                        elif j == 3: vec = Vector((0, -radius, radius))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock direction for tensile force
                        objConst.rigid_body_constraint.use_limit_lin_x = 1
                        objConst.rigid_body_constraint.use_limit_lin_y = 0
                        objConst.rigid_body_constraint.use_limit_lin_z = 0
                        objConst.rigid_body_constraint.limit_lin_x_lower = -99999
                        objConst.rigid_body_constraint.limit_lin_x_upper = 0
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation like above
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))
                    ### Third constraint
                    cIdx = consts[i+2]
                    if not asciiExport:
                        objConst = emptyObjs[cIdx]
                    else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                    objConst.rigid_body_constraint.breaking_threshold = constBreakThres3
                    objConst['BrkThres3'] = breakThres3   # Store value as ID property for debug purposes
                    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
                    if qUpdateComplete:
                        objConst.rotation_mode = 'QUATERNION'
                        objConst.rigid_body_constraint.type = 'GENERIC_SPRING'
                        objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                        objConst.empty_draw_size = emptyDrawSize
                        ### Rotate constraint matrix
                        if   j == 0: vec = Vector((0, radius, radius))
                        elif j == 1: vec = Vector((0, radius, -radius))
                        elif j == 2: vec = Vector((0, -radius, -radius))
                        elif j == 3: vec = Vector((0, -radius, radius))
                        vec.rotate(objConst.rotation_quaternion)
                        objConst.location += vec
                        ### Enable linear spring
                        objConst.rigid_body_constraint.use_spring_x = 1
                        objConst.rigid_body_constraint.use_spring_y = 1
                        objConst.rigid_body_constraint.use_spring_z = 1
                        objConst.rigid_body_constraint.spring_damping_x = 1
                        objConst.rigid_body_constraint.spring_damping_y = 1
                        objConst.rigid_body_constraint.spring_damping_z = 1
                        ### Lock directions for shearing force
                        objConst.rigid_body_constraint.use_limit_lin_x = 0
                        objConst.rigid_body_constraint.use_limit_lin_y = 1
                        objConst.rigid_body_constraint.use_limit_lin_z = 1
                        objConst.rigid_body_constraint.limit_lin_y_lower = 0
                        objConst.rigid_body_constraint.limit_lin_y_upper = 0
                        objConst.rigid_body_constraint.limit_lin_z_lower = 0
                        objConst.rigid_body_constraint.limit_lin_z_upper = 0
                        objConst.rigid_body_constraint.use_limit_ang_x = 0
                        objConst.rigid_body_constraint.use_limit_ang_y = 0
                        objConst.rigid_body_constraint.use_limit_ang_z = 0
                        #objConst.rigid_body_constraint.disable_collisions = False
                    # Set stiffness
                    objConst.rigid_body_constraint.spring_stiffness_x = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_y = springStiff
                    objConst.rigid_body_constraint.spring_stiffness_z = springStiff
                    # Align constraint rotation like above
                    objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
                    if asciiExport:
                        exportData[cIdx].append(["TOLERANCE", tol1dist, tol1rot])
                        exportData[cIdx].append(["PLASTIC", tol2dist, tol2rot])
                        exportData[cIdx].append(objConst.rotation_mode)
                        exportData[cIdx].append(Vector(objConst.rotation_quaternion).to_tuple())
                        exportData[cIdx].append(getAttribsOfConstraint(objConst))

    if asciiExport:
        # Remove constraint settings from temporary empty object
        bpy.ops.rigidbody.constraint_remove()
        # Delete temporary empty object
        scene.objects.unlink(objConst)
        
    print()
        
################################################################################

def createParentsIfRequired(scene, objs, objsEGrp, childObjs):

    ### Create parents if required
    print("Creating invisible parent / visible child elements...")
    
    ### Store selection
    selectionOld = []
    for k in range(len(objs)):
        if objs[k].select:
            selectionOld.append(k)
                
    ### Selecting objects without parent
    q = 0
    for k in range(len(objs)):
        obj = objs[k]
        facing = elemGrps[objsEGrp[k]][16]
        if facing:
            q = 1
            if obj.select:
                if not "bcb_child" in obj.keys():
                    obj["bcb_parent"] = obj.name
                else: obj.select = 0
        else: obj.select = 0
        
    if q:
        # Duplicate selected objects            
        bpy.ops.object.duplicate(linked=False)
        ### Add newly created objects to parent object list and make them actual parents
        childObjsNew = []
        for obj in scene.objects:
            if obj.select:
                childObjsNew.append(obj)
                obj.select = 0
        childObjs.extend(childObjsNew)
        
        ### Make parent relationship
        for k in range(len(childObjsNew)):
            sys.stdout.write('\r' +"%d" %k)
            
            childObj = childObjsNew[k]
            parentObj = scene.objects[childObj["bcb_parent"]]
            del parentObj["bcb_parent"]
            parentObj["bcb_child"] = childObj.name
            ### Make parent
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = parentObj
            bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
            parentObj.select = 0
            childObj.select = 0
            if len(childObjsNew) > 0: print()
        ### Remove child object from rigid body world (should not be simulated anymore)
        for k in range(len(childObjsNew)):
            childObjsNew[k].select
        bpy.ops.rigidbody.objects_remove()
        
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    ### Revert back to original selection
    for idx in selectionOld:
        objs[idx].select = 1       
        
################################################################################

def applyScale(scene, objs, objsEGrp, childObjs):
    
    ### Scale elements by custom scale factor and make separate collision object for that
    print("Applying scale...")
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    obj = None
    ### Select objects in question
    for k in range(len(objs)):
        scale = elemGrps[objsEGrp[k]][15]
        if scale != 0 and scale != 1:
            obj = objs[k]
            obj.select = 1
    
    if obj != None:
        ###### Create parents if required
        createParentsIfRequired(scene, objs, objsEGrp, childObjs)
        ### Apply scale
        for k in range(len(objs)):
            obj = objs[k]
            if obj.select:
                scale = elemGrps[objsEGrp[k]][15]
                obj.scale *= scale
                # For children invert scaling to compensate for indirect scaling through parenting
                if "bcb_child" in obj.keys():
                    scene.objects[obj["bcb_child"]].scale /= scale
                    
################################################################################   

def applyBevel(scene, objs, objsEGrp, childObjs):
    
    ### Bevel elements and make separate collision object for that
    print("Applying bevel...")
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    obj = None
    ### Select objects in question
    for k in range(len(objs)):
        qBevel = elemGrps[objsEGrp[k]][14]
        if qBevel:
            obj = objs[k]
            obj.select = 1
    
    ### Add only one bevel modifier and copy that to the other selected objects (Todo: Should be done for each object individually but is slower)
    if obj != None:
        ###### Create parents if required
        createParentsIfRequired(scene, objs, objsEGrp, childObjs)
        ### Apply bevel
        bpy.context.scene.objects.active = obj
        if "Bevel_bcb" not in obj.modifiers:
            bpy.ops.object.modifier_add(type='BEVEL')
            obj.modifiers["Bevel"].name = "Bevel_bcb"
            obj.modifiers["Bevel_bcb"].width = 10.0
            bpy.ops.object.make_links_data(type='MODIFIERS')
    
    ### Make modifiers real (required to be taken into account by Bullet physics)
    for k in range(len(objs)):
        obj = objs[k]
        if obj.select:
            bpy.context.scene.objects.active = obj
            bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Bevel_bcb")
       
################################################################################   

def calculateMass(scene, objs, objsEGrp, childObjs):
    
    ### Calculate a mass for all mesh objects according to element groups settings
    print("Calculating masses from preset material... (Children: %d)" %len(childObjs))
     
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    ### Create new rigid body settings for children with the data from its parent (so mass can be calculated on children)
    i = 0
    for childObj in childObjs:
        parentObj = scene.objects[childObj["bcb_parent"]]
        if parentObj.rigid_body != None:
            sys.stdout.write('\r' +"%d  " %i)
            i += 1
            
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_add()
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = parentObj
            bpy.ops.rigidbody.object_settings_copy()
            parentObj.select = 0
            childObj.select = 0
    if len(childObjs) > 0: sys.stdout.write('\r        ')
            
    ### Update masses
    for j in range(len(elemGrps)):
        elemGrp = elemGrps[j]
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        for k in range(len(objs)):
            if j == objsEGrp[k]:
                obj = objs[k]
                if obj != None:
                    if obj.rigid_body != None:
                        if not "bcb_child" in obj.keys():
                            obj.select = 1
                        else:
                            scene.objects[obj["bcb_child"]].select = 1
        
        materialPreset = elemGrp[2]
        materialDensity = elemGrp[3]
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material="Custom", density=materialDensity)
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Copy rigid body settings (and mass) from children back to their parents and remove children from rigid body world
    i = 0
    for childObj in childObjs:
        parentObj = scene.objects[childObj["bcb_parent"]]
        if parentObj.rigid_body != None:
            sys.stdout.write('\r' +"%d  " %i)
            i += 1
            
            parentObj.select = 1
            childObj.select = 1
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_settings_copy()
            parentObj.select = 0
            childObj.select = 0
    ### Remove child objects from rigid body world (should not be simulated anymore)
    for childObj in childObjs:
        childObj.select
    bpy.ops.rigidbody.objects_remove()
            
    if len(childObjs) > 0: print()
            
################################################################################   

def exportDataToText(exportData):

    ### Exporting data into internal ASCII text file
    print("Exporting data into internal ASCII text file:", asciiExportName)
    
    # Data structure ("[]" means not always present):
    # 0 - empty.location
    # 1 - obj1.name
    # 2 - obj2.name
    # 3 - [ ["TOLERANCE", tol1dist, tol1rot] ]
    # 4 - [ ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot] ]
    # 5 - [empty.rotation_mode]
    # 6 - [empty.rotation_quaternion]
    # 7 - empty.rigid_body_constraint (dictionary of attributes)
    #
    # Pseudo code for special constraint treatment:
    #
    # If tol1dist or tol1rot is exceeded:
    #     If normal constraint: It will be detached
    #     If spring constraint: It will be set to active
    # If tol2dist or tol2rot is exceeded:
    #     If spring constraint: It will be detached

    ### Ascii export into internal text file
    exportDataStr = pickle.dumps(exportData, 4)  # 0 for using real ASCII pickle protocol and comment out the base64 lines (slower but human readable)
    exportDataStr = zlib.compress(exportDataStr, 9)
    exportDataStr = base64.encodebytes(exportDataStr)  # Convert binary data into "text" representation
    text = bpy.data.texts.new(asciiExportName)
    text.write(exportDataStr.decode())
    
    ### Code for loading data back from text
#    exportDataStr = text.as_string()
#    exportDataStr = base64.decodestring(exportDataStr.encode())  # Convert binary data back from "text" representation
#    exportDataStr = zlib.decompress(exportDataStr)
#    exportData = pickle.loads(exportDataStr)  # Use exportDataStr.encode() here when using real ASCII pickle protocol
#    print(exportData)
    # For later import you can use setattr(item[0], item[1])
      
################################################################################   
################################################################################   
    
def build():
    
    print("\nStarting...\n")
    time_start = time.time()
        
    if "RigidBodyWorld" in bpy.data.groups:
    
        bpy.context.tool_settings.mesh_select_mode = True, False, False
        scene = bpy.context.scene
        # Display progress bar
        bpy.context.window_manager.progress_begin(0, 100)
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT') 
        except: pass
        
        exportData = None

        #########################
        ###### Create new empties
        if not "bcb_objs" in scene.keys():
                
            ###### Create object lists of selected objects
            childObjs = []
            objs, emptyObjs = gatherObjects(scene)
            objsEGrp = createElementGroupIndex(objs)
            
            # Remove instancing from objects
            bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True, material=False, texture=False, animation=False)
            # Apply scale factor of all objects (to make sure volume and mass calculation are correct)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            if len(objs) > 1:
                #############################
                ###### Prepare connection map
                time_start_connections = time.time()
                
                ###### Find connections by vertex pairs
                #connectsPair, connectsPairDist = findConnectionsByVertexPairs(objs, objsEGrp)
                ###### Find connections by boundary box intersection and skip connections whose elements are too small and store them for later parenting
                connectsPair, connectsPairDist = findConnectionsByBoundaryBoxIntersection(objs)
                ###### Delete connections whose elements are too small and make them parents instead
                if minimumElementSize: connectsPair, connectsPairParent = deleteConnectionsWithTooSmallElementsAndParentThemInstead(objs, connectsPair, connectsPairDist)
                else: connectsPairParent = []
                ###### Delete connections with too few connected vertices
                #connectsPair = deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair)
                ###### Calculate contact area for all connections
                if useAccurateArea:
                    #connectsArea, connectsLoc = calculateContactAreaBasedOnBooleansForAll(objs, connectsPair)
                    connectsArea, connectsLoc = calculateContactAreaBasedOnMaskingForAll(objs, connectsPair)
                else:
                    connectsArea, connectsLoc = calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair)
                ###### Delete connections with zero contact area
                connectsPair, connectsArea, connectsLoc = deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsArea, connectsLoc)
                ###### Create connection data
                connectsPair, connectsConsts, constsConnect = createConnectionData(objsEGrp, connectsPair)
                
                print('-- Time: %0.2f s\n' %(time.time()-time_start_connections))
                
                #########################                        
                ###### Main building part
                if len(constsConnect) > 0:
                    time_start_building = time.time()
                    
                    ###### Scale elements by custom scale factor and make separate collision object for that
                    applyScale(scene, objs, objsEGrp, childObjs)
                    ###### Bevel elements and make separate collision object for that
                    applyBevel(scene, objs, objsEGrp, childObjs)
                    ###### Create actual parents for too small elements
                    if minimumElementSize: makeParentsForTooSmallElementsReal(objs, connectsPairParent)
                    ###### Find and activate first empty layer
                    layersBak = BackupLayerSettingsAndActivateNextEmptyLayer(scene)
                    ###### Create empty objects (without any data)
                    if not asciiExport:
                        emptyObjs = createEmptyObjs(scene, len(constsConnect))
                    else:
                        emptyObjs = [None for i in range(len(constsConnect))]
                        exportData = [[] for i in range(len(emptyObjs))]  # if this is the case emptyObjs is filled with an empty array on None
                    ###### Bundling close empties into clusters, merge locations and count connections per cluster
                    if clusterRadius > 0: bundlingEmptyObjsToClusters(connectsLoc, connectsConsts)
                    ###### Add constraint base settings to empties
                    addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect, exportData)
                    # Restore old layers state
                    scene.update()  # Required to update empty locations before layer switching
                    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)
                    ###### Store build data in scene
                    if not asciiExport: storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsArea, connectsConsts, constsConnect)
                    
                    print('-- Time: %0.2f s\n' %(time.time()-time_start_building))
                
                ###########################
                ###### No connections found   
                else:
                    print('No connections found. Probably the search distance is too small.')       
            
            #####################
            ###### No input found   
            else:
                print('Please select at least two mesh objects to connect.')       
                print('Nothing done.')       
       
        ##########################################     
        ###### Update already existing constraints
        if "bcb_objs" in scene.keys() or asciiExport:
            
            ###### Store menu config data in scene
            storeConfigDataInScene(scene)
            ###### Get temp data from scene
            if not asciiExport: objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsArea, connectsConsts, constsConnect = getBuildDataFromScene(scene)
            ###### Create fresh element group index to make sure the data is still valid (reordering in menu invalidates it for instance)
            objsEGrp = createElementGroupIndex(objs)
            ###### Store build data in scene
            storeBuildDataInScene(scene, None, objsEGrp, None, None, None, None, None, None, None, None)
                            
            if len(emptyObjs) > 0:
                ###### Set general rigid body world settings
                initGeneralRigidBodyWorldSettings(scene)
                ###### Set constraint settings
                setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsArea, connectsConsts, constsConnect, exportData)
                ###### Calculate mass for all mesh objects
                calculateMass(scene, objs, objsEGrp, childObjs)
                ###### Exporting data into internal ASCII text file
                if asciiExport: exportDataToText(exportData)
                    
                if not asciiExport:
                    # Deselect all objects
                    bpy.ops.object.select_all(action='DESELECT')
                    # Select all new constraint empties
                    for emptyObj in emptyObjs: emptyObj.select = 1
                
                print('-- Time total: %0.2f s\n' %(time.time()-time_start))
                print('Constraints:', len(emptyObjs), '| Elements:', len(objs), '| Children:', len(childObjs))
                print('Done.')

            #####################
            ###### No input found   
            else:
                print('Neither mesh objects to connect nor constraint empties for updating selected.')       
                print('Nothing done.')
                     
    ####################################
    ###### No RigidBodyWorld group found   
    else:
        print('No "RigidBodyWorld" group found in scene. Please create rigid bodies first.')       
        print('Nothing done.')       
        
    # Terminate progress bar
    bpy.context.window_manager.progress_end()
           
################################################################################   
################################################################################   

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.bcb = bpy.props.PointerProperty(type=bcb_props)
    # Reinitialize menu for convenience reasons when running from text window
    props = bpy.context.window_manager.bcb
    props.prop_menu_gotConfig = 0
    props.prop_menu_gotData = 0
    props.props_update_menu()
    
           
def unregister():
    for c in classes:
        try: bpy.utils.unregister_class(c) 
        except: pass
    del bpy.types.WindowManager.bcb
 
 
if __name__ == "__main__":
    if withGUI:
        register()
    else:
        build()
