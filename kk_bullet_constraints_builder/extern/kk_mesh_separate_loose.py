################################################
# Efficient Separate Loose v1.5 by Kai Kostack #
################################################

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
  
import bpy, sys, time

def run():
    """"""
    ### Vars
    elementBase = 0        # What kind of elements to be used: 0 = vertices; 1 = polygons
    separationMode = 1     # Algorithm number to be used:
                           # 0 = No performance optimization: Selected first vertex, select linked and separate loose is performed.
                           # 1 = Halving based on element order (together with element sort operator this is more flexible than mode 2)
                           # 2 = Halving based on axis based space (Z)
    qUVislands = 0         # If enabled UV islands will be used instead of mesh islands (overrides elementBase and separationMode)

    qSilentVerbose = 1     # Reduces text output to a minimum
    
    ### Fixes
    if qUVislands: elementBase = 1  # This is required because a vertex can share multiple UV islands so we still would get multiple UV islands per separated mesh
    
    ###
    
    print("\nStarting separate loose...")
    time_start = time.time()

    scene = bpy.context.scene
    if elementBase == 0: bpy.context.tool_settings.mesh_select_mode = True, False, False
    elif elementBase == 1: bpy.context.tool_settings.mesh_select_mode = False, False, True
 
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Create object list of selected objects
    # (Because we add more objects with following function we need a separate list.)
    objs = []
    for obj in scene.objects:
        if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(scene):
            objs.append(obj)
            scene.objects.unlink(obj)   # Unlinking optimization: Unlink objects from scene for speed optimization
    
    # Main separation loop
    objsNew = []    # Unlinking optimization
    count = len(objs)
    while len(objs) > 0:
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        obj = objs[0]
        scene.objects.link(obj)   # Unlinking optimization: Relink objects to scene so we can work with it
        bpy.context.scene.objects.active = obj
        me = obj.data
        vertLen = len(me.vertices)
        polyLen = len(me.polygons)
            
        # Only start halving when object has more than this number of vertices
        # Some benchmarks showed that it's optimal to keep it low as it's more effective but not less than 10
        if vertLen > 10: qObjectIsLargeEnough = 1
        else: qObjectIsLargeEnough = 0
   
        if qObjectIsLargeEnough:
            if not qSilentVerbose:
                print('Objects to split:', len(objs))
                print('Splitting object:', obj.name)
                print('Vertices:', vertLen, '| polygons:', polyLen)
            else: sys.stdout.write('\r' +"%d " %len(objs))

            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass # continue
            # Deselect all elements
            bpy.ops.mesh.select_all(action='DESELECT')
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass # continue

            if separationMode == 0 or qUVislands:
                # Select first element only
                if elementBase == 0: me.vertices[0].select = 1
                elif elementBase == 1: me.polygons[0].select = 1
                
            elif separationMode == 1:
                # Select half the geometry (this only works when elements are deselected beforehand in edit mode,
                # because zeroing selection doesn't work for some reason)
                if elementBase == 0:
                    for i in range(int(vertLen/2)): me.vertices[i].select = 1
                elif elementBase == 1: 
                    for i in range(int(polyLen/2)): me.polygons[i].select = 1
    
            elif separationMode == 2:  # old half selection code based on location and axis
                # Calculate boundary box corners and center
                verts = me.vertices
                bbMin = verts[0].co.copy()
                bbMax = verts[0].co.copy()
                for vert in verts:
                    loc = vert.co.copy()
                    if bbMax[0] < loc[0]: bbMax[0] = loc[0]
                    if bbMin[0] > loc[0]: bbMin[0] = loc[0]
                    if bbMax[1] < loc[1]: bbMax[1] = loc[1]
                    if bbMin[1] > loc[1]: bbMin[1] = loc[1]
                    if bbMax[2] < loc[2]: bbMax[2] = loc[2]
                    if bbMin[2] > loc[2]: bbMin[2] = loc[2]
                bbCenter = (bbMin +bbMax) /2

                # Select half the geometry (this only works when elements are deselected beforehand in edit mode,
                # because zeroing selection doesn't work for some reason)
                if elementBase == 0:
                    for vert in me.vertices:
                        if vert.co.z > bbCenter.z:  # I chose Z axis arbitrarily, can also be X or Y
                            vert.select = 1
                elif elementBase == 1: 
                    for poly in me.polygons:
                        if poly.center.co.z > bbCenter.z:  # I chose Z axis arbitrarily, can also be X or Y
                            poly.select = 1
                
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass # continue
            # Select linked to make sure no undesired mesh splitting occurs
            if qUVislands: bpy.ops.mesh.select_linked(delimit={'UV'})
            else: bpy.ops.mesh.select_linked()
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass # continue
            
            # Count selected verts to make sure old object won't be empty
            sum = 0
            for vert in me.vertices:
                if vert.select: sum += 1
    
        # Enter edit mode              
        try: bpy.ops.object.mode_set(mode='EDIT')
        except: pass # continue
        
        if qUVislands:
            # Separate selection
            try: bpy.ops.mesh.separate(type='SELECTED')
            except: objs.remove(obj)
        else:
            # If no difference can be found try with regular separate loose
            if not qObjectIsLargeEnough or sum == 0 or sum == len(me.vertices):
                # Select all geometry
                bpy.ops.mesh.select_all(action='SELECT')
                # Separate loose
                try: bpy.ops.mesh.separate(type='LOOSE')
                except: pass
                objs.remove(obj)  # Separate loose operator will always finish the object so it can be removed from list
            else:
                # Separate selection
                try: bpy.ops.mesh.separate(type='SELECTED')
                except: objs.remove(obj)
                else:
                    # Append new objects to objs list
                    for objN in scene.objects:
                        if objN.select and objN.type == 'MESH' and not objN.hide and objN.is_visible(scene):
                            objs.append(objN)
        
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: pass # continue
        
        # Unlinking optimization: Append new objects to objsNew list so we can relink them back to scene after we finished, until then unlink them as well
        for objN in scene.objects:
            if objN.select and objN.type == 'MESH' and not objN.hide and objN.is_visible(scene):
                scene.objects.unlink(objN)   # Temporarily unlink again
                if objN not in objsNew: objsNew.append(objN)
        
        if not qSilentVerbose: print('Current database object count:', len(bpy.data.objects))

    if qSilentVerbose: print()
                                                 
    # Unlinking optimization: Relink all objects back to scene
    for objN in objsNew:
        scene.objects.link(objN)
        
    print('Original mesh objects split:', count)
    print('Done. -- Time: %0.2f s' %(time.time()-time_start))
                 
                   
if __name__ == "__main__":
    run()