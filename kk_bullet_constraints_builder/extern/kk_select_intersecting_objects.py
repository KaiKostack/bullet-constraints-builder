###################################################
# Select intersecting objects v1.1 by Kai Kostack #
###################################################
# This script detects and selects objects intersecting with other objects
# by a certain amount of volume based on boundary boxes (not actual geometry).
# Notes:
# Some functions are taken from kk_bullet_constraints_builder
# Slightly changed: findConnectionsByBoundaryBoxIntersection()
# Changed to volume: calculateContactAreaBasedOnBoundaryBoxesForPair()

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

debug = 0

import bpy, sys, mathutils, random, time
from mathutils import *

################################################################################   

def run(source=None, parameters=None):

    ### Vars
    mode = 1              # 1   | Search mode: 1 = boundary boxes 
    searchDistance = .02  # .02 | Near distance limit (object centers in range of selected mesh's vertices)
    minimumVolume = .0001 # .01 | Minimum intersection volume, object pairs with a shared volume equal or above that value will be selected (0 = off)
    encaseTol = 0         # .02 | Restricts one of the objects of a pair to be encased into the other by this specific tolerance (0 = off)
                          # This can help to avoid selection of objects whose boundary boxes are intersecting but are actually non-intersecting meshes
    qSelectByVertCnt = 0  # 1   | Prefer less vertices (= 1) over more for found object pairs (0 = off, 2 = more over less)
    qSelectSmallerVol = 0 # 1   | Select the smaller object of found object pairs by volume in case qSelectByVertCnt finds the same vertex counts
    qSelectA = 1          # 1   | Select first object of found object pairs (for qSelectByVertCnt = 0 & qSelectSmallerVol = 0)
    qSelectB = 1          # 0   | Select second object of found object pairs (for qSelectByVertCnt = 0 & qSelectSmallerVol = 0)
    qDelete = 0           # 0   | Deletes object duplicates (instead of selection only)

    qBool = 1             # 0   | Use boolean subtraction to resolve overlappings (overrides all above selection settings)

    ### Internal vars for BCB related functions
    connectionCountLimit = 0

    ### Custom BCB parameter handling
    if source == 'BCB':
        # Auto: [0.02, 1, 1, 0, 0]; Show selection: [0, 0, 0, 1, 1]
        encaseTol = parameters[0]
        qSelectByVertCnt = parameters[1]
        qSelectSmallerVol = parameters[2]
        qSelectA = parameters[3]
        qSelectB = parameters[4]
        qDelete = parameters[5]
        qBool = parameters[6]
        qSilentVerbose = 1

    ###

    print('\nStart detecting intersection objects...')

    time_start = time.time()
    random.seed(0)
    bpy.context.tool_settings.mesh_select_mode = True, False, False 
    scene = bpy.context.scene
    if mode == 1:
        
        objs = []
        for obj in scene.objects:
             if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(scene) and len(obj.data.vertices) > 0:
                objs.append(obj)
        
        ###### Find connections by boundary box intersection and skip connections whose elements are too small and store them for later parenting
        connectsPair, connectsPairDist = findConnectionsByBoundaryBoxIntersection(objs, searchDistance, connectionCountLimit)
        ###### Calculate contact area for all connections
        contactVolume, connectsLoc = calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair, encaseTol)
        ###### Delete connections with zero contact area/volume
        connectsPair, connectsArea, connectsLoc = deleteConnectionsWithZeroContactArea(objs, connectsPair, contactVolume, connectsLoc, minimumVolume)

        # Deselect all objects.
        bpy.ops.object.select_all(action='DESELECT')

        count = 0
        
        if qBool:

            print("Resolving found intersections... (%d)" %len(connectsPair))

            for k in range(len(connectsPair)):
                sys.stdout.write('\r' +"%d " %k)

                objA = objs[connectsPair[k][0]]
                objB = objs[connectsPair[k][1]]
                if qSelectA and not objA.select: objA.select = 1
                if qSelectB and not objB.select: objB.select = 1

                locA = objA.matrix_world.to_translation()  # Use actual locations (taking parent relationships into account)
                locB = objB.matrix_world.to_translation()
                # Always subtract the higher located object from the lower one (based on centroids) so swap objects if necessary
                if locA[2] > locB[2]: objA, objB = objB, objA
                # In case of same Z location for both objects subtract the one with the smaller volume so swap objects if necessary
                elif locA[2] == locB[2]:
                    volA = objA.dimensions[0] *objA.dimensions[1] *objA.dimensions[2]      
                    volB = objB.dimensions[0] *objB.dimensions[1] *objB.dimensions[2]      
                    if volA < volB: objA, objB = objB, objA
                
                ### Add triangulation modifier to A
                bpy.context.scene.objects.active = objA
                bpy.context.scene.objects.active.modifiers.new(name="Triangulate", type='TRIANGULATE')
                mod = bpy.context.scene.objects.active.modifiers["Triangulate"]
                mod.quad_method = 'BEAUTY'
                # Apply modifier
                try: bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                except: bpy.ops.object.modifier_remove(modifier=mod.name)
                
                ### Add triangulation modifier to B
                bpy.context.scene.objects.active = objB
                bpy.context.scene.objects.active.modifiers.new(name="Triangulate", type='TRIANGULATE')
                mod = bpy.context.scene.objects.active.modifiers["Triangulate"]
                mod.quad_method = 'BEAUTY'

                ### Add displacement modifier to B with a small random variation which can help to avoid boolean errors for exact overlapping geometry
                bpy.context.scene.objects.active.modifiers.new(name="Displace", type='DISPLACE')
                mod = bpy.context.scene.objects.active.modifiers["Displace"]
                mod.mid_level = 0
                mod.strength = random.uniform(0.00001, 0.001)

                ### Add boolean modifier to subtract B from A
                bpy.context.scene.objects.active = objA
                bpy.context.scene.objects.active.modifiers.new(name="Boolean_Intersect", type='BOOLEAN')
                mod = bpy.context.scene.objects.active.modifiers["Boolean_Intersect"]
                mod.operation = 'DIFFERENCE'
                try: mod.solver = 'CARVE'
                except: pass
                mod.object = objB
                # Apply modifier
                try: bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
                except: bpy.ops.object.modifier_remove(modifier=mod.name)
                
                # Remove modifiers
                bpy.context.scene.objects.active = objB
                bpy.ops.object.modifier_remove(modifier="Triangulate")
                bpy.ops.object.modifier_remove(modifier="Displace")
               
                count += 1
            print()
            print('Objects modified (one per pair):', count)

            # Backup selection
            selection = [obj for obj in bpy.context.scene.objects if obj.select]
            # Deselect all objects.
            bpy.ops.object.select_all(action='DESELECT')
            # Select objects without vertices for deletion
            cnt = 0
            for obj in objs:
                if len(obj.data.vertices) <= 1:
                    obj.select = 1
                    cnt += 1
            ### Delete all selected objects
            bpy.ops.object.delete(use_global=True)
            # Revert to backup selection again
            for obj in selection:
                try: obj.select = 1
                except: pass
            
            print('Objects deleted because of zero volume:', cnt)

        elif not qBool:

            if qSelectByVertCnt:
                if qSelectByVertCnt == 1:
                    for k in range(len(connectsPair)):
                        objA = objs[connectsPair[k][0]]
                        objB = objs[connectsPair[k][1]]
                        if len(objA.data.vertices) < len(objB.data.vertices):
                            if not objA.select: objA.select = 1; count += 1
                        elif len(objA.data.vertices) > len(objB.data.vertices):
                            if not objB.select: objB.select = 1; count += 1
                        elif qSelectSmallerVol:
                            if connectsArea[k][0] <= connectsArea[k][1]:
                                if not objA.select: objA.select = 1; count += 1
                            else: 
                                if not objB.select: objB.select = 1; count += 1
                elif qSelectByVertCnt == 2:
                    for k in range(len(connectsPair)):
                        objA = objs[connectsPair[k][0]]
                        objB = objs[connectsPair[k][1]]
                        if len(objA.data.vertices) < len(objB.data.vertices):
                            if not objB.select: objB.select = 1; count += 1
                        elif len(objA.data.vertices) > len(objB.data.vertices):
                            if not objA.select: objA.select = 1; count += 1
                        elif qSelectSmallerVol:
                            if connectsArea[k][0] <= connectsArea[k][1]:
                                if not objA.select: objA.select = 1; count += 1
                            else: 
                                if not objB.select: objB.select = 1; count += 1
            elif qSelectSmallerVol:
                for k in range(len(connectsPair)):
                    objA = objs[connectsPair[k][0]]
                    objB = objs[connectsPair[k][1]]
                    if connectsArea[k][0] <= connectsArea[k][1]:
                        if not objA.select: objA.select = 1; count += 1
                    else: 
                        if not objB.select: objB.select = 1; count += 1
            else:
                if qSelectA:
                    for k in range(len(connectsPair)):
                        objA = objs[connectsPair[k][0]]
                        if not objA.select: objA.select = 1; count += 1
                if qSelectB:
                    for k in range(len(connectsPair)):
                        objB = objs[connectsPair[k][1]]
                        if not objB.select: objB.select = 1; count += 1
       
            if qDelete:
                ### Delete all selected objects
                bpy.ops.object.delete(use_global=True)
                
                print('Objects deleted:', count)
            else:
                print('Objects selected:', count)

        
    print('Time: %0.2f s' %(time.time()-time_start))
    print('Done.')

    return count
    
