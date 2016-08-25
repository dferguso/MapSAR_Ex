#-------------------------------------------------------------------------------
# Name:     IGT4SAR_Cell_Coverage.py
# Purpose:  The tool uses as input a point feature class (ASSETS) and input
#           related to the performance of a wireless communication system to
#           calculate an estimate of signal strength in a pre-defined area.
#
# Author:   Don Ferguson
#
# Created:  10/15/2015
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
#import re
#import arcgisscripting, os
from arcpy import env
from arcpy.sa import *
from string import punctuation

invalidChars = set(punctuation)


# Create the Geoprocessor objects
#gp = arcgisscripting.create()

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

def AddViewFields(in_fc, fldNames):
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
                #arcpy.AddField_management(*(in_fc,) + field)
                arcpy.AddField_management(in_fc, field[0],field[1],'','','',field[2])

        del fieldnames, compList, field
    del fName
    return(chkList)

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

    outRstrb = "{0}_SigStrgth".format(out_fc)
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

########
# Main Program starts here
#######
if __name__ == '__main__':
    ## Script arguments
    mxd,df = getDataframe()

    #inFeature  - this is a point feature used to get the latitude and longitude of point.
    aSsets =arcpy.GetParameterAsText(0)
    if aSsets == '#' or not aSsets:
        aSsets = "empty"

    DEM = arcpy.GetParameterAsText(1)
    if DEM == '#' or not DEM:
        DEM = "empty"

    recThres = arcpy.GetParameterAsText(2)
    if recThres == '#' or not recThres:
        recThres = "empty"

    checkSR(DEM)
    inFC = 'Assets'
    arcpy.AddMessage('\n')
    ## Variables
    fldNames=[('OFFSETA', 'SHORT', 'OFFSETA (DEM Units)'),('OFFSETB', 'SHORT','OFFSETB (DEM Units)'), \
              ('AZIMUTH1', 'SHORT','AZIMUTH1 (deg)'),('AZIMUTH2', 'SHORT','AZIMUTH2 (deg)'),('VERT1', 'SHORT', 'VERT1 (deg)'), \
              ('VERT2', 'SHORT', 'VERT2 (deg)'),('RADIUS1', 'SHORT','RADIUS1 (DEM Units)'),('RADIUS2', 'SHORT','RADIUS2 (DEM Units)'), \
               ('Ptx', 'FLOAT','Transmit Power (W)'), ('Gtx','FLOAT','Transmit Antenna Gain (dB)'),('Freq_tx', 'FLOAT','Transmit Frequency (MHz)')]

    # Get the Sptial Reference from the DEM and linear Units
    DEM_lyr = arcpy.mapping.Layer(DEM)
    # Use Describe to get a SpatialReference object
    descPlanPt = arcpy.Describe(DEM_lyr)
    PlanPtCS = descPlanPt.SpatialReference
    aUnits = str(PlanPtCS.linearUnitName)

    #

    # Get a List of Layers
    LyrList=arcpy.mapping.ListLayers(mxd, "*", df)
    LyrName=[]
    refGroupLayerA = " "
    Asset_Layer=inFC
    for lyr in LyrList:
        LyrName.append(lyr.name)
    if inFC in LyrName:
        arcpy.SelectLayerByAttribute_management(Asset_Layer, "CLEAR_SELECTION")

        chkListB = AddViewFields(inFC, fldNames)
        if len(chkListB)>0:
            for chk in chkListB:
                arcpy.AddError('You need to enter a value in {0}'.format(chk))
            sys.exit(1)
    else:
        sys.exit(arcpy.AddError("This tool requires a feature class called 'ASSETS' with appropriate fields describing wireless communication system.\n "))
    if "Communications" in LyrName:
        refGroupLayerA = arcpy.mapping.ListLayers(mxd,"Communications",df)[0]
