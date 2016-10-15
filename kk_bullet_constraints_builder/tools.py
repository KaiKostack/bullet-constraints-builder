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
from builder_prep import *     # Contains preparation steps functions called by the builder

################################################################################

def estimateClusterRadius(scene):
    
    objs, emptyObjs = gatherObjects(scene)
    
    if len(objs) > 0:        
        print("Estimating optimal cluster radius...")
        
        #objsDiameter = []
        diameterSum = 0
        for obj in objs:
            
            ### Calculate diameter for each object
            dim = list(obj.dimensions)
            dim.sort()
            diameter = dim[2]   # Use the largest dimension axis as diameter
            
            #objsDiameter.append(diameter)
            diameterSum += diameter
        
#        ### Sort all diameters, take the midst item and multiply it by 1 /sqrt(2)
#        objsDiameter.sort()
#        diameterEstimation = (objsDiameter[int(len(objsDiameter) /2)] /2) *0.707

        ### Alternative: Calculate average of all object diameters and multiply it by 1 /sqrt(2)
        diameterEstimation = ((diameterSum /2) /len(objs)) *0.707
        
        return diameterEstimation

    else:
        print("Selected objects required for cluster radius estimation.") 
        return 0
