#-------------------------------------------------------------------------------
# Name:     IGT4SAR_Cell_Coverage.py
# Purpose:  The tool uses as input a point feature class, name for the new
#           polygon feature class, a Bearing (measured from North on
#           degrees), Angle (width of the sector in degrees), and the
#           Disatnce (in meters).
#
# Author:   Don Ferguson
#
# Created:  01/02/2013
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
import math
import arcpy, sys, arcgisscripting, os
import arcpy.mapping
from arcpy import env
from arcpy.sa import *
import IGT4SAR_geodesic_Cell

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

######### Modules modified from from Jon Pedder - MapSAR #########################
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def checkSR(inRaster):   #From Jon Peddar - MapSAR
    """ Check to see if the raster is GCS or PCS, if GCS it's converted """
    try:
        mxd, frame = getDataframe()

        # Check to see if DEM is projected or geographic
        sr = arcpy.Describe(inRaster).spatialreference
        if sr.PCSName == '':   # if geographic throw an error and convert to projected to match the dataframe
            inSR = frame.spatialReference
            inPCSName = frame.spatialReference.PCSName
            arcpy.AddWarning('This elevation file (DEM) is NOT projected. Converting DEM to {0}\n'.format(inPCSName))
            inRaster = arcpy.ProjectRaster_management(inRaster, "{0}\DEM_{1}".format(scratchdb,inPCSName),inSR, "BILINEAR", "#","#", "#", "#")

        return(inRaster)

    except SystemExit as err:
            pass

def ValidateNewLocation(Newpoint,NewCoord):
    if NewPoint!="empty":
        NewPt = NewPoint.split(" ")
        xCoord = float(NewPt[0])
        yCoord = float(NewPt[1])
        if xCoord == None or yCoord ==None:
                sys.exit(arcpy.AddError("Please check your coordinates\n"))
        if NewCoord=="Geographic (Long / Lat)":
            arcpy.AddMessage('Longitude: {0}  and Latitude: {1}\n'.format(xCoord, yCoord))
            if xCoord<-180 or xCoord > 180:
                sys.exit(arcpy.AddError("Check your Longitude Coordinate (X)\n"))
            elif yCoord<-90 or xCoord > 90:
                sys.exit(arcpy.AddError("Check your Latitude Coordinate (Y)\n"))
            else:
                return(xCoord, yCoord)
        else:
            arcpy.AddMessage('X Coord: {0}  and Y Coord: {1}\n'.format(xCoord, yCoord))
            if xCoord < 0 or yCoord < 0:
                arcpy.AddWarning("Projected Coordinate is negative - is this corrrect?\n")
            return(xCoord, yCoord)

    else:
        sys.exit(arcpy.AddError("Please check the Point Coordinates\n"))

def ValidateNewInfo(nInfo,tParam, towerParam):
    arcpy.AddMessage("\n")
    for k in range(len(nInfo)):
        arcpy.AddMessage('{0} : {1}'.format(towerParam[k],nInfo[k]))
        try:
            if k==0:
                nInfo[k] = str(nInfo[k])
            else:
                nInfo[k]=int(nInfo[k])
        except:
            sys.exit(arcpy.AddError('Tower properties need to be numeric\n'))

    if len(nInfo)!= 5:
        sys.exit(arcpy.AddError("Please Check Antenna/Tower Properties - each seperated by a comma\n"))
    else:
        AntInfo=dict((tParam[i],nInfo[i]) for i in range(len(tParam)))
        # Use is AntInfo.get("aBearing")
        return(AntInfo)

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

def WritePointGeometry(fc,xy):  #Only works for single point
##    Could be used with version >= 10.1
##    cursor = arcpy.da.InsertCursor(fc, ["SHAPE@XY"])
##    cursor.insertRow([xy])
##    del cursor

##   Use arcpy.InsertCursor to stay compatible with ArcMAP 10.0
    cur = arcpy.InsertCursor(fc)
    pnt = arcpy.Point(xy[0],xy[1])
    feat = cur.newRow()
    feat.shape = pnt
    cur.insertRow(feat)
    del cur
    return()

