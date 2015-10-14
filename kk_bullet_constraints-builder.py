###################################################
# Bullet Constraints Builder v1.62 by Kai Kostack #
###################################################
   
### Vars for constraint distribution
withGUI = 1    # Enable graphical user interface, after pressing the "Run Script" button the menu panel should appear

constraintUseBreaking = 1    # 1     | Enables breaking for all constraints
connectionCountLimit = 150   # 150   | Maximum count of connections per object pair (0 = disabled)
searchDistance = 0.13        # 0.15  | Search distance to neighbor geometry
clusterRadius = 0.4          # 0.4   | Radius for bundling close constraints into clusters (0 = clusters disabled)

# Customizable element groups list (for elements of different conflicting groups priority is defined by the list's order)
elemGrps = [ \
# 0          1    2           3        4   5    6    7
# Name       RVP  Mat.preset  Density  CT  BTC  BTT  Bevel
[ "",        1,   "Concrete", 0,       3,  5,  5,  1  ],   # Defaults to be used when element is not part of any element group
[ "Slabs",   1,   "Concrete", 0,       3,  5,  5,  1  ],
[ "Walls",   1,   "Concrete", 0,       3,  5,  5,  1  ],
[ "Girders", 1,   "Concrete", 0,       3,  5,  5,  1  ],
[ "Columns", 1,   "Concrete", 0,       3,  5,  5,  1  ]
]

# Column descriptions (in order from left to right):
#
# Required Vertex Pairs | How many vertex pairs between two elements are required to generate a constraint.
# (Depreciated)         | This can help to ensure there is an actual surface to surface connection between both elements (for at least 3 verts you can expect a shared surface).
#                       | For two elements from different groups with different RVPs the lower number is decisive.
# Material Preset       | Preset name of the physical material to be used from Blender's internal database.
#                       | See Blender's Rigid Body Tools for a list of available presets.
# Material Density      | Custom density value (kg/m^3) to use instead of material preset (0 = disabled).
# Connection Type       | Connection type ID for the constraint presets defined by this script, see list below.
# Break.Thresh.Compres. | Real world material compressive breaking threshold in N/mm^2.
# Break.Thresh.Tensile  | Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).
# Bevel                 | Use beveling for elements

# Connection types:
#
# 1 = 1x 'FIXED' constraint per connection, only compressive breaking threshold is used (tensile limit is the same, angular forces limit as well)
# 2 = 1x 'POINT' constraint per connection, only compressive breaking threshold is used (tensile limit is the same)
# 3 = 1x 'FIXED' & 1x 'POINT' constraint per connection, compressive breaking threshold is used for the first one and tensile for the second
# 4 = 2x 'GENERIC' constraint per connection, one to evaluate the compressive and the other the tensile breaking threshold

### Constants
maxMenuElementGroupItems = len(elemGrps) +100    # Maximum allowed element group entries in menu 

########################################

elemGrpsBak = elemGrps.copy()

################################################################################   

bl_info = {
    "name": "Bullet Constraints Builder",
    "author": "Kai Kostack",
    "version": (1, 6, 2),
    "blender": (2, 7, 5),
    "location": "View3D > Toolbar",
    "description": "Tool to connect rigid bodies via constraints in a physical plausible way.",
    "wiki_url": "http://www.inachus.eu",
    "tracker_url": "http://kaikostack.com",
    "category": "Animation"}

import bpy, sys, mathutils, time, copy
from mathutils import Vector
#import os
#os.system("cls")

################################################################################
################################################################################

def storeConfigDataInScene(scene):

    ### Store menu config data in scene
    scene["bcb_constraintUseBreaking"] = constraintUseBreaking
    scene["bcb_connectionCountLimit"] = connectionCountLimit
    scene["bcb_searchDistance"] = searchDistance
    scene["bcb_clusterRadius"] = clusterRadius
    
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    #scene["bcb_elemGrps"] = elemGrps
    elemGrpsInverted = []
    for i in range(len(elemGrps[0])):
        column = []
        for j in range(len(elemGrps)):
            column.append(elemGrps[j][i])
        elemGrpsInverted.append(column)
    scene["bcb_elemGrps"] = elemGrpsInverted

################################################################################   

