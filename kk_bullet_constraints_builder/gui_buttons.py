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
# Copyright (C) 2015-2018 Kai Kostack
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
    bl_description = "Stores actual config data in current scene"
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
    bl_description = "Loads previous config data from current scene"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        if "bcb_prop_elemGrps" in scene.keys():
            ###### Get menu config data from scene
            warning = getConfigDataFromScene(scene)
            if warning != None and len(warning): self.report({'ERROR'}, warning)  # Create popup message
            props.menu_gotConfig = 1
            ###### Get build data from scene
            #getBuildDataFromScene(scene)
            if "bcb_valid" in scene.keys(): props.menu_gotData = 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_clear(bpy.types.Operator):
    bl_idname = "bcb.clear"
    bl_label = ""
    bl_description = "Clears constraints from scene and revert back to original state (required to rebuild constraints from scratch)"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        ###### Clear all data from scene and delete also constraint empty objects
        if "bcb_prop_elemGrps" in scene.keys(): clearAllDataFromScene(scene, qKeepBuildData=0)
        props.menu_gotConfig = 0
        props.menu_gotData = 0
        return{'FINISHED'} 
        
########################################

class OBJECT_OT_bcb_build(bpy.types.Operator):
    bl_idname = "bcb.build"
    bl_label = "Build"
    bl_description = "Starts building process and adds constraints to selected elements"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        # Go to start frame for cache data removal
        if scene.frame_current != scene.frame_start:
            scene.frame_current = scene.frame_start
        ### Free previous bake data
        contextFix = bpy.context.copy()
        try: contextFix['point_cache'] = scene.rigidbody_world.point_cache
        except: pass
        try: bpy.ops.ptcache.free_bake(contextFix)
        except: pass
        ### Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            try: obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            except: pass
            else: obj.location = obj.location
        ###### Execute main building process from scratch
        # Display progress bar
        bpy.context.window_manager.progress_begin(0, 100)
        # Toggle console
        #bpy.ops.wm.console_toggle()
        ### Build
        error = build()
        if not error: props.menu_gotData = 1
        # Terminate progress bar
        bpy.context.window_manager.progress_end()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_update(bpy.types.Operator):
    bl_idname = "bcb.update"
    bl_label = "Update"
    bl_description = "Updates constraints generated from a previous built"
    def execute(self, context):
        OBJECT_OT_bcb_build.execute(self, context)
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
        elemGrps = mem["elemGrps"]
        if props.menu_selectedElemGrp >= len(elemGrps) and len(elemGrps) > 0:
            props.menu_selectedElemGrp = len(elemGrps)-1
        if not error:
            props.menu_gotConfig = 1
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_export_ascii(bpy.types.Operator):
    bl_idname = "bcb.export_ascii"
    bl_label = "Export to Text"
    bl_description = "Exports all constraint data to an ASCII text file within this .blend file instead of creating actual empty objects (only useful for developers at the moment)"
    def execute(self, context):
        props = context.window_manager.bcb
        props.asciiExport = 1
        if props.automaticMode and props.preprocTools_aut:
            OBJECT_OT_bcb_preprocess_do_all_steps_at_once.execute(self, context)
        OBJECT_OT_bcb_build.execute(self, context)
        if props.menu_gotData:
            if props.automaticMode and props.postprocTools_aut:
                OBJECT_OT_bcb_postprocess_do_all_steps_at_once.execute(self, context)
        props.asciiExport = 0
        return{'FINISHED'}
    
########################################

