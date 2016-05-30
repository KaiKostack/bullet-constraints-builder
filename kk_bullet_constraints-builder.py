####################################
# Bullet Constraints Builder v2.29 #
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
timeScalePeriod = 0          # 0     | For baking: Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled)
timeScalePeriodValue = 0.001 # 0.001 | For baking: Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime
warmUpPeriod = 20            # 20    | For baking: Disables breakability of constraints for an initial period of the simulation (frames). This is to prevent structural damage caused by the gravity impulse on start
progrWeak = 0                # 0     | Enables progressive weakening of all breaking thresholds by the specified factor per frame (starts not until timeScalePeriod and warmUpPeriod have passed). This can be used to enforce the certain collapse of a building structure after a while.
progrWeakLimit = 10          # 10    | For progressive weakening: Limits the weakening process by the number of broken connections per frame. If the limit is exceeded weakening will be disabled for the rest of the simulation.
progrWeakStartFact = 1       # 1     | Start weakness as factor all breaking thresholds will be multiplied with. This can be used to quick-change the initial thresholds without performing a regular update.
snapToAreaOrient = 1         # 1     | Enables axis snapping based on contact area orientation for constraints rotation instead of using center to center vector alignment (old method).
disableCollision = 1         # 1     | Disables collisions between connected elements until breach.

### Vars not directly accessible from GUI
asciiExport = 0              # 0     | Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment).

### Customizable element groups list (for elements of different conflicting groups the weaker thresholds is used, also the type is changed accordingly)
elemGrps = [
# 0          1    2           3        4   5       6         7         8      9         10     11      12   13   14   15    16   17    18     19              20
# Name       RVP  Mat.preset  Density  CT  BTC     BTT       BTS       BTS90  BTB       BTB90  Stiff.  T1D. T1R. T2D. T2R.  Bev. Scale Facing F.Assist.+Data  Cyl
[ "",        1,   "Concrete", 2400,    6,  "35*a", "5.2*a",  "155*a",  "",    "1.0*a",  "",    10**6,  .1,  .1,  .2,  1.6,  0,   .95,  0,     "con_rei_beam", 0 ],
[ "Columns", 1,   "Concrete", 2400,    6,  "35*a", "5.2*a",  "155*a",  "",    "1.0*a",  "",    10**6,  .1,  .1,  .2,  1.6,  0,   .95,  0,     "con_rei_beam", 0 ],
[ "Walls",   1,   "Concrete", 2400,    6,  "35*a", "5.2*a",  "0.9*a",  "",    "1.0*a",  "",    10**6,  .1,  .1,  .2,  1.6,  0,   .95,  0,     "con_rei_wall", 0 ],
[ "Slabs",   1,   "Concrete", 2400,    6,  "35*a", "5.2*a",  "0.9*a",  "",    "1.0*a",  "",    10**6,  .1,  .1,  .2,  1.6,  0,   .95,  0,     "con_rei_wall", 0 ],
[ "Masonry", 1,   "Masonry",  1800,    6,  "10*a", "2*a",    "0.3*a",  "",    "0.3*a",  "",    10**6,  .1,  .1,  .2,  1.6,  0,   .95,  0,     "None",         0 ]
] # Empty name means this group is to be used when element is not part of any element group

### Magic numbers / column descriptions for above element group settings (in order from left to right):
EGSidxName = 0    # Group Name               | The name of the object group these settings will be used for
EGSidxRqVP = 1    # Required Vertex Pairs    | How many vertex pairs between two elements are required to generate a connection.
                  # (Depreciated)            | This can help to ensure there is an actual surface to surface connection between both elements (for at least 3 verts you can expect a shared surface).
                  #                          | For two elements from different groups with different RVPs the lower number is decisive.
EGSidxMatP = 2    # Material Preset          | Preset name of the physical material to be used from Blender's internal database.
                  #                          | See Blender's Rigid Body Tools for a list of available presets.
EGSidxDens = 3    # Material Density         | Custom density value (kg/m^3) to use instead of material preset (0 = disabled).
EGSidxCTyp = 4    # Connection Type          | Connection type ID for the constraint presets defined by this script, see list below.
EGSidxBTC  = 5    # Break.Thresh.Compres.    | Real world material compressive breaking threshold in N/mm^2.
EGSidxBTT  = 6    # Break.Thresh.Tensile     | Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).
EGSidxBTS  = 7    # Break.Thresh.Shear       | Real world material shearing breaking threshold in N/mm^2.
EGSidxBTS9 = 8    # Break.Thresh.Shear 90°   | Real world material shearing breaking threshold with h and w swapped (rotated by 90°) in N/mm^2. If undefined other shearing threshold is used.
EGSidxBTB  = 9    # Break.Thresh.Bend        | Real world material bending breaking threshold in N/mm^2.
EGSidxBTB9 = 10   # Break.Thresh.Bend 90°    | Real world material bending breaking threshold with h and w swapped (rotated by 90°) in N/mm^2. If undefined other shearing threshold is used.
EGSidxSStf = 11   # Spring Stiffness         | Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.
EGSidxTl1D = 12   # Tolerance 1st Def.Dist.  | For baking: First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %)
EGSidxTl1R = 13   # Tolerance 1st Def.Rot.   | For baking: First deformation tolerance limit for angular change in radian for connection removal or plastic deformation
EGSidxTl2D = 14   # Tolerance 2nd Def.Dist.  | For baking: Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %)
EGSidxTl2R = 15   # Tolerance 2nd Def.Rot.   | For baking: Second deformation tolerance limit for angular change in radian for connection removal
EGSidxBevl = 16   # Bevel                    | Use beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes)
EGSidxScal = 17   # Scale                    | Apply scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes)
EGSidxFacg = 18   # Facing                   | Generate an addional layer of elements only for display (will only be used together with bevel and scale option)
EGSidxAsst = 19   # Formula Assistant        | Material specific formula assistant with related settings
EGSidxCyln = 20   # Cylindrical Shape        | Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns.

### Connection Types:
connectTypes = [           # Cnt C T S B S T T T T      CT
[ "UNDEFINED",               0, [0,0,0,0,0,1,1,0,0]], # 0. Undefined (reserved)
[ "1x FIXED",                1, [1,0,0,0,0,1,1,0,0]], # 1. Linear omni-directional + bending breaking threshold
[ "1x POINT",                1, [1,0,0,0,0,1,1,0,0]], # 2. Linear omni-directional breaking threshold
[ "1x POINT + 1x FIXED",     2, [1,0,0,1,0,1,1,0,0]], # 3. Linear omni-directional and bending breaking thresholds
[ "2x GENERIC",              2, [1,1,0,0,0,1,1,0,0]], # 4. Compressive and tensile breaking thresholds
[ "3x GENERIC",              3, [1,1,0,1,0,1,1,0,0]], # 5. Compressive, tensile + shearing and bending breaking thresholds
[ "4x GENERIC",              4, [1,1,1,1,0,1,1,0,0]], # 6. Compressive, tensile, shearing and bending breaking thresholds
[ "3x SPRING",               3, [1,0,0,0,1,0,0,1,1]], # 7. Linear omni-directional breaking threshold with plastic deformability
[ "4x SPRING",               4, [1,0,0,0,1,0,0,1,1]], # 8. Linear omni-directional breaking threshold with plastic deformability
[ "1x FIXED + 3x SPRING",    4, [1,0,0,0,1,1,1,1,1]], # 9. Linear omni-directional + bending breaking threshold with plastic deformability
[ "1x FIXED + 4x SPRING",    5, [1,0,0,0,1,1,1,1,1]], # 10. Linear omni-directional + bending breaking threshold with plastic deformability
[ "4x GENERIC + 3x SPRING",  7, [1,1,1,1,1,1,1,1,1]], # 11. Compressive, tensile, shearing and bending breaking thresholds with plastic deformability
[ "4x GENERIC + 4x SPRING",  8, [1,1,1,1,1,1,1,1,1]], # 12. Compressive, tensile, shearing and bending breaking thresholds with plastic deformability
[ "3 x 3x SPRING",           9, [1,1,1,0,1,0,0,1,1]], # 13. Compressive, tensile and shearing breaking thresholds with plastic deformability
[ "3 x 4x SPRING",          12, [1,1,1,0,1,0,0,1,1]], # 14. Compressive, tensile and shearing breaking thresholds with plastic deformability
[ "6x GENERIC",              6, [1,1,1,1,0,1,1,0,0]], # 15. Compressive, tensile, shearing XY and bending XY breaking thresholds
[ "7x GENERIC",              7, [1,1,1,1,0,1,1,0,0]], # 16. Compressive, tensile, shearing XY and bending XY and torsion breaking thresholds
[ "6x GENERIC + 3x SPRING",  9, [1,1,1,1,1,1,1,1,1]], # 17. Compressive, tensile, shearing XY and bending XY breaking thresholds with plastic deformability
[ "7x GENERIC + 3x SPRING", 10, [1,1,1,1,1,1,1,1,1]]  # 18. Compressive, tensile, shearing XY and bending XY and torsion breaking thresholds with plastic deformability
]
# To add further connection types changes to following functions are necessary:
# setConstraintSettings() and bcb_panel() for the UI

### Formula Assistants with defaults (see definitions below for reference):
formulaAssistants = [
{"Name":"None", "ID":"None"},
{"Name":"Reinforced Concrete (Beams & Columns)", "ID":"con_rei_beam",
 "h":250, "w":150, "fc":30, "fs":500, "c":20, "s":100, "ds":6, "dl":10, "n":5, "k":1.9,
 "Exp:d":   "h-c-dl/2",
 "Exp:e":   "h-2*c-dl",
 "Exp:rho": "(dl/2)**2*pi*n/(h*w)",
 "Exp:y":   "((ds/2)**2*pi*2/100*1000/s)*10/d",
 "Exp:e1":  "(h-2*c-dl)/h",
 "Exp:N-":  "fc*((h*w)-rho*(h*w))+fs*rho*(h*w)",
 "Exp:N+":  "fs*rho*(h*w)",
 "Exp:V+/-":"fs*y*e1*h**2*1.2",
 "Exp:M+/-":"(fc*(1-rho)/4+fs*rho*e1)*(h*w)*h/2/1000"
},
{"Name":"Reinforced Concrete (Walls & Slabs)", "ID":"con_rei_wall",
 "h":250, "w":150, "fc":30, "fs":500, "c":20, "s":100, "ds":6, "dl":10, "n":5, "k":1.9,
 "Exp:d":   "h-c-dl/2",
 "Exp:e":   "h-2*c-dl",
 "Exp:rho": "(dl/2)**2*pi*n/(h*w)",
 "Exp:y":   "((ds/2)**2*pi*2/100*1000/s)*10/d",
 "Exp:e1":  "(h-2*c-dl)/h",
 "Exp:N-":  "fc*((h*w)-rho*(h*w))+fs*rho*(h*w)",
 "Exp:N+":  "fs*rho*(h*w)",
 "Exp:V+/-":"(0.15*k*(100*rho*fc)**(1/3))*(h*w)",
 "Exp:M+/-":"(fc*(1-rho)+fs*rho*e1*4.5)*h*h*w/12/1000"
}]
# Material strength values (N/mm²):
# fs = strength of steel
# fc = strength of concrete
#
# Geometrical values (mm):
# h = height of element    
# b = width of element
# c = concrete cover
# d = distance between the tensile irons and the opposite concrete surface  h-c-dl/2
# e = distance between longitudinal irons                                   h-2*c-dl
# s = distance between stirrups
# ds = Ø steel stirrup bar
# dl = Ø steel longitudinal bar
#
# Areas (mm²):
# A = cross area beam, h*b
# As = total cross area of the sum of all longitudinal steel bars, (dl/2)²*pi
# asw = total cross area steel stirrup in cm²/m = (ds/2)²*pi*2 (per side one stirrup)*1000/s
#
# Coefficients:
# rho = reinforcement ratio = As/A             (dl/2)²*pi*n/h*b  
# y = shear coefficient (asw*10/d) (% value)   ((ds/2)²*pi*2)*10/(h-c-dl/2)
# 1.2 = coefficient for shear carrying capacity
# e1 = distance between longitudinal irons in relation to the beam height: e/h (% value)   (h-2*c-dl)/h
# n = number of longitudinal steel bars
# k = scale factor
#
# Formulas for beams & columns:
# N-      ≈ fc * (A- rho * (h*b))  +  fs* rho * (h*b)  
# N+      ≈ fs * rho * (h*b)   
# V+ = V- ≈ fs *y * e1*h²* 1,2  +  0.15/ k* ((100*rho*fc)^1/3) *h*b
# M+ = M- ≈ (fc*(1-rho) + fs*rho*e1*4.5) *h*h*w/12 /1000 
#
# Formulas for walls & slabs:
# N-      ≈ fc * (A- rho * (h*b))  +  fs* rho * (h*b)  
# N+      ≈ fs * rho * (h*b)   
# V+ = V- ≈ 0.15/k* ((100*rho*fc)^1/3) *h*b
# M+ = M- ≈ (fc*(1-rho) + fs*rho*e1*4.5) *h*h*w/12 /1000 

### Vars for developers
debug = 0                            # 0     | Enables verbose console output for debugging purposes
withGUI = 1                          # 1     | Enable graphical user interface, after pressing the "Run Script" button the menu panel should appear
logPath = r"/tmp"                    #       | Path to log files if debugging is enabled
commandStop = r"/tmp/bcb-stop"       #       | For very large simulations Blender can become unresponsive on baking, in this case you can create this file to make the BCB aware you want to stop
maxMenuElementGroupItems = 100       # 100   | Maximum allowed element group entries in menu 
emptyDrawSize = 0.25                 # 0.25  | Display size of constraint empty objects as radius in meters
asciiExportName = "BCB_export.txt"   #       | Name of ASCII text file to be exported
    
# For monitor event handler
qRenderAnimation = 0                 # 0     | Render animation by using render single image function for each frame (doesn't support motion blur, keep it disabled), 1 = regular, 2 = OpenGL

### Consts
pi = 3.1416
pi2 = pi /2
        
########################################

# Add formula assistant settings to element groups
for elemGrp in elemGrps:
    for formAssist in formulaAssistants:
        if elemGrp[EGSidxAsst] == formAssist['ID']:
            elemGrp[EGSidxAsst] = formAssist.copy()
            break

# Backup default element groups for reset functionality
elemGrpsBak = elemGrps.copy()

################################################################################   

bl_info = {
    "name": "Bullet Constraints Builder",
    "author": "Kai Kostack",
    "version": (2, 2, 9),
    "blender": (2, 7, 5),
    "location": "View3D > Toolbar",
    "description": "Tool to connect rigid bodies via constraints in a physical plausible way.",
    "wiki_url": "http://www.inachus.eu",
    "tracker_url": "http://kaikostack.com",
    "category": "Animation"}

import bpy, sys, os, platform, mathutils, time, copy, math, pickle, base64, zlib
from mathutils import Vector
#import os
#os.system("cls")

###### SymPy detection and import code
### Try to import SymPy
try: import sympy
except:
    pythonLibsPaths = []
    if platform.system() == 'Windows':
        #pythonLibsPaths.append(r"c:\Python34\Lib\site-packages")
        ### Try to find most recent path in registry
        import winreg
        regPath = r"SOFTWARE\Python\PythonCore"
        searchKey = "InstallPath"
        reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
        #reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        try: keyA = winreg.OpenKey(reg, regPath)
        except: pass
        else:
            pathFound = ""
            for i in range(1024):
                try: regPathA = winreg.EnumKey(keyA, i)
                except: pass
                else:
                    keyB = winreg.OpenKey(reg, regPath +"\\" +regPathA)
                    for j in range(1024):
                        try: regPathB = winreg.EnumKey(keyB, j)
                        except: pass
                        else:
                            keyC = winreg.OpenKey(reg, regPath +"\\" +regPathA +"\\" +regPathB)
                            if regPathB == searchKey:
                                try: val = winreg.QueryValueEx(keyC, "")
                                except: pass
                                else: pathFound = val[0]
            if len(pathFound):
                print("Python path found in registry:", pathFound)
                pythonLibsPaths.append(pathFound)                  
        # Add possible Python path(s) to known import paths
        for path in pythonLibsPaths:
            if path not in sys.path: sys.path.append(path)

    elif platform.system() == 'Linux':
        #pythonLibsPaths.append(r"/home/user/.local/lib/python3.4/site-packages")
        # Add possible Python path(s) to known import paths
        for path in pythonLibsPaths:
            if path not in sys.path: sys.path.append(path)

    else: print('Unknown platform detected, unable to guess path to Python:', platform.system())

