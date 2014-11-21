#-------------------------------------------------------------------------------
# Name:     IGT4SAR_AirSearchPattern.py
# Purpose:  The tool automates the process of generating aircraft search patterns
#           for a pre-defined area.  The user would select a pre-defined search
#           area as identified by a polygon feature.  IGT4SAR includes the map
#           layer:
#           Layer:  '9 Air operations / Search Pattern Extent'
#           The dataset for this layer is the "PatternExtent" feature class.
#
#           The search area is best defined using the "Rectangle" tool within
#           Create Features window.  The user would first draw a Rectangle polygon
#           and save it to the PatternExtent feature class by Editing Features of
#           the "Search Pattern Extent" Layer.
#
#           The user than selects from one of the five standard patterns
            # PATTERN OPTIONS
            # Expanding Square
            # Expanding Circle
            # Linked Circle
            # Longitudinal Traverse
            # Creeping Line - Lateral Traverse
#
#           More patterns may be added later.  Finally the user specifies a
#           Sweep Width for the aircraft being used.  For more information on
#           Sweep Width please see any of the many SAR rlated references on this
#           topic such as
#
#           Koester, Robert J., Donald C. Cooper, J. R. Frost, and R. Q. Robe.
#           Sweep width estimation for ground search and rescue. POTOMAC
#           MANAGEMENT GROUP ALEXANDRIA VA, 2004.
#
#           Additional comments have been placed throughout the script.
#
# Author:   Don Ferguson
#
# Created:  08/05/2014
# Copyright:   (c) Don Ferguson 2014
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
import math, numpy as np
import arcpy, sys, arcgisscripting, os
import arcpy.mapping
from arcpy import env
from arcpy.sa import *

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

pi = math.pi

######### Modules modified from from Jon Pedder - MapSAR #########################
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def WritePointGeometry(wrkspc,fc,xy,sr):
##   Use arcpy.InsertCursor to stay compatible with ArcMAP 10.0
    geometry_type = "POINT"
    arcpy.CreateFeatureclass_management(wrkspc,fc,geometry_type,spatial_reference=sr)
    cur = arcpy.InsertCursor(fc)
    for pt in xy:
        pnt = arcpy.Point(pt[0],pt[1])
        feat = cur.newRow()
        feat.shape = pnt
        cur.insertRow(feat)
    del cur
    return()

def eXpandSqr(Pt,sWeep,MaxExt,Ang):
    nn = int(round(MaxExt/sWeep,0))
    ds = sWeep
    k=1
    XY=[Pt]

    for gg in range(1,2*nn+1,2):
        LL=ds*k

        for jj in range(2):
            if -pi/2 < Ang < pi/2 or Ang > 3*pi/2:
                X=XY[gg-1+jj][0]+LL/math.sqrt(1+(math.tan(Ang))**2)
            else:
                X=XY[gg-1+jj][0]-LL/math.sqrt(1+(math.tan(Ang))**2)
            if Ang == 3*pi/2:
                Y=XY[gg-1+jj][1] - math.tan(Ang)*(X-XY[gg-1+jj][0])
            else:
                Y=XY[gg-1+jj][1] + math.tan(Ang)*(X-XY[gg-1+jj][0])

            XY.append([X,Y])
            Ang+=pi/2
            if abs(Ang)>2*pi:
                Ang-=2*pi
        k+=1
    return(XY)

def ExpandingCircle(Pt,sWeep,MaxExt):
    ds = sWeep/2.0
    nn = int(round(MaxExt/sWeep/2.0,0))
    if nn<0:
        sys.exit(arcpy.AddError("Invalid Sweep Width - Large than extent"))
    k=1
    XY = [Pt]
    aRad=0
    for gg in range(1,nn,2):
        LL=ds*k
        for theta in np.linspace(0,2*pi,360):
            rad=theta*ds*k/2/pi+aRad
            X=XY[0][0]+rad*math.cos(theta)
            Y=XY[0][1]+rad*math.sin(theta)
            XY.append([X,Y])
        k+=1
        aRad=rad
    return(XY)

def LinkedCircle(Pt,sWeep,MaxExt):
    ds = sWeep
    nn = int(round(MaxExt/sWeep,0))
    if nn<0:
        sys.exit(arcpy.AddError("Invalid Sweep Width - Large than extent"))
    XY = []
    rad=ds/2.0
    for gg in range(1,nn,2):
        for theta in np.linspace(0,2*pi*359/360,359):
            X=Pt[0]+rad*math.cos(theta)
            Y=Pt[1]+rad*math.sin(theta)
            XY.append([X,Y])
        rad+=ds
    return(XY)

