#-------------------------------------------------------------------------------
# Name:     IGT4SAR_geodesic_Cell.py
# Purpose:  The tool uses as input a point feature class, name for the new
#           polygon feature class, a Bearing (measured from North on
#           degrees), Angle (width of the sector in degrees), and the
#           Disatnce (in meters).
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
#!/usr/bin/env python
import math, arcpy, sys, arcgisscripting
from arcpy import env
import IGT4SAR_Geodesic

# Create the Geoprocessor objects
gp = arcgisscripting.create()

########
# Main Program starts here
#######

## Script arguments
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

inDataset = "Sector.shp"

#in_fc  - this is a point feature used to get the latitude and longitude of point.
in_fc = arcpy.GetParameterAsText(0)
if in_fc == '#' or not in_fc:
    arcpy.AddMessage("You need to provide a valid in_fc")

#out_fc - this will be the output feature for the sector.  May allow user to decide name or I may specify.
out_fc = arcpy.GetParameterAsText(1)
if out_fc == '#' or not out_fc:
    arcpy.AddMessage("You need to provide a valid out_fc")

in_bearing = arcpy.GetParameterAsText(2)
if in_bearing == '#' or not in_bearing:
    in_bearing = "empty"

in_angle = arcpy.GetParameterAsText(3)
if in_angle == '#' or not in_angle:
    in_angle = "empty"

in_dist = arcpy.GetParameterAsText(4)
if in_dist == '#' or not in_dist:
    in_dist = "empty"

# Use Describe to get a SpatialReference object
desc = arcpy.Describe(in_fc)
shapefieldname = desc.ShapeFieldName
outCS = desc.SpatialReference

unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

# Execute CreateFeatureclass

coordList = []
k=0
rows = arcpy.SearchCursor(in_fc, '', unProjCoordSys)

for row in rows:
    feat = row.getValue(shapefieldname)
    pnt = feat.getPart()
    k+=1
###################################################
    # A list of features and coordinate pairs
    pnt.X=pnt.X
    pnt.Y=pnt.Y
    coordList1 = IGT4SAR_Geodesic.Geodesic(pnt, float(in_bearing), float(in_angle), float(in_dist))
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
    ######################################################
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