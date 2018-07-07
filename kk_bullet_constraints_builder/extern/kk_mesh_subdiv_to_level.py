##########################################
# Subdivide to Level v2.1 by Kai Kostack #
##########################################
# This script subdivides the edges of all selected objects down until a specified minimum length is reached

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
limit = 2           # Tolerance for difference of vertex coordinates (conversion of meshes can change floats slightly)
useTriangles = 0    # Convert quads and ngons to triangles after each loop
useQuads = 0        # Forces conversion of ngons to quads at cost of higher memory usage and slower speed 
useSeparation = 0   # Try to separate subdivided edges (enforcing useTriangles)
maxVerticesToRipAtOnce = 1  # For useSeparation the number of vertices to rip per loop, higher values will be faster but might also prevent from ripping
qSilentVerbose = 0  # Reduces text output to a minimum

################################################################################   

import bpy, sys, time
from mathutils import Vector

################################################################################   

def run(source=None, parameters=None):
   
    ### Custom BCB parameter handling
    if source == 'BCB':
        global limit; limit = parameters[0]
        global qSilentVerbose; qSilentVerbose = 1

    ###

    print("\nStarting subdivision...")
    print("Maximum edge length: %0.2f" %limit) 
    
    bpy.context.tool_settings.mesh_select_mode = True, False, False
    scene = bpy.context.scene
    objActiveBak = bpy.context.scene.objects.active
    time_start = time.time()

    # Leave edit mode if necessary
    try: bpy.ops.object.mode_set(mode='OBJECT')
    except: pass

    # Create object list of selected objects without instances
    objs = []; objs_instance = []
    for obj in bpy.data.objects:
        if obj.select and obj.type == 'MESH' and not obj.hide and obj.is_visible(scene):
            if obj.data not in objs_instance:  # Leave out instances
                objs.append(obj)
                if obj.data.users > 1: objs_instance.append(obj.data)  # If multiple users then check all following objects against it
    
    # Deselect all objects.
    #bpy.ops.object.select_all(action='DESELECT')
        
    count = 0
    for obj in objs:
        if not qSilentVerbose: print(obj.name)
        else: sys.stdout.write('\r%d' %count)

        bpy.context.scene.objects.active = obj
        me = obj.data
        #bm = bmesh.from_edit_mesh(ob.data)
        
        q = 1; qCnt = 0
        while q > 0:
            q = 0
            
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass
            if useTriangles and not useQuads:
                # Select all elements
                bpy.ops.mesh.select_all(action='SELECT')
                # Convert selection to triangles
                bpy.ops.mesh.quads_convert_to_tris()
            # Deselect all elements
            bpy.ops.mesh.select_all(action='DESELECT')
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass
        
            # Select elements greater than limit
            i = 0; iCnt = len(me.edges)
            while i < iCnt:
                edge = me.edges[i]
                vIdx1 = edge.vertices[0]
                vIdx2 = edge.vertices[1]
                vecLength = me.vertices[vIdx1].co -me.vertices[vIdx2].co
                length = vecLength.length
                if length > limit:
                    edge.select = 1
                    q += 1                   
                i += 1

            oldVcount = len(me.vertices)
            
            bpy.context.tool_settings.mesh_select_mode = False, True, False 
            # Enter edit mode              
            try: bpy.ops.object.mode_set(mode='EDIT')
            except: pass
            # Subdivide selected edges once
            bpy.ops.mesh.subdivide(number_cuts=1, smoothness=0, quadtri=False, quadcorner='STRAIGHT_CUT', fractal=0, fractal_along_normal=0, seed=0)
            if useTriangles and not useQuads:        # then convert everything to triangles
                # Select all elements
                bpy.ops.mesh.select_all(action='SELECT')
                # Convert selection to triangles
                bpy.ops.mesh.quads_convert_to_tris()
            if useQuads and not useTriangles:       # Then convert only selection to quads
                bpy.context.tool_settings.mesh_select_mode = True, False, False 
                # Select more vertices
                bpy.ops.mesh.select_more()
                # Convert selection to triangles
                bpy.ops.mesh.quads_convert_to_tris()
                # Convert selection to quads
                try: bpy.ops.mesh.tris_convert_to_quads(limit=3.14, uvs=False, vcols=False, sharp=False, materials=False)  # 0.698132
                except: pass
            # Deselect all elements
            bpy.ops.mesh.select_all(action='DESELECT')
            # Leave edit mode
            try: bpy.ops.object.mode_set(mode='OBJECT')
            except: pass

            if useSeparation:
                Vcount = len(me.vertices)
                # Do ripping as long as there are new vertices (the created ones by subdivision)
                while oldVcount != Vcount:
                    # Select all new vertices (the created ones by subdivision)
                    j = 0
                    for i in range(oldVcount, Vcount):
                        me.vertices[i].select = 1
                        oldVcount += 1
                        j += 1
                        if j == maxVerticesToRipAtOnce:
                            break
                    if oldVcount != Vcount:
                        bpy.context.tool_settings.mesh_select_mode = True, False, False 
                        # Enter edit mode              
                        try: bpy.ops.object.mode_set(mode='EDIT')
                        except: pass
                        # rip selection
                        try: bpy.ops.mesh.rip('INVOKE_DEFAULT')                        
                        except: pass
                        # Deselect all elements
                        bpy.ops.mesh.select_all(action='DESELECT')
                        # Leave edit mode
                        try: bpy.ops.object.mode_set(mode='OBJECT')
                        except: pass
                  
            if not qSilentVerbose: sys.stdout.write('\r' +str(qCnt) +' ')
            qCnt += q
        if not qSilentVerbose: print('\r%d edges subdivided.' %qCnt)

        count += 1
    print()
    
    # Revert to start selection
    for obj in objs:
        if not obj.select: obj.select = 1
    bpy.context.scene.objects.active = objActiveBak
    
    print('Object(s) changed:', count)
    print('Done. -- Time: %0.2f s' %(time.time() -time_start))
 
################################################################################   

class kkOperator(bpy.types.Operator):
    '''Tooltip'''
    bl_idname = "object.kk_operator"
    bl_label = "KK Operator"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        run()
        return {'FINISHED'}
    
########################################

def register():
    bpy.utils.register_class(kkOperator)

########################################

def unregister():
    bpy.utils.unregister_class(kkOperator)

################################################################################   

if __name__ == "__main__":
    #register()
    #print("KK operator registered! This script needs to be started as operator.")
    #print("Press space bar and search for KK.")

    # Test call
    #bpy.ops.object.kk_operator()
    run()