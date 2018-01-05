#################################################
# Voxel Cell Grid From Mesh v1.3 by Kai Kostack #
#################################################
# Some code is based on Cells.py for Blender 2.4x by Michael Schardt released under the GPL.
# - Triangulation is a requirement, this can be done by this script but also manually before

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

import bpy, sys, mathutils, math, time
from mathutils import Vector

################################################################################   

def run(source=None, parameters=None):
    """"""
    ### Vars
    gridRes = 0                      # Grid resolution related to object dimensions (0 = disabled, [1,3,5..] = correct results, [2,4,6..] = wrong results)
    cellSize = Vector((.5, .5, .5))     # For gridRes = 0: Custom cell size in world units
    qUseUnifiedSpace = 1             # For gridRes = 0: Use one unified space for all cells from all objects to avoid cell overlapping, different scalings and different rotations between objects
                                     # (For cellsToObjectsMode = 1 this is always true for now, could be improved though)
    qFillVolume = 0                  # Enables filled cells within volume
    qFillFromFloor = 1               # Special fill method to fill from bottom to first cell occurrence above
    qCreateGridMesh = 1              # Enables actual creation of a grid mesh
    qFilterDoubleCells = 1           # For qUseUnifiedSpace = 1: Filter out possible double cells from neighboring objects
    qFilterInternalFaces = 1         # Enables different geometry generation method to avoid creation of internal faces, if disabled plain closed cubes will be created
                                     # (Requires qFilterDoubleCells and qUseUnifiedSpace to be enabled)
    qEnforceManifoldness = 1         # Enforces to keep the final mesh manifold by removing cells which would produce non-manifold geometry (corner to corner cells for instance)
                                     # (Requires qFilterInternalFaces to be enabled, also can change the mesh in an undesired way through removal or adding of cells, so better double-check the result afterwards)
    cellsToObjectsMode = 1           # Mode how cells are created as individual objects
                                     # 1 = all detected cells from all selected objects are joined into one mesh object (fastest)
                                     # 2 = cell clusters per object will be created so the overall object count stays the same (large object counts will make this slower)
                                     # 3 = each cell becomes an individual mesh object (can become very slow)
    qRemoveDoubles = 1               # Removes overlapping vertices for all created meshes
    qInvertOutput = 0                # Invert cell output for the entire grid
    qRemoveOpen = 0                  # Removes surroundings of (filled) open space to reveal only inside cavities (use it together with qInvertOutput=1 to visualize cavities)
    qRemoveOpenBottom = 1            # Removes also open spaces pointing downwards (assuming there would be no ground)
    qRemoveOriginal = 1              # Delete original objects
    
    ### Vars internal
    qTriangulate = 1                 # Enables automatic mesh triangulation
    #qSetWireView = 0                # Enables wire display mode for created meshes
    qSilentVerbose = 0               # Reduces text output to a minimum

    ### Custom BCB parameter handling
    if source == 'BCB_Discretize':
        cellSize = parameters[0]
        qSilentVerbose = 1
        qUseUnifiedSpace = 0
        qFilterInternalFaces = 0
        qEnforceManifoldness = 0
        cellsToObjectsMode = 2
        qRemoveDoubles = 0
        qInvertOutput = 0
        qRemoveOpen = 0
        qRemoveOriginal = 1

    elif source == 'BCB_Cavity':
        cellSize = parameters[0]
        qFillVolume = 1
        qFillFromFloor = 0
        qInvertOutput = 1
        qRemoveOpen = 1
        qRemoveOpenBottom = 0
        qRemoveOriginal = 0
         
    ###

    print("\nStarting mesh to cell grid conversion...")
    
    time_start = time.time()
    scene = bpy.context.scene
    pi = 3.1415927
    bpy.context.tool_settings.mesh_select_mode = False, False, True
    
    # Leave edit mode
    try: bpy.ops.object.mode_set(mode='OBJECT') 
    except: pass
    
    # Set object centers to geometry origin
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # create object list of selected objects
    # (because we add more objects with following function we need a separate list)
    objs = []
    for obj in scene.objects:
        if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(scene):
            objs.append(obj)
            # Unlink object (also serves as speed optimization)
            scene.objects.unlink(obj)
    
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
        
    # Main loop starts here
    if cellsToObjectsMode == 1:
        vertsN = []; facesN = []
    f_cells_global = {}
    objsN = []
    objMod = None
    for obj in objs:
        if not qSilentVerbose: print(obj.name)
        else: sys.stdout.write('\r' +"%d    " %len(objsN))
        # Link object (for speed optimization)
        scene.objects.link(obj)
        bpy.context.scene.objects.active = obj
        me = obj.data
        
        if len(me.vertices) == 0: continue
        
        if qTriangulate:
            if not qSilentVerbose: print("Triangulating...")
            ### Add triangulate modifier to original object
            bpy.ops.object.modifier_add(type='TRIANGULATE')
            objMod = createOrReuseObjectAndMesh(bpy.context.scene, objName="$TempMesh$")
            objMod.data = obj.to_mesh(bpy.context.scene, apply_modifiers=1, settings='PREVIEW', calc_tessface=True, calc_undeformed=False)
            objMod.matrix_world = obj.matrix_world
            me = objMod.data
            # Remove triangulate modifier (last) from original object
            obj.modifiers.remove(obj.modifiers[-1])
            ### Apply scale and rotation if necessary
            bpy.context.scene.objects.active = objMod
            objMod.select = 1
            if gridRes == 0:
                if qUseUnifiedSpace:
                    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
                else:
                    if cellsToObjectsMode > 1: bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                    else:                      bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            elif cellsToObjectsMode == 1:
                bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        # Unlink object (for speed optimization)
        if qRemoveOriginal: scene.objects.unlink(obj)
        
        if gridRes > 0:
            ### Find boundary borders
            x1=y1=z1 = 9999; x2=y2=z2 = -9999
            for vert in me.vertices:
                if vert.co.x < x1: x1 = vert.co.x
                if vert.co.x > x2: x2 = vert.co.x
                if vert.co.y < y1: y1 = vert.co.y
                if vert.co.y > y2: y2 = vert.co.y
                if vert.co.z < z1: z1 = vert.co.z
                if vert.co.z > z2: z2 = vert.co.z
            ### Calculate cell size from gridRes if available
            cellSizeX = (x2 -x1) /gridRes
            cellSizeY = (y2 -y1) /gridRes
            cellSizeZ = (z2 -z1) /gridRes
            # Replace possible zero size axis with size from other axis to avoid flat cells 
            for i in range(2):
                if cellSizeX == 0: cellSizeX = cellSizeY
                if cellSizeY == 0: cellSizeY = cellSizeZ
                if cellSizeZ == 0: cellSizeZ = cellSizeX
            if not qSilentVerbose: print("Calculated cell size: %0.3f, %0.3f, %0.3f" %(cellSizeX, cellSizeY, cellSizeZ))
        else:
            cellSizeX = cellSize[0]; cellSizeY = cellSize[1]; cellSizeZ = cellSize[2]
            if not qSilentVerbose: print("Custom cell size: %0.3f, %0.3f, %0.3f" %(cellSizeX, cellSizeY, cellSizeZ))
                   
        ### add polys to corresponding cells (code mostly taken from cells.py for blender 2.4x)
        es = [Vector((1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), Vector((0.0, 0.0, 1.0))]
        v_cells = {}		
        for vert in me.vertices:
            coords = vert.co
            v_cells[vert] = (int(round(coords[0] /cellSizeX)), int(round(coords[1] /cellSizeY)), int(round(coords[2] /cellSizeZ)))
        f_cells = {}
        for face in me.polygons:
            verts = [me.vertices[vertIdx] for vertIdx in face.vertices]
            fidxs = [v_cells[vert][0] for vert in verts]; fidxs.sort()		
            min_fidx = fidxs[0]; max_fidx = fidxs[-1]		
            fidys = [v_cells[vert][1] for vert in verts]; fidys.sort()
            min_fidy = fidys[0]; max_fidy = fidys[-1]
            fidzs = [v_cells[vert][2] for vert in verts]; fidzs.sort()
            min_fidz = fidzs[0]; max_fidz = fidzs[-1]
            ### fast path for special cases (especially small faces spanning a single cell only)
            category = 0
            if (max_fidx > min_fidx): category |= 1
            if (max_fidy > min_fidy): category |= 2
            if (max_fidz > min_fidz): category |= 4
            if category == 0: # single cell
                f_cells.setdefault((min_fidx, min_fidy, min_fidz), set()).add(face)
                continue
            if category == 1: # multiple cells in x-, single cell in y- and z-direction
                for fidx in range(min_fidx, max_fidx +1):
                    f_cells.setdefault((fidx, min_fidy, min_fidz), set()).add(face)
                continue
            if category == 2: # multiple cells in y-, single cell in x- and z-direction
                for fidy in range(min_fidy, max_fidy +1):
                    f_cells.setdefault((min_fidx, fidy, min_fidz), set()).add(face)
                continue
            if category == 4: # multiple cells in z-, single cell in x- and y-direction
                for fidz in range(min_fidz, max_fidz +1):
                    f_cells.setdefault((min_fidx, min_fidy, fidz), set()).add(face)
                continue

            ### long path (face spans multiple cells in more than one direction)
            a0 = face.normal
            r0 =  0.5 *(math.fabs(a0[0]) *cellSizeX +math.fabs(a0[1]) *cellSizeY +math.fabs(a0[2]) *cellSizeZ)
            cc = Vector((0.0, 0.0, 0.0))
            for fidx in range(min_fidx, max_fidx +1):
                cc[0] = fidx * cellSizeX
                for fidy in range(min_fidy, max_fidy +1):
                    cc[1] = fidy * cellSizeY
                    for fidz in range(min_fidz, max_fidz +1):
                        cc[2] = fidz * cellSizeZ
                        if not qFillVolume and (fidx, fidy, fidz) in f_cells: continue  # cell already populated -> no further processing needed for hollow model
                        vs = [vert.co -cc for vert in verts]
                        if not (-r0 <= a0 * vs[0] <= r0): continue  # cell not intersecting face hyperplane

                        ### check overlap of cell with face (separating axis theorem)
                        fs = [vs[1] -vs[0], vs[2] -vs[1], vs[0] -vs[2]]
                        overlap = True
                        for f in fs:
                            if not overlap: break
                            for e in es:
                                if not overlap: break
                                a = e.copy()
                                a = a.cross(f)
                                r = 0.5 *(math.fabs(a[0]) *cellSizeX +math.fabs(a[1]) *cellSizeY +math.fabs(a[2]) *cellSizeZ)						
                                ds = [a *v for v in vs]; ds.sort()
                                if (ds[0] > r or ds[-1] < -r): overlap = False
                        if overlap:
                            f_cells.setdefault((fidx, fidy, fidz), set()).add(face)
                            
        if qFillVolume:
            # find min, max cells in x, y, z
            idxs = [id[0] for id in f_cells]; idxs.sort()        
            min_idx = idxs[0]; max_idx = idxs[-1]        
            idys = [id[1] for id in f_cells]; idys.sort()
            min_idy = idys[0]; max_idy = idys[-1]
            idzs = [id[2] for id in f_cells]; idzs.sort()
            min_idz = idzs[0]; max_idz = idzs[-1]

            testpoint = Vector((0.0, 0.0, 0.0))
            # for x, y
            for idx in range(min_idx, max_idx +1):
                testpoint[0] = idx *cellSizeX
                for idy in range(min_idy, max_idy +1):
                    testpoint[1] = idy *cellSizeY
                    odd_parity = False
                    tested_faces = set()

                    # walk the z pile and keep track of parity
                    for idz in range(min_idz, max_idz +1):
                        fs = f_cells.get((idx, idy, idz), set()) -tested_faces
                        
                        # cell contains faces
                        if fs:
                            # categorize faces in this cell by normal
                            pfaces = []
                            nfaces = []
                            for f in fs:
                                fnoz = f.normal[2]
                                if fnoz >= 0.0: pfaces.append(f)
                                if fnoz <= 0.0: nfaces.append(f)                        
                                tested_faces.add(f)
                            
                            # check if testpoint inside z projections
                            if pfaces:                                                                        
                                if insideZProjection(me, testpoint, pfaces): odd_parity = not odd_parity
                            if nfaces:
                                if insideZProjection(me, testpoint, nfaces): odd_parity = not odd_parity

                        # cell contains no faces (empty cell)
                        else:
                            if odd_parity: f_cells[(idx, idy, idz)] = {}  # odd parity -> empty cell inside object

        ### Create mesh cells
        if qCreateGridMesh:

            ### Determine actual grid resolution for object and index ranges
            gridMinX = 999999; gridMinY = 999999; gridMinZ = 999999
            gridMaxX = -999999; gridMaxY = -999999; gridMaxZ = -999999
            for f in f_cells:
                if f[0] < gridMinX: gridMinX = f[0]
                if f[1] < gridMinY: gridMinY = f[1]
                if f[2] < gridMinZ: gridMinZ = f[2]
                if f[0] > gridMaxX: gridMaxX = f[0]
                if f[1] > gridMaxY: gridMaxY = f[1]
                if f[2] > gridMaxZ: gridMaxZ = f[2]
            gridResX = gridMaxX -gridMinX +1; gridResY = gridMaxY -gridMinY +1; gridResZ = gridMaxZ -gridMinZ +1
            if not qSilentVerbose: print("Resolution: %d, %d, %d" %(gridResX, gridResY, gridResZ))

            ### Inversion of cells
            if qInvertOutput:
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for y in range(gridMinY, gridMaxY+1):
                        for x in range(gridMinX, gridMaxX+1):
                            if (x, y, z) not in f_cells:
                                f_cells_new[(x, y, z)] = {}
                f_cells = f_cells_new

            ### Special fill method to fill from bottom to first cell occurrence above
            if qFillFromFloor:
                ### Fill from bottom
                f_cells_new = {}
                for y in range(gridMinY, gridMaxY+1):
                    for x in range(gridMinX, gridMaxX+1):
                        first = None
                        for z in range(gridMinZ, gridMaxZ+1):
                            if (x, y, z) in f_cells:
                                f_cells_new[(x, y, z)] = {}
                                if first == None and z > gridMinZ: first = z  # Skip the lowest cell to avoid stopping at the ground plane
                        if first != None:
                            for z in range(gridMinZ, first):
                                f_cells_new[(x, y, z)] = {}
                f_cells = f_cells_new
            
            ### Removes surroundings of (filled) open space to reveal only inside cavities
            if qRemoveOpen:
                f_cells_bak = f_cells.copy()
                ### Remove top
                f_cells_new = {}
                for y in range(gridMinY, gridMaxY+1):
                    for x in range(gridMinX, gridMaxX+1):
                        qFill = 0
                        cell = cell_last = 1
                        for z in reversed(range(gridMinZ, gridMaxZ+1)):
                            if (x, y, z) in f_cells:
                                if qFill: f_cells_new[(x, y, z)] = {}
                                else: cell_last = cell; cell = 1
                            else:
                                if cell_last != cell: qFill = 1
                                else: cell_last = cell; cell = 0
                f_cells = f_cells_new
                ### Remove bottom
                if qRemoveOpenBottom:
                    f_cells_new = {}
                    for y in range(gridMinY, gridMaxY+1):
                        for x in range(gridMinX, gridMaxX+1):
                            qFill = 0
                            cell = cell_last = 1
                            for z in range(gridMinZ, gridMaxZ+1):
                                if (x, y, z) in f_cells:
                                    if qFill: f_cells_new[(x, y, z)] = {}
                                    else: cell_last = cell; cell = 1
                                else:
                                    if cell_last != cell: qFill = 1
                                    else: cell_last = cell; cell = 0
                    f_cells_mul1 = f_cells_new
                
                f_cells = f_cells_bak.copy()
                ### Remove right
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for y in range(gridMinY, gridMaxY+1):
                        qFill = 0
                        cell = cell_last = 1
                        for x in reversed(range(gridMinX, gridMaxX+1)):
                            if (x, y, z) in f_cells:
                                if qFill: f_cells_new[(x, y, z)] = {}
                                else: cell_last = cell; cell = 1
                            else:
                                if cell_last != cell: qFill = 1
                                else: cell_last = cell; cell = 0
                f_cells = f_cells_new
                ### Remove left
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for y in range(gridMinY, gridMaxY+1):
                        qFill = 0
                        cell = cell_last = 1
                        for x in range(gridMinX, gridMaxX+1):
                            if (x, y, z) in f_cells:
                                if qFill: f_cells_new[(x, y, z)] = {}
                                else: cell_last = cell; cell = 1
                            else:
                                if cell_last != cell: qFill = 1
                                else: cell_last = cell; cell = 0
                f_cells_mul2 = f_cells_new
                
                f_cells = f_cells_bak.copy()
                ### Remove back
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for x in range(gridMinX, gridMaxX+1):
                        qFill = 0
                        cell = cell_last = 1
                        for y in reversed(range(gridMinY, gridMaxY+1)):
                            if (x, y, z) in f_cells:
                                if qFill: f_cells_new[(x, y, z)] = {}
                                else: cell_last = cell; cell = 1
                            else:
                                if cell_last != cell: qFill = 1
                                else: cell_last = cell; cell = 0
                f_cells = f_cells_new
                ### Remove front
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for x in range(gridMinX, gridMaxX+1):
                        qFill = 0
                        cell = cell_last = 1
                        for y in range(gridMinY, gridMaxY+1):
                            if (x, y, z) in f_cells:
                                if qFill: f_cells_new[(x, y, z)] = {}
                                else: cell_last = cell; cell = 1
                            else:
                                if cell_last != cell: qFill = 1
                                else: cell_last = cell; cell = 0
                f_cells_mul3 = f_cells_new

                ### Combine top+bottom, right+left and back+front layers
                f_cells_new = {}
                for z in range(gridMinZ, gridMaxZ+1):
                    for y in range(gridMinY, gridMaxY+1):
                        for x in range(gridMinX, gridMaxX+1):
                            if qRemoveOpenBottom:
                                if  (x, y, z) in f_cells_mul1 \
                                and (x, y, z) in f_cells_mul2 \
                                and (x, y, z) in f_cells_mul3:
                                    f_cells_new[(x, y, z)] = {}
                            else:
                                if  (x, y, z) in f_cells_mul2 \
                                and (x, y, z) in f_cells_mul3:
                                    f_cells_new[(x, y, z)] = {}
                f_cells = f_cells_new

            ### Start of actual geometry creation
            if cellsToObjectsMode > 1:
                vertsN = []; facesN = []
            cellCnt = 0
            
            for f in f_cells:
                if f not in f_cells_global or not (qFilterDoubleCells and qUseUnifiedSpace):
                    if cellCnt %100 == 0: sys.stdout.write('\r' +"%d    " %cellCnt)
                    cellCnt += 1
                    
                    if qFilterDoubleCells and qUseUnifiedSpace: f_cells_global[f] = 1
                    
                    if qFilterInternalFaces == 0:  # Otherwise mesh building will be postponed and the global cell list will be used later
                        boxV1 = Vector((f[0] *cellSizeX -(cellSizeX /2),
                                        f[1] *cellSizeY -(cellSizeY /2),
                                        f[2] *cellSizeZ -(cellSizeZ /2)))
                        boxV2 = Vector((f[0] *cellSizeX +(cellSizeX /2),
                                        f[1] *cellSizeY +(cellSizeY /2),
                                        f[2] *cellSizeZ +(cellSizeZ /2)))
                        o = len(vertsN)
                        vertsN.append((boxV1[0], boxV1[1], boxV1[2]))  # 0
                        vertsN.append((boxV2[0], boxV1[1], boxV1[2]))  # 1
                        vertsN.append((boxV1[0], boxV2[1], boxV1[2]))  # 2
                        vertsN.append((boxV2[0], boxV2[1], boxV1[2]))  # 3
                        vertsN.append((boxV1[0], boxV1[1], boxV2[2]))  # 4
                        vertsN.append((boxV2[0], boxV1[1], boxV2[2]))  # 5
                        vertsN.append((boxV1[0], boxV2[1], boxV2[2]))  # 6
                        vertsN.append((boxV2[0], boxV2[1], boxV2[2]))  # 7
                        facesN.append((o+1, o+0, o+2, o+3))  # Bottom
                        facesN.append((o+4, o+5, o+7, o+6))  # Top
                        facesN.append((o+0, o+1, o+5, o+4))  # Front
                        facesN.append((o+3, o+2, o+6, o+7))  # Behind
                        facesN.append((o+2, o+0, o+4, o+6))  # Left
                        facesN.append((o+1, o+3, o+7, o+5))  # Right
                        if cellsToObjectsMode == 3:
                            objN = createMeshObjectFromData(vertsN, [], facesN)
                            scene.objects.link(objN)
                            objN.name = obj.name
                            copyCustomData(objN, obj)
                            if gridRes > 0: objN.matrix_world = obj.matrix_world
                            elif not qUseUnifiedSpace:
                                objN.location = obj.location
                                objN.rotation_euler = obj.rotation_euler
                                objN.rotation_quaternion = obj.rotation_quaternion
                                objN.dimensions = Vector((obj.dimensions[0] /gridResX, obj.dimensions[1] /gridResY, obj.dimensions[2] /gridResZ))
                            objsN.append(objN)
                            vertsN = []; facesN = []
            if not qSilentVerbose: print()

            if cellsToObjectsMode == 2:
                objN = createMeshObjectFromData(vertsN, [], facesN)
                scene.objects.link(objN)
                objN.name = obj.name
                copyCustomData(objN, obj)
                if gridRes > 0: objN.matrix_world = obj.matrix_world
                elif not qUseUnifiedSpace:
                    objN.location = obj.location
                    objN.rotation_euler = obj.rotation_euler
                    objN.rotation_quaternion = obj.rotation_quaternion
                    objN.dimensions = obj.dimensions
                objsN.append(objN)
    if qSilentVerbose: print()
        
    ### Mesh building for global cell array if non-manifold mesh is enabled
    if qCreateGridMesh and qFilterInternalFaces == 1:
        print("Creating global cell mesh...")

        ### Determine actual grid resolution for all objects and index ranges
        gridMinX = 999999; gridMinY = 999999; gridMinZ = 999999
        gridMaxX = -999999; gridMaxY = -999999; gridMaxZ = -999999
        for f in f_cells_global:
            if f[0] < gridMinX: gridMinX = f[0]
            if f[1] < gridMinY: gridMinY = f[1]
            if f[2] < gridMinZ: gridMinZ = f[2]
            if f[0] > gridMaxX: gridMaxX = f[0]
            if f[1] > gridMaxY: gridMaxY = f[1]
            if f[2] > gridMaxZ: gridMaxZ = f[2]
        gridResX = gridMaxX -gridMinX +1; gridResY = gridMaxY -gridMinY +1; gridResZ = gridMaxZ -gridMinZ +1
        if not qSilentVerbose: print("Global resolution: %d, %d, %d" %(gridResX, gridResY, gridResZ))

        ### Filter corner to corner cases if non-manifolds should be avoided and remove problematic cells
        xEnd = gridMaxX +1; yEnd = gridMaxY +1; zEnd = gridMaxZ +1
        if qEnforceManifoldness:
            if not qSilentVerbose: print("Filtering non-manifold corner cases...")
            xStart = gridMinX; yStart = gridMinY; zStart = gridMinZ
            found = 1
            foundCnt = -1
            while found:
                foundCnt += found
                sys.stdout.write('\r' +"%d non-manifold cells identified and removed." %foundCnt)
                found = 0
                for z in range(zStart, zEnd):
                    for y in range(yStart, yEnd):
                        for x in range(xStart, xEnd):
                            ### Check for current cell + neighbors existence
                            ### Following vars describe a volume of 2x9 cells, since we are walking in +X direction we ignore the 9 cells from the backside
                            qXYZ = (x, y, z) in f_cells_global
                            # Neighbors
                            qX1 = (x+1, y, z) in f_cells_global
                            qY1 = (x, y+1, z) in f_cells_global
                            qZ1 = (x, y, z+1) in f_cells_global
                            qY2 = (x, y-1, z) in f_cells_global
                            qZ2 = (x, y, z-1) in f_cells_global
                            # Diagonals
                            qXYZ1 = (x+1, y+1, z+1) in f_cells_global
                            qXYZ2 = (x+1, y+1, z-1) in f_cells_global
                            qXYZ3 = (x+1, y-1, z+1) in f_cells_global
                            qXYZ4 = (x+1, y-1, z-1) in f_cells_global
                            qXY1 = (x+1, y+1, z) in f_cells_global
                            qXY2 = (x+1, y-1, z) in f_cells_global
                            qXZ1 = (x+1, y, z+1) in f_cells_global
                            qXZ2 = (x+1, y, z-1) in f_cells_global
                            qYZ1 = (x, y+1, z+1) in f_cells_global
                            qYZ2 = (x, y+1, z-1) in f_cells_global
                            qYZ3 = (x, y-1, z+1) in f_cells_global
                            qYZ4 = (x, y-1, z-1) in f_cells_global
                            ### Remove problematic combinations
                            ### Only diagonal cells without direct connection via surface neighbors will invoke removal of the current cell
                            # Corner cases, check for connection paths, result will be positive if not even one path to the vertex corner can be found
                            c1 = (qXYZ and qXYZ1 and not ((qX1 and (qXY1 or qXZ1)) or (qY1 and (qXY1 or qYZ1)) or (qZ1 and (qXZ1 or qYZ1))))
                            c2 = (qXYZ and qXYZ2 and not ((qX1 and (qXY1 or qXZ2)) or (qY1 and (qXY1 or qYZ2)) or (qZ2 and (qXZ2 or qYZ2))))
                            c3 = (qXYZ and qXYZ3 and not ((qX1 and (qXY2 or qXZ1)) or (qY2 and (qXY2 or qYZ3)) or (qZ1 and (qXZ1 or qYZ3))))
                            c4 = (qXYZ and qXYZ4 and not ((qX1 and (qXY2 or qXZ2)) or (qY2 and (qXY2 or qYZ4)) or (qZ2 and (qXZ2 or qYZ4))))
                            # Corner cases negative
                            cn1 = (not qXYZ and not qXYZ1 and not ((not qX1 and (not qXY1 or not qXZ1)) or (not qY1 and (not qXY1 or not qYZ1)) or (not qZ1 and (not qXZ1 or not qYZ1))))
                            cn2 = (not qXYZ and not qXYZ2 and not ((not qX1 and (not qXY1 or not qXZ2)) or (not qY1 and (not qXY1 or not qYZ2)) or (not qZ2 and (not qXZ2 or not qYZ2))))
                            cn3 = (not qXYZ and not qXYZ3 and not ((not qX1 and (not qXY2 or not qXZ1)) or (not qY2 and (not qXY2 or not qYZ3)) or (not qZ1 and (not qXZ1 or not qYZ3))))
                            cn4 = (not qXYZ and not qXYZ4 and not ((not qX1 and (not qXY2 or not qXZ2)) or (not qY2 and (not qXY2 or not qYZ4)) or (not qZ2 and (not qXZ2 or not qYZ4))))
                            # Edge cases, check for connection paths, result will be positive if not even one path to the edge corner can be found
                            e1 = (qXYZ and qXY1 and not (qX1 or qY1))
                            e2 = (qXYZ and qXY2 and not (qX1 or qY2))
                            e3 = (qXYZ and qXZ1 and not (qX1 or qZ1))
                            e4 = (qXYZ and qXZ2 and not (qX1 or qZ2))
                            e5 = (qXYZ and qYZ1 and not (qY1 or qZ1))
                            e6 = (qXYZ and qYZ2 and not (qY1 or qZ2))
                            e7 = (qXYZ and qYZ3 and not (qY2 or qZ1))
                            e8 = (qXYZ and qYZ4 and not (qY2 or qZ2))
                            # Edge cases negative
                            en1 = (not qXYZ and not qXY1 and not (not qX1 or not qY1))
                            en2 = (not qXYZ and not qXY2 and not (not qX1 or not qY2))
                            en3 = (not qXYZ and not qXZ1 and not (not qX1 or not qZ1))
                            en4 = (not qXYZ and not qXZ2 and not (not qX1 or not qZ2))
                            en5 = (not qXYZ and not qYZ1 and not (not qY1 or not qZ1))
                            en6 = (not qXYZ and not qYZ2 and not (not qY1 or not qZ2))
                            en7 = (not qXYZ and not qYZ3 and not (not qY2 or not qZ1))
                            en8 = (not qXYZ and not qYZ4 and not (not qY2 or not qZ2))
                            # Check if either of the paths could not be found (positive), only then remove the cell
                            # 2nd line: also check for the negative version of this condition
                            if c1 or c2 or c3 or c4 or e1 or e2 or e3 or e4 or e5 or e6 or e7 or e8 \
                            or cn1 or cn2 or cn3 or cn4 or en1 or en2 or en3 or en4 or en5 or en6 or en7 or en8:
                                if qXYZ: del f_cells_global[(x, y, z)]
                                else: f_cells_global[(x, y, z)] = 1
                                found += 1
            if not qSilentVerbose: print()
                    
        ### Actual mesh building
        xStart = gridMinX -1; yStart = gridMinY -1; zStart = gridMinZ -1
        cnt = 0
        zV2 = (-2 +1) *cellSizeZ
        for z in range(zStart, zEnd):
            zV1 = zV2
            zV2 = (z +1) *cellSizeZ
            
            yV2 = (-2 +1) *cellSizeY
            for y in range(yStart, yEnd):
                yV1 = yV2
                yV2 = (y +1) *cellSizeY

                if cnt %100 == 0: sys.stdout.write('\r' +"0, %d, %d      " %(y-yStart, z-zStart))
                cnt += 1
                
                xV2 = (-2 +1) *cellSizeX
                for x in range(xStart, xEnd):
                    xV1 = xV2
                    xV2 = (x +1) *cellSizeX
                    
                    ### Check for current cell + neighbors existence
                    qXYZ = (x, y, z) in f_cells_global
                    qX1 = (x+1, y, z) in f_cells_global
                    qY1 = (x, y+1, z) in f_cells_global
                    qZ1 = (x, y, z+1) in f_cells_global
                    
                    ### Check if neighbor cells for X are different and then create a face, "bool(a) != bool(b)" means "a xor b"
                    if bool(qXYZ) != bool(qX1):
                        o = len(vertsN)
                        vertsN.append((xV2, yV1, zV1))  # 0
                        vertsN.append((xV2, yV1, zV2))  # 1
                        vertsN.append((xV2, yV2, zV1))  # 2
                        vertsN.append((xV2, yV2, zV2))  # 3
                        facesN.append((o+1, o+0, o+2, o+3))
                    if bool(qXYZ) != bool(qY1):  # Same for Y
                        o = len(vertsN)
                        vertsN.append((xV1, yV2, zV1))  # 0
                        vertsN.append((xV1, yV2, zV2))  # 1
                        vertsN.append((xV2, yV2, zV1))  # 2
                        vertsN.append((xV2, yV2, zV2))  # 3
                        facesN.append((o+1, o+0, o+2, o+3))
                    if bool(qXYZ) != bool(qZ1):  # Same for Z
                        o = len(vertsN)
                        vertsN.append((xV1, yV1, zV2))  # 0
                        vertsN.append((xV1, yV2, zV2))  # 1
                        vertsN.append((xV2, yV1, zV2))  # 2
                        vertsN.append((xV2, yV2, zV2))  # 3
                        facesN.append((o+1, o+0, o+2, o+3))
        if not qSilentVerbose: print()

            
    if cellsToObjectsMode == 1:
        objN = createMeshObjectFromData(vertsN, [], facesN)
        scene.objects.link(objN)
        objN.name = obj.name
        copyCustomData(objN, obj)
        objsN.append(objN)

    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')
    # Delete temp object
    if objMod != None:
        objMod.select = 1
        bpy.ops.object.delete(use_global=False)
    # Select new objects
    for objN in objsN:
        objN.select = 1
    bpy.context.scene.objects.active = objN
    if cellsToObjectsMode == 3 or (cellsToObjectsMode == 2 and qUseUnifiedSpace):
        # Apply new object centers
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        
    # Remove doubles of new objects
    if qRemoveDoubles:
        for objN in objsN:
            bpy.context.tool_settings.mesh_select_mode = True, False, False
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass 
            # Select all elements
            try: bpy.ops.mesh.select_all(action='SELECT')
            except: pass 
            # Remove doubles
            bpy.ops.mesh.remove_doubles()
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass 
    
    print('Time: %0.2f s' %(time.time()-time_start))
    print('Done.')

################################################################################

def copyCustomData(obj, objSrc):

    ### Link new object to every group the original is linked to
    for grp in bpy.data.groups:
        for objG in grp.objects:
            if objG.name == objSrc.name:
                try: grp.objects.link(obj)
                except: pass
            
    ### Copy materials    
    bpy.context.scene.objects.active = obj
    # Remove all materials from new object first
    while len(obj.material_slots) > 0:
        obj.active_material_index = 0
        bpy.ops.object.material_slot_remove()
    # Add materials slot by slot
    for slot in objSrc.material_slots:
        bpy.ops.object.material_slot_add() 
        obj.material_slots[-1].material = slot.material

################################################################################

def createMeshObjectFromData(verts, edges, faces):

    # Create empty object
    meN = bpy.data.meshes.new("Mesh")
    # Add mesh data to new object
    meN.from_pydata(verts, edges, faces)
    objN = bpy.data.objects.new("Mesh", meN)
    # Switch to wireframe display mode
    #if qSetWireView: objN.draw_type = 'WIRE'
    return objN

################################################################################

def make_triangle(triV1, triV2, triV3):

    meN = bpy.data.meshes.new("$swap$")  
    objN = bpy.data.objects.new("$swap$", meN)
    bpy.context.scene.objects.link(objN)
    faces = [(0,1,2)]
    vertices = [triV1, triV2, triV3]
    meN.from_pydata(vertices, [], faces)
    
################################################################################      

def insideZProjection(me, point, faces):

    # calculate boundary:
    boundary_edges = set()
    for face in faces:
        for edge in ((face.vertices[0], face.vertices[1]),
                     (face.vertices[1], face.vertices[2]),
                     (face.vertices[2], face.vertices[0])):
            if (edge[0], edge[1]) in boundary_edges:
                boundary_edges.remove((edge[0], edge[1]))
                continue
            if (edge[1], edge[0]) in boundary_edges:
                boundary_edges.remove((edge[1], edge[0]))
                continue
            boundary_edges.add(edge)
            
    # point in 2D-polygon test:
    inside = False
    for edge in boundary_edges:
        p0 = me.vertices[edge[0]].co
        p1 = me.vertices[edge[1]].co
        if (p0[1] <= point[1] < p1[1]):
            if mathutils.geometry.normal(point, p0, p1)[2] < 0.0: inside = not inside
            continue
        if (p1[1] <= point[1] < p0[1]):
            if mathutils.geometry.normal(point, p0, p1)[2] > 0.0: inside = not inside
            continue
    
    return inside    
    
################################################################################   

def createOrReuseObjectAndMesh(scene, objName="Mesh"):

    ### Create a fresh object and delete old one, the complexity is needed to avoid pollution with old mesh datablocks
    ### Further, we cannot use the same mesh datablock that has already been used with from_pydata() so there is a workaround for this too
    objEmptyName = "$Temp$"
    try:    obj = bpy.data.objects[objName]
    except:
            try:    me = bpy.data.meshes[objName]
            except: 
                    me = bpy.data.meshes.new(objName)
                    obj = bpy.data.objects.new(objName, me)
            else:
                    obj = bpy.data.objects.new(objName, me)
                    try:    meT = bpy.data.meshes[objEmptyName]
                    except: meT = bpy.data.meshes.new(objEmptyName)
                    obj.data = meT
                    bpy.data.meshes.remove(me, do_unlink=1)
                    me = bpy.data.meshes.new(objName)
                    obj.data = me
            scene.objects.link(obj)
    else:
            #obj = bpy.data.objects[objName]
            me = obj.data
            try:    meT = bpy.data.meshes[objEmptyName]
            except: meT = bpy.data.meshes.new(objEmptyName)
            obj.data = meT
            bpy.data.meshes.remove(me, do_unlink=1)
            me = bpy.data.meshes.new(objName)
            obj.data = me
            try: scene.objects.link(obj)
            except: pass
            
    return obj

################################################################################
                   
if __name__ == "__main__":
    run()