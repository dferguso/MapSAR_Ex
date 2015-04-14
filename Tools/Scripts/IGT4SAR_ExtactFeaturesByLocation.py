#-------------------------------------------------------------------------------
# Name: IGT4SAR_ExtactFeaturesByLocation.py
# Purpose: Extract features to a new feature class based on a Location and an attribute query
#
# Author:      Don Ferguson
#
# Created:     06/19/2014
# Copyright:   (c) Don Ferguson 2014
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
from arcpy import env

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT')
        frame = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,frame)

    except SystemExit as err:
            pass

if __name__ == '__main__':
    mxd, df = getDataframe()

    SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
    if SubNum == '#' or not SubNum:
        SubNum = "1" # provide a default value if unspecified

    ippType = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP

    sourceLayer = arcpy.GetParameterAsText(2) # Desired units

    TheoDist = arcpy.GetParameterAsText(3)
    if TheoDist == '#' or not TheoDist:
        TheoDist = "0" # provide a default value if unspecified

    bufferUnit = arcpy.GetParameterAsText(4) # Desired units
    if bufferUnit == '#' or not bufferUnit:
        bufferUnit = "miles" # provide a default value if unspecified

##    targetLayer = arcpy.GetParameterAsText(5) # Desired units

    # Variables
    IPP = "Planning Point"
    SubNum = int(SubNum)

    theDist = "{0} {1}".format(TheoDist, bufferUnit)


    where1 = '"Subject_Number" = ' + str(SubNum)
    where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
    whereAll = where1 + where2

    arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", whereAll)


    arcpy.SelectLayerByLocation_management(sourceLayer, 'WITHIN_A_DISTANCE', IPP, theDist)
    arcpy.SelectLayerByAttribute_management(IPP, "CLEAR_SELECTION")

    # If features matched criteria write them to a new feature class
    matchcount = int(arcpy.GetCount_management(sourceLayer).getOutput(0))
    if matchcount == 0:
        arcpy.AddMessage('no features matched spatial and attribute criteria')
    else:
        arcpy.AddMessage('{0} features matched criteria'.format(
                                                      matchcount))