def getConfigDataFromScene(scene):
    
    ### Get menu config data from scene
    props = bpy.context.window_manager.bcb
    if "bcb_constraintUseBreaking" in scene.keys():
        global constraintUseBreaking; constraintUseBreaking = props.constraintUseBreaking = scene["bcb_constraintUseBreaking"]
    if "bcb_connectionCountLimit" in scene.keys():
        global connectionCountLimit; connectionCountLimit = props.connectionCountLimit = scene["bcb_connectionCountLimit"]
    if "bcb_searchDistance" in scene.keys():
        global searchDistance; searchDistance = props.searchDistance = scene["bcb_searchDistance"]
    if "bcb_clusterRadius" in scene.keys():
        global clusterRadius; clusterRadius = props.clusterRadius = scene["bcb_clusterRadius"]
            
    ### Because ID properties doesn't support different var types per list I do the trick of inverting the 2-dimensional elemGrps array
    elemGrps = scene["bcb_elemGrps"]
    elemGrpsInverted = []
    for i in range(len(elemGrps[0])):
        column = []
        for j in range(len(elemGrps)):
            column.append(elemGrps[j][i])
        elemGrpsInverted.append(column)
    global elemGrps
    elemGrps = elemGrpsInverted
    
################################################################################   

def storeTempDataInScene(scene, objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect):
    
    ### Store temp data in scene
    scene["bcb_objs"] = [obj.name for obj in objs]
    scene["bcb_objsEGrp"] = objsEGrp
    scene["bcb_emptyObjs"] = [obj.name for obj in emptyObjs]
    scene["bcb_connectsPair"] = connectsPair
    scene["bcb_connectsLoc"] = connectsLoc
    scene["bcb_connectsArea"] = connectsArea
    scene["bcb_connectsConsts"] = connectsConsts
    scene["bcb_constsConnect"] = constsConnect    
                    
################################################################################   

def getTempDataFromScene(scene):
    
    ### Get temp data from scene
    names = scene["bcb_objs"]; objs = [scene.objects[name] for name in names]
    objsEGrp = scene["bcb_objsEGrp"]
    names = scene["bcb_emptyObjs"]; emptyObjs = [scene.objects[name] for name in names]
    connectsPair = scene["bcb_connectsPair"]
    connectsLoc = scene["bcb_connectsLoc"]
    connectsArea = scene["bcb_connectsArea"]
    connectsConsts = scene["bcb_connectsConsts"]
    constsConnect = scene["bcb_constsConnect"]
    
    return objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect

################################################################################   

def clearAllDataFromScene(scene):
    
    ### Clear all data related to Bullet Constraint Builder from scene
    
    # Store layer settings and activate all layers
    layers = []
    for i in range(20):
        layers.append(int(scene.layers[i]))
        scene.layers[i] = 1
       
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    ### Start by deleting constraint empty objects from scene
    names = scene["bcb_emptyObjs"]
    for name in names: scene.objects[name].select = 1
    bpy.ops.object.delete(use_global=True)
        
    ### Select rigid bodies to revert also selection back to original state
    names = scene["bcb_objs"]
    for name in names: scene.objects[name].select = 1
    
    ### Remove only one bevel modifier and copy that to the other selected objects (Todo: Should be done for each object individually but is slower)
    obj = scene.objects[names[0]]
    if obj != None:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.modifier_remove(modifier="Bevel_bcb")
        bpy.ops.object.make_links_data(type='MODIFIERS')
    
    ### Finally remove all ID property data
    for key in scene.keys():
        if "bcb_" in key: del scene[key]
    
    # Set layers as in original scene
    for i in range(20): scene.layers[i] = layers[i]
        
################################################################################   
################################################################################

