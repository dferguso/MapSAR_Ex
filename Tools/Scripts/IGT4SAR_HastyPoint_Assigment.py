#-------------------------------------------------------------------------------
# Name:        HastyPoint_Assignment.py
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
fc2="Assignments"

fc1="Hasty_Points"
fieldName2="UTM_Easting"
fieldName3="UTM_Northing"

try:
    arcpy.AddMessage(fc1)
    #shapeName = arcpy.Describe(fc1).ShapeFieldName
    #arcpy.AddMessage(fc1)
    rows1 = arcpy.SearchCursor(fc1)
    row1 = rows1.next()

    while row1:
        # you need to insert correct field names in your getvalue function
        Area_Name = row1.getValue("Area_Name")
        arcpy.AddMessage(Area_Name)
        PtA_X = row1.getValue(fieldName2)
        PtA_Y = row1.getValue(fieldName3)
        arcpy.AddMessage(fc1)

        Descrip1 = "Search in / around " + str(Area_Name)
        Descrip2 = " located at: " + str(int(PtA_X)) + " " + str(int(PtA_Y)) + "."

        Descrip = Descrip1 + Descrip2
        arcpy.AddMessage(Descrip)
        rows = arcpy.InsertCursor(fc2)
        x = 1

        while x <= 1:
            row = rows.newRow()
            row.Description = Descrip
            row.Area_Name = Area_Name
            row.Priority = "High"
            row.Status = "Planned"
            rows.insertRow(row)
            x += 1

        del rows
        del row

        row1 = rows1.next()
    del row1
    del rows1

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