################################################################################   

def boundaryBox(obj, qGlobalSpace):

    ### Calculate boundary box corners and center from given object
    me = obj.data
    verts = me.vertices
    if qGlobalSpace:
        # Multiply local coordinates by world matrix to get global coordinates
        mat = obj.matrix_world
        bbMin = mat *verts[0].co
        bbMax = mat *verts[0].co
    else:
        bbMin = verts[0].co.copy()
        bbMax = verts[0].co.copy()
    for vert in verts:
        if qGlobalSpace: loc = mat *vert.co
        else:            loc = vert.co.copy()
        if bbMax[0] < loc[0]: bbMax[0] = loc[0]
        if bbMin[0] > loc[0]: bbMin[0] = loc[0]
        if bbMax[1] < loc[1]: bbMax[1] = loc[1]
        if bbMin[1] > loc[1]: bbMin[1] = loc[1]
        if bbMax[2] < loc[2]: bbMax[2] = loc[2]
        if bbMin[2] > loc[2]: bbMin[2] = loc[2]
    bbCenter = (bbMin +bbMax) /2
    
    return bbMin, bbMax, bbCenter

################################################################################   

def findConnectionsByBoundaryBoxIntersection(objs, searchDistance, connectionCountLimit):
    
    ### Find connections by boundary box intersection
    print("Searching connections by boundary box intersection... (%d)" %len(objs))
    
    ### Build kd-tree for object locations
    kdObjs = mathutils.kdtree.KDTree(len(objs))
    for i, obj in enumerate(objs):
        kdObjs.insert(obj.location, i)
    kdObjs.balance()
    
    ### Precalculate boundary boxes for all objects
    bboxes = []
    for obj in objs:
        # Calculate boundary box corners
        bbMin, bbMax, bbCenter = boundaryBox(obj, 1)
        # Extend boundary box dimensions by searchDistance
        bbMin -= Vector((searchDistance, searchDistance, searchDistance))
        bbMax += Vector((searchDistance, searchDistance, searchDistance))
        bboxes.append([bbMin, bbMax])
    
    ### Find connections by vertex pairs
    connectsPair = []          # Stores both connected objects indices per connection
    connectsPairDist = []      # Stores distance between both elements
    cnt_sel = 0
    for k in range(len(objs)):
        if objs[k].select:
            sys.stdout.write('\r' +"%d" %cnt_sel)
            cnt_sel += 1
            # Update progress bar
            bpy.context.window_manager.progress_update(k /len(objs))
            
            obj = objs[k]
            mat = obj.matrix_world
            me = obj.data
                    
            ### Find closest objects via kd-tree
            co_find = obj.location
            aIndex = []; aDist = [] #; aCo = [] 
            if connectionCountLimit:
                for (co, index, dist) in kdObjs.find_n(co_find, connectionCountLimit +1):  # +1 because the first item will be removed
                    aIndex.append(index); aDist.append(dist) #; aCo.append(co)
            else:
                for (co, index, dist) in kdObjs.find_range(co_find, 999999):
                    aIndex.append(index); aDist.append(dist) #; aCo.append(co) 
            aIndex = aIndex[1:]; aDist = aDist[1:]  # Remove first item because it's the same as co_find (zero distance)
        
            # Loop through comparison objects found
            for j in range(len(aIndex)):
                l = aIndex[j]
                
                # Skip same object index
                if k != l:
                    bbAMin, bbAMax = bboxes[k]
                    bbBMin, bbBMax = bboxes[l]
                    ### Calculate overlap per axis of both intersecting boundary boxes
                    overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
                    overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
                    overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
                    # Calculate volume
                    volume = overlapX *overlapY *overlapZ
                    if volume > 0:                
                        ### Store connection if not already existing
                        connectCnt = 0
                        pair = [k, l]
                        pair.sort()
                        if pair not in connectsPair:
                            connectsPair.append(pair)
                            connectsPairDist.append(aDist[j])
                            connectCnt += 1
                            if connectCnt == connectionCountLimit: break
        
    print("\nPossible connections found:", len(connectsPair))
    return connectsPair, connectsPairDist