def Traverse(Pt,sWeep,MinExt, MaxExt,AngMx, AngMn,k):

    aDj = sWeep/math.sqrt(2)

    aDjAng = (AngMx + AngMn)/2

    nn = int(round(MinExt/sWeep,0))
    Xt=Pt[0]+(aDj*math.cos(aDjAng))
    Yt=Pt[1]+(aDj*math.sin(aDjAng))
    XY=[[Xt,Yt]]

    for gg in range(1,(2*nn),2):
        if gg==2*nn+1:
            rj=1
        else:
            rj=2
        for jj in range(rj):
            if jj==0:
                LL=MaxExt-sWeep
            else:
                LL=sWeep
            X=XY[gg-1+jj][0]+LL*math.cos(AngMx)
            Y=XY[gg-1+jj][1]+LL*math.sin(AngMx)
            XY.append([X,Y])
            AngMx+=pi/2*(-1)**k
            if AngMx>=360:
                AngMx-=360
        k+=1
    return(XY)


def dotProduct(VectorA, VectorB):
    dp=sum(p*q for p,q in zip(VectorA,VectorB))
    return(dp)

def VectorMath(ExtPts):
    aDx = ExtPts[1].X-ExtPts[0].X
    aDy = ExtPts[1].Y-ExtPts[0].Y

    bDx = ExtPts[-2].X-ExtPts[0].X
    bDy = ExtPts[-2].Y-ExtPts[0].Y

    VectorA=[aDx,aDy]
    VectorB=[bDx,bDy]
    VectorX=[1,0]
    VectorY=[0,1]

    A_Len = np.linalg.norm(VectorA)
    B_Len = np.linalg.norm(VectorB)

    dpAB=dotProduct(VectorA, VectorB)
    AngAB=math.acos(dpAB/A_Len/B_Len)
    cpAB=(A_Len*B_Len)*math.sin(AngAB)

    dpAX=dotProduct(VectorA, VectorX)
    AngAx=math.acos(dpAX/A_Len/1.0)*math.copysign(1,aDy)

    dpBX=dotProduct(VectorB, VectorX)
    AngBx=math.acos(dpBX/B_Len/1.0)*math.copysign(1,bDy)

    eParts=[A_Len,B_Len, AngAB, AngAx, AngBx,cpAB]

    return(eParts)

def AppendPolyLineFeatures(df, outFc, spRef):
    # First test to see if the AirSearchPatterns Feature class exists
    fcList=arcpy.ListFeatureClasses("*","POLYLINE","Planning")
    AirPatterns="AirSearchPattern"

    if not AirPatterns in fcList:
        fClass=os.path.join(wrkspc,"Planning")
        arcpy.CreateFeatureclass_management(fClass, AirPatterns, "POLYLINE", spatial_reference=spRef)

        fldNames=[('Area_Name', 'TEXT'),('Area_Description','TEXT','','',500),('PATTERN','TEXT'), \
                  ('SWEEPWIDTH', 'SHORT'),('SEARCHED', 'SHORT'),('SEARCHSPEED', 'SHORT'), ('PATHLENGTH','FLOAT')]
        for field in fldNames:
            arcpy.AddField_management(*(AirPatterns,) + field)
        deleteLayer(df,[AirPatterns])
        try:
            refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Air Operations*',df)[0]
        except:
            refGroupLayer=""
        outFC_Lyr = arcpy.mapping.Layer(AirPatterns)
        arcpy.mapping.AddLayerToGroup(df,refGroupLayer,outFC_Lyr,'TOP')

    arcpy.Append_management(outFC,AirPatterns,"NO_TEST")

    where4 = '"Area_Name" = ' + "'" + outFC + "'"
    fc_lyr = arcpy.mapping.Layer(AirPatterns)
    arcpy.SelectLayerByAttribute_management(fc_lyr,"NEW_SELECTION",where4)
    arcpy.CalculateField_management(AirPatterns,"PATHLENGTH","!SHAPE.LENGTH@kilometers!","PYTHON")

    cursor = arcpy.UpdateCursor(AirPatterns,where4)
    for row in cursor:
        pLength = row.getValue("PATHLENGTH")
        pDescrip = "The flight path is {0} km".format(round(pLength,2))
        row.setValue("SEARCHED",0)
        row.setValue("SEARCHSPEED",0)
        row.setValue("Area_Description",pDescrip)
        cursor.updateRow(row)
    del cursor, row

    return()