class OBJECT_OT_bcb_export_ascii_fm(bpy.types.Operator):
    bl_idname = "bcb.export_ascii_fm"
    bl_label = "Build FM"
    bl_description = "Builds and simulates with help of the Fracture Modifier (special Blender version required). 'Build FM' will simulate scientifically like 'Build'; Dynamic: Enables geometry also to shatter for more realistic but non-scientific appearance"
    int_ = bpy.props.IntProperty 
    use_handler = int_(default = 0)
    def execute(self, context):
        if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'):
            self.report({'ERROR'}, "Fracture Modifier not available in this Blender version. Visit graphicall.org/1148 for the FM-enabled Blender version.")  # Create popup message
        else:
            ###### Execute main building process from scratch
            scene = bpy.context.scene
            props = context.window_manager.bcb
            OBJECT_OT_bcb_export_ascii.execute(self, context)
            if props.menu_gotData:
                ###### Fracture Modifier export
                if not "bcb_ext_noBuild" in scene.keys():  # Option for external scripts to prevent building and keep export data
                    build_fm(use_handler=self.use_handler)
                    if not self.use_handler and asciiExportName +".txt" in bpy.data.texts:
                        try:    bpy.data.texts.remove(bpy.data.texts[asciiExportName +".txt"], do_unlink=1)
                        except: bpy.data.texts.remove(bpy.data.texts[asciiExportName +".txt"])
                ### Free previous bake data
                contextFix = bpy.context.copy()
                if scene.rigidbody_world != None:
                    contextFix['point_cache'] = scene.rigidbody_world.point_cache
                else:
                    print("Error: No 'Rigid Body World' found, please create one in the Scene buttons.")
                    return{'CANCELLED'} 
                bpy.ops.ptcache.free_bake(contextFix)
                if props.automaticMode:
                    # Prepare event handler
                    bpy.app.handlers.frame_change_pre.append(monitor_stop_eventHandler)
                    # Invoke baking (old method, appears not to work together with the event handler past Blender v2.76 anymore)
                    #bpy.ops.ptcache.bake(contextFix, bake=True)
                    if props.automaticMode and props.postprocTools_aut: pass
                    else:
                        # Start animation playback and by that the baking process
                        if not bpy.context.screen.is_animation_playing:
                            bpy.ops.screen.animation_play()
        self.use_handler = 0
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_bake(bpy.types.Operator):
    bl_idname = "bcb.bake"
    bl_label = "Simulate"
    bl_description = "Starts the rigid body simulation. A build is invoked beforehand if not already done. Use this button instead of the regular Blender physics baking as the BCB needs to monitor the simulation for constraint detaching"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        # Go to start frame for cache data removal
        if scene.frame_current != scene.frame_start:
            scene.frame_current = scene.frame_start
            bpy.context.screen.scene = scene  # Hack to update scene completely (scene.update() is not enough causing the monitor not work correctly when invoking at a frame > 1)
        ### Free previous bake data
        contextFix = bpy.context.copy()
        if scene.rigidbody_world != None:
            contextFix['point_cache'] = scene.rigidbody_world.point_cache
        else:
            print("Error: No 'Rigid Body World' found, please create one in the Scene buttons.")
            return{'CANCELLED'} 
        bpy.ops.ptcache.free_bake(contextFix)
        ### Invalidate point cache to enforce a full bake without using previous cache data
        if "RigidBodyWorld" in bpy.data.groups:
            try: obj = bpy.data.groups["RigidBodyWorld"].objects[0]
            except: pass
            else: obj.location = obj.location

        ### Build constraints if required (menu_gotData will be set afterwards and this operator restarted)
        ### If asciiExportName exists then the use of Fracture Modifier is assumed and building is skipped
        if not props.menu_gotData and not asciiExportName in scene.objects:
            if props.automaticMode and props.preprocTools_aut:
                OBJECT_OT_bcb_preprocess_do_all_steps_at_once.execute(self, context)
            OBJECT_OT_bcb_build.execute(self, context)
            if props.menu_gotData:
                if props.automaticMode and props.postprocTools_aut:
                    OBJECT_OT_bcb_postprocess_do_all_steps_at_once.execute(self, context)
                OBJECT_OT_bcb_bake.execute(self, context)
        ### Start baking when we have constraints set
        else:
            # Prepare event handlers
            bpy.app.handlers.frame_change_pre.append(monitor_eventHandler)
            bpy.app.handlers.frame_change_pre.append(monitor_stop_eventHandler)
            monitor_eventHandler(scene)  # Init at current frame before starting simulation
            # Invoke baking (old method, appears not to work together with the event handler past Blender v2.76 anymore)
            #bpy.ops.ptcache.bake(contextFix, bake=True)
            if props.automaticMode and props.postprocTools_aut: pass
            else:
                # Start animation playback and by that the baking process
                if not bpy.context.screen.is_animation_playing:
                    bpy.ops.screen.animation_play()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_add(bpy.types.Operator):
    bl_idname = "bcb.add"
    bl_label = ""
    bl_description = "Adds a preset element group to list"
    int_ =    bpy.props.IntProperty 
    menuIdx = int_(default = -1)
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        if len(elemGrps) < maxMenuElementGroupItems:
            if self.menuIdx < 0:
                # Call menu
                bpy.ops.wm.call_menu(name="bcb.add_preset")
            else:
                props = context.window_manager.bcb
                elemGrps = mem["elemGrps"]
                # Add element group (syncing element group indices happens on execution)
                elemGrps.append(presets[self.menuIdx].copy())
                # Update menu selection
                props.menu_selectedElemGrp = len(elemGrps) -1
                # Update menu related properties from global vars
                props.props_update_menu()
                self.menuIdx = -1
        else: self.report({'ERROR'}, "Maximum allowed element group count reached.")  # Create popup message
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_dup(bpy.types.Operator):
    bl_idname = "bcb.dup"
    bl_label = ""
    bl_description = "Duplicates selected element group"
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        if len(elemGrps) > 0:
            if len(elemGrps) < maxMenuElementGroupItems:
                # Add element group (syncing element group indices happens on execution)
                elemGrps.append(elemGrps[props.menu_selectedElemGrp].copy())
                # Update menu selection
                props.menu_selectedElemGrp = len(elemGrps) -1
            else: self.report({'ERROR'}, "Maximum allowed element group count reached.")  # Create popup message
        else: self.report({'ERROR'}, "There is no element group to duplicate.")  # Create popup message
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_del(bpy.types.Operator):
    bl_idname = "bcb.del"
    bl_label = ""
    bl_description = "Deletes element group from list"
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        scene = bpy.context.scene
        if len(elemGrps) > 0:
            # Remove element group (syncing element group indices happens on execution)
            del elemGrps[props.menu_selectedElemGrp]
            # Update menu selection
            if props.menu_selectedElemGrp >= len(elemGrps) and len(elemGrps) > 0:
                props.menu_selectedElemGrp = len(elemGrps) -1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_move_up(bpy.types.Operator):
    bl_idname = "bcb.move_up"
    bl_label = ""
    bl_description = "Moves element group in list"
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
    bl_description = "Moves element group in list"
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
    bl_description = "Selects previous element group from list"
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
    bl_description = "Selects next element group from list"
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        if props.menu_selectedElemGrp < len(elemGrps) -1:
            props.menu_selectedElemGrp += 1
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_up_more(bpy.types.Operator):
    bl_idname = "bcb.up_more"
    bl_label = ""
    bl_description = "Selects previous element group from list. (x10)"
    def execute(self, context):
        props = context.window_manager.bcb
        stepSize = 10
        if props.menu_selectedElemGrp > 0 +stepSize:
              props.menu_selectedElemGrp -= stepSize
        else: props.menu_selectedElemGrp = 0
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_down_more(bpy.types.Operator):
    bl_idname = "bcb.down_more"
    bl_label = ""
    bl_description = "Selects next element group from list. (x10)"
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        stepSize = 10
        if props.menu_selectedElemGrp < len(elemGrps) -1 -stepSize:
              props.menu_selectedElemGrp += stepSize
        else: props.menu_selectedElemGrp = len(elemGrps) -1
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'} 

