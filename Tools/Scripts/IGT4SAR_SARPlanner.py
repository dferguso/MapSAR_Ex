#-------------------------------------------------------------------------------
# Name:        SARPlanner.py
#
# Purpose: Produces an estimate of Ground Searcher resources required to acheive
#          a desired POD based on user input.
#
# Author:      Don Ferguson
#
# Created:     01/05/2015
# Copyright:   (c) Don Ferguson 2015
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
import arcpy,math, os, sys

# Environment variables
wrkspc=arcpy.env.workspace
arcpy.env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

def AllSegments(fc, SrchSpd):
    SearchSpd = float(SrchSpd)
    sSeg = {}
    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    shapeType = desc.shapeType
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    field_Alias=[f.aliasName for f in fieldsList]

    SpatRef=desc.spatialReference
    uNits=SpatRef.linearUnitName
    if uNits.upper() == 'METER':
        mult = 1.0
    elif uNits.upper() == 'KILOMETER':
        mult = 0.001
    elif units.upper()== "FOOT":
        mult = 3.28084 # feet to meter
    elif units.upper()== "FEET":
        mult = 3.28084 # feet to meter
    else:
        arcpy.AddMessage(' could not compute requirements for {0} due to inconsistent units'.format(fc))
        return(sSeg)

    cursor = arcpy.SearchCursor(fc)
    for row in cursor:
        AreaN =row.Area_Name
        AreaN.encode('ascii','ignore')
        if shapeType == 'Polyline':
            SsegLength = (row.SHAPE_Length)/mult # length in meters
            assWidth = 15.0 # meters - Assume a width of the linear feature.
            SsegArea = SsegLength/1000.0 * assWidth/1000.0  # Area Units = km**2
        elif shapeType == 'Polygon':
            SsegArea = (row.Shape_Area)/mult/mult # area in meters**2
        if "SearchSpd" in field_names:
            if "Search Speed (km/hr)" in field_Alias:
                if row.SearchSpd > 0:
                    SearchSpd = min(row.SearchSpd,SrchSpd)
        else:
                SearchSpd = SrchSpd
        sSeg[AreaN] = [SsegArea/(1000.0**2), SearchSpd]

    return(sSeg)