def CreateKML(wrkspc,outFC):
    arcpy.AddMessage("Creating KML/KMZ file for: " +str(outFC))
    fc = "AirSearchPattern"
    where4 = '"Area_Name" = ' + "'" + outFC + "'"
    fc_lyr = arcpy.mapping.Layer(fc)
    arcpy.SelectLayerByAttribute_management(fc_lyr,"NEW_SELECTION",where4)
    fc_lyr.visible=True

    # Check if output directory exists
    outDIR=os.path.split(wrkspc)
    nPath=os.path.join(outDIR[0],"Products")
    fName = str(outFC) + ".kmz"
    if nPath:
        arcpy.AddMessage("{0} saved to the 'Products' sub-directory within your Incident Folder\n".format(outFC))
        newFName = os.path.join(nPath,fName)
    else:
        tPath=os.path.split(nPath)
        arcpy.AddMessage("{0} saved to the 'Products' sub-directory within your Incident Folder\n".format(tPath[1]))
        newFName = os.path.join(outDIR[0],fName)

    arcpy.LayerToKML_conversion(fc_lyr,newFName,ignore_zvalue="CLAMPED_TO_GROUND")

def appendName(pFeat,myList):
    cFeat=arcpy.GetCount_management(pFeat)
    if int(cFeat.getOutput(0)) > 0:
        arcpy.AddMessage("Add area names from " + pFeat)
        rows1 = arcpy.SearchCursor(pFeat)
        row1 = rows1.next()
        AName_list=[]
        while row1:
            AName = row1.getValue("Area_Name")
            if AName != "ROW":
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


def AreaNamesUpdate(workspc):
    fc1= "Area_Names"
    fc = ["AirSearchPattern"]
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

    fc1List=[]
    cursor=arcpy.SearchCursor(fc1)
    for row in cursor:
        fc1List.append(row.getValue("Area_Name"))

    for xd in myList:
        arcpy.AddMessage(xd)

        rows = arcpy.InsertCursor(fc1)

        row = rows.newRow()
        if xd not in fc1List:
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

##############################
##### Main Program Starts here
##############################
if __name__ == '__main__':
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    #PtrnExt  - This is intended to be the boundary of the desired search area.
    #Tyically the user would specify a rectangle polygon
    PtrnExt = arcpy.GetParameterAsText(0)
    if PtrnExt == '#' or not PtrnExt:
        sys.exit(arcpy.AddError("You need to provide a valid Feature Class"))

    #pAttern - User selects one of the pre-defined search patterns
    pAttern =arcpy.GetParameterAsText(1)
    if pAttern == '#' or not pAttern:
        pAttern = "empty"

    # PATTERN OPTIONS
    # Expanding Square
    # Expanding Circle
    # Linked Circle
    # Longitudinal Traverse
    # Creeping Line - Lateral Traverse

    # Sweep width in the data frame units.  Requires a Projected Coordinate System
    # If using UM the units would be Meters.
    sWeep =arcpy.GetParameterAsText(2)
    if sWeep == '#' or not sWeep:
        sWeep = "empty"
    sWeep = float(sWeep)

    # Option to export KML file of the search pattern
    createKML =arcpy.GetParameterAsText(3)
    if createKML == '#' or not createKML:
        createKML = "FALSE"

    # Get a List of Layers
    LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
    LyrName=[]
    for lyr in LyrList:
        LyrName.append(lyr.name)

    # Assign "Air Operations" as the Reference Layer to assist with layer placement
    if "Air Operations" in LyrName:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Air Operations*',df)[0]

    # Use Describe to get a SpatialReference object and conform the map is in a
    # Projected cooridnate system.
    spatial_reference = arcpy.Describe(PtrnExt).spatialReference
    if not spatial_reference.type == "Projected":
        sys.exit(arcpy.AddError("This tool requires a Projected Cooridnate System"))

    # Determine the centroid of the prescribed search area
    cursor=arcpy.SearchCursor(PtrnExt)
    for row in cursor:
        Extnt=row.Shape.extent
        Centrd =row.Shape.centroid
    extCentroid = [Centrd.X,Centrd.Y]

