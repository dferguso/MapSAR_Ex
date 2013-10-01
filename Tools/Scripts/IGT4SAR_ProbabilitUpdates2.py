#-------------------------------------------------------------------------------
# Name:        ProbabilityUpdates.py
# Purpose: Update POAcum, POScum_Responsive and POScum_Unreponsive in both
#  Segments and regions.  POAcum based on unresponsive subject.  Also updated
#  Segment status and # of times searched based on Assignment Debrief info
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

fc1 = "Debriefing"
fc3 = "Search_Segments"
fc4 = "Assignments"

where1 = '"Recorded" = 0'


POCN=[]
rows1 = arcpy.SearchCursor(fc3)
row1 = rows1.next()

# Get the previous POC for each Segment and sum together
while row1:
    POCN.append(row1.POC_Now)
    row1 = rows1.next()
pocSum=sum(POCN)
del row1
del rows1


rows1 = arcpy.UpdateCursor(fc1, where1)
row1 = rows1.next()

if not row1:
    msgs = "All tasks have been processed"
    arcpy.AddWarning(msgs)

# Get the Area Names and POD values for Segments that had tasks performed
while row1:
    AreaName = row1.Area_Searched
    PODunrep = row1.POD_Unresponsive
    PODrep = row1.POD_Response
    AssignNum = row1.Assignment_Number

    where4= '"Assignment_Number" = ' + "'" + AssignNum + "'"

    try:
        rows4 = arcpy.UpdateCursor(fc4, where4)
        row4 = rows4.next()
        while row4:
            row4.Status = "Complete"
            rows4.updateRow(row4)
            row4 = rows4.next()
        del row4
        del rows4
    except:
        arcpy.AddMessage("Did not update status for " + AssignNum)


#   Open Segments and update POD, POC only for the Segments that had tasks performed
    where3 = '"Area_Name" = ' + "'" + AreaName + "'"

    try:
        rows3 = arcpy.UpdateCursor(fc3, where3)
        row3 = rows3.next()
        while row3:
            #Reponsive POD - add the new POD to the existing POD for the segment to get cumulative POD
            row3.PODcum = (1-(1-row3.PODcum/100.0)*(1-PODrep/100.0))*100.0
            #Unreponsive POD - add the new POD to the existing POD for the segment to get cumulative POD
            row3.PODcumunrsp = (1-(1-row3.PODcumunrsp/100.0)*(1-PODunrep/100.0))*100.0

            #Now calculate POS for the segment which is only used to determine the new POC (unresponsive POD is used)
            POSi = row3.POC_Now * PODunrep/100.0
            #Need a new total for the sum of POC excluding the current value, accounting
            #for multiple tasks occuring in the same segment during the same update
            POCt = pocSum-row3.POC_Now
            #Record the new POC for the segment
            row3.POC_Now = row3.POC_Now - POSi

            row3.Searched = row3.Searched + 1
            row3.Status = "Complete"
            rows3.updateRow(row3)
            row3 = rows3.next()

        del row3
        del rows3

    except:
        if len(where3)==0:
            msgs = "All tasks have been processed"
            arcpy.AddWarning(msgs)
        else:
            msgs = "An error occurred, please check Assignment_Debrief data fields"
            arcpy.AddWarning(msgs)
    del PODrep
    del PODunrep

    try:
        rows3 = arcpy.UpdateCursor(fc3)
        for row3 in rows3:
            # Obtain the new POA for the segment that was searched
            # will be lower the previous
            if row3.Area_Name == AreaName:
                POCNew = row3.POC_Now
            else:
            # For all other segments not searched the POA should go up
                POCNew=row3.POC_Now*(1 + POSi/POCt)
            row3.POC_Now = (round(POCNew,2))
            AreaSeg = row3.Area_seg
            if AreaSeg != 0.0:
                PdenS = round(POCNew/AreaSeg,3)
            else:
                PdenS = 0.0
            row3.Pden = PdenS
            rows3.updateRow(row3)

        del row3
        del rows3
        del POCNew
        del POCt
        del POSi
        del AreaName

    except:
        # Get the tool error messages
        #
        msgs = "No tasks processed for " + where3

        # Return tool error messages for use with a script tool
        #
        arcpy.AddWarning(msgs)
        # Print tool error messages for use in Python/PythonWin
        #
        print msgs

    row1.Recorded = "1"
    rows1.updateRow(row1)
    row1 = rows1.next()

del rows1
del row1
del where1
del fc1
del fc3
del POCN


####  Now do the Probability Regions

fc1 = "Probability_Regions"
fc2 = "Search_Segments"

rows1 = arcpy.UpdateCursor(fc1,"","","",sort_fields="Region_Name A")
row1 = rows1.next()

while row1:
    RegionName = row1.Region_Name
    pocOld = row1.POAcum
    POCcum = 0.0
    POScum = 0.0
    POScumUn = 0.0
    PdenReg = 0.0
    where2 = '"Region_Name" = ' + "'" + RegionName + "'"
    rows2 = arcpy.SearchCursor(fc2, where2)
    row2 = rows2.next()

    while row2:
        POCcum = POCcum + row2.POC_Now
        PdenReg = PdenReg + row2.Pden
        POScum = POScum + row2.PODcum/100.0*row2.sPOC_Orig
        POScumUn = POScumUn + row2.sPOC_Orig * row2.PODcumunrsp/100.0
        row2 = rows2.next()

    del where2
    del row2
    del rows2
    arcpy.AddMessage("{0}  Previous POA: {1},  New POA: {2}".format(RegionName, str(round(pocOld,2)),str(round(POCcum,2)) ))
    row1.POAcum = round(POCcum,2)
    row1.POScum = round(POScum,2)
    row1.POScumUn = round(POScumUn,2)
    row1.Pden = round(PdenReg,3)


    rows1.updateRow(row1)
    row1 = rows1.next()

arcpy.AddMessage("DONE")

del POCcum
del POScum
del POScumUn

del RegionName
del rows1
del row1


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
