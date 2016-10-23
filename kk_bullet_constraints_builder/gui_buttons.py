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
from global_props import *     # Contains global properties
from global_vars import *      # Contains global variables
from build_data import *       # Contains build data access functions
from builder import *          # Contains constraints builder functions
from builder_fm import *       # Contains constraints builder function for Fracture Modifier (custom Blender version required)
from formula import *          # Contains formula assistant functions
from formula_props import *    # Contains formula assistant properties classes
from monitor import *          # Contains baking monitor event handler
from tools import *            # Contains smaller independently working tools

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
        props.menu_gotConfig = 1
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
            if warning != None and len(warning): self.report({'ERROR'}, warning)  # Create pop-up message
            props.menu_gotConfig = 1
            ###### Get build data from scene
            #getBuildDataFromScene(scene)
            if "bcb_objs" in scene.keys(): props.menu_gotData = 1
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
        props.menu_gotConfig = 0
        props.menu_gotData = 0
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
        try: contextFix['point_cache'] = scene.rigidbody_world.point_cache
        except: pass
        try: bpy.ops.ptcache.free_bake(contextFix)
        except: pass
        ### Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            obj.location = obj.location
        ###### Execute main building process from scratch
        build()
        props.menu_gotData = 1
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

class OBJECT_OT_bcb_export_config(bpy.types.Operator):
    bl_idname = "bcb.export_config"
    bl_label = ""
    bl_description = 'Exports BCB config data to an external file. Location: %s' %logPath
    def execute(self, context):
        scene = bpy.context.scene
        exportConfigData(scene)
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_import_config(bpy.types.Operator):
    bl_idname = "bcb.import_config"
    bl_label = ""
    bl_description = 'Imports BCB config data from an external file. Location: %s' %logPath
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        error = importConfigData(scene)
        if not error:
            props.menu_gotConfig = 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_export_ascii(bpy.types.Operator):
    bl_idname = "bcb.export_ascii"
    bl_label = "Export to Text"
    bl_description = "Exports all constraint data to an ASCII text file within this .blend file instead of creating actual empty objects (only useful for developers at the moment)."
    def execute(self, context):
        props = context.window_manager.bcb
        props.asciiExport = 1
        ###### Execute main building process from scratch
        build()
        props.asciiExport = 0
        return{'FINISHED'}
    
########################################