class bcb_props(bpy.types.PropertyGroup):
    int = bpy.props.IntProperty 
    float = bpy.props.FloatProperty
    bool = bpy.props.BoolProperty
    string = bpy.props.StringProperty
    
    menu_gotConfig = int(0)
    menu_selectedItem = int(0)
    
    constraintUseBreaking = bool(name="Enable Breaking", default=constraintUseBreaking, description="Enables breaking for all constraints.")
    connectionCountLimit = int(name="Con.Count Limit", default=connectionCountLimit, min=0, max=10000, description="Maximum count of connections per object pair (0 = disabled).")
    searchDistance = float(name="Search Distance", default=searchDistance, min=0.0, max=1000, description="Search distance to neighbor geometry.")
    clusterRadius = float(name="Cluster Radius", default=clusterRadius, min=0.0, max=1000, description="Radius for bundling close constraints into clusters (0 = clusters disabled).")
    
    for i in range(maxMenuElementGroupItems):
        if i < len(elemGrps): j = i
        else: j = 0
        exec("elemGrp_%d_0" %i +" = string(name='Grp.Name', default=elemGrps[j][0], description='The name of the element group.')")
        exec("elemGrp_%d_4" %i +" = int(name='Connect.Type', default=elemGrps[j][4], min=1, max=4, description='Connection type ID for the constraint presets defined by this script, see list in code.')")
        exec("elemGrp_%d_5" %i +" = float(name='Brk.Trs.Compressive', default=elemGrps[j][5], min=0.0, max=10000, description='Real world material compressive breaking threshold in N/mm^2.')")
        exec("elemGrp_%d_6" %i +" = float(name='Brk.Trs.Tensile', default=elemGrps[j][6], min=0.0, max=10000, description='Real world material tensile breaking threshold in N/mm^2 (not used by all constraint types).')")
        exec("elemGrp_%d_1" %i +" = int(name='Req.Vert.Pairs', default=elemGrps[j][1], min=0, max=100, description='How many vertex pairs between two elements are required to generate a constraint.')")
        exec("elemGrp_%d_2" %i +" = string(name='Mat.Preset', default=elemGrps[j][2], description='Preset name of the physical material to be used from Blender´s internal database. See Blender´s Rigid Body Tools for a list of available presets.')")
        exec("elemGrp_%d_3" %i +" = float(name='Mat.Density', default=elemGrps[j][3], min=0.0, max=100000, description='Custom density value (kg/m^3) to use instead of material preset (0 = disabled).')")
        exec("elemGrp_%d_7" %i +" = bool(name='Bevel', default=elemGrps[j][7], description='Use beveling for elements to avoid `Jenga effect´.')")
        
    def props_update_menu(self):
        ### Update menu related properties from global vars
        for i in range(len(elemGrps)):
            exec("self.elemGrp_%d_0" %i +" = elemGrps[i][0]")
            exec("self.elemGrp_%d_4" %i +" = elemGrps[i][4]")
            exec("self.elemGrp_%d_5" %i +" = elemGrps[i][5]")
            exec("self.elemGrp_%d_6" %i +" = elemGrps[i][6]")
            exec("self.elemGrp_%d_1" %i +" = elemGrps[i][1]")
            exec("self.elemGrp_%d_2" %i +" = elemGrps[i][2]")
            exec("self.elemGrp_%d_3" %i +" = elemGrps[i][3]")
            exec("self.elemGrp_%d_7" %i +" = elemGrps[i][7]")
        
    def props_update_globals(self):
        ### Update global vars from menu related properties
        global constraintUseBreaking; constraintUseBreaking = self.constraintUseBreaking
        global connectionCountLimit; connectionCountLimit = self.connectionCountLimit
        global searchDistance; searchDistance = self.searchDistance
        global clusterRadius; clusterRadius = self.clusterRadius
        global elemGrps
        for i in range(len(elemGrps)):
            elemGrpNew = []
            for j in range(len(elemGrps[i])):
                elemGrpNew.append(eval("self.elemGrp_%d_%d" %(i, j)))
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
        if not props.menu_gotConfig: 
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.execute", icon="MOD_SKIN")
            split2 = split.row()
            if "bcb_objs" in scene.keys(): split2.enabled = 1
            else: split2.enabled = 0
            split2.operator("bcb.get_config", icon="FILE_REFRESH")
        else:
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split.operator("bcb.clear", icon="CANCEL")
        
        row = layout.row(); row.prop(props, "constraintUseBreaking")
        row = layout.row(); row.prop(props, "connectionCountLimit")
        row = layout.row(); row.prop(props, "searchDistance")
        row = layout.row(); row.prop(props, "clusterRadius")
        
        layout.separator()
        row = layout.row(); row.label(text="Element Groups", icon="MOD_BUILD")
        frm = layout.box()
        for i in range(len(elemGrps)):
            if i == props.menu_selectedItem:
                  row = frm.box().row()
            else: row = frm.row()
            elemGrp0 = eval("props.elemGrp_%d_0" %i)
            elemGrp4 = eval("props.elemGrp_%d_4" %i)
            elemGrp5 = eval("props.elemGrp_%d_5" %i)
            elemGrp6 = eval("props.elemGrp_%d_6" %i)
            split = row.split(percentage=.35, align=False)
            if elemGrp0 == "": split.label(text="[Def.]")
            else:              split.label(text=str(elemGrp0))
            split2 = split.split(percentage=.22, align=False)
            split2.label(text=str(elemGrp4))
            split2.label(text=str(elemGrp5))
            split2.label(text=str(elemGrp6))
        row = frm.row()
        row.operator("bcb.add", icon="PLUS")
        row.operator("bcb.del", icon="X")
        row.operator("bcb.reset", icon="CANCEL")
        row.operator("bcb.up", icon="TRIA_UP")
        row.operator("bcb.down", icon="TRIA_DOWN")
        layout.separator()
        
        i = props.menu_selectedItem
        row = layout.row(); row.prop(props, "elemGrp_%d_0" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_4" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_5" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_6" %i)
        #row = layout.row(); row.prop(props, "elemGrp_%d_1" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_2" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_3" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_7" %i)
       
        # Update global vars from menu related properties
        props.props_update_globals()
 
        
class OBJECT_OT_bcb_get_config(bpy.types.Operator):
    bl_idname = "bcb.get_config"
    bl_label = "Get Config"
    bl_description = "Loads previous config data from current scene."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        if "bcb_elemGrps" in scene.keys():
            ###### Get menu config data from scene
            getConfigDataFromScene(scene)
        # Update menu related properties from global vars
        props.props_update_menu()
        props.menu_gotConfig = 1
        return{'FINISHED'} 
        
class OBJECT_OT_bcb_execute(bpy.types.Operator):
    bl_idname = "bcb.execute"
    bl_label = "Execute"
    bl_description = "Starts building process and adds constraints to selected elements."
    def execute(self, context):
        props = context.window_manager.bcb
        ###### Execute main building process from scratch
        execute()
        props.menu_gotConfig = 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_update(bpy.types.Operator):
    bl_idname = "bcb.update"
    bl_label = "Update"
    bl_description = "Update constraints generated from a previous built."
    def execute(self, context):
        ###### Execute update of all existing constraints with new settings
        execute()
        return{'FINISHED'} 

class OBJECT_OT_bcb_clear(bpy.types.Operator):
    bl_idname = "bcb.clear"
    bl_label = "Clear"
    bl_description = "Clear constraints from scene and revert back to original state (required to rebuild constraints from scratch)."
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Clear all data from scene and delete also constraint empty objects
        if "bcb_objs" in scene.keys(): clearAllDataFromScene(scene)
        props.menu_gotConfig = 0
        return{'FINISHED'} 

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = " Add"
    bl_description = "Add element group to list."
    def execute(self, context):
        props = context.window_manager.bcb
        if len(elemGrps) < maxMenuElementGroupItems:
            elemGrps.append(elemGrps[props.menu_selectedItem])
            props.menu_selectedItem = len(elemGrps) -1
        else: self.report({'ERROR'}, "Maximum allowed element group count reached.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_del(bpy.types.Operator):
    bl_idname = "bcb.del"
    bl_label = " Delete"
    bl_description = "Delete element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if len(elemGrps) > 1:
            elemGrps.remove(elemGrps[props.menu_selectedItem])
            if props.menu_selectedItem >= len(elemGrps):
                props.menu_selectedItem = len(elemGrps) -1
        else: self.report({'ERROR'}, "At least one element group is required.")
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

class OBJECT_OT_bcb_up(bpy.types.Operator):
    bl_idname = "bcb.up"
    bl_label = " Up"
    bl_description = "Select element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.menu_selectedItem > 0:
            props.menu_selectedItem -= 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_down(bpy.types.Operator):
    bl_idname = "bcb.down"
    bl_label = " Down"
    bl_description = "Select element group from list."
    def execute(self, context):
        props = context.window_manager.bcb
        if props.menu_selectedItem < len(elemGrps) -1:
            props.menu_selectedItem += 1
        return{'FINISHED'} 

class OBJECT_OT_bcb_reset(bpy.types.Operator):
    bl_idname = "bcb.reset"
    bl_label = " Reset"
    bl_description = "Reset element group list to defaults."
    def execute(self, context):
        props = context.window_manager.bcb
        global elemGrps
        elemGrps = elemGrpsBak.copy()
        props.menu_selectedItem = 0
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 


classes = [ \
    bcb_props,
    bcb_panel,
    OBJECT_OT_bcb_get_config,
    OBJECT_OT_bcb_execute,
    OBJECT_OT_bcb_update,
    OBJECT_OT_bcb_clear,
    OBJECT_OT_bcb_add,
    OBJECT_OT_bcb_del,
    OBJECT_OT_bcb_up,
    OBJECT_OT_bcb_down,
    OBJECT_OT_bcb_reset
    ]      
          
################################################################################   
################################################################################   

def gatherObjects(scene):

    ### Create object lists of selected objects
    print("\nGathering objects...")
    objs = []
    objsEGrp = []
    emptyObjs = []
    for obj in bpy.data.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            # Clear object properties
            for key in obj.keys(): del obj[key]
            # Detect if mesh or empty (constraint)
            if obj.type == 'MESH':
                sys.stdout.write('\r' +"%s      " %obj.name)
                objs.append(obj)
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
            elif obj.type == 'EMPTY':
                if obj.rigid_body_constraint != None:
                    sys.stdout.write('\r' +"%s      " %obj.name)
                    emptyObjs.append(obj)
    
    return objs, objsEGrp, emptyObjs

################################################################################   

def findConnectionsByVertexPairs(objs, objsEGrp):
    
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
    connectsLocs = []          # Stores locations of the connections
    count = 0
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
                        constCnt = 0
                        pair = [k, l]
                        pair.sort()
                        if pair not in connectsPair:
                            connectsPair.append(pair)
                            if clusterRadius > 0: connectsLocs.append([co])
                            else:                 connectsLocs.append([(objs[k].location +objs[l].location) /2])
                            constCnt += 1
                            count += 1
                            if constCnt == connectionCountLimit:
                                if elemGrps[objsEGrp[k]][1] <= 1:
                                    qNextObj = 1
                                    break
                        else:
                            if clusterRadius > 0: connectsLocs[connectsPair.index(pair)].append(co)
                            else:                 connectsLocs[connectsPair.index(pair)].append((objs[k].location +objs[l].location) /2)   # Not really necessary only needed for counting vertex pairs (items will be averaged later on)
                            
            if qNextObj: break
        
    return connectsPair, connectsLocs

################################################################################   

def deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair, connectsLocs):
    
    ### Delete connections with too few connected vertices
    connectsPairTmp = []
    connectsLocsTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        locs = connectsLocs[i]
        vertPairCnt = len(connectsLocs[i]) /2
        reqVertexPairsObjA = elemGrps[objsEGrp[objs.index(objs[pair[0]])]][1]
        reqVertexPairsObjB = elemGrps[objsEGrp[objs.index(objs[pair[1]])]][1]
        if vertPairCnt >= reqVertexPairsObjA and vertPairCnt >= reqVertexPairsObjB:
            connectsPairTmp.append(pair)
            connectsLocsTmp.append(locs)
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsLocs = connectsLocsTmp
    print("\n%d connections skipped due to too few connecting vertices." %(connectCntOld -connectCnt))
    print(connectCnt)
    
    return connectsPair, connectsLocs
        
################################################################################   

def calculateContactAreaForConnections(objs, connectsPair):
    
    ### Calculate contact area for all connections
    print("\nCalculate cross area for all connections...")
    connectsArea = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
    
        ### Calculate contact surface area from boundary box projection
        ### Requires the object pivot to be centered
        dimAhalf = objA.dimensions /2
        dimBhalf = objB.dimensions /2
        bbAMin = objA.location -dimAhalf
        bbAMax = objA.location +dimAhalf
        bbBMin = objB.location -dimBhalf
        bbBMax = objB.location +dimBhalf
        ### Project along all axis'
        overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
        overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
        overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
        overlapAreaX = overlapY *overlapZ
        overlapAreaY = overlapX *overlapZ
        overlapAreaZ = overlapX *overlapY
        # Add up all contact areas
        crossArea = overlapAreaX +overlapAreaY +overlapAreaZ
        connectsArea.append(crossArea)
        
    return connectsArea

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, objsEGrp, connectsPair, connectsLocs, connectsArea):
    
    ### Delete connections with zero contact area
    connectsPairTmp = []
    connectsLocsTmp = []
    connectsAreaTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        locs = connectsLocs[i]
        crossArea = connectsArea[i]
        if crossArea > 0.0001:
            connectsPairTmp.append(pair)
            connectsLocsTmp.append(locs)
            connectsAreaTmp.append(crossArea)
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsLocs = connectsLocsTmp
    connectsArea = connectsAreaTmp
    print("\n%d connections skipped due to zero contact area." %(connectCntOld -connectCnt))
    
    return connectsPair, connectsLocs, connectsArea

