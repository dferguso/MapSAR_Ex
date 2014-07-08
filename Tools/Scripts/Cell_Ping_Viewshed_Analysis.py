#-------------------------------------------------------------------------------
# Name:        ProcessCellPings
# Purpose:     Create viewshed from each ping location along with date/time of event
#              and clip to travel routes such as roads, trails, waterways etc.
# Author:      Jon Pedder
#
# Created:     04/29/2013
# Copyright:   (c) SMSR 2013
# Licence:
#     MapSAR wilderness search and rescue GIS data model and related python scripting
#     Copyright (C) 2012  - Jon Pedder & SMSR
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

# Import system modules
import arcpy, datetime, os
import time
from arcpy import env
from arcpy.sa import *

# Set enviroment, frames and layers
arcpy.env.workspace
arcpy.env.scratchGDB

scratchdb = arcpy.env.scratchGDB
defaultDB = arcpy.env.workspace
arcpy.env.overwriteOutput = True

templatePath = '{0}\{1}'.format(os.getcwd(),'Layer_Templates')

# Assure Scratch DB has been written to disk
time.sleep(2)

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT')
        #mxd = arcpy.mapping.MapDocument(r"C:\Users\SMSR\Desktop\MapSAR_Dev\Current_Dev\2013_03_22_Harry_Donn\MapSAR_Basic.mxd")
        frame = arcpy.mapping.ListDataFrames(mxd,'MapSAR')[0]

        return(mxd,frame)

    except SystemExit as err:
            pass

def processSinglePing():
    pass

def getPingRange(strValues):
    """ Parser which returns a list of single digit values for input of string separated by commas or dashes """
    try:
        getdash = []
        pingrange = []
        splitValues = strValues.split(',')
        # Split string to list with comma delimiter
        for i in splitValues[:]:
            # If a dash, then expand the range
            if '-' in i:
                getdash = (i.split('-'))
                pingrange.extend(range(int(getdash[0]),int(getdash[1])+1,1))
            # If no dash, just add the value as an int()
            else:
                pingrange.append(int(i))

        # Remove duplicate values in the list
        if pingrange:
            pingrange.sort()
            last = pingrange[-1]
            for d in range(len(pingrange)-2,-1,-1):
                if last == pingrange[d]:
                    del pingrange[d]
                else:
                    last = pingrange[d]
        # Return a list of unique values
        return(pingrange)

    except SystemExit as err:
            pass

def consolidatePoints(selectTowers,pingRange):
    """consolidatePoints(selectTowers,pingRange,PLS) selectTowers = ALL or SELECTED, pingRange, PLS = true or false """
    try:
        throwError = False
        pingDict = {}

        mxd, frame = getDataframe()

        # Create and process on scratchdb copy of cell pings and add layer to frame
        original_cell_pings = '{0}\Cell_Pings'.format(defaultDB)
        scratch_cell_pings = '{0}\Scratch_Cell_Pings'.format(scratchdb)
        working_cell_pings = arcpy.Copy_management(original_cell_pings,scratch_cell_pings,'#')

        cellLayer = arcpy.MakeFeatureLayer_management(working_cell_pings,'Scratch_Cell_Pings.lyr')
        refGroupHidden = arcpy.mapping.ListLayers(mxd,'*Hidden_Layers_Admin*',frame)[0]
        arcpy.mapping.AddLayerToGroup(frame,refGroupHidden,cellLayer.getOutput(0),'BOTTOM')

        # If selectTowers is SELECTION break out the selected records
        rows = arcpy.UpdateCursor(working_cell_pings)
        for row in rows:
            if row.getValue('Ping_Number') not in pingRange and 'SELECTION' in selectTowers:
                rows.deleteRow(row)
            elif 'ALL' in selectTowers or row.getValue('Ping_Number') in pingRange:
                # Loop through all pings and add values to dictionary
                if row.getValue('Ping_Number') == None:
                    throwError = True
                    break
                elif row.getValue('Date') == None:
                    throwError = True
                    break
                else:
                    pingDict[row.getValue('Ping_Number')] = [row.getValue('Date'),row.getValue('Description')]

        if throwError == True:
            arcpy.AddError('Cell Ping Records have missing PING_NUMBERS or DATE values\nPlease assign each entry a unique ping_number and date time value.\n')
            raise SystemExit(throwError)

        inputfeatures = ['PLS',working_cell_pings]
        allpoints = arcpy.Merge_management(inputfeatures,'{0}/allpoints'.format(scratchdb))
        featureCount = int(arcpy.GetCount_management(allpoints).getOutput(0))

        return(allpoints,featureCount,pingDict,working_cell_pings)

    except SystemExit as err:
            pass

