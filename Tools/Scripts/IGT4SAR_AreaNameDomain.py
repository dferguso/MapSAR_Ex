#-------------------------------------------------------------------------------
# Name:        AreaNameDomain.py
# Purpose:     Updates the list of names for search areas.  Values obtained from
#  Hasty Points, Hasty Lines, Hasty Segments and Search Segments
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

workspc = arcpy.GetParameterAsText(0)

arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

def appendName(pFeat,myList):
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        AName_list=[]
        while row1:
            AName = row1.getValue("Area_Name")
            AName_list.append(AName)
            #arcpy.AddMessage(AName)

            row1 = rows1.next()
        del row1
        del rows1
        AName_list.sort()
        myList.extend(AName_list)
    else:
        arcpy.AddMessage("No features in " + pFeat)
    return myList


########
# Main Program starts here
#######

fc1= "Area_Names"
fc = ["Hasty_Points", "Hasty_Line", "Hasty_Segments", "Search_Segments"]
myList =[]

#arcpy.AddMessage("Area Name ")
#try:
for pFeat in fc:
    appendName(pFeat,myList)

# Remove duplicates by turning the list into a set and
# then turning the set back into a list

checked=[]
for j in myList:
    if j not in checked:
        checked.append(j)

myList = checked
del checked

arcpy.DeleteRows_management(fc1)

for xd in myList:
    arcpy.AddMessage(xd)

    rows = arcpy.InsertCursor(fc1)

    row = rows.newRow()
    row.Area_Name = xd
    rows.insertRow(row)

    del rows
    del row

domTable = fc1
codeField = "Area_Name"
descField = "Area_Name"
dWorkspace = workspc
domName = "Area_Names"
domDesc = "Search area names"


# Process: Create a domain from an existing table
arcpy.TableToDomain_management(domTable, codeField, descField, dWorkspace, domName, domDesc,"REPLACE")


del fc1



##except:
##    # Get the tool error messages
##    #
##    msgs = "All tasks have been processed"
##
##    # Return tool error messages for use with a script tool
##    #
##    arcpy.AddWarning(msgs)
##    # Print tool error messages for use in Python/PythonWin
##    #
##    print msgs