### Try to import SymPy from paths
try: import sympy
except:
    ### If not found attempt using pip to automatically install SymPy module in Blender
    import subprocess, bpy
    def do(cmd, *arg):
        list = [bpy.app.binary_path_python, '-m', cmd]
        list.extend(arg)
        command = (list)       
        p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1)
        for line in iter(p.stdout.readline, b''):
            print(line.decode())
        p.stdout.close()
        p.wait()
    #do('pip', '--version')
    do('ensurepip')
    do('pip', 'install', '--upgrade', 'pip')
    do('pip', 'install', 'sympy')

### Ultimate attempt to import SymPy
try: import sympy
except:
    print("No SymPy module found, continuing without formula simplification feature...")
    qSymPy = 0
else:
    print("SymPy module found.")
    qSymPy = 1

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
    listNew1 = []
    for sub1 in listOld:
        try: test = len(sub1)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
        except: listNew1.append(sub1); continue  # If it fails it is no list (and also no vector)
        else:
            if isinstance(sub1, str):            # It could still be a string so check that as well
                listNew1.append(sub1); continue  
        listNew2 = []
        for sub2 in sub1:
            try: test = len(sub2)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
            except: listNew2.append(sub2); continue  # If it fails it is no list (and also no vector)
            else:
                if isinstance(sub2, str):            # It could still be a string so check that as well
                    listNew2.append(sub2); continue  
            listNew3 = []
            for sub3 in sub2:
                try: test = len(sub3)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
                except: listNew3.append(sub3); continue  # If it fails it is no list (and also no vector)
                else:
                    if isinstance(sub3, str):            # It could still be a string so check that as well
                        listNew3.append(sub3); continue  
                listNew4 = []
                for sub4 in sub3:
                    listNew4.append(sub4)
                listNew3.append(listNew4)
            listNew2.append(listNew3)
        listNew1.append(listNew2)
    return listNew1

################################################################################

def storeConfigDataInScene(scene):

    ### Store menu config data in scene
    if debug: print("Storing menu config data in scene...")
    
    scene["bcb_version"] = bl_info["version"]
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
    scene["bcb_prop_timeScalePeriod"] = timeScalePeriod
    scene["bcb_prop_timeScalePeriodValue"] = timeScalePeriodValue 
    scene["bcb_prop_warmUpPeriod"] = warmUpPeriod
    scene["bcb_prop_progrWeak"] = progrWeak
    scene["bcb_prop_progrWeakLimit"] = progrWeakLimit
    scene["bcb_prop_progrWeakStartFact"] = progrWeakStartFact
    scene["bcb_prop_snapToAreaOrient"] = snapToAreaOrient
    scene["bcb_prop_disableCollision"] = disableCollision
    
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
    if debug: print("Getting menu config data from scene...")

    warning = ""
    if "bcb_version" in scene.keys():
        versionCfg = scene["bcb_version"]
        version = bl_info["version"]
        if versionCfg != version:
            if versionCfg[0] < version[0]:
                warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."
    else:   warning = "Configuration settings from an older BCB version detected which is known to be incompatible with this one.\nTry to clear settings and reconfigure your scene from scratch."

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
    if "bcb_prop_timeScalePeriod" in scene.keys():
        global timeScalePeriod
        try: timeScalePeriod = props.prop_timeScalePeriod = scene["bcb_prop_timeScalePeriod"]
        except: pass
    if "bcb_prop_timeScalePeriodValue" in scene.keys():
        global timeScalePeriodValue
        try: timeScalePeriodValue = props.prop_timeScalePeriodValue = scene["bcb_prop_timeScalePeriodValue"]
        except: pass
    if "bcb_prop_warmUpPeriod" in scene.keys():
        global warmUpPeriod
        try: warmUpPeriod = props.prop_warmUpPeriod = scene["bcb_prop_warmUpPeriod"]
        except: pass
    if "bcb_prop_progrWeak" in scene.keys():
        global progrWeak
        try: progrWeak = props.prop_progrWeak = scene["bcb_prop_progrWeak"]
        except: pass
    if "bcb_prop_progrWeakLimit" in scene.keys():
        global progrWeakLimit
        try: progrWeakLimit = props.prop_progrWeakLimit = scene["bcb_prop_progrWeakLimit"]
        except: pass
    if "bcb_prop_progrWeakStartFact" in scene.keys():
        global progrWeakStartFact
        try: progrWeakStartFact = props.prop_progrWeakStartFact = scene["bcb_prop_progrWeakStartFact"]
        except: pass
    if "bcb_prop_snapToAreaOrient" in scene.keys():
        global snapToAreaOrient
        try: snapToAreaOrient = props.prop_snapToAreaOrient = scene["bcb_prop_snapToAreaOrient"]
        except: pass
    if "bcb_prop_disableCollision" in scene.keys():
        global disableCollision
        try: disableCollision = props.prop_disableCollision = scene["bcb_prop_disableCollision"]
        except: pass

    if len(warning): return warning
            
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    if "bcb_prop_elemGrps" in scene.keys():
        global elemGrps
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
        elemGrps = elemGrpsInverted

        if debug:
            print("LOADED:", len(elemGrps), len(elemGrps[0]))
            for i in range(grpPropCnt):
                print(i, elemGrps[i][0], elemGrps[i][20])
                
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
        logDataToFile(log, logPath +r"\log_bcb_keys.txt")
        log = []
        log.append([obj.name for obj in bpy.context.scene.objects])
        logDataToFile(log, logPath +r"\log_bcb_scene.txt")
        
    return objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, constsConnect

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
        try: scale = elemGrps[objsEGrp[k]][EGSidxScal]  # Try in case elemGrps is from an old BCB version
        except: pass
        else:
            obj = objs[k]
            if scale != 0 and scale != 1:
                obj.scale /= scale

    print("Removing ID properties...")
    
    ### Clear object properties
    for obj in objs:
        for key in obj.keys(): del obj[key]

    ### Remove ID property build data (leaves menu props in place)
    for key in scene.keys():
        if "bcb_" in key: del scene[key]

    print("Deleting objects...")

    ### Select modified elements for deletion from scene 
    for parentObj in parentTmpObjs: parentObj.select = 1
    ### Select constraint empty objects for deletion from scene
    for emptyObj in emptyObjs: emptyObj.select = 1
    
    if automaticMode and saveBackups:
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

    print('\nTime: %0.2f s' %(time.time()-time_start))
    print('Done.')
        
################################################################################   
################################################################################

def monitor_eventHandler(scene):

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

        # Store start time
        bpy.app.driver_namespace["bcb_time"] = time.time()
        
        ###### Function
        monitor_initBuffers(scene)

        ### Time scale correction with rebuild
        if timeScalePeriod:
            # Backup original time scale
            bpy.app.driver_namespace["bcb_monitor_originalTimeScale"] = scene.rigidbody_world.time_scale
            bpy.app.driver_namespace["bcb_monitor_originalSolverIterations"] = scene.rigidbody_world.solver_iterations
            if scene.rigidbody_world.time_scale != timeScalePeriodValue:
                ### Decrease precision for solver at extreme scale differences towards high-speed,
                ### as high step and iteration rates on multi-constraint connections make simulation more instable
                ratio = scene.rigidbody_world.time_scale /timeScalePeriodValue
                if ratio >= 50: scene.rigidbody_world.solver_iterations /= 10
                if ratio >= 500: scene.rigidbody_world.solver_iterations /= 10
                if ratio >= 5000: scene.rigidbody_world.solver_iterations /= 10
                ### Set new time scale
                scene.rigidbody_world.time_scale = timeScalePeriodValue
                ###### Execute update of all existing constraints with new time scale
                build()

        ### Init weakening
        if progrWeak:
            bpy.app.driver_namespace["bcb_progrWeakCurrent"] = 1
            bpy.app.driver_namespace["bcb_progrWeakTmp"] = progrWeak
        if progrWeakStartFact != 1:
            progressiveWeakening(scene, progrWeakStartFact)
                                            
    ################################
    ### What to do AFTER start frame
    elif scene.frame_current > scene.frame_start:   # Check this to skip the last run when jumping back to start frame
        time_last = bpy.app.driver_namespace["bcb_time"]
        sys.stdout.write("Frm: %d - T: %0.2f s" %(scene.frame_current, time.time() -time_last))
        bpy.app.driver_namespace["bcb_time"] = time.time()
        if progrWeak and bpy.app.driver_namespace["bcb_progrWeakTmp"]:
            progrWeakCurrent = bpy.app.driver_namespace["bcb_progrWeakCurrent"]
            sys.stdout.write(" - Wk: %0.3fx" %(progrWeakCurrent *progrWeakStartFact))
    
        ###### Function
        cntBroken = monitor_checkForChange(scene)
        
        ### Apply progressive weakening factor
        if progrWeak and bpy.app.driver_namespace["bcb_progrWeakTmp"] \
        and (not timeScalePeriod or (timeScalePeriod and scene.frame_current > scene.frame_start +timeScalePeriod)) \
        and (not warmUpPeriod or (warmUpPeriod and scene.frame_current > scene.frame_start +warmUpPeriod)):
            if cntBroken < progrWeakLimit:
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
        if timeScalePeriod:
            if scene.frame_current == scene.frame_start +timeScalePeriod:
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
            
    ### Check if last frame is reached
    if scene.frame_current == scene.frame_end or os.path.isfile(commandStop):
        if bpy.context.screen.is_animation_playing:
            # Stop animation playback
            bpy.ops.screen.animation_play()
            if os.path.isfile(commandStop):
                print("Baking stopped by user through external file command.")
                os.remove(commandStop)

    ### If animation playback has stopped (can also be done by user) then unload the event handler and free all monitor data
    if not bpy.context.screen.is_animation_playing:
        print('Removing BCB monitor event handler.')
        for i in range( len( bpy.app.handlers.frame_change_pre ) ):
             bpy.app.handlers.frame_change_pre.pop()
        # Convert animation point cache to fixed bake data 
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.bake_from_cache(contextFix)
        # Free all monitor related data
        monitor_freeBuffers(scene)
        # Go back to start frame
        scene.frame_current = scene.frame_start
        # Continue with further automatic mode steps
        if automaticMode:
            automaticModeAfterStop()
            
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
        
        ### Use the connection type with the smaller count of constraints for connection between different element groups
        ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
        if connectTypes[elemGrps[elemGrpA][EGSidxCTyp]][1] <= connectTypes[elemGrps[elemGrpB][EGSidxCTyp]][1]:
              elemGrp = elemGrpA
        else: elemGrp = elemGrpB
        springStiff = elemGrps[elemGrp][EGSidxSStf]
        tol1dist = elemGrps[elemGrp][EGSidxTl1D] *scene.rigidbody_world.time_scale
        tol1rot = elemGrps[elemGrp][EGSidxTl1R] *scene.rigidbody_world.time_scale
        tol2dist = elemGrps[elemGrp][EGSidxTl2D] *scene.rigidbody_world.time_scale
        tol2rot = elemGrps[elemGrp][EGSidxTl2R] *scene.rigidbody_world.time_scale
        
        # Calculate distance between both elements of the connection
        distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
        # Calculate angle between two elements
        quat0 = objA.matrix_world.to_quaternion()
        quat1 = objB.matrix_world.to_quaternion()
        angle = quat0.rotation_difference(quat1).angle
        consts = []
        constsEnabled = []
        constsUseBrk = []
        constsBrkThres = []
        for const in connectsConsts[d -1]:
            emptyObj = emptyObjs[const]
            consts.append(emptyObj)
            if emptyObj.rigid_body_constraint != None and emptyObj.rigid_body_constraint.object1 != None:
                # Backup original settings
                constsEnabled.append(emptyObj.rigid_body_constraint.enabled)
                constsUseBrk.append(emptyObj.rigid_body_constraint.use_breaking)
                constsBrkThres.append(emptyObj.rigid_body_constraint.breaking_threshold)
                # Disable breakability for warm up time
                if warmUpPeriod: emptyObj.rigid_body_constraint.use_breaking = 0
                # Set tolerance evaluation mode (if plastic or not)
                if emptyObj.rigid_body_constraint.type == 'GENERIC_SPRING':
                      mode = 1
                else: mode = 0
            else:
                if not qWarning:
                    qWarning = 1
                    print("\rWarning: Element has lost its constraint references or the corresponding empties their constraint properties respectively, rebuilding constraints is recommended.")
                print("(%s)" %emptyObj.name)
                constsEnabled.append(0)
                constsUseBrk.append(0)
                constsBrkThres.append(0)
        #                0                1                2         3      4       5              6             7            8         9        10        11       12    13
        connects.append([[objA, pair[0]], [objB, pair[1]], distance, angle, consts, constsEnabled, constsUseBrk, springStiff, tol1dist, tol1rot, tol2dist, tol2rot, mode, constsBrkThres])

    print("Connections")
        
################################################################################

def monitor_checkForChange(scene):

    if debug: print("Calling checkForDistanceChange")
    
    connects = bpy.app.driver_namespace["bcb_monitor"]
    d = 0; e = 0; cntP = 0; cntB = 0
    for connect in connects:

        ### If connection is in fixed mode then check if first tolerance is reached
        if connect[12] == 0:
            d += 1
            consts = connect[4]
            if consts[0].rigid_body_constraint.use_breaking:
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
                if distanceDif > toleranceDist +(angleDif /pi) \
                or angleDif > toleranceRot:
                    for const in consts:
                        # Enable spring constraints for this connection by setting its stiffness
                        if const.rigid_body_constraint.type == 'GENERIC_SPRING':
                            const.rigid_body_constraint.enabled = 1
                        # Disable non-spring constraints for this connection
                        else: const.rigid_body_constraint.enabled = 0
                    # Switch connection to plastic mode
                    connect[12] += 1
                    cntP += 1

        ### If connection is in plastic mode then check if second tolerance is reached
        if connect[12] == 1:
            e += 1
            consts = connect[4]
            if consts[0].rigid_body_constraint.use_breaking:
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
                if distanceDif > toleranceDist +(angleDif /pi) \
                or angleDif > toleranceRot:
                    # Disable all constraints for this connection
                    for const in consts:
                        const.rigid_body_constraint.enabled = 0
                    # Flag connection as being disconnected
                    connect[12] += 1
                    cntB += 1

        ### Enable original breakability for all constraints when warm up time is over
        if warmUpPeriod:
            if scene.frame_current == scene.frame_start +warmUpPeriod:
                consts = connect[4]
                constsUseBrk = connect[6]
                for i in range(len(consts)):
                    const = consts[i]
                    const.rigid_body_constraint.use_breaking = constsUseBrk[i]
           
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
        constsUseBrk = connect[6]
        for const in consts:
            const.rigid_body_constraint.breaking_threshold *= progrWeakVar
        i += 1
    sys.stdout.write("\r")
            
################################################################################

def monitor_freeBuffers(scene):
    
    if debug: print("Calling freeBuffers")
    
    if "bcb_monitor" in bpy.app.driver_namespace.keys():
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
                
        if timeScalePeriod:
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
        if timeScalePeriod:
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

def convertFloatToStr(value, precision):
    
    global strOut  # For some reason this global construct is needed for exec() to have access to strOut
    exec("global strOut; strOut = (('%0.' +str(precision) +'f')%value).strip('0')")
    if '.' in strOut:
        # If digit count of the integer part is higher than precision then remove fractional part
        strOutInt = strOut.split('.')[0]
        if len(strOutInt) > precision: strOut = strOutInt
    strOut = strOut.rstrip('.')    # Remove ending decimal point if no fractional digits are present
    if strOut == '': strOut = '0'  # Replace a single left over decimal point with 0
    elif strOut[0] == '.': strOut = '0' +strOut  # Add a 0 before a leading decimal point (comment out to disable)
    return strOut

