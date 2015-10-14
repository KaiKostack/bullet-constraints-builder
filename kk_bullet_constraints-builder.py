####################################
# Bullet Constraints Builder v1.70 #
####################################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# This version is developed at the Laurea University of applied Sciences, Finland
# Copyright (C) 2015 Kai Kostack
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
   
### Vars for constraint distribution
withGUI = 1    # Enable graphical user interface, after pressing the "Run Script" button the menu panel should appear

distanceTolerance = 0.05     # 0.05  | Allowed tolerance for distance change in percent for connection removal (1.00 = 100 %)
constraintUseBreaking = 1    # 1     | Enables breaking for all constraints
connectionCountLimit = 0     # 0     | Maximum count of connections per object pair (0 = disabled)
searchDistance = 0.02        # 0.02  | Search distance to neighbor geometry
clusterRadius = 0.4          # 0.4   | Radius for bundling close constraints into clusters (0 = clusters disabled)
alignVertical = 0.9          # 0.9   | Uses a vertical alignment multiplier for connection type 4 instead of using unweighted center to center orientation (0 = disabled)
                             #       | Internally X and Y components of the directional vector will be reduced by this factor, should always be < 1 to make horizontal connections still possible.
useAccurateArea = 1          # 1     | Enables accurate contact area calculation using booleans (only works correct with solid i.e. manifold objects, recommended for truss structures or steel constructions in general)
                             #       | If disabled a simpler boundary box intersection approach is used (only recommended for concrete constructions without diagonal elements)

# Customizable element groups list (for elements of different conflicting groups priority is defined by the list's order)
elemGrps = [ \
# 0          1    2           3        4   5     6    7    8     9
# Name       RVP  Mat.preset  Density  CT  BTC   BTT  Bev. Scale facing
[ "",        1,   "Concrete", 0,       5,  20,   5,   0,   .95,  0      ],   # Defaults to be used when element is not part of any element group
[ "Columns", 1,   "Concrete", 0,       5,  20,   5,   0,   .95,  0      ],
[ "Girders", 1,   "Concrete", 0,       5,  20,   5,   0,   .95,  0      ],
[ "Walls",   1,   "Concrete", 0,       5,  20,   5,   0,   .95,  0      ],
[ "Slabs",   1,   "Concrete", 0,       5,  20,   5,   0,   .95,  0      ]
]

# Column descriptions (in order from left to right):
#
# Required Vertex Pairs | How many vertex pairs between two elements are required to generate a connection.
# (Depreciated)         | This can help to ensure there is an actual surface to surface connection between both elements (for at least 3 verts you can expect a shared surface).
#                       | For two elements from different groups with different RVPs the lower number is decisive.
# Material Preset       | Preset name of the physical material to be used from Blender's internal database.
#                       | See Blender's Rigid Body Tools for a list of available presets.
# Material Density      | Custom density value (kg/m^3) to use instead of material preset (0 = disabled).
# Connection Type       | Connection type ID for the constraint presets defined by this script, see list below.
# Break.Thresh.Compres. | Real world material compressive breaking threshold in N/mm^2.
# Break.Thresh.Tensile  | Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).
# Bevel                 | Use beveling for elements to avoid `Jenga0
# Scale                 | Apply scaling factor on elements to avoid `Jenga
# Facing                | Generate an addional layer of elements only for display (will only be used together with bevel and scale option)

# Connection types:
#
# 1 = 1x 'FIXED' constraint per connection, only compressive breaking threshold is used (tensile limit stays the same, angular forces limit as well)
# 2 = 1x 'POINT' constraint per connection, only compressive breaking threshold is used (tensile limit stays the same)
# 3 = 1x 'FIXED' + 1x 'POINT' constraint per connection, compressive breaking threshold is used for the first one and tensile for the second
# 4 = 2x 'GENERIC' constraint per connection, one to evaluate the compressive and the other one for the tensile breaking threshold
# 5 = 3x 'GENERIC' constraint per connection, one to evaluate the compressive, another one for the tensile / lateral and the last one for bending / buckling breaking threshold

### Developer
debug = 0                         # Enables verbose console output for debugging purposes
maxMenuElementGroupItems = 100    # Maximum allowed element group entries in menu 
emptyDrawSize = 0.25              # Display size of constraint empty objects as radius in meters
                
# For monitor event handler:
qRenderAnimation = 0     # Render animation by using render single image function for each frame (doesn't support motion blur, keep it disabled), 1 = regular, 2 = OpenGL

########################################

elemGrpsBak = elemGrps.copy()

################################################################################   

bl_info = {
    "name": "Bullet Constraints Builder",
    "author": "Kai Kostack",
    "version": (1, 7, 0),
    "blender": (2, 7, 5),
    "location": "View3D > Toolbar",
    "description": "Tool to connect rigid bodies via constraints in a physical plausible way.",
    "wiki_url": "http://www.inachus.eu",
    "tracker_url": "http://kaikostack.com",
    "category": "Animation"}

import bpy, sys, mathutils, time, copy, math
from mathutils import Vector
#import os
#os.system("cls")

################################################################################
################################################################################

def storeConfigDataInScene(scene):

    ### Store menu config data in scene
    if debug: print("Storing menu config data in scene...")
    
    scene["bcb_prop_distanceTolerance"] = distanceTolerance
    scene["bcb_prop_constraintUseBreaking"] = constraintUseBreaking
    scene["bcb_prop_connectionCountLimit"] = connectionCountLimit
    scene["bcb_prop_searchDistance"] = searchDistance
    scene["bcb_prop_clusterRadius"] = clusterRadius
    scene["bcb_prop_alignVertical"] = alignVertical
    
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
    
    props = bpy.context.window_manager.bcb
    if "bcb_prop_distanceTolerance" in scene.keys():
        global distanceTolerance; distanceTolerance = props.prop_distanceTolerance = scene["bcb_prop_distanceTolerance"]
    if "bcb_prop_constraintUseBreaking" in scene.keys():
        global constraintUseBreaking; constraintUseBreaking = props.prop_constraintUseBreaking = scene["bcb_prop_constraintUseBreaking"]
    if "bcb_prop_connectionCountLimit" in scene.keys():
        global connectionCountLimit; connectionCountLimit = props.prop_connectionCountLimit = scene["bcb_prop_connectionCountLimit"]
    if "bcb_prop_searchDistance" in scene.keys():
        global searchDistance; searchDistance = props.prop_searchDistance = scene["bcb_prop_searchDistance"]
    if "bcb_prop_clusterRadius" in scene.keys():
        global clusterRadius; clusterRadius = props.prop_clusterRadius = scene["bcb_prop_clusterRadius"]
    if "bcb_prop_alignVertical" in scene.keys():
        global alignVertical; alignVertical = props.prop_alignVertical = scene["bcb_prop_alignVertical"]
            
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    if "bcb_prop_elemGrps" in scene.keys():
        global elemGrps
        elemGrpsProp = scene["bcb_prop_elemGrps"]
        elemGrpsInverted = []
        for i in range(len(elemGrpsProp[0])):
            column = []
            for j in range(len(elemGrpsProp)):
                column.append(elemGrpsProp[j][i])
            elemGrpsInverted.append(column)
        elemGrps = elemGrpsInverted
    
