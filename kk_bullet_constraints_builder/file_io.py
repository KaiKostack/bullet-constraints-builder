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

import bpy, mathutils, pickle, zlib, base64
from mathutils import Vector

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

def dataToFile(data, pathName):
    try: f = open(pathName, "wb")
    except:
        print('Error: Could not write file:', pathName)
        return 1
    else:
        pickle.dump(data, f, 0)
        f.close()

########################################

def dataFromFile(pathName):
    try: f = open(pathName, "rb")
    except:
        print('Error: Could not read file:', pathName)
        return 1
    else:
        raw = f.read()
        data = pickle.loads(raw)
        f.close()
        return data
    return None

########################################

def makeListsPickleFriendly(listOld):
    listNew1 = []
    for sub1 in listOld:
        try: test = len(sub1)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
        except: listNew1.append(sub1); continue  # If it fails it is no list (and also no vector)
        else:
            if isinstance(sub1, str):            # It could still be a string so check that as well
                listNew1.append(sub1); continue  
        listNew2 = []
        for sub2 in sub1:
            try: test = len(sub2)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
            except: listNew2.append(sub2); continue  # If it fails it is no list (and also no vector)
            else:
                if isinstance(sub2, str):            # It could still be a string so check that as well
                    listNew2.append(sub2); continue  
            listNew3 = []
            for sub3 in sub2:
                try: test = len(sub3)                    # Check if sub is a list, isinstance(sub, list) doesn't work on ID property lists
                except: listNew3.append(sub3); continue  # If it fails it is no list (and also no vector)
                else:
                    if isinstance(sub3, str):            # It could still be a string so check that as well
                        listNew3.append(sub3); continue  
                listNew4 = []
                for sub4 in sub3:
                    listNew4.append(sub4)
                listNew3.append(listNew4)
            listNew2.append(listNew3)
        listNew1.append(listNew2)
    return listNew1

################################################################################

def exportConfigData(scene):

    ### Store menu config data to file
    print("Exporting config data to external file...")
    
    props = bpy.context.window_manager.bcb
    configData = []
    configData.append(bcb_version)
    configData.append(props.stepsPerSecond)
    configData.append(props.constraintUseBreaking)
    configData.append(props.connectionCountLimit)
    configData.append(props.searchDistance)
    configData.append(props.clusterRadius)
    configData.append(props.alignVertical)
    configData.append(props.useAccurateArea)
    configData.append(props.nonManifoldThickness)
    configData.append(props.minimumElementSize)
    configData.append(props.automaticMode)
    configData.append(props.saveBackups)
    configData.append(props.timeScalePeriod)
    configData.append(props.timeScalePeriodValue)
    configData.append(props.warmUpPeriod)
    configData.append(props.progrWeak)
    configData.append(props.progrWeakLimit)
    configData.append(props.progrWeakStartFact)
    configData.append(props.snapToAreaOrient)
    configData.append(props.disableCollision)
    configData.append(props.lowerBrkThresPriority)
    configData.append(mem["elemGrps"])
    dataToFile(configData, logPath +r"\bcb.cfg")
    
################################################################################

def importConfigData(scene):

    ### Importing menu config data from file
    print("Importing config data from external file...")
    
    configData = dataFromFile(logPath +r"\bcb.cfg")
    if configData == 1: return 1  # Error
    i = 0
    if bcb_version != configData[i]:
        print("Error: Version mismatch. Try to use the same version of the BCB for export and import.")
        return 1
    else:
        props = bpy.context.window_manager.bcb
        i += 1
        props.stepsPerSecond = configData[i]; i += 1
        props.constraintUseBreaking = configData[i]; i += 1
        props.connectionCountLimit = configData[i]; i += 1
        props.searchDistance = configData[i]; i += 1
        props.clusterRadius = configData[i]; i += 1
        props.alignVertical = configData[i]; i += 1
        props.useAccurateArea = configData[i]; i += 1
        props.nonManifoldThickness = configData[i]; i += 1
        props.minimumElementSize = configData[i]; i += 1
        props.automaticMode = configData[i]; i += 1
        props.saveBackups = configData[i]; i += 1
        props.timeScalePeriod = configData[i]; i += 1
        props.timeScalePeriodValue = configData[i]; i += 1
        props.warmUpPeriod = configData[i]; i += 1
        props.progrWeak = configData[i]; i += 1
        props.progrWeakLimit = configData[i]; i += 1
        props.progrWeakStartFact = configData[i]; i += 1
        props.snapToAreaOrient = configData[i]; i += 1
        props.disableCollision = configData[i]; i += 1
        props.lowerBrkThresPriority = configData[i]; i += 1
        mem["elemGrps"] = configData[i]; i += 1
        return 0