################################################################################   

def calculateBoundaryBoxOfVertexPairs(connectsLocs):
    
    ### Calculate boundary box center of valid vertex pairs per connection
    connectsLoc = []
    for connectLocs in connectsLocs:
        if len(connectLocs) > 1:
            bbMin = connectLocs[0].copy()
            bbMax = connectLocs[0].copy()
            for connectLoc in connectLocs:
                loc = connectLoc.copy()
                if bbMax[0] < loc[0]: bbMax[0] = loc[0]
                if bbMin[0] > loc[0]: bbMin[0] = loc[0]
                if bbMax[1] < loc[1]: bbMax[1] = loc[1]
                if bbMin[1] > loc[1]: bbMin[1] = loc[1]
                if bbMax[2] < loc[2]: bbMax[2] = loc[2]
                if bbMin[2] > loc[2]: bbMin[2] = loc[2]
            bbCenter = (bbMin +bbMax) /2
            connectsLoc.append(bbCenter)
        else:
            connectsLoc.append(connectLocs[0])
        
    return connectsLoc

################################################################################   

def createConnectionData(objsEGrp, connectsPair, connectsLoc):
    
    ### Create connection data
    connectsConsts = []
    constsConnect = []
    constCnt = 0
    for i in range(len(connectsPair)):
        pair = connectsPair[i]
        co = connectsLoc[i]
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
    
    return connectsPair, connectsLoc, connectsConsts, constsConnect

