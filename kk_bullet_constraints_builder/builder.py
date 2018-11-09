##############################
# Bullet Constraints Builder #
##############################
#
# Written within the scope of Inachus FP7 Project (607522):
# "Technological and Methodological Solutions for Integrated
# Wide Area Situation Awareness and Survivor Localisation to
# Support Search and Rescue (USaR) Teams"
# Versions 1 & 2 were developed at the Laurea University of Applied Sciences,
# Finland. Later versions are independently developed.
# Copyright (C) 2015-2018 Kai Kostack
#
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

################################################################################

import bpy, time
mem = bpy.app.driver_namespace

### Import submodules
from global_vars import *      # Contains global variables
from build_data import *       # Contains build data access functions
from builder_prep import *     # Contains preparation steps functions called by the builder
from builder_setc import *     # Contains constraints settings functions called by the builder

################################################################################

def build():
    
    print("\nStarting...\n")
    time_start = time.time()

    if "RigidBodyWorld" in bpy.data.groups:
    
        bpy.context.tool_settings.mesh_select_mode = True, False, False
        props = bpy.context.window_manager.bcb
        scene = bpy.context.scene
        
        # Leave edit mode
        try: bpy.ops.object.mode_set(mode='OBJECT') 
        except: pass
        
        #########################
        ###### Create new empties
        if not "bcb_valid" in scene.keys():
                
            ###### Create object lists of selected objects
            childObjs = []
            objs, emptyObjs = gatherObjects(scene)
            objsEGrp, objCntInEGrps = createElementGroupIndex(objs)
            
            #############################
            ###### Prepare connection map
            if len(objs) > 1:
                if objCntInEGrps > 1:
                    time_start_connections = time.time()
                    
                    ###### Prepare objects (make unique, apply transforms etc.)
                    prepareObjects(objs)
                    ###### Find connections by vertex pairs
                    #connectsPair, connectsPairDist = findConnectionsByVertexPairs(objs, objsEGrp)
                    ###### Find connections by boundary box intersection and skip connections whose elements are too small and store them for later parenting
                    connectsPair, connectsPairDist = findConnectionsByBoundaryBoxIntersection(objs)
                    ###### Delete connections whose elements are too small and make them parents instead
                    if props.minimumElementSize: connectsPair, connectsPairParent = deleteConnectionsWithTooSmallElementsAndParentThemInstead(objs, connectsPair, connectsPairDist)
                    else: connectsPairParent = []
                    ###### Delete connections with too few connected vertices
                    #connectsPair = deleteConnectionsWithTooFewConnectedVertices(objs, objsEGrp, connectsPair)
                    ###### Calculate contact area for all connections
                    ### For now this is not used anymore as it is less safe than to derive an accurate contact area indirectly by using: volume /length
                    if props.useAccurateArea:
                        #connectsGeo, connectsLoc = calculateContactAreaBasedOnBooleansForAll(objs, connectsPair)
                        connectsGeo, connectsLoc = calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair, qAccurate=1)
                    else:
                        connectsGeo, connectsLoc = calculateContactAreaBasedOnBoundaryBoxesForAll(objs, connectsPair, qAccurate=0)
                    ###### Delete connections with zero contact area
                    connectsPair, connectsGeo, connectsLoc = deleteConnectionsWithZeroContactArea(objs, connectsPair, connectsGeo, connectsLoc)
                    ###### Delete connections with references from predefined constraints
                    connectsPair, connectsGeo, connectsLoc = deleteConnectionsWithReferences(objs, emptyObjs, connectsPair, connectsGeo, connectsLoc)
                    ###### Create connection data
                    connectsConsts, constsConnect = createConnectionData(objs, objsEGrp, connectsPair, connectsLoc, connectsGeo)
                    
                    print('-- Time: %0.2f s\n' %(time.time()-time_start_connections))
                    
                    #########################                        
                    ###### Main building part
                    if len(constsConnect) > 0:
                        time_start_building = time.time()
                        
                        ###### Scale elements by custom scale factor and make separate collision object for that
                        applyScale(scene, objs, objsEGrp, childObjs)
                        ###### Bevel elements and make separate collision object for that
                        applyBevel(scene, objs, objsEGrp, childObjs)
                        ###### Create actual parents for too small elements
                        if props.minimumElementSize: makeParentsForTooSmallElementsReal(objs, connectsPairParent)
                        ###### Find and activate first empty layer
                        layersBak = backupLayerSettingsAndActivateNextEmptyLayer(scene)
                        ###### Create empty objects (without any data)
                        if not props.asciiExport:
                            emptyObjs = createEmptyObjs(scene, len(constsConnect))
                        else:  # If FM is used the emptyObjs list is filled with just the names later
                            emptyObjs = [0 for i in range(len(constsConnect))]
                        ###### Bundling close empties into clusters, merge locations and count connections per cluster
                        if props.clusterRadius > 0: bundlingEmptyObjsToClusters(connectsLoc, connectsConsts)
                        # Restore old layers state
                        scene.update()  # Required to update empty locations before layer switching
                        scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)
                        ###### Store build data in scene
                        #if not props.asciiExport:  # Commented out b/c: Postprocessing Tools need some data so we keep it also for FM export, object references are converted to names
                        storeBuildDataInScene(scene, objs, objsEGrp, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, None, constsConnect)
                        
                        scene["bcb_valid"] = 1
                        
                        print('-- Time: %0.2f s\n' %(time.time()-time_start_building))
                    
                    ###### No connections found   
                    else:
                        print('No connections found. Probably the search distance is too small.')
                        return 1 
                
                ###### No element assigned to element group found
                else:
                    print('Please make sure that at least two mesh objects are assigned to element groups.')       
                    print('Nothing done.')
                    return 1

            ###### No selected input found   
            else:
                print('Please select at least two mesh objects to connect. Note that these objects')
                print('also need rigid body set enabled, preprocessing tools can be used to do this.')       
                print('Nothing done.')
                return 1     
       
        ##########################################     
        ###### Update already existing constraints
        if "bcb_valid" in scene.keys() or props.asciiExport:
            
            ###### Store menu config data in scene
            storeConfigDataInScene(scene)
            ###### Get temp data from scene
            if not props.asciiExport:
                objs, emptyObjs, childObjs, connectsPair, connectsPairParent, connectsLoc, connectsGeo, connectsConsts, connectsTol, constsConnect = getBuildDataFromScene(scene)
            ###### Create fresh element group index to make sure the data is still valid (reordering in menu invalidates it for instance)
            objsEGrp, objCntInEGrps = createElementGroupIndex(objs)
            ###### Store updated build data in scene
            storeBuildDataInScene(scene, None, objsEGrp, None, None, None, None, None, None, None, None, None)
                            
            if len(emptyObjs) > 0 and objCntInEGrps > 1:
                ###### Set general rigid body world settings
                initGeneralRigidBodyWorldSettings(scene)
                ###### Calculate mass for all mesh objects
                calculateMass(scene, objs, objsEGrp, childObjs)
                ###### Correct bbox based contact area by volume
                correctContactAreaByVolume(objs, objsEGrp, connectsPair, connectsGeo)
                ###### Find and activate first layer with constraint empty object (required to set constraint locations in setConstraintSettings())
                if not props.asciiExport: layersBak = backupLayerSettingsAndActivateNextLayerWithObj(scene, emptyObjs[0])
                ###### Set constraint settings
                connectsTol, exData = setConstraintSettings(objs, objsEGrp, emptyObjs, connectsPair, connectsLoc, connectsGeo, connectsConsts, constsConnect)
                ###### Store new build data in scene
                storeBuildDataInScene(scene, None, None, emptyObjs, None, None, None, None, None, None, connectsTol, None)
                ### Restore old layers state
                if not props.asciiExport:
                    scene.update()  # Required to update empty locations before layer switching
                    scene.layers = [bool(q) for q in layersBak]  # Convert array into boolean (required by layers)
                ###### Exporting data into internal ASCII text file
                if props.asciiExport and exData != None: exportDataToText(exData)
            
                if props.asciiExport:
                    # Removing flag for valid data for asciiExport & FM export
                    try: del scene["bcb_valid"]
                    except: pass
                else:
                    # Deselect all objects
                    bpy.ops.object.select_all(action='DESELECT')
                    # Select all new constraint empties
                    for emptyObj in emptyObjs:
                        try: emptyObj.select = 1
                        except: pass
                
                print('-- Time total: %0.2f s\n' %(time.time()-time_start))
                print('Constraints:', len(emptyObjs), '| Elements:', len(objs), '| Children:', len(childObjs))
                print('Done.')
                return 0

            ###### No input found   
            else:
                print('Neither mesh objects to connect nor constraint empties for updating selected.')       
                print('Nothing done.')
                return 1
                     
    ###### No RigidBodyWorld group found   
    else:
        print('No "RigidBodyWorld" group found in scene. Please create rigid bodies first.')       
        print('Nothing done.')       
        return 1
        