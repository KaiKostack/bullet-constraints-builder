################################################
# Efficient Separate Loose v1.4 by Kai Kostack #
################################################
    
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
    
    ### Fixes
    if qUVislands: elementBase = 1  # This is required because a vertex can share multiple UV islands so we still would get multiple UV islands per separated mesh
    
    ###
    
    print("\nStarting...")
    time_start = time.time()

    scene = bpy.context.scene
    if elementBase == 0: bpy.context.tool_settings.mesh_select_mode = True, False, False
    elif elementBase == 1: bpy.context.tool_settings.mesh_select_mode = False, False, True
 
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # create object list of selected objects
    # (because we add more objects with following function we need a separate list)
    objs = []
    for obj in scene.objects:
        if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(scene):
            objs.append(obj)
            scene.objects.unlink(obj)   # Unlinking optimization: Unlink objects from scene for speed optimization
    
    # main separation loop
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
            
        # only start halving when object has more than this number of vertices
        # some benchmarks showed that it's optimal to keep it low as it's more effective but not less than 10
        if vertLen > 10: qObjectIsLargeEnough = 1
        else: qObjectIsLargeEnough = 0
   
        if qObjectIsLargeEnough:
            print('Objects to split:', len(objs))
            print('Splitting Object:', obj.name)
            print('Vertices:', vertLen, '| polygons:', polyLen)

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
                # calculate boundary box corners and center
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
            # select linked to make sure no undesired mesh splitting occurs
            if qUVislands: bpy.ops.mesh.select_linked(delimit={'UV'})
            else: bpy.ops.mesh.select_linked()
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass # continue
            
            # count selected verts to make sure old object won't be empty
            sum = 0
            for vert in me.vertices:
                if vert.select: sum += 1
    
        # Enter edit mode              
        try: bpy.ops.object.mode_set(mode='EDIT')
        except: pass # continue
        
        if qUVislands:
            # separate selection
            try: bpy.ops.mesh.separate(type='SELECTED')
            except: objs.remove(obj)
        else:
            # if no difference can be found try with regular separate loose
            if not qObjectIsLargeEnough or sum == 0 or sum == len(me.vertices):
                # select all geometry
                bpy.ops.mesh.select_all(action='SELECT')
                # separate loose
                try: bpy.ops.mesh.separate(type='LOOSE')
                except: pass
                objs.remove(obj)  # separate loose operator will always finish the object so it can be removed from list
            else:
                # separate selection
                try: bpy.ops.mesh.separate(type='SELECTED')
                except: objs.remove(obj)
                else:
                    # append new objects to objs list
                    for objN in scene.objects:
                        if objN.select and objN.type == 'MESH' and not objN.hide:
                            objs.append(objN)
        
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT')
        except: pass # continue
        
        # Unlinking optimization: Append new objects to objsNew list so we can relink them back to scene after we finished, until then unlink them as well
        for objN in scene.objects:
            if objN.select and objN.type == 'MESH' and not objN.hide:
                scene.objects.unlink(objN)   # Temporarily unlink again
                if objN not in objsNew: objsNew.append(objN)
        
        print('Current database object count:', len(bpy.data.objects))
                                                 
    # Unlinking optimization: Relink all objects back to scene
    for objN in objsNew:
        scene.objects.link(objN)
        
    print('-- Time total: %0.2f s\n' %(time.time()-time_start))
    print('Original mesh objects split:', count)
    print('Done.')
                 
                   
if __name__ == "__main__":
    run()