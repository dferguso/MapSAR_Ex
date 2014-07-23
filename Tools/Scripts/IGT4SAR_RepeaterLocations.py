'''
-------------------------------------------------------------------------------
Name:        IGT4SAR_RepeaterLocations.py

Purpose:  Estimate potential locations for radio repeaters to provide coverage
of a pre-defined area based on either a random distribution or user defined
locations of "Observers" (radios in the field).  Radio coverage is estimated
using "Line-of-Sight" analysis based on digital elevation model (DEM) and
antenna heights of the transmit and receive units.  This analysis uses the
Spatial Analyst - Observer Points Tool.  This tool performs the Viewshed
analysis in reverse by considering the locations of "Observers" in the field and
highlighting locations that are visible from each raster surface location.  The
user has the option of using pre-defined points (preferably not more than 10) or
allowing the computer to pick 10 random points within the user prescribed area
(extent).  Locations across the raster are identified that can see the "Observer
Points" are a graded on how many points are visible from that location.  The
points that are visible from a location, the higher the grade.  Graded areas are
converted to polygons and
Various points are defined within the area either
by the using or using the Random Points Generator tool.  The Observer points
tool is than used to predict locations that has a "view" of the maximum number
of points.

Author:      Don Ferguson

Created:     07/12/2014
Copyright:   (c) Don Ferguson 2014
Licence:
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

The GNU General Public License can be found at
<http://www.gnu.org/licenses/>.
-------------------------------------------------------------------------------
'''

# Import arcpy module
import arcpy, sys, arcgisscripting, os
import arcpy.mapping
from arcpy import env
from arcpy.sa import *

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

######### Modules modified from from Jon Pedder - MapSAR #########################
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def checkSR(inRaster):   #From Jon Peddar - MapSAR
    """ Check to see if the raster is GCS or PCS, if GCS it's converted """
    try:
        mxd, frame = getDataframe()

        # Check to see if DEM is projected or geographic
        sr = arcpy.Describe(inRaster).spatialreference
        if sr.PCSName == '':   # if geographic throw an error and convert to projected to match the dataframe
            inSR = frame.spatialReference
            inPCSName = frame.spatialReference.PCSName
            arcpy.AddWarning('This elevation file (DEM) is NOT projected. Converting DEM to {0}\n'.format(inPCSName))
            inRaster = arcpy.ProjectRaster_management(inRaster, "{0}\DEM_{1}".format(scratchdb,inPCSName),inSR, "BILINEAR", "#","#", "#", "#")

        return(inRaster)

    except SystemExit as err:
            pass

def AddViewFields(obsvrPts, antHeight, rad2):
    obsvrName=[]
    fldNames=[('DESCRIPTION','TEXT'),('OFFSETA', 'SHORT'),('OFFSETB', 'SHORT'), \
              ('AZIMUTH1', 'SHORT'),('AZIMUTH2', 'SHORT'),('VERT1', 'SHORT'), \
              ('VERT2', 'SHORT'),('RADIUS1', 'SHORT'),('RADIUS2', 'SHORT')]
    fName=[fldNames[k][0] for k in range(9)]
    if int(arcpy.GetCount_management(obsvrPts).getOutput(0)) > 0:
        fieldnames = [f.name for f in arcpy.ListFields(obsvrPts)]
        if "OID" in fieldnames:
            OID="OID"
        elif "OBJECTID" in fieldnames:
            OID="OBJECTID"
        else:
            OID=None
        compList=set(fieldnames).intersection(fName)
        compList=list(compList); chkList=list(fName)
        [chkList.remove(kk) for kk in compList]

        #Default values for Observer Points
        obsvrDef=[antHeight,2,0,360,90,-90,0,rad2]
        #Add field if it does not exist
        for field in fldNames:
            if field[0] in chkList:
                arcpy.AddField_management(*(obsvrPts,) + field)

        cursor=arcpy.UpdateCursor(obsvrPts)
        cnt=1
        for row in cursor:
            if OID:
                descp="ObsvrPt_{0}".format(row.getValue(OID))
            else:
                descp="ObsvrPt_{0}".format(row.getValue(cnt))
            obsvrName.append(descp)
            cnt+=1

            if row.getValue(fName[0]) is None:
                row.setValue(fName[0], descp)
            ct=0
            for k in fName[1:9]:
                if row.getValue(k) is None:
                    row.setValue(k, obsvrDef[ct])
                ct+=1
            cursor.updateRow(row)
        del fieldnames, cursor, row, ct, cnt, compList, descp, field
    del fName, fldNames
    return()


