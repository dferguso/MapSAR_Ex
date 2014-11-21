#-------------------------------------------------------------------------------
# Name:        IGT4SAR_Watershed.py
# Purpose:
#  This tool identifies the watershed that contains the IPP, as well as the
#  adjacent watershed and watersheds that are "1" watershed away.  The
#  watersheds are labeled as "SAME" if it contains the IPP, "ADJACENT" if it
#  shares a boundary with the "SAME" watershed, and "DISTANT" if it shares a
#  boundary with the "ADJACENT" watershed but not the "SAME" watershed.
#
#  The user must first identify a watershed layer to use as the tool does not
#  estimate the watersheds from a DEM (future).  The prefered watershed size is
#  the WBD-HU12 which can be obtained from the National Hydrologic Dataset
#
#  http://nhd.usgs.gov
#
#  National Map
#  http://viewer.nationalmap.gov/viewer/nhd.html?p=nhd
#

# Author:      Don Ferguson
#
# Created:     12/12/2012
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

wShedLyr = arcpy.GetParameterAsText(3)
if wShedLyr == '#' or not wShedLyr:
    arcpy.AddMessage("You need to provide a valid Watershed Boundary Layer")

fieldList = arcpy.ListFields(wShedLyr)
chckr=0
for field in fieldList:
    if field.name.upper() == 'NAME' and field.type== 'String':
        chckr=1
if chckr==0:
    arcpy.AddError('User provided Watershed data layer must contain a TEXT (String) field titled "NAME" with a unique identifier for each feature.')


#File Names:
IPP = "Planning Point"
waterShed = "Watershed"

############################################
SubNum = int(SubNum)

# Buffer areas of impact around major roads
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
where = where1 + where2

arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)
arcpy.SelectLayerByLocation_management(wShedLyr, "CONTAINS", IPP)
arcpy.Append_management(wShedLyr, waterShed, "NO_TEST")

wshd_fld1 = "NAME"
wshd_fld2 = "CLASSIFICATION"
wshd_fld3 ="POA"
cursor = arcpy.UpdateCursor(waterShed)
for row in cursor:
    HUname = row.getValue(wshd_fld1)
    row.setValue(wshd_fld2,1)
    row.setValue(wshd_fld3, 48)
    cursor.updateRow(row)

where3 ='"NAME" = ' +"'" + HUname + "'"

arcpy.SelectLayerByLocation_management(wShedLyr, "BOUNDARY_TOUCHES", waterShed)
arcpy.SelectLayerByAttribute_management(wShedLyr, "REMOVE_FROM_SELECTION", where3)
arcpy.Append_management(wShedLyr, waterShed, "NO_TEST")

where4 = '"CLASSIFICATION" IS NULL'
HuNm=[HUname]
arcpy.SelectLayerByAttribute_management(waterShed, "NEW_SELECTION", where4)
matchCount = int(arcpy.GetCount_management(waterShed).getOutput(0))
if matchCount > 0:
    cursor = arcpy.UpdateCursor(waterShed, where4)
    for row in cursor:
        row.setValue(wshd_fld2,2)
        row.setValue(wshd_fld3,38/matchCount)
        HUname = row.getValue(wshd_fld1)
        HuNm.append(HUname)
        cursor.updateRow(row)

arcpy.SelectLayerByAttribute_management(wShedLyr, "CLEAR_SELECTION")
arcpy.SelectLayerByAttribute_management(waterShed, "CLEAR_SELECTION")
arcpy.SelectLayerByLocation_management(wShedLyr, "BOUNDARY_TOUCHES", waterShed)

for name in HuNm:
    where5 ='"NAME" = ' +"'" + name + "'"
    arcpy.SelectLayerByAttribute_management(wShedLyr, "REMOVE_FROM_SELECTION", where5)
arcpy.Append_management(wShedLyr, waterShed, "NO_TEST")

arcpy.SelectLayerByAttribute_management(waterShed, "NEW_SELECTION", where4)
matchCount = int(arcpy.GetCount_management(waterShed).getOutput(0))
if matchCount > 0:
    cursor = arcpy.UpdateCursor(waterShed, where4)
    for row in cursor:
        row.setValue(wshd_fld2,3)
        row.setValue(wshd_fld3,13/matchCount)
        cursor.updateRow(row)

arcpy.SelectLayerByAttribute_management(wShedLyr, "CLEAR_SELECTION")
arcpy.SelectLayerByAttribute_management(waterShed, "CLEAR_SELECTION")

del row, HuNm, HUname, matchCount, cursor, name

wshd_fld4 = "AREA_"
wshd_fld5 = "Pden"
express2 ="float(!SHAPE.AREA@ACRES!)"
express3 = 'float(!' + wshd_fld3 + '!/!' + wshd_fld4 +'!)'
arcpy.CalculateField_management(waterShed,wshd_fld4,express2, "PYTHON" )
arcpy.CalculateField_management(waterShed,wshd_fld5,express3, "PYTHON" )

