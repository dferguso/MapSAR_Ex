#-------------------------------------------------------------------------------
# Name:        TableExport.py
# Purpose: Export feature classes to Tables
#
# Author:      Don Ferguson
#
# Created:     02/03/2013
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

import arcpy

def remove_from_list(the_list, val):
    return [value for value in the_list if value.name.upper() != val.upper()]

def writeTable(table, outtable):
    #--make a list of all the fields in the table
    fields = arcpy.ListFields(table)
    #--remove items from list
    rmFields=["OBJECTID","SHAPE","TimeSlider","SHAPE_Length","Shape","Shape_Area","Display"]
    for rmField in rmFields:
        fields = remove_from_list(fields, rmField)

    del rmField
    del rmFields

    kk= 1
    ff=open(outtable, 'w')
    for field in fields:
        #--write all field names to the output file
        fldname = str(field.name).replace(',','.')
        if kk < len(fields):
            ff.write('{0}, '.format(fldname))
            kk+=1
        else:
            ff.write('{0}\n'.format(fldname))

    #--now we make the search cursor that will iterate through the rows of
    #--the table
    try:
        rows = arcpy.SearchCursor(table)
        for row in rows:
            kk = 1
            for field in fields:
                fldname1 = str(row.getValue(field.name))
                fldname = fldname1.replace(',','.')
                if kk < len(fields):
                    ff.write('{0}, '.format(fldname))
                    kk +=1
                else:
                    ff.write('{0}\n'.format(fldname))
        del rows
        del row
    except:
        pass

    del kk
    del field
    del fields
    ff.close()


########
# Main Program starts here
#######

#in_fc  - this is a point feature used to get the latitude and longitude of point.
outFolder = arcpy.GetParameterAsText(0)
if outFolder == '#' or not outFolder:
    arcpy.AddMessage("You need to provide a valid output folder")


Group = ["Incident","Operations", "Planning", "Resources_Comms"]
TableName = [["Plan_Point", "Found", "Incident_Info", "Incident_Staff",
    "Lead_Agency", "Plan_Point", "RP", "Subject_Information"],
    ["Air_operations", "Assignments", "Clues_Point", "Debriefing", "Teams",
    "Operation_Period", "Team_Members"], ["Hasty_Line", "Hasty_Points",
    "Hasty_Segments", "Probability_Regions", "Scenarios", "Search_Segments"],
    ["Assets", "Radio_Log", "Resource_Status"]]

kk=0
for grp in Group:
    arcpy.AddMessage(grp + " Group")
    for tbl in TableName[kk]:
        TableIn = grp + "\\" + tbl
        TableOut = outFolder + '\\' + tbl + ".txt"
        writeTable(TableIn, TableOut)
    kk+=1