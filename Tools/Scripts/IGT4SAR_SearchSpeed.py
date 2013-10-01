#-------------------------------------------------------------------------------
# Name:        Search Area Speed (SearchSpeed.py)
# Purpose:
#  User must run Cost Distance Model prior to running this script.
#  Baseline segment search speed based on an average 5 km per hour rate along a
#  flat, open space.  Search time varied based on slope, vegetation (NLCD),
#  availability of raods and trails, and inaccessibility due to large bodies of
#  water (large streams, river, lakes and ponds).

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

# Import system modules
import arcpy
from arcpy import env
from arcpy.sa import *

# Script arguments
#workspc = arcpy.GetParameterAsText(0)
#env.workspace = workspc
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

# Set local variables
TravSpd_kph = "TravSpd_kph"
SegSpd = "SegSrchSpd"
SegSpd_poly = "SegSpd_poly"
Search_Segments = "Planning\Search_Segments"
SegSpd_Joins = "Planning\SegSpd_Join"

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Execute ZonalStatistics
arcpy.AddMessage("Zonal Statistics")
outZonalStatistics = ZonalStatistics(Search_Segments, "Area_Name", TravSpd_kph,"MEAN", "NODATA")
# Save the output
outZonalStatistics.save("SegSrchSpd")

SpdTab = "SpeedTable"
SegSpd_rcl ="SegSpd_rcl"

# Execute Reclassify
arcpy.AddMessage("Reclass by Table")
outRaster = ReclassByTable(SegSpd, SpdTab,"FROM_","TO","OUT","NODATA")
# Save the output
outRaster.save(SegSpd_rcl)

arcpy.AddMessage("Raster to Polygon")
arcpy.RasterToPolygon_conversion(SegSpd_rcl, SegSpd_poly, "SIMPLIFY", "VALUE")

arcpy.AddMessage("Add field: SegSpd_kph")
arcpy.AddField_management(SegSpd_poly, "SegSpd", "DOUBLE", 6, "", "", "SegSpd_kph", "NULLABLE")
# Process: Calculate Field (2)
arcpy.AddMessage("Calculate Travel Speed Field")
arcpy.CalculateField_management(SegSpd_poly, "SegSpd", "!grid_code!/100.0", "PYTHON")

# Process: Spatial Join
arcpy.AddMessage("Spatial Joins")
arcpy.SpatialJoin_analysis(Search_Segments, SegSpd_poly, SegSpd_Joins)

# Execute DeleteField
arcpy.AddMessage("Delete fields")
dropFields = ["Join_Count","TARGET_FID","Status","Area","Area_Description","Searched","Period_Optional","Probability_Density","Display","POAcum","POScum","POScumUn","Coverage","POStheo","ResourceType_PSR","SearchTime_hr","Coverage_PSR","PSR","PODest","Id","grid_code","Shape_Length_1","Shape_Area_1"]
arcpy.DeleteField_management(SegSpd_Joins, dropFields)

SegSpd_Layer=arcpy.mapping.Layer(SegSpd_Joins)
arcpy.mapping.AddLayer(df,SegSpd_Layer,"BOTTOM")


arcpy.Delete_management(SegSpd_poly)
arcpy.Delete_management(SegSpd_rcl)
arcpy.Delete_management(SegSpd)