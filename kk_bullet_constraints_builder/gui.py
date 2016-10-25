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
        except: elemGrps = mem["elemGrps"] = elemGrpsBak
        #print(props_asst_con_rei_beam.h, '\n', elemGrps[props.menu_selectedElemGrp][EGSidxAsst])

        row = layout.row()
        if not props.menu_gotData: 
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.build", icon="MOD_SKIN")
            split2 = split.split(align=False)
            if not props.menu_gotConfig:
                if not "bcb_prop_elemGrps" in scene.keys(): split2.enabled = 0
                split2.operator("bcb.get_config", icon="FILE_REFRESH")
            else: split2.operator("bcb.clear", icon="CANCEL")

            row = layout.row()
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=False)
            split2.operator("bcb.set_config", icon="NEW")
        else:
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.update", icon="FILE_REFRESH")
            split2 = split.split(align=False)
            split2.operator("bcb.clear", icon="CANCEL")

            row = layout.row()
            split = row.split(percentage=.85, align=False)
            split.operator("bcb.bake", icon="REC")
            split2 = split.split(align=False)
            split2.operator("bcb.set_config", icon="NEW")

        layout.separator()
        row = layout.row()
        if props.menu_gotData: row.enabled = 0
        row.prop(props, "searchDistance")
        
        row = layout.row()
        split = row.split(percentage=.85, align=False)
        if props.menu_gotData: split.enabled = 0
        split.prop(props, "clusterRadius")
        split.operator("bcb.tool_estimate_cluster_radius", icon="AUTO")
        
        ###### Advanced main settings box
        
        layout.separator()
        box = layout.box()
        box.prop(props, "submenu_advancedG", text="Advanced Global Settings", icon=self.icon_pulldown(props.submenu_advancedG), emboss = False)

        if props.submenu_advancedG:
            row = box.row()
            split = row.split(percentage=.85, align=False)
            split2 = split.split(percentage=.5, align=False)
            split2.operator("bcb.export_ascii", icon="EXPORT")
            split2.operator("bcb.export_ascii_fm", icon="EXPORT")
            split.operator("bcb.import_config", icon="FILE_REFRESH")
            row = box.row()
            split = row.split(percentage=.85, align=False)
            split.prop(props, "stepsPerSecond")
            split.operator("bcb.export_config", icon="NEW")

            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "constraintUseBreaking")
            split.prop(props, "disableCollision")
       
            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "automaticMode")
            split.prop(props, "saveBackups")
            box.separator()

            row = box.row()
            split = row.split(percentage=.50, align=False)
            split.prop(props, "snapToAreaOrient")
            split.prop(props, "lowerBrkThresPriority")
            row = box.row()
            if props.snapToAreaOrient: row.enabled = 0
            row.prop(props, "alignVertical")
            box.separator()

            row = box.row()
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "useAccurateArea")
#            row = box.row()
#            if not props.useAccurateArea: row.enabled = 0
#            row.prop(props, "nonManifoldThickness")
            row = box.row()
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "connectionCountLimit")
            row = box.row()
            if props.menu_gotData: row.enabled = 0
            row.prop(props, "minimumElementSize")

            row = box.row(); row.prop(props, "warmUpPeriod")
            box.separator()
            row = box.row(); row.prop(props, "timeScalePeriod")
            row = box.row(); row.prop(props, "timeScalePeriodValue")
            if props.timeScalePeriod == 0: row.enabled = 0
            box.separator()

            row = box.row(); row.prop(props, "progrWeak")
            row = box.row(); row.prop(props, "progrWeakLimit")
            if props.progrWeak == 0: row.enabled = 0
            row = box.row(); row.prop(props, "progrWeakStartFact")

        ###### Advanced main settings box
        
        box = layout.box()
        box.prop(props, "submenu_preprocTools", text="Preprocessing Tools", icon=self.icon_pulldown(props.submenu_preprocTools), emboss = False)

        if props.submenu_preprocTools:
            row = box.row(); split = row.split(percentage=.08, align=False)
            split.label(text="", icon="LINKED")
            split.operator("bcb.tool_do_all_steps_at_once", icon="DOTSUP")
            box.separator()
            
            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_grp", text="")
            box2 = split.box()
            box2.operator("bcb.tool_create_groups_from_names", icon="DOT")
            row2 = box2.row(); row2.prop(props, "preprocTools_grp_sep")

            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_mod", text="")
            box2 = split.box()
            box2.operator("bcb.tool_apply_all_modifiers", icon="DOT")

            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_rbs", text="")
            box2 = split.box()
            box2.operator("bcb.tool_enable_rigid_bodies", icon="DOT")

            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_sep", text="")
            box2 = split.box()
            box2.operator("bcb.tool_separate_loose", icon="DOT")

            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_dis", text="")
            box2 = split.box()
            box2.operator("bcb.tool_discretize", icon="DOT")
            row2 = box2.row(); row2.prop(props, "preprocTools_dis_siz")
            row2 = box2.row(); row2.prop(props, "preprocTools_dis_jus")

            row = box.row(); split = row.split(percentage=.08, align=False)
            split.prop(props, "preprocTools_fix", text="")
            box2 = split.box()
            box2.operator("bcb.tool_fix_foundation", icon="DOT")
            row2 = box2.row(); row2.prop(props, "preprocTools_fix_gnd")
            row2 = box2.row(); row2.prop(props, "preprocTools_fix_obj")
            
        ###### Element groups box
        
        layout.separator()
        row = layout.row(); row.label(text="Element Groups", icon="MOD_BUILD")
        box = layout.box()
        row = box.split(align=False)
        row.operator("bcb.add", icon="ZOOMIN")
        row.operator("bcb.del", icon="X")
        row.operator("bcb.reset", icon="CANCEL")
        row.operator("bcb.move_up", icon="TRIA_UP")
        row.operator("bcb.move_down", icon="TRIA_DOWN")
        row = box.row()
        split = row.split(percentage=.25, align=False)
        split.label(text="GRP")
        split2 = split.split(align=False)
        split2.label(text="CT")
        split2.label(text="CPR")
        split2.label(text="TNS")
        split2.label(text="SHR")
        split2.label(text="BND")
        for i in range(len(elemGrps)):
            if i == props.menu_selectedElemGrp:
                  row = box.box().row()
            else: row = box.row()
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
            split = row.split(percentage=.25, align=False)
            if prop_EGSidxName == "": split.label(text="[Def.]")
            else:                     split.label(text=str(prop_EGSidxName))
            split2 = split.split(align=False)
            split2.label(text=str(prop_EGSidxCTyp))
            split2.label(text=str(prop_EGSidxBTC))
            split2.label(text=str(prop_EGSidxBTT))
            split2.label(text=str(prop_EGSidxBTS))
            split2.label(text=str(prop_EGSidxBTB))
        row = box.row()
        row.operator("bcb.up", icon="TRIA_UP")
        row.operator("bcb.down", icon="TRIA_DOWN")
        
        ###### Element group settings
        
        layout.separator()
        i = props.menu_selectedElemGrp
        row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxName" %i)

        ###### Formula assistant box

        box = layout.box()
        box.prop(props, "submenu_assistant", text="Formula Assistant", icon=self.icon_pulldown(props.submenu_assistant), emboss = False)

        if props.submenu_assistant:
            # Pull-down selector
            row = box.row(); row.prop(props, "assistant_menu")

            ### Reinforced Concrete (Beams & Columns)
            if props.assistant_menu == "con_rei_beam":
                box.label(text="Strengths of Base Material and Reinforcement:")
                row = box.split(); row.prop(props_asst_con_rei_beam, "fc")
                row.prop(props_asst_con_rei_beam, "fs")
                box.label(text="Geometry Parameters and Coefficients:")
                row = box.split(); row.prop(props_asst_con_rei_beam, "h")
                row.prop(props_asst_con_rei_beam, "w")
                row = box.split(); row.prop(props_asst_con_rei_beam, "c")
                row.prop(props_asst_con_rei_beam, "s")
                row = box.split(); row.prop(props_asst_con_rei_beam, "ds")
                row.prop(props_asst_con_rei_beam, "dl")
                row = box.split(); row.prop(props_asst_con_rei_beam, "n")
                if props.submenu_assistant_advanced:
                    row.prop(props_asst_con_rei_beam, "k")
                else: row.label(text="")
                box.label(text="Automatic & Manual Input is Allowed Here:")
                row = box.row(); row.prop(props_asst_con_rei_beam, "exp_d")
                row = box.row(); row.prop(props_asst_con_rei_beam, "exp_e")
                row = box.row(); row.prop(props_asst_con_rei_beam, "exp_rho")
                row = box.row(); row.prop(props_asst_con_rei_beam, "exp_y")
                row = box.row(); row.prop(props_asst_con_rei_beam, "exp_e1")
                if props.submenu_assistant_advanced:
                    box.label(text="Breaking Threshold Formulas:")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "exp_Nn")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "exp_Np")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "exp_Vpn")
                    row = box.row(); row.prop(props_asst_con_rei_beam, "exp_Mpn")
                
            ### Reinforced Concrete (Walls & Slabs)
            if props.assistant_menu == "con_rei_wall":
                box.label(text="Strengths of Base Material and Reinforcement:")
                row = box.split(); row.prop(props_asst_con_rei_wall, "fc")
                row.prop(props_asst_con_rei_wall, "fs")
                box.label(text="Geometry Parameters and Coefficients:")
                row = box.split(); row.prop(props_asst_con_rei_wall, "h")
                row.prop(props_asst_con_rei_wall, "w")
                row = box.split(); row.prop(props_asst_con_rei_wall, "c")
                row.prop(props_asst_con_rei_wall, "s")
                row = box.split(); row.prop(props_asst_con_rei_wall, "ds")
                row.prop(props_asst_con_rei_wall, "dl")
                row = box.split(); row.prop(props_asst_con_rei_wall, "n")
                if props.submenu_assistant_advanced:
                    row.prop(props_asst_con_rei_wall, "k")
                else: row.label(text="")
                box.label(text="Automatic & Manual Input is Allowed Here:")
                row = box.row(); row.prop(props_asst_con_rei_wall, "exp_d")
                row = box.row(); row.prop(props_asst_con_rei_wall, "exp_e")
                row = box.row(); row.prop(props_asst_con_rei_wall, "exp_rho")
                row = box.row(); row.prop(props_asst_con_rei_wall, "exp_y")
                row = box.row(); row.prop(props_asst_con_rei_wall, "exp_e1")
                if props.submenu_assistant_advanced:
                    box.label(text="Breaking Threshold Formulas:")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "exp_Nn")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "exp_Np")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "exp_Vpn")
                    row = box.row(); row.prop(props_asst_con_rei_wall, "exp_Mpn")
                
            if props.assistant_menu != "None":
                split = box.split(percentage=.85, align=False)
                split.operator("bcb.asst_update", icon="PASTEDOWN")
                split2 = split.split(align=False)
                split2.prop(props, "submenu_assistant_advanced")
                
        layout.separator()

        ###### Element group settings (more)        

        row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxCTyp" %i)
        if props.menu_gotData: row.enabled = 0
            
        ct = eval("props.elemGrp_%d_EGSidxCTyp" %i)
        try: connectType = connectTypes[ct]
        except: connectType = connectTypes[0]  # In case the connection type is unknown (no constraints)
        box = layout.box();
        box.label(text=connectType[0])

        row = layout.row(); row.label(text="Breaking Thresholds in [N or Nm] / mm²:")

        # Prepare possible expression variables
        a = h = w = b = s = 1   

        expression = eval("props.elemGrp_%d_EGSidxBTC" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "elemGrp_%d_EGSidxBTC" %i)
        if not connectType[2][0]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.elemGrp_%d_EGSidxBTT" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "elemGrp_%d_EGSidxBTT" %i)
        if not connectType[2][1]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.elemGrp_%d_EGSidxBTS" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "elemGrp_%d_EGSidxBTS" %i)
        if not connectType[2][2]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        if props.submenu_assistant_advanced:
            expression = eval("props.elemGrp_%d_EGSidxBTS9" %i)
            if expression != "":
                row = layout.row()
                try: value = eval(expression)
                except: row.alert = 1; qAlert = 1
                else: qAlert = 0
                row.prop(props, "elemGrp_%d_EGSidxBTS9" %i)
                if not connectType[2][2]: row.active = 0
                if qAlert: row = layout.row(); row.label(text="Error in expression")

        expression = eval("props.elemGrp_%d_EGSidxBTB" %i)
        row = layout.row()
        try: value = eval(expression)
        except: row.alert = 1; qAlert = 1
        else: qAlert = 0
        row.prop(props, "elemGrp_%d_EGSidxBTB" %i)
        if not connectType[2][3]: row.active = 0
        if qAlert: row = layout.row(); row.label(text="Error in expression")

        if props.submenu_assistant_advanced:
            expression = eval("props.elemGrp_%d_EGSidxBTB9" %i)
            if expression != "":
                row = layout.row()
                try: value = eval(expression)
                except: row.alert = 1; qAlert = 1
                else: qAlert = 0
                row.prop(props, "elemGrp_%d_EGSidxBTB9" %i)
                if not connectType[2][3]: row.active = 0
                if qAlert: row = layout.row(); row.label(text="Error in expression")

        layout.separator()
        #row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxRqVP" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxMatP" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxDens" %i)
        
        layout.separator()
        row = layout.row()
        if props.menu_gotData: row.enabled = 0
        row.prop(props, "elemGrp_%d_EGSidxScal" %i)
        row = layout.row(); row.prop(props, "elemGrp_%d_EGSidxCyln" %i)
        row = layout.row()
        if props.menu_gotData: row.enabled = 0
        row.prop(props, "elemGrp_%d_EGSidxBevl" %i)
        prop_EGSidxBevl = eval("props.elemGrp_%d_EGSidxBevl" %i)
        prop_EGSidxFacg = eval("props.elemGrp_%d_EGSidxFacg" %i)
        if prop_EGSidxBevl and not prop_EGSidxFacg: row.alert = 1
        if props.menu_gotData: row.enabled = 0
        row.prop(props, "elemGrp_%d_EGSidxFacg" %i)
        
        if prop_EGSidxBevl and not prop_EGSidxFacg:
            row = layout.row(); row.label(text="Warning: Disabled facing")
            row = layout.row(); row.label(text="makes bevel permanent!")
            
        ###### Advanced element group settings box
        
        box = layout.box()
        box.prop(props, "submenu_advancedE", text="Advanced Element Settings", icon=self.icon_pulldown(props.submenu_advancedE), emboss = False)

        if props.submenu_advancedE:
            row = box.row(); row.prop(props, "elemGrp_%d_EGSidxSStf" %i)
            if not connectType[2][4]: row.active = 0
            row = box.row(); row.label(text="1st & 2nd Tolerance (Plastic & Breaking):")
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "elemGrp_%d_EGSidxTl1D" %i)
            split.prop(props, "elemGrp_%d_EGSidxTl1R" %i)
            if not connectType[2][5]: split.active = 0
            row = box.row()
            split = row.split(percentage=.50, align=False);
            split.prop(props, "elemGrp_%d_EGSidxTl2D" %i)
            split.prop(props, "elemGrp_%d_EGSidxTl2R" %i)
            if not connectType[2][7]: split.active = 0
            
        ### Update global vars from menu related properties
        props.props_update_globals()
