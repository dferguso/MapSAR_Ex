#-------------------------------------------------------------------------------
# Name:    IGT4SAR_PlotXY.py
# Purpose: Create a point feature in an existing feature layer
#
# Author:      Don Ferguson
#
# Created:     04/09/2015
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
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
import datetime
from arcpy import env

# Environment variables
wrkspc=env.workspace
env.overwriteOutput = "True"
env.extent = "MAXOF"

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)
    except SystemExit as err:
            pass

def CreateTable():
    fPath = env.workspace
    tName = "xyTemp"
    tEmplate = "xyTemplate"
    config_keyword = ""
    # Execute CreateTable
    arcpy.CreateTable_management(fPath, tName, tEmplate, config_keyword)
    return(tName)

def SplitDMS(coord, pt):
    if not coord:
        sys.exit('You have not provided a valid {0} coordinate: {1}'.format(pt, coord))
    kCoord=[float(k) for k in coord.split(" ") if len(k.lstrip())>0]
    if len(kCoord) > 3:
        sys.exit('You have not provided a valid coordinate: {0}'.format(coord))

    if (kCoord[0])<0.0:
        mult = -1.0
    else:
        mult=1.0
    kCoord[0] = abs(kCoord[0])

    for k in range(len(kCoord),3):
        kCoord.append(0)
    kSum = 0.0
    for k in range(0,3):
        if kCoord[k]<0.0:
            sys.exit('You have not provided a valid coordinate: {0}'.format(coord))
        kSum+=kCoord[k]/60**k
    kSum=mult*kSum

    if pt == 'x':
        if kSum<-180.0 or kSum > 180.0:
            sys.exit('Longitude must be between -180 and 180, you entered: {0}'.format(coord))
    elif pt == 'y':
        if kSum<-90.0 or kSum > 90.0:
            sys.exit('Latitude must be between -90 and 90, you entered: {0}'.format(coord))

    return(kSum)

def WritePointGeometry(fc,xy,coMMents):  #Only works for single point
##    Could be used with version >= 10.1
##    cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
##    cursor.insertRow([xy])
##    del cursor

    pnt = arcpy.Point(xy[0],xy[1])

    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    field_upper = [f.name.upper() for f in fieldsList]
    chkFields = ['DESCRIPTION', 'COMMENTS', 'NOTES', 'AREA_DESCRIPTION']
    indx = [field_upper.index(y) for y in chkFields if y.upper() in field_upper]

##   Use arcpy.InsertCursor to stay compatible with ArcMAP 10.0

    cursor = arcpy.InsertCursor(fc)
    row = cursor.newRow()
    row.shape = pnt
    if indx:
        fldName = field_names[indx[0]]
        fldLength = fieldsList[indx[0]].length
        if coMMents:
            info = (coMMents[:(fldLength-2)] + '..') if len(coMMents) > fldLength else coMMents
            row.setValue(fldName,info)
    cursor.insertRow(row)
    del cursor, row
    return()