################################################################################   

def createEmptyObjs(scene, constCnt):
    
    ### Create first object
    objConst = bpy.data.objects.new('Constraint', None)
    scene.objects.link(objConst)
    objConst.empty_draw_type = 'SPHERE'
    objConst.empty_draw_size = searchDistance
    bpy.context.scene.objects.active = objConst
    bpy.ops.rigidbody.constraint_add()
    emptyObjs = [objConst]
    ### Duplicate them as long as we got the desired count   
    while len(emptyObjs) < constCnt:
        sys.stdout.write("%d\n" %len(emptyObjs))
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

    return emptyObjs        

################################################################################   

def bundlingEmptyObjsToClusters(connectsLoc, connectsConsts):
    
    ### Bundling close empties into clusters, merge locations and count connections per cluster
    if clusterRadius > 0:
        print("\nBundling close empties into clusters...")
        
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
            
################################################################################   

def addConstraintBaseSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect):
    
    ### Add constraint base settings to empties
    print("\nAdd constraint settings to empties...")
    for k in range(len(emptyObjs)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(emptyObjs))
                
        objConst = emptyObjs[k]
        l = constsConnect[k]
        objConst.location = connectsLoc[l]
        objConst.rigid_body_constraint.object1 = objs[connectsPair[l][0]]
        objConst.rigid_body_constraint.object2 = objs[connectsPair[l][1]]
                
