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

import bpy
mem = bpy.app.driver_namespace

################################################################################

### Vars:
bcb_version = (2, 6, 5)

### Customizable element group presets
presets = [
# 0                     1    2           3        4   5       6       7       8      9       10     11       12   13   14   15    16   17    18     19             20  21   22  23
# Name                  RVP  Mat.preset  Density  CT  BTC     BTT     BTS     BTS90  BTB     BTB90  BTP      T1D  T1R  T2D  T2R   Bev. Scale Facing F.Assist.+Data Cyl PLen BTX Prio
[ "",                   1,   "Uncategorized", 2400, 3, "35",  "5.2",  "155",  "",    "1.0",  "",    "1.3",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Base",               1,   "Uncategorized", 1,    0, "0",   "0",    "0",    "",    "0",    "",    "0",     0,   0,   0,   0,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Concrete",           1,   "Concrete", 2400,    6,  "35",   "3.5",  "0.9",  "",    "1.0",  "",    "0",    .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "RC Columns",         1,   "Concrete", 2400,    6,  "35",   "5.2",  "155",  "",    "1.0",  "",    "1.3",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "RC Walls",           1,   "Concrete", 2400,    6,  "35",   "5.2",  "0.9",  "",    "1.0",  "",    "1.3",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "RC Slabs",           1,   "Concrete", 2400,    6,  "35",   "5.2",  "0.9",  "",    "1.0",  "",    "1.3",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Masonry Walls",      1,   "Masonry",  1800,    6,  "10",   "2",    "0.3",  "",    "0.3",  "",    "0",    .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Timber Spruce",      1,   "Timber",   470,     6,  "40",   "80",   "7.5",  "",    "68",   "",    "80",   .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Timber Larch",       1,   "Timber",   590,     6,  "48",   "105",  "9",    "",    "93",   "",    "105",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "Timber Ash",         1,   "Timber",   690,     6,  "50",   "130",  "13"    "",    "105",  "",    "130",  .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "I-Beams Screwed",    1,   "Steel",    7800,    6,  "47.5", "23.5", "14.1", "",    "2.4",  "",    "30.6", .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "I-Beams Screwed 2",  1,   "Steel",    7800,    6,  "87.5", "33.8", "20.3", "",    "12.3", "",    "43.9", .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ],
[ "HSS-Beams Welded",   1,   "Steel",    7800,    6,  "37.5", "75",   "45",   "",    "6.6",  "",    "97.5", .1,  .4,  .2,  .8,   0,   .95,  0,     "None",        0,  0,   1,  5 ]
] # Empty name means this group is to be used when element is not part of any element group

# Actual element group list (for elements of different conflicting groups the weaker thresholds is used, also the type is changed accordingly)
elemGrps = mem["elemGrps"] = []

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
EGSidxBTS9 = 8    # Break.Thresh.Shear 90
EGSidxBTB  = 9    # Break.Thresh.Bend        | Real world material bending breaking threshold in N/mm^2.
EGSidxBTB9 = 10   # Break.Thresh.Bend 90
EGSidxBTP  = 11   # Break.Thresh.Plastic     | Real world material ultimate tensile breaking threshold in N/mm^2. Also the stiffness for Generic Spring constraints is derived from that value.
EGSidxBTPL = 21   # Plastic.Spring.Length    | Length of the springs used for plastic deformation in m. If no specific value is entered the distance between the element's centroids is used.
EGSidxBTX  = 22   # Break.Thresh.Multiplier  | Multiplier to be applied on all breaking thresholds for constraint building. This can be useful for quickly weaken or strengthen a given element group without changing the original settings.
EGSidxPrio = 23   # Connection Priority      | Changes the connection priority for this element group which will override that the weaker breaking threshold of two elements is preferred for an connection. Lower Strength Priority has similar functionality but works on all groups, however, it is ignored if the priority here is different for a particular connection.
EGSidxTl1D = 12   # Tolerance 1st Def.Dist.  | For baking: First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %)
EGSidxTl1R = 13   # Tolerance 1st Def.Rot.   | For baking: First deformation tolerance limit for angular change in radian for connection removal or plastic deformation
EGSidxTl2D = 14   # Tolerance 2nd Def.Dist.  | For baking: Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %)
EGSidxTl2R = 15   # Tolerance 2nd Def.Rot.   | For baking: Second deformation tolerance limit for angular change in radian for connection removal
EGSidxBevl = 16   # Bevel                    | Use beveling for elements to avoid `Jenga
EGSidxScal = 17   # Scale                    | Apply scaling factor on elements to avoid `Jenga
EGSidxFacg = 18   # Facing                   | Generate an addional layer of elements only for display (will only be used together with bevel and scale option)
EGSidxAsst = 19   # Formula Assistant        | Material specific formula assistant with related settings
EGSidxCyln = 20   # Cylindrical Shape        | Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns.
# Last ID: 23 (Can be different from above line!)

### Connection Types:
connectTypes = [           # Cnt C T S B S T T T T      CT
[ "PASSIVE",                 0, [0,0,0,0,0,0,0,0,0]], # 0. Passive (all other connection types will have priority over it)
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
[ "7x GENERIC + 3x SPRING", 10, [1,1,1,1,1,1,1,1,1]], # 18. Compressive, tensile, shearing XY and bending XY and torsion breaking thresholds with plastic deformability
[ "1x FIXED + 1x SPRING",    2, [1,0,0,0,1,1,1,1,1]], # 19. Linear omni-directional + bending breaking threshold with plastic deformability
[ "1x PNT + 1x FXD + 1x SPR",3, [1,0,0,1,0,1,1,1,1]], # 20. Linear omni-directional and bending breaking thresholds with plastic deformability
[ "4x GENERIC + 1x SPRING",  5, [1,1,1,1,1,1,1,1,1]], # 21. Compressive, tensile, shearing and bending breaking thresholds with plastic deformability
[ "6x GENERIC + 1x SPRING",  7, [1,1,1,1,1,1,1,1,1]], # 22. Compressive, tensile, shearing XY and bending XY breaking thresholds with plastic deformability
[ "7x GENERIC + 1x SPRING",  8, [1,1,1,1,1,1,1,1,1]]  # 23. Compressive, tensile, shearing XY and bending XY and torsion breaking thresholds with plastic deformability
]
# To add further connection types changes to following functions are necessary:
# setConstraintSettings() and bcb_panel() for the UI

### Formula Assistants with defaults (see definitions below for reference):
formulaAssistants = [
{"Name":"None", "ID":"None"},
{"Name":"Reinforced Concrete (Beams & Columns)", "ID":"con_rei_beam",
 "h":250, "w":150, "fc":30, "fs":500, "fsu":650, "elu":12, "c":20, "s":100, "ds":6, "dl":10, "n":5, "k":1.9,
 "Exp:d":   "h-c-dl/2",
 "Exp:e":   "h-2*c-dl",
 "Exp:rho": "(dl/2)**2*pi*n/(h*w)",
 "Exp:y":   "((ds/2)**2*pi*2/100*1000/s)*10/d",
 "Exp:e1":  "(h-2*c-dl)/h",
 "Exp:N-":  "fc*((h*w)-rho*(h*w))+fs*rho*(h*w)",
 "Exp:N+":  "fs*rho*(h*w)",
 "Exp:V+/-":"fs*y*e1*h**2*1.2",
 "Exp:M+/-":"(fc*(1-rho)+fs*rho*e1*4.5)*h*h*w/12/1000"
},
{"Name":"Reinforced Concrete (Walls & Slabs)", "ID":"con_rei_wall",
 "h":250, "w":150, "fc":30, "fs":500, "fsu":650, "elu":12, "c":20, "s":100, "ds":6, "dl":10, "n":5, "k":1.9,
 "Exp:d":   "h/2",
 "Exp:e":   "h-2*c-dl",
 "Exp:rho": "(dl/2)**2*pi*n/(h*w)",
 "Exp:y":   "((ds/2)**2*pi*2/100*1000/s)*10/d",
 "Exp:e1":  "(h-2*c-dl)/h",
 "Exp:N-":  "fc*((h*w)-rho*(h*w))+fs*rho*(h*w)",
 "Exp:N+":  "fs*rho*(h*w)",
 "Exp:V+/-":"(0.15*k*(100*rho*fc)**(1/3))*(h*w)",
 "Exp:M+/-":"(fc*(1-rho)+fs*rho*e1*4.5)*h*h*w/12/1000"
}]
# Material strength values (N/mm
# fs = strength of steel
# fc = strength of concrete
# fsu = ultimate strength of steel
# elu = ultimate elongation of steel
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
# Areas (mm
# A = cross area beam, h*b
# As = total cross area of the sum of all longitudinal steel bars, (dl/2)
# asw = total cross area steel stirrup in cm
#
# Coefficients:
# rho = reinforcement ratio = As/A             (dl/2)
# y = shear coefficient (asw*10/d) (% value)   ((ds/2)
# 1.2 = coefficient for shear carrying capacity
# e1 = distance between longitudinal irons in relation to the beam height: e/h (% value)   (h-2*c-dl)/h
# n = number of longitudinal steel bars
# k = scale factor
#
# Formulas for beams & columns:
# N-      ? fc * (A- rho * (h*b))  +  fs* rho * (h*b)  
# N+      ? fs * rho * (h*b)   
# V+ = V- ? fs *y * e1*h
# M+ = M- ? (fc*(1-rho) + fs*rho*e1*4.5) *h*h*w/12 /1000 
#
# Formulas for walls & slabs:
# N-      ? fc * (A- rho * (h*b))  +  fs* rho * (h*b)  
# N+      ? fs * rho * (h*b)   
# V+ = V- ? 0.15/k* ((100*rho*fc)^1/3) *h*b
# M+ = M- ? (fc*(1-rho) + fs*rho*e1*4.5) *h*h*w/12 /1000 

### Vars for developers
debug = 0                            # 0     | Enables verbose console output for debugging purposes
logPath = r"/tmp"                    #       | Path to log files if debugging is enabled
commandStop = r"/tmp/bcb-stop"       #       | For very large simulations Blender can become unresponsive on baking, in this case you can create this file to make the BCB aware you want to stop
maxMenuElementGroupItems = 300       # 300   | Maximum allowed element group entries in menu 
emptyDrawSize = 0.25                 # 0.25  | Display size of constraint empty objects as radius in meters
asciiExportName = "BCB_export.txt"   #       | Name of ASCII text file to be exported
  
# For monitor event handler
qRenderAnimation = 0                 # 0     | Render animation by using render single image function for each frame (doesn't support motion blur, keep it disabled), 1 = regular, 2 = OpenGL

### Consts
pi = 3.1416
pi2 = pi /2

########################################

# Add formula assistant settings to preset groups
for elemGrp in presets:
    for formAssist in formulaAssistants:
        if elemGrp[EGSidxAsst] == formAssist['ID']:
            elemGrp[EGSidxAsst] = formAssist.copy()
            break
# Add formula assistant settings to element groups (not required for empty elemGrps)
for elemGrp in elemGrps:
    for formAssist in formulaAssistants:
        if elemGrp[EGSidxAsst] == formAssist['ID']:
            elemGrp[EGSidxAsst] = formAssist.copy()
            break

# Backup default element groups for reset functionality
elemGrpsBak = elemGrps.copy()