########################################

def splitAndApplyPrecisionToFormula(formulaIn):

    ### Split formula at predefined splitting strings and add spaces
    splitter = ['**', '+', '-', '*', '/', '(', ')', '[', ']', '!=', '>=', '<=', '==', '=']
    formulaOut = ""; charLast = ''; qSkipNext = 0
    for char in formulaIn:
        if qSkipNext:
            charLast = char; qSkipNext = 0; continue
        if charLast in splitter:
            if charLast +char not in splitter: formulaOut += ' ' +charLast +' '
            else: formulaOut += ' ' +charLast +char +' '; qSkipNext = 1
        else: formulaOut += charLast
        charLast = char
    if charLast in splitter: formulaOut += ' ' +charLast
    else: formulaOut += charLast
    formulaOut = formulaOut.replace('  ',' ')
    formulaOut = formulaOut.strip(' ')

    ### Apply precision to separated floats
    formulaToSplit = formulaOut; formulaOut = ''
    for term in formulaToSplit.split(' '):
        try: formulaOut += convertFloatToStr(float(term), 4) +' '
        except: formulaOut += term +' '
    formulaOut = formulaOut.replace('  ',' ')
    formulaOut = formulaOut.strip(' ')

    # Clear all spaces
    formulaOut = formulaOut.replace(' ','')

    return formulaOut

########################################