################################################################################   
    
def setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect):
    
    ### Set constraint settings
    count = 0
    for k in range(len(connectsPair)):
        sys.stdout.write('\r' +"%d" %k)
        # Update progress bar
        bpy.context.window_manager.progress_update(k /len(connectsPair))
        
        consts = connectsConsts[k]
        crossArea = connectsArea[k]
        for idx in consts: emptyObjs[idx]['CrossArea'] = crossArea   # Store value as ID property for debug purposes
        
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
            objConst1.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
        
        elif connectionType == 2:
            objConst1 = emptyObjs[consts[0]]
            objConst1.rigid_body_constraint.type = 'POINT'
            objConst1.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
        
        elif connectionType == 3:
            ### First constraint
            objConst1 = emptyObjs[consts[0]]
            objConst1.rigid_body_constraint.type = 'FIXED'
            objConst1.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Second constraint
            objConst2 = emptyObjs[consts[1]]
            objConst2.rigid_body_constraint.type = 'POINT'
            objConst2.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst2['BrkThreshold'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst2.rigid_body_constraint.use_breaking = constraintUseBreaking
        
        elif connectionType == 4:
            ### First constraint
            objConst1 = emptyObjs[consts[0]]
            # Calculate orientation between the two elements, imagine a line from center to center
            dirVec = objB.matrix_world.to_translation() -objA.matrix_world.to_translation()   # Use actual locations (taking parent relationships into account)
            # Align constraint rotation to that line
            objConst1.rotation_mode = 'QUATERNION'
            objConst1.rotation_quaternion = dirVec.to_track_quat('X','Z')
            objConst1.rigid_body_constraint.type = 'GENERIC'
            objConst1.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold1 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst1['BrkThreshold'] = breakingThreshold1   # Store value as ID property for debug purposes
            objConst1.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Lock all directions but the tensile one (compressive is used for breaking theshold)
            ### I left Y and Z unlocked because as long as we have no separate breaking threshold for shearing force, the tensile constraint and its breaking threshold should apply for now
            ### Also rotational forces should only be carried by the tensile constraint
            objConst1.rigid_body_constraint.use_limit_lin_x = 1
            #objConst1.rigid_body_constraint.use_limit_lin_y = 1
            #objConst1.rigid_body_constraint.use_limit_lin_z = 1
            objConst1.rigid_body_constraint.limit_lin_x_lower = 0
            objConst1.rigid_body_constraint.limit_lin_x_upper = 99999
            #objConst1.rigid_body_constraint.limit_lin_y_lower = 0
            #objConst1.rigid_body_constraint.limit_lin_y_upper = 0
            #objConst1.rigid_body_constraint.limit_lin_z_lower = 0
            #objConst1.rigid_body_constraint.limit_lin_z_upper = 0
            #objConst1.rigid_body_constraint.use_limit_ang_x = 1
            #objConst1.rigid_body_constraint.use_limit_ang_y = 1
            #objConst1.rigid_body_constraint.use_limit_ang_z = 1
            #objConst1.rigid_body_constraint.limit_ang_x_lower = 0
            #objConst1.rigid_body_constraint.limit_ang_x_upper = 0
            #objConst1.rigid_body_constraint.limit_ang_y_lower = 0
            #objConst1.rigid_body_constraint.limit_ang_y_upper = 0
            #objConst1.rigid_body_constraint.limit_ang_z_lower = 0
            #objConst1.rigid_body_constraint.limit_ang_z_upper = 0
            ### Second constraint
            objConst2 = emptyObjs[consts[1]]
            # Align constraint rotation like above
            objConst2.rotation_mode = 'QUATERNION'
            objConst2.rotation_quaternion = dirVec.to_track_quat('X','Z')
            objConst2.rigid_body_constraint.type = 'GENERIC'
            objConst2.rigid_body_constraint.breaking_threshold = ( crossArea *1000000 *breakingThreshold2 ) /bpy.context.scene.rigidbody_world.steps_per_second
            objConst2['BrkThreshold'] = breakingThreshold2   # Store value as ID property for debug purposes
            objConst2.rigid_body_constraint.use_breaking = constraintUseBreaking
            ### Lock all directions but the compressive one (tensile is used for breaking theshold)
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
            
        # Add to Bullet group in case someone removed it in the mean time
        try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst)
        except: pass
        
