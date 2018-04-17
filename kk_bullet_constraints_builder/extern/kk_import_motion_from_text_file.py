#############################################
# Motion From Text File v1.2 by Kai Kostack #
#############################################
# This script imports ASCII based time histories of motion data.
# - Pay attention to the fps rate in Render panel before import

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

bl_info = {
    "name": "Motion Data Importer",
    "author": "Kai Kostack",
    "version": (1, 2, 0),
    "blender": (2, 69, 0),
    "location": "File > Import-Export",
    "warning": "",
    "description": "This script imports motion data for animation from a CSV text file.",
    "wiki_url": "",
    "tracker_url": "http://kaikostack.com",
    "support": "COMMUNITY",
    "category": "Import-Export"
}

"""
Notes:
The Motion format is very simple, it's just a simple ascii text file
with the location data for each frame listed on each line separated by tab spaces.
The first 3 columns contain X, Y and Z while the 4th column for custom timings is optional.
"""

import bpy
from operator import itemgetter, attrgetter, methodcaller

################################################################################   

def importData(filepath):
    
    ### Main function
    
    ### Vars
    logMode = 3    # Data interpretion mode (0 absolute location, 1 relative location, 2 velocity, 3 acceleration)
    timeStep = 0   # Timestep for value scaling (0 = off, > 0 = time step, overrides timescale derived from file time steps)
                   # This is only used for logMode > 1, you have to manually fit the length in curve editor, though. Set to 1 if unsure.

    ### Define columns (by column number, -1 = disabled)
    timS = 0  # Time step
    locX = 1; locY = 2; locZ = 3
    #rotX = -1; rotY = -1; rotZ = -1  # Not used atm

    ######
    # Umrechnung von Beschleunigungskräfte in G nach m/s²:
    # 1 G = 9,81 m/s²
    #
    # Relative Bewegungsänderung skaliert auf Zeitintervall:
    # weg = wegd *(1 /td)
    #
    # Gesamte Formel:
    # Beschleunigung [m/s²] *9.81 [m/s²] /0.005 [s] = Geschwindigkeit [m/s]
    # Geschwindigkeit [m/s] /0.005 [s] = Weg [m]

    scene = bpy.context.scene
    obj = scene.objects.active
    
    ### Read data from file
    linesItems = readData(filepath)
    if linesItems == None: return
    frameCount = len(linesItems)
     
    ### Use active/selected object, otherwise create a new camera
    if scene.objects.active is None or not scene.objects.active.select:
        bpy.ops.object.camera_add(view_align=False, enter_editmode=False, location=(0, 0, 0), rotation=(0, 0, 0))
        bpy.context.scene.camera = scene.objects.active

    # Owner of the animation data, can be object or scene 
    owner = obj

    ### Create new animation data and action if necessary
    if owner.animation_data == None:
        owner.animation_data_create()
    if owner.animation_data.action == None:
        print("Creating a new Motion action...")
        owner.animation_data.action = bpy.data.actions.new(name="Motion")

    ### Remove old curves while preserving the start values
    curve = owner.animation_data.action.fcurves.find(data_path="delta_location", index=0)
    if curve != None:
        if len(curve.keyframe_points) > 0:
            curveP = curve.keyframe_points[0]  # start value: 0 or end value: -1
            frame, value = curveP.co
            owner.animation_data.action.fcurves.remove(curve)  # Delete curve
    curve = owner.animation_data.action.fcurves.find(data_path="delta_location", index=1)
    if curve != None:
        if len(curve.keyframe_points) > 0:
            curveP = curve.keyframe_points[0]  # start value: 0 or end value: -1
            frame, value = curveP.co
            owner.animation_data.action.fcurves.remove(curve)  # Delete curve
    curve = owner.animation_data.action.fcurves.find(data_path="delta_location", index=2)
    if curve != None:
        if len(curve.keyframe_points) > 0:
            curveP = curve.keyframe_points[0]  # start value: 0 or end value: -1
            frame, value = curveP.co
            owner.animation_data.action.fcurves.remove(curve)  # Delete curve

    ### Create new curves
    if locX != -1:
        try: curveLocX = owner.animation_data.action.fcurves.new(data_path="delta_location", index=0)
        except: curveLocX = owner.animation_data.action.fcurves.find(data_path="delta_location", index=0)
        curveLocX.keyframe_points.add(frameCount)
    if locY != -1:
        try: curveLocY = owner.animation_data.action.fcurves.new(data_path="delta_location", index=1)
        except: curveLocY = owner.animation_data.action.fcurves.find(data_path="delta_location", index=1)
        curveLocY.keyframe_points.add(frameCount)
    if locZ != -1:
        try: curveLocZ = owner.animation_data.action.fcurves.new(data_path="delta_location", index=2)
        except: curveLocZ = owner.animation_data.action.fcurves.find(data_path="delta_location", index=2)
        curveLocZ.keyframe_points.add(frameCount)
   
    print("Animated frames:", frameCount)

    if len(linesItems) == 0:
        print("Nothing done.")
        return
    
    # Check if file has custom timings
    if timS != -1:
        # Sort array lines by time (in case they are not in order)
        linesItems = sorted(linesItems, key=itemgetter(timS))
    # Otherwise use one line per frame
    else:   
        scene.frame_end = scene.frame_start +frameCount-1
        frame = scene.frame_start

    # If no timeStep scale is given then calculate custom timeStep scaling from time steps in file (second line minus first line)
    if not timeStep and timS != -1: timeS = linesItems[1][timS] -linesItems[0][timS]
    else: timeS = timeStep
        
    if logMode == 1:
        ox = linesItems[0][locX]; oy = linesItems[0][locY]; oz = linesItems[0][locZ]
    elif logMode == 2:
        x = linesItems[0][locX] *timeS; y = linesItems[0][locY] *timeS; z = linesItems[0][locZ] *timeS
    elif logMode == 3:
        x = 0; y = 0; z = 0
        vx = 0; vy = 0; vz = 0
    lIdx = 0
    lCnt = len(linesItems)
    pIdx = 0
    while lIdx < lCnt:
        lineItems = linesItems[lIdx]

        qError = 0
        try: val_timS = lineItems[timS]
        except: qError = 1
        try: val_locX = lineItems[locX]
        except: qError = 1
        try: val_locY = lineItems[locY]
        except: qError = 1
        try: val_locZ = lineItems[locZ]
        except: qError = 1

        if qError:
            print("Error: Unexpected missing data in line:", lIdx)

        else:
            if timS != -1:
                frame = val_timS *bpy.context.scene.render.fps
                # If no timeStep scale is given then calculate custom timeStep scaling from time steps in file (current line minus last line)
                if not timeStep and lIdx < lCnt-1: timeS = linesItems[lIdx][timS] -linesItems[lIdx+1][timS]

            if logMode == 0:
                x = val_locX; y = val_locY; z = val_locZ
            elif logMode == 1:
                x = val_locX -ox; y = val_locY -oy; z = val_locZ -oz
            elif logMode == 2:
                x += val_locX *timeS; y += val_locY *timeS; z += val_locZ *timeS
            elif logMode == 3:
                vx += val_locX *timeS**2; vy += val_locY *timeS**2; vz += val_locZ *timeS**2
                x += vx; y += vy ; z += vz

            if locX != -1:
                curvePoint = curveLocX.keyframe_points[pIdx]; curvePoint.co = frame, x
                curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co; curvePoint.handle_left_type = 'AUTO_CLAMPED'; curvePoint.handle_right_type = 'AUTO_CLAMPED'
            if locY != -1:
                curvePoint = curveLocY.keyframe_points[pIdx]; curvePoint.co = frame, y
                curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co; curvePoint.handle_left_type = 'AUTO_CLAMPED'; curvePoint.handle_right_type = 'AUTO_CLAMPED'
            if locZ != -1:
                curvePoint = curveLocZ.keyframe_points[pIdx]; curvePoint.co = frame, z
                curvePoint.handle_left = curvePoint.co; curvePoint.handle_right = curvePoint.co; curvePoint.handle_left_type = 'AUTO_CLAMPED'; curvePoint.handle_right_type = 'AUTO_CLAMPED'

        lIdx += 1
        pIdx += 1
        if timS == -1: frame += 1
    
    print("Motion import done.")
    return