def combineExpressions():

    props = bpy.context.window_manager.bcb
    i = props.prop_menu_selectedElemGrp
    global elemGrps
    asst = elemGrps[i][EGSidxAsst]
    
    ### Reinforced Concrete (Beams & Columns)
    if props.prop_assistant_menu == "con_rei_beam":
        # Switch connection type to the recommended type
        elemGrps[i][EGSidxCTyp] = 16  # 7 x Generic
        # Prepare also a height and width swapped (90° rotated) formula for shear and moment thresholds
        for qHWswapped in range(2):
            if not qHWswapped:
                h = asst['h']
                w = asst['w']
            else:
                w = asst['h']
                h = asst['w']
            if h == 0: h = 'h'
            if w == 0: w = 'w'
            fc = asst['fc']
            fs = asst['fs']
            c = asst['c']
            s = asst['s']
            ds = asst['ds']
            dl = asst['dl']
            n = asst['n']
            k = asst['k']

            d = " (" +asst['Exp:d'] +") "
            e = " (" +asst['Exp:e'] +") "
            rho = " (" +asst['Exp:rho'] +") "
            y = " (" +asst['Exp:y'] +") "
            e1 = " (" +asst['Exp:e1'] +") "
            Nn = " (" +asst['Exp:N-'] +") "
            Np = " (" +asst['Exp:N+'] +") "
            Vpn = " (" +asst['Exp:V+/-'] +") "
            Mpn = " (" +asst['Exp:M+/-'] +") "
            
            ### Normalize result upon 1 mm^2, 'a' should be the only var left over
            a = 'a'
            Nn = "(" +Nn +")/(h*w)*a"
            Np = "(" +Np +")/(h*w)*a"
            Vpn = "(" +Vpn +")/(h*w)*a"
            Mpn = "(" +Mpn +")/(h*w)*a"

            ### Combine all available expressions with each other      
            symbols = ['rho','Vpn','Mpn','pi','fs','fc','ds','dl','e1','Nn','Np','c','s','n','k','h','w','d','e','y','a']  # sorted by length
            cnt = 0; cntLast = -1
            while cnt != cntLast:
                cntLast = cnt
                for symbol in symbols:
                    cnt -= len(d)
                    try:    d   = d.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: d   = d.replace(symbol, eval(symbol))
                    cnt += len(d)
                    cnt -= len(e)
                    try:    e   = e.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e   = e.replace(symbol, eval(symbol))
                    cnt += len(e)
                    cnt -= len(rho)
                    try:    rho = rho.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: rho = rho.replace(symbol, eval(symbol))
                    cnt += len(rho)
                    cnt -= len(y)
                    try:    y   = y.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: y   = y.replace(symbol, eval(symbol))
                    cnt += len(y)
                    cnt -= len(e1)
                    try:    e1  = e1.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e1  = e1.replace(symbol, eval(symbol))
                    cnt += len(e1)
                    cnt -= len(Nn)
                    try:    Nn  = Nn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Nn  = Nn.replace(symbol, eval(symbol))
                    cnt += len(Nn)
                    cnt -= len(Np)
                    try:    Np  = Np.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Np  = Np.replace(symbol, eval(symbol))
                    cnt += len(Np)
                    cnt -= len(Vpn)
                    try:    Vpn = Vpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Vpn = Vpn.replace(symbol, eval(symbol))
                    cnt += len(Vpn)
                    cnt -= len(Mpn)
                    try:    Mpn = Mpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Mpn = Mpn.replace(symbol, eval(symbol))
                    cnt += len(Mpn)
            
            if qSymPy:
                # Simplify formulas when SymPy module is available
                Nn = str(sympy.simplify(Nn))
                Np = str(sympy.simplify(Np))
                Vpn = str(sympy.simplify(Vpn))
                Mpn = str(sympy.simplify(Mpn))

            if not qHWswapped:
                elemGrps[i][EGSidxBTC] = splitAndApplyPrecisionToFormula(Nn)
                elemGrps[i][EGSidxBTT] = splitAndApplyPrecisionToFormula(Np)
                elemGrps[i][EGSidxBTS] = splitAndApplyPrecisionToFormula(Vpn)
                elemGrps[i][EGSidxBTB] = splitAndApplyPrecisionToFormula(Mpn)
            else:
                Vpn9 = splitAndApplyPrecisionToFormula(Vpn)
                Mpn9 = splitAndApplyPrecisionToFormula(Mpn)
                Vpn = elemGrps[i][EGSidxBTS]
                Mpn = elemGrps[i][EGSidxBTB]
                if Vpn9 != Vpn: elemGrps[i][EGSidxBTS9] = splitAndApplyPrecisionToFormula(Vpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                if Mpn9 != Mpn: elemGrps[i][EGSidxBTB9] = splitAndApplyPrecisionToFormula(Mpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
       
    ### Reinforced Concrete (Walls & Slabs)
    elif props.prop_assistant_menu == "con_rei_wall":
        # Switch connection type to the recommended type
        elemGrps[i][EGSidxCTyp] = 16  # 7 x Generic
        # Prepare also a height and width swapped (90° rotated) formula for shear and moment thresholds
        for qHWswapped in range(2):
            if not qHWswapped:
                h = asst['h']
                w = asst['w']
            else:
                w = asst['h']
                h = asst['w']
            if h == 0: h = 'h'
            if w == 0: w = 'w'
            fc = asst['fc']
            fs = asst['fs']
            c = asst['c']
            s = asst['s']
            ds = asst['ds']
            dl = asst['dl']
            n = asst['n']
            k = asst['k']

            d = " (" +asst['Exp:d'] +") "
            e = " (" +asst['Exp:e'] +") "
            rho = " (" +asst['Exp:rho'] +") "
            y = " (" +asst['Exp:y'] +") "
            e1 = " (" +asst['Exp:e1'] +") "
            Nn = " (" +asst['Exp:N-'] +") "
            Np = " (" +asst['Exp:N+'] +") "
            Vpn = " (" +asst['Exp:V+/-'] +") "
            Mpn = " (" +asst['Exp:M+/-'] +") "
            
            ### Normalize result upon 1 mm^2, 'a' should be the only var left over
            a = 'a'
            Nn = "(" +Nn +")/(h*w)*a"
            Np = "(" +Np +")/(h*w)*a"
            Vpn = "(" +Vpn +")/(h*w)*a"
            Mpn = "(" +Mpn +")/(h*w)*a"

            ### Combine all available expressions with each other      
            symbols = ['rho','Vpn','Mpn','pi','fs','fc','ds','dl','e1','Nn','Np','c','s','n','k','h','w','d','e','y','a']  # sorted by length
            cnt = 0; cntLast = -1
            while cnt != cntLast:
                cntLast = cnt
                for symbol in symbols:
                    cnt -= len(d)
                    try:    d   = d.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: d   = d.replace(symbol, eval(symbol))
                    cnt += len(d)
                    cnt -= len(e)
                    try:    e   = e.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e   = e.replace(symbol, eval(symbol))
                    cnt += len(e)
                    cnt -= len(rho)
                    try:    rho = rho.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: rho = rho.replace(symbol, eval(symbol))
                    cnt += len(rho)
                    cnt -= len(y)
                    try:    y   = y.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: y   = y.replace(symbol, eval(symbol))
                    cnt += len(y)
                    cnt -= len(e1)
                    try:    e1  = e1.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: e1  = e1.replace(symbol, eval(symbol))
                    cnt += len(e1)
                    cnt -= len(Nn)
                    try:    Nn  = Nn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Nn  = Nn.replace(symbol, eval(symbol))
                    cnt += len(Nn)
                    cnt -= len(Np)
                    try:    Np  = Np.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Np  = Np.replace(symbol, eval(symbol))
                    cnt += len(Np)
                    cnt -= len(Vpn)
                    try:    Vpn = Vpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Vpn = Vpn.replace(symbol, eval(symbol))
                    cnt += len(Vpn)
                    cnt -= len(Mpn)
                    try:    Mpn = Mpn.replace(symbol, convertFloatToStr(eval(symbol), 4))
                    except: Mpn = Mpn.replace(symbol, eval(symbol))
                    cnt += len(Mpn)
            
            if qSymPy:
                # Simplify formulas when SymPy module is available
                Nn = str(sympy.simplify(Nn))
                Np = str(sympy.simplify(Np))
                Vpn = str(sympy.simplify(Vpn))
                Mpn = str(sympy.simplify(Mpn))

            if not qHWswapped:
                elemGrps[i][EGSidxBTC] = splitAndApplyPrecisionToFormula(Nn)
                elemGrps[i][EGSidxBTT] = splitAndApplyPrecisionToFormula(Np)
                elemGrps[i][EGSidxBTS] = splitAndApplyPrecisionToFormula(Vpn)
                elemGrps[i][EGSidxBTB] = splitAndApplyPrecisionToFormula(Mpn)
            else:
                Vpn9 = splitAndApplyPrecisionToFormula(Vpn)
                Mpn9 = splitAndApplyPrecisionToFormula(Mpn)
                Vpn = elemGrps[i][EGSidxBTS]
                Mpn = elemGrps[i][EGSidxBTB]
                if Vpn9 != Vpn: elemGrps[i][EGSidxBTS9] = splitAndApplyPrecisionToFormula(Vpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                if Mpn9 != Mpn: elemGrps[i][EGSidxBTB9] = splitAndApplyPrecisionToFormula(Mpn9)
                else:           elemGrps[i][EGSidxBTS9] = ""
                
################################################################################
################################################################################

class bcb_asst_con_rei_beam_props(bpy.types.PropertyGroup):
    
    classID = "con_rei_beam"

    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    string_ = bpy.props.StringProperty

    # Find corresponding formula assistant preset
    for formAssist in formulaAssistants:
        if formAssist["ID"] == classID:
            asst = formAssist

    prop_h =  float_(name='h', default=asst['h'], min=0, max=100000, description='Height of element (mm). Leave it 0 to pass it through as variable instead of a fixed number.')
    prop_w =  float_(name='w', default=asst['w'], min=0, max=100000, description='Width of element (mm). Leave it 0 to pass it through as variable instead of a fixed number.')
    prop_fs = float_(name='fs', default=asst['fs'], min=0, max=100000, description='Breaking strength of reinforcement irons (N/mm^2).')
    prop_fc = float_(name='fc', default=asst['fc'], min=0, max=100000, description='Breaking strength of concrete (N/mm^2).')
    prop_c  = float_(name='c', default=asst['c'], min=0, max=100000, description='Concrete cover thickness above reinforcement (mm).')
    prop_s  = float_(name='s', default=asst['s'], min=0, max=100000, description='Distance between stirrups (mm).')
    prop_ds = float_(name='ds', default=asst['ds'], min=0, max=100000, description='Diameter of steel stirrup bar (mm).')
    prop_dl = float_(name='dl', default=asst['dl'], min=0, max=100000, description='Diameter of steel longitudinal bar (mm).')
    prop_n    = int_(name='n', default=asst['n'], min=0, max=100000, description='Number of longitudinal steel bars.')
    prop_k  = float_(name='k', default=asst['k'], min=0, max=100000, description='Scale factor.')

    prop_exp_d   = string_(name='d', default=asst['Exp:d'], description='Distance between the tensile irons and the opposite concrete surface (mm).')
    prop_exp_e   = string_(name='e', default=asst['Exp:e'], description='Distance between longitudinal irons (mm).')
    prop_exp_rho = string_(name='ϱ (rho)', default=asst['Exp:rho'], description='Reinforcement ratio = As/A.')
    prop_exp_y   = string_(name='υ (y)', default=asst['Exp:y'], description='Shear coefficient (asw*10/d) (% value).')
    prop_exp_e1  = string_(name='e´ (e1)', default=asst['Exp:e1'], description='Distance between longitudinal irons in relation to the element height: e/h (% value).')
    prop_exp_Nn  = string_(name='N-', default=asst['Exp:N-'], description='Compressive breaking threshold formula.')
    prop_exp_Np  = string_(name='N+', default=asst['Exp:N+'], description='Tensile breaking threshold formula.')
    prop_exp_Vpn = string_(name='V+/-', default=asst['Exp:V+/-'], description='Shearing breaking threshold formula.')
    prop_exp_Mpn = string_(name='M+/-', default=asst['Exp:M+/-'], description='Bending or momentum breaking threshold formula.')

    ###### Update menu related properties from global vars
    def props_update_menu(self):
        props = bpy.context.window_manager.bcb
        i = props.prop_menu_selectedElemGrp
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        asst = elemGrps[i][EGSidxAsst]
        self.prop_h = asst['h']
        self.prop_w = asst['w']
        self.prop_fs = asst['fs']
        self.prop_fc = asst['fc']
        self.prop_c = asst['c']
        self.prop_s = asst['s']
        self.prop_ds = asst['ds']
        self.prop_dl = asst['dl']
        self.prop_n = asst['n']
        self.prop_k = asst['k']

        self.prop_exp_d = asst['Exp:d']
        self.prop_exp_e = asst['Exp:e']
        self.prop_exp_rho = asst['Exp:rho']
        self.prop_exp_y = asst['Exp:y']
        self.prop_exp_e1 = asst['Exp:e1']
        self.prop_exp_Nn = asst['Exp:N-']
        self.prop_exp_Np = asst['Exp:N+']
        self.prop_exp_Vpn = asst['Exp:V+/-']
        self.prop_exp_Mpn = asst['Exp:M+/-']
        
    ###### Update global vars from menu related properties
    def props_update_globals(self):
        props = bpy.context.window_manager.bcb
        i = props.prop_menu_selectedElemGrp
        global elemGrps
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        elemGrps[i][EGSidxAsst]['h'] = self.prop_h
        elemGrps[i][EGSidxAsst]['w'] = self.prop_w
        elemGrps[i][EGSidxAsst]['fs'] = self.prop_fs
        elemGrps[i][EGSidxAsst]['fc'] = self.prop_fc
        elemGrps[i][EGSidxAsst]['c'] = self.prop_c
        elemGrps[i][EGSidxAsst]['s'] = self.prop_s
        elemGrps[i][EGSidxAsst]['ds'] = self.prop_ds
        elemGrps[i][EGSidxAsst]['dl'] = self.prop_dl
        elemGrps[i][EGSidxAsst]['n'] = self.prop_n
        elemGrps[i][EGSidxAsst]['k'] = self.prop_k

        elemGrps[i][EGSidxAsst]['Exp:d'] = self.prop_exp_d
        elemGrps[i][EGSidxAsst]['Exp:e'] = self.prop_exp_e
        elemGrps[i][EGSidxAsst]['Exp:rho'] = self.prop_exp_rho
        elemGrps[i][EGSidxAsst]['Exp:y'] = self.prop_exp_y
        elemGrps[i][EGSidxAsst]['Exp:e1'] = self.prop_exp_e1
        elemGrps[i][EGSidxAsst]['Exp:N-'] = self.prop_exp_Nn
        elemGrps[i][EGSidxAsst]['Exp:N+'] = self.prop_exp_Np
        elemGrps[i][EGSidxAsst]['Exp:V+/-'] = self.prop_exp_Vpn
        elemGrps[i][EGSidxAsst]['Exp:M+/-'] = self.prop_exp_Mpn
        
########################################

class bcb_asst_con_rei_wall_props(bpy.types.PropertyGroup):

    classID = "con_rei_wall"

    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    string_ = bpy.props.StringProperty

    # Find corresponding formula assistant preset
    for formAssist in formulaAssistants:
        if formAssist["ID"] == classID:
            asst = formAssist

    prop_h =  float_(name='h', default=asst['h'], min=0, max=100000, description='Height of element (mm). Leave it 0 to pass it through as variable instead of a fixed number.')
    prop_w =  float_(name='w', default=asst['w'], min=0, max=100000, description='Width of element (mm). Leave it 0 to pass it through as variable instead of a fixed number.')
    prop_fs = float_(name='fs', default=asst['fs'], min=0, max=100000, description='Breaking strength of reinforcement irons (N/mm^2).')
    prop_fc = float_(name='fc', default=asst['fc'], min=0, max=100000, description='Breaking strength of concrete (N/mm^2).')
    prop_c  = float_(name='c', default=asst['c'], min=0, max=100000, description='Concrete cover thickness above reinforcement (mm).')
    prop_s  = float_(name='s', default=asst['s'], min=0, max=100000, description='Distance between stirrups (mm).')
    prop_ds = float_(name='ds', default=asst['ds'], min=0, max=100000, description='Diameter of steel stirrup bar (mm).')
    prop_dl = float_(name='dl', default=asst['dl'], min=0, max=100000, description='Diameter of steel longitudinal bar (mm).')
    prop_n    = int_(name='n', default=asst['n'], min=0, max=100000, description='Number of longitudinal steel bars.')
    prop_k  = float_(name='k', default=asst['k'], min=0, max=100000, description='Scale factor.')

    prop_exp_d   = string_(name='d', default=asst['Exp:d'], description='Distance between the tensile irons and the opposite concrete surface (mm).')
    prop_exp_e   = string_(name='e', default=asst['Exp:e'], description='Distance between longitudinal irons (mm).')
    prop_exp_rho = string_(name='ϱ (rho)', default=asst['Exp:rho'], description='Reinforcement ratio = As/A.')
    prop_exp_y   = string_(name='υ (y)', default=asst['Exp:y'], description='Shear coefficient (asw*10/d) (% value).')
    prop_exp_e1  = string_(name='e´ (e1)', default=asst['Exp:e1'], description='Distance between longitudinal irons in relation to the element height: e/h (% value).')
    prop_exp_Nn  = string_(name='N-', default=asst['Exp:N-'], description='Compressive breaking threshold formula.')
    prop_exp_Np  = string_(name='N+', default=asst['Exp:N+'], description='Tensile breaking threshold formula.')
    prop_exp_Vpn = string_(name='V+/-', default=asst['Exp:V+/-'], description='Shearing breaking threshold formula.')
    prop_exp_Mpn = string_(name='M+/-', default=asst['Exp:M+/-'], description='Bending or momentum breaking threshold formula.')

    ###### Update menu related properties from global vars
    def props_update_menu(self):
        props = bpy.context.window_manager.bcb
        i = props.prop_menu_selectedElemGrp
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        asst = elemGrps[i][EGSidxAsst]
        self.prop_h = asst['h']
        self.prop_w = asst['w']
        self.prop_fs = asst['fs']
        self.prop_fc = asst['fc']
        self.prop_c = asst['c']
        self.prop_s = asst['s']
        self.prop_ds = asst['ds']
        self.prop_dl = asst['dl']
        self.prop_n = asst['n']
        self.prop_k = asst['k']

        self.prop_exp_d = asst['Exp:d']
        self.prop_exp_e = asst['Exp:e']
        self.prop_exp_rho = asst['Exp:rho']
        self.prop_exp_y = asst['Exp:y']
        self.prop_exp_e1 = asst['Exp:e1']
        self.prop_exp_Nn = asst['Exp:N-']
        self.prop_exp_Np = asst['Exp:N+']
        self.prop_exp_Vpn = asst['Exp:V+/-']
        self.prop_exp_Mpn = asst['Exp:M+/-']
        
    ###### Update global vars from menu related properties
    def props_update_globals(self):
        props = bpy.context.window_manager.bcb
        i = props.prop_menu_selectedElemGrp
        global elemGrps
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        elemGrps[i][EGSidxAsst]['h'] = self.prop_h
        elemGrps[i][EGSidxAsst]['w'] = self.prop_w
        elemGrps[i][EGSidxAsst]['fs'] = self.prop_fs
        elemGrps[i][EGSidxAsst]['fc'] = self.prop_fc
        elemGrps[i][EGSidxAsst]['c'] = self.prop_c
        elemGrps[i][EGSidxAsst]['s'] = self.prop_s
        elemGrps[i][EGSidxAsst]['ds'] = self.prop_ds
        elemGrps[i][EGSidxAsst]['dl'] = self.prop_dl
        elemGrps[i][EGSidxAsst]['n'] = self.prop_n
        elemGrps[i][EGSidxAsst]['k'] = self.prop_k

        elemGrps[i][EGSidxAsst]['Exp:d'] = self.prop_exp_d
        elemGrps[i][EGSidxAsst]['Exp:e'] = self.prop_exp_e
        elemGrps[i][EGSidxAsst]['Exp:rho'] = self.prop_exp_rho
        elemGrps[i][EGSidxAsst]['Exp:y'] = self.prop_exp_y
        elemGrps[i][EGSidxAsst]['Exp:e1'] = self.prop_exp_e1
        elemGrps[i][EGSidxAsst]['Exp:N-'] = self.prop_exp_Nn
        elemGrps[i][EGSidxAsst]['Exp:N+'] = self.prop_exp_Np
        elemGrps[i][EGSidxAsst]['Exp:V+/-'] = self.prop_exp_Vpn
        elemGrps[i][EGSidxAsst]['Exp:M+/-'] = self.prop_exp_Mpn

########################################

class bcb_props(bpy.types.PropertyGroup):
    
    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    bool_ = bpy.props.BoolProperty
    string_ = bpy.props.StringProperty
    enum_ = bpy.props.EnumProperty
    
    ###### Create menu related properties from global vars
    prop_menu_gotConfig = int_(0)
    prop_menu_gotData = int_(0)
    prop_menu_selectedElemGrp = int_(0)
    prop_submenu_advancedG = bool_(0)
    prop_submenu_advancedE = bool_(0)
    prop_submenu_assistant = bool_(0)
    prop_submenu_assistant_advanced = bool_(0, name="Advanced", description="Shows advanced settings and formulas.")

    assistant_menu = []  # (ID, Name in menu, "", Index)
    for i in range(len(formulaAssistants)):
        assistant_menu.append((formulaAssistants[i]["ID"], formulaAssistants[i]["Name"], "", i))
    #prop_assistant_menu = enum_(items=assistant_menu, name="Type of Building Material")
    
    prop_stepsPerSecond = int_(name="Steps Per Second", default=stepsPerSecond, min=1, max=32767, description="Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable).")
    prop_constraintUseBreaking = bool_(name="Enable Breaking", default=constraintUseBreaking, description="Enables breaking for all constraints.")
    prop_connectionCountLimit = int_(name="Con. Count Limit", default=connectionCountLimit, min=0, max=10000, description="Maximum count of connections per object pair (0 = disabled).")
    prop_searchDistance = float_(name="Search Distance", default=searchDistance, min=0.0, max=1000, description="Search distance to neighbor geometry.")
    prop_clusterRadius = float_(name="Cluster Radius", default=clusterRadius, min=0.0, max=1000, description="Radius for bundling close constraints into clusters (0 = clusters disabled).")
    prop_alignVertical = float_(name="Vertical Alignment", default=alignVertical, min=0.0, max=1.0, description="Enables a vertical alignment multiplier for connection type 4 or above instead of using unweighted center to center orientation (0 = disabled, 1 = fully vertical).")
    prop_useAccurateArea = bool_(name="Accur. Contact Area Calculation", default=useAccurateArea , description="Enables accurate contact area calculation using booleans for the cost of an slower building process. This only works correct with solids i.e. watertight and manifold objects and is therefore recommended for truss structures or steel constructions in general.")
    prop_nonManifoldThickness = float_(name="Non-solid Thickness", default=nonManifoldThickness, min=0.0, max=10, description="Thickness for non-manifold elements (surfaces) when using accurate contact area calculation.")
    prop_minimumElementSize = float_(name="Min. Element Size", default=minimumElementSize, min=0.0, max=10, description="Deletes connections whose elements are below this diameter and makes them parents instead. This can be helpful for increasing performance on models with unrelevant geometric detail such as screwheads.")
    prop_automaticMode = bool_(name="Automatic Mode", default=automaticMode, description="Enables a fully automated workflow for extremely large simulations (object count-wise) were Blender is prone to not being responsive anymore. After clicking Build these steps are being done automatically: Building of constraints, baking simulation, clearing constraint and BCB data from scene.")
    prop_saveBackups = bool_(name="Backup", default=saveBackups, description="Enables saving of a backup .blend file after each step for automatic mode, whereby the name of the new .blend ends with `_BCB´.")
    prop_timeScalePeriod = int_(name="Time Scale Period", default=timeScalePeriod, min=0, max=10000, description="For baking: Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled).")
    prop_timeScalePeriodValue = float_(name="Initial Time Scale", default=timeScalePeriodValue, min=0.0, max=100, description="For baking: Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime.")
    prop_warmUpPeriod = int_(name="Warm Up Period", default=warmUpPeriod, min=0, max=10000, description="For baking: Disables breakability of constraints for an initial period of the simulation (frames). This is to prevent structural damage caused by the gravity impulse on start.")
    prop_progrWeak = float_(name="Progr. Weakening", default=progrWeak, min=0.0, max=1.0, description="Enables progressive weakening of all breaking thresholds by the specified factor per frame (starts not until timeScalePeriod and warmUpPeriod have passed). This can be used to enforce the certain collapse of a building structure after a while.")
    prop_progrWeakLimit = int_(name="Progr. Weak. Limit", default=progrWeakLimit, min=0, max=10000, description="For progressive weakening: Limits the weakening process by the number of broken connections per frame. If the limit is exceeded weakening will be disabled for the rest of the simulation.")
    prop_progrWeakStartFact = float_(name="Start Weakness", default=progrWeakStartFact, min=0.0, max=1.0, description="Start weakness as factor all breaking thresholds will be multiplied with. This can be used to quick-change the initial thresholds without performing a full update.")
    prop_snapToAreaOrient = bool_(name="90° Axis Snapping for Const. Orient.", default=snapToAreaOrient, description="Enables axis snapping based on contact area orientation for constraints rotation instead of using center to center vector alignment (old method).")
    prop_disableCollision = bool_(name="Disable Collisions", default=disableCollision, description="Disables collisions between connected elements until breach.")
    
    for i in range(maxMenuElementGroupItems):
        if i < len(elemGrps): j = i
        else: j = 0
        exec("prop_elemGrp_%d_EGSidxName" %i +" = string_(name='Grp. Name', default=elemGrps[j][EGSidxName], description='The name of the element group.')")
        exec("prop_elemGrp_%d_EGSidxCTyp" %i +" = int_(name='Connection Type', default=elemGrps[j][EGSidxCTyp], min=1, max=1000, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code.')")

        exec("prop_elemGrp_%d_EGSidxBTC" %i +" = string_(name='Compressive', default=elemGrps[j][EGSidxBTC], description='Math expression for the material´s real world compressive breaking threshold in N/mm^2 together with related geometry properties. (Example: `30*a´)')")
        exec("prop_elemGrp_%d_EGSidxBTT" %i +" = string_(name='Tensile', default=elemGrps[j][EGSidxBTT], description='Math expression for the material´s real world tensile breaking threshold in N/mm^2 together with related geometry properties. (Example: `30*a´)')")
        exec("prop_elemGrp_%d_EGSidxBTS" %i +" = string_(name='Shear', default=elemGrps[j][EGSidxBTS], description='Math expression for the material´s real world shearing breaking threshold in N/mm^2 together with related geometry properties. (Example: `30*a´)')")
        exec("prop_elemGrp_%d_EGSidxBTS9" %i +" = string_(name='Shear 90°', default=elemGrps[j][EGSidxBTS9], description='Math expression for the material´s real world shearing breaking threshold with h and w swapped (rotated by 90°) in N/mm^2 together with related geometry properties. (Example: `30*a´)')")
        exec("prop_elemGrp_%d_EGSidxBTB" %i +" = string_(name='Bend', default=elemGrps[j][EGSidxBTB], description='Math expression for the material´s real world bending breaking threshold in N/mm^2 together with related geometry properties. (Example: `30*a´)')")
        exec("prop_elemGrp_%d_EGSidxBTB9" %i +" = string_(name='Bend 90°', default=elemGrps[j][EGSidxBTB9], description='Math expression for the material´s real world bending breaking threshold with h and w swapped (rotated by 90°) in N/mm^2 together with related geometry properties. (Example: `30*a´)')")

        exec("prop_elemGrp_%d_EGSidxSStf" %i +" = float_(name='Spring Stiffness', default=elemGrps[j][EGSidxSStf], min=0.0, max=10**20, description='Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.')")
        exec("prop_elemGrp_%d_EGSidxRqVP" %i +" = int_(name='Req. Vertex Pairs', default=elemGrps[j][EGSidxRqVP], min=0, max=100, description='How many vertex pairs between two elements are required to generate a connection.')")
        exec("prop_elemGrp_%d_EGSidxMatP" %i +" = string_(name='Mat. Preset', default=elemGrps[j][EGSidxMatP], description='Preset name of the physical material to be used from BlenderJs internal database. See Blenders Rigid Body Tools for a list of available presets.')")
        exec("prop_elemGrp_%d_EGSidxDens" %i +" = float_(name='Density', default=elemGrps[j][EGSidxDens], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("prop_elemGrp_%d_EGSidxTl1D" %i +" = float_(name='1st Dist. Tol.', default=elemGrps[j][EGSidxTl1D], min=0.0, max=10.0, description='For baking: First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %).')")
        exec("prop_elemGrp_%d_EGSidxTl1R" %i +" = float_(name='1st Rot. Tol.', default=elemGrps[j][EGSidxTl1R], min=0.0, max=pi, description='For baking: First deformation tolerance limit for angular change in radian for connection removal or plastic deformation.')")
        exec("prop_elemGrp_%d_EGSidxTl2D" %i +" = float_(name='2nd Dist. Tol.', default=elemGrps[j][EGSidxTl2D], min=0.0, max=10.0, description='For baking: Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %).')")
        exec("prop_elemGrp_%d_EGSidxTl2R" %i +" = float_(name='2nd Rot. Tol.', default=elemGrps[j][EGSidxTl2R], min=0.0, max=pi, description='For baking: Second deformation tolerance limit for angular change in radian for connection removal.')")
        exec("prop_elemGrp_%d_EGSidxBevl" %i +" = bool_(name='Bevel', default=elemGrps[j][EGSidxBevl], description='Enables beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_EGSidxScal" %i +" = float_(name='Rescale Factor', default=elemGrps[j][EGSidxScal], min=0.0, max=1, description='Applies scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_EGSidxFacg" %i +" = bool_(name='Facing', default=elemGrps[j][EGSidxFacg], description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation).')")
        exec("prop_elemGrp_%d_EGSidxCyln" %i +" = bool_(name='Cylindric Shape', default=elemGrps[j][EGSidxCyln], description='Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns.')")

        # Update fromula assistant submenu according to the chosen element group
        exec("prop_assistant_menu = enum_(name='Type of Building Material', items=assistant_menu, default=elemGrps[j][EGSidxAsst]['ID'])")

    ###### Update menu related properties from global vars
    def props_update_menu(self):

        ### Update main class properties
        for i in range(len(elemGrps)):
            exec("self.prop_elemGrp_%d_EGSidxName" %i +" = elemGrps[i][EGSidxName]")
            exec("self.prop_elemGrp_%d_EGSidxRqVP" %i +" = elemGrps[i][EGSidxRqVP]")
            exec("self.prop_elemGrp_%d_EGSidxMatP" %i +" = elemGrps[i][EGSidxMatP]")
            exec("self.prop_elemGrp_%d_EGSidxDens" %i +" = elemGrps[i][EGSidxDens]")
            exec("self.prop_elemGrp_%d_EGSidxCTyp" %i +" = elemGrps[i][EGSidxCTyp]")
            exec("self.prop_elemGrp_%d_EGSidxBTC" %i +" = elemGrps[i][EGSidxBTC]")
            exec("self.prop_elemGrp_%d_EGSidxBTT" %i +" = elemGrps[i][EGSidxBTT]")
            exec("self.prop_elemGrp_%d_EGSidxBTS" %i +" = elemGrps[i][EGSidxBTS]")
            exec("self.prop_elemGrp_%d_EGSidxBTS9" %i +" = elemGrps[i][EGSidxBTS9]")
            exec("self.prop_elemGrp_%d_EGSidxBTB" %i +" = elemGrps[i][EGSidxBTB]")
            exec("self.prop_elemGrp_%d_EGSidxBTB9" %i +" = elemGrps[i][EGSidxBTB9]")
            exec("self.prop_elemGrp_%d_EGSidxSStf" %i +" = elemGrps[i][EGSidxSStf]")
            exec("self.prop_elemGrp_%d_EGSidxTl1D" %i +" = elemGrps[i][EGSidxTl1D]")
            exec("self.prop_elemGrp_%d_EGSidxTl1R" %i +" = elemGrps[i][EGSidxTl1R]")
            exec("self.prop_elemGrp_%d_EGSidxTl2D" %i +" = elemGrps[i][EGSidxTl2D]")
            exec("self.prop_elemGrp_%d_EGSidxTl2R" %i +" = elemGrps[i][EGSidxTl2R]")
            exec("self.prop_elemGrp_%d_EGSidxBevl" %i +" = elemGrps[i][EGSidxBevl]")
            exec("self.prop_elemGrp_%d_EGSidxScal" %i +" = elemGrps[i][EGSidxScal]")
            exec("self.prop_elemGrp_%d_EGSidxFacg" %i +" = elemGrps[i][EGSidxFacg]")
            exec("self.prop_elemGrp_%d_EGSidxCyln" %i +" = elemGrps[i][EGSidxCyln]")
        
        # Update fromula assistant submenu according to the chosen element group
        i = self.prop_menu_selectedElemGrp
        try: self.prop_assistant_menu = elemGrps[i][EGSidxAsst]['ID']
        except: self.prop_assistant_menu = "None"
        
        ### Update also the other classes properties
        props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
        props_asst_con_rei_beam.props_update_menu()
        props_asst_con_rei_wall.props_update_menu()
            
    ###### Update global vars from menu related properties
    def props_update_globals(self):
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
        global timeScalePeriod; timeScalePeriod = self.prop_timeScalePeriod
        global timeScalePeriodValue; timeScalePeriodValue = self.prop_timeScalePeriodValue
        global warmUpPeriod; warmUpPeriod = self.prop_warmUpPeriod
        global progrWeak; progrWeak = self.prop_progrWeak
        global progrWeakLimit; progrWeakLimit = self.prop_progrWeakLimit
        global progrWeakStartFact; progrWeakStartFact = self.prop_progrWeakStartFact
        global snapToAreaOrient; snapToAreaOrient = self.prop_snapToAreaOrient
        global disableCollision; disableCollision = self.prop_disableCollision

        global elemGrps
        for i in range(len(elemGrps)):
            elemGrps[i][EGSidxName] = eval("self.prop_elemGrp_%d_EGSidxName" %i)
            elemGrps[i][EGSidxRqVP] = eval("self.prop_elemGrp_%d_EGSidxRqVP" %i)
            elemGrps[i][EGSidxMatP] = eval("self.prop_elemGrp_%d_EGSidxMatP" %i)
            elemGrps[i][EGSidxDens] = eval("self.prop_elemGrp_%d_EGSidxDens" %i)
            elemGrps[i][EGSidxCTyp] = eval("self.prop_elemGrp_%d_EGSidxCTyp" %i)
            elemGrps[i][EGSidxBTC] = eval("self.prop_elemGrp_%d_EGSidxBTC" %i)
            elemGrps[i][EGSidxBTT] = eval("self.prop_elemGrp_%d_EGSidxBTT" %i)
            elemGrps[i][EGSidxBTS] = eval("self.prop_elemGrp_%d_EGSidxBTS" %i)
            elemGrps[i][EGSidxBTS9] = eval("self.prop_elemGrp_%d_EGSidxBTS9" %i)
            elemGrps[i][EGSidxBTB] = eval("self.prop_elemGrp_%d_EGSidxBTB" %i)
            elemGrps[i][EGSidxBTB9] = eval("self.prop_elemGrp_%d_EGSidxBTB9" %i)
            elemGrps[i][EGSidxSStf] = eval("self.prop_elemGrp_%d_EGSidxSStf" %i)
            elemGrps[i][EGSidxTl1D] = eval("self.prop_elemGrp_%d_EGSidxTl1D" %i)
            elemGrps[i][EGSidxTl1R] = eval("self.prop_elemGrp_%d_EGSidxTl1R" %i)
            elemGrps[i][EGSidxTl2D] = eval("self.prop_elemGrp_%d_EGSidxTl2D" %i)
            elemGrps[i][EGSidxTl2R] = eval("self.prop_elemGrp_%d_EGSidxTl2R" %i)
            elemGrps[i][EGSidxBevl] = eval("self.prop_elemGrp_%d_EGSidxBevl" %i)
            elemGrps[i][EGSidxScal] = eval("self.prop_elemGrp_%d_EGSidxScal" %i)
            elemGrps[i][EGSidxFacg] = eval("self.prop_elemGrp_%d_EGSidxFacg" %i)
            elemGrps[i][EGSidxCyln] = eval("self.prop_elemGrp_%d_EGSidxCyln" %i)

        ### If different formula assistant ID from that stored in element group then update with defaults
        i = self.prop_menu_selectedElemGrp
        if self.prop_assistant_menu != elemGrps[i][EGSidxAsst]['ID']:
            # Add formula assistant settings to element group
            for formAssist in formulaAssistants:
                if self.prop_assistant_menu == formAssist['ID']:
                    elemGrps[i][EGSidxAsst] = formAssist.copy()

        ### Update global vars also from the other classes properties
        props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
        props_asst_con_rei_beam.props_update_globals()
        props_asst_con_rei_wall.props_update_globals()        

################################################################################   
           
class bcb_panel(bpy.types.Panel):
    ver = bl_info["version"]
    bl_label = "Bullet Constraints Builder v%d.%d%d" %(ver[0], ver[1], ver[2]) 
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" 

    def icon(self, bool):
        if bool: return 'TRIA_DOWN'
        else: return 'TRIA_RIGHT'

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.bcb
        props_asst_con_rei_beam = context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = context.window_manager.bcb_asst_con_rei_wall
        obj = context.object
        scene = bpy.context.scene
        #print(props_asst_con_rei_beam.prop_h, '\n', elemGrps[props.prop_menu_selectedElemGrp][EGSidxAsst])

        row = layout.row()
        if not props.prop_menu_gotData: 
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.build", icon="MOD_SKIN")
            split2 = split.split(align=False)
            if not props.prop_menu_gotConfig:
                if not "bcb_prop_elemGrps" in scene.keys(): split2.enabled = 0
                split2.operator("bcb.get_config", icon="FILE_REFRESH")
            else: split2.operator("bcb.clear", icon="CANCEL")

            row = layout.row()
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=False)
            split2.operator("bcb.set_config", icon="NEW")
        else:
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split2 = split.split(align=False)
            split2.operator("bcb.clear", icon="CANCEL")

            row = layout.row()
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=False)
            split2.operator("bcb.set_config", icon="NEW")

        layout.separator()
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
        box.prop(props, "prop_submenu_advancedG", text="Advanced Global Settings", icon=self.icon(props.prop_submenu_advancedG), emboss = False)

        if props.prop_submenu_advancedG:
            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.operator("bcb.export_ascii", icon="EXPORT")
            split.operator("bcb.export_ascii_fm", icon="EXPORT")
            box.separator()

            row = box.row(); row.prop(props, "prop_stepsPerSecond")

            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "prop_constraintUseBreaking")
            split.prop(props, "prop_disableCollision")
       
            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "prop_automaticMode")
            split.prop(props, "prop_saveBackups")
            box.separator()

            row = box.row(); row.prop(props, "prop_snapToAreaOrient")
            row = box.row()
            if props.prop_snapToAreaOrient: row.enabled = 0
            row.prop(props, "prop_alignVertical")
            box.separator()

            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_useAccurateArea")