def CellViewshed(CellPts_Lyr, DEM, refGroupLayer, df, mxd):
    # Set layer that output symbology will be based on
    # Set local variables
    zFactor = 1; useEarthCurvature = "CURVED_EARTH"; refractivityCoefficient = 0.15

    # Execute Viewshed
    outViewshed = Viewshed(DEM, CellPts_Lyr, zFactor, useEarthCurvature, refractivityCoefficient)
    # Save the output
    outViewshed.save(nList)
    arcpy.RefreshCatalog(nList)

    nRstr = nList+'rstr'
    arcpy.MakeRasterLayer_management(Raster(nList), nRstr)
    nList_Lyr = arcpy.mapping.Layer(nRstr)
    nList_Lyr.name=nList
    arcpy.mapping.RemoveLayer(df,nList_Lyr)
##    deleteLayer(df,[nList_Lyr])
    arcpy.mapping.AddLayerToGroup(df,refGroupLayer,nList_Lyr,'BOTTOM')

    try:
        lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
        symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\10 Coverage Area.lyr"
        arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
    except:
        pass

    return()

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
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    #inFeature  - this is a point feature used to get the latitude and longitude of point.
    inFeature = arcpy.GetParameterAsText(0)
    if inFeature == '#' or not inFeature:
        sys.exit(arcpy.AddError("You need to provide a valid Feature Class"))

    #out_fc - this will be the output feature for the sector.  May allow user to decide name or I may specify.
    cellTowers =arcpy.GetParameterAsText(1)
    if cellTowers == '#' or not cellTowers:
        cellTowers = "empty"

    NewCoord = arcpy.GetParameterAsText(2)
    if NewCoord == '#' or not NewCoord:
        NewCoord = "empty"

    NewPoint = arcpy.GetParameterAsText(3)
    if NewPoint == '#' or not NewPoint:
        NewPoint = "empty"

    NewInfo = arcpy.GetParameterAsText(4)
    if NewInfo == '#' or not NewInfo:
        NewInfo = "empty"

    NewGenSector = arcpy.GetParameterAsText(5)
    if NewGenSector == '#' or not NewGenSector:
        NewGenSector = "empty"

    NewViewshed = arcpy.GetParameterAsText(6)
    if NewViewshed == '#' or not NewViewshed:
        NewViewshed = "empty"

    DEM = arcpy.GetParameterAsText(7)
    if DEM == '#' or not DEM:
        DEM = "empty"

    arcpy.AddMessage('\n')
    ## Variables
    tParam=['aDescrip', 'aHeight','aBearing', 'aSecAng', 'aRange']
    towerParam=['Description','Height','Bearing', 'Sector Angle', 'Range']
    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', \
                      SPHEROID['WGS_1984',6378137.0,298.257223563]],\
                      PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    fldNamesA=[('OFFSETA', 'SHORT'),('OFFSETB', 'SHORT'), \
              ('AZIMUTH1', 'SHORT'),('AZIMUTH2', 'SHORT'),('VERT1', 'SHORT'), \
              ('VERT2', 'SHORT'),('RADIUS1', 'SHORT'),('RADIUS2', 'SHORT')]
    fldNamesB=[('DESCRIPTION','TEXT'),('HEIGHT','SHORT'),('ANTSEC_DIR','SHORT'),('ANTSEC_DISP', 'SHORT'),('RANGE_MAX', 'SHORT')]
    CellTowers = "CellTowers"

    OFFSETA = 15
    OFFSETB = 2
    AZIMUTH1 = 0
    AZIMUTH2 = 360
    VERT1 = 90
    VERT2 = -90
    RADIUS1 = 0
    RADIUS2 = 5000
    obsvrDef=[OFFSETA,OFFSETB,AZIMUTH1,AZIMUTH2,VERT1,VERT2,RADIUS1,RADIUS2]


    planPt = arcpy.mapping.Layer("Planning Point")
    # Use Describe to get a SpatialReference object
    descPlanPt = arcpy.Describe(planPt)
    shapefieldname = descPlanPt.ShapeFieldName
    PlanPtCS = descPlanPt.SpatialReference

    # Check to see if the cell Tower Layer exists
    #
    # Get a List of Layers
    LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
    LyrName=[]
    for lyr in LyrList:
        LyrName.append(lyr.name)
        if "CellTowers" in lyr.name:
            arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")

    if "Cellular" in LyrName:
        refGroupLayerA = arcpy.mapping.ListLayers(mxd,'*Cellular*',df)[0]
        arcpy.AddMessage("refGroupLayer = {0}".format(refGroupLayerA))
        arcpy.AddMessage("line 297")
    else:
        refGroupLayerA = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]

    if "Point_Features" in LyrName:
        refGroupLayerB = arcpy.mapping.ListLayers(mxd,'*Point_Features*',df)[0]
    ########################################################

    if NewGenSector =="false" and NewViewshed == "false":
        sys.exit(arcpy.AddError("You must select either to generate a Cell Sector or Estimate Coverage"))

    if NewViewshed == "true":
        if DEM=="empty":
            sys.exit(arcpy.AddError("Need to select DEM to estimate Cellular Coverage"))

