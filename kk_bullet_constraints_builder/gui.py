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

import bpy, sys
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

def dpifac100():
    prefs = bpy.context.user_preferences.system
    if hasattr(prefs, 'pixel_size'):  # python access to this was only added recently, assume non-retina display is used if using older blender
        retinafac = bpy.context.user_preferences.system.pixel_size
    else:
        retinafac = 1
    return bpy.context.user_preferences.system.dpi/(100/retinafac)
   
class bcb_report(bpy.types.Operator):
    bl_idname = "bcb.report"
    bl_label = "Info"
    bl_description = "Report message operator"
    def execute(self, context):
        return {'FINISHED'}
    def invoke(self, context, event):
        wm = context.window_manager
        props = context.window_manager.bcb
        print(props.message)
        # Calculate safe width in pixel from char count of the string
        strSize = len(props.message)
        # widthPx = (strSize*12+40) /dpifac100()  # Approx. width for capitals
        widthPx = (strSize*8+30) /dpifac100()   # Approx. width for normal text
        #return wm.invoke_props_dialog(self)
        return wm.invoke_popup(self, width=widthPx, height=300)
    def draw(self, context):
        layout = self.layout
        props = context.window_manager.bcb
        message = props.message
        row = layout.row()
        row.label(text=message, icon="ERROR")

########################################

class bcb_add_preset(bpy.types.Menu):
    bl_idname = "bcb.add_preset"
    bl_label = "Available Presets"
    bl_description = "Duplicates selected element group."
    def draw(self, context):
        layout = self.layout
        #layout.operator("wm.open_mainfile")
        for i in range(len(presets)):
            pres_EGSidxName = eval("presets[%d][EGSidxName]" %i)
            pres_EGSidxMatP = eval("presets[%d][EGSidxMatP]" %i)
            pres_EGSidxDens = eval("presets[%d][EGSidxDens]" %i)
            pres_EGSidxCTyp = eval("presets[%d][EGSidxCTyp]" %i)
            pres_EGSidxBTC = eval("presets[%d][EGSidxBTC]" %i)
            pres_EGSidxBTS = eval("presets[%d][EGSidxBTS]" %i)
            if pres_EGSidxName == "": pres_EGSidxName = "[Default]"
            if pres_EGSidxCTyp != 0:
                preset = "%s  |  Density: %s kg/m³    CPR: %s N/mm²    SHR: %s N/mm²    CT: %d" \
                %(pres_EGSidxName, pres_EGSidxDens, pres_EGSidxBTC, pres_EGSidxBTS, pres_EGSidxCTyp)
            else:
                preset = "%s  |  Passive & Indestructible    CT: %d" \
                %(pres_EGSidxName, pres_EGSidxCTyp)
            qNewCategory = 0
            if i > 0:
                pres_EGSidxMatP_last = eval("presets[%d][EGSidxMatP]" %(i-1))
                if pres_EGSidxMatP != pres_EGSidxMatP_last: qNewCategory = 1
            else: qNewCategory = 1
            if qNewCategory:
                if i > 0: layout.separator()
                layout.label(text= pres_EGSidxMatP.upper())
            layout.operator("bcb.add", text=preset).menuIdx = i
            
########################################