########################################

class OBJECT_OT_bcb_reset(bpy.types.Operator):
    bl_idname = "bcb.reset"
    bl_label = ""
    bl_description = "Resets element group list to defaults"
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
    bl_description = "Combines and evaluates above expressions for constraint breaking threshold calculation. It is recommended to choose a Connection Type with 7x Generic constraints to get the best simulation results"
    def execute(self, context):
        props = context.window_manager.bcb
        ###### Execute expression evaluation
        combineExpressions()
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'}
    
########################################

class OBJECT_OT_bcb_asst_update_all(bpy.types.Operator):
    bl_idname = "bcb.asst_update_all"
    bl_label = "Evaluate All"
    bl_description = "Combines and evaluates expressions for every element groups with active Formula Assistant. Warning: Use this with care as it will overwrite also manually changed breaking thresholds for these element groups"
    def execute(self, context):
        props = context.window_manager.bcb
        elemGrps = mem["elemGrps"]
        selElemGrp_bak = props.menu_selectedElemGrp
        # Walk over all element groups and evaluate formula expressions
        for i in range(len(elemGrps)):
            props.menu_selectedElemGrp = i
            # Update menu related properties from global vars
            props.props_update_menu()
            # Only evaluate if Formula Assistant is active
            if props.assistant_menu != "None":
                ###### Execute expression evaluation
                combineExpressions()
        props.menu_selectedElemGrp = selElemGrp_bak
        # Update menu related properties from global vars
        props.props_update_menu()
        return{'FINISHED'}
    