# Transform the vertices of the Search Pattern Extent polygon into points to interrogate the geometry
    outPts = "VertPts"
    try:
        deleteFeature([outPts])
    except:
        pass
    arcpy.FeatureVerticesToPoints_management(PtrnExt,outPts,"ALL")
    cursor=arcpy.SearchCursor(outPts)
    ExtPts=[]
    #
    for row in cursor:
        ExtPts.append(row.Shape.getPart(0))

    eParts = VectorMath(ExtPts) # Perform various vetor math operations to define parts

    A_Len=eParts[0];B_Len=eParts[1]
    AngAB=eParts[2];AngAx=eParts[3];AngBx=eParts[4]
    cpAB=eParts[5]

##    arcpy.AddMessage("AngAx = {0}; AngBx = {1}".format(AngAx*180/pi, AngBx*180/pi))
##    arcpy.AddMessage("A_Len = {0}; B_Len = {1}".format(A_Len,B_Len))
##    arcpy.AddMessage("Cross Product = {0}".format(cpAB))

# Different process depending on desired Search Pattern

    if pAttern == "Expanding Square":
        if A_Len>=B_Len:
            MaxExt = A_Len
            Ang = AngAx
        else:
            MaxExt = B_Len
            Ang = AngBx
        # Get the X and Y cooridnates for the Center Point
        Pt=extCentroid
        nAme = "ExpdSqr"
        XY =eXpandSqr(Pt,float(sWeep),MaxExt,Ang)

    if pAttern == "Expanding Circle":
        if A_Len>=B_Len:
            MaxExt = A_Len
        else:
            MaxExt = B_Len
        # Get the X and Y cooridnates for the Center Point
        Pt=extCentroid
        nAme = "ExpdCir"
        XY =ExpandingCircle(Pt,float(sWeep),MaxExt)

    if pAttern == "Linked Circle":
        if A_Len>=B_Len:
            MaxExt = A_Len
        else:
            MaxExt = B_Len
        # Get the X and Y cooridnates for the Center Point
        Pt=extCentroid
        nAme = "LinkedCir"
        XY =LinkedCircle(Pt,float(sWeep),MaxExt)

    if pAttern == "Longitudinal Traverse":
        Pt=[ExtPts[0].X,ExtPts[0].Y]
        if A_Len <= B_Len:
            MinExt = A_Len
            MaxExt = B_Len
            AngMx = AngBx
            AngMn = AngAx
            if cpAB>0:
                k=0
            else:
                k=1
        else:
            MinExt = B_Len
            MaxExt = A_Len
            AngMx = AngAx
            AngMn = AngBx
            if cpAB>0:
                k=1
            else:
                k=0
        nAme="LongTrav"
        XY=Traverse(Pt,float(sWeep),MinExt, MaxExt,AngMx, AngMn,k)

    if pAttern == "Creeping Line - Lateral Traverse":
        Pt=[ExtPts[0].X,ExtPts[0].Y]
        if A_Len <= B_Len:
            MinExt = B_Len
            MaxExt = A_Len
            AngMx = AngAx
            AngMn = AngBx
            if cpAB>0:
                k=1
            else:
                k=0
        else:
            MinExt = A_Len
            MaxExt = B_Len
            AngMx = AngBx
            AngMn = AngAx
            if cpAB>0:
                k=0
            else:
                k=1
        nAme="LatTrav"
        XY=Traverse(Pt,float(sWeep),MinExt, MaxExt,AngMx, AngMn,k)

    tempFC = "TempPt_{0}".format(timestamp)
    outFC = "{0}_{1}".format(nAme,timestamp)
    WritePointGeometry(wrkspc,tempFC,XY,spatial_reference)

    # create the polylines which make up the desired pattern.
    arcpy.PointsToLine_management(tempFC,outFC)

    fldNames=[('Area_Name', 'TEXT'),('SWEEPWIDTH', 'SHORT'),('PATTERN','TEXT')]
    for field in fldNames:
        arcpy.AddField_management(*(outFC,) + field) #often creates new Lyer
    deleteLayer(df,[outFC])

    cursor = arcpy.UpdateCursor(outFC)
    for row in cursor:
        row.setValue("Area_Name",outFC)
        row.setValue("SWEEPWIDTH",sWeep)
        row.setValue("PATTERN",pAttern)
        cursor.updateRow(row)
    del cursor, row

    AppendPolyLineFeatures(df,outFC, spatial_reference)

    if createKML.upper() == "TRUE":
        CreateKML(wrkspc,outFC)

    deleteFeature([tempFC,outFC,outPts])

    AreaNamesUpdate(wrkspc)
##


