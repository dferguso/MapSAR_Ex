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


# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"


def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def AddViewFields(in_fc, fldNames):
    obsvrName=[]
    fName=[fldNames[k][0] for k in range(len(fldNames))]
    if int(arcpy.GetCount_management(in_fc).getOutput(0)) > 0:
        fieldnames = [f.name for f in arcpy.ListFields(in_fc)]
        if "OID" in fieldnames:
            OID="OID"
        elif "OBJECTID" in fieldnames:
            OID="OBJECTID"
        else:
            OID=None
        compList=set(fieldnames).intersection(fName)
        compList=list(compList); chkList=list(fName)
        [chkList.remove(kk) for kk in compList]

        #Add field if it does not exist
        for field in fldNames:
            if field[0] in chkList:
                arcpy.AddField_management(*(in_fc,) + field)

        del fieldnames, compList, field
    del fName
    return(chkList)

def getKey(item):
    return(item[1])

def deleteFeature(fcList):
    for gg in fcList:
        if arcpy.Exists(gg):
            try:
                arcpy.Delete_management(wrkspc + '\\' + gg)
            except:
                pass

    return()

def deleteLayer(df,fcLayer):
    for lyr in fcLayer:
        for ii in arcpy.mapping.ListLayers(mxd, lyr):
            try:
                print "Deleting layer", ii
                arcpy.mapping.RemoveLayer(df , ii)
            except:
                pass
    return()

########
# Main Program starts here
#######
if __name__ == '__main__':
# Script arguments
    mxd,df = getDataframe()

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

    Dist = OffDists.split(',')
    Distances=[]
    for k in Dist:
        if ":" in k:
            Distances.append(map(int,k.split(":")))
        else:
            sys.exit(arcpy.AddError("Please use the correct format"))

    sorted(Distances,key=getKey)

    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)
    OutName = "{0}\TrackOffset_{1}".format(wrkspc,timestamp)

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
    ## Corrected an error that would not run script if Trails data layer was empty
    ## DHF - Oct 04, 2013
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
    ## Corrected an error that would not run script if Roads data layer was empty
    ## DHF - Oct 04, 2013
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
    ## Corrected an error that would not run script if Streams data layer was empty
    ## DHF - Oct 04, 2013
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
    ## Corrected an error that would not run script if Powerlines data layer was empty
    ## DHF - Oct 04, 2013
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


    pDist=[]
    for x in Distances:
    ### - Commented Jan 29, 2014 - x should always be in meters so no reason for mult
    #    pDist.append(round(x * mult,2))
        pDist.append(round(x[0],2))
    arcpy.AddMessage(pDist)

    ##try:
    arcpy.MultipleRingBuffer_analysis(LineTrack, TrackBuffer, pDist, "Meters", "TRACKOFFSET", "ALL", "FULL")
    ##TrackOff = arcpy.MultipleRingBuffer_analysis(LineTrack, TrackBuffer, pDist, "Meters", "TRACKOFFSET", "ALL", "FULL")

    ##
    ##except:
    ##    TrackBuf = TrackBuffer
    ##    arcpy.AddMessage("Loop through the distances")
    ##    for x in Distances:
    ##        arcpy.AddMessage(str(x))
    ##        TrackBuffer = TrackBuf + str(x)
    ##        dist = str(x) + ' Meters'
    ##        arcpy.Buffer_analysis(LineTrack, TrackBuffer, dist, "", "", "ALL", "")

    #Try to erase water polygon if user as Advanced license

    try:
        arcpy.Erase_analysis(TrackBuffer,"Water_Polygon",OutName)
    except:
        arcpy.Copy_management(TrackBuffer,OutName)

    delFC=[Roads_Clipped,Trails_Clipped,pStreams_Clipped,Electric_Clipped,LineTrack,TrackBuffer,IPP_dist]
    deleteFeature(delFC)

    # Add Probability Field to TrackOffset
    arcpy.AddField_management(OutName, "PROBABILITY", "FLOAT")
    cursor=arcpy.UpdateCursor(OutName)
    for row in cursor:
        chCk=row.getValue("TRACKOFFSET")
        chCkr=[k[1] for k in Distances if k[0]==chCk]
        row.setValue("PROBABILITY",chCkr[0])
        cursor.updateRow(row)

    # create a new layer
    arcpy.AddMessage('Insert Track Buffer')
    insertLayer=arcpy.mapping.Layer(OutName)

    #Insert layer into Reference layer Group
    arcpy.AddMessage("Add layer to '13 Incident_Analysis'")

    LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
    LyrName=[]
    for lyr in LyrList:
        LyrName.append(lyr.name)

    if "Track Offset" in LyrName:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'Track Offset',df)[0]
    else:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]

    arcpy.mapping.AddLayerToGroup(df, refGroupLayer, insertLayer,'BOTTOM')

    try:
        symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\Track_Offset.lyr"
        arcpy.ApplySymbologyFromLayer_management(insertLayer.name, symbologyLayer)
    except:
        pass