################################################################################   

def calculateContactVolumeBasedOnBoundaryBoxesForPair(objA, objB, encaseTol):

    ###### Calculate contact Volume for a single pair of objects
    
    ### Calculate boundary box corners
    bbAMin, bbAMax, bbACenter = boundaryBox(objA, 1)
    bbBMin, bbBMax, bbBCenter = boundaryBox(objB, 1)
    
    ### Calculate contact surface Volume from boundary box projection
    ### Project along all axis'
    overlapX = max(0, min(bbAMax[0],bbBMax[0]) -max(bbAMin[0],bbBMin[0]))
    overlapY = max(0, min(bbAMax[1],bbBMax[1]) -max(bbAMin[1],bbBMin[1]))
    overlapZ = max(0, min(bbAMax[2],bbBMax[2]) -max(bbAMin[2],bbBMin[2]))
    
    ### Calculate Volume
    contactVolume = overlapX *overlapY *overlapZ
    
    ### Invalidate objects if encasement condition applies
    if encaseTol:
        # Check if A is inside B or B is inside A
        if (bbAMax[0] < bbBMax[0] +encaseTol and bbAMin[0] > bbBMin[0] -encaseTol \
        and bbAMax[1] < bbBMax[1] +encaseTol and bbAMin[1] > bbBMin[1] -encaseTol \
        and bbAMax[2] < bbBMax[2] +encaseTol and bbAMin[2] > bbBMin[2] -encaseTol) \
        or (bbBMax[0] < bbAMax[0] +encaseTol and bbBMin[0] > bbAMin[0] -encaseTol \
        and bbBMax[1] < bbAMax[1] +encaseTol and bbBMin[1] > bbAMin[1] -encaseTol \
        and bbBMax[2] < bbAMax[2] +encaseTol and bbBMin[2] > bbAMin[2] -encaseTol):
            pass
        else:
            contactVolume = -1

    ### Use center of contact area boundary box as constraints location
    centerX = max(bbAMin[0],bbBMin[0]) +(overlapX /2)
    centerY = max(bbAMin[1],bbBMin[1]) +(overlapY /2)
    centerZ = max(bbAMin[2],bbBMin[2]) +(overlapZ /2)
    center = Vector((centerX, centerY, centerZ))
    #center = (bbACenter +bbBCenter) /2     # Debug: Place constraints at the center of both elements like in bashi's addon

    return contactVolume, 0, center 

