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

import bpy, mathutils, pickle, zlib, base64
from mathutils import Vector

### Import submodules
from global_vars import *      # Contains global variables

################################################################################

def removeBadCharsFromFilename(filename):
    
    # Replaces problematic chars from a filename string with a clean underscore
    filenameNew = ""
    for b in filename:
        if b > chr(0x2c) and b not in ":?<>|/\\":  # General conditions 
            filenameNew += b
        elif b in " ,'`!.()[]{}+-&$^=":  # Accepted under 0x2c
            filenameNew += b
        elif b == '\"':
            filenameNew += '\''
        else:
            filenameNew += '_'
    return filenameNew
        
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
    configData.append(props.passiveUseBreaking)
    configData.append(props.connectionCountLimit)
    configData.append(props.searchDistance)
    configData.append(props.clusterRadius)
    configData.append(props.alignVertical)
    configData.append(props.useAccurateArea)
    configData.append(props.rebarMesh)
    configData.append(props.surfaceThickness)
    configData.append(props.surfaceForced)
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
    configData.append(props.disableCollisionPerm)
    configData.append(props.lowerBrkThresPriority)
    configData.append(props.detonatorObj)
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
        props.passiveUseBreaking = configData[i]; i += 1
        props.connectionCountLimit = configData[i]; i += 1
        props.searchDistance = configData[i]; i += 1
        props.clusterRadius = configData[i]; i += 1
        props.alignVertical = configData[i]; i += 1
        props.useAccurateArea = configData[i]; i += 1
        props.rebarMesh = configData[i]; i += 1
        props.surfaceThickness = configData[i]; i += 1
        props.surfaceForced = configData[i]; i += 1
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
        props.disableCollisionPerm = configData[i]; i += 1
        props.lowerBrkThresPriority = configData[i]; i += 1
        props.detonatorObj = configData[i]; i += 1
        mem["elemGrps"] = configData[i]; i += 1
        return 0

################################################################################   

def getAttribsOfConstraint(const):

    ### Create a dictionary of all attributes with values from the given constraint empty object    
    props = {}
    for prop in const.bl_rna.properties:
        if not prop.is_hidden:
            if prop.identifier not in {"object1", "object2"}:
                if prop.type == 'POINTER':
                    attr = getattr(const, prop.identifier)
                    props[prop.identifier] = None
                    if attr is not None:
                        props[prop.identifier] = attr.name    
                else:   props[prop.identifier] = getattr(const, prop.identifier)
    return props

########################################

def setAttribsOfConstraint(const, props):

    ### Overwrite all attributes of the given constraint empty object with the values of the dictionary provided    
    for prop in props.items():
        try: attr = getattr(const, prop[0])
        except: pass
        else:
            if attr != prop[1]: setattr(const, prop[0], prop[1])

########################################

def exportDataToText(exportData):

    ### Exporting data into internal ASCII text file
    print("Exporting data into internal ASCII text file:", asciiExportName +".txt")
    
    ### Ascii export into internal text file
    exportDataStr = pickle.dumps(exportData, 4)  # 0 for using real ASCII pickle protocol and comment out the base64 lines (slower but human readable)
    exportDataStr = zlib.compress(exportDataStr, 9)
    exportDataStr = base64.encodebytes(exportDataStr)  # Convert binary data into "text" representation
    text = bpy.data.texts.new(asciiExportName +".txt")
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