#            row = box.row()
#            if not props.prop_useAccurateArea: row.enabled = 0
#            row.prop(props, "prop_nonManifoldThickness")
            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_connectionCountLimit")
            row = box.row()
            if props.prop_menu_gotData: row.enabled = 0
            row.prop(props, "prop_minimumElementSize")

            row = box.row(); row.prop(props, "prop_warmUpPeriod")
            box.separator()
            row = box.row(); row.prop(props, "prop_timeScalePeriod")
            row = box.row(); row.prop(props, "prop_timeScalePeriodValue")
            if props.prop_timeScalePeriod == 0: row.enabled = 0
            box.separator()

            row = box.row(); row.prop(props, "prop_progrWeak")
            row = box.row(); row.prop(props, "prop_progrWeakLimit")
            if props.prop_progrWeak == 0: row.enabled = 0
            row = box.row(); row.prop(props, "prop_progrWeakStartFact")
            
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
            if i == props.prop_menu_selectedElemGrp:
                  row = box.box().row()
            else: row = box.row()
            prop_EGSidxName = eval("props.prop_elemGrp_%d_EGSidxName" %i)
            prop_EGSidxCTyp = ct = eval("props.prop_elemGrp_%d_EGSidxCTyp" %i)
            try: connectType = connectTypes[ct]
            except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
            if not connectType[2][0]: prop_EGSidxBTC = "-"
            else: prop_EGSidxBTC = eval("props.prop_elemGrp_%d_EGSidxBTC" %i)
            if not connectType[2][1]: prop_EGSidxBTT = "-"
            else: prop_EGSidxBTT = eval("props.prop_elemGrp_%d_EGSidxBTT" %i)
            if not connectType[2][2]: prop_EGSidxBTS = "-"
            else: prop_EGSidxBTS = eval("props.prop_elemGrp_%d_EGSidxBTS" %i)
            if not connectType[2][3]: prop_EGSidxBTB = "-"
            else: prop_EGSidxBTB = eval("props.prop_elemGrp_%d_EGSidxBTB" %i)
            split = row.split(percentage=.25, align=False)
            if prop_EGSidxName == "": split.label(text="[Def.]")
            else:                     split.label(text=str(prop_EGSidxName))
            split2 = split.split(align=False)
            split2.label(text=str(prop_EGSidxCTyp))
            split2.label(text=str(prop_EGSidxBTC))
            split2.label(text=str(prop_EGSidxBTT))
            split2.label(text=str(prop_EGSidxBTS))
            split2.label(text=str(prop_EGSidxBTB))
        row = box.row()
        row.operator("bcb.up", icon="TRIA_UP")
        row.operator("bcb.down", icon="TRIA_DOWN")
        
        ###### Element group settings
        
        layout.separator()
        i = props.prop_menu_selectedElemGrp
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxName" %i)

        ###### Formula assistant box

        box = layout.box()
        box.prop(props, "prop_submenu_assistant", text="Formula Assistant", icon=self.icon(props.prop_submenu_assistant), emboss = False)

        if props.prop_submenu_assistant:
            # Pull-down selector
            row = box.row(); row.prop(props, "prop_assistant_menu")

            ### Reinforced Concrete (Beams & Columns)
            if props.prop_assistant_menu == "con_rei_beam":
                box.label(text="Strengths of Base Material and Reinforcement:")
                row = box.split(); row.prop(props_asst_con_rei_beam, "prop_fc")
                row.prop(props_asst_con_rei_beam, "prop_fs")
                box.label(text="Geometry Parameters and Coefficients:")
                row = box.split(); row.prop(props_asst_con_rei_beam, "prop_h")
                row.prop(props_asst_con_rei_beam, "prop_w")
                row = box.split(); row.prop(props_asst_con_rei_beam, "prop_c")
                row.prop(props_asst_con_rei_beam, "prop_s")
                row = box.split(); row.prop(props_asst_con_rei_beam, "prop_ds")
                row.prop(props_asst_con_rei_beam, "prop_dl")
                row = box.split(); row.prop(props_asst_con_rei_beam, "prop_n")
                if props.prop_submenu_assistant_advanced:
                    row.prop(props_asst_con_rei_beam, "prop_k")
                else: row.label(text="")
                box.label(text="Automatic & Manual Input is Allowed Here:")
                row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_d")
                row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_e")
                row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_rho")
                row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_y")
                row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_e1")
                if props.prop_submenu_assistant_advanced:
                    box.label(text="Breaking Threshold Formulas:")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_Nn")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_Np")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_Vpn")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "prop_exp_Mpn")
                
            ### Reinforced Concrete (Walls & Slabs)
            if props.prop_assistant_menu == "con_rei_wall":
                box.label(text="Strengths of Base Material and Reinforcement:")
                row = box.split(); row.prop(props_asst_con_rei_wall, "prop_fc")
                row.prop(props_asst_con_rei_wall, "prop_fs")
                box.label(text="Geometry Parameters and Coefficients:")
                row = box.split(); row.prop(props_asst_con_rei_wall, "prop_h")
                row.prop(props_asst_con_rei_wall, "prop_w")
                row = box.split(); row.prop(props_asst_con_rei_wall, "prop_c")
                row.prop(props_asst_con_rei_wall, "prop_s")
                row = box.split(); row.prop(props_asst_con_rei_wall, "prop_ds")
                row.prop(props_asst_con_rei_wall, "prop_dl")
                row = box.split(); row.prop(props_asst_con_rei_wall, "prop_n")
                if props.prop_submenu_assistant_advanced:
                    row.prop(props_asst_con_rei_wall, "prop_k")
                else: row.label(text="")
                box.label(text="Automatic & Manual Input is Allowed Here:")
                row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_d")
                row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_e")
                row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_rho")
                row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_y")
                row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_e1")
                if props.prop_submenu_assistant_advanced:
                    box.label(text="Breaking Threshold Formulas:")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_Nn")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_Np")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_Vpn")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "prop_exp_Mpn")
                
            if props.prop_assistant_menu != "None":
                split = box.split(percentage=.85, align=False)
                split.operator("bcb.asst_update", icon="PASTEDOWN")
                split2 = split.split(align=False)
                split2.prop(props, "prop_submenu_assistant_advanced")
                
        layout.separator()

        ###### Element group settings (more)        

        row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxCTyp" %i)
        if props.prop_menu_gotData: row.enabled = 0
            
        ct = eval("props.prop_elemGrp_%d_EGSidxCTyp" %i)
        try: connectType = connectTypes[ct]
        except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
        box = layout.box();
        box.label(text=connectType[0])

        row = layout.row(); row.label(text="Breaking Thresholds in [N or Nm] *a (mm²):")

        # Prepare possible expression variables
        a = h = w = b = s = 1   

        expression = eval("props.prop_elemGrp_%d_EGSidxBTC" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxBTC" %i)
        if not connectType[2][0]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.prop_elemGrp_%d_EGSidxBTT" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxBTT" %i)
        if not connectType[2][1]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.prop_elemGrp_%d_EGSidxBTS" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxBTS" %i)
        if not connectType[2][2]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        if props.prop_submenu_assistant_advanced:
            expression = eval("props.prop_elemGrp_%d_EGSidxBTS9" %i)
            if expression != "":
                row = layout.row()
                try: value = eval(expression)
                except: row.alert = 1; qAlert = 1
                else: qAlert = 0
                row.prop(props, "prop_elemGrp_%d_EGSidxBTS9" %i)
                if not connectType[2][2]: row.active = 0
                if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.prop_elemGrp_%d_EGSidxBTB" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxBTB" %i)
        if not connectType[2][3]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        if props.prop_submenu_assistant_advanced:
            expression = eval("props.prop_elemGrp_%d_EGSidxBTB9" %i)
            if expression != "":
                row = layout.row()
                try: value = eval(expression)
                except: row.alert = 1; qAlert = 1
                else: qAlert = 0
                row.prop(props, "prop_elemGrp_%d_EGSidxBTB9" %i)
                if not connectType[2][3]: row.active = 0
                if qAlert: row = layout.row(); row.label(text="Error in expression")

        layout.separator()
        #row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxRqVP" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxMatP" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxDens" %i)
        
        layout.separator()
        row = layout.row()
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxScal" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_EGSidxCyln" %i)
        row = layout.row()
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxBevl" %i)
        prop_EGSidxBevl = eval("props.prop_elemGrp_%d_EGSidxBevl" %i)
        prop_EGSidxFacg = eval("props.prop_elemGrp_%d_EGSidxFacg" %i)
        if prop_EGSidxBevl and not prop_EGSidxFacg: row.alert = 1
        if props.prop_menu_gotData: row.enabled = 0
        row.prop(props, "prop_elemGrp_%d_EGSidxFacg" %i)
        
        if prop_EGSidxBevl and not prop_EGSidxFacg:
            row = layout.row(); row.label(text="Warning: Disabled facing")
            row = layout.row(); row.label(text="makes bevel permanent!")
            
        ###### Advanced element group settings box
        
        box = layout.box()
        box.prop(props, "prop_submenu_advancedE", text="Advanced Element Settings", icon=self.icon(props.prop_submenu_advancedE), emboss = False)

        if props.prop_submenu_advancedE:
            row = box.row(); row.prop(props, "prop_elemGrp_%d_EGSidxSStf" %i)
            if not connectType[2][4]: row.active = 0
            row = box.row(); row.label(text="1st & 2nd Tolerance (Plastic & Breaking):")
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "prop_elemGrp_%d_EGSidxTl1D" %i)
            split.prop(props, "prop_elemGrp_%d_EGSidxTl1R" %i)
            if not connectType[2][5]: split.active = 0
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "prop_elemGrp_%d_EGSidxTl2D" %i)
            split.prop(props, "prop_elemGrp_%d_EGSidxTl2R" %i)
            if not connectType[2][7]: split.active = 0
            
        ### Update global vars from menu related properties
        props.props_update_globals()
        