class OBJECT_OT_bcb_export_ascii_fm(bpy.types.Operator):
    bl_idname = "bcb.export_ascii_fm"
    bl_label = "Export to FM"
    bl_description = "Exports all constraint data to the fracture modifier (special Blender version required). WARNING: This feature is experimental and results of the FM can vary, use with care!"
    def execute(self, context):
        if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'):
            self.report({'ERROR'}, "Fracture modifier not available in this Blender version.")  # Create pop-up message
        else:
            ###### Execute main building process from scratch
            scene = bpy.context.scene
            props = context.window_manager.bcb
            props.asciiExport = 1
            build()
            props.asciiExport = 0
            build_fm()
            if "BCB_export.txt" in bpy.data.texts:
                bpy.data.texts.remove(bpy.data.texts["BCB_export.txt"], do_unlink=1)
                ### Free previous bake data
                contextFix = bpy.context.copy()
                contextFix['point_cache'] = scene.rigidbody_world.point_cache
                bpy.ops.ptcache.free_bake(contextFix)
                if props.automaticMode:
                    # Prepare event handler
                    bpy.app.handlers.frame_change_pre.append(stop_eventHandler)
                    # Invoke baking (old method, appears not to work together with the event handler past Blender v2.76 anymore)
                    #bpy.ops.ptcache.bake(contextFix, bake=True)
                    # Start animation playback and by that the baking process
                    if not bpy.context.screen.is_animation_playing:
                        bpy.ops.screen.animation_play()
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
        if props.menu_gotData:
            print('\nInit BCB monitor event handler.')
            # Free old monitor data if still in memory (can happen if user stops baking before finished)
            monitor_freeBuffers(scene)
            # Prepare event handlers
            bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
            bpy.app.handlers.frame_change_pre.append(stop_eventHandler)
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

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = ""
    bl_description = "Adds element group to list."
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        if len(elemGrps) < maxMenuElementGroupItems:
            # Add element group (syncing element group indices happens on execution)
            elemGrps.append(elemGrps[props.menu_selectedElemGrp].copy())
            # Update menu selection
            props.menu_selectedElemGrp = len(elemGrps) -1
        else: self.report({'ERROR'}, "Maximum allowed element group count reached.")  # Create pop-up message
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
        elemGrps = mem["elemGrps"]
        scene = bpy.context.scene
        if len(elemGrps) > 1:
            # Remove element group (syncing element group indices happens on execution)
            elemGrps.remove(elemGrps[props.menu_selectedElemGrp])
            # Update menu selection
            if props.menu_selectedElemGrp >= len(elemGrps):
                props.menu_selectedElemGrp = len(elemGrps) -1
        else: self.report({'ERROR'}, "At least one element group is required.")  # Create pop-up message
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
        elemGrps = mem["elemGrps"]
        scene = bpy.context.scene
        if props.menu_selectedElemGrp > 0:
            swapItem = props.menu_selectedElemGrp -1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.menu_selectedElemGrp] = elemGrps[props.menu_selectedElemGrp], elemGrps[swapItem]
            # Also move menu selection
            props.menu_selectedElemGrp -= 1
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
        elemGrps = mem["elemGrps"]
        scene = bpy.context.scene
        if props.menu_selectedElemGrp < len(elemGrps) -1:
            swapItem = props.menu_selectedElemGrp +1
            # Swap items (syncing element group indices happens on execution)
            elemGrps[swapItem], elemGrps[props.menu_selectedElemGrp] = elemGrps[props.menu_selectedElemGrp], elemGrps[swapItem]
            # Also move menu selection
            props.menu_selectedElemGrp += 1
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
        if props.menu_selectedElemGrp > 0:
            props.menu_selectedElemGrp -= 1
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
        elemGrps = mem["elemGrps"]
        if props.menu_selectedElemGrp < len(elemGrps) -1:
            props.menu_selectedElemGrp += 1
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
        scene = bpy.context.scene
        # Overwrite element group with original backup (syncing element group indices happens on execution)
        mem["elemGrps"] = elemGrpsBak.copy()
        # Update menu selection
        props.menu_selectedElemGrp = 0
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
    
################################################################################

class OBJECT_OT_bcb_tool_estimate_cluster_radius(bpy.types.Operator):
    bl_idname = "bcb.tool_estimate_cluster_radius"
    bl_label = ""
    bl_description = "Estimate optimal cluster radius from selected objects in scene (even if you already have built a BCB structure only selected objects are considered)."
    def execute(self, context):
        scene = bpy.context.scene
        result = tool_estimateClusterRadius(scene)
        if result > 0:
            props = context.window_manager.bcb
            props.clusterRadius = result
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_do_all_steps_at_once(bpy.types.Operator):
    bl_idname = "bcb.tool_do_all_steps_at_once"
    bl_label = "Do All Steps At Once!"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_createGroupsFromNames(scene)
        tool_applyAllModifiers(scene)
        tool_separateLoose(scene)
        tool_discretize(scene)
        tool_enableRigidBodies(scene)
        tool_fixFoundation(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_create_groups_from_names(bpy.types.Operator):
    bl_idname = "bcb.tool_create_groups_from_names"
    bl_label = "Create Groups From Names"
    bl_description = "Creates object groups from object names and adds them to the element group list. (':' is used as name separator by default.)"
    def execute(self, context):
        scene = bpy.context.scene
        tool_createGroupsFromNames(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_apply_all_modifiers(bpy.types.Operator):
    bl_idname = "bcb.tool_apply_all_modifiers"
    bl_label = "Apply All Modifiers"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_applyAllModifiers(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_separate_loose(bpy.types.Operator):
    bl_idname = "bcb.tool_separate_loose"
    bl_label = "Separate Loose"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_separateLoose(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_discretize(bpy.types.Operator):
    bl_idname = "bcb.tool_discretize"
    bl_label = "Discretize"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_discretize(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_enable_rigid_bodies(bpy.types.Operator):
    bl_idname = "bcb.tool_enable_rigid_bodies"
    bl_label = "Enable Rigid Bodies"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_enableRigidBodies(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_fix_foundation(bpy.types.Operator):
    bl_idname = "bcb.tool_fix_foundation"
    bl_label = "Fix Foundation"
    bl_description = ""
    def execute(self, context):
        scene = bpy.context.scene
        tool_fixFoundation(scene)
        return{'FINISHED'}
