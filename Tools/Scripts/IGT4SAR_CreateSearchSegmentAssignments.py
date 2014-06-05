#-------------------------------------------------------------------------------
# Name:        CreateSearchSegmentAssignment.py
#
# Purpose: Create Quick Response Task stored in the Assignments layer from a
#  "Hasty Point" feature.
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

#workspc = arcpy.GetParameterAsText(0)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

##fc1="Hasty_Segments"
fc1="Search Segments"
fc2="Assignments"

fieldName1="Area_Description"

rows1 = arcpy.SearchCursor(fc1)
row1 = rows1.next()

while row1:
    # you need to insert correct field names in your getvalue function
    Area_Name = row1.getValue("Area_Name")
    Area_Description = row1.getValue(fieldName1)

    rows = arcpy.InsertCursor(fc2)

    row = rows.newRow()
    row.Description = Area_Description
    row.Area_Name = Area_Name
    try:
        row.Priority = "High"
    except:
        pass
    row.Status = "Planned"
    row.Map_Scale = 24000
    row.Create_Map = "Yes"
    row.Create_gpx = "Yes"
    row.Previous_Search = "No"
    arcpy.AddMessage(Area_Name)
    rows.insertRow(row)

    del rows
    del row

    row1 = rows1.next()

del row1
del rows1
