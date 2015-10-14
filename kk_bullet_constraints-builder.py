##################################################
# Bullet Constraints Builder v1.3 by Kai Kostack #
##################################################

### Vars for constraint distribution
searchDistance = 0.5            # 0.15    | Search distance to neighbor geometry
constraintCountLimit = 1000       # 0       | Maximum count of constraints per object (0 = disabled)

### Vars for constraint settings
realWorldBreakingThresholdCompressive = 60  # 60      | Real world material compressive breaking threshold in N/mm^2
realWorldBreakingThresholdTensile     = 20  # 20      | Real world material tensile breaking threshold in N/mm^2
constraintType = 'FIXED'                    # 'FIXED' | Available: FIXED, POINT, HINGE, SLIDER, PISTON, GENERIC, GENERIC_SPRING, MOTOR
constraintUseBreaking = 1                   # 1       | Enables breaking

### Vars for volume calculation
materialPreset = 'Concrete'      # 'Concrete' | See Blender rigid body tools for a list of available presets
materialDensity = 0              # 0          | Custom density value (kg/m^3) to use instead of material preset (0 = disabled)
    
##################################################  

import bpy, sys, mathutils, time
from mathutils import Vector

##################################################  

def setConstraintSettings(objConst, empties):
    """"""
    ### Calculate constraint threshold from real world thresholds for compressive or tensile force limits per mm^2
    ### While calculating the area of the smallest possible cross section also interpret if it's a column or a girder
    ### In case of a column use rather compressive threshold and in case of a girder the tensile one
    dim1 = objConst.rigid_body_constraint.object1.dimensions
    connectionCount = objConst.rigid_body_constraint.object1['conCount'] +objConst.rigid_body_constraint.object2['conCount']
    if dim1.x > dim1.y and dim1.x > dim1.z:    # If X axis is the greatest (Girder)
        crossArea1 = dim1.y *dim1.z
        breakingThreshold1 = crossArea1 *1000000 *realWorldBreakingThresholdTensile
        # Divide threshold by connection count to neighbor constraints to respect shared connection space
        if connectionCount > 1: breakingThreshold1 /= connectionCount
    elif dim1.y > dim1.x and dim1.y > dim1.z:  # If Y axis is the greatest (Girder)
        crossArea1 = dim1.x *dim1.z
        breakingThreshold1 = crossArea1 *1000000 *realWorldBreakingThresholdTensile
        # Divide threshold by connection count to neighbor constraints to respect shared connection space
        if connectionCount > 1: breakingThreshold1 /= connectionCount
    else:                                      # If Z axis is the greatest (Column)
        crossArea1 = dim1.x *dim1.y
        breakingThreshold1 = crossArea1 *1000000 *realWorldBreakingThresholdCompressive
        # For columns we don't divide by connection count
    ### Do the same for the second object
    dim2 = objConst.rigid_body_constraint.object2.dimensions
    if dim2.x > dim2.y and dim2.x > dim2.z:    # If X axis is the greatest (Girder)
        crossArea2 = dim2.y *dim2.z
        breakingThreshold2 = crossArea2 *1000000 *realWorldBreakingThresholdTensile
        # Divide threshold by connection count to neighbor constraints to respect shared connection space
        if connectionCount > 1: breakingThreshold2 /= connectionCount
    elif dim2.y > dim2.x and dim2.y > dim2.z:  # If Y axis is the greatest (Girder)
        crossArea2 = dim2.x *dim2.z
        breakingThreshold2 = crossArea2 *1000000 *realWorldBreakingThresholdTensile
        # Divide threshold by connection count to neighbor constraints to respect shared connection space
        if connectionCount > 1: breakingThreshold2 /= connectionCount
    else:                                      # If Z axis is the greatest (Column)
        crossArea2 = dim2.x *dim2.y
        breakingThreshold2 = crossArea2 *1000000 *realWorldBreakingThresholdCompressive
        # For columns we don't divide by connection count
    # Use the weaker threshold of both connected elements
    if breakingThreshold1 <= breakingThreshold2: breakingThreshold = breakingThreshold1
    else:                                        breakingThreshold = breakingThreshold2
    # Take also simulation steps into account (Threshold = F / Steps)
    objConst.rigid_body_constraint.breaking_threshold = breakingThreshold /bpy.context.scene.rigidbody_world.steps_per_second
    
    # Override calculation with a fixed threshold for everything
    #objConst.rigid_body_constraint.breaking_threshold = 300   # 30000     | Predefined breaking threshold

    ### Constraints settings
    objConst.rigid_body_constraint.type = constraintType
    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
    
    
