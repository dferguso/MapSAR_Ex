#-------------------------------------------------------------------------------
# Name:        CreateSearchSegmentAssignment.py
#
# Purpose: Create Search Segment Task stored in the Assignments layer from a
#  "Hasty Segment" or "Search Segment" feature.
#
# Author:      Don Ferguson
#
# Created:     06/25/2012
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

# Take courage my friend help is on the way
import arcpy

SegmentName = arcpy.GetParameterAsText(0)  # Get the subject number
if SegmentName == '#' or not SegmentName:
    arcpy.AddMessage("You need to select a Segment")

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc1="Search_Segments"
fc2="Assignments"
fc4 = "Hasty_Segments"

fieldName1="Area_Description"

SSeg = []
rows1 = arcpy.SearchCursor(fc1)
row1 = rows1.next()
while row1:
    AreaN =row1.Area_Name
    AreaN.encode('ascii','ignore')
    SSeg.append(AreaN)
    row1 = rows1.next()

HSeg = []
rows1 = arcpy.SearchCursor(fc4)
row1 = rows1.next()
while row1:
    AreaN =row1.Area_Name
    AreaN.encode('ascii','ignore')
    HSeg.append(str(AreaN))
    row1 = rows1.next()

Areas=[]
rows1 = arcpy.SearchCursor(fc2)
row1 = rows1.next()
while row1:
    AreaN =row1.Area_Name
    AreaN.encode('ascii','ignore')
    Areas.append(AreaN)
    row1 = rows1.next()

fc3 = "Operation_Period"
Perd=[0]
Safety = " "
rows1 = arcpy.SearchCursor(fc3)
row1 = rows1.next()
while row1:
    Perd.append(row1.Period)
    Safety = row1.Safety_Message
    row1 = rows1.next()
OpPerid = max(Perd)
if OpPerid==0:
    arcpy.AddMessage('No Operational Period Established - Default to 0')

arcpy.AddMessage("\n")


SName = SegmentName.split(";")
for SegName in SName:
    SegName.encode('ascii','ignore')
    SgName = SegName.replace("'","")
    where1 = ('"Area_Name" = \'{0}\''.format(SgName))
    try:
    #########3
    ## Search Segments
        if SgName in SSeg:
            rows1 = arcpy.UpdateCursor(fc1,where1)
            row1 = rows1.next()
            while row1:
                Area_Name = row1.getValue("Area_Name")
                Area_Name.encode('ascii','ignore')
                arcpy.AddMessage("Segment: " + Area_Name)
                Area_Description = row1.getValue(fieldName1)
                row1.Status = "Planned"
                rows1.updateRow(row1)
                row1 = rows1.next()
            del row1, rows1

        elif SgtName in HSeg:
            rows1 = arcpy.SearchCursor(fc4,where1)
            row1 = rows1.next()
            while row1:
                Area_Name = row1.getValue("Area_Name")
                Area_Name.encode('ascii','ignore')
                arcpy.AddMessage("Segment: " + Area_Name)
                Area_Description = ""
                row1 = rows1.next()
            del row1, rows1

        rows = arcpy.InsertCursor(fc2)
        row = rows.newRow()
        row.Description = Area_Description
        row.Area_Name = Area_Name
        try:
            row.Priority = "High"
        except:
            pass

        if OpPerid>0:
            row.Period = OpPerid
            row.Safety_Note = Safety

        row.Status = "Planned"
        row.Map_Scale = 24000
        row.Create_Map = "Yes"
        row.Create_gpx = "Yes"
        if Area_Name in Areas:
            row.Previous_Search = "Yes"
        else:
            row.Previous_Search = "No"
        rows.insertRow(row)

        del rows
        del row

    except:
        # Get the tool error messages
        #
        msgs = "There was an error"

        # Return tool error messages for use with a script tool
        #
        arcpy.AddError(msgs)
        # Print tool error messages for use in Python/PythonWin
        #
        print msgs

arcpy.AddMessage("\n")