def createBuffer(inRaster,allpoints,featureCount,bufferArea,bufferDistance,bufferUnit):
    """ Creates a buffered area around cell towers and PLS to clip raster to"""
    try:
        mxd, frame = getDataframe()
        buffDist = ''

        if 'Maximum' in bufferArea:
            dem_area = arcpy.RasterDomain_3d(inRaster,'{0}/coverage_area'.format(scratchdb), "POLYGON")
            coverage_area = arcpy.Buffer_analysis(dem_area,'{0}/buffered_coverage_area'.format(scratchdb),'-50 Meters','FULL', '', 'ALL', '')
            buffered_area = arcpy.Buffer_analysis(coverage_area,'{0}/buffered_coverage_area'.format(scratchdb),'20 Meters','FULL', '', 'ALL', '')
        else:
            # If manually entered
            if 'Enter Buffer Distance' in bufferArea:
                if 'Miles' in bufferUnit:
                    coverDist = '{0} {1}'.format(float(bufferDistance),'Miles')
                    buffDist = '{0} {1}'.format(float(coverDist)+0.1,'Miles')
                elif 'Kilometers' in bufferUnit:
                    coverDist = '{0} {1}'.format(float(bufferDistance),'Kilometers')
                    buffDist = '{0} {1}'.format(float(coverDist)+0.1,'Kilometers')
                elif 'Meters' in bufferUnit:
                    coverDist = '{0} {1}'.format(float(bufferDistance),'Meters')
                    buffDist = '{0} {1}'.format(float(coverDist)+50,'Meters')

            # Single tower plus pls
            if featureCount < 2:

                # processSinglePing()

                arcpy.AddError('Houston we have a problem, only a single feature was found in the allpoints FC')
                raise SystemExit(2)
            elif featureCount == 2:
                if 'Enter Buffer Distance' not in bufferArea:
                    mindist, avgdist, maxdist = arcpy.CalculateDistanceBand_stats(allpoints, featureCount-1, "EUCLIDEAN_DISTANCE")
                    # get distances between towers
                    if 'Minimum' in bufferArea:
                        coverDist = '{0} {1}'.format(float(str(mindist)) * 1.2,'Meters')
                        buffDist = '{0} {1}'.format(float(coverDist.partition(' ')[0])+50,'Meters')
                    elif 'Medium' in bufferArea:
                        coverDist = '{0} {1}'.format(float(str(avgdist)) * 1.4,'Meters')
                        buffDist = '{0} {1}'.format(float(coverDist.partition(' ')[0])+50,'Meters')
                    elif 'Large' in bufferArea:
                        coverDist = '{0} {1}'.format(float(str(maxdist)) * 1.6,'Meters')
                        buffDist = '{0} {1}'.format(float(coverDist.partition(' ')[0])+50,'Meters')

                coverage_area = arcpy.Buffer_analysis(allpoints,'{0}/coverage_area'.format(scratchdb), coverDist,'FULL', '', 'ALL', '')
                buffered_area = arcpy.Buffer_analysis(coverage_area,'{0}/buffered_coverage_area'.format(scratchdb), buffDist,'FULL', '', 'ALL', '')

            elif featureCount > 2:
                if 'Enter Buffer Distance' not in bufferArea:
                    mindist, avgdist, maxdist = arcpy.CalculateDistanceBand_stats(allpoints, featureCount-1, "EUCLIDEAN_DISTANCE")
                    # get distances between towers
                    if 'Minimum' in bufferArea:
                        buffDist = '{0} {1}'.format(float(str(mindist)) * 1.1,'Meters')
                    elif 'Medium' in bufferArea:
                        buffDist = '{0} {1}'.format(float(str(avgdist)) * 1.2,'Meters')
                    elif 'Large' in bufferArea:
                        buffDist = '{0} {1}'.format(float(str(maxdist)) * 1.3,'Meters')

                coverage_area = arcpy.MinimumBoundingGeometry_management(allpoints,'{0}/coverage_area'.format(scratchdb))
                buffered_area = arcpy.Buffer_analysis(coverage_area,'{0}/buffered_coverage_area'.format(scratchdb),buffDist,'FULL', '', 'ALL', '')

        # Add fields to FC which will be populated by the spatial join
        arcpy.AddField_management(buffered_area, 'Ping_Number', "SHORT", 0, "", "", "Ping Number", "NULLABLE", "NON_REQUIRED")
        arcpy.AddField_management(buffered_area, 'Date', "DATE", 0, "", "", "Date", "NULLABLE", "NON_REQUIRED")
        arcpy.AddField_management(buffered_area, 'Description', "TEXT", 0, "", "250", "Description", "NULLABLE", "NON_REQUIRED")

        # Add coverage layer to frame
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Hidden_Layers*',frame)[0]

        coverage_area_name = 'coverage_area_lyr_footprint_{0}'.format(timestamp)
        coverage_tempLayer = arcpy.MakeFeatureLayer_management(coverage_area,coverage_area_name)
        arcpy.mapping.AddLayerToGroup(frame,refGroupLayer,coverage_tempLayer.getOutput(0),'BOTTOM')

        coveragelayer = arcpy.mapping.ListLayers(mxd,coverage_area_name,frame)[0]
        coveragelayer.visible = False

        return(buffered_area,coveragelayer)

    except SystemExit as err:
            pass

