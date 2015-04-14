#-------------------------------------------------------------------------------
# Name:        IGT4SAR_FeatureExport.py
# Purpose: Export feature class layers from the current map
#
# Author:      Don Ferguson
#
# Created:     04/09/2015
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


'''
for lyr in arcpy.mapping.Lfor lyr in arcpy.mapping.ListLayers(mxd, "*", df):
...     if lyr.isFeatureLayer:
...         print lyr.name
'''
try:
    arcpy
except NameError:
    import arcpy

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass


########
# Main Program starts here
#######

#in_fc  - this is a point feature used to get the latitude and longitude of point.
outFolder = arcpy.GetParameterAsText(0)
if outFolder == '#' or not outFolder:
    arcpy.AddMessage("You need to provide a valid output folder")

layerNames = arcpy.GetParameterAsText(1)
layerNames = layerNames.split(";")

# Execute FeatureClassToGeodatabase
arcpy.FeatureClassToShapefile_conversion(layerNames, outFolder)