################################################################################   

def calculateMass(objs, objsEGrp):
    
    ### Calculate a mass for all mesh objects
    print("\nCalculating masses from preset material...")
    for obj in objs:
        if obj != None:
            if obj.rigid_body != None:
                obj.select = 1
    elemGrp = elemGrps[objsEGrp[objs.index(obj)]]
    materialPreset = elemGrp[2]
    materialDensity = elemGrp[3]
    if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
    else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
    
################################################################################   

def updateBevel(objs, objsEGrp):
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    obj = None
    ### Select all objects to be beveled
    for k in range(len(objs)):
        qBevel = elemGrps[objsEGrp[k]][7]
        if qBevel:
            obj = objs[k]
            obj.select = 1
    ### Add only one bevel modifier and copy that to the other selected objects (Todo: Should be done for each object individually but is slower)
    if obj != None:
        bpy.context.scene.objects.active = obj
        if "Bevel_bcb" not in obj.modifiers:
            bpy.ops.object.modifier_add(type='BEVEL')
            obj.modifiers["Bevel"].name = "Bevel_bcb"
            obj.modifiers["Bevel_bcb"].width = 10.0
            bpy.ops.object.make_links_data(type='MODIFIERS')
            
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    obj = None
    ### Select all objects not to be beveled
    for k in range(len(objs)):
        qBevel = elemGrps[objsEGrp[k]][7]
        if not qBevel:
            obj = objs[k]
            obj.select = 1
    ### Remove only one bevel modifier and copy that to the other selected objects (Todo: Should be done for each object individually but is slower)
    if obj != None:
        bpy.context.scene.objects.active = obj
        bpy.ops.object.modifier_remove(modifier="Bevel_bcb")
        bpy.ops.object.make_links_data(type='MODIFIERS')
        
