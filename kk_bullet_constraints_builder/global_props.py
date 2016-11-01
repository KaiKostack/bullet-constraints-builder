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
    
    int_ =    bpy.props.IntProperty 
    float_ =  bpy.props.FloatProperty
    bool_ =   bpy.props.BoolProperty
    string_ = bpy.props.StringProperty
    enum_ =   bpy.props.EnumProperty
    
    ###### Menu properties

    menu_gotPreproc =      int_(default=0)
    menu_gotConfig =       int_(default=0)
    menu_gotData =         int_(default=0)
    menu_selectedElemGrp = int_(default=0)
    submenu_advancedG =    bool_(default=0)
    submenu_advancedE =    bool_(default=0)
    submenu_preprocTools = bool_(default=0)

    ### Formula assistant
    submenu_assistant = bool_(default=0)
    submenu_assistant_advanced = bool_(default=0, name="Advanced", description="Shows advanced settings and formulas.")
    assistant_menu_data = []  # (ID, Name in menu, "", Index)
    for i in range(len(formulaAssistants)):
        assistant_menu_data.append((formulaAssistants[i]["ID"], formulaAssistants[i]["Name"], "", i))

    ### Special menu properties
    asciiExport = bool_(default=0)  # Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment).
    message = string_(default="")

    ###### Properties to be stored in blend file

    ### Preprocessing tools properties
    preprocTools_grp = bool_(default=1)
    preprocTools_mod = bool_(default=1)
    preprocTools_ctr = bool_(default=1)
    preprocTools_sep = bool_(default=1)
    preprocTools_dis = bool_(default=1)
    preprocTools_rbs = bool_(default=1)
    preprocTools_fix = bool_(default=1)
    preprocTools_gnd = bool_(default=1)
    
    preprocTools_grp_sep = string_(name="Separator",               default=':', description="Defines a key character or string to derive the group names from the object names in the scene. Example: An object name 'Columns:B4' with separator ':' will generate a group named 'Columns' containing all objects with this phrase in their names.")
    preprocTools_dis_siz = float_(name="Minimum Size Limit",       default=2.9, min=0.0, max=1000, description="Minimum dimension for an element for still being considered for subdivision, at least two dimension axis must be above this size. After discretization no element will be larger than this value anymore, although they can be smaller down to 50%.")
    preprocTools_dis_jus = bool_(name="Enable Junction Search",    default=1, description="Tries to split cornered walls at the corner rather than splitting based on object space to generate more clean shapes.")
    preprocTools_fix_nam = string_(name="Obj. Name",               default='Base', description="Enter a name (or substring) for objects that should be set to 'Passive' in rigid body settings.")
    preprocTools_fix_cac = bool_(name="Create New Foundation Objects", default=0, description="Enables generation of additional rigid body objects to serve as anchors adjacent to the selected model objects.")
    preprocTools_fix_rng = float_(name="Boundary Range",           default=0.3, min=0, max=1000, description="Internal margin in m for the model boundary box to include also objects within a certain distance from the outer border.")
    preprocTools_fix_axp = bool_(name="X+",                        default=0, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_fix_axn = bool_(name="X -",                       default=0, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_fix_ayp = bool_(name="Y+",                        default=0, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_fix_ayn = bool_(name="Y -",                       default=0, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_fix_azp = bool_(name="Z+",                        default=0, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_fix_azn = bool_(name="Z -",                       default=1, description="Enables this side of the overall model boundary for which fixed foundation objects will be created.")
    preprocTools_gnd_obj = string_(name="Obj. Name", default='Ground_Motion', description="Enter the name of a ground motion object here and the passive objects will automatically be attached to it.")
    preprocTools_gnd_nac = bool_(name="Create Artificial Earthquake Motion", default=0, description="Enables generation of artificial ground motion data based on noise functions, this can be useful if there is no real world ground motion data available.")
    preprocTools_gnd_nap = float_(name="Amplitude",   default=0.4, min=0.0, max=1000, description="Amplitude of the artificial earthquake to be generated in m (because of the random nature of the noise function this should be taken as approximation).")
    preprocTools_gnd_nfq = float_(name="Frequency",   default=0.6, min=0.0, max=1000, description="Frequency of the artificial earthquake to be generated in Hz (because of the random nature of the noise function this should be taken as approximation).")
    preprocTools_gnd_ndu = float_(name="Duration",    default=10, min=0.0, max=1000, description="Duration of the artificial earthquake to be generated in seconds.")
    preprocTools_gnd_nsd = float_(name="Random Seed", default=0, min=0.0, max=10000000, description="Seed number for the random noise function used to generate the artificial earthquake, modification will change the characteristics of the motion.")
    
    ### Element group properties
    stepsPerSecond = int_(name="Steps Per Second",                        default=300, min=1, max=32767,   description="Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable).")
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
    
    # Create element groups properties for all possible future entries (maxMenuElementGroupItems)
    for i in range(maxMenuElementGroupItems):
        elemGrps = mem["elemGrps"]
        j = 0  # Use preset 0 as dummy data 
        exec("elemGrp_%d_EGSidxName" %i +" = string_(name='Grp. Name', default=presets[j][EGSidxName], description='The name of the element group.')")
        exec("elemGrp_%d_EGSidxCTyp" %i +" = int_(name='Connection Type', default=presets[j][EGSidxCTyp], min=1, max=1000, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code.')")

        exec("elemGrp_%d_EGSidxBTC" %i +" = string_(name='Compressive', default=presets[j][EGSidxBTC], description='Math expression for the material´s real world compressive breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTT" %i +" = string_(name='Tensile', default=presets[j][EGSidxBTT], description='Math expression for the material´s real world tensile breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTS" %i +" = string_(name='Shear', default=presets[j][EGSidxBTS], description='Math expression for the material´s real world shearing breaking threshold in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTS9" %i +" = string_(name='Shear 90°', default=presets[j][EGSidxBTS9], description='Math expression for the material´s real world shearing breaking threshold with h and w swapped (rotated by 90°) in N/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTB" %i +" = string_(name='Bend', default=presets[j][EGSidxBTB], description='Math expression for the material´s real world bending breaking threshold in Nm/mm^2 together with related geometry properties.')")
        exec("elemGrp_%d_EGSidxBTB9" %i +" = string_(name='Bend 90°', default=presets[j][EGSidxBTB9], description='Math expression for the material´s real world bending breaking threshold with h and w swapped (rotated by 90°) in Nm/mm^2 together with related geometry properties.')")

        exec("elemGrp_%d_EGSidxSStf" %i +" = float_(name='Spring Stiffness', default=presets[j][EGSidxSStf], min=0.0, max=10**20, description='Stiffness to be used for Generic Spring constraints. Maximum stiffness is highly depending on the constraint solver iteration count as well, which can be found in the Rigid Body World panel.')")
        exec("elemGrp_%d_EGSidxRqVP" %i +" = int_(name='Req. Vertex Pairs', default=presets[j][EGSidxRqVP], min=0, max=100, description='How many vertex pairs between two elements are required to generate a connection.')")
        exec("elemGrp_%d_EGSidxMatP" %i +" = string_(name='Mat. Preset', default=presets[j][EGSidxMatP], description='Preset name of the physical material to be used from BlenderJs internal database. See Blenders Rigid Body Tools for a list of available presets.')")
        exec("elemGrp_%d_EGSidxDens" %i +" = float_(name='Density', default=presets[j][EGSidxDens], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("elemGrp_%d_EGSidxTl1D" %i +" = float_(name='1st Dist. Tol.', default=presets[j][EGSidxTl1D], min=0.0, max=10.0, description='For baking: First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %).')")
        exec("elemGrp_%d_EGSidxTl1R" %i +" = float_(name='1st Rot. Tol.', default=presets[j][EGSidxTl1R], min=0.0, max=pi, description='For baking: First deformation tolerance limit for angular change in radian for connection removal or plastic deformation.')")
        exec("elemGrp_%d_EGSidxTl2D" %i +" = float_(name='2nd Dist. Tol.', default=presets[j][EGSidxTl2D], min=0.0, max=10.0, description='For baking: Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %).')")
        exec("elemGrp_%d_EGSidxTl2R" %i +" = float_(name='2nd Rot. Tol.', default=presets[j][EGSidxTl2R], min=0.0, max=pi, description='For baking: Second deformation tolerance limit for angular change in radian for connection removal.')")
        exec("elemGrp_%d_EGSidxBevl" %i +" = bool_(name='Bevel', default=presets[j][EGSidxBevl], description='Enables beveling for elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("elemGrp_%d_EGSidxScal" %i +" = float_(name='Rescale Factor', default=presets[j][EGSidxScal], min=0.0, max=1, description='Applies scaling factor on elements to avoid `Jenga´ effect (uses hidden collision meshes).')")
        exec("elemGrp_%d_EGSidxFacg" %i +" = bool_(name='Facing', default=presets[j][EGSidxFacg], description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation).')")
        exec("elemGrp_%d_EGSidxCyln" %i +" = bool_(name='Cylindric Shape', default=presets[j][EGSidxCyln], description='Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns.')")

        # Update fromula assistant submenu according to the chosen element group
        exec("assistant_menu = enum_(name='Type of Building Material', items=assistant_menu_data, default=presets[j][EGSidxAsst]['ID'])")

    ###### Update menu properties from global vars
    def props_update_menu(self):

        ### Update main class properties
        elemGrps = mem["elemGrps"]
        if len(elemGrps) > 0:
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
            
    ###### Update global vars from menu properties
    def props_update_globals(self):

        elemGrps = mem["elemGrps"]
        if len(elemGrps) > 0:
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
