#-------------------------------------------------------------------------------
# Name:        HastyLine_Assignment.py
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
SegmentName = arcpy.GetParameterAsText(0)  # Get the subject number
if SegmentName == '#' or not SegmentName:
    arcpy.AddMessage("You need to select a Track - Quick response Task")

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"



##fc1="Hasty_Segments"
fc1="Hasty_Line"
fc2="Assignments"

fieldName1="Length_miles"
fieldName2="PointA_X"
fieldName3="PointA_Y"
fieldName4="PointB_X"
fieldName5="PointB_Y"
expression2 = "float(!shape.firstpoint!.split()[0])"
expression3 = "float(!shape.firstpoint!.split()[1])"
expression4 = "float(!shape.lastpoint!.split()[0])"
expression5 = "float(!shape.lastpoint!.split()[1])"


# Get a list of areas that have already been assigned
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
    where1 = ('"Area_Name" = \'{0}\''.format(SegName.replace("'","")))
    rows1 = arcpy.SearchCursor(fc1,where1)
    row1 = rows1.next()

    while row1:
        try:
            Area_Name = row1.getValue("Area_Name")
            Area_Name.encode('ascii','ignore')
            arcpy.AddMessage("Segment: " + Area_Name)

            arcpy.CalculateField_management(fc1, fieldName1, "!SHAPE.length@miles!", "PYTHON")
            arcpy.CalculateField_management(fc1, fieldName2, expression2, "PYTHON")
            arcpy.CalculateField_management(fc1, fieldName3, expression3, "PYTHON")
            arcpy.CalculateField_management(fc1, fieldName4, expression4, "PYTHON")
            arcpy.CalculateField_management(fc1, fieldName5, expression5, "PYTHON")
            Length_miles = row1.getValue("Length_miles")
            Type = row1.getValue("Type")
            PtA_X = row1.getValue("PointA_X")
            PtA_Y = row1.getValue("PointA_Y")
            PtB_X = row1.getValue("PointB_X")
            PtB_Y = row1.getValue("PointB_Y")
        ##    feat = row1.getValue(shapeName)
        ##    #pnt = feat.getPart()
        ##
        ##    # Print x,y coordinates of current point
        ##    #
        ##    #print pnt.X, pnt.Y
        ##
        ##    fpointX = int(feat.firstPoint.X)
        ##    fpointY = int(feat.firstPoint.Y)
        ##    lpointX = int(feat.lastPoint.X)
        ##    lpointY = int(feat.lastPoint.Y)

            Descrip1 = "Search along " + Area_Name + " for a distance of " + str(int(Length_miles*100.0)/100.0) + " miles"
            Descrip2 = " between point 1: " + str(int(PtA_X)) + " " + str(int(PtA_Y)) + ", and point2: "
            Descrip3 = str(int(PtB_X)) + " " +str(int(PtB_Y)) + "."
            Descrip4 = "  Sweep 10 - 20 ft on each side of road/trail.  Look for decision points and location where someone may leave the trail."

            Descrip = Descrip1 + Descrip2 + Descrip3 + Descrip4
            rows = arcpy.InsertCursor(fc2)

            x = 1

            while x <= 1:
                row = rows.newRow()
                row.Description = Descrip
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
                x += 1

            del rows
            del row

        except:
            # Get the tool error messages
            #
            msgs = ("There was an error with {0}".format(where1))

            # Return tool error messages for use with a script tool
            #
            arcpy.AddError(msgs)
            # Print tool error messages for use in Python/PythonWin
            #
            print msgs
        row1 = rows1.next()

    del row1
    del rows1

arcpy.AddMessage("\n")