def RandomPts(outName, wrkspc, fcExtent, numPoints=10):
    #Creates random points throughout fcExtent
    obsvrName=[]
    minDistance = "100 Meters"
    arcpy.CreateRandomPoints_management(wrkspc, outName, fcExtent, "", numPoints, minDistance)
    return()

def enterXY(fcName):
    inRows = arcpy.SearchCursor(outName)
    # Open insertcursor
    #
    outRows = arcpy.InsertCursor(outPts)
    for inRow in inRows: # One output feature for each input point feature
        inShape = inRow.shape
        pnt = inShape.getPart(0)
        feat = outRows.newRow()
        feat.shape = pnt
        # Insert the feature
        #
        outRows.insertRow(feat)
    return()

def deleteFeature(fcList):
    for gg in fcList:
        if arcpy.Exists(gg):
            try:
                arcpy.Delete_management(wrkspc + '\\' + gg)
            except:
                pass

    return()

def deleteLayer(df,fcLayer):
    for lyr in fcLayer:
        for ii in arcpy.mapping.ListLayers(mxd, lyr):
            try:
                print "Deleting layer", ii
                arcpy.mapping.RemoveLayer(df , ii)
            except:
                pass
    return()


def RepeaterAreas(RptrPoly_Lyr,DEM, nList, df):
    DEM_Clip="DEM_{0}".format(nList[0])
    ElevPt="Rpt_{0}".format(nList[0])
    DEM_Max="DEMmax_{0}".format(nList[0])

    express02 = '"DESCRIPTION" = \'{0}\''.format(nList[0])
    arcpy.AddMessage(express02)

    arcpy.SelectLayerByAttribute_management(RptrPoly_Lyr, "NEW_SELECTION", express02)

    arcpy.Clip_management(DEM, "#",DEM_Clip ,RptrPoly_Lyr, "", "ClippingGeometry")

    arcpy.SelectLayerByAttribute_management(RptrPoly_Lyr,"CLEAR_SELECTION")

    demMax=arcpy.GetRasterProperties_management (DEM_Clip, "MAXIMUM")
    cPtChk=0
    rdNum = 2
    field='Value'
    while cPtChk<1:
        if rdNum>=0:
            demMax2 = int(float(demMax.getOutput(0))*(10.0**rdNum))/(10**rdNum)
        elif rdNum==-1:
            demMax2 = int(float(demMax.getOutput(0)))-1
        else:
            arcpy.AddError('Problem with your DEM')
            break

        OutRas=Con((Raster(DEM_Clip) > demMax2),1)
        OutRas.save(DEM_Max)
        del OutRas
        deleteFeature([DEM_Clip])
        try:
            cDemMax=arcpy.GetRasterProperties_management (DEM_Max, "MAXIMUM")
            arcpy.RasterToPoint_conversion(DEM_Max,ElevPt,field)
            deleteFeature([DEM_Max])
            cPtChk001=arcpy.GetCount_management(ElevPt)
            cPtChk = int(cPtChk001.getOutput(0))
            del cPtChk001
        except:
            cPtChk = 0
        arcpy.AddMessage("Maximum of DEM in this region is: {0} m\n".format(demMax2))
        rdNum-=1

    nList=[]
    cursor = arcpy.SearchCursor(ElevPt)
    for row in cursor:
        nList.append(row.getValue('OBJECTID'))
    nList.sort

    if len(nList)>1:
        ElevPt_Lyr = arcpy.mapping.Layer(ElevPt)
        arcpy.mapping.AddLayer(df,ElevPt_Lyr,'BOTTOM')
        # If more than one point is generated, delete the extras.
        expression = "OBJECTID > " + str(nList[0])
        arcpy.SelectLayerByAttribute_management(ElevPt_Lyr, "NEW_SELECTION", expression)
        # Execute GetCount and if some features have been selected, then execute
        #  DeleteRows to remove the selected rows.
        arcpy.DeleteRows_management(ElevPt_Lyr)
        deleteLayer(df,[ElevPt_Lyr])

    del demMax, demMax2, cPtChk
    return(ElevPt)