############################################################
    if inFeature == "Use Cell Towers Layer":
        if cellTowers=="empty":
            sys.exit(arcpy.AddError("Please select one or more Cell Tower to consider if no towers are listed check that the 'DESCRIPTION' field in the 'CellTowers' layer is populated.  If there is no CellTower Layer than use 'New Location'\n "))
        else:
            cTower = cellTowers.split(";")
            cTower=[x.replace("'","") for x in cTower]
            cTower=[x.encode('ascii') for x in cTower]

            arcpy.AddMessage(cTower)
            [arcpy.AddMessage(type(kk)) for kk in cTower]
            if "CellTowers" in LyrName:
                in_fc = arcpy.mapping.Layer(CellTowers)

                desc = arcpy.Describe(in_fc)
                shapefieldname = desc.ShapeFieldName
                outCS = desc.SpatialReference

                chkListB = AddViewFields(in_fc, fldNamesB)

                if len(chkListB)>0:
                    for chk in chkListB:
                        arcpy.AddError('You need to enter a value in {0}'.format(chk))
                    sys.exit(1)
                else:
                    for tower in cTower:
                        try:
                            where_clause="DESCRIPTION = %s" % tower
                            cursor = arcpy.SearchCursor(in_fc, where_clause)
                        except:
                            where_clause="DESCRIPTION = '%s'" % tower
                            cursor = arcpy.SearchCursor(in_fc, where_clause)
                        for row in cursor:
                            aDescrip = row.getValue('DESCRIPTION')
                            if len(aDescrip)<1:
                                sys.exit(arcpy.AddError("Check DESCRIPTION in CellTower Layer for the selected Tower"))

                            aHeight=row.getValue('HEIGHT')
                            if aHeight is None:
                                sys.exit(arcpy.AddError("Check HEIGHT in CellTower Layer for the selected Tower"))
                            aBearing=row.getValue('ANTSEC_DIR')
                            if aBearing is None:
                                sys.exit(arcpy.AddError("Check ANTSEC_DIR in CellTower Layer for the selected Tower"))

                            aSecAng =row.getValue('ANTSEC_DISP')
                            if aSecAng is None:
                                sys.exit(arcpy.AddError("Check ANTSEC_DISP in CellTower Layer for the selected Tower"))

                            aRange =row.getValue('RANGE_MAX')
                            if aRange is None:
                                sys.exit(arcpy.AddError("Check RANGE_MAX in CellTower Layer for the selected Tower"))

                        nInfo=[aDescrip,aHeight,aBearing, aSecAng, aRange]
                        AntInfo = ValidateNewInfo(nInfo,tParam,towerParam)
            else:
                sys.exit(arcpy.AddError("There is no CellTower Layer.  Run this tool using 'New Location'\n "))
    ########################################################
    elif inFeature == "New Location":
        #First check to see if CellTowers Layer exists, if not create it.
        if "CellTowers" in LyrName:
            in_fc = arcpy.mapping.Layer(CellTowers)
        else:
            # Create a CellTowers Feature Class and Layer in the coordinate system defined by Planning Point
            # Use default values to populate the data fields
            arcpy.CreateFeatureclass_management(wrkspc, CellTowers, "POINT", "", "DISABLED", "DISABLED", PlanPtCS)
            in_fc = arcpy.mapping.Layer(CellTowers)
            arcpy.mapping.AddLayerToGroup(df,refGroupLayerB,in_fc,'BOTTOM')
