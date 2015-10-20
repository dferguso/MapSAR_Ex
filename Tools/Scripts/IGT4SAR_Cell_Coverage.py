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
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
try:
    math
except NameError:
    import math
try:
    arcpy.mapping
except NameError:
    import arcpy.mapping
import re, datetime
import arcgisscripting, os
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
        mxd, df = getDataframe()

        # Check to see if DEM is projected or geographic
        sr = arcpy.Describe(inRaster).spatialreference
        inSR = df.spatialReference
        inPCSName = df.spatialReference.PCSName

        if sr.PCSName == '':   # if geographic throw an error and convert to projected to match the dataframe
            arcpy.AddWarning('This elevation file (DEM) is NOT projected. Converting DEM to {0}\n'.format(inPCSName))
            inRaster = arcpy.ProjectRaster_management(inRaster, "DEM_{0}".format(inPCSName),inSR, "BILINEAR", "#","#", "#", "#")
        elif sr.PCSName != inPCSName:
            arcpy.AddWarning('This elevation file (DEM) is in a different projection than the data frame. Converting DEM to {0}\n'.format(inPCSName))
            inRaster = arcpy.ProjectRaster_management(inRaster, "DEM_{0}".format(inPCSName),inSR, "BILINEAR", "#","#", "#", "#")
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
                nInfo[k]=float(nInfo[k])
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

def chkCellSize(DEM):
    XCel = arcpy.GetRasterProperties_management(DEM,"CELLSIZEX")
    XCell = float(XCel.getOutput(0))
    return(XCell)

def CellViewshed(CellPts_Lyr, DEM, trPower, Ftx, Gtx, recThres, aRange, refGroupLayer, out_fc):
    mxd,df = getDataframe()
    cellSize = chkCellSize(DEM)
    arcpy.env.extent = DEM
    # Calculate Received Signal Strength and Path Loss
    # Prx (dBm) = Ptx + Gtx + Grx - Ltx - Lfs - Lfm - Lrx
    # Prx (dBm) = Received input power (dBm)
    # Ptx (dBm) = Transmitter output power (dBm)
    # Gtx (dBm) = Transmitter antenna gain (dBm)
    # Grx (dBm) = Receiver antenna gain (dBm)
    # Ltx (dBm) = Transmit feeder and associated losses (feeder, connectors, etc.)
    # Lfs (dBm) = Free space path loss
    # Lfm (dBm) = many-sided signal propagation losses (these include fading margin, polarization mismatch,
    #             losses associated with medium through which signal is travelling, other losses...)
    # Lrx (dBm) = Receiver feeder losses
    # Decibel milliwatts (dBm) = 10*log10(milliWatts)
    # e.g. 0 dBm = 10*log10(1 mW)

    # Convert the tranmission power from W to dBm (decibel milliWatts)
    Ptx = 10.0 * math.log10(trPower / 1000.0) # Covert W to milliwatts

    Grx = 0 # Receiver gain (dBm) - typical cell phone has zero gain as it is equity with a uni-direction antenna.
    Ltx = 0 # Currently neglecting trnsmitter feeder losses as it would be difficult to determine for cellular - Oct 2015 - DHF
    Lfm = 0 # Currently neglecting addtional path losses - Oct 2015 - DHF
    Lrx = 0 # Currently neglecting receiver fedder losses - Oct 2015 - DHF

    cSpd = 2997924458.0 # Speed of light (m/sec)

    # Set layer that output symbology will be based on
    # Set local variables
    zFactor = 1; useEarthCurvature = "CURVED_EARTH"; refractivityCoefficient = 0.15
    # Check spatial reference
    DEM=checkSR(DEM)
    # Execute Viewshed
    outViewshed = Viewshed(DEM, CellPts_Lyr, zFactor, useEarthCurvature, refractivityCoefficient)
    outEucDistance = EucDistance(CellPts_Lyr, aRange, cellSize)

    Lfs = SetNull(outViewshed==0,20*Log10((4*math.pi*(10**6))/cSpd*Ftx*outEucDistance))

    Prx = Ptx + Gtx + Grx - Ltx - Lfs - Lfm - Lrx
    # Received signal strength cut off at Receiver Threshold
    outVisible = SetNull(Prx, Prx, 'Value < {0}'.format(recThres))

    # Save the output
    outRstr = "{0}_rstr".format(out_fc)
    outVisible.save(outRstr)
    del outViewshed, outEucDistance, outVisible, Prx

    arcpy.RefreshCatalog(outRstr)

    outRstrb = "{0}_rstrb".format(out_fc)
    arcpy.MakeRasterLayer_management(Raster(outRstr),outRstrb)
    nList_Lyr = arcpy.mapping.Layer(outRstrb)
    nList_Lyr.name=outRstrb
    arcpy.mapping.RemoveLayer(df,nList_Lyr)

    arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_Lyr,'BOTTOM')
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
                #arcpy.Delete_management(wrkspc + '\\' + gg)
                arcpy.Delete_management(gg)
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

    CellUncert = arcpy.GetParameterAsText(6)
    if CellUncert == '#' or not CellUncert:
        CellUncert = "empty"

    UncertDist = arcpy.GetParameterAsText(7)
    if UncertDist == '#' or not UncertDist:
        UncertDist = "empty"

    UncertUnits = arcpy.GetParameterAsText(8)
    if UncertUnits == '#' or not UncertUnits:
        UncertUnits = "empty"

    NewViewshed = arcpy.GetParameterAsText(9)
    if NewViewshed == '#' or not NewViewshed:
        NewViewshed = "empty"

    DEM = arcpy.GetParameterAsText(10)
    if DEM == '#' or not DEM:
        DEM = "empty"

    recThres = arcpy.GetParameterAsText(11)
    if recThres == '#' or not recThres:
        recThres = "empty"

    arcpy.AddMessage('\n')
    ## Variables
    tParam=['aDescrip', 'aHeight','aBearing', 'aSecAng', 'aRange', 'aPtx', 'aGtx', 'aFreq_tx']
    towerParam=['Description','Height','Bearing', 'Sector Angle', 'Range', 'Transmit Power (W)', 'Transmit Antenna Gain (dB)', 'Transmit Frequency (MHz)']
    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', \
                      SPHEROID['WGS_1984',6378137.0,298.257223563]],\
                      PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    fldNamesA=[('OFFSETA', 'SHORT'),('OFFSETB', 'SHORT'), \
              ('AZIMUTH1', 'SHORT'),('AZIMUTH2', 'SHORT'),('VERT1', 'SHORT'), \
              ('VERT2', 'SHORT'),('RADIUS1', 'SHORT'),('RADIUS2', 'SHORT')]
    fldNamesB=[('DESCRIPTION','TEXT'),('HEIGHT','SHORT'),('ANTSEC_DIR','SHORT'),('ANTSEC_DISP', 'SHORT'),('RANGE_MAX', 'SHORT'), \
               ('Ptx', 'FLOAT'), ('Gtx','FLOAT'),('Freq_tx', 'FLOAT')]
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
    if "Cellphone Coverage" in LyrName:
        refGroupLayerA = arcpy.mapping.ListLayers(mxd,'Cellphone Coverage',df)[0]
        arcpy.AddMessage("refGroupLayer = {0}".format(refGroupLayerA))
    else:
        refGroupLayerA = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis',df)[0]

    if "Point_Features" in LyrName:
        refGroupLayerB = arcpy.mapping.ListLayers(mxd,'*Point_Features*',df)[0]
    ########################################################

    if CellUncert.lower() == "true":  #Must generate a New Sector to use Uncertainty
        NewGenSector=="true"

    if NewGenSector =="false" and NewViewshed == "false":
        sys.exit(arcpy.AddError("You must select either to generate a Cell Sector or Estimate Coverage"))