################################################################################

class OBJECT_OT_bcb_tool_estimate_cluster_radius(bpy.types.Operator):
    bl_idname = "bcb.tool_estimate_cluster_radius"
    bl_label = ""
    bl_description = "Estimate optimal cluster radius from selected objects in scene (even if you already have built a BCB structure only selected objects are considered)"
    def execute(self, context):
        scene = bpy.context.scene
        result = tool_estimateClusterRadius(scene)
        if result > 0:
            props = context.window_manager.bcb
            props.clusterRadius = result
            # Update menu related properties from global vars
            props.props_update_menu()
        return{'FINISHED'}
    
################################################################################

class OBJECT_OT_bcb_tool_select_group(bpy.types.Operator):
    bl_idname = "bcb.tool_select_group"
    bl_label = ""
    bl_description = "Selects objects belonging to this element group in viewport"
    def execute(self, context):
        scene = bpy.context.scene
        tool_selectGroup(scene)
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preprocess_do_all_steps_at_once(bpy.types.Operator):
    bl_idname = "bcb.preprocess_do_all_steps_at_once"
    bl_label = "Do All Selected Steps At Once!"
    bl_description = "Executes all selected tools in the order from top to bottom"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        time_start = time.time()
        if props.preprocTools_rps: tool_runPythonScript(scene, props.preprocTools_rps_nam); props.preprocTools_rps = 0
        if props.preprocTools_grp: tool_createGroupsFromNames(scene); props.preprocTools_grp = 0
        if props.preprocTools_mod: tool_applyAllModifiers(scene); props.preprocTools_mod = 0
        if props.preprocTools_ctr: tool_centerModel(scene); props.preprocTools_ctr = 0
        if props.preprocTools_sep: tool_separateLoose(scene); props.preprocTools_sep = 0
        if props.preprocTools_dis: tool_discretize(scene); props.preprocTools_dis = 0
        if props.preprocTools_rbs: tool_enableRigidBodies(scene); props.preprocTools_rbs = 0
        if props.preprocTools_int: tool_removeIntersections(scene); props.preprocTools_int = 0
        if props.preprocTools_fix: tool_fixFoundation(scene); props.preprocTools_fix = 0
        if props.preprocTools_gnd: tool_groundMotion(scene); props.preprocTools_gnd = 0
        props.preprocTools_aut = 0
        if not props.automaticMode and not props.preprocTools_int_bol:
            ### Check for intersections and warn if some are left
            count = tool_removeIntersections(scene, mode=4)
            if count > 0:
                # Throw warning
                bpy.context.window_manager.bcb.message = "Warning: Some element intersections could not automatically be resolved, please review selected objects"
                bpy.ops.bcb.report('INVOKE_DEFAULT')  # Create popup message box
        print('-- Time total: %0.2f s' %(time.time()-time_start))
        print()

        ###### Store menu config data in scene
        storeConfigDataInScene(scene)
        props.menu_gotConfig = 1
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_run_python_script(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_run_python_script"
    bl_label = "Run Python Script"
    bl_description = "Executes a user-defined Python script for customizable automatization purposes (e.g. for scene management and modification)"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_runPythonScript(scene, props.preprocTools_rps_nam)
        props.preprocTools_rps = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_select_py_file(bpy.types.Operator):
    bl_idname = "bcb.tool_select_py_file"
    bl_label = "Select"
    bl_description = "Search for Python file (.py)"
    string_ = bpy.props.StringProperty
    filepath = string_(subtype='FILE_PATH')
    filter_glob = string_(default="*.py", options={'HIDDEN'})
    int_ = bpy.props.IntProperty 
    opNo = int_(default = 1)

    def execute(self, context):
        props = context.window_manager.bcb
        if   self.opNo == 1: props.preprocTools_rps_nam = self.filepath
        elif self.opNo == 2: props.postprocTools_rps_nam = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
########################################

class OBJECT_OT_bcb_preproc_tool_create_groups_from_names(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_create_groups_from_names"
    bl_label = "Create Groups From Names"
    bl_description = "Creates groups for all selected objects based on a specified naming convention and adds them also to the element groups list"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_createGroupsFromNames(scene)
        props.preprocTools_grp = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_apply_all_modifiers(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_apply_all_modifiers"
    bl_label = "Apply All Modifiers"
    bl_description = "Applies all modifiers on all selected objects"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_applyAllModifiers(scene)
        props.preprocTools_mod = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_center_model(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_center_model"
    bl_label = "Center Model"
    bl_description = "Shifts all selected objects as a whole to the world center of the scene"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_centerModel(scene)
        props.preprocTools_ctr = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_separate_loose(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_separate_loose"
    bl_label = "Separate Loose"
    bl_description = "Separates all loose (not connected) mesh elements within an object into separate objects, this is done for all selected objects"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_separateLoose(scene)
        props.preprocTools_sep = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_discretize(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_discretize"
    bl_label = "Discretize"
    bl_description = "Discretizes (subdivides) all selected objects into smaller segments by splitting them into halves as long as a specified minimum size is reached"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_discretize(scene)
        props.preprocTools_dis = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_enable_rigid_bodies(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_enable_rigid_bodies"
    bl_label = "Enable Rigid Bodies"
    bl_description = "Enables rigid body settings for all selected objects"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_enableRigidBodies(scene)
        props.preprocTools_rbs = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_remove_intersections(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_remove_intersections"
    bl_label = "Intersection Removal"
    bl_description = "Detects and removes intersecting objects (one per found pair). Intesecting objects can be caused by several reasons: accidental object duplication, forgotten boolean cutout objects, careless modeling etc"
    int_ =    bpy.props.IntProperty 
    mode = int_(default = 0)
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_removeIntersections(scene, mode=self.mode)
        props.preprocTools_int = 0
        return{'FINISHED'}
    
########################################

class OBJECT_OT_bcb_preproc_tool_fix_foundation(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_fix_foundation"
    bl_label = "Fix Foundation"
    bl_description = "Either uses name based search to find foundation objects or creates foundation objects for all objects touching the overall model boundary box. These foundation objects will be set to be 'Passive' rigid bodies"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_fixFoundation(scene)
        props.preprocTools_fix = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_preproc_tool_ground_motion(bpy.types.Operator):
    bl_idname = "bcb.preproc_tool_ground_motion"
    bl_label = "Ground Motion"
    bl_description = "Attaches all selected passive rigid body objects to a specified and animated ground object. This can be useful for simulating earthquakes through a pre-animated ground motion object like a virtual shake table"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_groundMotion(scene)
        props.preprocTools_gnd = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_tool_select_csv_file(bpy.types.Operator):
    bl_idname = "bcb.tool_select_csv_file"
    bl_label = "Select"
    bl_description = "Select location for .csv time history file"
    string_ = bpy.props.StringProperty
    filepath = string_(subtype='FILE_PATH')
    filter_glob = string_(default="*.csv", options={'HIDDEN'})
    int_ = bpy.props.IntProperty 
    opNo = int_(default = 1)

    def execute(self, context):
        props = context.window_manager.bcb
        if   self.opNo == 1: props.preprocTools_gnd_nam = self.filepath
        elif self.opNo == 2: props.postprocTools_lox_nam = os.path.dirname(self.filepath)
        elif self.opNo == 3: props.postprocTools_fcx_nam = os.path.dirname(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

################################################################################

class OBJECT_OT_bcb_postprocess_do_all_steps_at_once(bpy.types.Operator):
    bl_idname = "bcb.postprocess_do_all_steps_at_once"
    bl_label = "Do All Selected Steps At Once!"
    bl_description = "Executes all selected tools in the order from top to bottom"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        time_start = time.time()
        if props.postprocTools_lox: tool_exportLocationHistory(scene); props.postprocTools_lox = 0
        if props.postprocTools_fcx: tool_exportForceHistory(scene); props.postprocTools_fcx = 0
        if props.postprocTools_fcv: tool_forcesVisualization(scene); props.postprocTools_fcv = 0
        if props.postprocTools_cav: tool_cavityDetection(scene); props.postprocTools_cav = 0
        if props.postprocTools_rps: tool_runPythonScript(scene, props.postprocTools_rps_nam); props.postprocTools_rps = 0
        props.postprocTools_aut = 0
        print('-- Time total: %0.2f s' %(time.time()-time_start))
        print()

        ###### Store menu config data in scene
        storeConfigDataInScene(scene)
        props.menu_gotConfig = 1
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_postproc_tool_export_location_history(bpy.types.Operator):
    bl_idname = "bcb.postproc_tool_export_location_history"
    bl_label = "Export Location History"
    bl_description = "Exports the location time history of an element centroid into a .csv file"
    def execute(self, context):
        OBJECT_OT_bcb_bake.execute(self, context)
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_exportLocationHistory(scene)
        props.postprocTools_lox = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_postproc_tool_export_force_history(bpy.types.Operator):
    bl_idname = "bcb.postproc_tool_export_force_history"
    bl_label = "Export Force History"
    bl_description = "Exports the force time history for a constraint into a .csv file"
    def execute(self, context):
        if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'):
            self.report({'ERROR'}, "This tool requires the Fracture Modifier which is not available in this Blender version. Visit graphicall.org/1148 for the FM-enabled Blender version.")  # Create popup message
        else:
            OBJECT_OT_bcb_bake.execute(self, context)
            props = context.window_manager.bcb
            scene = bpy.context.scene
            tool_exportForceHistory(scene)
            props.postprocTools_fcx = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_postproc_tool_visualize_forces(bpy.types.Operator):
    bl_idname = "bcb.postproc_tool_visualize_forces"
    bl_label = "Visualize Forces"
    bl_description = "Visualizes forces for constraints as spheres to be created in the scene whereby each sphere's radius is normalized to the predefined maximum force. Accurate values can be found in each sphere's properties"
    def execute(self, context):
        if not hasattr(bpy.types.DATA_PT_modifiers, 'FRACTURE'):
            self.report({'ERROR'}, "This tool requires the Fracture Modifier which is not available in this Blender version. Visit graphicall.org/1148 for the FM-enabled Blender version.")  # Create popup message
        else:
            OBJECT_OT_bcb_bake.execute(self, context)
            props = context.window_manager.bcb
            scene = bpy.context.scene
            tool_forcesVisualization(scene)
            props.postprocTools_fcv = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_postproc_tool_detect_cavities(bpy.types.Operator):
    bl_idname = "bcb.postproc_tool_detect_cavities"
    bl_label = "Detect Cavities"
    bl_description = "Visualizes cavities on the selected mesh in form of a cell grid where each cell represents an air pocket large enough to contain the cell"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_cavityDetection(scene)
        props.postprocTools_cav = 0
        return{'FINISHED'}

########################################

class OBJECT_OT_bcb_postproc_tool_run_python_script(bpy.types.Operator):
    bl_idname = "bcb.postproc_tool_run_python_script"
    bl_label = "Run Python Script"
    bl_description = "Executes a user-defined Python script for customizable automatization purposes (e.g. for scene management and modification)"
    def execute(self, context):
        props = context.window_manager.bcb
        scene = bpy.context.scene
        tool_runPythonScript(scene, props.postprocTools_rps_nam)
        props.postprocTools_rps = 0
        return{'FINISHED'}
