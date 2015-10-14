##################################################
# Bullet Constraints Builder v1.4 by Kai Kostack #
##################################################

### Vars for constraint distribution
searchDistance = 0.5            # 0.15        | Search distance to neighbor geometry
constraintCountLimit = 1000       # 100       | Maximum count of constraints per object (0 = disabled)

### Vars for constraint settings
realWorldBreakingThresholdCompressive = 60  # 60      | Real world material compressive breaking threshold in N/mm^2
realWorldBreakingThresholdTensile     = 10  # 20      | Real world material tensile breaking threshold in N/mm^2
constraintUseBreaking = 1                   # 1       | Enables breaking
constraintType = 'FIXED'                    # 'FIXED' | Available: FIXED, POINT, HINGE, SLIDER, PISTON, GENERIC, GENERIC_SPRING, MOTOR
pillarGroup = "Pillars"                     #         | Name of group which contains only pillars (optional, overrides autodetection)  
pillarGroupConstraintTypeTop = 'FIXED'      # 'FIXED' | Available: FIXED, POINT, HINGE, SLIDER, PISTON, GENERIC, GENERIC_SPRING, MOTOR
pillarGroupConstraintTypeBottom = 'FIXED'   # 'FIXED' | Available: FIXED, POINT, HINGE, SLIDER, PISTON, GENERIC, GENERIC_SPRING, MOTOR

### Vars for volume calculation
materialPreset = 'Concrete'      # 'Concrete' | See Blender rigid body tools for a list of available presets
materialDensity = 0              # 0          | Custom density value (kg/m^3) to use instead of material preset (0 = disabled)
    
##################################################  

import bpy, sys, mathutils, time
from mathutils import Vector

##################################################  

def calculateThreshold(obj, objConst):
    """"""
    ### Autodetect if pillar or girder and calculate breaking threshold from cross area
    ### In case of a pillar use rather compressive threshold and in case of a girder the tensile one
    try: grpPillarGroup = bpy.data.groups[pillarGroup]
    except: grpPillarGroup = None
    dim = obj.dimensions
    # If X axis is the greatest (Girder detected)
    if dim.x > dim.y and dim.x > dim.z:    
        crossArea = dim.y *dim.z
        breakingThreshold = crossArea *1000000 *realWorldBreakingThresholdTensile
    # If Y axis is the greatest (Girder detected)
    elif dim.y > dim.x and dim.y > dim.z:
        crossArea = dim.x *dim.z
        breakingThreshold = crossArea *1000000 *realWorldBreakingThresholdTensile
    # If Z axis is the greatest (Pillar detected) also check if there is an extra group for pillars
    else:
        crossArea = dim.x *dim.y
        breakingThreshold = crossArea *1000000 *realWorldBreakingThresholdCompressive
    ### Now check if there is an extra group for pillars and deal with special cases
    qPillar = 0
    if grpPillarGroup and obj.name in bpy.data.groups[pillarGroup].objects:
        qPillar = 1
    elif (dim.z > dim.x and dim.z > dim.y):
        qPillar = 2
        # If the pillar is less then 1.5x as high as its width then it's considered to be no pillar
        if dim.z < dim.x *1.5 or dim.z < dim.y *1.5: qPillar = 3
    if qPillar:
        if qPillar == 1: # group pillar
            if objConst.location.z > obj.location.z: objConst.rigid_body_constraint.type = pillarGroupConstraintTypeTop
            else: objConst.rigid_body_constraint.type = pillarGroupConstraintTypeBottom
            elementType = 1
        elif qPillar == 2: # autodetected pillar
            elementType = 1
        elif qPillar == 3: # no pillar
            elementType = 2
    else: elementType = 2
        
    return breakingThreshold, elementType
    
#######################

def setConstraintSettings(objConst, empties):
    """"""
    ### Constraints settings
    objConst.rigid_body_constraint.use_breaking = constraintUseBreaking
    objConst.rigid_body_constraint.type = constraintType
    
    ### Calculate constraint threshold from real world thresholds for compressive or tensile force limits per mm^2
    obj1 = objConst.rigid_body_constraint.object1
    obj2 = objConst.rigid_body_constraint.object2
    
    if obj1 == None or obj2 == None: return obj1, obj2
    
    breakingThreshold1, elementType1 = calculateThreshold(obj1, objConst)
    breakingThreshold2, elementType2 = calculateThreshold(obj2, objConst)
    
    # Store element type as object property (1 = pillar, 2 = other, girder, slab, wall etc.)
    obj1['elemType'] = elementType1
    obj2['elemType'] = elementType2
    # Store breaking threshold sum and also take simulation steps into account (Threshold = F / Steps)
    obj1['brkThreshSum'] = breakingThreshold1 /bpy.context.scene.rigidbody_world.steps_per_second
    obj2['brkThreshSum'] = breakingThreshold2 /bpy.context.scene.rigidbody_world.steps_per_second
    
    # Flag breaking threshold for later balancing
    objConst.rigid_body_constraint.breaking_threshold = 999999999
    
    # Add to Bullet group in case someone removed it in the mean time
    try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst)
    except: pass

    return obj1, obj2
   