################################################################################   

def storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect):
    
    ### Store build data in scene
    if debug: print("Storing build data in scene...")
    
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
    if debug: print("Getting build data from scene...")
    
    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ### Get data from scene
    names = scene["bcb_objs"]
    try: objs = [scnObjs[name] for name in names]
    except: objs = []; print("Error: BCB related object(s) not found, rebuilding constraints is required.")
    #objsEGrp = scene["bcb_objsEGrp"]    # Not required for building only for clearAllDataFromScene(), index will be renewed on update
    names = scene["bcb_emptyObjs"]
    try: emptyObjs = [scnEmptyObjs[name] for name in names]
    except: emptyObjs = []; print("Error: BCB related object(s) not found, rebuilding constraints is required.")
    names = scene["bcb_childObjs"]
    try: childObjs = [scnObjs[name] for name in names]
    except: childObjs = []; print("Error: BCB related object(s) not found, rebuilding constraints is required.")
    connectsPair = scene["bcb_connectsPair"]
    connectsLoc = scene["bcb_connectsLoc"]
    connectsArea = scene["bcb_connectsArea"]
    connectsConsts = scene["bcb_connectsConsts"]
    constsConnect = scene["bcb_constsConnect"]
    
    return objs, emptyObjs, childObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect

################################################################################   

def clearAllDataFromScene(scene):
    
    ### Clear all data related to Bullet Constraint Builder from scene
    if debug: print("Clearing all data related to Bullet Constraint Builder from scene...")
    
    ### Prepare scene object dictionaries by type to be used for faster item search (optimization)
    scnObjs = {}
    scnEmptyObjs = {}
    for obj in scene.objects:
        if obj.type == 'MESH':    scnObjs[obj.name] = obj
        elif obj.type == 'EMPTY': scnEmptyObjs[obj.name] = obj

    ### Get data from scene
    objsEGrp = scene["bcb_objsEGrp"]
    objsNames = scene["bcb_objs"]
    try: objs = [scnObjs[name] for name in objsNames]
    except: objs = []; print("Error: BCB related object(s) not found, cleanup may be incomplete.")
    names = scene["bcb_emptyObjs"]
    try: emptyObjs = [scnEmptyObjs[name] for name in names]
    except: emptyObjs = []; print("Error: BCB related object(s) not found, cleanup may be incomplete.")
    names = scene["bcb_childObjs"]
    try: childObjs = [scnObjs[name] for name in names]
    except: childObjs = []; print("Error: BCB related object(s) not found, cleanup may be incomplete.")
    
    ### Store layer settings and activate all layers
    layers = []
    for i in range(20):
        layers.append(int(scene.layers[i]))
        scene.layers[i] = 1
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    
    ### Replace modified elements with their child counterparts (the original meshes) 
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

    ### Get data again from scene after we changed obj names
    names = scene["bcb_objs"]
    try: objs = [scnObjs[name] for name in names]
    except: objs = []; print("Error: BCB related object(s) not found, cleanup may be incomplete.")
    names = scene["bcb_emptyObjs"]
    try: emptyObjs = [scnEmptyObjs[name] for name in names]
    except: emptyObjs = []; print("Error: BCB related object(s) not found, cleanup may be incomplete.")
    
    ### Revert element scaling
    for k in range(len(objs)):
        obj = objs[k]
        scale = elemGrps[objsEGrp[k]][8]
        if scale != 0 and scale != 1:
            obj.scale /= scale
            
    ### Select modified elements for deletion from scene 
    for parentObj in parentTmpObjs: parentObj.select = 1
    ### Select constraint empty objects for deletion from scene
    for emptyObj in emptyObjs: emptyObj.select = 1
    
    ### Delete all selected objects
    bpy.ops.object.delete(use_global=True)
    
    ### Revert selection back to original state and clear ID properties from objects
    for obj in objs:
        obj.select = 1
        # Clear object properties
        for key in obj.keys(): del obj[key]
    
    ### Finally remove ID property build data (leaves menu props in place)
    for key in scene.keys():
        if "bcb_" in key and not "bcb_prop" in key: del scene[key]
   
    # Set layers as in original scene
    for i in range(20): scene.layers[i] = layers[i]
        
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
                
    ################################
    ### What to do AFTER start frame
    else:
        print("Frame:", scene.frame_current, " ")
        
        ###### Function
        monitor_checkForDistanceChange()
                            
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
    
    ### Get temp data from scene
    names = scene["bcb_objs"]
    try: objs = [scnObjs[name] for name in names]
    except: objs = []; print("Error: BCB related object(s) not found, rebuilding constraints is required."); return
    names = scene["bcb_emptyObjs"]
    try: emptyObjs = [scnEmptyObjs[name] for name in names]
    except: emptyObjs = []; print("Error: BCB related object(s) not found, rebuilding constraints is required."); return
    connectsPair = scene["bcb_connectsPair"]
    connectsConsts = scene["bcb_connectsConsts"]
    
    ### Create original transform data array
    d = 0
    for pair in connectsPair:
        d += 1
        sys.stdout.write('\r' +"%d " %d)
        
        objA = objs[pair[0]]
        objB = objs[pair[1]]
        # Calculate distance between both elements of the connection
        distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
        # Calculate angle between two elements
        quat0 = objA.matrix_world.to_quaternion()
        quat1 = objB.matrix_world.to_quaternion()
        angle = quat0.rotation_difference(quat1).angle
        consts = []
        constsBrkTs = []
        for const in connectsConsts[d -1]:
            emptyObj = emptyObjs[const]
            consts.append(emptyObj)
            # Backup original breaking thresholds
            constsBrkTs.append(emptyObj.rigid_body_constraint.breaking_threshold)
        connects.append([objA, objB, distance, angle, consts, constsBrkTs, 1])

    print("Connections")
        
################################################################################

