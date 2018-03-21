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
from global_vars import *      # Contains global variables

################################################################################

class bcb_asst_con_rei_beam_props(bpy.types.PropertyGroup):
    
    classID = "con_rei_beam"

    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    string_ = bpy.props.StringProperty

    # Find corresponding formula assistant preset
    for formAssist in formulaAssistants:
        if formAssist["ID"] == classID:
            asst = formAssist

    h =  float_(name='h', default=asst['h'], min=0, max=100000, description='Height of element (mm). Leave it 0 to pass it through as variable instead of a fixed number')
    w =  float_(name='w', default=asst['w'], min=0, max=100000, description='Width of element (mm). Leave it 0 to pass it through as variable instead of a fixed number')
    fs = float_(name='fs', default=asst['fs'], min=0, max=100000, description='Yield strength of reinforcement irons (N/mm^2)')
    fc = float_(name='fc', default=asst['fc'], min=0, max=100000, description='Yield strength of concrete (N/mm^2)')
    fsu = float_(name='fsu', default=asst['fsu'], min=0, max=100000, description='Ultimate breaking strength of reinforcement irons (N/mm^2)')
    elu = float_(name='elu', default=asst['elu'], min=0, max=100000, description='Ultimate elongation of reinforcement irons (%)')
    densc = float_(name='Dens. Concrete', default=asst['densc'], min=0, max=100000, description='Density for concrete (kg/m^3)')
    denss = float_(name='Dens. Reinforcement', default=asst['denss'], min=0, max=100000, description='Density for reinforcement / steel (kg/m^3)')
    c  = float_(name='c', default=asst['c'], min=0, max=100000, description='Concrete cover thickness above reinforcement (mm)')
    s  = float_(name='s', default=asst['s'], min=0, max=100000, description='Distance between stirrups (mm)')
    ds = float_(name='ds', default=asst['ds'], min=0, max=100000, description='Diameter of steel stirrup bar (mm)')
    dl = float_(name='dl', default=asst['dl'], min=0, max=100000, description='Diameter of steel longitudinal bar (mm)')
    n    = int_(name='n', default=asst['n'], min=0, max=100000, description='Number of longitudinal steel bars')
    k  = float_(name='k', default=asst['k'], min=0, max=100000, description='Scale factor')
    
    exp_d   = string_(name='d', default=asst['Exp:d'], description='Distance between the tensile irons and the opposite concrete surface (mm)')
    exp_e   = string_(name='e', default=asst['Exp:e'], description='Distance between longitudinal irons (mm)')
    exp_rho = string_(name='ϱ (rho)', default=asst['Exp:rho'], description='Reinforcement ratio = As/A')
    exp_y   = string_(name='υ (y)', default=asst['Exp:y'], description='Shear coefficient (asw*10/d) (% value)')
    exp_e1  = string_(name='e´ (e1)', default=asst['Exp:e1'], description='Distance between longitudinal irons in relation to the element height: e/h (% value)')
    exp_Nn  = string_(name='N-', default=asst['Exp:N-'], description='Compressive breaking threshold formula')
    exp_Np  = string_(name='N+', default=asst['Exp:N+'], description='Tensile breaking threshold formula')
    exp_Vpn = string_(name='V+/-', default=asst['Exp:V+/-'], description='Shearing breaking threshold formula')
    exp_Mpn = string_(name='M+/-', default=asst['Exp:M+/-'], description='Bending or momentum breaking threshold formula')

    ###### Update menu related properties from global vars
    def props_update_menu(self):
        props = bpy.context.window_manager.bcb
        i = props.menu_selectedElemGrp
        elemGrps = mem["elemGrps"]
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        asst = elemGrps[i][EGSidxAsst]
        self.h = asst['h']
        self.w = asst['w']
        self.fs = asst['fs']
        self.fc = asst['fc']
        self.fsu = asst['fsu']
        self.elu = asst['elu']
        self.densc = asst['densc']
        self.denss = asst['denss']
        self.c = asst['c']
        self.s = asst['s']
        self.ds = asst['ds']
        self.dl = asst['dl']
        self.n = asst['n']
        self.k = asst['k']

        self.exp_d = asst['Exp:d']
        self.exp_e = asst['Exp:e']
        self.exp_rho = asst['Exp:rho']
        self.exp_y = asst['Exp:y']
        self.exp_e1 = asst['Exp:e1']
        self.exp_Nn = asst['Exp:N-']
        self.exp_Np = asst['Exp:N+']
        self.exp_Vpn = asst['Exp:V+/-']
        self.exp_Mpn = asst['Exp:M+/-']
        
    ###### Update global vars from menu related properties
    def props_update_globals(self):
        props = bpy.context.window_manager.bcb
        i = props.menu_selectedElemGrp
        elemGrps = mem["elemGrps"]
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        elemGrps[i][EGSidxAsst]['h'] = self.h
        elemGrps[i][EGSidxAsst]['w'] = self.w
        elemGrps[i][EGSidxAsst]['fs'] = self.fs
        elemGrps[i][EGSidxAsst]['fc'] = self.fc
        elemGrps[i][EGSidxAsst]['fsu'] = self.fsu
        elemGrps[i][EGSidxAsst]['elu'] = self.elu
        elemGrps[i][EGSidxAsst]['densc'] = self.densc
        elemGrps[i][EGSidxAsst]['denss'] = self.denss
        elemGrps[i][EGSidxAsst]['c'] = self.c
        elemGrps[i][EGSidxAsst]['s'] = self.s
        elemGrps[i][EGSidxAsst]['ds'] = self.ds
        elemGrps[i][EGSidxAsst]['dl'] = self.dl
        elemGrps[i][EGSidxAsst]['n'] = self.n
        elemGrps[i][EGSidxAsst]['k'] = self.k

        elemGrps[i][EGSidxAsst]['Exp:d'] = self.exp_d
        elemGrps[i][EGSidxAsst]['Exp:e'] = self.exp_e
        elemGrps[i][EGSidxAsst]['Exp:rho'] = self.exp_rho
        elemGrps[i][EGSidxAsst]['Exp:y'] = self.exp_y
        elemGrps[i][EGSidxAsst]['Exp:e1'] = self.exp_e1
        elemGrps[i][EGSidxAsst]['Exp:N-'] = self.exp_Nn
        elemGrps[i][EGSidxAsst]['Exp:N+'] = self.exp_Np
        elemGrps[i][EGSidxAsst]['Exp:V+/-'] = self.exp_Vpn
        elemGrps[i][EGSidxAsst]['Exp:M+/-'] = self.exp_Mpn
        
