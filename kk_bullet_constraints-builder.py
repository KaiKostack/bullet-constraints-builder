##################################################
# Bullet Constraints Builder v1.5 by Kai Kostack #
##################################################

### Vars for constraint distribution
constraintCountLimit = 1000  # 150   | Maximum count of constraints per object (0 = disabled)
searchDistance = 0.9         # 0.10  | Search distance to neighbor geometry
clusterRadius = 0.9          # 0.40  | Radius for bundling close constraints into clusters (0 = clusters disabled)
ReqVertexPairs = 3           # 3     | How many vertex connections between an object pair are required to create an constraint
ReqVertexPairsToPillars = 2  # 2     | How many vertex connections between an object pair of whom one is a pillar are required to create an constraint
                             # This can help to ensure there is an actual surface on surface connection between both objects (for at least 3 verts you can expect a shared surface).

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
    try: grpPillarGroup = bpy.data.groups[pillarGroup]
    except: grpPillarGroup = None
    
    ### Find smallest cross section area
    dim = obj.dimensions
    if dim.x > dim.y and dim.x > dim.z:   crossArea = dim.y *dim.z
    elif dim.y > dim.x and dim.y > dim.z: crossArea = dim.x *dim.z
    else:                                 crossArea = dim.x *dim.y
         
    ### Check if pillar or girder and apply respective settings
    ### In case of a pillar use rather compressive threshold and in case of a girder the tensile one
    if grpPillarGroup and obj.name in bpy.data.groups[pillarGroup].objects:
        # Pillar
        elementType = 1
        # Convert real world breaking threshold to bullet breaking threshold
        breakingThreshold = crossArea *1000000 *realWorldBreakingThresholdCompressive
        # Set constraint typ for top or bottom connection
        if objConst.location.z > obj.location.z: objConst.rigid_body_constraint.type = pillarGroupConstraintTypeTop
        else: objConst.rigid_body_constraint.type = pillarGroupConstraintTypeBottom
    else:
        # Girder, slab, wall etc.
        elementType = 2
        # Convert real world breaking threshold to bullet breaking threshold
        breakingThreshold = crossArea *1000000 *realWorldBreakingThresholdTensile
        objConst.rigid_body_constraint.type = constraintType
    
    # Take simulation steps into account (Threshold = F / Steps)    
    breakingThreshold /= bpy.context.scene.rigidbody_world.steps_per_second
        
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
    # Store breaking threshold sum (all connections combined over the cross section)
    obj1['brkThreshSum'] = breakingThreshold1
    obj2['brkThreshSum'] = breakingThreshold2
    # Always use weaker breaking threshold of both objects for the connecting constraint
    if breakingThreshold1 <= breakingThreshold2: breakingThreshold = breakingThreshold1
    else:                                        breakingThreshold = breakingThreshold2 
    
    # If it's not a connection between two pillars:
    # Divide breaking threshold by connection count, this should emulate the shared connection space (based on cross section area).
    #if elementType1 != 1 or elementType2 != 1:
    #    breakingThreshold /= 4     # Because of 4 connecting sides, earlier I used: objConst['clusterConCount']
    
    objConst.rigid_body_constraint.breaking_threshold = breakingThreshold

    # Add to Bullet group in case someone removed it in the mean time
    try: bpy.data.groups["RigidBodyConstraints"].objects.link(objConst)
    except: pass

    return obj1, obj2
   
#######################    
    