def clipRaster(inRaster, buffered_area):
    """ Clip the raster for faster processing """
    try:
        mxd, frame = getDataframe()

        # Clip the DEM raster to the size of the Buffered_Area
        clipped_raster = arcpy.Clip_management(inRaster,'#','{0}\clipped_DEM_raster'.format(scratchdb),buffered_area,'0', 'ClippingGeometry')

        # Set any nodata values to zero
        clipped_raster_con = Con(IsNull(clipped_raster), 0, clipped_raster)

        # Add layers to map and check if DEM covers coverage area
        DEMfootprint = arcpy.RasterDomain_3d(clipped_raster_con,'{0}\Clipped_DEM_Raster_Footprint'.format(scratchdb), "POLYGON")

        return(DEMfootprint,clipped_raster_con)

    except SystemExit as err:
            pass

def testCoverage(coveragelayer,DEMfootprint):
    try:
         # Test that the DEM covers the minimum required veiwshed area, coverage_area
        arcpy.SelectLayerByLocation_management (coveragelayer,"WITHIN",DEMfootprint,'#',"NEW_SELECTION")
        resultCount = arcpy.GetCount_management(coveragelayer)

        featureCount = int(resultCount.getOutput(0))
        if featureCount == 0:
            arcpy.AddError('Test completed: Cell towers and PLS do NOT fit within the selected Raster (DEM, Elevation)\nPlease load a raster that fits the area.\nJoin multiple Rasters using the Mosiac Tool\n')
            raise SystemExit(2)
        elif featureCount == 1:
            arcpy.AddMessage('Test completed: The DEM file does cover the required viewshed area\nProceeding with Viewshed analysis\n')

        return(featureCount)

    except SystemExit as err:
            pass

