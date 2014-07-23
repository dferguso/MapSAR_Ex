#-------------------------------------------------------------------------------
# Name:     IGT4SAR_Cell_Coverage.py
# Purpose:  The tool uses as input a point feature class, name for the new
#           polygon feature class, a Bearing (measured from North on
#           degrees), Angle (width of the sector in degrees), and the
#           Disatnce (in meters).
#
# Author:   Don Ferguson
#
# Created:  01/02/2013
# Copyright:   (c) Don Ferguson 2013
# Licence:
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  The GNU General Public License can be found at
#  <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
# Import arcpy module
import math
import arcpy, sys, arcgisscripting, os
import arcpy.mapping
from arcpy import env
from arcpy.sa import *
import IGT4SAR_Geodesic

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

def ValidateNewLocation(Newpoint,NewCoord):
    if NewPoint!="empty":
        NewPt = NewPoint.split(" ")
        xCoord = float(NewPt[0])
        yCoord = float(NewPt[1])
        if xCoord == None or yCoord ==None:
                sys.exit(arcpy.AddError("Please check your coordinates\n"))
        if NewCoord=="Geographic (Long / Lat)":
            arcpy.AddMessage('Longitude: {0}  and Latitude: {1}\n'.format(xCoord, yCoord))
            if xCoord<-180 or xCoord > 180:
                sys.exit(arcpy.AddError("Check your Longitude Coordinate (X)\n"))
            elif yCoord<-90 or xCoord > 90:
                sys.exit(arcpy.AddError("Check your Latitude Coordinate (Y)\n"))
            else:
                return(xCoord, yCoord)
        else:
            arcpy.AddMessage('X Coord: {0}  and Y Coord: {1}\n'.format(xCoord, yCoord))
            if xCoord < 0 or yCoord < 0:
                arcpy.AddWarning("Projected Coordinate is negative - is this corrrect?\n")
            return(xCoord, yCoord)

    else:
        sys.exit(arcpy.AddError("Please check the Point Coordinates\n"))

def ValidateNewInfo(NewInfo,tParam, towerParam):
    if NewInfo=='empty':
        sys.exit(arcpy.AddError("Please check the tower/antenna information \n"))
    else:
        arcpy.AddMessage('Tower / Antenna Properties')
        nInfo=NewInfo.split(',')
        for k in range(len(nInfo)):
            arcpy.AddMessage('{0} : {1}'.format(towerParam[k],nInfo[k]))
            try:
                kInt=int(nInfo[k])
            except:
                sys.exit(arcpy.AddError('Tower properties need to be numeric\n'))

        if len(nInfo)!= 4:
            sys.exit(arcpy.AddError("Please Check Antenna/Tower Properties - each seperated by a comma\n"))
        else:
            AntInfo=dict((tParam[i],int(nInfo[i])) for i in range(len(tParam)))
            # Use is AntInfo.get("aBearing")
            return(AntInfo)

def AddViewFields(in_fc, fldNames):
    obsvrName=[]
    fName=[fldNames[k][0] for k in range(len(fldNames))]
    if int(arcpy.GetCount_management(in_fcs).getOutput(0)) > 0:
        fieldnames = [f.name for f in arcpy.ListFields(in_fc)]
        if "OID" in fieldnames:
            OID="OID"
        elif "OBJECTID" in fieldnames:
            OID="OBJECTID"
        else:
            OID=None
        compList=set(fieldnames).intersection(fName)
        compList=list(compList); chkList=list(fName)
        [chkList.remove(kk) for kk in compList]

        #Add field if it does not exist
        for field in fldNames:
            if field[0] in chkList:
                arcpy.AddField_management(*(in_fc,) + field)

        del fieldnames, cursor, row, ct, cnt, compList, descp, field
    del fName
    return()