################################################################################   

def getAttribsOfConstraint(objConst):

    ### Create a dictionary of all attributes with values from the given constraint empty object    
    con = objConst.rigid_body_constraint
    props = {}
    for prop in con.bl_rna.properties:
        if not prop.is_hidden:
            if prop.identifier not in {"object1", "object2"}:
                if prop.type == 'POINTER':
                    attr = getattr(con, prop.identifier)
                    props[prop.identifier] = None
                    if attr is not None:
                        props[prop.identifier] = attr.name    
                else:   props[prop.identifier] = getattr(con, prop.identifier)
    return props
        
########################################

def export(exData, idx=None, objC=None, name=None, loc=None, obj1=None, obj2=None, tol1=None, tol2=None, rotm=None, rot=None, attr=None):

    ### Adds data to the export data array
    # export(exData, idx=1, objC=objConst, name=1, loc=1, obj1=1, obj2=1, tol1=[tol1dist, tol1rot], tol2=[tol2dist, tol2rot], rotm=1, rot=1, attr=1)
    
    if idx == None:
        exData.append([])
        idx = len(exData) -1
        for i in range(9):
            exData[idx].append(None)
    if name != None and objC != None: exData[idx][0] = objC.name
    elif name != None:                exData[idx][0] = name
    if loc != None and objC != None:  exData[idx][1] = objC.location.to_tuple()
    elif loc != None:                 exData[idx][1] = loc
    if obj1 != None and objC != None: exData[idx][2] = objC.rigid_body_constraint.object1.name
    elif obj1 != None:                exData[idx][2] = obj1
    if obj2 != None and objC != None: exData[idx][3] = objC.rigid_body_constraint.object2.name
    elif obj2 != None:                exData[idx][3] = obj2
    if tol1 != None and objC != None: exData[idx][4] = ["TOLERANCE", 0, 0]  # Undefined special case
    elif tol1 != None:                exData[idx][4] = tol1                 # Should always get data
    if tol2 != None and objC != None: exData[idx][5] = ["PLASTIC", 0, 0]  # Undefined special case
    elif tol2 != None:                exData[idx][5] = tol2               # Should always get data
    if rotm != None and objC != None: exData[idx][6] = objC.rotation_mode
    elif rotm != None:                exData[idx][6] = rotm
    if rot != None and objC != None:  exData[idx][7] = Vector(objC.rotation_quaternion).to_tuple()
    elif rot != None:                 exData[idx][7] = rot
    if attr != None and objC != None: exData[idx][8] = getAttribsOfConstraint(objC)
    elif attr != None:                exData[idx][8] = attr

    # Data structure ("[]" means not always present, will be None instead):
    # 0 - empty.name
    # 1 - empty.location
    # 2 - obj1.name
    # 3 - obj2.name
    # 4 - [ ["TOLERANCE", tol1dist, tol1rot] ]
    # 5 - [ ["PLASTIC"/"PLASTIC_OFF", tol2dist, tol2rot] ]
    # 6 - [empty.rotation_mode]
    # 7 - [empty.rotation_quaternion]
    # 8 - empty.rigid_body_constraint (dictionary of attributes)
    #
    # Pseudo code for special constraint treatment:
    #
    # If tol1dist or tol1rot is exceeded:
    #     If normal constraint: It will be detached
    #     If spring constraint: It will be set to active
    # If tol2dist or tol2rot is exceeded:
    #     If spring constraint: It will be detached

    return exData

########################################

def exportDataToText(exportData):

    ### Exporting data into internal ASCII text file
    print("Exporting data into internal ASCII text file:", asciiExportName)
    
    ### Ascii export into internal text file
    exportDataStr = pickle.dumps(exportData, 4)  # 0 for using real ASCII pickle protocol and comment out the base64 lines (slower but human readable)
    exportDataStr = zlib.compress(exportDataStr, 9)
    exportDataStr = base64.encodebytes(exportDataStr)  # Convert binary data into "text" representation
    text = bpy.data.texts.new(asciiExportName)
    text.write(exportDataStr.decode())
    
    ### Code for loading data back from text
#    exportDataStr = text.as_string()
#    exportDataStr = base64.decodestring(exportDataStr.encode())  # Convert binary data back from "text" representation
#    exportDataStr = zlib.decompress(exportDataStr)
#    exportData = pickle.loads(exportDataStr)  # Use exportDataStr.encode() here when using real ASCII pickle protocol
#    #print(exportData)
#    i = 0
#    for const in exportData:
#        if i > 300: bpy.ops.object.empty_add(type='SPHERE', view_align=False, location=const[0], layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
#        if i > 600: break
#        i += 1
    # For later import you can use setattr(item[0], item[1])