########################################

def calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair, encaseTol):
    
    ### Calculate contact area for all connections
    print("Calculating contact area for connections...")
    
    connectsArea = []
    connectsLoc = []
    for k in range(len(connectsPair)):
        objA = objs[connectsPair[k][0]]
        objB = objs[connectsPair[k][1]]
        
        ###### Calculate contact area for a single pair of objects
        contactArea, bendingThickness, center = calculateContactVolumeBasedOnBoundaryBoxesForPair(objA, objB, encaseTol)
        
        connectsArea.append([contactArea, bendingThickness, 0])
        connectsLoc.append(center)
        
    return connectsArea, connectsLoc

################################################################################   

def deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsArea, connectsLoc, minimumVolume):
    
    ### Delete connections with zero contact area
    if debug: print("Deleting connections with zero contact area...")
    
    connectsPairTmp = []
    connectsAreaTmp = []
    connectsLocTmp = []
    connectCntOld = len(connectsPair)
    connectCnt = 0
    for i in range(len(connectsPair)):
        if connectsArea[i][0] > minimumVolume:
            connectsPairTmp.append(connectsPair[i])
            connectsAreaTmp.append(connectsArea[i])
            connectsLocTmp.append(connectsLoc[i])
            connectCnt += 1
    connectsPair = connectsPairTmp
    connectsArea = connectsAreaTmp
    connectsLoc = connectsLocTmp
    
    print("Connections skipped due to search conditions:", connectCntOld -connectCnt)
    return connectsPair, connectsArea, connectsLoc

################################################################################   
                
if __name__ == "__main__":
    run()