def Geodesic(in_fc,unProjCoordSys,AntInfo,timestamp):
    # Execute CreateFeatureclass for Sector
    inDataset = "CellSec_%s.shp" % (timestamp)
    coordList = []
    k=0
    rows = arcpy.SearchCursor(in_fc, '', unProjCoordSys)

    for row in rows:
        feat = row.getValue(shapefieldname)
        pnt = feat.getPart()
        k+=1

        # A list of features and coordinate pairs
        pnt.X=pnt.X
        pnt.Y=pnt.Y
        coordList1 = IGT4SAR_Geodesic.Geodesic(pnt, float(AntInfo.get("aBearing")), \
                     float(AntInfo.get("aSecAng")), float(AntInfo.get("aRange")))
        coordList.append(coordList1)

    del row
    del rows
    # Create empty Point and Array objects
    #
    array = arcpy.Array()

    # A list that will hold each of the Polygon objects
    #
    featureList = []

    for feature in coordList:
        for coordPair in feature:
            # For each coordinate pair, set the x,y properties and add to the
            #  Array object.
            #
            point = arcpy.Point(float(coordPair[0]),float(coordPair[1]))

            array.add(point)
        # Create a Polygon object based on the array of points
        #
        polygon = arcpy.Polygon(array, unProjCoordSys)
        # Clear the array for future use
        #
        array.removeAll()

        # Append to the list of Polygon objects
        #
        featureList.append(polygon)

    # Create a copy of the Polygon objects, by using featureList as input to
    #  the CopyFeatures tool.
    #
    arcpy.CopyFeatures_management(featureList, inDataset)

    arcpy.Project_management(inDataset, out_fc, outCS)
    arcpy.Delete_management(inDataset)

    del coordList
    del polygon
    del featureList
    del feature


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


########
# Main Program starts here
#######

## Script arguments
mxd,df = getDataframe()
# Set date and time vars
timestamp = ''
now = datetime.datetime.now()
todaydate = now.strftime("%m_%d")
todaytime = now.strftime("%H_%M_%p")
timestamp = '{0}_{1}'.format(todaydate,todaytime)

#inFeature  - this is a point feature used to get the latitude and longitude of point.
inFeature = arcpy.GetParameterAsText(0)
if inFeature == '#' or not inFeature:
    sys.exit(arcpy.AddError("You need to provide a valid Feature Class"))

#out_fc - this will be the output feature for the sector.  May allow user to decide name or I may specify.
cellTowers =arcpy.GetParameterAsText(1)
if cellTowers == '#' or not cellTowers:
    cellTowers = "empty"

NewCoord = arcpy.GetParameterAsText(2)
if NewCoord == '#' or not NewCoord:
    NewCoord = "empty"

NewPoint = arcpy.GetParameterAsText(3)
if NewPoint == '#' or not NewPoint:
    NewPoint = "empty"

NewInfo = arcpy.GetParameterAsText(4)
if NewInfo == '#' or not NewInfo:
    NewInfo = "empty"

NewGenSector = arcpy.GetParameterAsText(5)
if NewGenSector == '#' or not NewGenSector:
    NewGenSector = "empty"

NewViewshed = arcpy.GetParameterAsText(6)
if NewViewshed == '#' or not NewViewshed:
    NewViewshed = "empty"

DEM = arcpy.GetParameterAsText(7)
if DEM == '#' or not DEM:
    DEM = "empty"

arcpy.AddMessage('\n')

## Variables
tParam=['aHeight','aBearing', 'aSecAng', 'aRange']
towerParam=['Height','Bearing', 'Sector Angle', 'Range']
unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', \
                  SPHEROID['WGS_1984',6378137.0,298.257223563]],\
                  PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
fldNamesA=[('DESCRIPTION','TEXT'),('OFFSETA', 'SHORT'),('OFFSETB', 'SHORT'), \
          ('AZIMUTH1', 'SHORT'),('AZIMUTH2', 'SHORT'),('VERT1', 'SHORT'), \
          ('VERT2', 'SHORT'),('RADIUS1', 'SHORT'),('RADIUS2', 'SHORT')]
fldNamesB=[('ANTSEC_DIR','SHORT'),('ANTSEC_DISP', 'SHORT'),('RANGE_MAX', 'SHORT')]
CellTowers = "CellTowers"

planPt = arcpy.mapping.Layer("Planning Point")
# Use Describe to get a SpatialReference object
descPlanPt = arcpy.Describe(planPt)
shapefieldname = descPlanPt.ShapeFieldName
PlanPtCS = descPlanPt.SpatialReference

########################################################
if inFeature == "Use Cell Towers Layer":
    if cellTowers=="empty":
        sys.exit(arcpy.AddError("Please select one or more Cell Tower to consider\n"))
    else:
        cTower = cellTowers.split(";")
    ##
########################################################

# Check to see if the cell Tower Layer exists
#
# Get a List of Layers
LyrList=arcpy.mapping.ListLayers(mxd, "", df)
LyrName=[]
for lyr in LyrList:
    LyrName.append(lyr.name)

