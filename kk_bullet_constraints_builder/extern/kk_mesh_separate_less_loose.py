###########################################
# Separate Less Loose v1.1 by Kai Kostack #
###########################################
# Separates all connected loose parts in a specific random radius into new objects.
# (Makes larger pieces then regular separate loose.)

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

### Vars
searchMode = 4          # 1 = Completely randomized search but keep islands intact, works also on point clouds
                        # 2 = Improved island search using boundary boxes (faces only)
                        # 3 = Face based completely randomized search ignoring mesh connections to cut through it, use this to split geographic surfaces
                        # 4 = Face based halving down to searchSize
searchSize = .5         # Base radius or tolerance for search for neighbours
randomSizeFactor = 0    # How much size randomization should be used [0..1] 
qSilentVerbose = 0      # Reduces text output to a minimum

################################################################################

import bpy, sys, random, time
from mathutils import *

################################################################################

def run(source=None, parameters=None):
   
    ### Custom BCB parameter handling
    if source == 'BCB':
        global searchSize; searchSize = parameters[0]
        global searchMode; searchMode = 4
        global qSilentVerbose; qSilentVerbose = 1

    ###

    print("\nStarting splitting process...")
    
    time_start = time.time()
    scene = bpy.context.scene

    objs = allSelectedObjects(scene)

    # Deselect all objects.
    bpy.ops.object.select_all(action='DESELECT')
    
    objsNew = []
    for obj in objs:
        if not qSilentVerbose: print("Object: " +obj.name)
       
        if searchMode == 1: searchAndSeparateMode1(scene, obj)
        elif searchMode == 2: searchAndSeparateMode2(scene, obj)
        elif searchMode == 3: searchAndSeparateMode3(scene, obj)
        elif searchMode == 4: objsNew.extend(searchAndSeparateMode4(scene, obj))
    print()

    # Optimization: Relink all objects back to scene
    for objN in objsNew:
        try: scene.objects.link(objN)
        except: pass

    # Select original objects again
    for obj in objs: obj.select = 1

    print('Original mesh objects split:', len(objs))
    print('Done. -- Time: %0.2f s' %(time.time() -time_start))

################################################################################

def updateObjList(scene, objs):
    
    ### Add new objects and selected objects to the object list and remove deleted ones
    objsNew = []
    for objTemp in scene.objects:
        if objTemp.select:
            if objTemp not in objs:
                if objTemp.type == 'MESH' and not objTemp.hide and objTemp.is_visible(scene):
                    objsNew.append(objTemp)
    objs.extend(objsNew)
    # Remove missing objects
#    for idx in reversed(range(len(objs))):
#        if objs[idx].name not in scene.objects:
#            del objs[idx]
    return objsNew

########################################

def searchAndSeparateMode4(scene, obj):
    """"""
    bpy.context.tool_settings.mesh_select_mode = False, False, True 
    
    obj.select = 1
    # Reset object origins
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    objs = [obj]
    lenObjsLast = 0
    lenObjs = lenObjsStart = len(objs)
    objsFin = set()
    k = 0
    while k < lenObjs:
        obj = objs[k]
        k += 1

        if not qSilentVerbose: sys.stdout.write('\r' +"%d / %d Objects: %s   " %(lenObjs,len(bpy.data.objects)-lenObjsStart,obj.name))
        else: sys.stdout.write('\r' +"%d " %(len(bpy.data.objects)-lenObjsStart))

        if k not in objsFin:
            try: scene.objects.link(obj)   # Optimization: Relink objects to scene so we can work with it
            except: pass
            bpy.context.scene.objects.active = obj
            me = obj.data
            
            ### Deselect all elements without entering edit mode
            for vert in me.vertices:
                if vert.select: vert.select = 0
            for edge in me.edges:
                if edge.select: edge.select = 0
            for face in me.polygons:
                if face.select: face.select = 0

            ### Find out length and largest axis for halving
            dims = obj.dimensions
            axis = [0, 1, 2]
            dims, axis = zip(*sorted(zip(dims, axis)))
            length = dims[2]
            axis = axis[2]

            size = len(me.polygons)
            if length >= searchSize and size > 1:
                
                # Select faces of one half of the object depending on axis
                selCnt = 0
                for i in range(size):
                    vert = me.polygons[i].center
                    if vert[axis] >= 0:
                        me.polygons[i].select = 1
                        selCnt += 1

                if selCnt > 0 and selCnt < size:  # Avoid empty object as result
                    # Enter edit mode              
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass # continue
                    # Separate selected geometry
                    bpy.ops.mesh.separate()
                    # Separate loose
                    try: bpy.ops.mesh.separate(type='LOOSE')
                    except: pass
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass # continue

                    # Reset object origins
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

                    scene.objects.unlink(obj)   # Optimization: Unlink objects from scene for speed optimization
            else:
                objsFin.add(k)
                scene.objects.unlink(obj)  # Optimization: Unlink objects from scene for speed optimization
                continue

            # Update objs list with new object
            objsNew = updateObjList(scene, objs)

            # Set new object to active
            obj = objs[-1]
            try: scene.objects.link(obj)   # Optimization: Relink objects to scene so we can work with it
            except: pass
            bpy.context.scene.objects.active = obj
            me = obj.data
            
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass # continue
            # Separate loose
            try: bpy.ops.mesh.separate(type='LOOSE')
            except: pass
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass # continue
            scene.objects.unlink(obj)   # Optimization: Unlink objects from scene for speed optimization
            
            # Update objs list with new objects
            objsNew = updateObjList(scene, objs)

            # Reset object origins
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

            # Optimization: Unlink objects from scene for speed optimization
            for objTemp in objsNew:
                scene.objects.unlink(objTemp)

            lenObjs = len(objs)

        if lenObjs != lenObjsLast:
            lenObjsLast = lenObjs
            k = 0
    if not qSilentVerbose: print()

    return objs
        