def UpdateSpatialFields(RepeaterLocations,nlist):
    RptrNames = [f.name for f in arcpy.ListFields(RepeaterLocations)]
    if "Descritpion" in RptrNames:
        where01 = "Description = {0}".format(nlist)
    else:
        where01 = ""

    desc=arcpy.Describe(RepeaterLocations)
    shapeFN = desc.ShapeFieldName
    cursor = arcpy.UpdateCursor(RepeaterLocations, where01)
    for row in cursor:
        feat=row.getValue(shapeFN)
        pnt=feat.getPart()
        if 'UTM_Easting' in RptrNames:
            row.setValue('UTM_Easting',int(pnt.X))
        if 'UTM_Northing' in RptrNames:
            row.setValue('UTM_Northing',int(pnt.Y))
        cursor.updateRow(row)
    try:
        del cursor, row, desc, shapeFN
    except:
        pass
    return()

    desc=arcpy.Describe(RepeaterLocations)
    shapeFN = desc.ShapeFieldName
    cursor = arcpy.UpdateCursor(RepeaterLocations, where01, \
                        r'GEOGCS["GCS_WGS_1984",' + \
                        'DATUM["D_WGS_1984",' + \
                        'SPHEROID["WGS_1984",6378137,298.257223563]],' + \
                        'PRIMEM["Greenwich",0],' + \
                        'UNIT["Degree",0.017453292519943295]]')
    for row in cursor:
        feat=row.getValue(shapeFN)
        pnt=feat.getPart()
        if 'LATITUDE' in RptrNames:
            row.setValue('LATITUDE',float(pnt.Y))
        if 'LONGITUDE' in RptrNames:
            row.setValue('LONGITUDE',float(pnt.X))
        cursor.updateRow(row)
    del cursor, row, desc, shapeFN

    return()

def RepeaterViewshed(RptrPts_Lyr, DEM, nList,refGroupLayer, df, mxd):
    # Set layer that output symbology will be based on

    expression = "DESCRIPTION = '{0}'".format(nList)
    arcpy.SelectLayerByAttribute_management(RptrPts_Lyr, "NEW_SELECTION", expression)

    # Set local variables
    zFactor = 1; useEarthCurvature = "CURVED_EARTH"; refractivityCoefficient = 0.15

    # Execute Viewshed
    outViewshed = Viewshed(DEM, RptrPts_Lyr, zFactor, useEarthCurvature, refractivityCoefficient)
    # Save the output
    outViewshed.save(nList)
    arcpy.RefreshCatalog(nList)

    nRstr = nList+'rstr'
    arcpy.MakeRasterLayer_management(Raster(nList), nRstr)
    nList_Lyr = arcpy.mapping.Layer(nRstr)
    nList_Lyr.name=nList
    arcpy.mapping.RemoveLayer(df,nList_Lyr)
##    deleteLayer(df,[nList_Lyr])
    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,nList_Lyr,'BOTTOM')

    try:
        lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
        symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\10 Coverage Area.lyr"
        arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
    except:
        pass

    return()

##########################################