def monitor_checkForDistanceChange():

    if debug: print("Calling checkForDistanceChange")
    
    connects = bpy.app.driver_namespace["bcb_monitor"]
    d = 0
    cnt = 0
    for connect in connects:
        # If connection is not flagged as loose then do:
        if connect[6]:
            d += 1
            sys.stdout.write('\r' +"%d " %d)
            
            objA = connect[0]
            objB = connect[1]
            # Calculate distance between both elements of the connection
            distance = (objA.matrix_world.to_translation() -objB.matrix_world.to_translation()).length
            distanceDif = abs(1 -(connect[2] /distance))
            # Calculate angle between two elements
            quatA = objA.matrix_world.to_quaternion()
            quatB = objB.matrix_world.to_quaternion()
            angleDif = math.asin(math.sin( abs(connect[3] -quatA.rotation_difference(quatB).angle) /2))   # The construct "asin(sin(x))" is a triangle function to achieve a seamless rotation loop from input
            # If change in relative distance is larger than tolerance plus change in angle (angle is involved here to allow for bending and buckling)
            if distanceDif > distanceTolerance +(angleDif /3.1416) \
            or angleDif > 1.5708:       # Use pi/2 as tolerance for angle (could be an further setting in UI later though)
                if angleDif > 1.5708: print(angleDif, connect[3], quatA.rotation_difference(quatB).angle)
                # Disable all constraints for this connection by setting breaking threshold to 0
                for const in connect[4]:
                    const.rigid_body_constraint.breaking_threshold = 0
                # Flag connection as being disconnected
                connect[6] = 0
                cnt += 1
    
    if cnt > 0: print("Connections | Removed:", cnt)
    else: print("Connections")
                
################################################################################