################################################################################

def searchAndSeparateMode3(scene, obj):
    """"""
    bpy.context.tool_settings.mesh_select_mode = False, False, True 
        
    bpy.context.scene.objects.active = obj
    me = obj.data
    
    # Enter edit mode              
    try: bpy.ops.object.mode_set(mode='EDIT')
    except: pass # continue
    # Deselect all elements
    try: bpy.ops.mesh.select_all(action='DESELECT')
    except: pass # continue
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT')
    except: pass # continue

    size = 0
    sizeF = len(me.polygons)
    while len(me.polygons) != size and len(me.polygons) > 0:
        
        limit = searchSize-(random.random()*randomSizeFactor*searchSize)
        
        size = len(me.polygons)
        i = random.randrange(0, size)
        
        # Compare face center agains all others
        for j in range(size):
            sys.stdout.write('\r' +"%d / %d Faces   " %(len(me.polygons),sizeF))
    
            vert = me.polygons[i].center
            vert2 = me.polygons[j].center
            q = 0
            if vert[0] < vert2[0]-limit or vert[0] > vert2[0]+limit: q = 1
            elif vert[1] < vert2[1]-limit or vert[1] > vert2[1]+limit: q = 1
            elif vert[2] < vert2[2]-limit or vert[2] > vert2[2]+limit: q = 1             
            if q == 0:
                me.polygons[j].select = 1
           
        # Enter edit mode              
        try: bpy.ops.object.mode_set(mode='EDIT')
        except: pass # continue
    
        # Separate selected geometry
        bpy.ops.mesh.separate()
        
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: pass # continue
    print()       

    # Delete empty object
    try: bpy.context.scene.objects.unlink(obj)
    except: pass

################################################################################

