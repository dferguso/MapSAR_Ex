#-------------------------------------------------------------------------------
# Name:        StreamInterface.py
# Purpose:     Terrain analysis of SAR incidents have identified the trail-stream
#              interface as being a high probable location to find a lost
#              subject in a wilderness environment (Jacobs, M., "Terrain Based
#              Probability in SAR".
#              This script was created to identify the insections between streams
#              and other linear features such as Roads, Trails and Powerlines.
#
# Author:      ferguson
#
# Created:     11/09/2015
# Copyright:   (c) ferguson 2015
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
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
from arcpy import env

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

if __name__ == '__main__':
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

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

    inStreams = arcpy.GetParameterAsText(4)
    if inStreams == '#' or not inStreams:
        sys.exit(arcpy.AddError("You need to provide a valid Feature Layer for Streams"))

    #inFeature  - this is a point feature used to get the latitude and longitude of point.
    inFeatures = arcpy.GetParameterAsText(5)
    if inFeatures == '#' or not inFeatures:
        sys.exit(arcpy.AddError("You need to provide a valid Feature Class"))

    intsectOutput = "intsectOutput"
    bUfStreamInt = "streamIntercept_{0}".format(timestamp)
    clusterTolerance = 5 #meters - maximum distance between features to consider them intersecting.
    IPP = "Planning Point"
    IPP_dist = "IPPTheoDistance"
    cLipFeat = "cLipFeat"
    bUfFeat = "bUfFeat"
    cLipStream = "cLipStream"
    bUfStream = "bUfStream"

    SubNum = int(SubNum)

    if bufferUnit =='Kilometers':
        mult = 1.6093472
    else:
        mult = 1.0
    TheoSearch = mult * float(TheoDist)

    theDist = "{0} {1}".format(TheoSearch, bufferUnit)
    try:
        arcpy.Delete_management(IPP_dist)
    except:
        pass

    # Define the area of interest around the IPP
    where1 = '"Subject_Number" = ' + str(SubNum)
    where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
    where = where1 + where2

    arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)
    arcpy.AddMessage("Buffer IPP around the " + ippType )
    arcpy.Buffer_analysis(IPP, IPP_dist, theDist)
    IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
    arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")
    arcpy.SelectLayerByAttribute_management(IPP, "CLEAR_SELECTION")

    #Set extent
    desc = arcpy.Describe(IPP_dist)
    extent = desc.extent
    arcpy.env.extent = IPP_dist

    # if more than on linear feature is selected, merge elements together
    # there conduct Intersect with streams
    featList=inFeatures.split(';')

    if len(featList)>1:
        # Need to merge inFeatures after they have been clipped
        MergedFeatures="MergedFeatures"
        arcpy.Merge_management (inFeatures, MergedFeatures)
        arcpy.Clip_analysis(MergedFeatures, IPP_dist, cLipFeat, "")
        arcpy.Delete_management(MergedFeatures)
    else:
        featList = featList[0].replace("'","")
        arcpy.Clip_analysis(featList, IPP_dist, cLipFeat, "")

    del featList
    arcpy.Buffer_analysis(cLipFeat, bUfFeat, "7 Meters","","","ALL")

    # Clip and buffer the streams features
    arcpy.Clip_analysis(inStreams, IPP_dist, cLipStream, "")
    arcpy.Buffer_analysis(cLipStream, bUfStream, "7 Meters","","","NONE")

    # Find the intersections between Streams and travel aides
    arcpy.Intersect_analysis([bUfStream,bUfFeat], intsectOutput, "ALL", clusterTolerance, "INPUT")
    arcpy.Buffer_analysis(intsectOutput, bUfStreamInt, "50 Meters","","","NONE")

    # Aid field to later identify if the feature is an intersection of Stream-Trail,
    # Stream-Road, Stream-Etc.  Can be symbololized for easier identification.
    arcpy.AddField_management(bUfStreamInt, "TYPE", "TEXT", "", "", "30")

    arcpy.mapping.RemoveLayer(df,IPPDist_Layer)
    dElFeat = [bUfFeat, bUfStream, intsectOutput,cLipFeat, cLipStream, IPP_dist]
    for dFeat in dElFeat:
        arcpy.Delete_management(dFeat)

    insertLayer=arcpy.mapping.Layer(bUfStreamInt)
    try:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]
        arcpy.mapping.AddLayerToGroup(df, refGroupLayer, insertLayer,'BOTTOM')
    except:
        pass