def checkSR(inRaster,clipped_raster):
    """ Check to see if the raster is GCS or PCS, if GCS it's converted """
    try:
        mxd, frame = getDataframe()

        # Check to see if DEM is projected or geographic
        sr = arcpy.Describe(inRaster).spatialreference
        if sr.PCSName == '':
        # if geographic throw an error and convert to projected to match the dataframe
            inSR = frame.spatialReference
            inPCSName = frame.spatialReference.PCSName
            arcpy.AddWarning('This elevation file (DEM) is NOT projected. Converting DEM to {0}\n'.format(inPCSName))
            clipped_raster = arcpy.ProjectRaster_management(clipped_raster, "{0}\clipped_DEM_raster_{1}".format(scratchdb,inPCSName),inSR, "BILINEAR", "#","#", "#", "#")

        return(clipped_raster)

    except SystemExit as err:
            pass

def createPingData(working_cell_pings,buffered_area,pingDict):
    # Create a FC buffered area for each cell ping and populate with dictionary data
    # Will be used with the spatial join to populate date and ping number
    try:
        # PLS record will have no ping data
        featureView_Dict = {}

        currPing = arcpy.SearchCursor(working_cell_pings)
        for p in currPing:
            pingNum = p.getValue('Ping_Number')
            # Duplicate buffered area for each ping
            featureView = '{0}/Feature_join_area_ping_{1}'.format(scratchdb,pingNum)
            arcpy.CopyFeatures_management(buffered_area,featureView)

            # Populate dictionary of pings and the path to the feature for use with spatial join
            featureView_Dict[pingNum] = featureView

            currView = arcpy.UpdateCursor(featureView)
            # Populate values from dict to all features
            for f in currView:
                f.Ping_Number = pingNum
                f.Date = pingDict[pingNum][0]
                f.Description = pingDict[pingNum][1]
                currView.updateRow(f)
            del currView
        return(featureView_Dict)

    except SystemExit as err:
            pass

def createTowerViewshed(clipped_raster,inAGL,working_cell_pings,featureView_Dict):
    """ Create a viewshed for each tower location """
    try:
        mxd, frame = getDataframe()
        CellLyr = arcpy.mapping.ListLayers(mxd,'*Scratch_Cell_Pings.lyr*',frame)[0]
        # Set defaut variable values for viewshed

        zFactor = 1
        useEarthCurvature = "FLAT_EARTH"
        refractivityCoefficient = 0.13

        if arcpy.CheckOutExtension('Spatial'):
            # Initialize counters and list for next section of processing
            featurelist = []
            iCount = 0

            # Loop through each feature in the FC
            pingField = arcpy.AddFieldDelimiters(CellLyr,"Ping_Number")

            currPing = arcpy.SearchCursor(CellLyr)
            for cp in currPing:
                current_ping = cp.getValue('Ping_Number')
                arcpy.AddMessage('Processing Viewshed for Cell Ping {0}'.format(current_ping))

                # Make a new selection for each record
                cQuery = '{0} = {1}'.format(pingField,current_ping)
                arcpy.SelectLayerByAttribute_management(CellLyr,'NEW_SELECTION',cQuery)

                # Create a raster viewshed for each cell pings
                if inAGL:
                    outViewshed = Viewshed(clipped_raster, CellLyr, zFactor, useEarthCurvature, refractivityCoefficient,inAGL)
                else:
                    outViewshed = Viewshed(clipped_raster, CellLyr, zFactor, useEarthCurvature, refractivityCoefficient)

                Raster_Viewshed_Ping ='{0}\Raster_Viewshed_Ping{1}'.format(scratchdb,current_ping)
                outViewshed.save(Raster_Viewshed_Ping)

                # Remove zero values
                conView = Con(Raster(Raster_Viewshed_Ping),Raster(Raster_Viewshed_Ping) , "", "VALUE > 0")
                conView.save(Raster_Viewshed_Ping)


                # Turn each raster ping into a feature ping viewshed
                Feature_Viewshed_Ping = '{0}\Feature_Viewshed_Ping{1}'.format(scratchdb,current_ping)
                arcpy.RasterToPolygon_conversion(Raster_Viewshed_Ping,Feature_Viewshed_Ping, 'SIMPLIFY', 'Value')

