#-------------------------------------------------------------------------------
# Name:        Coverage_Model.py
# Purpose:   This tool is designed to calaculate the Coverage area of a segment
#  based on a buffered GPS track sored in the Routes Feature class.  The
#  buffered track is determined by the team size and sweep width entered in the
#  Assignment_Debrief feature class.  Once the buffered tracked is determined it
#  is intersected and dissolved for each Search Segment and Probability Region.
#  The area of the dissolved track is determined and compared to the area of the
#  segment or region to determine coverage.  All of the tracks are included each
#  time this tool is run.
#
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
#!/usr/bin/env python

# Import arcpy module
import arcpy
import string
import math

#workspc = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1 = "Routes_Line"
fc2 = "Debriefing"
fc3 = "Search_Segments"
fc4 = "GPS_Data\GPSBuffer"
fc5 = "GPS_Data\GPSBuffer_Intersect"
fc7 = "Probability_Regions"

# Set local variables
fieldName0 = "MilageOfTrack"
fieldName1 = "Area_1"
fieldPrecision = 9
fieldName2 = "Area_Name"
fieldName3= "Coverage"
fieldName4 = "Area_seg"
fieldName5 = "Region_Name"
fieldName6 = "PODTheo"
fieldName7 = "POStheo"

try:
    arcpy.Delete_management(fc4)
except:
    pass
try:
    arcpy.Delete_management(fc5)
except:
    pass

check = "False"
fieldList = arcpy.ListFields(fc1)
for field in fieldList:
    if (field.name == "Sweep"):
        check="True"

if check != "True":
    arcpy.AddField_management(fc1, "Sweep", "FLOAT", fieldPrecision, "", "", "Sweep", "NULLABLE")

rows1 = arcpy.UpdateCursor(fc1)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    AssignNumber = row1.Assignment_Number
    where2 = '"Assignment_Number" = ' + "'" + str(AssignNumber) + "'"
    rows2 = arcpy.SearchCursor(fc2, where2)
    row2 = rows2.next()

    arcpy.AddMessage(AssignNumber)

    while row2:
        # you need to insert correct field names in your getvalue function
        TeamSize = row2.Team_Size
        SweepWidth = row2.SweepWidth_m
        GPSLoc = row2.GPSLoc
        Sweep = TeamSize * SweepWidth*2.0
        row1.Sweep = Sweep
        row2 = rows2.next()

    del where2
    del row2
    del rows2
###############################################################################
    row1.Processed = 1
###############################################################################
##    if GPSLoc == "Left":
##        GPSLoc = "LEFT"
##    elif GPSLoc == "Right":
##        GPSLoc = "RIGHT"
##    else:
##        GPSLoc = "FULL"
##    row1.GPSLoc = GPSLoc

    rows1.updateRow(row1)
    row1 = rows1.next()

del row1
del rows1

arcpy.AddMessage(" ")
arcpy.AddMessage("Calculate length of GPS tracks.")
arcpy.AddMessage(" ")
expression0 = "!shape.length@miles!"
arcpy.CalculateField_management(fc1, fieldName0, expression0,"PYTHON")

arcpy.AddMessage("Buffer GPS tracks to account for sweepwidth and team size.")
arcpy.AddMessage(" ")
# Buffer areas around GPS track
bufferUnit = "meters"
distanceField = "TeamSweep_m"
sideType = "GPSLoc"
dissolveType = "NONE"
arcpy.Buffer_analysis(fc1, fc4, Sweep, "","", dissolveType, "")

arcpy.DeleteField_management(fc1, "Sweep")


arcpy.AddMessage("Intersection analysis between GPS tracks and Search Segments")
arcpy.AddMessage(" ")
# Process: Intersect
inFeatures = [fc4, fc3]
arcpy.Intersect_analysis(inFeatures, fc5, "ALL", "", "INPUT")

# Set the local parameters

# Execute AddField
arcpy.AddField_management(fc5, fieldName1, "FLOAT", fieldPrecision, "", "", fieldName1, "NULLABLE")

arcpy.AddMessage("Verify areas of Search Segments and buffered tracks-post intersect")
arcpy.AddMessage(" ")
expression1="!shape.area@acres!"
arcpy.CalculateField_management(fc5, fieldName1, expression1,"PYTHON")
arcpy.CalculateField_management(fc3, fieldName4, expression1,"PYTHON")
##
### Join two feature classes by the zonecode field and only carry
### over the land use and land cover fields

arcpy.AddMessage("Calculate the Coverage = Area Searched / Segment Area")
arcpy.AddMessage(" ")


rows2 = arcpy.UpdateCursor(fc3)
row2 = rows2.next()
Cover = 0.0

while row2:
    AreaName = row2.Area_Name
    AreaSeg = row2.Area_seg
    where3 = '"Area_Name" = ' + "'" + AreaName + "'"

    if AreaSeg == None:
        arcpy.AddMessage("Segment: " +AreaName + ", area is Null")
    elif AreaSeg == 0.0:
        arcpy.AddMessage("Segment: " +AreaName + ", area is zero")
    else:
        AreaCov = 0.0
        rows3 = arcpy.SearchCursor(fc5,where3)
        row3 = rows3.next()

        while row3:
            AreaCov = AreaCov + row3.Area_1
            row3 = rows3.next()

        Cover = AreaCov/AreaSeg
        del AreaCov
        del row3
        del rows3

    row2.Coverage = Cover
    rows2.updateRow(row2)
    row2 = rows2.next()

del row2
del rows2
del AreaSeg
del AreaName


arcpy.AddMessage("Calculate theoretical POD based on Coverage")
arcpy.AddMessage(" ")

#Calculate theoretical POS based on Coverage and POAcum
expression3 = "(1-math.exp(-!Coverage!))*100.0"
arcpy.CalculateField_management(fc3, fieldName6, expression3,"PYTHON")
##
##
##try:
##    arcpy.Delete_management(fc4)
##except:
##    pass
##try:
##    arcpy.Delete_management(fc5)
##except:
##    pass


rows2 = arcpy.UpdateCursor(fc7)
row2 = rows2.next()

arcpy.AddMessage("Determine theoretical POS based on measured")
arcpy.AddMessage("Coverage for Probability Regions")
arcpy.AddMessage(" ")
while row2:
    RegName = row2.Region_Name
    AreaReg = row2.Area
    where3 = '"Region_Name" = ' + "'" + RegName + "'"
    Cover = 0.0
    #arcpy.AddMessage(RegName)
    rows3 = arcpy.SearchCursor(fc3,where3)
    row3 = rows3.next()

    while row3:
        AreaSeg = row3.Area_seg
        Cover = Cover + row3.Coverage * AreaSeg
        del AreaSeg
        row3 = rows3.next()

    if AreaReg > 0.0:
        row2.Coverage = Cover/AreaReg
    else:
        row2.Coverage = 0.0
    #Calculate theoretical POS based on Coverage and POAcum
    expression4 = "!POA! * (1-math.exp(-!Coverage!))"
    arcpy.CalculateField_management(fc7, fieldName7, expression4,"PYTHON")

    del AreaReg
    del RegName
    del Cover
    del row3
    del rows3
    rows2.updateRow(row2)
    row2 = rows2.next()

del row2
del rows2
del expression0
del expression1
del expression3
del expression4

##
##del AssignNumber
##del rows1
##del row1
##del fc1
##del fc2
