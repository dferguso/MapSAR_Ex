#-------------------------------------------------------------------------------
# Name:        TrackOffseteModel.py
# Purpose:     Purpose: This is the track offset model as described in Robert
#  Koester's "Lost Person Behavior: A Search and Rescue Guide on Where to Look
#  - for Land, Air and Water", dbs Publications, Charlottesville, VA.
# Usage:       Clip distance, multiple feature classes
#
# Author:      Don Ferguson
#
# Created:     2/15/2013
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


# Import arcpy module
import arcpy, sys, arcgisscripting
from arcpy import env

gp = arcgisscripting.create()

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

# Overwrite pre-existing files
env.overwriteOutput = "True"

# Script arguments
##workspc = arcpy.GetParameterAsText(0)
##env.workspace = workspc
### Setting the Geoprocessing workspace
##gp.Workspace = workspc

SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
if SubNum == '#' or not SubNum:
    SubNum = "1" # provide a default value if unspecified

ippType = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP

TheoDist = arcpy.GetParameterAsText(2)
if TheoDist == '#' or not TheoDist:
    TheoDist = "0" # provide a default value if unspecified

bufferUnit = arcpy.GetParameterAsText(3) # Desired units
if bufferUnit == '#' or not bufferUnit:
    bufferUnit = "miles" # provide a default value if unspecified


OffDists = arcpy.GetParameterAsText(4)  # Optional - User entered distancesDetermine to use PLS or LKP

OutName = arcpy.GetParameterAsText(5)

Dist = OffDists.split(',')
Distances=map(int,Dist)
Distances.sort()

#File Names:
IPP = "Planning Point"
IPP_dist = "IPPTheoDistance"
Trails = "Trails"
Roads = "Roads"
pStreams ="Streams"
Electric ="PowerLines"

Roads_Clipped = "Roads_Clipped"
Trails_Clipped = "Trails_Clipped"
pStreams_Clipped = "Streams_Clipped"
Electric_Clipped = "Electric_Clipped"
LineTrack = "LinearTracks"
TrackBuffer = "TrackBuffer"


SubNum = int(SubNum)

if bufferUnit =='kilometers':
    mult = 1.6093472
else:
    mult = 1.0
TheoSearch = mult * float(TheoDist)

theDist = "{0} {1}".format(TheoSearch, bufferUnit)

#Clip features to max distance
try:
    arcpy.Delete_management(IPP_dist)
except:
    pass

# Buffer areas of impact around major roads
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
where = where1 + where2

arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)
arcpy.AddMessage("Buffer IPP around the " + ippType )
arcpy.Buffer_analysis(IPP, IPP_dist, theDist)
IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")


#Set extent
desc = arcpy.Describe(IPP_dist)
extent = desc.extent
arcpy.env.extent = IPP_dist

fieldName1 = "TYPE"

#Trails
expression2 = '"TRAIL"'
fcname = Trails
fcClip = Trails_Clipped
fcNoMess ="No Trails"
fcProcessMess = "Clip Trails"

if gp.GetCount_management(fcname) == 0:
    arcpy.AddMessage(fcNoMess)
else:
    arcpy.AddMessage(fcProcessMess)
    arcpy.Clip_analysis(fcname, IPP_dist, fcClip, "")
    arcpy.AddField_management(fcClip, fieldName1, "TEXT", "", "", "10")
    arcpy.CalculateField_management(fcClip, fieldName1, expression2)


#Roads
expression2 = '"ROAD"'
fcname = Roads
fcClip = Roads_Clipped
fcNoMess ="No Roads"
fcProcessMess = "Clip Roads"

if gp.GetCount_management(fcname) == 0:
    arcpy.AddMessage(fcNoMess)
else:
    arcpy.AddMessage(fcProcessMess)
    arcpy.Clip_analysis(fcname, IPP_dist, fcClip, "")
    arcpy.AddField_management(fcClip, fieldName1, "TEXT", "", "", "10")
    arcpy.CalculateField_management(fcClip, fieldName1, expression2)


#Streams
expression2 = '"DRAINAGE"'
fcname = pStreams
fcClip = pStreams_Clipped
fcNoMess ="No Drainages"
fcProcessMess = "Clip Drainages"

if gp.GetCount_management(fcname) == 0:
    arcpy.AddMessage(fcNoMess)
else:
    arcpy.AddMessage(fcProcessMess)
    arcpy.Clip_analysis(fcname, IPP_dist, fcClip, "")
    arcpy.AddField_management(fcClip, fieldName1, "TEXT", "", "", "10")
    arcpy.CalculateField_management(fcClip, fieldName1, expression2)


#Utility Right of Way
expression2 = '"UTILITY"'
fcname = Electric
fcClip = Electric_Clipped
fcNoMess ="No Utility ROWs"
fcProcessMess = "Clip Utility ROWs"

if gp.GetCount_management(fcname) == 0:
    arcpy.AddMessage(fcNoMess)
else:
    arcpy.AddMessage(fcProcessMess)
    arcpy.Clip_analysis(fcname, IPP_dist, fcClip, "")
    arcpy.AddField_management(fcClip, fieldName1, "TEXT", "", "", "10")
    arcpy.CalculateField_management(fcClip, fieldName1, expression2)

arcpy.Delete_management(IPP_dist)

# Create FieldMappings object to manage merge output fields
fms = arcpy.FieldMappings()
# Add all fields from both oldStreets and newStreets
fms.addTable(Roads_Clipped)
fms.addTable(Trails_Clipped)
fms.addTable(pStreams_Clipped)
fms.addTable(Electric_Clipped)

for field in fms.fields:
    if field.name not in ["TYPE"]:
        fms.removeFieldMap(fms.findFieldMapIndex(field.name))

# Use Merge tool to move features into single dataset
arcpy.Merge_management([Roads_Clipped, Trails_Clipped, pStreams_Clipped, Electric_Clipped], LineTrack,fms)


arcpy.Delete_management(Roads_Clipped)
arcpy.Delete_management(Trails_Clipped)
arcpy.Delete_management(pStreams_Clipped)
arcpy.Delete_management(Electric_Clipped)

pDist=[]
for x in Distances:
    pDist.append(round(x * mult,2))

arcpy.AddMessage(pDist)

##try:
arcpy.MultipleRingBuffer_analysis(LineTrack, TrackBuffer, pDist, "Meters", "TRACKOFFSET", "ALL", "FULL")
##
##except:
##    TrackBuf = TrackBuffer
##    arcpy.AddMessage("Loop through the distances")
##    for x in Distances:
##        arcpy.AddMessage(str(x))
##        TrackBuffer = TrackBuf + str(x)
##        dist = str(x) + ' Meters'
##        arcpy.Buffer_analysis(LineTrack, TrackBuffer, dist, "", "", "ALL", "")

arcpy.Delete_management(LineTrack)

#Try to erase water polygon if user as Advanced license

try:
    arcpy.Erase_analysis(TrackBuffer,"Water_Polygon",OutName)
except:
    arcpy.Copy_management(TrackBuffer,OutName)

arcpy.Delete_management(TrackBuffer)

# create a new layer
arcpy.AddMessage('Insert Track Buffer')
insertLayer = arcpy.mapping.Layer(OutName)


