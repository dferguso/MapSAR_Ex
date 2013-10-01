#-------------------------------------------------------------------------------
# Name:        PSR_Updates.py
# Purpose:  Estimate the Probability of Success Rate for a given segment along
#  with an estimate Probability of Detection for a given resource type and
# search time.
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

#workspc = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc0 = "PODImpactZones"
fc1 = "EffectiveSweepWidth"
fc2 = "Search_Segments"

rows1 = arcpy.UpdateCursor(fc2)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    AreaName = row1.Area_Name
    where0 = '"Area_Name" = ' + "'" + str(AreaName) + "'"
    if arcpy.Exists(fc0):
        arcpy.AddMessage(fc0)
        rows0 = arcpy.SearchCursor(fc0, where0)
        row0 = rows0.next()
        while row0:
            # you need to insert correct field names in your getvalue function
            PODfactor = row0.Mean/10
            row0 = rows0.next()
        del rows0
        del row0
    else:
        PODfactor = 1.0

    resourceType = row1.ResourceType_PSR
    where2 = '"ResourceType" = ' + "'" + str(resourceType) + "'"
    #arcpy.AddMessage(resourceType)
    rows2 = arcpy.SearchCursor(fc1, where2)
    row2 = rows2.next()

    #arcpy.AddMessage(resoureType)
    while row2:
        # you need to insert correct field names in your getvalue function
        TeamSize = row2.TeamSize
        SearchSpeed = row2.SearchSpeed_mph
        SweepWidth = row2.SweepWidth_m
        row2 = rows2.next()
    del rows2
    del row2

    SearchTime = row1.SearchTime_hr
    SegArea = row1.Area
    if SearchTime > 0:
        CoveragePSR = SearchSpeed*1609.344*SweepWidth*PODfactor*TeamSize*SearchTime/SegArea/4046.87261
    else:
        CoveragePSR = row1.Coverage_PSR
    POAcum = row1.POAcum
    PODest = (1-math.exp(-CoveragePSR))*100

    row1.Coverage_PSR = CoveragePSR
    row1.PSR = CoveragePSR * POAcum
    row1.PODest = PODest

    rows1.updateRow(row1)
    row1 = rows1.next()

del where2
del TeamSize
del SearchSpeed
del SweepWidth
del SearchTime
del SegArea
del CoveragePSR
del PODest
del rows1
del row1