################################################################################   
################################################################################   
    
def execute():
    
    print("\nStarting...")
    time_start = time.time()
    
    pi = 3.1415927
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
        objs, objsEGrp, emptyObjs = gatherObjects(scene) 
        
        if len(objs) > 0:
            #############################
            ###### Prepare connection map
            print("\nBuilding connection map for %d objects..." %len(objs))
            time_start_connections = time.time()
            
            ###### Find connections by vertex pairs
            connectsPair, connectsLocs = findConnectionsByVertexPairs(objs, objsEGrp)
            ###### Delete connections with too few connected vertices
            connectsPair, connectsLocs = deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair, connectsLocs)
            ###### Calculate contact area for all connections
            connectsArea = calculateContactAreaForConnections(objs, connectsPair)
            ###### Delete connections with zero contact area
            connectsPair, connectsLocs, connectsArea = deleteConnectionsWithZeroContactArea(objs, objsEGrp, connectsPair, connectsLocs, connectsArea)
            ###### Calculate boundary box center of valid vertex pairs per connection
            connectsLoc = calculateBoundaryBoxOfVertexPairs(connectsLocs)
            ###### Create connection data
            connectsPair, connectsLoc, connectsConsts, constsConnect = createConnectionData(objsEGrp, connectsPair, connectsLoc)
        
            print(' - Time: %0.2f s' %(time.time()-time_start_connections))
            
            #########################                        
            ###### Main building part
            if len(constsConnect) > 0:
                print("\nBuilding %d empties..." %len(constsConnect))
                time_start_building = time.time()
                
                ###### Create empty objects (without any data)
                emptyObjs = createEmptyObjs(scene, len(constsConnect))
                ###### Bundling close empties into clusters, merge locations and count connections per cluster
                bundlingEmptyObjsToClusters(connectsLoc, connectsConsts)
                ###### Add constraint base settings to empties
                addConstraintBaseSettings(objs, emptyObjs, connectsPair, connectsLoc, constsConnect)
                ###### Store temp data in scene
                storeTempDataInScene(scene, objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect)
                
                print(' - Time: %0.2f s' %(time.time()-time_start_building))
            
            ###########################
            ###### No connections found   
            else:
                print('\nNo connections found. Probably the search distance is too small.')       
        
        #####################
        ###### No input found   
        else:
            print('\nNo mesh objects to connect selected.')       
            print('Nothing done.')       
   
    ##########################################     
    ###### Update already existing constraints
    if "bcb_objs" in scene.keys():
        
        ###### Store menu config data in scene
        storeConfigDataInScene(scene)
        ###### Get temp data from scene
        objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect = getTempDataFromScene(scene)
        
        if len(emptyObjs) > 0:
            print("\nUpdating %d selected constraints..." %len(emptyObjs))
            
            ###### Set constraint settings
            setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsArea, connectsConsts, constsConnect)
            ###### Calculate mass for all mesh objects
            calculateMass(objs, objsEGrp)
            ###### Add bevel modifiers
            updateBevel(objs, objsEGrp)
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            # Select all new constraint empties
            for emptyObj in emptyObjs: emptyObj.select = 1
            
            print('\nConstraints:', len(emptyObjs), '- Time total: %0.2f s' %(time.time()-time_start))
            print('Done.')

        #####################
        ###### No input found   
        else:
            print('\nNeither mesh objects to connect nor constraint empties for updating selected.')       
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