############################################################
    if inFeature == "Use Cell Towers Layer":
        if cellTowers=="empty":
            sys.exit(arcpy.AddError("Please select one or more Cell Tower to consider if no towers are listed check that the 'DESCRIPTION' field in the 'CellTowers' layer is populated.  If there is no CellTower Layer than use 'New Location'\n "))
        else:
            cTower = cellTowers.split(";")
            cTower=[x.replace("'","") for x in cTower]
            cTower=[x.encode('ascii') for x in cTower]

#            arcpy.AddMessage(cTower)
#            [arcpy.AddMessage(type(kk)) for kk in cTower]
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

                            aPtx =row.getValue('Ptx')
                            if aPtx is None:
                                sys.exit(arcpy.AddError("Check Transmit Power (W) in CellTower Layer for the selected Tower"))

                            aGtx =row.getValue('Gtx')
                            if aGtx is None:
                                sys.exit(arcpy.AddError("Check Transmit Antenna Gain (dB) in CellTower Layer for the selected Tower"))

                            aFreq_tx =row.getValue('Freq_tx')
                            if aFreq_tx is None:
                                sys.exit(arcpy.AddError("Check Transmit Frequency (MHz) in CellTower Layer for the selected Tower"))

                        nInfo=[aDescrip,aHeight,aBearing, aSecAng, aRange, aPtx, aGtx, aFreq_tx]
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
        TempPoints="TempPoints"
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
                #fcList = [aTower,TempPoints]
                #deleteFeature([fcList])
                arcpy.Delete_management(aTower)
                arcpy.Delete_management(TempPoints)

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
            descript01 =row.getValue('DESCRIPTION')
            descript = re.sub("[^\w-]","",descript01)
            aHeight =row.getValue('HEIGHT')
            aBearing=row.getValue('ANTSEC_DIR')
            aSecAng =row.getValue('ANTSEC_DISP')
            aRange =row.getValue('RANGE_MAX')
            aPtx = row.getValue('Ptx')
            aGtx = row.getValue('Gtx')
            aFreq_tx = row.getValue('Freq_tx')
            if aSecAng == 360:
                AziChkL = 0
                AziChkH = 360
            else:
                AziChkL = aBearing - (1.05*aSecAng)/2
                if AziChkL<0:
                    AziChkL=360+AziChkL
                AziChkH = aBearing + (1.05*aSecAng)/2
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
        if not descript01:
            sys.exit(arcpy.AddError('Problem most likely do to improperly selected features'))
        expression = 'DESCRIPTION = \'{0}\''.format(descript01)
        arcpy.SelectLayerByAttribute_management(cellTower_Layer, "NEW_SELECTION", expression)
        out_fc="{0}_B{1}_Ang{2}_Ptx{3}".format(descript[0:10],str(aBearing),str(aSecAng),str(int(aPtx)))
        inDataset="{0}\{1}".format(wrkspc, descript[0:5])

        if NewGenSector=="true":
            arcpy.AddMessage("Genrate Sector for {0} as {1}".format(descript01, out_fc))
        ##        out_fc="B{0}_Ang{1}_Rng{2}".format(str(aBearing),str(aSecAng),str(int(aRange)))
            if CellUncert.lower() == "true":
                UncertBuff = "{0} {1}".format(str(UncertDist),UncertUnits)
                out_fcUNC = out_fc + '_Uncert'
            else:
                UncertBuff=""
                out_fcUNC =""

            IGT4SAR_geodesic_Cell.Geodesic_Main(cellTower_Layer, out_fc, aBearing, aSecAng, aRange, wrkspc, UncertBuff, out_fcUNC)

            if arcpy.Exists(out_fc):
                out_fc_lyr="{0}_Lyr".format(out_fc)
                arcpy.MakeFeatureLayer_management(out_fc,out_fc_lyr)
                nList_Lyr = arcpy.mapping.Layer(out_fc)
                nList_Lyr.name=out_fc
                arcpy.mapping.RemoveLayer(df,nList_Lyr)
                arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_Lyr,'BOTTOM')

                try:
                    lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
                    arcpy.AddMessage("Change symbology of Cell Sector")
                    symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\15 Cell Sector.lyr"
                    arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
                except:
                    pass

            if arcpy.Exists(out_fcUNC):
                out_fc_lyrUn="{0}_Lyr".format(out_fcUNC)
                arcpy.MakeFeatureLayer_management(out_fcUNC,out_fc_lyrUn)
                nList_LyrUn = arcpy.mapping.Layer(out_fcUNC)
                nList_LyrUn.name=out_fcUNC
                arcpy.mapping.RemoveLayer(df,nList_LyrUn)
                arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_LyrUn,'BOTTOM')
                try:
                    lyr = arcpy.mapping.ListLayers(mxd, nList_LyrUn.name, df)[0]
                    arcpy.AddMessage("Change symbology of Uncertainty")
                    symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\Cell_Uncertainty.lyr"
                    arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
                except:
                    pass
        else:
            arcpy.AddWarning("User did not select Sector")

        if NewViewshed == "true":
            if DEM=="empty":
                sys.exit(arcpy.AddError("Need to select DEM to estimate Cellular Coverage"))
            try:
                trPower = float(aPtx)
            except:
                if trPower =="empty":
                    sys.exit(arcpy.AddError("Need to provide a Transmitter Power, or use default value of 60 Watts"))
                else:
                    sys.exit(arcpy.AddError("Format error with Transmitter Power.  Correct or use default value of 60 Watts"))
            try:
                trFreq=float(aFreq_tx)
            except:
                if trFreq =="empty":
                    sys.exit(arcpy.AddError("Need to provide a Transmitter Frequency, or use default value of 900 MHz"))
                else:
                    sys.exit(arcpy.AddError("Format error with Transmitter Frequency.  Correct or use default value of 900 MHz"))
            try:
                trGain = float(aGtx)
            except:
                if trGain =="empty":
                    sys.exit(arcpy.AddError("Need to provide a Transmitter Antenna Gain, or use default value of 10 dB"))
                else:
                    sys.exit(arcpy.AddError("Format error with Transmitter Antenna Gain.  Correct or use default value of 10 dB"))
            try:
                recThres ==float(recThres)
            except:
                if recThres =="empty":
                    sys.exit(arcpy.AddError("Need to provide a Receiver Threshold, or use default value of -90 dBm"))
                else:
                    sys.exit(arcpy.AddError("Format error with Receiver Threshold. Correct or use default value of -90 dBm"))

            arcpy.AddMessage("Estimate coverage for {0}\n".format(descript01))
            # Execute Viewshed
            CellViewshed(cellTower_Layer, DEM, trPower, trFreq, trGain, recThres, aRange, refGroupLayerA, out_fc)
        else:
            arcpy.AddWarning("User did not select Viewshed")
        arcpy.SelectLayerByAttribute_management(cellTower_Layer, "CLEAR_SELECTION")