############################################################
    if aSsets=="empty":
        sys.exit(arcpy.AddError("Please select one or more ASETS to consider if no towers are listed check that the 'Asset_Type' field in the 'Assets' layer is populated.'\n "))
    else:
        astPts = aSsets.split(";")
        astPts=[x.replace("'","") for x in astPts]
        astPts=[x.encode('ascii') for x in astPts]

    arcpy.SelectLayerByAttribute_management(Asset_Layer, "CLEAR_SELECTION")

    for aSstPt in astPts:
        NewPt = aSstPt.split("-")
        NewPt=[k.lstrip() for k in NewPt]
        NewPt=[k.rstrip() for k in NewPt]
        if len(NewPt) < 3:
            where_clause = 'Asset_Type = {0}'.format(NewPt[0])
            descript = 'NoDescription'
        else:
            descript = NewPt[2].replace(" ", "")
            if any(char in invalidChars for char in descript):
                sys.exit(arcpy.AddError("Special Characters are not allowed in the Description"))
            where_clause = 'Asset_Type = {0} AND Description = \'{1}\''.format(NewPt[0],NewPt[2])

        arcpy.SelectLayerByAttribute_management(Asset_Layer, "NEW_SELECTION", where_clause)
        cursor = arcpy.SearchCursor(Asset_Layer, where_clause)
        for row in cursor:
            desType =row.getValue('Asset_Type')
            if desType is None:
                sys.exit(arcpy.AddError("Check Asset_Type in Assets Layer for the selected Feature"))
            aOffsetA =row.getValue('OFFSETA')
            if aOffsetA is None:
                sys.exit(arcpy.AddError("Check OFFSETA in Assets Layer for the selected Feature"))
            aOffsetB =row.getValue('OFFSETB')
            if aOffsetB is None:
                sys.exit(arcpy.AddError("Check OFFSETB in Assets Layer for the selected Feature"))
            aAzimuth1 =row.getValue('AZIMUTH1')
            if aAzimuth1 is None:
                sys.exit(arcpy.AddError("Check AZIMUTH1 in Assets Layer for the selected Feature"))
            aAzimuth2 =row.getValue('AZIMUTH2')
            if aAzimuth2 is None:
                sys.exit(arcpy.AddError("Check AZIMUTH2 in Assets Layer for the selected Feature"))
            aVert1 =row.getValue('VERT1')
            if aVert1 is None:
                sys.exit(arcpy.AddError("Check VERT1 in Assets Layer for the selected Feature"))
            aVert2 =row.getValue('VERT2')
            if aVert2 is None:
                sys.exit(arcpy.AddError("Check VERT2 in Assets Layer for the selected Feature"))
            aRadius1 =row.getValue('RADIUS1')
            if aRadius1 is None:
                sys.exit(arcpy.AddError("Check RADIUS1 in Assets Layer for the selected Feature"))
            aRadius2 =row.getValue('RADIUS2')
            if aRadius2 is None:
                sys.exit(arcpy.AddError("Check RADIUS2 in Assets Layer for the selected Feature"))
            aPtx = row.getValue('Ptx')
            if aPtx is None:
                sys.exit(arcpy.AddError("Check Transmit Power in Assets Layer for the selected Feature"))
            aGtx = row.getValue('Gtx')
            if aGtx is None:
                sys.exit(arcpy.AddError("Check Transmit Antenna Gain in Assets Layer for the selected Feature"))
            aFreq_tx = row.getValue('Freq_tx')
            if aFreq_tx is None:
                sys.exit(arcpy.AddError("Check Transmit Frequency in Assets Layer for the selected Feature"))
            aRng = [float(aRadius1), float(aRadius2)]
            Rng = max(aRng)
        del cursor, row

        theDist = "{0} {1}".format(Rng, aUnits)
        out_fc="{0}_Ptx{1}_Freq{2}".format(descript,str(int(aPtx)),str(int(aFreq_tx)))
        try:
            arcpy.Delete_management(out_fc)
        except:
            pass

        arcpy.Buffer_analysis(inFC, out_fc, theDist)
        if arcpy.Exists(out_fc):
            out_fc_lyr="{0}_Lyr".format(out_fc)
            arcpy.MakeFeatureLayer_management(out_fc,out_fc_lyr)
            nList_Lyr = arcpy.mapping.Layer(out_fc)
            nList_Lyr.name=out_fc
            try:
                arcpy.mapping.RemoveLayer(df,nList_Lyr)
            except:
                pass
            arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,nList_Lyr,'BOTTOM')

            try:
                lyr = arcpy.mapping.ListLayers(mxd, nList_Lyr.name, df)[0]
                symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\15 Cell Sector.lyr"
                arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
            except:
                pass

            if DEM=="empty":
                sys.exit(arcpy.AddError("Need to select DEM to estimate Cellular Coverage"))
            try:
                recThres ==float(recThres)
            except:
                if recThres =="empty":
                    sys.exit(arcpy.AddError("Need to provide a Receiver Threshold, or use default value of -90 dBm"))
                else:
                    sys.exit(arcpy.AddError("Format error with Receiver Threshold. Correct or use default value of -90 dBm"))

            arcpy.AddMessage("Estimate signal strength for {0}\n".format(descript))
            # Execute Viewshed
            CellViewshed(Asset_Layer, DEM, aPtx, aFreq_tx, aGtx, recThres, Rng, refGroupLayerA, out_fc)

        arcpy.SelectLayerByAttribute_management(Asset_Layer, "CLEAR_SELECTION")

