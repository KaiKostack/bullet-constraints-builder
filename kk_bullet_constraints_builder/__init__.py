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

import bpy, sys, os, platform, mathutils, time, copy, math, pickle, base64, zlib, random, imp
from mathutils import Vector
mem = bpy.app.driver_namespace
#import os
#os.system("cls")

########################################

###### SymPy detection and import code
from pkgutil import iter_modules
def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

### Try to import SymPy
if module_exists("sympy"): import sympy
else:
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
if module_exists("sympy"): import sympy
else:
    ### If not found attempt using pip to automatically install SymPy module in Blender
    import subprocess, bpy
    def do(cmd, *arg):
        list = [bpy.app.binary_path_python, '-m', cmd]
        list.extend(arg)
        command = (list)       
        try: p = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1)
        except: print("Failed executing command:", command)
        else:
            for line in iter(p.stdout.readline, b''):
                print(line.decode())
            p.stdout.close()
            p.wait()
    #do('pip', '--version')
    do('ensurepip')
    do('pip', 'install', '--upgrade', 'pip')
    do('pip', 'install', 'sympy')

### Ultimate attempt to import SymPy
if module_exists("sympy"):
    import sympy
    print("SymPy module found.")
    qSymPy = 1
else:
    print("No SymPy module found, continuing without formula simplification feature...")
    qSymPy = 0

########################################

# Take either the path of the current blend file into consideration for module import (for more convenient development)
try:    basedir = os.path.join(os.path.dirname(bpy.data.filepath), "kk_bullet_constraints_builder")
# Or if that fails it's probably being installed as add-on and we have to use a different path instead
except: basedir = os.path.dirname(__file__)
if basedir not in sys.path: sys.path.append(basedir)
# Add also subfolder(s)
subdir = os.path.join(basedir, "extern")
if subdir not in sys.path: sys.path.append(subdir)
#print("BASEDIR:", basedir)

### Force all modules to reload (doesn't work as expected as UI elements aren't updated, you have to restart Blender)
#if "bcb_init_modules" in mem.keys():
#    # Second or subsequent run: remove all but initially loaded modules
#    del_modules = []
#    for m in sys.modules.keys():
#        if m not in mem["bcb_init_modules"]:
#            del_modules.append(m)
#    for m in del_modules:
#        del sys.modules[m]
#        #imp.reload(sys.modules[m])
#else:
#    # First run: find out which modules were initially loaded
#    init_modules = []
#    for m in sys.modules.keys():
#        init_modules.append(m)
#    mem["bcb_init_modules"] = init_modules     
    
### Import submodules
from build_data import *       # Contains build data access functions
from builder import *          # Contains constraints builder function
from builder_fm import *       # Contains constraints builder function for Fracture Modifier (custom Blender version required)
from builder_prep import *     # Contains preparation steps functions called by the builder
from builder_setc import *     # Contains constraints settings functions called by the builder
from file_io import *          # Contains file input & output functions
from formula import *          # Contains formula assistant functions
from formula_props import *    # Contains formula assistant properties classes
from global_props import *     # Contains global properties
from global_vars import *      # Contains global variables
from gui import *              # Contains graphical user interface layout class
from gui_buttons import *      # Contains graphical user interface button classes
from monitor import *          # Contains baking monitor event handler
from tools import *            # Contains smaller independently working tools

########################################

bl_info = {
    "name": "Bullet Constraints Builder",
    "author": "Kai Kostack",
    "blender": (2, 7, 8),
    "location": "View3D > Toolshelf > Create Tab",
    "description": "Tool to connect rigid bodies via constraints in a physical plausible way.",
    "wiki_url": "http://www.inachus.eu",
    "tracker_url": "http://kaikostack.com",
    "category": "Animation"}

################################################################################

classes = [ \
    bcb_props,
    bcb_asst_con_rei_beam_props,
    bcb_asst_con_rei_wall_props,
    
    bcb_report,
    bcb_add_preset,
    
    bcb_panel_preprocessing_tools,
    bcb_panel_execute,
    bcb_panel_global_settings,
    bcb_panel_advanced_global_settings,
    bcb_panel_triggers,
    bcb_panel_element_group_list,
    bcb_panel_element_group_selector,
    bcb_panel_formula_assistant,
    bcb_panel_element_group_settings,
    bcb_panel_advanced_element_group_settings,
    bcb_panel_postprocessing_tools,
    
    OBJECT_OT_bcb_set_config,
    OBJECT_OT_bcb_get_config,
    OBJECT_OT_bcb_clear,
    OBJECT_OT_bcb_build,
    OBJECT_OT_bcb_update,
    OBJECT_OT_bcb_export_config,
    OBJECT_OT_bcb_import_config,
    OBJECT_OT_bcb_export_ascii,
    OBJECT_OT_bcb_export_ascii_fm,
    OBJECT_OT_bcb_bake,
    
    OBJECT_OT_bcb_add,
    OBJECT_OT_bcb_dup,
    OBJECT_OT_bcb_del,
    OBJECT_OT_bcb_move_up,
    OBJECT_OT_bcb_move_down,
    OBJECT_OT_bcb_up,
    OBJECT_OT_bcb_down,
    OBJECT_OT_bcb_up_more,
    OBJECT_OT_bcb_down_more,
    OBJECT_OT_bcb_reset,
    
    OBJECT_OT_bcb_asst_update,
    OBJECT_OT_bcb_asst_update_all,
    OBJECT_OT_bcb_tool_estimate_cluster_radius,
    OBJECT_OT_bcb_tool_select_group,

    OBJECT_OT_bcb_tool_do_all_steps_at_once,
    OBJECT_OT_bcb_tool_run_python_script,
    OBJECT_OT_bcb_tool_run_python_script_file,
    OBJECT_OT_bcb_tool_create_groups_from_names,
    OBJECT_OT_bcb_tool_apply_all_modifiers,
    OBJECT_OT_bcb_tool_center_model,
    OBJECT_OT_bcb_tool_separate_loose,
    OBJECT_OT_bcb_tool_discretize,
    OBJECT_OT_bcb_tool_enable_rigid_bodies,
    OBJECT_OT_bcb_tool_remove_intersections,
    OBJECT_OT_bcb_tool_fix_foundation,
    OBJECT_OT_bcb_tool_ground_motion,
    OBJECT_OT_bcb_tool_select_csv_file,
    OBJECT_OT_bcb_tool_export_location_history,
    OBJECT_OT_bcb_tool_export_force_history,
    OBJECT_OT_bcb_tool_visualize_forces
    ]

################################################################################

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.WindowManager.bcb = bpy.props.PointerProperty(type=bcb_props)
    bpy.types.WindowManager.bcb_asst_con_rei_beam = bpy.props.PointerProperty(type=bcb_asst_con_rei_beam_props)
    bpy.types.WindowManager.bcb_asst_con_rei_wall = bpy.props.PointerProperty(type=bcb_asst_con_rei_wall_props)
    
           
def unregister():
    for c in classes:
        try: bpy.utils.unregister_class(c) 
        except: pass
    del bpy.types.WindowManager.bcb
    del bpy.types.WindowManager.bcb_asst_con_rei_beam
    del bpy.types.WindowManager.bcb_asst_con_rei_wall

 
if __name__ == "__main__":
    try: unregister()
    except: pass
    register()