################################################################################   

def readData(filename):
    
    ### Read raw data into array as numeric items
    
    ### Vars
    skipLines = 0        # Skip that many lines at start
    separators = ['\t', ';', ',', ' '] # Column separators chars or strings ('\t' ';' ',')
    commentChars = ['/', '#']          # Chars that indicate comment lines to be skipped

    ###

    print("\nStarting import of motion data from external file...")

    try: f = open(filename, "rb")
    except:
        print("Error: Could not open file.")
        return
    
    qError = 0
    linesItems = []
    i = -1
    for line in f.readlines():
        i += 1
        if i < skipLines: continue
        line = line.decode()    # Decode the bytes into unicode (str)
        # Check if comment line to skip
        q = 0
        for chr in commentChars:
            if line[0] == chr: q = 1
        if q: continue
        # Remove chains of whitespaces and tabulators
        line = " ".join(line.split())
        # Split line into items
        for separator in separators:
            line = line.replace(separator, ';')
        lineSplits = line.split(';')
        items = []
        for item in lineSplits:
            if len(item) > 0:
                try: value = float(item)
                except:
                    print("Error: Value could not be converted:", item)
                    qError = 1
                    break
                else: items.append(value)
        linesItems.append(items)
        if qError: break

    f.close()
 
    if len(linesItems) >= 1: print("Last row(s) of values:")
    if len(linesItems) >= 2: print(linesItems[-2])
    if len(linesItems) >= 1: print(linesItems[-1])
    print("(If corrupted file structure might be wrong.)")
    if qError:
        print("Error: Inconsistency in file detected, some data might not be imported!")
        linesItems = linesItems[:-1]  # Remove last erroneous line
    
    return linesItems

################################################################################   
################################################################################   

from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ExportHelper

class MotionImporter(bpy.types.Operator):
    """Load Motion data"""
    bl_idname = "import_scene.motion"
    bl_label = "Import Motion Data (.csv)"
    bl_options = {'UNDO'}

    filepath = StringProperty(
            subtype='FILE_PATH',
            )
    filter_glob = StringProperty(default="*.csv", options={'HIDDEN'})

    def execute(self, context):
        importData(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}

################################################################################   

def menu_import(self, context):
    self.layout.operator(MotionImporter.bl_idname, text="Motion Data (.csv)")
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_import)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_import)

################################################################################   

if __name__ == "__main__":
    register()