def run():
    """"""
    pi = 3.1415927
    bpy.context.tool_settings.mesh_select_mode = True, False, False
    scene = bpy.context.scene
    try: grpPillarGroup = bpy.data.groups[pillarGroup]
    except: grpPillarGroup = None
    
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
            # Clear object properties
            for key in obj.keys(): del obj[key]
            # Detect if mesh or empty (constraint)
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
                loc = mat *v.co       # Multiply matrix by vertex coordinates to get global coordinates
                kd.insert(loc, i)
            kd.balance()
            kdsMeComp.append(kd)
                        
        ###### Prepare connection map
        print("Building connection map for %d objects..." %len(objs))
        time_start_connections = time.time()
    
        consPair = []   # Stores both connected objects indices per constraint
        consLoc = []    # Stores locations of the constraints
        consVertPairCnt = []    # Stores number of vertex pairs found between each object pair
        count = 0
        for k in range(len(objs)):
            sys.stdout.write('\r' +"%d" %k)
            
            qNextObj = 0
            obj = objs[k]
            mat = obj.matrix_world
            me = obj.data
                    
            ### Find closest objects via kd-tree
            co_find = obj.location
            aIndex = []#; aCo = []; aDist = [];
            if constraintCountLimit:
                for (co, index, dist) in kdObjs.find_n(co_find, constraintCountLimit +1):  # +1 because the first item will be removed
                    aIndex.append(index)#; aCo.append(co); aDist.append(dist)
            else:
                for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                    aIndex.append(index)#; aCo.append(co); aDist.append(dist)
            aIndex = aIndex[1:] # Remove first item because it's the same as co_find (zero distance)
            
            for m in range(len(me.vertices)):
                vert = me.vertices[m]
                co_find = mat *vert.co     # Multiply matrix by vertex coordinates to get global coordinates
                            
                # Loops for comparison object
                for j in range(len(aIndex)):
                    l = aIndex[j]
                    
                    if k != l:
                        # Use object specific vertex kd-tree
                        kdMeComp = kdsMeComp[l]
                        
                        ### Find closest vertices via kd-tree
                        if len(kdMeComp.find_range(co_find, searchDistance)) > 0:   # If vert is within search range add connection to sublist
                            coComp = kdMeComp.find(co_find)[0]    # Find coordinates of the closest vertex
                            co = (co_find +coComp) /2             # Calculate center of both vertices
                            
                            ### Create connection if not already existing
                            conCount = 0
                            pair = [k, l]
                            pair.sort()
                            if pair not in consPair:
                                consPair.append(pair)
                                if clusterRadius > 0: consLoc.append(co)
                                else:                 consLoc.append((objs[k].location +objs[l].location) /2)
                                consVertPairCnt.append(.5)
                                conCount += 1
                                count += 1
                                if conCount == constraintCountLimit:
                                    if ReqVertexPairs <= 1:
                                        qNextObj = 1
                                        break
                            else:
                                consVertPairCnt[consPair.index(pair)] += .5
                if qNextObj: break
        
        print(' - Time: %0.2f s' %(time.time()-time_start_connections))
        
        ### Delete connections with too few connected vertices
        ### With one exception: Connections to pillars need only one vertex pair
        if ReqVertexPairs > 1:
            consPairTmp = []
            consLocTmp = []
            countOld = count
            count = 0
            for i in range(len(consPair)):
                pair = consPair[i]
                co = consLoc[i]
                if consVertPairCnt[i] >= ReqVertexPairs \
                or (grpPillarGroup and (objs[pair[0]].name in bpy.data.groups[pillarGroup].objects \
                or objs[pair[1]].name in bpy.data.groups[pillarGroup].objects) \
                and consVertPairCnt[i] >= ReqVertexPairsToPillars):
                    consPairTmp.append(pair)
                    consLocTmp.append(co)
                    count += 1
            consPair = consPairTmp
            consLoc = consLocTmp
            print("%d connections skipped due to too few connecting vertices." %(countOld -count))
                                
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
        
        ### Bundling close empties into clusters, merge locations and count connections per cluster
        if clusterRadius > 0:
            print("Bundling close empties into clusters...")
            ### Build kd-tree for constraint locations
            kdObjs = mathutils.kdtree.KDTree(len(consLoc))
            for i, loc in enumerate(consLoc):
                kdObjs.insert(loc, i)
            kdObjs.balance()
            clustersCons = []   # Stores all constraints indices per cluster
            clustersLoc = []    # Stores the location of each cluster
            consIdx = []
            for i in range(len(consLoc)):
                consIdx.append(i)
            while len(consIdx) > 0:
                ### Find closest objects via kd-tree (zero distance start item included)
                co_find = consLoc[consIdx[0]]
                aIndex = []; aCo = []#; aDist = [];
                for (co, index, dist) in kdObjs.find_range(co_find, clusterRadius):
                    aIndex.append(index); aCo.append(co)#; aDist.append(dist)
                
                ### Calculate average location of all constraints found in cluster radius
                ### (Cluster locations can be fuzzy because of "first come, first served" method if constraints are scattered all over the place.
                ### This however could be improved by more clever averaging, like only merge two constraints at a time and doing multiple loops.)
                clustersCons.append([])
                loc = Vector((0,0,0))
                for l in range(len(aIndex)):
                    if aIndex[l] in consIdx:
                        clustersCons[-1:][0].append(aIndex[l])
                        consIdx.remove(aIndex[l])
                        loc += aCo[l]
                loc /= len(clustersCons[-1:][0])
                clustersLoc.append(loc)
            ### Apply cluster locations to constraints
            for l in range(len(clustersCons)):
                for k in clustersCons[l]:
                    consLoc[k] = clustersLoc[l]
                    empties[k]['clusterConCount'] = len(clustersCons[l])
        else:
            for empty in empties:
                empty['clusterConCount'] = 1
                                
        ### Add constraint settings to empties
        print("Add constraint settings to empties...")
        for k in range(len(empties)):
            sys.stdout.write('\r' +"%d" %k)
                
            objConst = empties[k]
            objConst.location = consLoc[k]
            objConst.rigid_body_constraint.object1 = objs[consPair[k][0]]
            objConst.rigid_body_constraint.object2 = objs[consPair[k][1]]
        
        print(' - Time: %0.2f s' %(time.time()-time_start_building))

            
    ### If constraint empties are detected then update constraint settings
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