### Use Describe to get a SpatialReference object
        desc = arcpy.Describe(in_fc)
        shapefieldname = desc.ShapeFieldName
        outCS = desc.SpatialReference

        try:
            if NewInfo=='empty':
                sys.exit(arcpy.AddError("Please check the tower/antenna information \n"))

            arcpy.AddMessage('Tower / Antenna Properties')
            nInfo=NewInfo.split(',')
            aDescrip = ["NL_{0}".format(timestamp)]
            nInfo = aDescrip + nInfo

            AntInfo = ValidateNewInfo(nInfo,tParam,towerParam)
            # Use is AntInfo.get("aBearing")
            # Default values for Cell Towers
        except SystemError as err:
            pass

        try:
            xCrd, yCrd = ValidateNewLocation(NewPoint,NewCoord)
            xy=(xCrd,yCrd)
        except SystemError as err:
            pass
        #################################
        ## Write geometry if NewLocation is True
        aTower = "Temp_{0}".format(timestamp)
        ## Create a temporary feature class for the new point until it can be
        ## appended into the existing CellTower feature class
        if NewCoord=="Geographic (Long / Lat)":
            ## Write new points to this temporary dataset
            ## Is the Map in GCS?
            if outCS != unProjCoordSys:
                arcpy.CreateFeatureclass_management(wrkspc, aTower, "POINT", "", "DISABLED", "DISABLED", unProjCoordSys)
                # use update Cursor to write the new geometry
                indx = WritePointGeometry(aTower,xy)
                # Project the temporary feature class to the OutCS coordinate system
                arcpy.Project_management(aTower, TempPoints, outCS)
                # Append points from temporary FC to the CellTowers layer
                arcpy.Append_management(TempPoints, CellTowers,"NO_TEST")
                # Delete the two temporary FC's
                fcList = [aTower,TempPoints]
                deleteFeature([fcList])

            else:
                ## Directly write geometry to CellTowers using UpdateCursor
                WritePointGeometry(CellTowers,xy)

        else:
            ## Assume New Locations in projected in same coordinate system as outCS
            ## Directly write geometry to CellTowers using UpdateCursor
            WritePointGeometry(CellTowers,xy)

        indx=[]
        cursor = arcpy.SearchCursor(CellTowers)
        ################################ To DO #################
        ## Check the field list and update values using the most recent point added
        for row in cursor:
            indx.append(row.getValue("OBJECTID"))
        CellID=max(indx)
        del cursor
        where1 = 'OBJECTID = {0}'.format(CellID)
        cursor = arcpy.UpdateCursor(CellTowers,where1)
        cTower=[AntInfo.get('aDescrip')]
        for row in cursor:
            for kk in range(len(fldNamesB)):
                row.setValue(fldNamesB[kk][0],AntInfo.get(tParam[kk]))
            # Calculate UTM and LAT/LONG
            if outCS.type=='Projected':
                pnt=row.Shape.getPart(0)
                row.setValue('UTM_Easting',pnt.X)
                row.setValue('UTM_Northing',pnt.Y)
            else:
                pnt=row.Shape.getPart(0)
                row.setValue('LONGITUDE',pnt.X)
                row.setValue('LATITUDE',pnt.Y)
            cursor.updateRow(row)

    nList=arcpy.mapping.ListLayers(mxd,'*CellTowers*',df)
    for nL in nList:
        cellTower_Layer=nL
    arcpy.SelectLayerByAttribute_management(cellTower_Layer, "CLEAR_SELECTION")

    arcpy.AddMessage('\n')
    for tower in cTower:
        where_clause="DESCRIPTION = '%s'" % tower
        cursor = arcpy.UpdateCursor(cellTower_Layer, where_clause)
        for row in cursor:
            descript =row.getValue('DESCRIPTION')
            aHeight =row.getValue('HEIGHT')
            aBearing=row.getValue('ANTSEC_DIR')
            aSecAng =row.getValue('ANTSEC_DISP')
            aRange =row.getValue('RANGE_MAX')
            AziChkL = aBearing - (1.1*aSecAng)/2
            if AziChkL<0:
                AziChkL=360+AziChkL
            AziChkH = aBearing + (1.1*aSecAng)/2
            if AziChkH>360:
                AziChkH=AziChkH-360

            row.setValue('OFFSETA',int(aHeight))
            row.setValue('OFFSETB',2)

            row.setValue('AZIMUTH1',AziChkL)
            row.setValue('AZIMUTH2',AziChkH)
            row.setValue('VERT1',90)
            row.setValue('VERT2',-90)
            row.setValue('RADIUS1',0)
            row.setValue('RADIUS2',aRange)
            cursor.updateRow(row)
        del cursor
        if not descript:
            sys.exit(arcpy.AddError('Problem most likely do to improperly selected features'))
        expression = 'DESCRIPTION = \'{0}\''.format(descript)
        arcpy.SelectLayerByAttribute_management(cellTower_Layer, "NEW_SELECTION", expression)

        out_fc="{0}_B{1}_Ang{2}_Rng{3}".format(descript.replace(" ","")[0:10],str(aBearing),str(aSecAng),str(int(aRange)))
        inDataset="{0}\{1}".format(wrkspc, descript.replace(" ","")[0:5])
        if NewGenSector=="true":
            arcpy.AddMessage("Genrate Sector for {0}".format(descript))
        ##        out_fc="B{0}_Ang{1}_Rng{2}".format(str(aBearing),str(aSecAng),str(int(aRange)))
            IGT4SAR_geodesic_Cell.Geodesic_Main(cellTower_Layer, out_fc, aBearing, aSecAng, aRange,wrkspc)
            out_fc_lyr="{0}_Lyr".format(out_fc)
            arcpy.MakeFeatureLayer_management(out_fc,out_fc_lyr)
            nList_Lyr = arcpy.mapping.Layer(out_fc)
            nList_Lyr.name=out_fc
            arcpy.mapping.RemoveLayer(df,nList_Lyr)
        ##    deleteLayer(df,[nList_Lyr])
            arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_Lyr,'BOTTOM')
            try:
                lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
                symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\15 Cell Sector.lyr"
                arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
            except:
                pass

        else:
            arcpy.AddWarning("User did not select Sector")

        if NewViewshed == "true":
            if DEM=="empty":
                sys.exit(arcpy.AddError("No DEM Selected"))
            else:
                arcpy.AddMessage("Estimate coverage for {0}\n".format(descript))
                zFactor = 1; useEarthCurvature = "CURVED_EARTH"; refractivityCoefficient = 0.15

                # Execute Viewshed
                outViewshed = Viewshed(DEM, cellTower_Layer, zFactor, useEarthCurvature, refractivityCoefficient)
                # Save the output
                outRstr = "{0}_rstr".format(out_fc)
                outViewshed.save(outRstr)
                arcpy.RefreshCatalog(outRstr)

                outRstrb = "{0}_rstrb".format(out_fc)
                arcpy.MakeRasterLayer_management(Raster(outRstr),outRstrb)
                nList_Lyr = arcpy.mapping.Layer(outRstrb)
                nList_Lyr.name=outRstrb
                arcpy.mapping.RemoveLayer(df,nList_Lyr)
            ##    deleteLayer(df,[nList_Lyr])
                arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_Lyr,'BOTTOM')
                try:
                    lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
                    symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\10 Coverage Area.lyr"
                    arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
                except:
                    pass


        else:
            arcpy.AddWarning("User did not select Viewshed")
        arcpy.SelectLayerByAttribute_management(cellTower_Layer, "CLEAR_SELECTION")

