#-------------------------------------------------------------------------------
# Name:        IGT4SAR_TopoPositionIndex.py
# Purpose:
#  Relative topographic position (also called the Topographic Position Index) is
#  a terrain ruggedness metric and a local elevation index (Jenness, 2002).
#  Topographic position of each pixel is identified with respect to its local
#  neighborhood, thus its relative position. The index is useful for identifying
#  landscape patterns and boundaries that may correspond with rock type, dominant
#  geomorphic process, soil characteristics, vegetation, or air drainage.
#  Classify the final output raster into high, medium, low based on natural breaks

# Author:      Don Ferguson
#
# Created:     09/25/2015
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

# Import arcpy module
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
try:
    math
except NameError:
    import math
try:
    arcpy.mapping
except NameError:
    import arcpy.mapping
import datetime
import arcgisscripting, os
from arcpy import env
from arcpy.sa import *

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")
ProdInfo=arcpy.ProductInfo()

# Environment variables
out_fc = os.getcwd()
arcpy.env.workspace
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
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    DEM = arcpy.GetParameterAsText(0)
    if DEM == '#' or not DEM:
        arcpy.AddError("You need to provide a valid DEM")

    nEighborSize = float(arcpy.GetParameterAsText(1))
    if nEighborSize == '#' or not nEighborSize:
        nEighborSize = 10.0
#############################################
# TPI(DEM) = (MEAN - MIN) / (MAX - MIN)
    MinDEM = FocalStatistics(DEM, NbrCircle(nEighborSize, "CELL"),"MINIMUM", "NODATA")
    MaxDEM = FocalStatistics(DEM, NbrCircle(nEighborSize, "CELL"),"MAXIMUM", "NODATA")
    MeanDEM = FocalStatistics(DEM, NbrCircle((2.5*nEighborSize), "CELL"),"MEAN", "NODATA")
    outTPI = (MeanDEM - MinDEM) / (MaxDEM - MinDEM)
    TPI = "TPI_{0}".format(timestamp)
    outTPI.save(TPI)
    del outTPI, MinDEM, MaxDEM, MeanDEM

    insertLayer=arcpy.mapping.Layer(TPI)
    try:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]
        arcpy.mapping.AddLayerToGroup(df, refGroupLayer, insertLayer,'BOTTOM')
    except:
        arcpy.mapping.AddLayer(df, insertLayer,'TOP')

    arcpy.AddMessage("Modify the Classified Symbology to highlight ridgetops and valley bottom")
    arcpy.AddMessage("Recommendation: 3 element classification - 0.25, 0.75, 1.0\n")

    try:
        # Set layer that output symbology will be based on
        symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\TPI.lyr"

        # Apply the symbology from the symbology layer to the input layer
        updateLayer = arcpy.mapping.ListLayers(mxd, insertLayer, df)[0]
        arcpy.ApplySymbologyFromLayer_management (updateLayer, symbologyLayer)
    except:
        pass

