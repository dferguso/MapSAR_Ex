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
out_fc = os.getcwd()
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

wrkspc = arcpy.GetParameterAsText(0)  # Get the subject number
arcpy.AddMessage("\nCurrent Workspace" + '\n' + wrkspc + '\n')
env.workspace = wrkspc

SubNum = arcpy.GetParameterAsText(1)  # Get the subject number
if SubNum == '#' or not SubNum:
    SubNum = "1" # provide a default value if unspecified

ippType = arcpy.GetParameterAsText(2)  # Determine to use PLS or LKP

TheoDist = arcpy.GetParameterAsText(3)
if TheoDist == '#' or not TheoDist:
    TheoDist = "0" # provide a default value if unspecified

bufferUnit = arcpy.GetParameterAsText(4) # Desired units
if bufferUnit == '#' or not bufferUnit:
    bufferUnit = "miles" # provide a default value if unspecified

uSeStr= arcpy.GetParameterAsText(5) # Desired units
if uSeStr == '#' or not uSeStr:
    uSeStr = "true" # provide a default value if unspecified

DEM2 = arcpy.GetParameterAsText(6)
if DEM2 == '#' or not DEM2:
#    DEM2 = "DEM" # provide a default value if unspecified
    arcpy.AddMessage("You need to provide a valid DEM")

# Elevation distances for Same, Uphill, Downhill
ElevDists = arcpy.GetParameterAsText(7)
if ElevDists == '#' or not ElevDists:
    ElevDists=[0,0,0] # provide a default value if unspecified
    arcpy.AddMessage("You need to provide a valid DEM")

# Variables
IPP = "Planning Point"
IPP_dist = "IPPTheoDistance"

# Need to select the correct IPP location
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
whereAll = where1 + where2

desc=arcpy.Describe(IPP)
shapefieldname=desc.ShapeFieldName
for row in arcpy.SearchCursor(IPP, whereAll):
    feat=row.getValue(shapefieldname)
    pnt=feat.getPart()
    cellPt="{0} {1}".format(pnt.X, pnt.Y)
    cellElev=arcpy.GetCellValue_management(DEM2, cellPt)
    # Print x,y coordinates of each point feature
    print "The coordinates at the {0} are: {1}, {2}".format(ippType, pnt.X, pnt.Y)
    print "And the elevation is at the {1} is: {0}".format(cellElev, ippType)
# Determine the elevation at the IPP


#####
# IPP Elevation = cellelev
# Same Elevation
Con((((cellElev-10) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (cellElev+10))),16,0)

### Down
##Con((((cellElev-40) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (cellElev-10))),36,0)
##Con((((cellElev-86) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (cellElev-40))),36,0)
##Con((((cellElev-203) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (cellElev-86))),36,0)
##
### Up
##Con((((cellElev+10) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+48))),33,0)
##Con((((cellElev+48) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+100))),33,0)
##Con((((cellElev+100) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+370))),33,0)

# Overall up
Con((((cellElev+10) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (cellElev+distUp))),42,0)

# Overall down
Con((((cellElev-distDown) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (cellElev-10))),55,0)