class bcb_panel(bpy.types.Panel):
    ver = bcb_version
    bl_label = "Bullet Constraints Builder v%d.%d%d" %(ver[0], ver[1], ver[2]) 
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS" 

    def icon_pulldown(self, bool):
        if bool: return 'TRIA_DOWN'
        else: return 'TRIA_RIGHT'

    def draw(self, context):
        layout = self.layout
        props = context.window_manager.bcb
        props_asst_con_rei_beam = context.window_manager.bcb_asst_con_rei_beam
        props_asst_con_rei_wall = context.window_manager.bcb_asst_con_rei_wall
        obj = context.object
        scene = bpy.context.scene
        try: elemGrps = mem["elemGrps"]
        except: elemGrps = mem["elemGrps"] = elemGrpsBak.copy()

        ###### Preprocessing tools box
        
        box = layout.box()
        box.prop(props, "submenu_preprocTools", text="Preprocessing Tools", icon=self.icon_pulldown(props.submenu_preprocTools), emboss = False)
        if props.submenu_preprocTools:
            col = box.column(align=1)

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.label(text="", icon="LINKED")
            split.operator("bcb.tool_do_all_steps_at_once", icon="DOTSUP")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.label(text="")
            split.prop(props, "preprocTools_aut")
            col.separator()
            
            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_rps", text="")
            box2 = split.box()
            box2.operator("bcb.tool_run_python_script", icon="DOT")
            row2 = box2.row(align=1)
            row2.prop(props, "preprocTools_rps_nam")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_grp", text="")
            box2 = split.box()
            box2.operator("bcb.tool_create_groups_from_names", icon="DOT")
            row2 = box2.row(align=1)
            row2.prop(props, "preprocTools_grp_sep")
            row2.prop(props, "preprocTools_grp_occ")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_mod", text="")
            box2 = split.box()
            box2.operator("bcb.tool_apply_all_modifiers", icon="DOT")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_ctr", text="")
            box2 = split.box()
            box2.operator("bcb.tool_center_model", icon="DOT")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_sep", text="")
            box2 = split.box()
            box2.operator("bcb.tool_separate_loose", icon="DOT")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_dis", text="")
            box2 = split.box()
            box2.operator("bcb.tool_discretize", icon="DOT")
            col2 = box2.column(align=1)
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_dis_siz")
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_dis_cel")
            row3 = col2.row(align=1); row3.prop(props, "preprocTools_dis_jus")
            #if not props.preprocTools_dis_cel: row3.enabled = 0; 
            
            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_rbs", text="")
            box2 = split.box()
            box2.operator("bcb.tool_enable_rigid_bodies", icon="DOT")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_int", text="")
            box2 = split.box()
            box2.operator("bcb.tool_remove_intersections", icon="DOT").menuIdx = 0
            col2 = box2.column(align=1)
            row2 = col2.row(align=1)
            row2.label(text="Select Instead Of Deletion (Diagnostic):")
            row2 = col2.row(align=1)
            row2.operator("bcb.tool_remove_intersections", text="Select All Pairs").menuIdx = 1
            row2.operator("bcb.tool_remove_intersections", text="Select Removal").menuIdx = 2
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_int_bol")

            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_fix", text="")
            box2 = split.box()
            box2.operator("bcb.tool_fix_foundation", icon="DOT")
            col2 = box2.column(align=1)
            row = col2.row(align=1); row.prop(props, "preprocTools_fix_nam")
            row = col2.row(align=1); row.prop(props, "preprocTools_fix_cac")
            row2 = col2.row(align=1)
            if props.preprocTools_fix_rng > props.preprocTools_dis_siz /2:
                row2.alert = 1; qAlert = 1
            else: qAlert = 0
            row2.prop(props, "preprocTools_fix_rng")
            if qAlert:
                row5 = col2.row(align=1); row5.label(text="Warning: Range to large compared")
                row5 = col2.row(align=1); row5.label(text="to Discr. Size => mesh overlaps")
            row3 = col2.row(align=1)
            row3.prop(props, "preprocTools_fix_axp")
            row3.prop(props, "preprocTools_fix_ayp")
            row3.prop(props, "preprocTools_fix_azp")
            row4 = col2.row(align=1)
            row4.prop(props, "preprocTools_fix_axn")
            row4.prop(props, "preprocTools_fix_ayn")
            row4.prop(props, "preprocTools_fix_azn")
            if not props.preprocTools_fix_cac:
                row2.enabled = 0; row3.enabled = 0; row4.enabled = 0
            
            row = col.row(align=1); split = row.split(percentage=.08, align=0)
            split.prop(props, "preprocTools_gnd", text="")
            box2 = split.box()
            box2.operator("bcb.tool_ground_motion", icon="DOT")
            col2 = box2.column(align=1)
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_gnd_obj")
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_gnd_obm")
            row2 = col2.row(align=1); row2.prop(props, "preprocTools_gnd_nac")
            row = col2.row(align=1)
            row.prop(props, "preprocTools_gnd_nap")
            row.prop(props, "preprocTools_gnd_nfq")
            row2 = col2.row(align=1)
            row2.prop(props, "preprocTools_gnd_ndu")
            row2.prop(props, "preprocTools_gnd_nsd")
            if not props.preprocTools_gnd_nac:
                row.enabled = 0; row2.enabled = 0
        
            layout.separator()
            
        col = layout.column(align=1)
        row = col.row(align=1)
        if not props.menu_gotData: 
            split = row.split(percentage=.85, align=1)
            split.operator("bcb.build", icon="MOD_SKIN")
            split2 = split.split(align=1)
            if not props.menu_gotConfig:
                if not "bcb_prop_elemGrps" in scene.keys(): split2.enabled = 0
                split2.operator("bcb.get_config", icon="FILE_REFRESH")
            else: split2.operator("bcb.clear", icon="CANCEL")

            row = col.row(align=1)
            split = row.split(percentage=.85, align=1)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=1)
            split2.operator("bcb.set_config", icon="NEW")
        else:
            split = row.split(percentage=.85, align=1)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split2 = split.split(align=1)
            split2.operator("bcb.clear", icon="CANCEL")

            row = col.row(align=1)
            split = row.split(percentage=.85, align=1)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=1)
            split2.operator("bcb.set_config", icon="NEW")

        col = layout.column(align=1)

        row = col.row(align=1)
        if props.menu_gotData: row.enabled = 0
        row.prop(props, "searchDistance")

        row = col.row(align=1)
        split = row.split(percentage=.85, align=1)
        if props.menu_gotData: split.enabled = 0
        split.prop(props, "clusterRadius")
        split.operator("bcb.tool_estimate_cluster_radius", icon="AUTO")
        
        ###### Advanced main settings box
        
        box = layout.box()
        box.prop(props, "submenu_advancedG", text="Advanced Global Settings", icon=self.icon_pulldown(props.submenu_advancedG), emboss = False)
        if props.submenu_advancedG:
            col = box.column(align=1)

            row = col.row(align=1)
            split = row.split(percentage=.85, align=1)
            split2 = split.split(percentage=.5, align=1)
            split2.operator("bcb.export_ascii", icon="EXPORT")
            split2.operator("bcb.export_ascii_fm", icon="EXPORT")
            split.operator("bcb.import_config", icon="FILE_REFRESH")

            row = col.row(align=1)
            split = row.split(percentage=.85, align=1)
            split.prop(props, "stepsPerSecond")
            split.operator("bcb.export_config", icon="NEW")

            row = col.row(align=1)
            split = row.split(percentage=.50, align=1)
            split.prop(props, "constraintUseBreaking")
            split.prop(props, "disableCollision")
       
            row = col.row(align=1)
            split = row.split(percentage=.50, align=1)
            split.prop(props, "automaticMode")
            split.prop(props, "saveBackups")
            col.separator()

            row = col.row(align=1)
            split = row.split(percentage=.50, align=1)
            split.prop(props, "snapToAreaOrient")
            split.prop(props, "lowerBrkThresPriority")
            row = col.row(align=1)
            if props.snapToAreaOrient: row.enabled = 0
            row.prop(props, "alignVertical")
            col.separator()

            row = col.row(align=1)
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "useAccurateArea")
#            row = col.row(align=1)
#            if not props.useAccurateArea: row.enabled = 0
#            row.prop(props, "nonManifoldThickness")
            row = col.row(align=1)
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "connectionCountLimit")
            row = col.row(align=1)
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "minimumElementSize")

            row = col.row(align=1); row.prop(props, "warmUpPeriod")
            col.separator()
            row = col.row(align=1); row.prop(props, "timeScalePeriod")
            row = col.row(align=1); row.prop(props, "timeScalePeriodValue")
            if props.timeScalePeriod == 0: row.enabled = 0
            col.separator()

            row = col.row(align=1); row.prop(props, "progrWeak")
            row = col.row(align=1); row.prop(props, "progrWeakLimit")
            if props.progrWeak == 0: row.enabled = 0
            row = col.row(align=1); row.prop(props, "progrWeakStartFact")
            col.separator()
            
            row = col.row(align=1); row.prop(props, "detonatorObj")

            layout.separator()

        ###### Element groups box
        col = layout.column(align=1)
        row = col.row(align=1); row.label(text="Element Groups", icon="MOD_BUILD")
        box = col.box()
        col2 = box.column(align=0)
        row = col2.split(align=1)
        row.operator("bcb.add", icon="ZOOMIN")
        row.operator("bcb.dup", icon="PASTEDOWN")
        row.operator("bcb.del", icon="X")
        row.operator("bcb.reset", icon="CANCEL")
        row.operator("bcb.move_up", icon="TRIA_UP")
        row.operator("bcb.move_down", icon="TRIA_DOWN")
        row = col2.row(align=1)
        split = col2.split(percentage=.40, align=1)
        split.label(text="GRP")
        split2 = split.split(align=1)
        split2.label(text="CT")
        split2.label(text="CPR")
        split2.label(text="TNS")
        split2.label(text="SHR")
        split2.label(text="BND")
        if len(elemGrps) == 0 or props.menu_init:  # Hide list also on first draw just to make sure element groups are up-to-date
            row = col2.row(align=1); row.alignment = 'CENTER'
            row.label(text="Press + button to add a group!", icon="INFO")
            col2.separator()
            # These buttons are existing twice (see below)
            row = col2.row(align=1)
            split = row.split(percentage=.50, align=1)
            split2 = split.split(percentage=.30, align=1)
            split2.operator("bcb.up_more", icon="PREV_KEYFRAME")
            split2.operator("bcb.up", icon="TRIA_UP")
            split2 = split.split(percentage=.70, align=1)
            split2.operator("bcb.down", icon="TRIA_DOWN")
            split2.operator("bcb.down_more", icon="NEXT_KEYFRAME")

        ### Everything below is only visible if at least one element group is existing
        else:  
            for i in range(len(elemGrps)):
                if i == props.menu_selectedElemGrp:
                      row = col2.box().row(align=1)
                else: row = col2.row(align=1)
                prop_EGSidxName = eval("props.elemGrp_%d_EGSidxName" %i)
                prop_EGSidxCTyp = ct = eval("props.elemGrp_%d_EGSidxCTyp" %i)
                try: connectType = connectTypes[ct]
                except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
                if not connectType[2][0]: prop_EGSidxBTC = "-"
                else: prop_EGSidxBTC = eval("props.elemGrp_%d_EGSidxBTC" %i)
                if not connectType[2][1]: prop_EGSidxBTT = "-"
                else: prop_EGSidxBTT = eval("props.elemGrp_%d_EGSidxBTT" %i)
                if not connectType[2][2]: prop_EGSidxBTS = "-"
                else: prop_EGSidxBTS = eval("props.elemGrp_%d_EGSidxBTS" %i)
                if not connectType[2][3]: prop_EGSidxBTB = "-"
                else: prop_EGSidxBTB = eval("props.elemGrp_%d_EGSidxBTB" %i)
                split = row.split(percentage=.40, align=1)
                if prop_EGSidxName == "": split.label(text="[Def.]")
                else:                     split.label(text=str(prop_EGSidxName))
                split2 = split.split(align=1)
                split2.label(text=str(prop_EGSidxCTyp))
                split2.label(text=str(prop_EGSidxBTC))
                split2.label(text=str(prop_EGSidxBTT))
                split2.label(text=str(prop_EGSidxBTS))
                split2.label(text=str(prop_EGSidxBTB))

            # These buttons are existing twice (see above)
            row = col2.row(align=1)
            split = row.split(percentage=.50, align=1)
            split2 = split.split(percentage=.30, align=1)
            split2.operator("bcb.up_more", icon="PREV_KEYFRAME")
            split2.operator("bcb.up", icon="TRIA_UP")
            split2 = split.split(percentage=.70, align=1)
            split2.operator("bcb.down", icon="TRIA_DOWN")
            split2.operator("bcb.down_more", icon="NEXT_KEYFRAME")
            
            ###### Element group settings
            
            layout.separator()
            i = props.menu_selectedElemGrp
            split = layout.split(percentage=.85, align=1)
            split.prop(props, "elemGrp_%d_EGSidxName" %i)
            split.operator("bcb.tool_select_group", icon="UV_ISLANDSEL")

            ###### Formula assistant box

            box = layout.box()
            box.prop(props, "submenu_assistant", text="Formula Assistant", icon=self.icon_pulldown(props.submenu_assistant), emboss = False)
            if props.submenu_assistant:
                col = box.column(align=1)

                # Pull-down selector
                row = col.row(align=1); row.prop(props, "assistant_menu")
                    
                ### Reinforced Concrete (Beams & Columns)
                if props.assistant_menu == "con_rei_beam":
                    col.separator()
                    col.label(text="Strengths of Base Material and Reinforcement:")
                    row = col.split(align=1); row.prop(props_asst_con_rei_beam, "fc")
                    row.prop(props_asst_con_rei_beam, "fs")
                    if props.submenu_assistant_advanced:
                        row = col.split(align=1); row.prop(props_asst_con_rei_beam, "elu")
                        row.prop(props_asst_con_rei_beam, "fsu")
                    col.separator()
                    col.label(text="Geometry Parameters and Coefficients:")
                    row = col.split(align=1); row.prop(props_asst_con_rei_beam, "h")
                    row.prop(props_asst_con_rei_beam, "w")
                    row = col.split(align=1); row.prop(props_asst_con_rei_beam, "c")
                    row.prop(props_asst_con_rei_beam, "s")
                    row = col.split(align=1); row.prop(props_asst_con_rei_beam, "ds")
                    row.prop(props_asst_con_rei_beam, "dl")
                    row = col.split(align=1); row.prop(props_asst_con_rei_beam, "n")
                    if props.submenu_assistant_advanced:
                        row.prop(props_asst_con_rei_beam, "k")
                    else: row.label(text="")
                    col.separator()
                    col.label(text="Automatic & Manual Input is Allowed Here:")
                    row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_d")
                    row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_e")
                    row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_rho")
                    row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_y")
                    row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_e1")
                    if props.submenu_assistant_advanced:
                        col.separator()
                        col.label(text="Breaking Threshold Formulas:")
                        row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_Nn")
                        row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_Np")
                        row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_Vpn")
                        row = col.row(align=1); row.prop(props_asst_con_rei_beam, "exp_Mpn")
                    
                ### Reinforced Concrete (Walls & Slabs)
                if props.assistant_menu == "con_rei_wall":
                    col.separator()
                    col.label(text="Strengths of Base Material and Reinforcement:")
                    row = col.split(align=1); row.prop(props_asst_con_rei_wall, "fc")
                    row.prop(props_asst_con_rei_wall, "fs")
                    if props.submenu_assistant_advanced:
                        row = col.split(align=1); row.prop(props_asst_con_rei_wall, "elu")
                        row.prop(props_asst_con_rei_wall, "fsu")
                    col.separator()
                    col.label(text="Geometry Parameters and Coefficients:")
                    row = col.split(align=1); row.prop(props_asst_con_rei_wall, "h")
                    row.prop(props_asst_con_rei_wall, "w")
                    row = col.split(align=1); row.prop(props_asst_con_rei_wall, "c")
                    row.prop(props_asst_con_rei_wall, "s")
                    row = col.split(align=1); row.prop(props_asst_con_rei_wall, "ds")
                    row.prop(props_asst_con_rei_wall, "dl")
                    row = col.split(align=1); row.prop(props_asst_con_rei_wall, "n")
                    if props.submenu_assistant_advanced:
                        row.prop(props_asst_con_rei_wall, "k")
                    else: row.label(text="")
                    col.separator()
                    col.label(text="Automatic & Manual Input is Allowed Here:")
                    row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_d")
                    row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_e")
                    row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_rho")
                    row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_y")
                    row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_e1")
                    if props.submenu_assistant_advanced:
                        col.separator()
                        col.label(text="Breaking Threshold Formulas:")
                        row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_Nn")
                        row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_Np")
                        row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_Vpn")
                        row = col.row(align=1); row.prop(props_asst_con_rei_wall, "exp_Mpn")
                    
                if props.assistant_menu != "None":
                    col.separator()
                    split = col.split(percentage=.85, align=1)
                    split2 = split.split(percentage=.5, align=1)
                    split2.operator("bcb.asst_update", icon="PASTEDOWN")
                    split2.operator("bcb.asst_update_all", icon="SCRIPT")
                    split3 = split.split(align=1)
                else:
                    col.separator()
                    split = col.split(percentage=.85, align=1)
                    split.operator("bcb.asst_update_all", icon="SCRIPT")
                    split3 = split.split(align=1)
                split3.prop(props, "submenu_assistant_advanced")
                    
            ###### Element group settings (more)        

            col = layout.column(align=1)
            row = col.row(align=1); row.prop(props, "elemGrp_%d_EGSidxCTyp" %i)
            if props.menu_gotData: row.enabled = 0
                
            ct = eval("props.elemGrp_%d_EGSidxCTyp" %i)
            try: connectType = connectTypes[ct]
            except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
            box = col.box();
            box.label(text=connectType[0])

            col.separator()
            row = col.row(align=1); row.label(text="Breaking Thresholds in [N or Nm] / mm²:")

            # Prepare possible expression variables
            a = h = w = b = s = 1   

            expression = eval("props.elemGrp_%d_EGSidxBTC" %i)
            row = col.row(align=1)
            try: value = eval(expression)
            except: row.alert = 1; qAlert = 1
            else: qAlert = 0
            row.prop(props, "elemGrp_%d_EGSidxBTC" %i)
            if not connectType[2][0]: row.active = 0
            if qAlert: row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTT" %i)
            row = col.row(align=1)
            try: value = eval(expression)
            except: row.alert = 1; qAlert = 1
            else: qAlert = 0
            row.prop(props, "elemGrp_%d_EGSidxBTT" %i)
            if not connectType[2][1]: row.active = 0
            if qAlert: row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTS" %i)
            row = col.row(align=1)
            try: value = eval(expression)
            except: row.alert = 1; qAlert = 1
            else: qAlert = 0
            row.prop(props, "elemGrp_%d_EGSidxBTS" %i)
            if not connectType[2][2]: row.active = 0
            if qAlert: row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTS9" %i)
            if expression != "" or props.submenu_assistant_advanced:
                row = col.row(align=1)
                try: value = eval(expression)
                except: qAlert = 1
                else: qAlert = 0
                if qAlert and expression != "": row.alert = 1
                row.prop(props, "elemGrp_%d_EGSidxBTS9" %i)
                if not connectType[2][2]: row.active = 0
                if qAlert and expression != "":
                    row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTB" %i)
            row = col.row(align=1)
            try: value = eval(expression)
            except: row.alert = 1; qAlert = 1
            else: qAlert = 0
            row.prop(props, "elemGrp_%d_EGSidxBTB" %i)
            if not connectType[2][3]: row.active = 0
            if qAlert: row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTB9" %i)
            if expression != "" or props.submenu_assistant_advanced:
                row = col.row(align=1)
                try: value = eval(expression)
                except: qAlert = 1
                else: qAlert = 0
                if qAlert and expression != "": row.alert = 1
                row.prop(props, "elemGrp_%d_EGSidxBTB9" %i)
                if not connectType[2][3]: row.active = 0
                if qAlert and expression != "":
                    row = col.row(align=1); row.label(text="Error in expression")

            expression = eval("props.elemGrp_%d_EGSidxBTP" %i)
            if expression != "" or props.submenu_assistant_advanced:
                row = col.row(align=1)
                try: value = eval(expression)
                except: qAlert = 1
                else: qAlert = 0
                if qAlert and expression != "": row.alert = 1
                row.prop(props, "elemGrp_%d_EGSidxBTP" %i)
                if not connectType[2][4]: row.active = 0
                if qAlert and expression != "":
                    row = col.row(align=1); row.label(text="Error in expression")

            value = eval("props.elemGrp_%d_EGSidxBTPL" %i)
            if value != 0 or props.submenu_assistant_advanced:
                row = col.row(align=1)
                row.prop(props, "elemGrp_%d_EGSidxBTPL" %i)
                if not connectType[2][4]: row.active = 0

            col.separator()
            value = eval("props.elemGrp_%d_EGSidxBTX" %i)
            if value != 1 or props.submenu_assistant_advanced:
                row = col.row(align=1)
                row.prop(props, "elemGrp_%d_EGSidxBTX" %i)
                if not connectType[2][4]: row.active = 0

            col.separator()
            #row = col.row(align=1); row.prop(props, "elemGrp_%d_EGSidxRqVP" %i)
            row = col.row(align=1); row.prop(props, "elemGrp_%d_EGSidxMatP" %i)
            row = col.row(align=1); row.prop(props, "elemGrp_%d_EGSidxDens" %i)
            row = col.row(align=1); row.prop(props, "elemGrp_%d_EGSidxPrio" %i)
                            
            ###### Advanced element group settings box
            
            box = layout.box()
            box.prop(props, "submenu_advancedE", text="Advanced Element Settings", icon=self.icon_pulldown(props.submenu_advancedE), emboss = False)

            if props.submenu_advancedE:
                col = box.column(align=1)

                row = col.row(align=1); row.label(text="1st & 2nd Tolerance (Plastic & Breaking):")
                row = col.row(align=1)
                split = row.split(align=1);
                split.prop(props, "elemGrp_%d_EGSidxTl1D" %i)
                split.prop(props, "elemGrp_%d_EGSidxTl1R" %i)
                if not connectType[2][5]: split.active = 0
                row = col.row(align=1)
                split = row.split(align=1);
                split.prop(props, "elemGrp_%d_EGSidxTl2D" %i)
                split.prop(props, "elemGrp_%d_EGSidxTl2R" %i)
                if not connectType[2][7]: split.active = 0
                value1 = eval("props.elemGrp_%d_EGSidxTl2D" %i)
                value2 = eval("props.elemGrp_%d_EGSidxTl2R" %i)
                if value1 == 0 or value2 == 0: split.active = 0
                
                col.separator()
                row = col.row(align=1)
                if props.menu_gotData: row.enabled = 0
                row.prop(props, "elemGrp_%d_EGSidxCyln" %i)
                row.prop(props, "elemGrp_%d_EGSidxScal" %i)
                row = col.row(align=1)
                if props.menu_gotData: row.enabled = 0
                row.prop(props, "elemGrp_%d_EGSidxBevl" %i)
                prop_EGSidxBevl = eval("props.elemGrp_%d_EGSidxBevl" %i)
                prop_EGSidxFacg = eval("props.elemGrp_%d_EGSidxFacg" %i)
                if prop_EGSidxBevl and not prop_EGSidxFacg: row.alert = 1
                if props.menu_gotData: row.enabled = 0
                row.prop(props, "elemGrp_%d_EGSidxFacg" %i)
                
                if prop_EGSidxBevl and not prop_EGSidxFacg:
                    row = col.row(align=1); row.label(text="Warning: Disabled facing")
                    row = col.row(align=1); row.label(text="makes bevel permanent!")

        ### Update global vars from menu related properties
        props.props_update_globals()
    