########
# Main Program starts here
#######
if __name__ == '__main__':
    #######
    #Automate map production - July 27, 2012
    mxd, df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    NewFC = arcpy.GetParameterAsText(0)
    if NewFC == '#' or not NewFC:
        sys.exit('Must elect to either use an existing point feature or create a new one')

    NewSR = arcpy.GetParameter(1)
    if NewSR == '#' or not NewSR:
        NewSR = None

    inFC = arcpy.GetParameterAsText(2)
    if inFC=='#' or not inFC:
        inFC = None

    coordFormat = arcpy.GetParameterAsText(3)

    NewPointX = arcpy.GetParameter(4)
    if NewPointX == '#' or not NewPointX:
        arcpy.AddMessage("You need to provide a valid entry for Longitude/Meters/UTM/MGRS/USNG")

    NewPointY = arcpy.GetParameterAsText(5)
    if NewPointY == '#' or not NewPointY:
        NewPointY=None

    NewCoord = arcpy.GetParameter(6)
    if NewCoord == '#' or not NewCoord:
        arcpy.AddMessage("You need to provide a valid Coordinate System")

    coMMents = arcpy.GetParameter(7)
    if coMMents == '#' or not coMMents:
        coMMents = None

    # Get a List of Layers
    LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
    LyrName=[]
    for lyr in LyrList:
        LyrName.append(lyr.name)
    if "Point_Features" in LyrName:
        refGroupLayerB = arcpy.mapping.ListLayers(mxd,'*Point_Features*',df)[0]
    else:
        refGroupLayerB = None
    # First check if NewCoord is GCS or PCS.
    arcpy.AddMessage("\nThe type of the New Coordinate system: {0}".format(NewCoord.type))

    if NewFC == "Use Existing Point Feature":
        if not inFC:
            sys.exit("If using Existing Layer, you must specify Target Feature Layer")

        #Check the spatial reference for the target feature class
        sr = arcpy.Describe(inFC).spatialReference

        # If the spatial reference is unknown
        #
        if sr.name == "Unknown":
            sys.exit("{0} has an unknown spatial reference\n".format(inFC))
    else:
        inFC = "Point_{0}".format(timestamp)
        if not NewSR:
            sys.exit("If creating a new point feature you must provide a vaalid coordinate system")
        else:
            sr = NewSR
            # Create a CellTowers Feature Class and Layer in the coordinate system defined by Planning Point
            # Use default values to populate the data fields
            arcpy.CreateFeatureclass_management(wrkspc, inFC, "POINT", "", "DISABLED", "DISABLED", sr)
            fieldlength = 250
            arcpy.AddField_management(inFC, "Description", "TEXT", "", "", fieldlength)
            in_fc = arcpy.mapping.Layer(inFC)
            if refGroupLayerB:
                arcpy.mapping.AddLayerToGroup(df,refGroupLayerB,in_fc,'BOTTOM')
            else:
                arcpy.mapping.AddLayer(df, in_fc,'TOP')




    #Check the format of the coordinates provided and if lat/long convert to D.DD
    if coordFormat == 'D M S':
        xCoord = round(SplitDMS(NewPointX, pt="x"),5)
        yCoord = round(SplitDMS(NewPointY, pt="y"),5)
        input_format = 'DD_2'
    elif coordFormat == 'D M.M':
        xCoord = round(SplitDMS(NewPointX, pt="x"),5)
        yCoord = round(SplitDMS(NewPointY, pt="y"),5)
        input_format = 'DD_2'
    elif coordFormat == 'D.DD':
        xCoord = round(SplitDMS(NewPointX, pt="x"),5)
        yCoord = round(SplitDMS(NewPointY, pt="y"),5)
        input_format = 'DD_2'
    elif coordFormat == 'UTM':
        xCoord = NewPointX
        yCoord = ""
        input_format = 'UTM_ZONES'
        ##UTM_ZONES ?The letter N or S after the UTM zone number designates only North or South hemisphere.
    elif coordFormat == 'MGRS':
        xCoord = NewPointX
        yCoord = ""
        input_format = 'MGRS'
    elif coordFormat == 'US National Grid':
        xCoord = NewPointX
        yCoord = ""
        input_format = 'USNG'
        ##USNG ?United States National Grid. Almost exactly the same as MGRS but uses North American Datum 1983 (NAD83) as its datum.
    else:
        arcpy.AddError("There was a problem")

    # Create Table with XY values
    in_table = CreateTable()
    arcpy.AddMessage("xCoord: {0}".format(xCoord))
    if yCoord:
        arcpy.AddMessage("yCoord: {0}".format(yCoord))
    cursor = arcpy.InsertCursor(in_table)
    row = cursor.newRow()
    row.setValue('x_Field', xCoord)
    row.setValue('y_Field', yCoord)
    row.setValue('in_Coord', NewCoord.name)
    row.setValue('out_Coord', sr.name)
    cursor.insertRow(row)

    # Delete cursor and row objects
    del cursor, row

    # Coordinate conversion

    # set parameter values
    out_featureclass = "fcTemp"
    x_field = 'x_Field'
    y_field = 'y_Field'
    output_format = 'DD_1'

    arcpy.ConvertCoordinateNotation_management(in_table, out_featureclass, x_field, y_field, input_format, output_format, "", sr, NewCoord)

    desc = arcpy.Describe(out_featureclass)
    shapefieldname = desc.ShapeFieldName

    # Create search cursor
    #
    cursor = arcpy.SearchCursor(out_featureclass)

    # Enter for loop for each feature/row
    #
    for row in cursor:
        # Create the geometry object 'feat'
        #
        feat = row.getValue(shapefieldname)
        pnt = feat.getPart()
        xy = (pnt.X, pnt.Y)

    del row, cursor
    WritePointGeometry(inFC,xy,coMMents)
    arcpy.Delete_management(out_featureclass)
    arcpy.Delete_management(in_table)

    sys.exit(0)




