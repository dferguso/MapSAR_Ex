#-------------------------------------------------------------------------------
# Name:        ElevationDifferenceModel_Example
# Purpose:  This is not an actual script but examples of the calculations that
#  would be performed inside of the Raster Calculator to complete the Elevation
#  Model as described in Koester's Lost Person Behavior.
#
# Author:      Don Ferguson
#
# Created:     06/12/2012
# Copyright:   (c) Don Ferguson 2012
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


##########################################

if __name__ == '__main__':
    mxd, df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)
    Elev_Model = "Elev_Model_{0}".format(timestamp)

    SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
    if SubNum == '#' or not SubNum:
        SubNum = "1" # provide a default value if unspecified

    ippType = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP

    TheoDist = arcpy.GetParameterAsText(2)
    if TheoDist == '#' or not TheoDist:
        TheoDist = "0" # provide a default value if unspecified

    bufferUnit = arcpy.GetParameterAsText(3) # Desired units
    if bufferUnit == '#' or not bufferUnit:
        bufferUnit = "miles" # provide a default value if unspecified

    DEM2 = arcpy.GetParameterAsText(4)
    if DEM2 == '#' or not DEM2:
    #    DEM2 = "DEM" # provide a default value if unspecified
        arcpy.AddMessage("You need to provide a valid DEM")

    # Elevation distances for Same, Uphill, Downhill
    ElevProb = arcpy.GetParameterAsText(5)
    if ElevProb == '#' or not ElevProb:
        ElevProb=['16','32','52'] # provide a default value if unspecified - default hiker
        arcpy.AddMessage("You need to provide a valid elevations")

    # Elevation distances for Same, Uphill, Downhill
    ElevDists = arcpy.GetParameterAsText(6)
    if ElevDists == '#' or not ElevDists:
        ElevDists=[0,0] # provide a default value if unspecified
        arcpy.AddMessage("You need to provide a valid elevations")

    # Variables
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