########################################

class bcb_asst_con_rei_wall_props(bpy.types.PropertyGroup):

    classID = "con_rei_wall"

    int_ = bpy.props.IntProperty 
    float_ = bpy.props.FloatProperty
    string_ = bpy.props.StringProperty

    # Find corresponding formula assistant preset
    for formAssist in formulaAssistants:
        if formAssist["ID"] == classID:
            asst = formAssist

    h =  float_(name='h', default=asst['h'], min=0, max=100000, description='Height of element (mm). Leave it 0 to pass it through as variable instead of a fixed number')
    w =  float_(name='w', default=asst['w'], min=0, max=100000, description='Width of element (mm). Leave it 0 to pass it through as variable instead of a fixed number')
    fs = float_(name='fs', default=asst['fs'], min=0, max=100000, description='Yield strength of reinforcement irons (N/mm^2)')
    fc = float_(name='fc', default=asst['fc'], min=0, max=100000, description='Yield strength of concrete (N/mm^2)')
    fsu = float_(name='fsu', default=asst['fsu'], min=0, max=100000, description='Ultimate breaking strength of reinforcement irons (N/mm^2)')
    elu = float_(name='elu', default=asst['elu'], min=0, max=100000, description='Ultimate elongation of reinforcement irons (%)')
    densc = float_(name='Dens. Concrete', default=asst['densc'], min=0, max=100000, description='Density for concrete in kg/m^3')
    denss = float_(name='Dens. Reinforcement', default=asst['denss'], min=0, max=100000, description='Density for reinforcement / steel in kg/m^3')
    c  = float_(name='c', default=asst['c'], min=0, max=100000, description='Concrete cover thickness above reinforcement (mm)')
    s  = float_(name='s', default=asst['s'], min=0, max=100000, description='Distance between stirrups (mm)')
    ds = float_(name='ds', default=asst['ds'], min=0, max=100000, description='Diameter of steel stirrup bar (mm)')
    dl = float_(name='dl', default=asst['dl'], min=0, max=100000, description='Diameter of steel longitudinal bar (mm)')
    n    = int_(name='n', default=asst['n'], min=0, max=100000, description='Number of longitudinal steel bars')
    k  = float_(name='k', default=asst['k'], min=0, max=100000, description='Scale factor')

    exp_d   = string_(name='d', default=asst['Exp:d'], description='Distance between the tensile irons and the opposite concrete surface (mm)')
    exp_e   = string_(name='e', default=asst['Exp:e'], description='Distance between longitudinal irons (mm)')
    exp_rho = string_(name='ϱ (rho)', default=asst['Exp:rho'], description='Reinforcement ratio = As/A')
    exp_y   = string_(name='υ (y)', default=asst['Exp:y'], description='Shear coefficient (asw*10/d) (% value)')
    exp_e1  = string_(name='e´ (e1)', default=asst['Exp:e1'], description='Distance between longitudinal irons in relation to the element height: e/h (% value)')
    exp_Nn  = string_(name='N-', default=asst['Exp:N-'], description='Compressive breaking threshold formula')
    exp_Np  = string_(name='N+', default=asst['Exp:N+'], description='Tensile breaking threshold formula')
    exp_Vpn = string_(name='V+/-', default=asst['Exp:V+/-'], description='Shearing breaking threshold formula')
    exp_Mpn = string_(name='M+/-', default=asst['Exp:M+/-'], description='Bending or momentum breaking threshold formula')

    ###### Update menu related properties from global vars
    def props_update_menu(self):
        props = bpy.context.window_manager.bcb
        i = props.menu_selectedElemGrp
        # Check if stored ID matches the correct assistant type otherwise return
        elemGrps = mem["elemGrps"]
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        asst = elemGrps[i][EGSidxAsst]
        self.h = asst['h']
        self.w = asst['w']
        self.fs = asst['fs']
        self.fc = asst['fc']
        self.fsu = asst['fsu']
        self.elu = asst['elu']
        self.densc = asst['densc']
        self.denss = asst['denss']
        self.c = asst['c']
        self.s = asst['s']
        self.ds = asst['ds']
        self.dl = asst['dl']
        self.n = asst['n']
        self.k = asst['k']

        self.exp_d = asst['Exp:d']
        self.exp_e = asst['Exp:e']
        self.exp_rho = asst['Exp:rho']
        self.exp_y = asst['Exp:y']
        self.exp_e1 = asst['Exp:e1']
        self.exp_Nn = asst['Exp:N-']
        self.exp_Np = asst['Exp:N+']
        self.exp_Vpn = asst['Exp:V+/-']
        self.exp_Mpn = asst['Exp:M+/-']
        
    ###### Update global vars from menu related properties
    def props_update_globals(self):
        props = bpy.context.window_manager.bcb
        i = props.menu_selectedElemGrp
        elemGrps = mem["elemGrps"]
        # Check if stored ID matches the correct assistant type otherwise return
        if elemGrps[i][EGSidxAsst]['ID'] != self.classID: return

        elemGrps[i][EGSidxAsst]['h'] = self.h
        elemGrps[i][EGSidxAsst]['w'] = self.w
        elemGrps[i][EGSidxAsst]['fs'] = self.fs
        elemGrps[i][EGSidxAsst]['fc'] = self.fc
        elemGrps[i][EGSidxAsst]['fsu'] = self.fsu
        elemGrps[i][EGSidxAsst]['elu'] = self.elu
        elemGrps[i][EGSidxAsst]['densc'] = self.densc
        elemGrps[i][EGSidxAsst]['denss'] = self.denss
        elemGrps[i][EGSidxAsst]['c'] = self.c
        elemGrps[i][EGSidxAsst]['s'] = self.s
        elemGrps[i][EGSidxAsst]['ds'] = self.ds
        elemGrps[i][EGSidxAsst]['dl'] = self.dl
        elemGrps[i][EGSidxAsst]['n'] = self.n
        elemGrps[i][EGSidxAsst]['k'] = self.k

        elemGrps[i][EGSidxAsst]['Exp:d'] = self.exp_d
        elemGrps[i][EGSidxAsst]['Exp:e'] = self.exp_e
        elemGrps[i][EGSidxAsst]['Exp:rho'] = self.exp_rho
        elemGrps[i][EGSidxAsst]['Exp:y'] = self.exp_y
        elemGrps[i][EGSidxAsst]['Exp:e1'] = self.exp_e1
        elemGrps[i][EGSidxAsst]['Exp:N-'] = self.exp_Nn
        elemGrps[i][EGSidxAsst]['Exp:N+'] = self.exp_Np
        elemGrps[i][EGSidxAsst]['Exp:V+/-'] = self.exp_Vpn
        elemGrps[i][EGSidxAsst]['Exp:M+/-'] = self.exp_Mpn