################################################################################   
         
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

########################################

class OBJECT_OT_bcb_get_config(bpy.types.Operator):
    bl_idname = "bcb.get_config"
    bl_label = ""
    bl_description = "Loads previous config data from current scene."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        if "bcb_prop_elemGrps" in scene.keys():
            ###### Get menu config data from scene
            warning = getConfigDataFromScene(scene)
            if warning != None and len(warning): self.report({'ERROR'}, warning)
            props.prop_menu_gotConfig = 1
            ###### Get build data from scene
            #getBuildDataFromScene(scene)
            if "bcb_objs" in scene.keys(): props.prop_menu_gotData = 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_clear(bpy.types.Operator):
    bl_idname = "bcb.clear"
    bl_label = ""
    bl_description = "Clears constraints from scene and revert back to original state (required to rebuild constraints from scratch)."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Clear all data from scene and delete also constraint empty objects
        if "bcb_prop_elemGrps" in scene.keys(): clearAllDataFromScene(scene)
        props.prop_menu_gotConfig = 0
        props.prop_menu_gotData = 0
        return{'FINISHED'} 
        
########################################

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
        return{'FINISHED'} 

########################################

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
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_export_ascii(bpy.types.Operator):
    bl_idname = "bcb.export_ascii"
    bl_label = "Export to Text"
    bl_description = "Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment)."
    def execute(self, context):
        global asciiExport
        asciiExport = 1
        ###### Execute main building process from scratch
        build()
        asciiExport = 0
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_export_ascii_fm(bpy.types.Operator):
    bl_idname = "bcb.export_ascii_fm"
    bl_label = "Export to FM"
    bl_description = "Exports all constraint data to the Fracture Modifier (special Blender version required). WARNING: This feature is experimental and results of the FM can vary, use with care!"
    def execute(self, context):
        scene = bpy.context.scene
        global asciiExport
        asciiExport = 1
        ###### Execute main building process from scratch
        build()
        asciiExport = 0
        build_fm()
        bpy.data.texts.remove(bpy.data.texts["BCB_export.txt"])
        ### Free previous bake data
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.free_bake(contextFix)
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_bake(bpy.types.Operator):
    bl_idname = "bcb.bake"
    bl_label = "Bake"
    bl_description = "Bakes simulation. Use of this button is crucial if connection type 4 or above is used, because then constraints require monitoring on per frame basis during simulation."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ### Only start baking when we have constraints set
        if props.prop_menu_gotData:
            print('\nInit BCB monitor event handler.')
            # Free old monitor data if still in memory (can happen if user stops baking before finished)
            monitor_freeBuffers(scene)
            # Prepare event handler
            bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
            ### Free previous bake data
            contextFix = bpy.context.copy()
            contextFix['point_cache'] = scene.rigidbody_world.point_cache
            bpy.ops.ptcache.free_bake(contextFix)
            ### Invalidate point cache to enforce a full bake without using previous cache data
            if "RigidBodyWorld" in bpy.data.groups:
                obj = bpy.data.groups["RigidBodyWorld"].objects[0]
                obj.location = obj.location
            # Invoke baking (old method, appears not to work together with the event handler past Blender v2.76 anymore)
            #bpy.ops.ptcache.bake(contextFix, bake=True)
            # Start animation playback and by that the baking process
            if not bpy.context.screen.is_animation_playing:
                bpy.ops.screen.animation_play()
        ### Otherwise build constraints if required
        else:
            OBJECT_OT_bcb_build.execute(self, context)
            OBJECT_OT_bcb_bake.execute(self, context)
        return{'FINISHED'} 

########################################

def automaticModeAfterStop():
    if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('.blend')[0] +'_BCB.blend')
    OBJECT_OT_bcb_clear.execute(None, bpy.context)
    if saveBackups: bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath.split('_BCB.blend')[0].split('_BCB-bake.blend')[0].split('.blend')[0] +'_BCB-bake.blend')
        
########################################

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = ""
    bl_description = "Adds element group to list."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        if len(elemGrps) < maxMenuElementGroupItems:
            # Add element group (syncing element group indices happens on execution)
            elemGrps.append(elemGrps[props.prop_menu_selectedElemGrp].copy())
            # Update menu selection
            props.prop_menu_selectedElemGrp = len(elemGrps) -1
        else: self.report({'ERROR'}, "Maximum allowed element group count reached.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

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
            elemGrps.remove(elemGrps[props.prop_menu_selectedElemGrp])
            # Update menu selection
            if props.prop_menu_selectedElemGrp >= len(elemGrps):
                props.prop_menu_selectedElemGrp = len(elemGrps) -1
        else: self.report({'ERROR'}, "At least one element group is required.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_move_up(bpy.types.Operator):
    bl_idname = "bcb.move_up"
    bl_label = ""
    bl_description = "Moves element group in list."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        if props.prop_menu_selectedElemGrp > 0:
            swapItem = props.prop_menu_selectedElemGrp -1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.prop_menu_selectedElemGrp] = elemGrps[props.prop_menu_selectedElemGrp], elemGrps[swapItem]
            # Also move menu selection
            props.prop_menu_selectedElemGrp -= 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_move_down(bpy.types.Operator):
    bl_idname = "bcb.move_down"
    bl_label = ""
    bl_description = "Moves element group in list."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        scene = bpy.context.scene
        if props.prop_menu_selectedElemGrp < len(elemGrps) -1:
            swapItem = props.prop_menu_selectedElemGrp +1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.prop_menu_selectedElemGrp] = elemGrps[props.prop_menu_selectedElemGrp], elemGrps[swapItem]
            # Also move menu selection
            props.prop_menu_selectedElemGrp += 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_up(bpy.types.Operator):
    bl_idname = "bcb.up"
    bl_label = " Previous"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedElemGrp > 0:
            props.prop_menu_selectedElemGrp -= 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_down(bpy.types.Operator):
    bl_idname = "bcb.down"
    bl_label = " Next"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedElemGrp < len(elemGrps) -1:
            props.prop_menu_selectedElemGrp += 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

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
        props.prop_menu_selectedElemGrp = 0
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

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

########################################

class OBJECT_OT_bcb_asst_update(bpy.types.Operator):
    bl_idname = "bcb.asst_update"
    bl_label = "Evaluate"
    bl_description = "Combines and evaluates all expressions for constraint breaking threshold calculation."
    def execute(self, context):
        props = context.window_manager.bcb
        ###### Execute expression evaluation
        combineExpressions()
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'}

########################################

classes = [ \
    bcb_props,
    bcb_asst_con_rei_beam_props,
    bcb_asst_con_rei_wall_props,
    bcb_panel,
    OBJECT_OT_bcb_set_config,
    OBJECT_OT_bcb_get_config,
    OBJECT_OT_bcb_clear,
    OBJECT_OT_bcb_build,
    OBJECT_OT_bcb_update,
    OBJECT_OT_bcb_export_ascii,
    OBJECT_OT_bcb_export_ascii_fm,
    OBJECT_OT_bcb_bake,
    OBJECT_OT_bcb_add,
    OBJECT_OT_bcb_del,
    OBJECT_OT_bcb_move_up,
    OBJECT_OT_bcb_move_down,
    OBJECT_OT_bcb_up,
    OBJECT_OT_bcb_down,
    OBJECT_OT_bcb_reset,
    OBJECT_OT_bcb_estimate_cluster_radius,
    OBJECT_OT_bcb_asst_update
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
    cnt = 0
    for obj in objs:
        objGrpsTmp = []
        for elemGrp in elemGrps:
            elemGrpName = elemGrp[EGSidxName]
            if elemGrpName in bpy.data.groups:
                if obj.name in bpy.data.groups[elemGrpName].objects:
                    objGrpsTmp.append(elemGrps.index(elemGrp))
        if len(objGrpsTmp) > 1:
            sys.stdout.write("Warning: Object %s belongs to more than one element group, defaults are used. Element groups:" %obj.name)
            for idx in objGrpsTmp: sys.stdout.write(" #%d %s" %(idx, elemGrps[idx][EGSidxName]))
            print()
            q = 1
        elif len(objGrpsTmp) == 0: q = 1
        else: q = 0
        if q:
            for elemGrp in elemGrps:
                elemGrpName = elemGrp[EGSidxName]
                if elemGrpName == '':
                    objGrpsTmp = [elemGrps.index(elemGrp)]
                    break
        if len(objGrpsTmp) > 0:
              objsEGrp.append(objGrpsTmp[0])
              cnt += 1
        else: objsEGrp.append(0)

    return objsEGrp, cnt

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
                                if elemGrps[objsEGrp[k]][EGSidxRqVP] <= 1:
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
        reqVertexPairsObjA = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][EGSidxRqVP]
        reqVertexPairsObjB = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][EGSidxRqVP]
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
            geoContactArea = overlapAreaX +overlapAreaY +overlapAreaZ

        ### Or calculate contact area based on predefined custom thickness
        else:
            geoContactArea = overlapX +overlapY +overlapZ
            # This should actually be:
            # geoContactArea = (overlapX +overlapY +overlapZ) *nonManifoldThickness
            # For updating possibility this last operation is postponed to setConstraintSettings()

    else: geoContactArea = 0
            
    ### Find out element thickness to be used for bending threshold calculation 
    geo = [overlapX, overlapY, overlapZ]
    geoAxis = [1, 2, 3]
    geo, geoAxis = zip(*sorted(zip(geo, geoAxis)))
    geoHeight = geo[1]  # First item = mostly 0, second item = thickness/height, third item = width 
    geoWidth = geo[2]
    
    ### Use center of contact area boundary box as constraints location
    centerX = max(bbAMin[0],bbBMin[0]) +(overlapX /2)
    centerY = max(bbAMin[1],bbBMin[1]) +(overlapY /2)
    centerZ = max(bbAMin[2],bbBMin[2]) +(overlapZ /2)
    center = Vector((centerX, centerY, centerZ))
    #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon

    return geoContactArea, geoHeight, geoWidth, center, geoAxis

########################################

def calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    connectsGeo = []
    connectsLoc = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        
        ###### Calculate contact area for a single pair of objects
        geoContactArea, geoHeight, geoWidth, center, geoAxis = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB)
        
        # Geometry array: [area, height, width, surfThick, axisNormal, axisHeight, axisWidth]
        connectsGeo.append([geoContactArea, geoHeight, geoWidth, 0, geoAxis[0], geoAxis[1], geoAxis[2]])
        connectsLoc.append(center)
        
    return connectsGeo, connectsLoc

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
    connectsGeo = []
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
            geoContactArea, geoHeight, geoWidth, center, geoAxis = calculateContactAreaBasedOnBoundaryBoxesForPair(objA, objB, customThickness=1)
            geoSurfThick = nonManifoldThickness
            
            # Geometry array: [area, height, width, surfThick, axisNormal, axisHeight, axisWidth]
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, geoSurfThick, geoAxis[0], geoAxis[1], geoAxis[2]])
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
#            try: modA_bool.use_bmesh = 1  # Try to enable bmesh based boolean if possible
#            except: pass
#            else:
#                try: modA_bool.use_bmesh_connect_regions = 0  # Disable this for bmesh to avoid long malformed faces
#                except: pass
#                try: modA_bool.threshold = 0.2  # Not sure what kind of threshold this is but 0 or 1 led to bad results including the full original mesh
#                except: pass                    # (If connection centers are lying on element centers, that's a sign for a bad boolean operation)
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
                # Apply transforms so that local axes are matching world space axes (important for constraint orientation)
                objIntersect.select = 1
                bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
                
                ### Calculate center of intersection mesh based on its boundary box (throws ugly "group # is unclassified!" warnings)