##                # Remove non visable data
##                arcpy.AddMessage('Removing Zero Values')
##                Feature_Viewshed_Ping = removeZeroRows(Feature_Viewshed_Ping)

                # Add each feature created to a list for use with Merge tool
                Spatial_Join_Feature = '{0}\Spatial_Joined_Feature_ping{1}'.format(scratchdb,current_ping)
                featurelist.append(Spatial_Join_Feature)

                # Setup field mappings to pull in data from the feature_viewshed
                refItem = featureView_Dict[current_ping]
                fieldmappings = arcpy.FieldMappings()
                fieldmappings.addTable(Feature_Viewshed_Ping)
                fieldmappings.addTable(refItem)

                # Perform spatial join to populate the value data from the buffered_feature
                arcpy.SpatialJoin_analysis(Feature_Viewshed_Ping,refItem, Spatial_Join_Feature, "#", "#", fieldmappings)


        return(featurelist)

    except SystemExit as err:
            pass

def mergeViewsheds(featurelist):
    """ Merge the viewsheds and add back the ping data """
    try:
        arcpy.AddMessage('\nVerifying Viewsheds and creating layers\n')

        merged_features = '{0}\Merged_detailed_FC{1}'.format(scratchdb,timestamp)
        arcpy.Merge_management(featurelist,merged_features)

##        merged_features = removeZeroRows(merged_features)

# Removed Dissolve function as it blows up with large datasets. ArcMap bug,
##        # Consolidate the features using dissolve
##        dissolveFields = ['Date','Ping_Number','gridcode']
##        dissolved_feature = '{0}\Cell_Ping_Viewshed_{1}'.format(defaultDB,timestamp)
##
##        arcpy.AddMessage('\nDissolving features\n')
##        arcpy.Dissolve_management(merged_features, dissolved_feature,dissolveFields, "", "MULTI_PART", "DISSOLVE_LINES")
##
##        dissolved_feature = removeZeroRows(dissolved_feature)

        return(merged_features)

    except SystemExit as err:
            pass


def removeZeroRows(feature):
    """ remove zero grid values"""
    # Remove zero values to work with transportation clip
    rows = arcpy.UpdateCursor(feature)
    for row in rows:
        if row.getValue('grid_code') == 0:
            rows.deleteRow(row)

    return(feature)

    del rows


def displayViewshed(dissolved_feature):
    # Lastly add the viewshed featureclass to the analysis group
    try:
        mxd, frame = getDataframe()
        tempLayer = arcpy.MakeFeatureLayer_management(dissolved_feature,'{0}\Cell_Ping_Viewshed_{1}'.format(templatePath,timestamp))

        arcpy.AddMessage('Adding The Completed Viewshed To The Map\n{0}\n'.format('Cell_Ping_Viewshed_{0}'.format(timestamp)))

        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',frame)[0]
        refGroupLayer.visible = True

        arcpy.mapping.AddLayerToGroup(frame,refGroupLayer,tempLayer.getOutput(0),'BOTTOM')

        lyr = arcpy.mapping.ListLayers(mxd,'*Cell_Ping_Viewshed_{0}*'.format(timestamp),frame)[0]
        lyr.name = 'Cell_Ping_Viewshed_{0}'.format(timestamp)

        if os.path.exists(templatePath):
            arcpy.ApplySymbologyFromLayer_management(lyr, '{0}\Cell_Symbology_Template.lyr'.format(templatePath))

        lyr.visible = True
        lyr.transparency = 40
        for l in lyr.labelClasses:
            l.expression = '"Visible by ping # "& [Ping_Number] &" at "& [Date]'
        lyr.showLabels = False

        # Refresh view of TOC and view
        frame.extent = lyr.getExtent()
        arcpy.RefreshTOC()
        arcpy.RefreshActiveView()

    except SystemExit as err:
            pass


