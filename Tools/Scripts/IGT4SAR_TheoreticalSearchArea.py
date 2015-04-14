#-------------------------------------------------------------------------------
# Name:        IGT4SAR_TheoreticalSearchArea.py
# Purpose:
#  This tool utilizes the output from the Cost Distance Model to
#  determine a least cost Path Distance surface from a point.

# Author:      Don Ferguson
#
# Created:     01/25/2012
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
try:
    arcpy
except NameError:
    import arcpy
try:
    arcpy.mapping
except NameError:
    import arcpy.mapping
import datetime
from arcpy import env
from arcpy.sa import *

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Script arguments
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

# Script arguments
wrkspc = arcpy.GetParameterAsText(0)  # Get the subject number
arcpy.AddMessage("\nCurrent Workspace" + '\n' + wrkspc + '\n')
env.workspace = wrkspc

SubNum = arcpy.GetParameterAsText(1)  # Get the subject number
if SubNum == '#' or not SubNum:
    SubNum = "1" # provide a default value if unspecified

ippType = arcpy.GetParameterAsText(2)  # Determine to use PLS or LKP

bufferUnit = arcpy.GetParameterAsText(3) # Desired units
if bufferUnit == '#' or not bufferUnit:
    bufferUnit = "miles" # provide a default value if unspecified

deSiredSpdA = arcpy.GetParameterAsText(4) # Nominal walking speed
if deSiredSpdA == '#' or not deSiredSpdA:
    deSiredSpdA = "3.0" # provide a default value if unspecified


DEM2 = arcpy.GetParameterAsText(5)
if DEM2 == '#' or not DEM2:
    DEM2 = "DEM" # provide a default value if unspecified

# Set date and time vars
timestamp = ''
now = datetime.datetime.now()
todaydate = now.strftime("%m_%d")
todaytime = now.strftime("%H_%M_%p")
timestamp = '{0}_{1}'.format(todaydate,todaytime)

# Local variables:
IPP = "Planning Point"
Sloper = "Slope"
Impedance = "Impedance"
walkspd_kph = "walkspd_kph"
Travspd_spm = "TravSpd_spm"
PthDis_travsp = "PthDis_travsp"
blnk_travsppd = "blnk_travsppd"
Travspd_kph = "Travspd_kph"
Travspd_mph = "Travspd_mph"
Travspd_Layer = "Travspd_Layer"

TravTime_hrs = "TravTime_hrs"
travtimhr_rcl = "Travtimhr_rcl_{0}".format(timestamp)
traveltime_hrs_poly = "traveltime_hrs_poly"

##May 07, 2013#########################
##TimeTable = "C:\MapSAR_Ex\Template\SAR_Default.gdb\TimeTable"
##TimeTable = "Time_Table_3hr"
TimeTable = "TimeTable"
##May 07, 2013#########################

arcpy.env.cellSize = DEM2

desc = arcpy.Describe(Impedance)
extent = desc.extent
arcpy.env.extent = Impedance

spatialRef = desc.SpatialReference
arcpy.AddMessage("Spatial Reference is: " + spatialRef.name)

XCel = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
XCell = float(XCel.getOutput(0))
cellSize = XCell

############################
if bufferUnit =='kilometers':
    TravTimePoly_hrs = "MobilityModel_{0}kph_{1}".format(int(float(deSiredSpdA)*10.0), timestamp)
    mult = 1.0
else:
    TravTimePoly_hrs = "MobilityModel_{0}mph_{1}".format(int(float(deSiredSpdA)*10.0), timestamp)
    mult = 1.6093472

deSiredSpd = mult * float(deSiredSpdA)
arcpy.AddMessage("Desired Speed Raster")
outDivide = CreateConstantRaster(deSiredSpd, "FLOAT", cellSize, extent)
outDivide.save(walkspd_kph)

arcpy.DefineProjection_management(walkspd_kph, spatialRef)
del outDivide

# This Raster Calculator function determines locations in which the Impedance is
# excessively high (Imp > 98%).  When the Impedance meets this criteria, the
# raster cell at this location used to represent travel speed (kph) is assigned
# a value of zero becuase the impedance is too high for nominal foot travel.
# If the Impdeance is below this thresold the raster cell is assigna value of
#
# Travspd_kph = Raster(walkspd_kph)/Exp(0.0212*Float(Raster(Impedance)))

try:
    arcpy.Delete_management(Travspd_kph)
except:
    pass

arcpy.AddMessage("Calculate Traveling Speed across requested area")
outRast = Con((Exp(0.0212*(Raster(Impedance))) > Exp(0.0212*98.0)),0.0,(Raster(walkspd_kph)/Exp(0.0212*(Raster(Impedance)))))
outRast.save(Travspd_kph)
del outRast


##arcpy.Delete_management(wrkspc + '\\' + Impedance)
##arcpy.Delete_management(wrkspc + '\\' + walkspd_kph)

if bufferUnit =='kilometers':
    Travspd_Layer=arcpy.MakeRasterLayer_management(Travspd_kph, "Travel Speed in kph")
else:
    outSpeed = Raster(Travspd_kph)/1.6093472
    outSpeed.save(Travspd_mph)
    Travspd_Layer=arcpy.MakeRasterLayer_management(Travspd_mph, "Travel Speed in mph")
    del outSpeed

LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
LyrName=[]
for lyr in LyrList:
    LyrName.append(lyr.name)

if "Mobility" in LyrName:
    refGroupLayer = arcpy.mapping.ListLayers(mxd,'Mobility',df)[0]
else:
    refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',df)[0]


arcpy.mapping.AddLayerToGroup(df,refGroupLayer,Travspd_Layer.getOutput(0),'TOP')
arcpy.RefreshActiveView()

arcpy.AddMessage("Calculate Travel Time in Seconds per Meter")
outDivideA=SetNull(Raster(Travspd_kph) == 0.0,Raster(Travspd_kph))
#outDivide = Con(Raster(Travspd_kph) == 0.0,36000,3600.0/(Raster(Travspd_kph) * 1000.0))
outDivide = 3600.0/(outDivideA*1000.0)
outDivide.save(Travspd_spm)
del outDivide

# Buffer areas of impact around major roads
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
where = where1 + where2

arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)

arcpy.AddMessage("Path Distance")

# InVertFact identifies that a table file will be used to define the vertical-
# factor graph used to determine the VFs. The Vertical Factor (VF) defines the
# vertical difficulty encountered in moving from one cell to the next.
# In this application the Tobler Hiking Function can be used to define the
# cost of travelling on slope.
# Slope = Angle * pi /180 (radians)
# VF = Exp(-3.5*abs(tan(slope)+0.05))
# This is the Tobler Hiking Function less the baseline velocity.  The baseline
# velocity is determined by the Travspd_spm layer ands the "cost" of directional
# slope dtravel is obtained from the VF.  Path Distance Tool applies directionality.

InVertFact = 'VfTable("C:\MapSAR_Ex\Tools\Tables\Tobler.txt")'
##InVertFact = 'VfTable("C:\MapSAR_Ex\Tools\Tables\Tobler_Bike.txt")'
##InVertFact = 'VfTable("C:\MapSAR_Ex\Tools\Tables\ToblerTest.txt")'

############Test Section##################
# Create the VfCosSec Object
lowCutAngle = -60
highCutAngle = 60
cosPower = 1
secPower = 1
myVerticalFactor = VfCosSec(lowCutAngle, highCutAngle, cosPower, secPower)
##########################################

##outPathDist = PathDistance(IPP, Travspd_spm, DEM2, "", "BINARY 1 45", DEM2, myVerticalFactor)
outPathDist = PathDistance(IPP, Travspd_spm, DEM2, "", "BINARY 1 45", DEM2, InVertFact)#, "", blnk_travsppd)
outPathDist.save(PthDis_travsp)
del outPathDist

# Process: Divide (6)
##May 07, 2013#########################
outDivide = Int(Raster(PthDis_travsp)/3600.0*10.0)
##May 07, 2013#########################
outDivide.save(TravTime_hrs)
del outDivide

# Process: Reclassify
arcpy.AddMessage("Reclassify Travel Time - hrs")
# Execute Reclassify
# The output from Reclassification is multiplied by 10 to allow for 1/2 hour
# increments with integer math.  Thus 5 = 0.5 hours.  Correction will be made below.
outRaster = ReclassByTable(TravTime_hrs, TimeTable , "FROM_","TO","OUT","NODATA")
# Save the output
outRaster.save(travtimhr_rcl)

# Process: Raster to Polygon
arcpy.AddMessage("Raster to Polygon")
arcpy.RasterToPolygon_conversion(travtimhr_rcl, traveltime_hrs_poly, "SIMPLIFY", "VALUE")

# Process: Add Field
arcpy.AddMessage("Add field: Hours")
arcpy.AddField_management(traveltime_hrs_poly, "HOURS", "FLOAT", 6, "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculate Field (2)
arcpy.AddMessage("Calculate Hours Field")
##May 07, 2013#########################
arcpy.CalculateField_management(traveltime_hrs_poly, "HOURS", "!gridcode!/10.0", "PYTHON")
##May 07, 2013#########################
# Process: Add Field (2)
arcpy.AddMessage("Add field: DateHrsTxt")
arcpy.AddField_management(traveltime_hrs_poly, "DateHrsTxt", "TEXT", "", "", "30", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Dissolve
arcpy.AddMessage("Dissolve")
arcpy.Dissolve_management(traveltime_hrs_poly, TravTimePoly_hrs, "HOURS;DateHrsTxt", "", "MULTI_PART", "DISSOLVE_LINES")

TravTime_Layer=arcpy.mapping.Layer(TravTimePoly_hrs)
arcpy.mapping.AddLayerToGroup(df,refGroupLayer,TravTime_Layer,'TOP')

##try:
# Set layer that output symbology will be based on
symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\MobilityModel.lyr"

# Apply the symbology from the symbology layer to the input layer
updateLayer = arcpy.mapping.ListLayers(mxd, TravTimePoly_hrs, df)[0]
arcpy.ApplySymbologyFromLayer_management (updateLayer, symbologyLayer)

##except:
##    pass

arcpy.Delete_management(wrkspc + '\\' + PthDis_travsp)
arcpy.Delete_management(wrkspc + '\\' + Travspd_spm)
arcpy.Delete_management(wrkspc + '\\' + TravTime_hrs)
arcpy.Delete_management(wrkspc + '\\' + travtimhr_rcl)
arcpy.Delete_management(wrkspc + '\\' + traveltime_hrs_poly)