#                objIntersect.select = 1
#                #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
#                center = objIntersect.matrix_world.to_translation()
                ### Calculate center of intersection mesh based on its boundary box (alternative code, slower but no warnings)
                bbMin, bbMax, center = boundaryBox(objIntersect, 1)
                
                ### Find out element thickness to be used for bending threshold calculation (the diameter of the intersection mesh should be sufficient for now)
                geo = list(objIntersect.dimensions)
                geoAxis = [1, 2, 3]
                geo, geoAxis = zip(*sorted(zip(geo, geoAxis)))
                geoHeight = geo[1]   # First item = mostly 0, second item = thickness/height, third item = width 
                geoWidth = geo[2]
                
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
#                geoContactArea = (surfaceDisp -surfaceBoolUnion) /2
                ### The contact area is half the surface area of the intersection mesh without displacement
                geoContactArea = surfaceBoolIntersectRemDisp /2
                geoContactArea *= correction
                if geoContactArea < 0: print('Error on boolean operation, contact area negative:', objA.name, objB.name)
                
                # Unlink new object from second scene
                sceneTemp.objects.unlink(objIntersect)
                
            # If intersection mesh has no geometry then invalidate connection
            else:
                geoContactArea = 0
                geoHeight = 0
                geoWidth = 0
                geoAxis = [1, 2, 3]
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
            
            # Geometry array: [area, height, width, surfThick, axisNormal, axisHeight, axisWidth]
            connectsGeo.append([geoContactArea, geoHeight, geoWidth, 0, geoAxis[0], geoAxis[1], geoAxis[2]])
            connectsLoc.append(center)
                
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    bpy.data.scenes.remove(sceneTemp)
                
    print()
    return connectsGeo, connectsLoc

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsGeo, connectsLoc):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")
    
    connectsPairTmp = []
    connectsGeoTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    minimumArea = searchDistance**2
    for i in range(len(connectsPair)):
        if connectsGeo[i][0] > minimumArea:
            connectsPairTmp.append(connectsPair[i])
            connectsGeoTmp.append(connectsGeo[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsGeo = connectsGeoTmp
    connectsLoc = connectsLocTmp
    
    print("Connections skipped due to zero contact area:", connectCntOld -connectCnt)
    return connectsPair, connectsGeo, connectsLoc

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
        ### First check if connection type is valid for both groups
        connectTypeIdxA = elemGrps[elemGrpA][EGSidxCTyp]
        try: connectTypeA = connectTypes[connectTypeIdxA]
        except: connectTypeA = [None, 0]
        connectTypeIdxB = elemGrps[elemGrpB][EGSidxCTyp]
        try: connectTypeB = connectTypes[connectTypeIdxB]
        except: connectTypeB = [None, 0]
        ### Use the connection type with the smaller count of constraints for connection between different element groups
        ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
        if connectTypeA[1] <= connectTypeB[1]:
              connectType = connectTypeA
        else: connectType = connectTypeB
        if connectType[0] == None: connectsConsts.append([])  # In case the connection type is unknown (no constraints)
        else:
            items = []
            for j in range(connectType[1]):
                items.append(constCnt +j)
                constsConnect.append(i)
            connectsConsts.append(items)
            constCnt += len(items)
            
    return connectsPair, connectsConsts, constsConnect

################################################################################   

def backupLayerSettingsAndActivateNextEmptyLayer(scene):

    ### Activate the first empty layer
    print("Activating the first empty layer...")
    
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
    
########################################

def backupLayerSettingsAndActivateNextLayerWithObj(scene, objToFind):

    ### Activating the first layer with constraint empty object
    print("Activating the first layer with constraint empty object...")
    
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
        if objToFind in objsOnLayer:
            layersNew[i] = 1
            qFound = 1
            break
    if qFound:
        # Set new layers
        scene.layers = [bool(q) for q in layersNew]  # Convert array into boolean (required by layers)
        
    # Return old layers state
    return layersBak

########################################

def backupLayerSettingsAndActivateAllLayers(scene):

    ### Activate all layers
    print("Activating all layers...")
    
    ### Backup layer settings
    layersBak = []
    layersNew = []
    for i in range(20):
        layersBak.append(int(scene.layers[i]))
        layersNew.append(0)
    # Activate all layers
    scene.layers = [True for q in scene.layers]
       
    # Return old layers state
    return layersBak
    
################################################################################   

def createEmptyObjs(scene, constCnt):
    
    ### Create empty objects
    print("Creating empty objects... (%d)" %constCnt)

    ### Create first object
    objConst = bpy.data.objects.new('Constraint', None)
    bpy.context.scene.objects.link(objConst)
    objConst.empty_draw_type = 'CUBE'
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

def addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsConsts, connectsLoc, constsConnect, exData):
    
    ### Add base constraint settings to empties
    print("Adding base constraint settings to empties... (%d)" %len(emptyObjs))
    
    ### Add further settings
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
            export(exData, loc=connectsLoc[l].to_tuple(), obj1=objs[connectsPair[l][0]].name, obj2=objs[connectsPair[l][1]].name)
              
    ### Naming of the constraints according to their connection participation
    for k in range(len(connectsPair)):
        i = 1
        for cIdx in connectsConsts[k]:
            name = "Con.%03d.%d" %(k, i)
            if not asciiExport: emptyObjs[cIdx].name = name
            else:               export(exData, idx=cIdx, name=name)
            i += 1
            
    print()
                
################################################################################   

def getAttribsOfConstraint(objConst):

    ### Create a dictionary of all attributes with values from the given constraint empty object    
    con = objConst.rigid_body_constraint
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
    con = objConst.rigid_body_constraint    
    for prop in props.items():
        try: setattr(con, prop[0], prop[1])
        except: print("Error: Failed to set attribute:", prop[0], prop[1])
        
########################################

def export(exData, idx=None, objC=None, name=None, loc=None, obj1=None, obj2=None, tol1=None, tol2=None, rotm=None, quat=None, attr=None):

    ### Adds data to the export data array
    # export(exData, idx=1, objC=objConst, name=1, loc=1, obj1=1, obj2=1, tol1=[tol1dist, tol1rot], tol2=[tol2dist, tol2rot], rotm=1, quat=1, attr=1)
    
    if idx == None:
        exData.append([])
        idx = len(exData) -1
        for i in range(9):
            exData[idx].append(None)
    if name != None and objC != None: exData[idx][0] = objC.name
    elif name != None:                exData[idx][0] = name
    if loc != None and objC != None:  exData[idx][1] = objC.location.to_tuple()
    elif loc != None:                 exData[idx][1] = loc
    if obj1 != None and objC != None: exData[idx][2] = objC.rigid_body_constraint.object1.name
    elif obj1 != None:                exData[idx][2] = obj1
    if obj2 != None and objC != None: exData[idx][3] = objC.rigid_body_constraint.object2.name
    elif obj2 != None:                exData[idx][3] = obj2
    if tol1 != None and objC != None: exData[idx][4] = ["TOLERANCE", 0, 0]  # Undefined special case
    elif tol1 != None:                exData[idx][4] = tol1                 # Should always get data
    if tol2 != None and objC != None: exData[idx][5] = ["PLASTIC", 0, 0]  # Undefined special case
    elif tol2 != None:                exData[idx][5] = tol2               # Should always get data
    if rotm != None and objC != None: exData[idx][6] = objC.rotation_mode
    elif rotm != None:                exData[idx][6] = rotm
    if quat != None and objC != None: exData[idx][7] = Vector(objC.rotation_quaternion).to_tuple()
    elif quat != None:                exData[idx][7] = quat
    if attr != None and objC != None: exData[idx][8] = getAttribsOfConstraint(objC)
    elif attr != None:                exData[idx][8] = attr

    # Data structure ("[]" means not always present):
    # 0 - empty.name
    # 1 - empty.location
    # 2 - obj1.name
    # 3 - obj2.name
    # 4 - [ ["TOLERANCE", tol1dist, tol1rot] ]
    # 5 - [ ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot] ]
    # 6 - [empty.rotation_mode]
    # 7 - [empty.rotation_quaternion]
    # 8 - empty.rigid_body_constraint (dictionary of attributes)
    #
    # Pseudo code for special constraint treatment:
    #
    # If tol1dist or tol1rot is exceeded:
    #     If normal constraint: It will be detached
    #     If spring constraint: It will be set to active
    # If tol2dist or tol2rot is exceeded:
    #     If spring constraint: It will be detached

    return exData

########################################

def build_fm():

    ### Exports all constraint data to the Fracture Modifier (special Blender version required).
    print()
    print("Creating fracture modifier mesh from BCB data...")
    time_start = time.time()

    scene = bpy.context.scene

    s = bpy.data.texts["BCB_export.txt"].as_string()
    o = pickle.loads(zlib.decompress(base64.decodestring(s.encode())))

    # Create object to use the fracture modifier on
    bpy.ops.mesh.primitive_ico_sphere_add(size=1, view_align=False, enter_editmode=False, location=(0, 0, 0))
    ob = bpy.context.scene.objects.active
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

    obParent = None
    count = len(o)
    indexmap = dict()
    j = 0
    for i in range(count):
        ob1 = o[i][2]
        ob2 = o[i][3]
        if not ob1 in indexmap.keys():
            try: obb1 = bpy.context.scene.objects[ob1]
            except: pass
            else:
                indexmap[ob1] = md.mesh_islands.new(obb1)
                #indexmap[ob1].rigidbody.use_margin = True
                #if obb1.rigid_body.type == 'PASSIVE':
                #    indexmap[ob1].rigidbody.kinematic=True
                #    indexmap[ob1].rigidbody.type='ACTIVE'
                if obParent == None and obb1.parent: obParent = obb1.parent
                obb1.select = True
                
        if not ob2 in indexmap.keys():
            try: obb2 = bpy.context.scene.objects[ob2]
            except: pass
            else:
                indexmap[ob2] = md.mesh_islands.new(obb2)
                #indexmap[ob2].rigidbody.use_margin = True
                #if obb2.rigid_body.type == 'PASSIVE':
                #    indexmap[ob2].rigidbody.kinematic=True
                #    indexmap[ob2].rigidbody.type='ACTIVE'
                if obParent == None and obb2.parent: obParent = obb2.parent
                obb2.select = True

    print('Time mesh islands: %0.2f s' %(time.time()-time_start))
    time_const = time.time()

    plastic_on = 0
    plastic_off = 0
    noplastic = 0
    for i in range(count):
        #print("CONSTRAINT", i)
        #print(o[i])
        prop_index = 0
        j = 0
        name = o[i][j]
        j += 1
        
        # 0 - empty.location
        pos = mathutils.Vector(o[i][j])
        j += 1
        
        # 1 - obj1.name
        # 2 - obj2.name
        ob1 = o[i][j]
        ob2 = o[i][j+1]
        j += 2
        
        # 3 - [ ["TOLERANCE", tol1dist, tol1rot] ]
        if o[i][j] is not None and len(o[i][j]) == 3 and o[i][j][0] in {"TOLERANCE"}:
            breaking_distance = o[i][j][1]
            breaking_angle = o[i][j][2]
            #j += 1
        else:
            breaking_distance = -1
            breaking_angle = -1
        j += 1
        
        # 4 - [ ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot] ]
        if o[i][j] is not None and len(o[i][j]) == 3 and o[i][j][0] in {"PLASTIC", "PLASTIC_OFF"}: #ugh, variable length ?
            plastic_distance = o[i][j][1]
            plastic_angle = o[i][j][2]
            
            if o[i][j][0] == "PLASTIC": 
                plastic = True
                plastic_on += 1
            else:
                plastic = False
                plastic_off += 1
            #j += 1
        else:
            plastic_distance = -1
            plastic_angle = -1
            plastic = False
            noplastic += 1
        j += 1    
        
        # 5 - [empty.rotation_mode]
        # 6 - [empty.rotation_quaternion]
        if o[i][j] == "QUATERNION": # euler ?
            rot = mathutils.Quaternion(o[i][j+1])
            #j += 2
        else:
            rot = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
        j += 2
                
        # 7 - empty.rigid_body_constraint (dictionary of attributes)
        props = o[i][j]
        prop_index = j
        
        #peek the type...
        type = props["type"]
        if type != "GENERIC_SPRING":
            noplastic -= 1
        
        #ok first check whether the mi exists
        #via is object in group (else its double)
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
               
            for p in props.items():
                if p[0] not in {"name","type", "object1", "object2"}:
                    #print("Set: ", p[0], p[1])
                    setattr(con, p[0], p[1])
            
            #con.id = props["name"]
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
            
    #        ind = prop_index+1
    #        if len(o[i][ind]) == 3 and o[i][ind][0] == "BREAK":
    #            con.breaking_distance = o[i][ind][1] # this is normed to 0...1, odd... why not absolute ?
    #            con.breaking_angle = o[i][ind][2] * math.pi

    #clumsy, but could work: disable plastic globally, when no plastic has been found at all
    #if plastic_on == 0 and plastic_off == 0:
    #    for i in range(count):
    #        md.mesh_constraints[i].plastic_angle = -1
    #        md.mesh_constraints[i].plastic_distance = -1
    
    print('Time constraints: %0.2f s' %(time.time()-time_const))
    
    #bpy.ops.object.fracture_refresh()
    bpy.context.scene.objects.active = None
    ob.select = False
    
    bpy.ops.object.delete(use_global=True)

    # Apply parent if one has been found earlier
    if obParent != None:
        ob.select = 1
        obParent.select = 1
        bpy.context.scene.objects.active = obParent
        print("Parenting", ob.name, "to", obParent.name, "...")
        bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)
        obParent.select = 0
        bpy.context.scene.objects.active = ob

    scene.layers = [bool(q) for q in layersBak]  # Revert scene layer settings from backup

    print('-- Time total: %0.2f s' %(time.time()-time_start))
    print()
    print('Imported: %d Plastic ON,  %d Plastic OFF,  %d NOPLASTIC' % (plastic_on, plastic_off, noplastic))
    print('Done.')
    print()