def searchAndSeparateMode2(scene, obj):
    """"""
    bpy.context.tool_settings.mesh_select_mode = True, False, False 
    
    bpy.context.scene.objects.active = obj
    me = obj.data
    
    # Enter edit mode              
    try: bpy.ops.object.mode_set(mode='EDIT')
    except: pass # continue
    # Deselect all elements
    bpy.ops.mesh.select_all(action='DESELECT')
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT')
    except: pass # continue
    
    sizeF2 = len(me.polygons)
    while len(me.polygons) > 0:
        
        sizeF = len(me.polygons)
        f = 0
        #f = random.randrange(0, sizeF-1)
        me.polygons[f].select = 1
        
        faceFinishedL = []
        for face in me.polygons:
            faceFinishedL.append(0)
        
        selectionCount = 0
        qFinished = 0
        while qFinished == 0:
            
            for f in range(len(me.polygons)):
                if me.polygons[f].select and not faceFinishedL[f]:
                    sys.stdout.write('\r' +"%d / %d Faces - Index: %d    " %(sizeF,sizeF2,f))
                        
                    vertices = []
                    for vert in me.polygons[f].vertices:
                        vertices.append(me.vertices[vert.numerator])
                    
                    #bbCenter = me.polygons[f].center
                    
                    # Calculate boundary box corners and center
                    bbMin = vertices[0].co.copy()
                    bbMax = vertices[0].co.copy()
                    for vert in vertices:
                        loc = vert.co.copy()
                        if bbMax[0] < loc[0]: bbMax[0] = loc[0]
                        if bbMin[0] > loc[0]: bbMin[0] = loc[0]
                        if bbMax[1] < loc[1]: bbMax[1] = loc[1]
                        if bbMin[1] > loc[1]: bbMin[1] = loc[1]
                        if bbMax[2] < loc[2]: bbMax[2] = loc[2]
                        if bbMin[2] > loc[2]: bbMin[2] = loc[2]
                    bbCenter = (bbMin +bbMax) /2
                        
                    # Calculate limit including random factors
                    if randomSizeFactor > 0:
                        limit = searchSize-(random.random()*randomSizeFactor*searchSize)
                    else: limit = searchSize
                    
                    # Extend boundary box by limits
                    bbMin -= Vector((limit,limit,limit))
                    bbMax += Vector((limit,limit,limit))
                    
                    # Compare boundary box against all vertices, all inside should be selected
                    for vert in me.vertices:
                        if vert.co.x > bbMin.x and vert.co.x < bbMax.x and \
                           vert.co.y > bbMin.y and vert.co.y < bbMax.y and \
                           vert.co.z > bbMin.z and vert.co.z < bbMax.z:
                            vert.select = 1
                       
                    # Enter edit mode              
                    try: bpy.ops.object.mode_set(mode='EDIT')
                    except: pass # continue
                    # Select more until no more connected vertices are found
                    bpy.ops.mesh.select_linked()
                    # Leave edit mode
                    try: bpy.ops.object.mode_set(mode='OBJECT')
                    except: pass # continue
            
                    faceFinishedL[f] = 1
                        
            selectionCountOld = selectionCount
            selectionCount = 0
            for face in me.polygons:
                if face.select: selectionCount += 1
            #print(selectionCount)
            if selectionCountOld == selectionCount:
                qFinished = 1
    
        # Enter edit mode              
        try: bpy.ops.object.mode_set(mode='EDIT')
        except: pass # continue
        # Separate selected geometry
        bpy.ops.mesh.separate()
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: pass # continue
    print()
            
    # delete empty object
    try: bpy.context.scene.objects.unlink(obj)
    except: pass
                    
################################################################################

def searchAndSeparateMode1(scene, obj):
    """"""
    bpy.context.tool_settings.mesh_select_mode = True, False, False 
    
    bpy.context.scene.objects.active = obj
    me = obj.data
    
    # Enter edit mode              
    try: bpy.ops.object.mode_set(mode='EDIT')
    except: pass # continue
    # Deselect all elements
    try: bpy.ops.mesh.select_all(action='DESELECT')
    except: pass # continue
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT')
    except: pass # continue

    size = 0
    sizeF = len(me.vertices)
    while len(me.vertices) != size and len(me.vertices) > 0:
        
        limit = searchSize-(random.random()*randomSizeFactor*searchSize)
        
        size = len(me.vertices)
        i = random.randrange(0, size)
        
        # Compare i vertex agains all other vertices to find connections
        for j in range(size):
            sys.stdout.write('\r' +"%d / %d Verts   " %(len(me.vertices),sizeF))
           
            # Use exact value (faster)
            if searchSize == 0:
                if me.vertices[i].co == me.vertices[j].co: me.vertices[j].select = 1

            # Use limit (slower)
            else:
                vert = me.vertices[i]
                vert2 = me.vertices[j]
                q = 0
                if vert.co.x < vert2.co.x-limit or vert.co.x > vert2.co.x+limit: q = 1
                elif vert.co.y < vert2.co.y-limit or vert.co.y > vert2.co.y+limit: q = 1
                elif vert.co.z < vert2.co.z-limit or vert.co.z > vert2.co.z+limit: q = 1             
                if q == 0:
                    vert2.select = 1
     
        # Enter edit mode              
        try: bpy.ops.object.mode_set(mode='EDIT')
        except: pass # continue
    
        bpy.ops.mesh.select_linked()
            
        # Remove doubles
        #bpy.ops.mesh.remove_doubles(limit=0.0001)
        
        # Separate selected geometry
        bpy.ops.mesh.separate()
        
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: pass # continue
    print()       

    # Delete empty object
    try: bpy.context.scene.objects.unlink(obj)
    except: pass
    
################################################################################

def allSelectedObjects(scene):
    
    # create object list of selected objects
    objs = []
    for obj in bpy.data.objects:
        if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(bpy.context.scene):
            objs.append(obj)
            scene.objects.unlink(obj)   # Optimization: Unlink objects from scene for speed optimization
    return objs
    
################################################################################

if __name__ == "__main__":
    run()  