########
# Main Program starts here
#######
if __name__ == '__main__':

    now = datetime.datetime.now()
    todaydate = now.strftime("%m%d")
    todaytime = now.strftime("%H%M%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    ## Script arguments

    ##SelectionMethod
    ## Give the user the option of selecting by individual segments or by selecting
    ## segments within the ring model (25%, 50% and 75%)
    SrchSpd = arcpy.GetParameterAsText(0)  # Effective Search Speed
    SrchSpd = float(SrchSpd)

    SrchTime = arcpy.GetParameterAsText(1)  # Effective Search time
    SrchTime = float(SrchTime)

    SwpWdth = arcpy.GetParameterAsText(2)  # Effective sweep width
    SwpWdth = float(SwpWdth)

    dPOD = arcpy.GetParameterAsText(3)  # Desired POD
    dPOD = float(dPOD)

    SelectInd = arcpy.GetParameterAsText(4)  # Desired POD
    if SelectInd == '#' or not SelectInd:
        SelectInd = False

    SelectStat= arcpy.GetParameterAsText(5)  # Desired POD
    if SelectStat == '#' or not SelectStat:
        SelectStat = None

    LineName = arcpy.GetParameterAsText(6)  # Line names
    if LineName == '#' or not LineName:
        LineName = None

    SegmentName = arcpy.GetParameterAsText(7)  # Area Names
    if SegmentName == '#' or not SegmentName:
        SegmentName = None

    sSeg = {}
    if arcpy.Exists("QRT_Lines"):
        fc1 = "QRT_Lines"
        sSeg.update(AllSegments(fc1, float(SrchSpd)))
    elif arcpy.Exists("Hasty_Line"):
        fc1 = "Hasty_Line"
        sSeg.update(AllSegments(fc1, float(SrchSpd)))
    else:
        fc1 = "None"

    if arcpy.Exists("Search_Segments"):
        fc2 = "Search_Segments"
        sSeg.update(AllSegments(fc2, float(SrchSpd)))
    else:
        fc2 = "None"

    if arcpy.Exists("QRT_Segments"):
        fc3 = "QRT_Segments"
        sSeg.update(AllSegments(fc3, float(SrchSpd)))
    elif arcpy.Exists("Hasty_Segments"):
        fc3 = "Hasty_Segments"
        sSeg.update(AllSegments(fc3, float(SrchSpd)))
    else:
        fc3 = "None"

    sName=[]
    fcList=[fc1, fc2, fc3]
    if SelectStat:
        fcStat = "StatisticalArea"
        fcS_lyr = arcpy.mapping.Layer(fcStat)
        arcpy.SelectLayerByAttribute_management(fcS_lyr,"CLEAR_SELECTION")
        if arcpy.Exists("StatisticalArea"):
            StatSeg = SelectStat.split(";")
            for SS in StatSeg:
                whereClause = '\'{0}\''.format(SS.replace("'",""))
                arcpy.AddMessage("Select Layers that intersect the {0} Ring".format(SS.replace("'","")))
                arcpy.MakeFeatureLayer_management(fcS_lyr, "TempLyr", '"Descrip" = ' + whereClause)

                for fc in fcList:
                    if fc != 'None':
                        fc_lyr = arcpy.mapping.Layer(fc)
                        arcpy.SelectLayerByLocation_management(fc_lyr, "INTERSECT", "TempLyr", "", "NEW_SELECTION")
                        cursor = arcpy.SearchCursor(fc_lyr)
                        row = cursor.next()
                        while row:
                            sName.append(row.getValue("Area_Name"))
                            row = cursor.next()
                        arcpy.SelectLayerByAttribute_management(fc_lyr,"CLEAR_SELECTION")

                if arcpy.Exists("TempLyr"): arcpy.Delete_management("TempLyr")
                arcpy.SelectLayerByAttribute_management(fcS_lyr,"CLEAR_SELECTION")
        else:
            arcpy.AddError("Run 'A. Statistical Search Area - IPP' Tool located in the 'SAR_Toolbox - Planning' prior to executing this tool!")
#######################################################
    arcpy.AddMessage("Process Individual Features")
    if LineName:
        arcpy.AddMessage("\nProcessing Linear Assignments")
        if fc1 == 'None':
            arcpy.AddError("No QRT / Hasty Lines Feature Exists")
        else:
            [sName.append(f) for f in LineName.split(";")]

    cnt = 0
    if SegmentName:
        sName=[]
        arcpy.AddMessage("\nProcessing Area (Segment) Assignments")
        if fc2 == "None":
            cnt = 0
        else:
            cnt += 1

        if fc3 == "None":
            cnt = 0
        else:
            cnt += 1
        if cnt > 0:
            [sName.append(f) for f in SegmentName.split(";")]
        else:
            arcpy.AddError("No Search_Segments Feature Exists")

    # Get a list of unique feature names
    sNameUnq = list(set(sName))

    # Calculate Coverage and Spacing
    Coverage=-(math.log(1.0-dPOD/100.0))
    EffSpcng = float(SwpWdth) / Coverage / 1000.0 # km

    # Output file
    dirNm = os.path.dirname(wrkspc)
    pRoducts = os.path.join(dirNm,"Products")
    if not os.path.exists(pRoducts):
        os.makedirs(pRoducts)
    fileName = os.path.join(pRoducts, "ResourceEstimate_{0}.txt".format(timestamp))
    target = open(fileName, 'w')
    target.write("Resource Estimate - Time: {0}".format(timestamp))

    lIne01 = "POD target of {0} with {1} hour(s) of Search Time".format(dPOD, SrchTime)
    lIne02 = "Assuming a Sweep width of {0} meters\n".format(SwpWdth)

    target.write(lIne01)
    target.write("\n")
    target.write(lIne02)
    target.write("\n")

    arcpy.AddMessage(lIne01)
    arcpy.AddMessage(lIne02)
    nSrchSum=0
    for SegName in sNameUnq:
        lArea = sSeg[SegName][0]
        lSpd = sSeg[SegName][1]
        TrkLngth = lSpd * float(SrchTime)
        eFfort = lArea/EffSpcng
        nSrchr = math.ceil(eFfort/TrkLngth)
        nSrchSum+=nSrchr
        lIne03 = "Area(km^2): {0}, Search Speed (kph): {1}, Searchers Required: {2}".format(SegName, lSpd, nSrchr)
        arcpy.AddMessage(lIne03)
        target.write(lIne03)
        target.write("\n")
    lIne04 = '\nA total of {0} Searchers as required to complete the desired task\n\n'.format(nSrchSum)
    arcpy.AddMessage(lIne04)
    target.write(lIne04)


    target.close()
    arcpy.AddMessage("Output file written to: {0}".format(pRoducts))





