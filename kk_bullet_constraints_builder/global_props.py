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

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

class bcb_props(bpy.types.PropertyGroup):
    
    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    bool_ = bpy.props.BoolProperty
    string_ = bpy.props.StringProperty
    enum_ = bpy.props.EnumProperty
    
    ###### Create menu related properties from global vars
    menu_gotConfig = int_(0)
    menu_gotData = int_(0)
    menu_selectedElemGrp = int_(0)
    submenu_advancedG = bool_(0)
    submenu_advancedE = bool_(0)
    submenu_preprocTools = bool_(0)
    submenu_assistant = bool_(0)
    submenu_assistant_advanced = bool_(0, name="Advanced", description="Shows advanced settings and formulas.")
    asciiExport = bool_(0)  # Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment).

    assistant_menu_data = []  # (ID, Name in menu, "", Index)
    for i in range(len(formulaAssistants)):
        assistant_menu_data.append((formulaAssistants[i]["ID"], formulaAssistants[i]["Name"], "", i))
    #assistant_menu = enum_(items=assistant_menu_data, name="Type of Building Material")
    
    stepsPerSecond = int_(name="Steps Per Second",                        default=200, min=1, max=32767,   description="Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable).")
    constraintUseBreaking = bool_(name="Enable Breaking",                 default=1,                       description="Enables breaking for all constraints.")
    connectionCountLimit = int_(name="Con. Count Limit",                  default=100, min=0, max=10000,   description="Maximum count of connections per object pair (0 = disabled).")
    searchDistance = float_(name="Search Distance",                       default=0.02, min=0.0, max=1000, description="Search distance to neighbor geometry.")
    clusterRadius = float_(name="Cluster Radius",                         default=0, min=0.0, max=1000,    description="Radius for bundling close constraints into clusters (0 = clusters disabled).")
    alignVertical = float_(name="Vertical Alignment",                     default=0, min=0.0, max=1.0,     description="Enables a vertical alignment multiplier for connection type 4 or above instead of using unweighted center to center orientation (0 = disabled, 1 = fully vertical).")
    useAccurateArea = bool_(name="Accur. Contact Area Calculation",       default=0,                       description="Enables accurate contact area calculation using booleans for the cost of an slower building process. This only works correct with solids i.e. watertight and manifold objects and is therefore recommended for truss structures or steel constructions in general.")
    nonManifoldThickness = float_(name="Non-solid Thickness",             default=0.1, min=0.0, max=10,    description="Thickness for non-manifold elements (surfaces) when using accurate contact area calculation.")
    minimumElementSize = float_(name="Min. Element Size",                 default=0, min=0.0, max=10,      description="Deletes connections whose elements are below this diameter and makes them parents instead. This can be helpful for increasing performance on models with unrelevant geometric detail such as screwheads.")
    automaticMode = bool_(name="Automatic Mode",                          default=0,                       description="Enables a fully automated workflow for extremely large simulations (object count-wise) were Blender is prone to not being responsive anymore. After clicking Build these steps are being done automatically: Building of constraints, baking simulation, clearing constraint and BCB data from scene.")
    saveBackups = bool_(name="Backup",                                    default=0,                       description="Enables saving of a backup .blend file after each step for automatic mode, whereby the name of the new .blend ends with `_BCB´.")
    timeScalePeriod = int_(name="Time Scale Period",                      default=0, min=0, max=10000,     description="For baking: Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled).")
    timeScalePeriodValue = float_(name="Initial Time Scale",              default=0.001, min=0.0, max=100, description="For baking: Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime.")
    warmUpPeriod = int_(name="Warm Up Period",                            default=20, min=0, max=10000,    description="For baking: Disables breakability of constraints for an initial period of the simulation (frames). This is to prevent structural damage caused by the gravity impulse on start.")
    progrWeak = float_(name="Progr. Weakening",                           default=0, min=0.0, max=1.0,     description="Enables progressive weakening of all breaking thresholds by the specified factor per frame (starts not until timeScalePeriod and warmUpPeriod have passed). This can be used to enforce the certain collapse of a building structure after a while.")
    progrWeakLimit = int_(name="Progr. Weak. Limit",                      default=10, min=0, max=10000,    description="For progressive weakening: Limits the weakening process by the number of broken connections per frame. If the limit is exceeded weakening will be disabled for the rest of the simulation.")
    progrWeakStartFact = float_(name="Start Weakness",                    default=1, min=0.0, max=1.0,     description="Start weakness as factor all breaking thresholds will be multiplied with. This can be used to quick-change the initial thresholds without performing a full update.")
    snapToAreaOrient = bool_(name="90° Axis Snapping for Const. Orient.", default=1,                       description="Enables axis snapping based on contact area orientation for constraints rotation instead of using center to center vector alignment (old method).")
    disableCollision = bool_(name="Disable Collisions",                   default=1,                       description="Disables collisions between connected elements until breach.")
    lowerBrkThresPriority = bool_(name="Lower Strength Priority",         default=1,                       description="Gives priority to the weaker breaking threshold of two elements to be connected, if disabled the stronger value is used for the connection.")
    
    for i in range(maxMenuElementGroupItems):
        elemGrps = mem["elemGrps"]
        if i < len(elemGrps): j = i
        else: j = 0
        exec("elemGrp_%d_EGSidxName" %i +" = string_(name='Grp. Name', default=elemGrps[j][EGSidxName], description='The name of the element group.')")
        exec("elemGrp_%d_EGSidxCTyp" %i +" = int_(name='Connection Type', default=elemGrps[j][EGSidxCTyp], min=1, max=1000, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code.')")

        exec("elemGrp_%d_EGSidxBTC" %i +" = string_(name='Compressive', default=elemGrps[j][EGSidxBTC], description='Math expression for the material´s real world compressive breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTT" %i +" = string_(name='Tensile', default=elemGrps[j][EGSidxBTT], description='Math expression for the material´s real world tensile breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTS" %i +" = string_(name='Shear', default=elemGrps[j][EGSidxBTS], description='Math expression for the material´s real world shearing breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTS9" %i +" = string_(name='Shear 90°', default=elemGrps[j][EGSidxBTS9], description='Math expression for the material´s real world shearing breaking threshold with h and w swapped (rotated by 90°) in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTB" %i +" = string_(name='Bend', default=elemGrps[j][EGSidxBTB], description='Math expression for the material´s real world bending breaking threshold in Nm/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTB9" %i +" = string_(name='Bend 90°', default=elemGrps[j][EGSidxBTB9], description='Math expression for the material´s real world bending breaking threshold with h and w swapped (rotated by 90°) in Nm/mm^2 together with related geometry properties.')")

        exec("elemGrp_%d_EGSidxSStf" %i +" = float_(name='Spring Stiffness', default=elemGrps[j][EGSidxSStf], min=0.0, max=10**20, description='Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.')")
        exec("elemGrp_%d_EGSidxRqVP" %i +" = int_(name='Req. Vertex Pairs', default=elemGrps[j][EGSidxRqVP], min=0, max=100, description='How many vertex pairs between two elements are required to generate a connection.')")
        exec("elemGrp_%d_EGSidxMatP" %i +" = string_(name='Mat. Preset', default=elemGrps[j][EGSidxMatP], description='Preset name of the physical material to be used from BlenderJs internal database. See Blenders Rigid Body Tools for a list of available presets.')")
        exec("elemGrp_%d_EGSidxDens" %i +" = float_(name='Density', default=elemGrps[j][EGSidxDens], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("elemGrp_%d_EGSidxTl1D" %i +" = float_(name='1st Dist. Tol.', default=elemGrps[j][EGSidxTl1D], min=0.0, max=10.0, description='For baking: First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %).')")
        exec("elemGrp_%d_EGSidxTl1R" %i +" = float_(name='1st Rot. Tol.', default=elemGrps[j][EGSidxTl1R], min=0.0, max=pi, description='For baking: First deformation tolerance limit for angular change in radian for connection removal or plastic deformation.')")
        exec("elemGrp_%d_EGSidxTl2D" %i +" = float_(name='2nd Dist. Tol.', default=elemGrps[j][EGSidxTl2D], min=0.0, max=10.0, description='For baking: Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %).')")
        exec("elemGrp_%d_EGSidxTl2R" %i +" = float_(name='2nd Rot. Tol.', default=elemGrps[j][EGSidxTl2R], min=0.0, max=pi, description='For baking: Second deformation tolerance limit for angular change in radian for connection removal.')")
        exec("elemGrp_%d_EGSidxBevl" %i +" = bool_(name='Bevel', default=elemGrps[j][EGSidxBevl], description='Enables beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("elemGrp_%d_EGSidxScal" %i +" = float_(name='Rescale Factor', default=elemGrps[j][EGSidxScal], min=0.0, max=1, description='Applies scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("elemGrp_%d_EGSidxFacg" %i +" = bool_(name='Facing', default=elemGrps[j][EGSidxFacg], description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation).')")
        exec("elemGrp_%d_EGSidxCyln" %i +" = bool_(name='Cylindric Shape', default=elemGrps[j][EGSidxCyln], description='Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns.')")

        # Update fromula assistant submenu according to the chosen element group
        exec("assistant_menu = enum_(name='Type of Building Material', items=assistant_menu_data, default=elemGrps[j][EGSidxAsst]['ID'])")

    ###### Update menu related properties from global vars
    def props_update_menu(self):

        ### Update main class properties
        elemGrps = mem["elemGrps"]
        for i in range(len(elemGrps)):
            exec("self.elemGrp_%d_EGSidxName" %i +" = elemGrps[i][EGSidxName]")
            exec("self.elemGrp_%d_EGSidxRqVP" %i +" = elemGrps[i][EGSidxRqVP]")
            exec("self.elemGrp_%d_EGSidxMatP" %i +" = elemGrps[i][EGSidxMatP]")
            exec("self.elemGrp_%d_EGSidxDens" %i +" = elemGrps[i][EGSidxDens]")
            exec("self.elemGrp_%d_EGSidxCTyp" %i +" = elemGrps[i][EGSidxCTyp]")
            exec("self.elemGrp_%d_EGSidxBTC" %i +" = elemGrps[i][EGSidxBTC].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxBTT" %i +" = elemGrps[i][EGSidxBTT].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxBTS" %i +" = elemGrps[i][EGSidxBTS].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxBTS9" %i +" = elemGrps[i][EGSidxBTS9].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxBTB" %i +" = elemGrps[i][EGSidxBTB].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxBTB9" %i +" = elemGrps[i][EGSidxBTB9].replace('*a','')")
            exec("self.elemGrp_%d_EGSidxSStf" %i +" = elemGrps[i][EGSidxSStf]")
            exec("self.elemGrp_%d_EGSidxTl1D" %i +" = elemGrps[i][EGSidxTl1D]")
            exec("self.elemGrp_%d_EGSidxTl1R" %i +" = elemGrps[i][EGSidxTl1R]")
            exec("self.elemGrp_%d_EGSidxTl2D" %i +" = elemGrps[i][EGSidxTl2D]")
            exec("self.elemGrp_%d_EGSidxTl2R" %i +" = elemGrps[i][EGSidxTl2R]")
            exec("self.elemGrp_%d_EGSidxBevl" %i +" = elemGrps[i][EGSidxBevl]")
            exec("self.elemGrp_%d_EGSidxScal" %i +" = elemGrps[i][EGSidxScal]")
            exec("self.elemGrp_%d_EGSidxFacg" %i +" = elemGrps[i][EGSidxFacg]")
            exec("self.elemGrp_%d_EGSidxCyln" %i +" = elemGrps[i][EGSidxCyln]")
        
        # Update fromula assistant submenu according to the chosen element group
        i = self.menu_selectedElemGrp
        try: self.assistant_menu = elemGrps[i][EGSidxAsst]['ID']
        except: self.assistant_menu = "None"
        
        ### Update also the other classes properties
        props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
        props_asst_con_rei_beam.props_update_menu()
        props_asst_con_rei_wall.props_update_menu()
            
    ###### Update global vars from menu related properties
    def props_update_globals(self):

        elemGrps = mem["elemGrps"]
        for i in range(len(elemGrps)):
            elemGrps[i][EGSidxName] = eval("self.elemGrp_%d_EGSidxName" %i)
            elemGrps[i][EGSidxRqVP] = eval("self.elemGrp_%d_EGSidxRqVP" %i)
            elemGrps[i][EGSidxMatP] = eval("self.elemGrp_%d_EGSidxMatP" %i)
            elemGrps[i][EGSidxDens] = eval("self.elemGrp_%d_EGSidxDens" %i)
            elemGrps[i][EGSidxCTyp] = eval("self.elemGrp_%d_EGSidxCTyp" %i)
            elemGrps[i][EGSidxBTC] = eval("self.elemGrp_%d_EGSidxBTC" %i)
            elemGrps[i][EGSidxBTT] = eval("self.elemGrp_%d_EGSidxBTT" %i)
            elemGrps[i][EGSidxBTS] = eval("self.elemGrp_%d_EGSidxBTS" %i)
            elemGrps[i][EGSidxBTS9] = eval("self.elemGrp_%d_EGSidxBTS9" %i)
            elemGrps[i][EGSidxBTB] = eval("self.elemGrp_%d_EGSidxBTB" %i)
            elemGrps[i][EGSidxBTB9] = eval("self.elemGrp_%d_EGSidxBTB9" %i)
            elemGrps[i][EGSidxSStf] = eval("self.elemGrp_%d_EGSidxSStf" %i)
            elemGrps[i][EGSidxTl1D] = eval("self.elemGrp_%d_EGSidxTl1D" %i)
            elemGrps[i][EGSidxTl1R] = eval("self.elemGrp_%d_EGSidxTl1R" %i)
            elemGrps[i][EGSidxTl2D] = eval("self.elemGrp_%d_EGSidxTl2D" %i)
            elemGrps[i][EGSidxTl2R] = eval("self.elemGrp_%d_EGSidxTl2R" %i)
            elemGrps[i][EGSidxBevl] = eval("self.elemGrp_%d_EGSidxBevl" %i)
            elemGrps[i][EGSidxScal] = eval("self.elemGrp_%d_EGSidxScal" %i)
            elemGrps[i][EGSidxFacg] = eval("self.elemGrp_%d_EGSidxFacg" %i)
            elemGrps[i][EGSidxCyln] = eval("self.elemGrp_%d_EGSidxCyln" %i)
            # Remove surface variable if existing (will be added in setConstraintSettings()
            elemGrps[i][EGSidxBTC] = elemGrps[i][EGSidxBTC].replace('*a','')
            elemGrps[i][EGSidxBTT] = elemGrps[i][EGSidxBTT].replace('*a','')
            elemGrps[i][EGSidxBTS] = elemGrps[i][EGSidxBTS].replace('*a','')
            elemGrps[i][EGSidxBTS9] = elemGrps[i][EGSidxBTS9].replace('*a','')
            elemGrps[i][EGSidxBTB] = elemGrps[i][EGSidxBTB].replace('*a','')
            elemGrps[i][EGSidxBTB9] = elemGrps[i][EGSidxBTB9].replace('*a','')

        ### If different formula assistant ID from that stored in element group then update with defaults
        i = self.menu_selectedElemGrp
        if self.assistant_menu != elemGrps[i][EGSidxAsst]['ID']:
            # Add formula assistant settings to element group
            for formAssist in formulaAssistants:
                if self.assistant_menu == formAssist['ID']:
                    elemGrps[i][EGSidxAsst] = formAssist.copy()

        ### Update global vars also from the other classes properties
        props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
        props_asst_con_rei_beam.props_update_globals()
        props_asst_con_rei_wall.props_update_globals()        