#######################   
   
def balanceThreshold(obj, objConsts):
    """"""
    ### Balance breaking threshold by splitting it according to shared connection space (based on cross section area)   
    if obj['elemType'] == 2:  # Girder, slab, wall etc.
        breakingThreshold = obj['brkThreshSum'] #/len(objConsts)
    elif obj['elemType'] == 1:  # Pillar
        breakingThreshold = obj['brkThreshSum'] #/len(objConsts) ### Debug-Test
    
    ### Now we got the final breaking threshold
    for objConst in objConsts:
        breakingThresholdItem = objConst.rigid_body_constraint.breaking_threshold
        # Overwrite threshold only if weaker than the already set one
        if breakingThreshold < breakingThresholdItem:
            objConst.rigid_body_constraint.breaking_threshold = breakingThreshold
        
#######################    
    
def run():
    """"""
    bpy.context.tool_settings.mesh_select_mode = True, False, False
    scene = bpy.context.scene
    pi = 3.1415927
    
    time_start = time.time()
    
    print("\nStarting...")
        
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Remove instancing from objects
    bpy.ops.object.make_single_user(object=True, obdata=True, material=False, texture=False, animation=False)

    ### Create object lists of selected objects
    print("Gathering objects...")
    objs = []
    empties = []
    for obj in bpy.data.objects:
        if obj.select and not obj.hide and obj.is_visible(scene):
            if obj.type == 'MESH':
                sys.stdout.write('\r' +"%s      " %obj.name)
                objs.append(obj)
            elif obj.type == 'EMPTY':
                if obj.rigid_body_constraint != None:
                    sys.stdout.write('\r' +"%s      " %obj.name)
                    empties.append(obj)
        
            
    ### If no constraint empties are detected and instead only meshes then start building new ones
    if len(objs) > 0:
        print("\nStarting building process...")
        
        # Create or reset connection count per object property
        for obj in objs:
            obj['conCount'] = 0
                       
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
        
        print(' - Time: %0.2f s' %(time.time()-time_start_building))

            
    ### If constraint emptys are detected then update constraint settings
    if len(empties) > 0:
        print("\nUpdating %d selected constraints..." %len(empties))
        
        ### Create element list
        objs = []
        for objConst in empties:
            obj1 = objConst.rigid_body_constraint.object1
            obj2 = objConst.rigid_body_constraint.object2
            if obj1 not in objs: objs.append(obj1)
            if obj2 not in objs: objs.append(obj2)
            
        ### Set constraint settings and create connected constraints list per element
        objsConsts = []
        for obj in objs:
            objsConsts.append([])
        count = 0
        for objConst in empties:
            sys.stdout.write('\r' +"%d" %count)
            
            ###### Own function
            obj1, obj2 = setConstraintSettings(objConst, empties)
            
            objsConsts[objs.index(obj1)].append(objConst)
            objsConsts[objs.index(obj2)].append(objConst)
            count += 1
        
        ### Balance breaking thresholds by splitting them according to shared connection space (based on cross section area)   
        print("\nBalancing breaking thresholds for %d objects..." %len(objs))
        count = 0
        for obj in objs:
            if obj != None:
                sys.stdout.write('\r' +"%d" %count)
            
                objConsts = objsConsts[objs.index(obj)]
                
                ###### Own function
                balanceThreshold(obj, objConsts)
            
                count += 1
        
        ### Calculate a mass for all mesh objects
        print("\nCalculating masses from preset material...")
        for obj in objs:
            if obj != None:
                if obj.rigid_body != None:
                    obj.select = 1
        if not materialDensity: bpy.ops.rigidbody.mass_calculate(material=materialPreset)
        else: bpy.ops.rigidbody.mass_calculate(material=materialPreset, density=materialDensity)
        
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')
        
        # Select all new constraint empties
        for obj in empties: obj.select = 1
        
        print('\nConstraints:', len(empties), '- Time total: %0.2f s' %(time.time()-time_start))
        print('Done.')       

            
    else:
        print('\nNeither mesh objects to connect nor constraint empties for updating selected.')       
        print('Nothing done.')       



if __name__ == "__main__":
    run()