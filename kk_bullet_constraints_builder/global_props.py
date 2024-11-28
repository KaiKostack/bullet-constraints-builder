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
# Copyright (C) 2015-2021 Kai Kostack
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
import global_vars

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

def updGlob(self, context):

    props = context.window_manager.bcb
    # For internal loading of settings into the properties we need to lock the updating event handler
    if not props.update_lock:
        ###### Update global vars from menu properties
        props.props_update_globals()
    
########################################

class bcb_props(bpy.types.PropertyGroup):
    
    int_ =    bpy.props.IntProperty 
    float_ =  bpy.props.FloatProperty
    bool_ =   bpy.props.BoolProperty
    string_ = bpy.props.StringProperty
    enum_ =   bpy.props.EnumProperty
    
    ###### Menu properties (volatile)

    update_lock           = bool_(default=0)
    menu_init             = bool_(default=1)
    menu_gotConfig        = int_(default=0)
    menu_gotData          = int_(default=0)
    menu_selectedElemGrp  = int_(default=0)

    ### Formula assistant
    submenu_assistant_advanced = bool_(default=0, name="Advanced", update=updGlob, description="Shows advanced settings and formulas")
    assistant_menu_data = []  # (ID, Name in menu, "", Index)
    for i in range(len(formulaAssistants)):
        assistant_menu_data.append((formulaAssistants[i]["ID"], formulaAssistants[i]["Name"], "", i))

    ### Special menu properties
    asciiExport = bool_(default=0)  # Exports all constraint data to an ASCII text file instead of creating actual empty objects (only useful for developers at the moment).
    message = string_(default="")

    ###### Properties to be stored in blend file

    ### Preprocessing Tools
    preprocTools_aut = bool_(default=1, name="Run On Automatic Mode", update=updGlob, description="Enables that preprocessing will be performed on Automatic Mode. To avoid accidental double execution, this will be disabled whenever a preprocessing tool is activated manually, but it can be activated again at any time")

    preprocTools_rps = bool_(default=1)
    preprocTools_rps_nam = string_(name="Script File",             default='', update=updGlob, description="Enter the filename of an existing Python script")

    preprocTools_grp = bool_(default=1)
    preprocTools_grp_sep = string_(name="Separator",               default=':', update=updGlob, description="Defines a key character or string to derive the group names from the object names in the scene. Example: An object name 'Columns:B4' with separator ':' will generate a group named 'Columns' containing all objects with this phrase in their names")
    preprocTools_grp_occ = bool_(name="First Occurrence",          default=1, update=updGlob, description="Enables first occurrence search of the separator within an element name for cases when there are more than one separator included, if disabled the last occurrence is used")

    preprocTools_sep = bool_(default=1)

    preprocTools_mod = bool_(default=1)

    preprocTools_rem = bool_(default=0)

    preprocTools_ctr = bool_(default=1)

    preprocTools_sep2 = bool_(default=1)

    preprocTools_dis = bool_(default=1)
    preprocTools_dis_siz = float_(name="Minimum Size Limit",       default=2.9, min=0.0, max=1000, update=updGlob, description="Discretization size in m this tool tries to reach by discretization. To enforce regularity at all times, elements afterwards can deviate in size to some extent from the target size. For booleans (default method): The minimum dimension value serves as limit for an element still being considered for subdivision, at least two dimension axis must be above this size. After discretization no element will be larger than this value anymore, although they can be smaller up to 50%")
    preprocTools_dis_cel = bool_(name="Use Voxel Method (Faster)", default=0, update=updGlob, description="Enables the voxel based discretizaton method and geometry is converted into cuboid-shaped cells. While this method has the disadvantage that it can't keep mesh details such as curved surfaces, round columns or mural reliefs, it is very fast compared to the default boolean based method. Also note that this method is limited to odd subdivision level numbers [1,3,5,7..], so you basically can't split an element into two for instance but only into three, five and so on")
    preprocTools_dis_bis = bool_(name="Use Bisect Method (Fastest)", default=0, update=updGlob, description="Enables the bisect based discretizaton method. While this method has the disadvantage that filling holes can fail on more complex shapes, it is extremely fast compared to the default boolean based method and is more robust on non-manifold geometry")
    preprocTools_dis_jus = bool_(name="Enable Junction Search",    default=1, update=updGlob, description="Tries to split cornered walls at the corner rather than splitting based on object space to generate more clean shapes")

    preprocTools_mod2 = bool_(default=0)

    preprocTools_rem2 = bool_(default=0)

    preprocTools_rbs = bool_(default=1)

    preprocTools_int = bool_(default=1)
    preprocTools_int_bol = bool_(name="Use Boolean Subtraction",   default=1, update=updGlob, description="Uses boolean operations to resolve overlapping elements. Their geometries will be subtracted from each other and the collision shapes will be switched to 'Mesh'. (For accurate simulations it is strongly recommended to resolve such intersections manually and leave this option disabled.)")

    preprocTools_fix = bool_(default=1)
    preprocTools_fix_nam = string_(name="Obj. Name",               default='Foundation', update=updGlob, description="Enter a name (or substring) for objects which should be set to 'Passive' in rigid body settings")
    preprocTools_fix_cac = bool_(name="Create New Foundation Objects", default=1, update=updGlob, description="Enables generation of additional rigid body objects to serve as anchors adjacent to the selected model objects")
    preprocTools_fix_rng = float_(name="Boundary Range",           default=0.1, min=0, max=1000, update=updGlob, description="Internal margin in m for the model boundary box to include also objects within a certain distance from the outer border. This value should always stay smaller than Discretization Size divided by 2 because otherwise foundation elements can overlap user elements")
    preprocTools_fix_axp = bool_(name="X+",                        default=0, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")
    preprocTools_fix_axn = bool_(name="X -",                       default=0, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")
    preprocTools_fix_ayp = bool_(name="Y+",                        default=0, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")
    preprocTools_fix_ayn = bool_(name="Y -",                       default=0, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")
    preprocTools_fix_azp = bool_(name="Z+",                        default=0, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")
    preprocTools_fix_azn = bool_(name="Z -",                       default=1, update=updGlob, description="Enables this side of the overall model boundary for which fixed foundation objects will be created")

    preprocTools_gnd = bool_(default=1)
    preprocTools_gnd_obj = string_(name="Ground Object",           default='Ground_Motion', update=updGlob, description="Enter the name of a ground object here and the passive foundation objects will automatically be attached to it. If it is not existing it will be created at the underside of the active rigid body boundary box")
    preprocTools_gnd_obm = string_(name="Motion Object",           default='Motion_Data', update=updGlob, description="Enter the name of an optional motion data object here and the ground object will automatically be attached to it. This can be useful in case animation data should be manageable completely separate from the ground object")
    preprocTools_gnd_nac = bool_(name="Create Artificial Earthquake Motion", default=0, update=updGlob, description="Enables generation of artificial ground motion data based on noise functions, this can be useful if there is no real world ground motion data available")
    preprocTools_gnd_nap = float_(name="Amplitude",                default=1, min=0.0, max=1000, update=updGlob, description="Amplitude of the artificial earthquake to be generated in m (because of the random nature of the noise function this should be taken as approximation)")
    preprocTools_gnd_nfq = float_(name="Frequency",                default=0.5, min=0.0, max=1000, update=updGlob, description="Frequency of the artificial earthquake to be generated in Hz (because of the random nature of the noise function this should be taken as approximation)")
    preprocTools_gnd_ndu = float_(name="Duration",                 default=10, min=0.0, max=1000, update=updGlob, description="Duration of the artificial earthquake to be generated in seconds")
    preprocTools_gnd_nsd = float_(name="Random Seed",              default=0, min=0.0, max=10000000, update=updGlob, description="Seed number for the random noise function used to generate the artificial earthquake, modification will change the characteristics of the motion")
    preprocTools_gnd_nam = string_(name="CSV File",                default='', update=updGlob, description="Enter filename or search for earthquake time history file as plain ASCII text with comma-separated values (.csv). File structure: 4 columns: t [s], X [m/s²], Y [m/s²], Z [m/s²]. Lines starting with '#' are skipped")

    ### Postprocessing Tools
    postprocTools_aut = bool_(default=0, name="Run On Automatic Mode", update=updGlob, description="Enables that postprocessing will be performed on Automatic Mode. To avoid accidental double execution, this will be disabled whenever a postprocessing tool is activated manually, but it can be activated again at any time")

    postprocTools_lox = bool_(default=1)
    postprocTools_lox_elm = string_(name="Element",       default='Cube', update=updGlob, description="Enter the name of an element for which the location time history should be exported")
    postprocTools_lox_nam = string_(name="CSV Folder",    default='', update=updGlob, description="Enter a path or search for folder for data export as plain ASCII text with comma-separated values (.csv)")

    postprocTools_fcx = bool_(default=1)
    postprocTools_fcx_con = string_(name="Constraint",    default='Con.000', update=updGlob, description="Enter the name of a constraint for which the location time history should be exported")
    postprocTools_fcx_nam = string_(name="CSV Folder",    default='', update=updGlob, description="Enter a path or search for folder for data export as plain ASCII text with comma-separated values (.csv)")

    postprocTools_fcv = bool_(default=1)
    postprocTools_fcv_con = string_(name="Range Object",  default='Visualization Limiter', update=updGlob, description="Enter the name of a helper object whose dimensions will be used to define for which connections forces should be visualized, i.e. all within its boundary range. For instance an empty object can be placed and scaled accordingly to fit a specific area of interest")
    postprocTools_fcv_frm = int_(name="Frame",            default=80, min=0, max=32767,   update=updGlob, description="Frame number at which the visualization snap-shot of forces will be taken")
    postprocTools_fcv_nbt = bool_(name="Normalize To Breaking Threshold", default=1, update=updGlob, description="Normalizes the visualizer to the breaking thresholds of the constraints, so that red color always means close to failure")
    postprocTools_fcv_max = float_(name="Maximum",        default=20, min=0.0, max=10000000, update=updGlob, description="Maximum force per mm² to be expected, actual forces will be normalized accordingly. This will only influence the appearance of the visualizer, but the readout value stored within the visualizer's properties will not be modified")
    postprocTools_fcv_pas = bool_(name="Limit To Foundation Connections", default=0, update=updGlob, description="Limits visualization to connections with foundation / passive elements")

    postprocTools_cav = bool_(default=1)
    postprocTools_cav_siz = float_(name="Cell Size",      default=.3, min=0.0, max=100, update=updGlob, description="Cell size for cavity detection algorithm to consider empty spaces (smaller values are more accurate but take longer to compute)")

    postprocTools_rps = bool_(default=1)
    postprocTools_rps_nam = string_(name="Script File",   default='', update=updGlob, description="Enter the filename of an existing Python script")

    ### General
    stepsPerSecond        = int_(name="Steps Per Second",         default=200, min=1, max=32767,   update=updGlob, description="Number of simulation steps taken per second (higher values are more accurate but slower and can also be more instable)")
    solverIterations      = int_(name="Solver Iterations",        default=100, min=1, max=32767,   update=updGlob, description="Number of constraint solver iterations per simulation step (higher values are more accurate but slower)")
    constraintUseBreaking = bool_(name="Enable Breaking",         default=1,                       update=updGlob, description="Enables breaking for all constraints")
    passiveUseBreaking    = bool_(name="Enbl. Brk. Passive",      default=1,                       update=updGlob, description="Enables breaking for active to passive connections. Usually this should stay enabled but in some cases the evaluation of forces in active-passive connections can be more inaccurate than those of active-active connections, then it may help to disable breaking of such connections altogether")
    connectionCountLimit  = int_(name="Con. Count Limit",         default=0, min=0, max=100000,    update=updGlob, description="Maximum count of connections per object pair (0 = disabled)")
    searchDistance        = float_(name="Search Distance",        default=0.02, min=0.0, max=1000, update=updGlob, description="Search distance to neighbor element boundary box in m")
    searchDistanceMesh    = float_(name="Mesh Search Distance",   default=0.02, min=0.0, max=1000, update=updGlob, description="Search distance to neighbor element mesh geometry in m")
    searchDistanceFallback = bool_(name="Fallback",               default=1,                       update=updGlob, description="In case no geometry could be detected within mesh search distance while the neighbor element's boundary box is still within range this enables a fallback using the intersection of the boundary boxes as contact area instead of the mesh surface. If disabled contact area will remain zero and no connection will be created in that case")
    clusterRadius         = float_(name="Cluster Radius",         default=0, min=0.0, max=1000,    update=updGlob, description="Radius for bundling close constraints into clusters in m (0 = clusters disabled)")
    alignVertical         = float_(name="Vertical Alignment",     default=0, min=0.0, max=1.0,     update=updGlob, description="Enables a vertical alignment multiplier for connection type 4 or above instead of using unweighted center to center orientation (0 = disabled, 1 = fully vertical)")
    useAccurateArea       = bool_(name="Accur. Contact Area Calculation", default=1,               update=updGlob, description="Enables accurate contact area calculation. It is derived indirectly by dividing the calculated geometry volume divided by the element length")
    rebarMesh             = bool_(name="Rebar Mesh",              default=0,                       update=updGlob, description="Enables creation of a rebar mesh on build or export execution using the settings from the Formula Assistant. This mesh is meant for diagnostic purposes only, it is not required nor used for the simulation. It is also not very accurate for very small elements as the rebar count is converted from the definition to the actual element size with a minimum limit of 4 bars per element")
    surfaceThickness      = float_(name="Surface Thickness",      default=0, min=0.0, max=10,      update=updGlob, description="Artificial thickness for non-manifold elements (surfaces). If the element is solid this value will be added as extra margin to the detected contact area")
    surfaceForced         = bool_(name="Treat Solids As Surfaces",default=0,                       update=updGlob, description="Enforces treatment of solid elements as surface elements. This has impact on discretization and mass calculation")
    minimumElementSize    = float_(name="Min. Element Size",      default=0, min=0.0, max=10,      update=updGlob, description="Deletes connections whose elements are below this diameter and makes them parents instead. This can be helpful for increasing performance on models with unrelevant geometric detail such as screwheads")
    automaticMode         = bool_(name="Automatic Mode",          default=0,                       update=updGlob, description="Enables a fully automated workflow for extremely large simulations (object count-wise) were Blender is prone to not being responsive anymore. After clicking Bake (not Build) these steps are being done automatically: Building of constraints, baking simulation, clearing constraint and BCB data from scene")
    saveBackups           = bool_(name="Backup",                  default=0,                       update=updGlob, description="Enables saving of a backup .blend file after each step for automatic mode, whereby the name of the new .blend ends with `_BCB´")
    timeScalePeriod       = int_(name="Time Scale Period",        default=0, min=0, max=10000,     update=updGlob, description="Use a different time scale for an initial period of the simulation until this many frames has passed (0 = disabled)")
    timeScalePeriodValue  = float_(name="Initial Time Scale",     default=0.001, min=0.0, max=100, update=updGlob, description="Use this time scale for the initial period of the simulation, after that it is switching back to default time scale and updating breaking thresholds accordingly during runtime")
    warmUpPeriod          = int_(name="Warm Up Period",           default=20, min=0, max=10000,    update=updGlob, description="Disables breakability of constraints for an initial period of the simulation (frames). This is to prevent structural damage caused by the gravity impulse on start")
    progrWeak             = float_(name="Progr. Weakening",       default=0, min=0.0, max=1.0,     update=updGlob, description="Enables progressive weakening of all breaking thresholds by the specified factor per frame like 0.02 (starts not until timeScalePeriod and warmUpPeriod have passed). This can be used to enforce the certain collapse of a building structure after a while")
    progrWeakLimit        = int_(name="Progr. Weak. Limit",       default=10, min=0, max=10000,    update=updGlob, description="For progressive weakening: Limits the weakening process by the number of broken connections per frame. If the limit is exceeded weakening will be disabled for the rest of the simulation")
    progrWeakStartFact    = float_(name="Start Weakness",         default=1, min=0.0, max=1.0,     update=updGlob, description="Start weakness as factor all breaking thresholds will be multiplied with. This can be used to quick-change the initial thresholds without performing a full update")
    snapToAreaOrient      = bool_(name="90° Axis Snapping for Const. Orient.", default=1,          update=updGlob, description="Enables axis snapping based on contact area orientation for constraints rotation instead of using center to center vector alignment (old method)")
    disableCollision      = bool_(name="Disable Collisions",      default=1,                       update=updGlob, description="Disables collisions between connected elements until breach")
    disableCollisionPerm  = bool_(name="Dis. Col. Permanently",   default=0,                       update=updGlob, description="Disables collisions between initially connected elements permanently. This can help to make simulations with intersecting geometry more stable at the cost of accuracy")
    lowerBrkThresPriority = bool_(name="Lower Strength Priority", default=1,                       update=updGlob, description="Gives priority to the weaker breaking threshold of two elements from different element groups with same Priority value to be connected, if disabled the stronger value is used for the connection")
    dampRegObj            = string_(name="Damping Region Object", default="Waterbody",             update=updGlob, description="Enter the name of an object to define the region in which the damping effects should be simulated. This feature is intended to simulate environments with a higher viscosity than air, e.g. water. Note: The element groups must be activated individually for the effect to take effect. Multiple damping regions are supported if they contain this string in the name")
    dampRegLin            = float_(name="Linear Damping",         default=0.9, min=0.0, max=1.0,   update=updGlob, description="For a Damping Region: Amount of linear velocity that is lost over time")
    dampRegAng            = float_(name="Angular Damping",        default=0.1, min=0.0, max=1.0,   update=updGlob, description="For a Damping Region: Amount of angular velocity that is lost over time")
    detonatorObj          = string_(name="Detonator Object",      default="Detonator",             update=updGlob, description="Enter name of an object to be used to simulate the effects of an explosion. This feature replicates the damage caused by such an event by weakening the constraints within range of the object. It is recommended to use an Empty object with a sphere shape for this. The damage is calculated as gradient of the distance mapped to the size, from 200% weakening at center to 0% at boundary. Multiple detonators are supported if they contain this string in the name")
    detonatorMul          = float_(name="Multiplier",             default=1, min=0.0, max=1000.0,  update=updGlob, description="Multiplier the weakening gradient strength derived from the Detonator object space will be multiplied with (not used for Advanced Detonator)")
    detonatorMax          = float_(name="Maximum",                default=1, min=0.0, max=1.0,     update=updGlob, description="Detonator influence maximum to limit the weakening (not used for Advanced Detonator)")
    detonAdvanced         = bool_(name="Advanced Detonator",      default=0,                       update=updGlob, description="Enables advanced detonation blast wave simulation using animated force fields and the Time Scale Period functionality. If enabled the detonator object will be used as origin to place the force fields but is ignored otherwise")
    detonRayDist          = float_(name="Max. Ray Distance",      default=10, min=0.0, max=10000,  update=updGlob, description="Maximum distance in m for ray casting for confined space detection")
    detonDeflection       = float_(name="Deflection Multiplier",  default=0, min=0.0, max=1000,    update=updGlob, description="Detonation deflection multiplier for open/confined spaces. Larger values will increase the blast wave impact on revealed structures such as outside walls compared to protected elements inside of buildings (0 = no difference)")
    detonExplosiveMass    = float_(name="Explosive Mass",         default=250, min=0.0, max=1000000000000, update=updGlob, description="Mass of the explosive in kg TNT equivalent")
    detonBlastWaveVel     = float_(name="Blast Wave Velocity",    default=6900, min=0.0, max=1000000, update=updGlob, description="Velocity with which the blast wave is traveling in m/s (depends on frame rate)")
    detonPullBackDelay    = int_(name="Pull Back Delay",          default=2, min=0, max=10000,    update=updGlob, description="Delay in frames until the negative pressure wave follows the positive one (pressure will be divided by this value to keep overall pressure consistent)")
    detonGroundReflect    = bool_(name="Ground Reflection",       default=0,                      update=updGlob, description="Enables reflection of the blast wave from the ground by adding duplicate force fields beneath the ground level")
    
    ### Element group properties
    # Create element groups properties for all possible future entries (maxMenuElementGroupItems)
    for i in range(maxMenuElementGroupItems):
        elemGrps = global_vars.elemGrps
        j = 0  # Use preset 0 as dummy data 
        exec("elemGrp_%d_EGSidxName" %i +" = string_(name='Grp. Name', default=presets[j][EGSidxName], update=updGlob, description='The name of the chosen element group')")
        exec("elemGrp_%d_EGSidxCTyp" %i +" = int_(name='Connection Type', default=presets[j][EGSidxCTyp], min=0, max=1000, update=updGlob, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code')")

        exec("elemGrp_%d_EGSidxBTC" %i +" = string_(name='Compressive', default=presets[j][EGSidxBTC], update=updGlob, description='Math expression for the material´s real world compressive breaking threshold in N/mm^2 together with related geometry properties')")
        exec("elemGrp_%d_EGSidxBTT" %i +" = string_(name='Tensile', default=presets[j][EGSidxBTT], update=updGlob, description='Math expression for the material´s real world tensile breaking threshold in N/mm^2 together with related geometry properties')")
        exec("elemGrp_%d_EGSidxBTS" %i +" = string_(name='Shear', default=presets[j][EGSidxBTS], update=updGlob, description='Math expression for the material´s real world shearing breaking threshold in N/mm^2 together with related geometry properties')")
        exec("elemGrp_%d_EGSidxBTS9" %i +" = string_(name='Shear 90°', default=presets[j][EGSidxBTS9], update=updGlob, description='Math expression for the material´s real world shearing breaking threshold with h and w swapped (rotated by 90°) in N/mm^2 together with related geometry properties. If this field is empty the above shearing breaking threshold is used')")
        exec("elemGrp_%d_EGSidxBTB" %i +" = string_(name='Bend', default=presets[j][EGSidxBTB], update=updGlob, description='Math expression for the material´s real world bending breaking threshold in Nm/mm^2 together with related geometry properties')")
        exec("elemGrp_%d_EGSidxBTB9" %i +" = string_(name='Bend 90°', default=presets[j][EGSidxBTB9], update=updGlob, description='Math expression for the material´s real world bending breaking threshold with h and w swapped (rotated by 90°) in Nm/mm^2 together with related geometry properties. If this field is empty the above bending breaking threshold is used')")
        exec("elemGrp_%d_EGSidxBTP" %i +" = string_(name='Plastic', default=presets[j][EGSidxBTP], update=updGlob, description='Math expression for the material´s real world ultimate tensile breaking threshold in N/mm^2. Also the stiffness for Generic Spring constraints is derived from that value')")
        exec("elemGrp_%d_EGSidxBTPL" %i +" = float_(name='Plastic Length', default=presets[j][EGSidxBTPL], min=0.0, max=10**15, update=updGlob, description='Length of the springs used for plastic deformation in m. If 0 is entered the distance between the element´s centroids is used (default)')")
        exec("elemGrp_%d_EGSidxBTX" %i +" = float_(name='Breaking Threshold Multiplier', default=presets[j][EGSidxBTX], min=0.0, max=1000000000, update=updGlob, description='Multiplier to be applied on all breaking thresholds for constraint building. This can be useful for quickly weaken or strengthen a given element group without changing the original settings')")
        exec("elemGrp_%d_EGSidxBTI" %i +" = float_(name='Intercomponent Multiplier', default=presets[j][EGSidxBTI], min=0.0, max=1000000000, update=updGlob, description='Multiplier to be applied on breaking thresholds that connect only different components (= multiple elements in one unit) within an element group. This can be useful to artificially weaken the strength between components')")

        exec("elemGrp_%d_EGSidxBLC" %i +" = float_(name='Compressive', default=presets[j][EGSidxBLC], min=0.0, max=1000, update=updGlob, description='Maximum distance in m through which any connected element may be moved in compressive direction without applying force or motion to the next element')")
        exec("elemGrp_%d_EGSidxBLT" %i +" = float_(name='Tensile', default=presets[j][EGSidxBLT], min=0.0, max=1000, update=updGlob, description='Maximum distance in m through which any connected element may be moved in tensile direction without applying force or motion to the next element')")
        exec("elemGrp_%d_EGSidxBLS" %i +" = float_(name='Shear', default=presets[j][EGSidxBLS], min=0.0, max=1000, update=updGlob, description='Maximum distance in m through which any connected element may be moved in shearing direction without applying force or motion to the next element')")
        exec("elemGrp_%d_EGSidxBLS9" %i +" = float_(name='Shear 90°', default=presets[j][EGSidxBLS9], min=0.0, max=1000, update=updGlob, description='Maximum distance in m through which any connected element may be moved in shearing direction, with h and w swapped (rotated by 90°), without applying force or motion to the next element')")
        exec("elemGrp_%d_EGSidxBLB" %i +" = float_(name='Bend', default=presets[j][EGSidxBLB], min=0.0, max=1000, update=updGlob, description='Maximum angle in rad through which any connected element may be moved in bending direction without applying force or motion to the next element')")
        exec("elemGrp_%d_EGSidxBLB9" %i +" = float_(name='Bend 90°', default=presets[j][EGSidxBLB9], min=0.0, max=1000, update=updGlob, description='Maximum angle in rad through which any connected element may be moved in bending direction, with h and w swapped (rotated by 90°), without applying force or motion to the next element')")

        exec("elemGrp_%d_EGSidxRqVP" %i +" = int_(name='Req. Vertex Pairs', default=presets[j][EGSidxRqVP], min=0, max=100, update=updGlob, description='How many vertex pairs between two elements are required to generate a connection')")
        exec("elemGrp_%d_EGSidxMatP" %i +" = string_(name='Mat. Preset', default=presets[j][EGSidxMatP], update=updGlob, description='Preset name of the physical material to be used from Blender´s internal database. See Blender´s Rigid Body Tools for a list of available presets')")
        exec("elemGrp_%d_EGSidxDens" %i +" = float_(name='Density', default=presets[j][EGSidxDens], min=0.0, max=10000000, update=updGlob, description='Custom density value to use instead of material preset in kg/m^3 (0 = disabled)')")
        exec("elemGrp_%d_EGSidxLoad" %i +" = float_(name='Live Load', default=presets[j][EGSidxLoad], min=0.0, max=10000000, update=updGlob, description='Additional weight representing live load which will be added to the total mass with respect to floor area (kg/m^2)')")

        exec("elemGrp_%d_EGSidxTl1D" %i +" = float_(name='1st Dist. Tol.', default=presets[j][EGSidxTl1D], min=-1.0, max=10.0, update=updGlob, description='First deformation tolerance limit for distance change in percent for connection removal or plastic deformation (1.00 = 100 %)')")
        exec("elemGrp_%d_EGSidxTl1R" %i +" = float_(name='1st Rot. Tol.', default=presets[j][EGSidxTl1R], min=-1.0, max=pi, update=updGlob, description='First deformation tolerance limit for angular change in radian for connection removal or plastic deformation')")
        exec("elemGrp_%d_EGSidxTl2D" %i +" = float_(name='2nd Dist. Tol.', default=presets[j][EGSidxTl2D], min=-1.0, max=10.0, update=updGlob, description='Second deformation tolerance limit for distance change in percent for connection removal (1.00 = 100 %). The Formula Assistant might calculate this setting automatically on evaluation, it will appear greyed out then')")
        exec("elemGrp_%d_EGSidxTl2R" %i +" = float_(name='2nd Rot. Tol.', default=presets[j][EGSidxTl2R], min=-1.0, max=pi, update=updGlob, description='Second deformation tolerance limit for angular change in radian for connection removal. The Formula Assistant might set this to 0 which means that this tolerance will be calculated later during the constraint building phase individually for each connection using Formula Assistant settings, there is no need to change it back then')")
        exec("elemGrp_%d_EGSidxPrio" %i +" = int_(name='Connection Priority', default=presets[j][EGSidxPrio], min=1, max=9, update=updGlob, description='Changes the connection priority for this element group which will override that the weaker breaking threshold of two elements is preferred for an connection. Lower Strength Priority has similar functionality but works on all groups, however, it is ignored if the priority here is different for a particular connection')")
        exec("elemGrp_%d_EGSidxFric" %i +" = float_(name='Friction', default=presets[j][EGSidxFric], min=0.0, max=100000, update=updGlob, description='Coefficient of friction for the given material (dimensionless)')")
        exec("elemGrp_%d_EGSidxBlnc" %i +" = float_(name='Balance Masses', default=presets[j][EGSidxBlnc], min=0.0, max=1.0, update=updGlob, description='Factor to balance the masses of elements within this group. A value of 1 assigns the same mass to each element, regardless of size, while maintaining the total mass of the group. This can be useful for force fields that require uniform element masses. A value of 0 (default) calculates masses proportionally based on the elements´ volume')")
        exec("elemGrp_%d_EGSidxIter" %i +" = int_(name='Solver Iterations Override', default=presets[j][EGSidxIter], min=0, max=100000, update=updGlob, description='Overrides the Constraint Solver Iterations value of the scene for constraints of this element group if set to a value greater 0. Higher numbers can help to reduce solver induced deformation on elements bearing extreme loads')")
        exec("elemGrp_%d_EGSidxSDFl" %i +" = bool_(name='Search Dist. Fallback', default=presets[j][EGSidxSDFl], update=updGlob, description='In case no geometry could be detected within mesh search distance while the neighbor element´s boundary box is still within range this enables a fallback using the intersection of the boundary boxes as contact area instead of the mesh surface. If disabled contact area will remain zero and no connection will be created in that case')")
        exec("elemGrp_%d_EGSidxMCTh" %i +" = bool_(name='Mohr-Coulomb Theory', default=presets[j][EGSidxMCTh], update=updGlob, description='Enables the calculation of shear and bending strength using the Mohr-Coulomb theory and makes it stress-related. This method is recommended for masonry structures in earthquake scenarios. Note that the Multiplier setting is also applied to the strength increase')")
        exec("elemGrp_%d_EGSidxScal" %i +" = float_(name='Rescale Factor', default=presets[j][EGSidxScal], min=0.0, max=10.0, update=updGlob, description='Applies scaling factor on elements to avoid `Jenga´ effect (undesired stability increase caused by incompressible rigid bodies). This has no influence on breaking threshold and mass calculations')")
        exec("elemGrp_%d_EGSidxNoHo" %i +" = bool_(name='No Horizontal Connections', default=presets[j][EGSidxNoHo], update=updGlob, description='Removes horizontal connections between elements of different element groups. This can be useful for masonry walls touching a framing structure without a particular fixation')")
        exec("elemGrp_%d_EGSidxNoCo" %i +" = bool_(name='No Connections At All', default=presets[j][EGSidxNoCo], update=updGlob, description='Removes connections between elements of different element groups if priorities of the groups are equal, only when priorities are different then this setting will be ignored. This can be useful for rigs with predefined constraints where groups should stay completely detached from another even when they are actually touching or overlapping')")
        exec("elemGrp_%d_EGSidxBevl" %i +" = bool_(name='Bevel', default=presets[j][EGSidxBevl], update=updGlob, description='Enables beveling for elements to avoid `Jenga´ effect (undesired stability increase caused by incompressible rigid bodies). This uses hidden collision meshes and has no influence on breaking threshold and mass calculations')")
        exec("elemGrp_%d_EGSidxFacg" %i +" = bool_(name='Facing', default=presets[j][EGSidxFacg], update=updGlob, description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation)')")
        exec("elemGrp_%d_EGSidxCyln" %i +" = bool_(name='Cylindric Shape', default=presets[j][EGSidxCyln], update=updGlob, description='Interpret connection area as round instead of rectangular (ar = a *pi/4). This can be useful when you have to deal with cylindrical columns')")
        exec("elemGrp_%d_EGSidxDCor" %i +" = bool_(name='Displ. Correction', default=presets[j][EGSidxDCor], update=updGlob, description='Enables the correction of initial displacements. This can compensate for sagging structures such as bridges that would otherwise require a very high solver step count to be straight. To do this, the simulation must be run twice. On the first run, the displacements are saved into an external file when the warm-up period ends. In the second run (rebuilding required), the differences are integrated into the mesh. Delete the external file to reset')")
        exec("elemGrp_%d_EGSidxDClP" %i +" = bool_(name='Dis. Col. Permanently', default=presets[j][EGSidxDClP], update=updGlob, description='Disables collisions between initially connected elements of this element group permanently (overrides global setting)')")
        exec("elemGrp_%d_EGSidxDmpR" %i +" = bool_(name='Damp. Region', default=presets[j][EGSidxDmpR], update=updGlob, description='Enables the Damping Region feature for this element group. Refer to Advanced Global Settings to define boundary objects and damping parameters')")

        # Update fromula assistant submenu according to the chosen element group
        exec("assistant_menu = enum_(name='Type of Building Material', items=assistant_menu_data, default=presets[j][EGSidxAsst]['ID'], update=updGlob)")

    ###### Update menu properties from global vars
    def props_update_menu(self):

        # Update main class properties
        elemGrps = global_vars.elemGrps

        if len(elemGrps) > 0:
            self.update_lock = 1  # Suppress automatic updating to set a new property value

            for i in range(len(elemGrps)):
                exec("self.elemGrp_%d_EGSidxName" %i +" = elemGrps[i][EGSidxName]")
                exec("self.elemGrp_%d_EGSidxCTyp" %i +" = elemGrps[i][EGSidxCTyp]")
                exec("self.elemGrp_%d_EGSidxBTC" %i +" = elemGrps[i][EGSidxBTC].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTT" %i +" = elemGrps[i][EGSidxBTT].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTS" %i +" = elemGrps[i][EGSidxBTS].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTS9" %i +" = elemGrps[i][EGSidxBTS9].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTB" %i +" = elemGrps[i][EGSidxBTB].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTB9" %i +" = elemGrps[i][EGSidxBTB9].replace('*a','')")
                exec("self.elemGrp_%d_EGSidxBTP" %i +" = elemGrps[i][EGSidxBTP]")
                exec("self.elemGrp_%d_EGSidxBTPL" %i +" = elemGrps[i][EGSidxBTPL]")
                exec("self.elemGrp_%d_EGSidxBTX" %i +" = elemGrps[i][EGSidxBTX]")
                exec("self.elemGrp_%d_EGSidxBTI" %i +" = elemGrps[i][EGSidxBTI]")
                exec("self.elemGrp_%d_EGSidxBLC" %i +" = elemGrps[i][EGSidxBLC]")
                exec("self.elemGrp_%d_EGSidxBLT" %i +" = elemGrps[i][EGSidxBLT]")
                exec("self.elemGrp_%d_EGSidxBLS" %i +" = elemGrps[i][EGSidxBLS]")
                exec("self.elemGrp_%d_EGSidxBLS9" %i +" = elemGrps[i][EGSidxBLS9]")
                exec("self.elemGrp_%d_EGSidxBLB" %i +" = elemGrps[i][EGSidxBLB]")
                exec("self.elemGrp_%d_EGSidxBLB9" %i +" = elemGrps[i][EGSidxBLB9]")
                exec("self.elemGrp_%d_EGSidxRqVP" %i +" = elemGrps[i][EGSidxRqVP]")
                exec("self.elemGrp_%d_EGSidxMatP" %i +" = elemGrps[i][EGSidxMatP]")
                exec("self.elemGrp_%d_EGSidxDens" %i +" = elemGrps[i][EGSidxDens]")
                exec("self.elemGrp_%d_EGSidxLoad" %i +" = elemGrps[i][EGSidxLoad]")

                exec("self.elemGrp_%d_EGSidxTl1D" %i +" = elemGrps[i][EGSidxTl1D]")
                exec("self.elemGrp_%d_EGSidxTl1R" %i +" = elemGrps[i][EGSidxTl1R]")
                exec("self.elemGrp_%d_EGSidxTl2D" %i +" = elemGrps[i][EGSidxTl2D]")
                exec("self.elemGrp_%d_EGSidxTl2R" %i +" = elemGrps[i][EGSidxTl2R]")
                exec("self.elemGrp_%d_EGSidxPrio" %i +" = elemGrps[i][EGSidxPrio]")
                exec("self.elemGrp_%d_EGSidxFric" %i +" = elemGrps[i][EGSidxFric]")
                exec("self.elemGrp_%d_EGSidxBlnc" %i +" = elemGrps[i][EGSidxBlnc]")
                exec("self.elemGrp_%d_EGSidxIter" %i +" = elemGrps[i][EGSidxIter]")
                exec("self.elemGrp_%d_EGSidxSDFl" %i +" = elemGrps[i][EGSidxSDFl]")
                exec("self.elemGrp_%d_EGSidxMCTh" %i +" = elemGrps[i][EGSidxMCTh]")
                exec("self.elemGrp_%d_EGSidxScal" %i +" = elemGrps[i][EGSidxScal]")
                exec("self.elemGrp_%d_EGSidxNoHo" %i +" = elemGrps[i][EGSidxNoHo]")
                exec("self.elemGrp_%d_EGSidxNoCo" %i +" = elemGrps[i][EGSidxNoCo]")
                exec("self.elemGrp_%d_EGSidxBevl" %i +" = elemGrps[i][EGSidxBevl]")
                exec("self.elemGrp_%d_EGSidxFacg" %i +" = elemGrps[i][EGSidxFacg]")
                exec("self.elemGrp_%d_EGSidxCyln" %i +" = elemGrps[i][EGSidxCyln]")
                exec("self.elemGrp_%d_EGSidxDCor" %i +" = elemGrps[i][EGSidxDCor]")
                exec("self.elemGrp_%d_EGSidxDClP" %i +" = elemGrps[i][EGSidxDClP]")
                exec("self.elemGrp_%d_EGSidxDmpR" %i +" = elemGrps[i][EGSidxDmpR]")

            # Update fromula assistant submenu according to the chosen element group
            i = self.menu_selectedElemGrp
            try: self.assistant_menu = elemGrps[i][EGSidxAsst]['ID']
            except: self.assistant_menu = "None"

            self.update_lock = 0
            
            ### Update also the other classes properties
            props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
            props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
            props_asst_con_rei_beam.props_update_menu()
            props_asst_con_rei_wall.props_update_menu()

        return{'FINISHED'}
            
    ###### Update global vars from menu properties
    def props_update_globals(self):

        ### On loading a new scene properties are lost, in this case reset element groups to defaults
        if self.menu_init:
            elemGrps = global_vars.elemGrps = elemGrpsBak.copy()
            self.menu_init = 0
        else:
            elemGrps = global_vars.elemGrps
        
        if len(elemGrps) > 0:
            
            qFMonlySettingModified = 0
            for i in range(len(elemGrps)):
                elemGrps[i][EGSidxName] = eval("self.elemGrp_%d_EGSidxName" %i)
                elemGrps[i][EGSidxCTyp] = eval("self.elemGrp_%d_EGSidxCTyp" %i)
                elemGrps[i][EGSidxBTC] = eval("self.elemGrp_%d_EGSidxBTC" %i)
                elemGrps[i][EGSidxBTT] = eval("self.elemGrp_%d_EGSidxBTT" %i)
                elemGrps[i][EGSidxBTS] = eval("self.elemGrp_%d_EGSidxBTS" %i)
                elemGrps[i][EGSidxBTS9] = eval("self.elemGrp_%d_EGSidxBTS9" %i)
                elemGrps[i][EGSidxBTB] = eval("self.elemGrp_%d_EGSidxBTB" %i)
                elemGrps[i][EGSidxBTB9] = eval("self.elemGrp_%d_EGSidxBTB9" %i)
                elemGrps[i][EGSidxBTP] = eval("self.elemGrp_%d_EGSidxBTP" %i)
                elemGrps[i][EGSidxBTPL] = eval("self.elemGrp_%d_EGSidxBTPL" %i)
                elemGrps[i][EGSidxBTX] = eval("self.elemGrp_%d_EGSidxBTX" %i)
                elemGrps[i][EGSidxBTI] = eval("self.elemGrp_%d_EGSidxBTI" %i)
                elemGrps[i][EGSidxBLC] = eval("self.elemGrp_%d_EGSidxBLC" %i)
                elemGrps[i][EGSidxBLT] = eval("self.elemGrp_%d_EGSidxBLT" %i)
                elemGrps[i][EGSidxBLS] = eval("self.elemGrp_%d_EGSidxBLS" %i)
                elemGrps[i][EGSidxBLS9] = eval("self.elemGrp_%d_EGSidxBLS9" %i)
                elemGrps[i][EGSidxBLB] = eval("self.elemGrp_%d_EGSidxBLB" %i)
                elemGrps[i][EGSidxBLB9] = eval("self.elemGrp_%d_EGSidxBLB9" %i)
                elemGrps[i][EGSidxRqVP] = eval("self.elemGrp_%d_EGSidxRqVP" %i)
                elemGrps[i][EGSidxMatP] = eval("self.elemGrp_%d_EGSidxMatP" %i)
                elemGrps[i][EGSidxDens] = eval("self.elemGrp_%d_EGSidxDens" %i)
                elemGrps[i][EGSidxLoad] = eval("self.elemGrp_%d_EGSidxLoad" %i)

                elemGrps[i][EGSidxTl1D] = eval("self.elemGrp_%d_EGSidxTl1D" %i)
                elemGrps[i][EGSidxTl1R] = eval("self.elemGrp_%d_EGSidxTl1R" %i)
                elemGrps[i][EGSidxTl2D] = eval("self.elemGrp_%d_EGSidxTl2D" %i)
                elemGrps[i][EGSidxTl2R] = eval("self.elemGrp_%d_EGSidxTl2R" %i)
                elemGrps[i][EGSidxPrio] = eval("self.elemGrp_%d_EGSidxPrio" %i)
                elemGrps[i][EGSidxFric] = eval("self.elemGrp_%d_EGSidxFric" %i)
                elemGrps[i][EGSidxBlnc] = eval("self.elemGrp_%d_EGSidxBlnc" %i)
                elemGrps[i][EGSidxIter] = eval("self.elemGrp_%d_EGSidxIter" %i)
                elemGrps[i][EGSidxSDFl] = eval("self.elemGrp_%d_EGSidxSDFl" %i)
                lastValue = elemGrps[i][EGSidxMCTh]
                elemGrps[i][EGSidxMCTh] = eval("self.elemGrp_%d_EGSidxMCTh" %i)
                if elemGrps[i][EGSidxMCTh] != lastValue: qFMonlySettingModified = 1
                elemGrps[i][EGSidxScal] = eval("self.elemGrp_%d_EGSidxScal" %i)
                elemGrps[i][EGSidxNoHo] = eval("self.elemGrp_%d_EGSidxNoHo" %i)
                elemGrps[i][EGSidxNoCo] = eval("self.elemGrp_%d_EGSidxNoCo" %i)
                elemGrps[i][EGSidxBevl] = eval("self.elemGrp_%d_EGSidxBevl" %i)
                elemGrps[i][EGSidxFacg] = eval("self.elemGrp_%d_EGSidxFacg" %i)
                elemGrps[i][EGSidxCyln] = eval("self.elemGrp_%d_EGSidxCyln" %i)
                elemGrps[i][EGSidxDCor] = eval("self.elemGrp_%d_EGSidxDCor" %i)
                elemGrps[i][EGSidxDClP] = eval("self.elemGrp_%d_EGSidxDClP" %i)
                elemGrps[i][EGSidxDmpR] = eval("self.elemGrp_%d_EGSidxDmpR" %i)
                # Remove surface variable if existing (will be added in setConstraintSettings()
                elemGrps[i][EGSidxBTC] = elemGrps[i][EGSidxBTC].replace('*a','')
                elemGrps[i][EGSidxBTT] = elemGrps[i][EGSidxBTT].replace('*a','')
                elemGrps[i][EGSidxBTS] = elemGrps[i][EGSidxBTS].replace('*a','')
                elemGrps[i][EGSidxBTS9] = elemGrps[i][EGSidxBTS9].replace('*a','')
                elemGrps[i][EGSidxBTB] = elemGrps[i][EGSidxBTB].replace('*a','')
                elemGrps[i][EGSidxBTB9] = elemGrps[i][EGSidxBTB9].replace('*a','')
                elemGrps[i][EGSidxBTP] = elemGrps[i][EGSidxBTP].replace('*a','')

            if qFMonlySettingModified:
                if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'):
                    bpy.ops.bcb.report('INVOKE_DEFAULT', message="This feature requires a Blender version with Fracture Modifier. Visit kaikostack.com/fracture for the FM-enabled Blender version.", icon="ERROR") 
                        
            ### If different formula assistant ID from that stored in element group then update with defaults
            i = self.menu_selectedElemGrp
            if self.assistant_menu != elemGrps[i][EGSidxAsst]['ID']:
                # Add formula assistant settings to element group
                for formAssist in formulaAssistants:
                    if self.assistant_menu == formAssist['ID']:
                        elemGrps[i][EGSidxAsst] = formAssist.copy()

                ### Update also the other classes properties
                props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
                props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
                props_asst_con_rei_beam.props_update_menu()
                props_asst_con_rei_wall.props_update_menu()
            
            else:
                ### Update global vars also from the other classes properties
                props_asst_con_rei_beam = bpy.context.window_manager.bcb_asst_con_rei_beam
                props_asst_con_rei_wall = bpy.context.window_manager.bcb_asst_con_rei_wall
                props_asst_con_rei_beam.props_update_globals()
                props_asst_con_rei_wall.props_update_globals()

        return{'FINISHED'}
            