if "Cellular" in LyrName:
    refGroupLayerA = arcpy.mapping.ListLayers(mxd,'*Cellular*',df)[0]
else:
    refGroupLayerA = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]

if "Point_Features" in LyrName:
    refGroupLayerB = arcpy.mapping.ListLayers(mxd,'*Point_Features*',df)[0]

if "CellTowers" in LyrName:
    in_fc = arcpy.mapping.Layer(CellTowers)
    # Use Describe to get a SpatialReference object
else:
    # Create a CellTowers Feature Class and Layer in the coordinate system defined by Planning Point
    arcpy.CreateFeatureclass_management(wrkspc, CellTowers, "POINT", "", "DISABLED", "DISABLED", PlanPtCS)
    in_fc = arcpy.mapping.Layer(CellTowers)
    arcpy.mapping.AddLayerToGroup(df,refGroupLayerB,in_fc,'BOTTOM')

desc = arcpy.Describe(in_fc)
shapefieldname = desc.ShapeFieldName
outCS = desc.SpatialReference

# Check the field names in the Cell
AddViewFields(in_fc, fldNamesA)
AddViewFields(in_fc, fldNamesA)


if inFeature == "New Location":
    try:
        AntInfo = ValidateNewInfo(NewInfo,tParam,towerParam)
        arcpy.AddMessage(AntInfo)
        # Use is AntInfo.get("aBearing")
    except SystemError as err:
        pass

    try:
        xCrd, yCrd = ValidateNewLocation(NewPoint,NewCoord)
    except SystemError as err:
        pass
    #################################
    ## Write geometry if NewLocation is True
    cTower = "Temp_{0}".format(timestamp)
    ## Create a temporary layer with either Projected c
    if NewCoord=="Geographic (Long / Lat)":
        ## Write new points to this temporary dataset
        ## Is the Map in GCS?
        if outCS == unProjCoordSys:
            ## Directly write geometry to CellTowers using UpdateCursor
        else:
            arcpy.CreateFeatureclass_management(wrkspc, cTower, "POINT", "", "DISABLED", "DISABLED", unProjCoordSys)
            arcpy.Project_management(cTower, TempPoints, outCS)
            arcpy.Append_management(TempPoints, CellTowers,"NO_TEST")
            deleteFeature([fcList])

    elif NewCoord == "Projected":
        ## Assume New Locations in projected in same coordinate system as outCS
        ## Directly write geometry to CellTowers using UpdateCursor

##  ^
## ^|^

## Need to think about the above





## Stopped Here

# Default values for Cell Towers
OFFSETA = aHeight
OFFSETB = 2
AZIMUTH1 = aBearing - aSecAng/2
AZIMUTH2 = aBearing + aSecAng/2
VERT1 = 90
VERT2 = -90
RADIUS1 = 0
RADIUS2 = aRange
obsvrDef=[OFFSETA,OFFSETB,AZIMUTH1,AZIMUTH2,VERT1,VERT2,RADIUS1,RADIUS2]













## Check to see if all the values required are present
## Get Values
for cell in cTower:
    expression = "DESCRIPTION = {0}".format(cell)

    cursor=arcpy.UpdateCursor(in_fc, expression)
    for row in cursor:
        aHeight=row.getValue('gridcode')
        gArea=row.getValue('Shape_Area')
        firstName="RptrPt{0}_{1}".format(gCode,rowCt)
        row.setValue("DESCRIPTION", firstName)
        newList.append([firstName, gCode, gArea])
        rowCt+=1
        cursor.updateRow(row)
    del cursor, row, rowCt
#################################
## Generate Sector
if NewGenSector.upper()=="TRUE":
    for cell in cTower:
        expression = "DESCRIPTION = {0}".format(cell)
        arcpy.AddMessage(expression)
        arcpy.AddMessage(in_fc.name)
        cursor=arcpy.SearchCursor(in_fc, expression)
        for row in cursor:

        AntInfo=dict((tParam[i],int(nInfo[i])) for i in range(len(tParam)))
        # Use is AntInfo.get("aBearing")

        arcpy.SelectLayerByAttribute_management(in_fc, "NEW_SELECTION", expression)
        Geodesic(in_fc,unProjCoordSys,AntInfo,timestamp)
#################################
sys.exit()
#################################
## Viewshed Analysis
if NewViewshed==True:
    RepeaterViewshed(RptrPts_Lyr, DEM, nList,refGroupLayer, df, mxd)

######################################################