def run():
    """"""
    bpy.context.tool_settings.mesh_select_mode = True, False, False
    scene = bpy.context.scene
    pi = 3.1415927
    
    time_start = time.time()
    
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Remove instancing from objects
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)

    ### Create object lists of selected objects
    objs = []
    empties = []
    for obj in bpy.data.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            if obj.type == 'MESH':
                objs.append(obj)
            elif obj.type == 'EMPTY':
                if obj.rigid_body_constraint != None:
                    empties.append(obj)
        
        
    ### If constraint emptys are detected then only update constraint settings
    if len(empties) > 0:
        print("\nOnly updating %d selected constraints..." %len(empties))
        
        count = 0
        for obj in empties:
            sys.stdout.write('\r' +"%d" %count)
            
            ###### Own function
            setConstraintSettings(obj, empties)
            count += 1
    
        ### Calculate a mass for all mesh objects
        print("\nUpdating masses from preset material...")
        for obj in objs:
            if obj.rigid_body != None:
                obj.select = 1
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        print('\nConstraints:', count, '- Time total: %0.2f s' %(time.time()-time_start))
        print('Done.')
       
        
    ### If no constraint empties are detected and instead only meshes then start building new ones
    elif len(objs) > 0:
        print("\nStarting building...")
        
        # Create or reset connection count per object property
        for obj in objs:
            obj['conCount'] = 0
            
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        ### Calculate a mass for all mesh objects
        print("\nCalculating masses from preset material...")
        for obj in objs:
            if obj.rigid_body != None:
                obj.select = 1
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
                        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        ### Build kd-tree for object locations
        kdObjs = mathutils.kdtree.KDTree(len(objs))
        for i, obj in enumerate(objs):
            kdObjs.insert(obj.location, i)
        kdObjs.balance()
        
        ### Build kd-trees for every object's vertices
        kdsMeComp = []
        for obj in objs:
            me = obj.data
            mat = obj.matrix_world
            
            kd = mathutils.kdtree.KDTree(len(me.vertices))
            for i, v in enumerate(me.vertices):
                loc = mat *v.co       # Multiply matrix by vertex to get global coordinates
                kd.insert(loc, i)
            kd.balance()
            kdsMeComp.append(kd)
                        
        ###### Prepare connection map
        print("Building connection map for %d objects..." %len(objs))
        time_start_connections = time.time()
    
        objsCons = []   # will store object indices and locations of the constraints to be created
        conPairs = []
        count = 0
        for k in range(len(objs)):
            sys.stdout.write('\r' +"%d" %k)
            
            qNextObj = 0
            obj = objs[k]
            mat = obj.matrix_world
            me = obj.data
            objsCons.append([])
                    
            ### Find closest objects via kd-tree
            co_find = obj.location
            aIndex = []#; aCo = []; aDist = [];
            if constraintCountLimit:
                for (co, index, dist) in kdObjs.find_n(co_find, constraintCountLimit +1):  # +1 because the first item will be removed
                    aIndex.append(index)#; aCo.append(co); aDist.append(dist)
            else:
                for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                    aIndex.append(index)#; aCo.append(co); aDist.append(dist)
            aIndex = aIndex[1:] # Remove first item because it's the same as k (zero distance)
            
            for m in range(len(me.vertices)):
                vert = me.vertices[m]
                co_find = mat *vert.co     # Multiply matrix by vertex to get global coordinates
                            
                # Loops for comparison object
                for j in range(len(aIndex)):
                    l = aIndex[j]
                    
                    if k != l:
                        # Use object specific kd-tree
                        kdMeComp = kdsMeComp[l]
                        
                        ### Find closest vertices via kd-tree
                        if len(kdMeComp.find_range(co_find, searchDistance)) > 0:   # If vert is within search range add connection to sublist
                            coComp = kdMeComp.find(co_find)[0]    # Find coordinates of the closest vertex
                            co = (co_find +coComp) /2             # Calculate center of both vertices
                            
                            ### create connection if not already existing
                            if (k, l) not in conPairs and (l, k) not in conPairs:
                                objsCons[-1:][0].append((l, co))
                                conPairs.append((k, l))
                                count += 1
                                if len(objsCons[-1:][0]) == constraintCountLimit:
                                    qNextObj = 1
                                    break
                if qNextObj: break             
        
        print(' - Time: %0.2f s' %(time.time()-time_start_connections))
           
                    
        ###### Main building part
        print("Building %d empties..." %count)
        time_start_building = time.time()
        
        ### Create first object
        objConst = bpy.data.objects.new('Constraint', None)
        scene.objects.link(objConst)
        objConst.empty_draw_type = 'SPHERE'
        objConst.empty_draw_size = searchDistance
        bpy.context.scene.objects.active = objConst
        bpy.ops.rigidbody.constraint_add()
        empties = [objConst]
        ### Duplicate them as long as we got the desired count   
        while len(empties) < count:
            sys.stdout.write("%d\n" %len(empties))
            
            # Deselect all objects
            bpy.ops.object.select_all(action='DESELECT')
            # Select empties already in list
            c = 0
            for obj in empties:
                if c < count -len(empties):
                    obj.select = 1
                    c += 1
                else: break
            # Duplicate them
            bpy.ops.object.duplicate(linked=False)
            # Add duplicates to list again
            for obj in bpy.data.objects:
                if obj.select and obj.is_visible(scene):
                    if obj.type == 'EMPTY':
                        empties.append(obj)
                        
        ### Add constraint settings to empties
        i = 0
        for k in range(len(objs)):
            cons = objsCons[k]
            
            for l in range(len(cons)):
                sys.stdout.write('\r' +"%d" %i)
                
                obj = objs[cons[l][0]]
                loc = cons[l][1]
               
                objConst = empties[i]
                objConst.location = loc
                #objConst.empty_draw_type = 'PLAIN_AXES'
                
                obj1 = objs[k]
                obj2 = obj
                
                objConst.rigid_body_constraint.object1 = obj1
                objConst.rigid_body_constraint.object2 = obj2
                
                obj1['conCount'] += 1
                obj2['conCount'] += 1
                
                i += 1
        print()
        
        ### If objects are set continue to calculate other constraint settings
        count = 0
        for obj in empties:
            sys.stdout.write('\r' +"%d" %count)
            
            ###### Own function
            setConstraintSettings(obj, empties)
            count += 1
        
        # Finished   
        print(' - Time: %0.2f s' %(time.time()-time_start_building))

        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select all new constraint empties
        for obj in empties: obj.select = 1
                                           
        print('\nConstraints:', count, '- Time total: %0.2f s' %(time.time()-time_start))
        print('Done.')
            
            
    else:
        print('\nNeither mesh objects to connect nor constraint empties for updating selected.')       
        print('Nothing done.')       


if __name__ == "__main__":
    run()