# Function to clip travel routes to cell ping viewshed and populate with ping data
def clipTravelRoutes(featureIn,dissolved_feature):
    """ Feataureclass to clip: featureIn, dissolved_feature
    Clip travel routes to viewsheds and populate with date and ping number data from viewshed """
    try:
        mxd, frame = getDataframe()

        # Clean input for clear naming
        featureSplit = featureIn.split('\\')
        featurename = featureSplit[len(featureSplit)-1]
        arcpy.AddMessage('Processing Travel Route {0} against Viewshed\n'.format(featurename))

        # Clip travel routes to viewshed
        travel_route_name = '{0}\Travel_Route_{1}_ClippedToViewShed_{2}'.format(scratchdb,timestamp,featurename)
        featureIn_clipped = arcpy.Clip_analysis(featureIn,dissolved_feature,travel_route_name)

        # Setup field mappings to pull in data from the dissolved_feature
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(featureIn_clipped)
        fieldmappings.addTable(dissolved_feature)

        # Perform spatial join to populate the value data from the buffered_feature
        travel_join_name = '{0}\{1}_cellpings_{2}'.format(defaultDB,featurename,timestamp)
        arcpy.SpatialJoin_analysis(featureIn_clipped,dissolved_feature,travel_join_name, "#", "#", fieldmappings)

        # Add layer to map and position
        travel_layer_name = '{0}_cellping_Layer_{1}'.format(featurename,timestamp)
        tempLayer = arcpy.MakeFeatureLayer_management(travel_join_name,travel_layer_name)

        frame = arcpy.mapping.ListDataFrames(mxd,'MapSAR')[0]
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',frame)[0]
        arcpy.mapping.AddLayerToGroup(frame,refGroupLayer,tempLayer.getOutput(0),'BOTTOM')

        if os.path.exists(templatePath):
            lyr = arcpy.mapping.ListLayers(mxd,'*cellping_Layer_{0}*'.format(timestamp),frame)[0]
            if '1' in featureIn:
                arcpy.ApplySymbologyFromLayer_management(lyr, '{0}\Route_Symbology_Template1.lyr'.format(templatePath))
            elif '1' in featureIn:
                arcpy.ApplySymbologyFromLayer_management(lyr, '{0}\Route_Symbology_Template2.lyr'.format(templatePath))
            elif '1' in featureIn:
                arcpy.ApplySymbologyFromLayer_management(lyr, '{0}\Route_Symbology_Template3.lyr'.format(templatePath))

    except SystemExit as err:
            pass

# Get user input parameters
inRaster = arcpy.GetParameterAsText(0)
inAGL = arcpy.GetParameterAsText(1)
selectTowers = arcpy.GetParameterAsText(2)
selectedTowers = arcpy.GetParameterAsText(3)
bufferArea = arcpy.GetParameterAsText(4)
bufferDistance = arcpy.GetParameterAsText(5)
bufferUnit = arcpy.GetParameterAsText(6)
travel_route_1 = arcpy.GetParameterAsText(7)
travel_route_2 = arcpy.GetParameterAsText(8)
travel_route_3 = arcpy.GetParameterAsText(9)

# Set date and time vars
now = datetime.datetime.now()
todaydate = now.strftime("%m_%d")
todaytime = now.strftime("%H_%M_%p")
timestamp = '{0}_{1}'.format(todaydate,todaytime)