if __name__ == '__main__':
    mxd, df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    fcExtent = arcpy.GetParameterAsText(0)
    if fcExtent == '#' or not fcExtent:
        fcExtent = "Search_Boundary" # provide a default value if unspecified

    UserSelect = arcpy.GetParameterAsText(1)
    if UserSelect == '#' or not UserSelect:
        UserSelect = "System" # provide a default value if unspecified

    inputFeature = arcpy.GetParameterAsText(2)  # If not using System points then define

    DEM2 = arcpy.GetParameterAsText(3)
    if DEM2 == '#' or not DEM2:
        arcpy.AddMessage("You need to provide a valid DEM")

    antHeight = arcpy.GetParameterAsText(4)
    if antHeight == '#' or not antHeight:
        antHeight = 15 # provide a default value if unspecified

    maxDist = arcpy.GetParameterAsText(5) # Desired units
    if maxDist == '#' or not maxDist:
        maxDist = 5000 # provide a default value if unspecified

    arcpy.AddMessage("\n")

    # Variables
    outName = 'ObsvrPts_{0}'.format(timestamp)
    rptrView = 'rptrView'
    rptrArea = 'rptrArea'
    rptrPolys = 'RptrRegions_{0}'.format(timestamp)
    scratchPt = "Scratch_Point"
    RepeaterLocations = 'RptrLocations'
    RptrPts_Lyr = "Repeater Locations (Potential)"
    RptrTemp_Lyr = "RptrTemp_Lyr"
    fcNames=[outName, rptrView,rptrArea,rptrPolys]
    for fcN in fcNames:
        try:
            arcpy.Delete_management(wrkspc + '\\' + fcN)
        except:
            pass

    checkSR(DEM2)
    XCel = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
    XCell = float(XCel.getOutput(0))

    '''
    Check if user is using System values which are Random Points distributed
    throughout the search area, or is user planning to use a User Defined feature
    '''
    refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Communications*',df)[0]

    if UserSelect=="System":
        #Does the Search Boundary exist?
        cSearchArea=arcpy.GetCount_management(fcExtent)
        numPoints = 10
        if int(cSearchArea.getOutput(0)) == 1:
            RandomPts(outName, wrkspc, fcExtent,numPoints)
            obsvrPts= outName
            ObsvrPts_Lyr = arcpy.mapping.Layer(obsvrPts)
            arcpy.mapping.AddLayerToGroup(df,refGroupLayer,ObsvrPts_Lyr,'BOTTOM')

        elif int(cSearchArea.getOutput(0)) < 1:
            arcpy.AddError("You need to specify the Search Area Boundary (8 Segments_Group \ Search Boundary")
        else:
            arcpy.AddError("You need to select a single polygon")

    else:
        obsvrPts = inputFeature
        # Check fields inprep for Observer

    #Check to see if the feature as the appropriate fields
    AddViewFields(obsvrPts, antHeight, maxDist)

    outObsPoints = ObserverPoints(DEM2,obsvrPts, 1, "CURVED_EARTH", 0.13)
    outObsPoints.save(rptrView)

    # Set local variables
    field = "VALUE"
    # Execute RasterToPolygon
    arcpy.RasterToPolygon_conversion(rptrView, rptrPolys, "SIMPLIFY", field)
    deleteFeature([rptrView])
    #deleteFeature([rptrArea])


    # Delete any polygons that have a area smaller than the DEM cell size squared
    shapeArea=1.1*XCell*XCell

    expression = "Shape_Area <= " + str(shapeArea) + "OR gridcode = 0"
    arcpy.AddMessage("Delete regions with Area less than {0} and gridcode = 0 (no pts visible)\n".format(shapeArea))

    arcpy.MakeTableView_management(rptrPolys, RptrTemp_Lyr)

    arcpy.SelectLayerByAttribute_management(RptrTemp_Lyr, "NEW_SELECTION", expression)

    # Execute GetCount and if some features have been selected, then execute
    #  DeleteRows to remove the selected rows.
    if int(arcpy.GetCount_management(RptrTemp_Lyr).getOutput(0)) > 0:
        arcpy.DeleteRows_management(RptrTemp_Lyr)

    deleteLayer(df,[RptrTemp_Lyr])

    arcpy.AddField_management(rptrPolys,"DESCRIPTION", "TEXT")
    gcList=[]
    cursor=arcpy.SearchCursor(rptrPolys)
    for row in cursor:
        gcList.append(row.getValue('gridcode'))
    del row, cursor
    gcCode=sorted(list(set(gcList)),reverse=True)

    newList=[]
    for nCode in gcCode:
        where_clause="gridcode = {0}".format(nCode)
        cursor=arcpy.UpdateCursor(rptrPolys, where_clause)
        rowCt=1
        for row in cursor:
            gCode=row.getValue('gridcode')
            gArea=row.getValue('Shape_Area')
            firstName="RptrPt{0}_{1}".format(gCode,rowCt)
            row.setValue("DESCRIPTION", firstName)
            newList.append([firstName, gCode, gArea])
            rowCt+=1
            cursor.updateRow(row)
        del cursor, row, rowCt
    del nCode

    #sort by "gridcode" (area[1]) in ascending order (1 - best, 2 - good) and "Area" (area[2]) in descending order
    nameList=sorted(newList,key=lambda fld: (-fld[1], -fld[2]))

    #take the top 10 from the list
    tempList = nameList
    if len(tempList)>5:
        nameList=[]
        nameList=tempList[0:4]
    del tempList

    arcpy.AddMessage("There will be {0} regions considered\n".format(len(nameList)))

    RptrPoly_Lyr = arcpy.mapping.Layer(rptrPolys)
    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,RptrPoly_Lyr,'BOTTOM')

    for nList in nameList:
        RptrPts=RepeaterAreas(RptrPoly_Lyr,DEM2, nList, df)
        AddViewFields(RptrPts, antHeight, maxDist)
        cursor=arcpy.UpdateCursor(RptrPts)
        for row in cursor:
            row.setValue('DESCRIPTION', nList[0])
            cursor.updateRow(row)
        if RepeaterLocations:
            arcpy.Append_management(RptrPts, RepeaterLocations,"NO_TEST")
        else:
            arcpy.Copy_management(RptrPts,RepeaterLocations)
            RptrPts_Lyr = arcpy.mapping.Layer(RepeaterLocations)
            arcpy.mapping.AddLayerToGroup(df,refGroupLayer,RptrPts_Lyr,'BOTTOM')

        deleteFeature([RptrPts])

    for nList in nameList:
        UpdateSpatialFields(RepeaterLocations,nList[0])
        RepeaterViewshed(RptrPts_Lyr, DEM2, nList[0],refGroupLayer, df, mxd)

    lyr = arcpy.mapping.ListLayers(mxd, RptrPoly_Lyr.name, df)[0]
    arcpy.mapping.RemoveLayer(df,lyr)
    arcpy.RefreshTOC()
    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,RptrPoly_Lyr,'BOTTOM')
##
##    fcList=[rptrPolys]
##    deleteFeature(fcList)