########################################

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
        if useAccurateArea:
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

        # Area correction calculation for cylinders (*pi/4)
        if elemGrps[elemGrpA][EGSidxCyln] or elemGrps[elemGrpB][EGSidxCyln]: a *= 0.7854

        ### Use the connection type with the smaller count of constraints for connection between different element groups
        ### (Menu order priority driven in older versions. This way is still not perfect as it has some ambiguities left, ideally the CT should be forced to stay the same for all EGs.)
        if connectTypes[elemGrps[elemGrpA][EGSidxCTyp]][1] <= connectTypes[elemGrps[elemGrpB][EGSidxCTyp]][1]:
            CT = elemGrps[elemGrpA][EGSidxCTyp]
            elemGrp = elemGrpA
        else:
            CT = elemGrps[elemGrpB][EGSidxCTyp]
            elemGrp = elemGrpB

        ### Evaluate and Use always the weaker of both thresholds for every degree of freedom
        try: brkThresExprC_A = eval(elemGrps[elemGrpA][EGSidxBTC])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTC]); brkThresExprC_A = 0
        try: brkThresExprC_B = eval(elemGrps[elemGrpB][EGSidxBTC])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTC]); brkThresExprC_B = 0
        if brkThresExprC_A <= brkThresExprC_B: brkThresExprC = brkThresExprC_A
        else:                                  brkThresExprC = brkThresExprC_B

        try: brkThresExprT_A = eval(elemGrps[elemGrpA][EGSidxBTT])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTT]); brkThresExprT_A = 0
        try: brkThresExprT_B = eval(elemGrps[elemGrpB][EGSidxBTT])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTT]); brkThresExprT_B = 0
        if brkThresExprT_A <= brkThresExprT_B: brkThresExprT = brkThresExprT_A
        else:                                  brkThresExprT = brkThresExprT_B

        try: brkThresExprS_A = eval(elemGrps[elemGrpA][EGSidxBTS])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTS]); brkThresExprS_A = 0
        try: brkThresExprS_B = eval(elemGrps[elemGrpB][EGSidxBTS])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTS]); brkThresExprS_B = 0
        if brkThresExprS_A <= brkThresExprS_B: brkThresExprS = brkThresExprS_A
        else:                                  brkThresExprS = brkThresExprS_B

        if len(elemGrps[elemGrpA][EGSidxBTS9]):  # Can also have zero-size string if not used
            try: brkThresExprS9_A = eval(elemGrps[elemGrpA][EGSidxBTS9])
            except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTS9]); brkThresExprS9_A = 0
        else: brkThresExprS9_A = -1
        if len(elemGrps[elemGrpB][EGSidxBTS9]):  # Can also have zero-size string if not used
            try: brkThresExprS9_B = eval(elemGrps[elemGrpB][EGSidxBTS9])
            except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTS9]); brkThresExprS9_B = 0
        else: brkThresExprS9_B = -1
        if brkThresExprS9_A == -1 or brkThresExprS9_B == -1: brkThresExprS9 = -1
        else:    
            if brkThresExprS9_A <= brkThresExprS9_B: brkThresExprS9 = brkThresExprS9_A
            else:                                    brkThresExprS9 = brkThresExprS9_B

        try: brkThresExprB_A = eval(elemGrps[elemGrpA][EGSidxBTB])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTB]); brkThresExprB_A = 0
        try: brkThresExprB_B = eval(elemGrps[elemGrpB][EGSidxBTB])
        except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTB]); brkThresExprB_B = 0
        if brkThresExprB_A <= brkThresExprB_B: brkThresExprB = brkThresExprB_A
        else:                                  brkThresExprB = brkThresExprB_B

        if len(elemGrps[elemGrpA][EGSidxBTB9]):  # Can also have zero-size string if not used
            try: brkThresExprB9_A = eval(elemGrps[elemGrpA][EGSidxBTB9])
            except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpA][EGSidxBTB9]); brkThresExprB9_A = 0
        else: brkThresExprB9_A = -1
        if len(elemGrps[elemGrpB][EGSidxBTB9]):  # Can also have zero-size string if not used
            try: brkThresExprB9_B = eval(elemGrps[elemGrpB][EGSidxBTB9])
            except: print("\rError: Expression could not be evaluated:", elemGrps[elemGrpB][EGSidxBTB9]); brkThresExprB9_B = 0
        else: brkThresExprB9_B = -1
        if brkThresExprB9_A == -1 or brkThresExprB9_B == -1: brkThresExprB9 = -1
        else:    
            if brkThresExprB9_A <= brkThresExprB9_B: brkThresExprB9 = brkThresExprB9_A
            else:                                    brkThresExprB9 = brkThresExprB9_B

        springStiff = elemGrps[elemGrp][EGSidxSStf]

        if not asciiExport:
            # Store value as ID property for debug purposes
            for idx in consts: emptyObjs[idx]['ContactArea'] = geoContactArea
            ### Check if full update is necessary (optimization)
            objConst0 = emptyObjs[consts[0]]
            if 'ConnectType' in objConst0.keys() and objConst0['ConnectType'] == CT: qUpdateComplete = 0
            else: objConst0['ConnectType'] = CT; qUpdateComplete = 1
        else:
            tol1dist = elemGrps[elemGrp][EGSidxTl1D] *scene.rigidbody_world.time_scale
            tol1rot = elemGrps[elemGrp][EGSidxTl1R] *scene.rigidbody_world.time_scale
            tol2dist = elemGrps[elemGrp][EGSidxTl2D] *scene.rigidbody_world.time_scale
            tol2rot = elemGrps[elemGrp][EGSidxTl2R] *scene.rigidbody_world.time_scale

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
        if snapToAreaOrient:
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
            if alignVertical:
                # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
                
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
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision, ct='FIXED')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
                
        ### 1x POINT; Linear omni-directional breaking threshold
        if CT == 2:
            correction = 1
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision, ct='POINT')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
        
        ### 1x POINT + 1x FIXED; Linear omni-directional, bending breaking thresholds    
        if CT == 3:
            correction = 1 /2   # As both constraints bear all load and forces are evenly distributed among them the breaking thresholds need to be divided by their count to compensate

            ### First constraint
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision, ct='POINT')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Second constraint
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprB
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision, ct='FIXED')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
        
        ### 1x GENERIC; Compressive threshold
        if CT == 4 or CT == 5 or CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
            ### First constraint
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock all directions for the compressive force
                ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                ### Also rotational forces should only be carried by the tensile constraint
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=0,llxu=99999, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation to that vector
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 1x GENERIC; Tensile (3D)
        if CT == 4:
            ### Second constraint
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock all directions for the tensile force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=0,llyl=0,llyu=0,llzl=0,llzu=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 2x GENERIC; Tensile + shearing (3D), bending (3D) breaking thresholds
        if CT == 5:
            ### Tensile + shearing constraint (3D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for shearing force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=1,ullz=1, llxl=-99999,llxu=0,llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending constraint (3D)
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprS
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for bending force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 3x GENERIC; Tensile constraint (1D) breaking threshold
        if CT == 6 or CT == 11 or CT == 12 or CT == 15 or CT == 16 or CT == 17 or CT == 18:
            ### Tensile constraint (1D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprT
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock direction for tensile force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=1,ully=0,ullz=0, llxl=-99999,llxu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 3x GENERIC; Shearing constraint (2D), bending constraint (3D) breaking thresholds
        if CT == 6 or CT == 11 or CT == 12:
            ### Shearing constraint (2D)
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprS
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for shearing force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=1,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending constraint (3D)
            correction = 1
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprB
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions for bending force
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 2x GENERIC; Shearing (1D) breaking thresholds
        if CT == 15 or CT == 16 or CT == 17 or CT == 18:
            correction = 2.2   # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            ### Shearing constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprS
            if brkThresExprS9 != -1:
                value1 = value
                value = brkThresExprS9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
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
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Shearing constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresExprS9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ully=1,ullz=0, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ully=0,ullz=1, llyl=0,llyu=0,llzl=0,llzu=0, ulax=0,ulay=0,ulaz=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])
            
        ### 2x GENERIC; Bending + torsion (1D) breaking thresholds
        if CT == 15 or CT == 17:
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library

            ### Bending with torsion constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprB
            if brkThresExprB9 != -1:
                value1 = value
                value = brkThresExprB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
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
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending with torsion constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresExprB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ### 3x GENERIC; Bending (1D), torsion (1D) breaking thresholds
        if CT == 16 or CT == 18:
            correction = 1.5  # Averaged correction factor for deviation of angular force evaluation for 6Dof constraints within the Bullet library

            ### Bending without torsion constraint #1
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            value = brkThresExprB
            if brkThresExprB9 != -1:
                value1 = value
                value = brkThresExprB9
                value2 = value
                values = [value1, value2]
                values.sort()
                value = values[0]  # Find and use smaller value (to be used along h axis)
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
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
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Bending without torsion constraint #2
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
            if brkThresExprB9 != -1:
                value = values[1]  # Find and use larger value (to be used along w axis)
                brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=0,ulaz=1, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=0,ulay=1,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

            ### Torsion constraint
            cIdx = consts[cInc]; cInc += 1
            if not asciiExport:
                objConst = emptyObjs[cIdx]
            else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings

            try: value = values[0]  # Use the smaller value from either standard or 90° bending thresholds as base for torsion
            except: pass
#            value *= .01  # Use 1% of the bending thresholds for torsion 
            value *= .1  # Use 10% of the bending thresholds for torsion 

#            value = brkThresExprS
#            if brkThresExprS9 != -1:
#                value1 = value
#                value = brkThresExprS9
#                value2 = value
#                values = [value1, value2]
#                values.sort()
#                value = values[0]  # Find and use smaller value (to be used along h axis)
#            value /= 2  # Use half of the smaller shearing breaking thresholds for torsion

            brkThres = value /scene.rigidbody_world.steps_per_second *correction
            ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
            setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
            if qUpdateComplete:
                objConst.rotation_mode = 'QUATERNION'
                ### Lock directions accordingly to axis
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                if constAxisToLock == 3:   setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
                elif constAxisToLock == 2: setConstParams(objConst, ct='GENERIC', ullx=0,ully=0,ullz=0, ulax=1,ulay=0,ulaz=0, laxl=0,laxu=0,layl=0,layu=0,lazl=0,lazu=0)
            # Align constraint rotation like above
            objConst.rotation_quaternion = dirVec.to_track_quat('X','Z')
            if asciiExport:
                export(exData, idx=cIdx, objC=objConst, rotm=1, quat=1, attr=1)
                export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot])

        ###### Springs (additional)

        ### 3x SPRING; Circular placed for plastic deformability
        if CT == 7 or CT == 9 or CT == 11 or CT == 17 or CT == 18:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ### Loop through all constraints of this connection
            for i in range(3):
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    if CT == 7:
                           export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])
                    else:  export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC_OFF", tol2dist, tol2rot])
                
        ### 4x SPRING; Circular placed for plastic deformability
        if CT == 8 or CT == 10 or CT == 12:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresExprC
            brkThres = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            ### Loop through all constraints of this connection
            for i in range(4):
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    if CT == 8:
                           export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])
                    else:  export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC_OFF", tol2dist, tol2rot])
                
        ###### Springs only CTs

        ### 3 x 3x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 13:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 3   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresExprC
            brkThres1 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresExprT
            brkThres2 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresExprS
            brkThres3 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # Loop through all constraints of this connection
            for j in range(3):

                ### First constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres1, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Second constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres2, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Third constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres3, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

        ### 3 x 4x SPRING; Compressive (1D), tensile (1D), shearing (2D) breaking thresholds; circular placed for plastic deformability
        if CT == 14:
            correction = 2.2  # Generic constraints detach already when less force than the breaking threshold is applied (around a factor of 0.455) so we multiply our threshold by this correctional value
            correction /= 4   # Divided by the count of constraints which are sharing the same degree of freedom
            radius = geoHeight /2
            value = brkThresExprC
            brkThres1 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresExprT
            brkThres2 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            value = brkThresExprS
            brkThres3 = value /scene.rigidbody_world.steps_per_second *scene.rigidbody_world.time_scale *correction
            # Loop through all constraints of this connection
            for j in range(4):

                ### First constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres1, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Second constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres2, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

                ### Third constraint
                cIdx = consts[cInc]; cInc += 1
                if not asciiExport:
                    objConst = emptyObjs[cIdx]
                else: setAttribsOfConstraint(objConst, constSettingsBak)  # Overwrite temporary constraint object with default settings
                if asciiExport:
                    objConst.location = Vector(exData[cIdx][1])  # Move temporary constraint empty object to correct location
                    # This is no nice solution as we reuse already exported data for further calculation as we have no access to earlier connectsLoc here.
                    # TODO: Better would be to postpone writing of locations from addBaseConstraintSettings() to here but this requires locs to be stored as another scene property.
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, bt=brkThres3, ub=constraintUseBreaking, dc=disableCollision)
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
                if asciiExport:
                    export(exData, idx=cIdx, objC=objConst, loc=1, rotm=1, quat=1, attr=1)
                    export(exData, idx=cIdx, tol1=["TOLERANCE", tol1dist, tol1rot], tol2=["PLASTIC", tol2dist, tol2rot])

        if not asciiExport:
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
                axs = Vector((0, side *aspect, side))
            else:
                # Use standard size for drawing of non-directional constraints
                axs = Vector((emptyDrawSize, emptyDrawSize, emptyDrawSize))
            # Add settings for drawing    
            for cIdx in consts:
                objConst = emptyObjs[cIdx]
                ###### setConstParams(objConst, axs,e,bt,ub,dc,ct, ullx,ully,ullz, llxl,llxu,llyl,llyu,llzl,llzu, ulax,ulay,ulaz, laxl,laxu,layl,layu,lazl,lazu, usx,usy,usz, sdx,sdy,sdz, ssx,ssy,ssz)
                setConstParams(objConst, axs=axs)

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
        facing = elemGrps[objsEGrp[k]][EGSidxFacg]
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
        scale = elemGrps[objsEGrp[k]][EGSidxScal]
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
                scale = elemGrps[objsEGrp[k]][EGSidxScal]
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
        qBevel = elemGrps[objsEGrp[k]][EGSidxBevl]
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
    
    objsRevertScale = []
    for j in range(len(elemGrps)):
        elemGrp = elemGrps[j]
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        for k in range(len(objs)):
            try: scale = elemGrps[objsEGrp[k]][EGSidxScal]  # Try in case elemGrps is from an old BCB version
            except: qScale = 0
            else: qScale = 1
            if j == objsEGrp[k]:
                obj = objs[k]
                if obj != None:
                    if obj.rigid_body != None:
                        if "bcb_child" in obj.keys():
                            obj = scene.objects[obj["bcb_child"]]
                        obj.select = 1
                        # Temporarily revert element scaling for mass calculation
                        if qScale:
                            if scale != 0 and scale != 1:
                                obj.scale /= scale
                                objsRevertScale.append([obj, scale])
        
        materialPreset = elemGrp[EGSidxMatP]
        materialDensity = elemGrp[EGSidxDens]
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material="Custom", density=materialDensity)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Reapply element scaling after mass calculation
    for objScale in objsRevertScale:
        obj = objScale[0]
        scale = objScale[1]
        obj.scale *= scale

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
#    #print(exportData)
#    i = 0
#    for const in exportData:
#        if i > 300: bpy.ops.object.empty_add(type='SPHERE', view_align=False, location=const[0], layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
#        if i > 600: break
#        i += 1
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
        
        exData = []

        #########################
        ###### Create new empties
        if not "bcb_objs" in scene.keys():
                
            ###### Create object lists of selected objects
            childObjs = []
            objs, emptyObjs = gatherObjects(scene)
            objsEGrp, objCntInEGrps = createElementGroupIndex(objs)
            
            #############################
            ###### Prepare connection map
            if len(objs) > 1:
                if objCntInEGrps > 1:
                    time_start_connections = time.time()

                    # Remove instancing from objects
                    bpy.ops.object.make_single_user(type='SELECTED_OBJECTS', object=False, obdata=True, material=False, texture=False, animation=False)
                    # Apply scale factor of all objects (to make sure volume and mass calculation are correct)
                    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                
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
                        connectsGeo, connectsLoc = calculateContactAreaBasedOnBooleansForAll(objs, connectsPair)
                    else:
                        connectsGeo, connectsLoc = calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair)
                    ###### Delete connections with zero contact area
                    connectsPair, connectsGeo, connectsLoc = deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsGeo, connectsLoc)
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
                        layersBak = backupLayerSettingsAndActivateNextEmptyLayer(scene)
                        ###### Create empty objects (without any data)
                        if not asciiExport:
                            emptyObjs = createEmptyObjs(scene, len(constsConnect))
                        else:
                            emptyObjs = [None for i in range(len(constsConnect))]  # if this is the case emptyObjs is filled with an empty array on None
                        ###### Bundling close empties into clusters, merge locations and count connections per cluster
                        if clusterRadius > 0: bundlingEmptyObjsToClusters(connectsLoc, connectsConsts)
                        ###### Add constraint base settings to empties
                        addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsConsts, connectsLoc, constsConnect, exData)
                        # Restore old layers state
                        scene.update()  # Required to update empty locations before layer switching
                        scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)
                        ###### Store build data in scene
                        if not asciiExport: storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, constsConnect)
                        
                        print('-- Time: %0.2f s\n' %(time.time()-time_start_building))
                    
                    ###### No connections found   
                    else:
                        print('No connections found. Probably the search distance is too small.')       
                
                ###### No element assigned to element group found
                else:
                    print('Please make sure that at least two mesh objects are assigned to element groups.')       
                    print('Nothing done.')       

            ###### No selected input found   
            else:
                print('Please select at least two mesh objects to connect.')       
                print('Nothing done.')       
       
        ##########################################     
        ###### Update already existing constraints
        if "bcb_objs" in scene.keys() or asciiExport:
            
            ###### Store menu config data in scene
            storeConfigDataInScene(scene)
            ###### Get temp data from scene
            if not asciiExport: objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, constsConnect = getBuildDataFromScene(scene)
            ###### Create fresh element group index to make sure the data is still valid (reordering in menu invalidates it for instance)
            objsEGrp, objCntInEGrps = createElementGroupIndex(objs)
            ###### Store build data in scene
            storeBuildDataInScene(scene, None, objsEGrp, None, None, None, None, None, None, None, None)
                            
            if len(emptyObjs) > 0 and objCntInEGrps > 1:
                ###### Set general rigid body world settings
                initGeneralRigidBodyWorldSettings(scene)
                ###### Find and activate first layer with constraint empty object (required to set constraint locations in setConstraintSettings())
                if not asciiExport: layersBak = backupLayerSettingsAndActivateNextLayerWithObj(scene, emptyObjs[0])
                ###### Set constraint settings
                setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsGeo, connectsConsts, constsConnect, exData)
                ### Restore old layers state
                if not asciiExport:
                    scene.update()  # Required to update empty locations before layer switching
                    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)
                ###### Calculate mass for all mesh objects
                calculateMass(scene, objs, objsEGrp, childObjs)
                ###### Exporting data into internal ASCII text file
                if asciiExport: exportDataToText(exData)
            
                if not asciiExport:
                    # Deselect all objects
                    bpy.ops.object.select_all(action='DESELECT')
                    # Select all new constraint empties
                    for emptyObj in emptyObjs: emptyObj.select = 1
                
                print('-- Time total: %0.2f s\n' %(time.time()-time_start))
                print('Constraints:', len(emptyObjs), '| Elements:', len(objs), '| Children:', len(childObjs))
                print('Done.')

            ###### No input found   
            else:
                print('Neither mesh objects to connect nor constraint empties for updating selected.')       
                print('Nothing done.')
                     
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
    bpy.types.WindowManager.bcb_asst_con_rei_beam = bpy.props.PointerProperty(type=bcb_asst_con_rei_beam_props)
    bpy.types.WindowManager.bcb_asst_con_rei_wall = bpy.props.PointerProperty(type=bcb_asst_con_rei_wall_props)
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
