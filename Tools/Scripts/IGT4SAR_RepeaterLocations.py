'''
-------------------------------------------------------------------------------
Name:        IGT4SAR_RepeaterLocations.py

Purpose:  Estimate optimal locations for radio repeaters based on the terrain
within the prescribed area.  Various points are defined within the area either
by the using or using the Random Points Generator tool.  The Observer points
tool is than used to predict locations that has a "view" of the maximum number
of points.

Author:      Don Ferguson

Created:     06/12/2012
Copyright:   (c) Don Ferguson 2012
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
        mxd = arcpy.mapping.MapDocument('CURRENT')
        frame = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,frame)

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
    fldNames=[('Description','TEXT'),('OFFSETA', 'SHORT'),('OFFSETB', 'SHORT'), \
              ('AZIMUTH1', 'SHORT'),('AZIMUTH2', 'SHORT'),('VERT1', 'SHORT'), \
              ('VERT2', 'SHORT'),('RADIUS1', 'SHORT'),('RADIUS2', 'SHORT')]
    fName=[fldNames[i][0] for i in range(9)]
    fieldnames = [f.name for f in arcpy.ListFields(obsvrPts)]
    compList=set(fieldnames).intersection(fName)
    compList=list(compList); chkList=list(fName)
    [chkList.remove(kk) for kk in compList]

    #Default values for Observer Points
    obsvrDef=[antHeight,2,0,360,90,-90,0,rad2]

    #Add field if it does not exist
    for field in fldNames:
        if field in chkList:
            arcpy.AddField_management(*(outName,) + field)

    cursor=arcpy.UpdateCursor(outName)
    for row in cursor:
        descp="ObsvrPt_{0}".format(row.getValue("OID"))
        obsvrName.append(descp)

        if row.getValue(fName[0]) is None:
            row.setValue(fName[0], descp)
        ct=0
        for k in fname[1:9]:
            if row.getValue(k) is None:
                row.setValue(k, obsvrDef[ct])
            ct+=1
        cursor.updateRow(row)

    return()


def RandomPts(outName, wrkspc, fcExtent):
    #Creates random points throughout fcExtent
    obsvrName=[]
    numPoints = 10
    minDistance = "100 Meters"
    arcpy.CreateRandomPoints_management(wrkspc, outName, "", fcExtent, numPoints, minDistance)
    return()

def RepeaterAreas(rptrPolys,DEM):
    #Select each polygon
        #clip DEM to polygon
        #maxElev = Get raster property - max value
        #Raster math - ElevArea=Con(Clipped DEM >= Max Value,1) - or >=round(maxElev,2)
        #convert ElevArea to Polygon
        #Dissolve Polygon
        #convert polygon to point
        #Return points
    return

def RepeaterViewshed(Rptrpts, DEM):
    return



##########################################

if __name__ == '__main__':
    mxd, df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    UserSelect = arcpy.GetParameterAsText(0)
    if UserSelect == '#' or not UserSelect:
        UserSelect = "System" # provide a default value if unspecified

    inputFeature = arcpy.GetParameterAsText(1)  # If not using System points then define

    DEM2 = arcpy.GetParameterAsText(2)
    if DEM2 == '#' or not DEM2:
        arcpy.AddMessage("You need to provide a valid DEM")

    antHeight = arcpy.GetParameterAsText(3)
    if antHeight == '#' or not antHeight:
        antHeight = 15 # provide a default value if unspecified

    maxDist = arcpy.GetParameterAsText(4) # Desired units
    if maxDist == '#' or not maxDist:
        maxDist = 5000 # provide a default value if unspecified

    # Variables
    outName = 'ObsvrRandom'
    rptrView = 'rptrView'
    rptrArea = 'rptrArea'
    rptrPolys = 'rptrPolys'
    fcExtent = "Search_Boundary"

    '''
    Check if user is using System values which are Random Points distributed
    throughout the search area, or is user planning to use a User Defined feature
    '''
    if UserSelect=="System":
        cSearchArea=arcpy.GetCount_management(fcExtent)
        #Does the Search Boundary exist?
        if int(cSearchArea.getOutput(0)) > 0:
            obsvrPts=RandomPts(outName, wrkspc, fcExtent)
        else:
            arcpy.AddError("You need to specify the Search Area Boundary (8 Segments_Group \ Search Boundary")
    else:
        obsvrPts = inputFeature
        # Check fields inprep for Observer

    #Check to see if the feature as the appropriate fields
    AddViewFields(obsvrPts, antHeight, maxDist)

    outObsPoints = ObserverPoints(DEM,obsvrPts, 1, "CURVED_EARTH", 0.13)
    outObsPoints.save(rptrView)

    rptrList=[]
    cursor=arcpy.SearchCursor(rptrView)
    for row in cursor:
        rptrList.append(row.getValue('Value'))
    OutRas = Con((rptrView==rptrList[-2]),1,Con((rptrView==rptrList[-1]),2))
    OutRas.save(rptrArea)

    # Set local variables
    field = "VALUE"

    # Execute RasterToPolygon
    arcpy.RasterToPolygon_conversion(rptrArea, rptrPolys, "SIMPLIFY", field)
    arcpy.AddField_management(rptrPolys,"NAME")
    rowCtA=1
    rowCtB=1
    nameList=[]
    cursor=arcpy.UpdateCursor(rptrPolys)
    for row in cursor:
        if row.getValue('gridcode'==rptrList[-2]):
            firstName="ObsvrPt{1}_{0}".format(rptrList[-2],rowCtA)
            rowCtA+=1
        else:
            firstName="ObsvrPt{1}_{0}".format(rptrList[-1],rowCtB)
            rowCtB+=1
        row.setValue("NAME", firstName)
        nameList.append(firstName)

    # Process for each Polygon
    # if there are more than 3 locations for Best than do 5 "Best" locations
    # Otherwise do 3 "Best" locations and 3 "Good" locations
    RepeaterAreas(rptrPolys,DEM)

    AddViewFields(outName, antHeight, rad2)

    RepeaterViewshed(Rptrpts, DEM)


























    DEM_Clip="DEM_Clip"
    IPP = "Planning Point"
    IPP_dist = "IPPTheoDistance"
    Elev_Same="Elev_Same"
    Elev_Up = "Elev_Up"
    Elev_Down="Elev_Down"


    Prob = ElevProb.split(',')
    ProbElev=map(int,Prob)

    Dist = ElevDists.split(',')
    Distances=map(float,Dist)
    Distances.append(0)
    Distances.sort()


    SubNum = int(SubNum)

    if bufferUnit =='kilometers':
        mult = 1.6093472
    else:
        mult = 1.0

    theDist = float(TheoDist)*mult
    TheoSearch = "{0} {1}".format(theDist, bufferUnit)

    Distances = [k*mult for k in Distances]
    distUp = Distances[1]
    distDown = Distances[2]

    try:
        arcpy.Delete_management(IPP_dist)
    except:
        pass

    # Buffer around IPP
    where1 = '"Subject_Number" = ' + str(SubNum)
    where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
    whereAll = where1 + where2

    arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", whereAll)

    # Process: Buffer for theoretical search area
    arcpy.Buffer_analysis(IPP, IPP_dist, TheoSearch)

    desc = arcpy.Describe(IPP_dist)
    extent = desc.extent
    arcpy.env.extent = IPP_dist

    ########################
    arcpy.Clip_management(DEM2, "#", DEM_Clip, IPP_dist, "", "ClippingGeometry")
    ##DEM_Clip = DEM2
    ########################
    DEM_Clip = checkSR(DEM_Clip)

    desc=arcpy.Describe(IPP)
    shapeName=desc.ShapeFieldName
    arcpy.AddMessage("\n")
    for row in arcpy.SearchCursor(IPP, whereAll):
        feat=row.getValue(shapeName)
        pnt=feat.getPart()
        cellPt="{0} {1}".format(pnt.X, pnt.Y)
        # Determine the elevation at the IPP
        result = (arcpy.GetCellValue_management(DEM_Clip, cellPt))
        cellElev = int(float(result.getOutput(0)))
        # Print x,y coordinates of each point feature
        arcpy.AddMessage("The coordinates at the {0} are: {1}, {2}".format(ippType, pnt.X, pnt.Y))
        arcpy.AddMessage("And the elevation is at the {1} is: {0}".format(cellElev, ippType))
    del row

    #####
    # IPP Elevation = cellelev
    # Same Elevation
    OutRas = Con((((cellElev-10) <= Raster(DEM_Clip))  &  (Raster(DEM_Clip)  <= (cellElev+10))),ProbElev[0],0)
    OutRas.save(Elev_Same)


    # Overall up
    OutRas = Con((((cellElev+10) < Raster(DEM_Clip))  &  (Raster(DEM_Clip)  <= (cellElev+distUp))),ProbElev[1],0)
    ##OutRas((((cellElev+10) < DEM_Clip)  &  (DEM_Clip  <= (640+48))),ElevProb[1],0)
    ##OutRas((((cellElev+48) < DEM_Clip)  &  (DEM_Clip  <= (640+100))),ElevProb[1],0)
    ##OutRas((((cellElev+100) < DEM_Clip)  &  (DEM_Clip  <= (640+370))),ElevProb[1],0)
    OutRas.save(Elev_Up)

    # Overall down
    OutRas=Con((((cellElev-distDown) <= Raster(DEM_Clip))  &  (Raster(DEM_Clip)  < (cellElev-10))),ProbElev[2],0)
    ##OutRas((((cellElev-40) <= DEM_Clip)  &  (DEM_Clip  < (cellElev-10))),ElevProb[2],0)
    ##OutRas((((cellElev-86) <= DEM_Clip)  &  (DEM_Clip  < (cellElev-40))),ElevProb[2],0)
    ##OutRas((((cellElev-203) <= DEM_Clip)  &  (DEM_Clip  < (cellElev-86))),ElevProb[2],0)
    OutRas.save(Elev_Down)

    OutRas=(Raster(Elev_Same)+Raster(Elev_Up)+Raster(Elev_Down))
    OutRas.save(Elev_Model)

    refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',df)[0]
##    ElevModel_Lyr = arcpy.MakeRasterLayer_management(Elev_Model, "Elevation Model")
##    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,ElevModel_Lyr.getOutput(0),'TOP')
    ElevModel_Lyr = arcpy.mapping.Layer(Elev_Model)
    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,ElevModel_Lyr,'TOP')


    fcList=["IPPTheoDistance","Elev_Same","Elev_Up", "Elev_Down", "DEM_Clip"]

    for gg in fcList:
        if arcpy.Exists(gg):
            try:
                arcpy.Delete_management(wrkspc + '\\' + gg)
            except:
                pass