def main():
    """ Process pings from cell tower locations and PLS"""
    # Select points to work with in a single FC
    arcpy.AddMessage('\nCreating Workspace for Cell Ping Analysis\n')
    allpoints, featureCount, pingDict, working_cell_pings = consolidatePoints(selectTowers,pingRange)

    # Create a buffered area around cell towers and PLS
    buffered_area,coveragelayer = createBuffer(inRaster,allpoints,featureCount,bufferArea,bufferDistance,bufferUnit)

    # Clip the raster to the buffered area size
    DEMfootprint,clipped_raster = clipRaster(inRaster,buffered_area)

    # Test to see if towers fit within the Raster foorptint. 0 = no, 1 = yes
    arcpy.AddMessage('Testing That Tower Locations Fit Within The Workspace\n')
    if 'Enter Buffer Distance' not in bufferArea:
        featureCount = testCoverage(coveragelayer,DEMfootprint)
    else:
        resultCount = arcpy.GetCount_management(coveragelayer)
        featureCount = int(resultCount.getOutput(0))

    # Check to see if the raster is GCS or PCS, if GCS it's converted
    arcpy.AddMessage('Checking The DEM Rasters Extent and Spatial Reference\n')
    clipped_raster = checkSR(inRaster,clipped_raster)

    # Add tower values to new FC for each ping
    featureView_Dict = createPingData(working_cell_pings,buffered_area,pingDict)

    # Create viewsheds from each tower
    arcpy.AddMessage('Creating Viewsheds For Each Selected Tower\n')
    featurelist = createTowerViewshed(clipped_raster,inAGL,working_cell_pings,featureView_Dict)

    # Create a merged featureclass containing viewsheds and their related data
    dissolved_feature = mergeViewsheds(featurelist)

    # Clip travel routes to viewshed and add layers to map
    if travel_route_1:
        clipTravelRoutes(travel_route_1,dissolved_feature)

    if travel_route_2:
        clipTravelRoutes(travel_route_2,dissolved_feature)

    if travel_route_3:
        clipTravelRoutes(travel_route_3,dissolved_feature)

    # Add Viewshed layers to frame
    # displayViewshed(dissolved_feature)
    displayViewshed(dissolved_feature)

    # Clear temp feature layers
    arcpy.AddMessage('Performing Housekeeping duties\n')
    mxd, frame = getDataframe()
    lyrs = arcpy.mapping.ListLayers(mxd,'*',frame)
    for lyr in lyrs:
        if 'Scratch_Cell_Pings' in lyr.name:
            arcpy.mapping.RemoveLayer(frame,lyr)
        if 'coverage_area_lyr_footprint' in lyr.name:
            arcpy.mapping.RemoveLayer(frame,lyr)

# Main event
if __name__ == '__main__':

    # Check for valid entries before executing script
    FC_pings = [row[0] for row in arcpy.da.SearchCursor('Cell_Pings', ("Ping_Number"))]

    pingRange = []
    errors = []
    isError = False
    if 'SELECTION' in selectTowers:
        pingRange = getPingRange(selectedTowers)
        if len(pingRange) > 0:
            for i in pingRange:
                if i not in FC_pings:
                    errors.append(i)
            if len(errors) > 0:
                isError = True
                arcpy.AddError('\nCell Pings {0} Are Not Valid Selections\n'.format(errors))
                raise SystemExit(2)
        elif len(pingRange) == 0:
            isError = True
            arcpy.AddError('\nThere Are No Cell Tower Values Entered\n')
            raise SystemExit(2)
    elif 'ALL' in selectTowers:
        pingRange = FC_pings
        if len(pingRange) == 0:
            isError = True
            arcpy.AddError('\nThere are no Cell Towers to Process\n')
            raise SystemExit(2)
    else:
        isError = True
        arcpy.AddError('\nThere are no Cell Towers to Process\n')
        raise SystemExit(2)

    if isError == False:
        try:
            main()
        except SystemExit as err:
            pass

