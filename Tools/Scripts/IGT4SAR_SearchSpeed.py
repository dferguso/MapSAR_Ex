#-------------------------------------------------------------------------------
# Name:        IGT4SAR_SearchSpeed.py
# Purpose:
#  User must run Cost Distance Model prior to running this script.
#  Baseline segment search speed based on an average 5 km per hour rate along a
#  flat, open space.  Search time varied based on slope, vegetation (NLCD),
#  availability of raods and trails, and inaccessibility due to large bodies of
#  water (large streams, river, lakes and ponds).

# Author:      Don Ferguson
#
# Created:     01/25/2012
# Updated:     01/05/2015
# Copyright:   (c) Don Ferguson 2015
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
try:
    arcpy
except NameError:
    import arcpy
from arcpy import env
from arcpy.sa import *

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")

# Script arguments
workspc = env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"


# Get map and dataframe to access properties
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

if __name__ == '__main__':
    mxd,df = getDataframe() # Set Map Document and data frame handles
    # Set local variables
    TSpd_kph = "Tspd_kph"
    TravSpd_kph = "TravSpd_kph"
    SegSpd = "SegSrchSpd"
    SegSpd_poly = "SegSpd_poly"
    Search_Segments = "Search_Segments"
    SegSpd_Joins = "SegSpd_Join"

    deSiredSpdA = arcpy.GetParameterAsText(0) # Nominal walking speed
    if deSiredSpdA == '#' or not deSiredSpdA:
        deSiredSpdA = "3.0" # provide a default value if unspecified

    lengthUnit = arcpy.GetParameterAsText(1) # Desired units
    if lengthUnit == '#' or not lengthUnit:
        lengthUnit = "kilometers" # provide a default value if unspecified

    if lengthUnit =='kilometers':
        mult = 1.0
    else:
        mult = 1.6093472

    deSiredSpd = mult * float(deSiredSpdA)

    inConstant=deSiredSpd/5.0
    outSpd=Times(TSpd_kph, inConstant)
    outSpd.save(TravSpd_kph)
    #arcpy.Delete_management(workspc + '\\' + TSpd_kph)

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

    if lengthUnit.lower() == "miles":
        arcpy.AddMessage("Add field: SegSpd_mph")
        arcpy.AddField_management(SegSpd_poly, "SegSpd", "DOUBLE", 6, "", "", "SegSpd_mph", "NULLABLE")
        # Process: Calculate Field (2)
        arcpy.AddMessage("Calculate Travel Speed Field")
        arcpy.CalculateField_management(SegSpd_poly, "SegSpd", "!gridcode!/100.0/1.6093472", "PYTHON")
        fAlias = 'Search Speed (miles/hr)'
    else:
        arcpy.AddMessage("Add field: SegSpd_kph")
        arcpy.AddField_management(SegSpd_poly, "SegSpd", "DOUBLE", 6, "", "", "SegSpd_kph", "NULLABLE")
        # Process: Calculate Field (2)
        arcpy.AddMessage("Calculate Travel Speed Field")
        arcpy.CalculateField_management(SegSpd_poly, "SegSpd", "!gridcode!/100.0", "PYTHON")
        fAlias = 'Search Speed (km/hr)'

    # Process: Spatial Join
    arcpy.AddMessage("Spatial Joins")
    arcpy.SpatialJoin_analysis(Search_Segments, SegSpd_poly, SegSpd_Joins)

    arcpy.Delete_management(SegSpd_poly)
    arcpy.Delete_management(SegSpd_rcl)
    arcpy.Delete_management(SegSpd)

    arcpy.AddMessage("Join Search Segments with Search Speed Layer")
    arcpy.JoinField_management(Search_Segments, "Area_Name", SegSpd_Joins, "Area_Name", ["SegSpd"])
##    try:
##        arcpy.mapping.RemoveLayer (df, SegSpd_Joins)
##    except:
##        pass
##    arcpy.Delete_management(SegSpd_Joins)

    desc=arcpy.Describe(Search_Segments)
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    if "SearchSpd" in field_names:
        arcpy.CalculateField_management(Search_Segments, "SearchSpd", "!SegSpd!", "PYTHON")
        try:
            arcpy.AlterField_management(Search_Segments, field, 'SearchSpd', fAlias)
        except:
            pass
    arcpy.DeleteField_management(Search_Segments, ["SegSpd"])