def monitor_freeBuffers():
    
    if debug: print("Calling freeBuffers")
    
    connects = bpy.app.driver_namespace["bcb_monitor"]
    ### Restore original breaking thresholds
    for connect in connects:
        consts = connect[4]
        constsBrkTs = connect[5]
        for i in range(len(consts)):
            consts[i].rigid_body_constraint.breaking_threshold = constsBrkTs[i]
    # Clear property
    del bpy.app.driver_namespace["bcb_monitor"]

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
    
    prop_distanceTolerance = float(name="Tolerance", default=distanceTolerance, min=0.0, max=1.0, description="Allowed tolerance for distance change in percent for connection removal (1.00 = 100 %).")
    prop_constraintUseBreaking = bool(name="Enable Breaking", default=constraintUseBreaking, description="Enables breaking for all constraints.")
    prop_connectionCountLimit = int(name="Con.Count Limit", default=connectionCountLimit, min=0, max=10000, description="Maximum count of connections per object pair (0 = disabled).")
    prop_searchDistance = float(name="Search Distance", default=searchDistance, min=0.0, max=1000, description="Search distance to neighbor geometry.")
    prop_clusterRadius = float(name="Cluster Radius", default=clusterRadius, min=0.0, max=1000, description="Radius for bundling close constraints into clusters (0 = clusters disabled).")
    prop_alignVertical = float(name="Vertical Alignment", default=alignVertical, min=0.0, max=1.0, description="Enables a vertical alignment multiplier for connection type 4 or above instead of using unweighted center to center orientation (0 = disabled, 1 = fully vertical).")
    
    for i in range(maxMenuElementGroupItems):
        if i < len(elemGrps): j = i
        else: j = 0
        exec("prop_elemGrp_%d_0" %i +" = string(name='Grp.Name', default=elemGrps[j][0], description='The name of the element group.')")
        exec("prop_elemGrp_%d_4" %i +" = int(name='Connection Type', default=elemGrps[j][4], min=1, max=5, description='Connection type ID for the constraint presets defined by this script, see docs or connection type list in code.')")
        exec("prop_elemGrp_%d_5" %i +" = float(name='Brk.Trs.Compressive', default=elemGrps[j][5], min=0.0, max=10000, description='Real world material compressive breaking threshold in N/mm^2.')")
        exec("prop_elemGrp_%d_6" %i +" = float(name='Brk.Trs.Tensile', default=elemGrps[j][6], min=0.0, max=10000, description='Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).')")
        exec("prop_elemGrp_%d_1" %i +" = int(name='Req.Vert.Pairs', default=elemGrps[j][1], min=0, max=100, description='How many vertex pairs between two elements are required to generate a connection.')")
        exec("prop_elemGrp_%d_2" %i +" = string(name='Mat.Preset', default=elemGrps[j][2], description='Preset name of the physical material to be used from BlenderJs internal database. See Blenders Rigid Body Tools for a list of available presets.')")
        exec("prop_elemGrp_%d_3" %i +" = float(name='Matl. Density', default=elemGrps[j][3], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("prop_elemGrp_%d_7" %i +" = bool(name='Bevel', default=elemGrps[j][7], description='Enables beveling for elements to avoid `Jengax effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_8" %i +" = float(name='Rescale Factor', default=elemGrps[j][8], min=0.0, max=1, description='Applies scaling factor on elements to avoid `Jengai effect (uses hidden collision meshes).')")
        exec("prop_elemGrp_%d_9" %i +" = bool(name='Facing', default=elemGrps[j][9], description='Generates an addional layer of elements only for display (will only be used together with bevel and scale option, also serves as backup and for mass calculation).')")
        
    def props_update_menu(self):
        ### Update menu related properties from global vars
        for i in range(len(elemGrps)):
            exec("self.prop_elemGrp_%d_0" %i +" = elemGrps[i][0]")
            exec("self.prop_elemGrp_%d_4" %i +" = elemGrps[i][4]")
            exec("self.prop_elemGrp_%d_5" %i +" = elemGrps[i][5]")
            exec("self.prop_elemGrp_%d_6" %i +" = elemGrps[i][6]")
            exec("self.prop_elemGrp_%d_1" %i +" = elemGrps[i][1]")
            exec("self.prop_elemGrp_%d_2" %i +" = elemGrps[i][2]")
            exec("self.prop_elemGrp_%d_3" %i +" = elemGrps[i][3]")
            exec("self.prop_elemGrp_%d_7" %i +" = elemGrps[i][7]")
            exec("self.prop_elemGrp_%d_8" %i +" = elemGrps[i][8]")
            exec("self.prop_elemGrp_%d_9" %i +" = elemGrps[i][9]")
            
    def props_update_globals(self):
        ### Update global vars from menu related properties
        global distanceTolerance; distanceTolerance = self.prop_distanceTolerance
        global constraintUseBreaking; constraintUseBreaking = self.prop_constraintUseBreaking
        global connectionCountLimit; connectionCountLimit = self.prop_connectionCountLimit
        global searchDistance; searchDistance = self.prop_searchDistance
        global clusterRadius; clusterRadius = self.prop_clusterRadius
        global alignVertical; alignVertical = self.prop_alignVertical
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
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.bcb
        obj = context.object
        scene = bpy.context.scene
        
        row = layout.row()
        if not props.prop_menu_gotData: 
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.execute", icon="MOD_SKIN")
            split2 = split.row()
            if not props.prop_menu_gotConfig:
                if "bcb_prop_elemGrps" in scene.keys():
                      split2.operator("bcb.get_config", icon="FILE_REFRESH")
                else: split2.operator("bcb.set_config", icon="NEW")
            else:
                split2.operator("bcb.set_config", icon="NEW")
            row = layout.row() # for baking buttons
            row.enabled = 0
        else:
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split.operator("bcb.clear", icon="CANCEL")
            row = layout.row() # for baking buttons
        split = row.split(percentage=.50, align=False)
        split.operator("bcb.bake", icon="REC")
        split2 = split.row()
        split2.prop(props, "prop_distanceTolerance")
        
        row = layout.row(); row.prop(props, "prop_constraintUseBreaking")
        row = layout.row(); row.prop(props, "prop_connectionCountLimit")
        row = layout.row(); row.prop(props, "prop_searchDistance")
        row = layout.row(); row.prop(props, "prop_clusterRadius")
        row = layout.row(); row.prop(props, "prop_alignVertical")
        
        layout.separator()
        row = layout.row(); row.label(text="Element Groups", icon="MOD_BUILD")
        frm = layout.box()
        row = frm.row()
        row.operator("bcb.add", icon="ZOOMIN")
        row.operator("bcb.del", icon="X")
        row.operator("bcb.reset", icon="CANCEL")
        row.operator("bcb.move_up", icon="TRIA_UP")
        row.operator("bcb.move_down", icon="TRIA_DOWN")
        for i in range(len(elemGrps)):
            if i == props.prop_menu_selectedItem:
                  row = frm.box().row()
            else: row = frm.row()
            elemGrp0 = eval("props.prop_elemGrp_%d_0" %i)
            elemGrp4 = eval("props.prop_elemGrp_%d_4" %i)
            elemGrp5 = eval("props.prop_elemGrp_%d_5" %i)
            elemGrp6 = eval("props.prop_elemGrp_%d_6" %i)
            split = row.split(percentage=.35, align=False)
            if elemGrp0 == "": split.label(text="[Def.]")
            else:              split.label(text=str(elemGrp0))
            split2 = split.split(percentage=.23, align=False)
            split2.label(text=str(elemGrp4))
            split2.label(text=str(elemGrp5))
            split2.label(text=str(elemGrp6))
        row = frm.row()
        row.operator("bcb.up", icon="TRIA_UP")
        row.operator("bcb.down", icon="TRIA_DOWN")
        layout.separator()
        
        i = props.prop_menu_selectedItem
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_0" %i)
        
        box = layout.box(); 
        elemGrp4 = eval("props.prop_elemGrp_%d_4" %i)
        if   elemGrp4 == 1: box.label(text="1x FIXED")
        elif elemGrp4 == 2: box.label(text="1x POINT")
        elif elemGrp4 == 3: box.label(text="1x FIXED + 1x POINT")
        elif elemGrp4 == 4: box.label(text="2x GENERIC")
        elif elemGrp4 == 5: box.label(text="3x GENERIC")
        
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_4" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_5" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_6" %i)
        #row = layout.row(); row.prop(props, "prop_elemGrp_%d_1" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_2" %i)
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_3" %i)
        layout.separator()
        
        row = layout.row(); row.prop(props, "prop_elemGrp_%d_8" %i)
        row = layout.row();
        row.prop(props, "prop_elemGrp_%d_7" %i)
        elemGrp7 = eval("props.prop_elemGrp_%d_7" %i)
        elemGrp9 = eval("props.prop_elemGrp_%d_9" %i)
        if elemGrp7 and not elemGrp9: row.alert = 1
        row.prop(props, "prop_elemGrp_%d_9" %i)
        
        if elemGrp7 and not elemGrp9:
            row = layout.row(); row.label(text="Warning: Disabled facing")
            row = layout.row(); row.label(text="makes bevel permanent!")
            
        # Update global vars from menu related properties
        props.props_update_globals()
 
         
class OBJECT_OT_bcb_set_config(bpy.types.Operator):
    bl_idname = "bcb.set_config"
    bl_label = "Set Config"
    bl_description = "Stores actual config data in current scene."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Store menu config data in scene
        storeConfigDataInScene(scene)
        # Update menu related properties from global vars
        props.prop_menu_gotConfig = 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_get_config(bpy.types.Operator):
    bl_idname = "bcb.get_config"
    bl_label = "Get Config"
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
        
class OBJECT_OT_bcb_execute(bpy.types.Operator):
    bl_idname = "bcb.execute"
    bl_label = "Execute"
    bl_description = "Starts building process and adds constraints to selected elements."
    def execute(self, context):
        props = context.window_manager.bcb
        ###### Execute main building process from scratch
        execute()
        props.prop_menu_gotData = 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_update(bpy.types.Operator):
    bl_idname = "bcb.update"
    bl_label = "Update"
    bl_description = "Updates constraints generated from a previous built."
    def execute(self, context):
        props = context.window_manager.bcb
        # Update menu related properties from global vars
        props.props_update_menu()
        ###### Execute update of all existing constraints with new settings
        execute()
        return{'FINISHED'} 

class OBJECT_OT_bcb_bake(bpy.types.Operator):
    bl_idname = "bcb.bake"
    bl_label = "Bake"
    bl_description = "Bakes simulation. Use of this button is crucial if connection type 4 or above is used, because then constraints require monitoring on per frame basis during simulation."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        print('Init BCB monitor event handler.')
        bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
        # Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            obj.location = obj.location
        # Invoke baking
        contextFix = bpy.context.copy()
        contextFix['point_cache'] = scene.rigidbody_world.point_cache
        bpy.ops.ptcache.free_bake(contextFix)
        bpy.ops.ptcache.bake(contextFix, bake=True)
        print('Removing BCB monitor event handler.')
        for i in range( len( bpy.app.handlers.frame_change_pre ) ):
             bpy.app.handlers.frame_change_pre.pop()
        monitor_freeBuffers()
        return{'FINISHED'} 

class OBJECT_OT_bcb_clear(bpy.types.Operator):
    bl_idname = "bcb.clear"
    bl_label = "Clear"
    bl_description = "Clears constraints from scene and revert back to original state (required to rebuild constraints from scratch)."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Clear all data from scene and delete also constraint empty objects
        if "bcb_objs" in scene.keys(): clearAllDataFromScene(scene)
        props.prop_menu_gotData = 0
        return{'FINISHED'} 

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = " Add"
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
    bl_label = " Delete"
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
    bl_label = " M.Up"
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
    bl_label = " M.Down"
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
    bl_label = " Up"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedItem > 0:
            props.prop_menu_selectedItem -= 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_down(bpy.types.Operator):
    bl_idname = "bcb.down"
    bl_label = " Down"
    bl_description = "Selects element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.prop_menu_selectedItem < len(elemGrps) -1:
            props.prop_menu_selectedItem += 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_reset(bpy.types.Operator):
    bl_idname = "bcb.reset"
    bl_label = " Reset"
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


classes = [ \
    bcb_props,
    bcb_panel,
    OBJECT_OT_bcb_set_config,
    OBJECT_OT_bcb_get_config,
    OBJECT_OT_bcb_execute,
    OBJECT_OT_bcb_update,
    OBJECT_OT_bcb_bake,
    OBJECT_OT_bcb_clear,
    OBJECT_OT_bcb_add,
    OBJECT_OT_bcb_del,
    OBJECT_OT_bcb_move_up,
    OBJECT_OT_bcb_move_down,
    OBJECT_OT_bcb_up,
    OBJECT_OT_bcb_down,
    OBJECT_OT_bcb_reset
    ]      
          
################################################################################   
################################################################################   

def createElementGroupIndex(objs):

    ### Create a list about which object belongs to which element group
    objsEGrp = []
    for obj in objs:
        objGrpsTmp = []
        for elemGrp in elemGrps:
            if elemGrp[0] in bpy.data.groups:
                if obj.name in bpy.data.groups[elemGrp[0]].objects:
                    objGrpsTmp.append(elemGrps.index(elemGrp))
        if len(objGrpsTmp) > 1:
            print("\nWarning: Object %s belongs to more than one element group, defaults are used." %obj.name)
            objGrpsTmp = [0]
        elif len(objGrpsTmp) == 0: objGrpsTmp = [0]
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
            if obj.type == 'MESH':
                objs.append(obj)
            elif obj.type == 'EMPTY':
                if obj.rigid_body_constraint != None:
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
        aIndex = []#; aCo = []; aDist = [];
        if connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index)#; aCo.append(co); aDist.append(dist)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index)#; aCo.append(co); aDist.append(dist)
        aIndex = aIndex[1:] # Remove first item because it's the same as co_find (zero distance)
        
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
                            connectCnt += 1
                            if connectCnt == connectionCountLimit:
                                if elemGrps[objsEGrp[k]][1] <= 1:
                                    qNextObj = 1
                                    break
                            
            if qNextObj: break
        
    print()
    return connectsPair

################################################################################   

def findConnectionsByBoundaryBoxIntersection(objs, objsEGrp):
    
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
    for k in range(len(objs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(objs))
        
        obj = objs[k]
        mat = obj.matrix_world
        me = obj.data
                
        ### Find closest objects via kd-tree
        co_find = obj.location
        aIndex = []#; aCo = []; aDist = [];
        if connectionCountLimit:
            for (co, index, dist) in kdObjs.find_n(co_find, connectionCountLimit +1):  # +1 because the first item will be removed
                aIndex.append(index)#; aCo.append(co); aDist.append(dist)
        else:
            for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                aIndex.append(index)#; aCo.append(co); aDist.append(dist)
        aIndex = aIndex[1:] # Remove first item because it's the same as co_find (zero distance)
    
        # Loop through comparison object found
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
                        connectCnt += 1
                        if connectCnt == connectionCountLimit:
                            break
    
    print()
    return connectsPair

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
    
    print("%d connections skipped due to too few connecting vertices." %(connectCntOld -connectCnt))
    return connectsPair
        
################################################################################   

def calculateContactAreaBasedOnBoundaryBoxes(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    connectsArea = []
    connectsLoc = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        
        ###### Calculate boundary box corners
        bbAMin, bbAMax, bbACenter = boundaryBox(objA, 1)
        bbBMin, bbBMax, bbBCenter = boundaryBox(objB, 1)
        
        ### Calculate contact surface area from boundary box projection
        ### Project along all axis'
        overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
        overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
        overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
        overlapAreaX = overlapY *overlapZ
        overlapAreaY = overlapX *overlapZ
        overlapAreaZ = overlapX *overlapY
        # Add up all contact areas
        contactArea = overlapAreaX +overlapAreaY +overlapAreaZ
        # Find out element thickness to be used for bending threshold calculation 
        thickness = [overlapX, overlapY, overlapZ]
        thickness.sort()
        thickness = thickness[1]   # First item = mostly 0, second item = thickness, third item = width 
        connectsArea.append([contactArea, thickness])
        
        ### Use center of contact area boundary box as constraints location
        centerX = max(bbAMin[0],bbBMin[0]) +(overlapX /2)
        centerY = max(bbAMin[1],bbBMin[1]) +(overlapY /2)
        centerZ = max(bbAMin[2],bbBMin[2]) +(overlapZ /2)
        center = Vector((centerX, centerY, centerZ))
        #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon
        connectsLoc.append(center)
        
    return connectsArea, connectsLoc

################################################################################   

def calculateContactAreaBasedOnBooleans(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...", len(connectsPair))

    ### Create a second scene to temporarily move objects to, to avoid depsgraph update overhead (optimization)
    scene = bpy.context.scene
    sceneTemp = bpy.data.scenes.new("BCB Temp Scene")
    # Switch to original scene (shouldn't be necessary but is required for error free Bullet simulation on later scene switching for some strange reason)
    bpy.context.screen.scene = scene
    # Link cameras because in second scene is none and when coming back camera view will losing focus
    for objTemp in scene.objects:
        if objTemp.type == 'CAMERA':
            objTemp.select = 0
            sceneTemp.objects.link(objTemp)
    # Switch to new scene
    bpy.context.screen.scene = sceneTemp

    ### Main calculation loop
    connectsArea = []
    connectsLoc = []
    connectsPair_len = len(connectsPair)
    for k in range(connectsPair_len):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /connectsPair_len)

        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        objA.select = 0
        objB.select = 0
            
        # Link objects we're working on to second scene
        sceneTemp.objects.link(objA)
        sceneTemp.objects.link(objB)

        ### Check if meshes are water tight (non-manifold), if not, issue a warning
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
            qNonManifolds = 0
            for edge in me.edges:
                if edge.select: qNonManifolds = 1; break
            if qNonManifolds:
                print('Warning: Mesh not water tight, non-manifolds found:', obj.name)
        
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
            
#            ### Create a boolean union mesh (for contact area calculation)
#            modA_bool.operation = 'UNION'
#            me_union = objA.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
#            # Clean boolean result in case it is corrupted, because otherwise Blender sometimes crashes with "Error: EXCEPTION_ACCESS_VIOLATION"
#            qBadResult = me_union.validate(verbose=False, clean_customdata=False)
#            if qBadResult: print('Error on boolean operation, mesh problems detected:', objA.name, objB.name)
            
            ### Calculate center point for the intersection mesh
            # Create a new object for the mesh
            objIntersect = bpy.data.objects.new("BCB Temp Object", me_intersect)
            bpy.context.scene.objects.link(objIntersect)
            objIntersect.matrix_world = objA.matrix_world
            
            ### Calculate center of intersection mesh based on its boundary box (throws ugly "group # is unclassified!" warnings)
#            objIntersect.select = 1
#            #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
#            center = objIntersect.matrix_world.to_translation()
            ### Calculate center of intersection mesh based on its boundary box (alternative code, slower but no warnings)
            bbMin, bbMax, center = boundaryBox(objIntersect, 1)
            
            ### Find out element thickness to be used for bending threshold calculation (the diameter of the intersection mesh should be sufficient for now)
            thickness = list(objIntersect.dimensions)
            thickness.sort()
            thickness = thickness[1]   # First item = mostly 0, second item = thickness, third item = width 
            
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
#            ### Calculate surface area for the unified mesh
#            surfaceBoolUnion = 0
#            for poly in me_union.polygons: surfaceBoolUnion += poly.area
            ### Calculate surface area for the intersection mesh
            surfaceBoolIntersect = 0
            for poly in me_intersect.polygons: surfaceBoolIntersect += poly.area
            ### Calculate surface area for the intersection mesh with removed displacement
            surfaceBoolIntersectRemDisp = 0
            for poly in me_intersect_remDisp.polygons: surfaceBoolIntersectRemDisp += poly.area
#            ### The contact area is half the difference of both surface areas
#            contactArea = (surfaceDisp -surfaceBoolUnion) /2
            ### The contact area is half the surface area of the intersection mesh without displacement
            contactArea = surfaceBoolIntersectRemDisp /2
            contactArea *= correction
            if contactArea < 0: print('Error on boolean operation, contact area negative:', objA.name, objB.name)
            
            # Unlink new object from second scene
            sceneTemp.objects.unlink(objIntersect)
            
        # If intersection mesh has no geometry then invalidate connection
        else:
            contactArea = 0
            thickness = 0
            center = Vector((0, 0, 0))
        
        # Remove modifiers from original object again
        objA.modifiers.remove(modA_bool)
        objA.modifiers.remove(modA_disp)
        objB.modifiers.remove(modB_disp)
            
        # Unlink objects from second scene
        sceneTemp.objects.unlink(objA)
        sceneTemp.objects.unlink(objB)
        
        connectsArea.append([contactArea, thickness])
        connectsLoc.append(center)
            
    # Switch back to original scene
    bpy.context.screen.scene = scene
    # Delete second scene
    bpy.data.scenes.remove(sceneTemp)
                
    print()
    return connectsArea, connectsLoc

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, objsEGrp, connectsPair, connectsArea, connectsLoc):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")
    
    connectsPairTmp = []
    connectsAreaTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        if connectsArea[i][0] > 0.0001:
            connectsPairTmp.append(connectsPair[i])
            connectsAreaTmp.append(connectsArea[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsArea = connectsAreaTmp
    connectsLoc = connectsLocTmp
    
    print("%d connections skipped due to zero contact area." %(connectCntOld -connectCnt))
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
        connectionType = elemGrps[elemGrp][4]
        if connectionType == 1:
            connectsConsts.append([constCnt])
            constsConnect.append(i)
            constCnt += 1
        elif connectionType == 2:
            connectsConsts.append([constCnt])
            constsConnect.append(i)
            constCnt += 1
        elif connectionType == 3:
            connectsConsts.append([constCnt, constCnt +1])
            constsConnect.append(i)
            constsConnect.append(i)
            constCnt += 2
        elif connectionType == 4:
            connectsConsts.append([constCnt, constCnt +1])
            constsConnect.append(i)
            constsConnect.append(i)
            constCnt += 2
        elif connectionType == 5:
            connectsConsts.append([constCnt, constCnt +1, constCnt +2])
            constsConnect.append(i)
            constsConnect.append(i)
            constsConnect.append(i)
            constCnt += 3
    
    return connectsPair, connectsConsts, constsConnect

################################################################################   

def createEmptyObjs(scene, constCnt):
    
    ### Create empty objects
    print("Creating empty objects... (%d)" %constCnt)
    
    ### Create first object
    objConst = bpy.data.objects.new('Constraint', None)
    scene.objects.link(objConst)
    objConst.empty_draw_type = 'SPHERE'
    bpy.context.scene.objects.active = objConst
    bpy.ops.rigidbody.constraint_add()
    emptyObjs = [objConst]
    ### Duplicate them as long as we got the desired count   
    while len(emptyObjs) < constCnt:
        if len(emptyObjs) < 2048: sys.stdout.write("%d " %len(emptyObjs))
        else:                     sys.stdout.write("%d\n" %len(emptyObjs))
        # Update progress bar
        bpy.context.window_manager.progress_update(len(emptyObjs) /constCnt)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        # Select empties already in list
        c = 0
        for obj in emptyObjs:
            if c < constCnt -len(emptyObjs):
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
    
    if len(emptyObjs) < 2048: print()
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

def addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect):
    
    ### Add base constraint settings to empties
    print("Adding base constraint settings to empties... (%d)" %len(emptyObjs))
    
    for k in range(len(emptyObjs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(emptyObjs))
                
        objConst = emptyObjs[k]
        l = constsConnect[k]
        objConst.location = connectsLoc[l]
        objConst.rigid_body_constraint.object1 = objs[connectsPair[l][0]]
        objConst.rigid_body_constraint.object2 = objs[connectsPair[l][1]]
    
    print()
                
################################################################################   
    
def setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsArea, connectsConsts, constsConnect):
    
    ### Set constraint settings
    print("Adding main constraint settings... (%d)" %len(connectsPair))
    
    count = 0
    for k in range(len(connectsPair)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(connectsPair))
        
        consts = connectsConsts[k]
        contactArea = connectsArea[k][0]
        thickness = connectsArea[k][1]
        for idx in consts: emptyObjs[idx]['ContactArea'] = contactArea   # Store value as ID property for debug purposes
        
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        elemGrpA = objsEGrp[objs.index(objA)]
        elemGrpB = objsEGrp[objs.index(objB)]
        # Element group order defines priority for connection type (first preferred over latter) 
        if elemGrpA <= elemGrpB: elemGrp = elemGrpA
        else:                    elemGrp = elemGrpB
        
        connectionType = elemGrps[elemGrp][4]
        breakingThreshold1 = elemGrps[elemGrp][5]
        breakingThreshold2 = elemGrps[elemGrp][6]
        
        ### Set constraints by connection type preset
        ### Also convert real world breaking threshold to bullet breaking threshold and take simulation steps into account (Threshold = F / Steps)
        
        if   connectionType == 1:
            objConst1 = emptyObjs[consts[0]]
            objConst1.rigid_body_constraint.type = 'FIXED'
            objConst1.rigid_body_constraint.breaking_threshold = ( contactArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold1'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Add to Bullet constraint group in case it got removed for some reason
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst1)
            except: pass
            objConst1.empty_draw_size = emptyDrawSize
        
        elif connectionType == 2:
            objConst1 = emptyObjs[consts[0]]
            objConst1.rigid_body_constraint.type = 'POINT'
            objConst1.rigid_body_constraint.breaking_threshold = ( contactArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold1'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Add to Bullet constraint group in case it got removed for some reason
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst1)
            except: pass
            objConst1.empty_draw_size = emptyDrawSize
        
        elif connectionType == 3:
            constCnt = 2   # As both constraints bear all load and forces are evenly distributed among them the breaking thresholds need to be divided by their count to compensate
            ### First constraint
            objConst1 = emptyObjs[consts[0]]
            objConst1.rigid_body_constraint.type = 'FIXED'
            objConst1.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second) /constCnt
            objConst1['BrkThreshold1'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Second constraint
            objConst2 = emptyObjs[consts[1]]
            objConst2.rigid_body_constraint.type = 'POINT'
            objConst2.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second) /constCnt
            objConst2['BrkThreshold2'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst2.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Add to Bullet constraint group in case it got removed for some reason
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst1)
            except: pass
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst2)
            except: pass
            objConst1.empty_draw_size = emptyDrawSize
            objConst2.empty_draw_size = emptyDrawSize
        
        elif connectionType == 4:
            # Correction multiplier for breaking thresholds
            # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
            # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
            correction = 2
            ### First constraint
            objConst1 = emptyObjs[consts[0]]
            # Check if full update is necessary (optimization)
            if 'ConnectType' in objConst1.keys() and objConst1['ConnectType'] == connectionType: qUpdateComplete = 0
            else: objConst1['ConnectType'] = connectionType; qUpdateComplete = 1
            # Calculate orientation between the two elements, imagine a line from center to center
            dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
            if alignVertical:
                # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
            objConst1.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second) *correction
            objConst1['BrkThreshold1'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            if qUpdateComplete:
                objConst1.rotation_mode = 'QUATERNION'
                objConst1.rigid_body_constraint.type = 'GENERIC'
                objConst1.empty_draw_size = emptyDrawSize
                ### Lock all directions for the compressive force
                ### I left Y and Z unlocked because for this CT we have no separate breaking threshold for lateral force, the tensile constraint and its breaking threshold should apply for now
                ### Also rotational forces should only be carried by the tensile constraint
                objConst1.rigid_body_constraint.use_limit_lin_x = 1
                objConst1.rigid_body_constraint.use_limit_lin_y = 0
                objConst1.rigid_body_constraint.use_limit_lin_z = 0
                objConst1.rigid_body_constraint.limit_lin_x_lower = 0
                objConst1.rigid_body_constraint.limit_lin_x_upper = 99999
                objConst1.rigid_body_constraint.use_limit_ang_x = 0
                objConst1.rigid_body_constraint.use_limit_ang_y = 0
                objConst1.rigid_body_constraint.use_limit_ang_z = 0
            # Align constraint rotation to that vector
            objConst1.rotation_quaternion = dirVec.to_track_quat('X','Z')
            ### Second constraint
            objConst2 = emptyObjs[consts[1]]
            objConst2.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second) *correction
            objConst2['BrkThreshold2'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst2.rigid_body_constraint.use_breaking = constraintUseBreaking
            if qUpdateComplete:
                objConst2.rotation_mode = 'QUATERNION'
                objConst2.rigid_body_constraint.type = 'GENERIC'
                objConst2.empty_draw_size = emptyDrawSize
                ### Lock all directions for the tensile force
                objConst2.rigid_body_constraint.use_limit_lin_x = 1
                objConst2.rigid_body_constraint.use_limit_lin_y = 1
                objConst2.rigid_body_constraint.use_limit_lin_z = 1
                objConst2.rigid_body_constraint.limit_lin_x_lower = -99999
                objConst2.rigid_body_constraint.limit_lin_x_upper = 0
                objConst2.rigid_body_constraint.limit_lin_y_lower = 0
                objConst2.rigid_body_constraint.limit_lin_y_upper = 0
                objConst2.rigid_body_constraint.limit_lin_z_lower = 0
                objConst2.rigid_body_constraint.limit_lin_z_upper = 0
                objConst2.rigid_body_constraint.use_limit_ang_x = 1
                objConst2.rigid_body_constraint.use_limit_ang_y = 1
                objConst2.rigid_body_constraint.use_limit_ang_z = 1
                objConst2.rigid_body_constraint.limit_ang_x_lower = 0
                objConst2.rigid_body_constraint.limit_ang_x_upper = 0
                objConst2.rigid_body_constraint.limit_ang_y_lower = 0
                objConst2.rigid_body_constraint.limit_ang_y_upper = 0
                objConst2.rigid_body_constraint.limit_ang_z_lower = 0
                objConst2.rigid_body_constraint.limit_ang_z_upper = 0
            # Align constraint rotation like above
            objConst2.rotation_quaternion = dirVec.to_track_quat('X','Z')
            ### Add to Bullet constraint group in case it got removed for some reason
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst1)
            except: pass
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst2)
            except: pass
            
        elif connectionType == 5:
            # Correction multiplier for breaking thresholds
            # For now this is a hack as it appears that generic constraints need a significant higher breaking thresholds compared to fixed or point constraints for bearing same force (like 10 instead of 4.5)
            # It's not yet clear how to resolve the issue, this needs definitely more research. First tests indicated it could be an precision problem as with extremely high simulation step and iteration rates it could be resolved, but for large structures this isn't really an option.
            correction = 2
            ### First constraint
            objConst1 = emptyObjs[consts[0]]
            # Check if full update is necessary (optimization)
            if 'ConnectType' in objConst1.keys() and objConst1['ConnectType'] == connectionType: qUpdateComplete = 0
            else: objConst1['ConnectType'] = connectionType; qUpdateComplete = 1
            # Calculate orientation between the two elements, imagine a line from center to center
            dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
            if alignVertical:
                # Reduce X and Y components by factor of alignVertical (should be < 1 to make horizontal connections still possible)
                dirVec = Vector((dirVec[0] *(1 -alignVertical), dirVec[1] *(1 -alignVertical), dirVec[2]))
            objConst1.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second) *correction
            objConst1['BrkThreshold1'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            if qUpdateComplete:
                objConst1.rotation_mode = 'QUATERNION'
                objConst1.rigid_body_constraint.type = 'GENERIC'
                objConst1.empty_draw_size = emptyDrawSize
                ### Lock all directions for the compressive force
                objConst1.rigid_body_constraint.use_limit_lin_x = 1
                objConst1.rigid_body_constraint.use_limit_lin_y = 0
                objConst1.rigid_body_constraint.use_limit_lin_z = 0
                objConst1.rigid_body_constraint.limit_lin_x_lower = 0
                objConst1.rigid_body_constraint.limit_lin_x_upper = 99999
                objConst1.rigid_body_constraint.use_limit_ang_x = 0
                objConst1.rigid_body_constraint.use_limit_ang_y = 0
                objConst1.rigid_body_constraint.use_limit_ang_z = 0
                #objConst1.rigid_body_constraint.disable_collisions = False   # Can reduce instability (explosion-like repelling)
            # Align constraint rotation to that vector
            objConst1.rotation_quaternion = dirVec.to_track_quat('X','Z')
            ### Second constraint
            objConst2 = emptyObjs[consts[1]]
            objConst2.rigid_body_constraint.breaking_threshold = (( contactArea *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second) *correction
            objConst2['BrkThreshold2'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst2.rigid_body_constraint.use_breaking = constraintUseBreaking
            if qUpdateComplete:
                objConst2.rotation_mode = 'QUATERNION'
                objConst2.rigid_body_constraint.type = 'GENERIC'
                objConst2.empty_draw_size = emptyDrawSize
                ### Lock all directions for the tensile force
                objConst2.rigid_body_constraint.use_limit_lin_x = 1
                objConst2.rigid_body_constraint.use_limit_lin_y = 1
                objConst2.rigid_body_constraint.use_limit_lin_z = 1
                objConst2.rigid_body_constraint.limit_lin_x_lower = -99999
                objConst2.rigid_body_constraint.limit_lin_x_upper = 0
                objConst2.rigid_body_constraint.limit_lin_y_lower = 0
                objConst2.rigid_body_constraint.limit_lin_y_upper = 0
                objConst2.rigid_body_constraint.limit_lin_z_lower = 0
                objConst2.rigid_body_constraint.limit_lin_z_upper = 0
                objConst2.rigid_body_constraint.use_limit_ang_x = 0
                objConst2.rigid_body_constraint.use_limit_ang_y = 0
                objConst2.rigid_body_constraint.use_limit_ang_z = 0
                #objConst2.rigid_body_constraint.disable_collisions = False   # Can reduce instability (explosion-like repelling)
            # Align constraint rotation like above
            objConst2.rotation_quaternion = dirVec.to_track_quat('X','Z')
            ### Third constraint
            objConst3 = emptyObjs[consts[2]]
            objConst3.rigid_body_constraint.breaking_threshold = (( (contactArea *thickness *0.33) *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second) *correction
            objConst3['BrkThreshold3'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst3.rigid_body_constraint.use_breaking = constraintUseBreaking
            if qUpdateComplete:
                objConst3.rotation_mode = 'QUATERNION'
                objConst3.rigid_body_constraint.type = 'GENERIC'
                objConst3.empty_draw_size = emptyDrawSize
                ### Lock all directions for the lateral tensile and bending force
                objConst3.rigid_body_constraint.use_limit_lin_x = 0
                objConst3.rigid_body_constraint.use_limit_lin_y = 0
                objConst3.rigid_body_constraint.use_limit_lin_z = 0
                objConst3.rigid_body_constraint.use_limit_ang_x = 1
                objConst3.rigid_body_constraint.use_limit_ang_y = 1
                objConst3.rigid_body_constraint.use_limit_ang_z = 1
                objConst3.rigid_body_constraint.limit_ang_x_lower = 0 
                objConst3.rigid_body_constraint.limit_ang_x_upper = 0 
                objConst3.rigid_body_constraint.limit_ang_y_lower = 0
                objConst3.rigid_body_constraint.limit_ang_y_upper = 0
                objConst3.rigid_body_constraint.limit_ang_z_lower = 0
                objConst3.rigid_body_constraint.limit_ang_z_upper = 0
                #objConst3.rigid_body_constraint.disable_collisions = False   # Can reduce instability (explosion-like repelling)
            # Align constraint rotation like above
            objConst3.rotation_quaternion = dirVec.to_track_quat('X','Z')
            ### Add to Bullet constraint group in case it got removed for some reason
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst1)
            except: pass
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst2)
            except: pass
            try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst3)
            except: pass
            
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
        facing = elemGrps[objsEGrp[k]][9]
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
            ### Remove child object from rigid body world (should not be simulated anymore)
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_remove()
        
            if len(childObjsNew) > 0: print()
            
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
        scale = elemGrps[objsEGrp[k]][8]
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
                scale = elemGrps[objsEGrp[k]][8]
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
        qBevel = elemGrps[objsEGrp[k]][7]
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
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
    
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
            ### Remove child object from rigid body world (should not be simulated anymore)
            bpy.context.scene.objects.active = childObj
            bpy.ops.rigidbody.object_remove()
            
    if len(childObjs) > 0: print()
            
################################################################################   
################################################################################   
    
def execute():
    
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
        
        #########################
        ###### Create new empties
        if not "bcb_objs" in scene.keys():
                
            # Remove instancing from objects
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)
           
            ###### Create object lists of selected objects
            childObjs = []
            objs, emptyObjs = gatherObjects(scene)
            objsEGrp = createElementGroupIndex(objs)
            
            if len(objs) > 1:
                #############################
                ###### Prepare connection map
                time_start_connections = time.time()
                
                ###### Find connections by vertex pairs
                #connectsPair = findConnectionsByVertexPairs(objs, objsEGrp)
                ###### Find connections by boundary box intersection
                connectsPair = findConnectionsByBoundaryBoxIntersection(objs, objsEGrp)
                ###### Delete connections with too few connected vertices
                connectsPair = deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair)
                ###### Calculate contact area for all connections
                if useAccurateArea:
                    connectsArea, connectsLoc = calculateContactAreaBasedOnBooleans(objs, connectsPair)
                else:
                    connectsArea, connectsLoc = calculateContactAreaBasedOnBoundaryBoxes(objs, connectsPair)
                ###### Delete connections with zero contact area
                connectsPair, connectsArea, connectsLoc = deleteConnectionsWithZeroContactArea(objs, objsEGrp, connectsPair, connectsArea, connectsLoc)
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
                    ###### Create empty objects (without any data)
                    emptyObjs = createEmptyObjs(scene, len(constsConnect))
                    ###### Bundling close empties into clusters, merge locations and count connections per cluster
                    if clusterRadius > 0: bundlingEmptyObjsToClusters(connectsLoc, connectsConsts)
                    ###### Add constraint base settings to empties
                    addBaseConstraintSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect)
                    ###### Store build data in scene
                    storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect)
                    
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
        if "bcb_objs" in scene.keys():
            
            ###### Store menu config data in scene
            storeConfigDataInScene(scene)
            ###### Get temp data from scene
            objs, emptyObjs, childObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect = getBuildDataFromScene(scene)
            ###### Create fresh element group index to make sure the data is still valid (reordering in menu invalidates it for instance)
            objsEGrp = createElementGroupIndex(objs)
            ###### Store build data in scene
            storeBuildDataInScene(scene, None, objsEGrp, None, None, None, None, None, None, None)
                            
            if len(emptyObjs) > 0:
                ###### Set constraint settings
                setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsArea, connectsConsts, constsConnect)
                ###### Calculate mass for all mesh objects
                calculateMass(scene, objs, objsEGrp, childObjs)
                
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

           
def unregister():
    for c in classes:
        bpy.utils.unregister_class(c) 
    del bpy.types.WindowManager.bcb
 
 
if __name__ == "__main__":
    if withGUI:
        register()
    else:
        execute()
