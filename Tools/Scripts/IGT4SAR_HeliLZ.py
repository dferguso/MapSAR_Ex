#-------------------------------------------------------------------------------
# Name:        IGT4SAR_HeliLZ.py
# Purpose:
#  This tool creates an estimate for helicopter landing zones within a pre-
#  defined area based on user input.

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
#import datetime
import arcgisscripting, os
from arcpy import env
from arcpy.sa import *

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")
ProdInfo=arcpy.ProductInfo()

# Environment variables
out_fc = os.getcwd()
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

# Get map and dataframe to access properties
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def fcClip(fc, regExt):
    fcDesc = arcpy.Describe(fc)
    dsType = fcDesc.datasetType
    if ("\\" in fc):
        fcr=fc.split("\\")
        cName = fcr[-1]
    else:
        cName = fc
    if dsType == 'RasterDataset' or dsType == 'Raster':
        clipName = cName[0:9] + "_Clp"
        arcpy.Clip_management(fc, "#", clipName, regExt, "", "ClippingGeometry")
    elif dsType == 'FeatureClass':
        clipName = cName +"_Clp"
        arcpy.Clip_analysis(fc, regExt, clipName, "")
    else:
        arcpy.AddError('{0} is of unknown datatype'.format(fc.name))
    return(clipName)


def LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt):
    arcpy.SelectLayerByLocation_management(fcLyr, "INTERSECT", RegExt, "", "NEW_SELECTION")
    arcpy.SelectLayerByAttribute_management(fcLyr,"SUBSET_SELECTION",where1)
    try:
        fcCount = int(arcpy.GetCount_management(fcLyr).getOutput(0))
    except:
        fcCount=0
    SpecNames=["ROAD_BUFF","UTLYBG_BUFF"]
    if fcCount > 0:
        fcClpLyr = fcClip(fcLyr, RegExt)
        fcCnt = int(arcpy.GetCount_management(fcClpLyr).getOutput(0))
        if fcCnt > 0:
            arcpy.AddMessage(BuffName)
            if BuffName in SpecNames:
                BuffDist='{0} Meters'.format(int(2*CellSize))
            else:
                BuffDist='{0} Meters'.format(int(100.0))
            arcpy.Buffer_analysis(fcClpLyr, BuffName, BuffDist,"","","ALL")
            arcpy.AddField_management(BuffName, "Value","SHORT")
            arcpy.CalculateField_management(BuffName, "Value", rValue)
            arcpy.FeatureToRaster_conversion(BuffName, "Value", RstrName, CellSize)
            try:
                arcpy.Delete_management(wrkspc + '\\' + BuffName)
            except:
                pass
        else:
            arcpy.CopyRaster_management(RstrConst,RstrName)
        try:
            arcpy.Delete_management(wrkspc + '\\' + fcClpLyr)
        except:
            pass


    else:
        arcpy.AddMessage(Message)
        arcpy.CopyRaster_management(RstrConst,RstrName)
    arcpy.SelectLayerByAttribute_management(fcLyr,"CLEAR_SELECTION")

def deleteLayer(df,fcLayer):
    for lyr in fcLayer:
        for ii in arcpy.mapping.ListLayers(mxd, lyr):
            try:
                print "Deleting layer", ii
                arcpy.mapping.RemoveLayer(df , ii)
            except:
                pass
    return()


if __name__ == '__main__':
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
##    timestamp = ''
##    now = datetime.datetime.now()
##    todaydate = now.strftime("%m_%d")
##    todaytime = now.strftime("%H_%M_%p")
##    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    wrkspc = arcpy.GetParameterAsText(0)  # Get the subject number
    global wrkspc
    arcpy.AddMessage("\nCurrent Workspace" + '\n' + wrkspc + '\n')
    env.workspace = wrkspc

    RegExt = arcpy.GetParameterAsText(1)  # Extent of the area for analysis

    DEM2 = arcpy.GetParameterAsText(2)
    if DEM2 == '#' or not DEM2:
    #    DEM2 = "DEM" # provide a default value if unspecified
        arcpy.AddError("You need to provide a valid DEM")

    NLCD = arcpy.GetParameterAsText(3)
    if NLCD == '#' or not NLCD:
    #    NLCD = "NLCD" # provide a default value if unspecified
        NLCD = "empty"

    uSeStr= arcpy.GetParameterAsText(4) # Desired units
    if uSeStr == '#' or not uSeStr:
        uSeStr = "true" # provide a default value if unspecified

    safeKM2 = arcpy.GetParameterAsText(5)
    if safeKM2 == '#' or not safeKM2:
        arcpy.AddMessage('Default value of 1 acre = 0.004 KM**2 used as minimum flat area needed for landing zone.')
        safeKM2 = 0.004 # 1 acre = 0.004 km**2
    safeKM2 = float(safeKM2)

    safeSlope = arcpy.GetParameterAsText(6)
    if safeSlope == '#' or not safeSlope:
        arcpy.AddMessage('Default maximum safe slope of 5 degrees was used.')
        safeSlope = 5.0
    safeSlope = float(safeSlope)

    # Get coordinate system for the DEM.  The Coordinate System should
    # be the same for all selected layers.
    spRefDEM = arcpy.Describe(DEM2).SpatialReference
    spnDEM =spRefDEM.name
    spnDEMcode = spRefDEM.projectionCode
    arcpy.AddMessage("DEM Spatial Reference is: " + spnDEM)

    fcDesc = arcpy.Describe(RegExt)
    spatialRef = fcDesc.SpatialReference
    spn = spatialRef.name
    spnCode = spatialRef.projectionCode

    if spnDEMcode != spnCode:
        State1 = "Project DEM using 'Project Raster tool' with the output coord system:"
        State2 = "Select the appropriate coord transformation for your data and"
        State3 = "use the default Cell Size. Use the projected DEM for this tool."
        arcpy.AddError(State1)
        arcpy.AddError(spn)
        arcpy.AddError(State2)
        arcpy.AddError(State3)
        sys.exit()

    # Set the cell size environment using a raster dataset.
    #arcpy.env.cellSize = DEM2
    arcpy.AddMessage("Get Cellsize")

    XCel = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
    XCell = float(XCel.getOutput(0))
    CellSize = int(XCell)
    BuffSize = str(CellSize * 1.5)
    Buff = '"'+ BuffSize + ' Meters"'
    arcpy.AddMessage("Cellsize is " + str(CellSize))

    ## Safe helicopter landing zone size
    ## iHOG suggests a safe diameter of 90 ft but let's give the bird some buffer
    ## safe landing requires a 5d slope over a 1 acre area
    ## 1 acre = 4046m**2 = 63.6m x 63.6 m
    ## 1 km**2 = 1000m x 1000m = 1e6m**2
    uNits=spRefDEM.linearUnitName
    if uNits.upper() == 'METER':
        mult = 1.0
    elif uNits.upper() == 'KILOMETER':
        mult = 0.001
    elif units.upper()== "FOOT":
        mult = 3.28084 # feet to meter
    elif units.upper()== "FEET":
        mult = 3.28084 # feet to meter
    else:
        arcpy.AddMessage(' could not compute requirements for {0} due to inconsistent units'.format(DEM2))
    safeSize = math.sqrt(float(safeKM2))/1000.0
    CellNum = math.ceil(safeSize / (CellSize*mult))

#############################################
    # Process the DEM and determine slope
    # Clip DEM to the desire extent
    demClip = fcClip(DEM2, RegExt)

    demDesc = arcpy.Describe(demClip)
    extent = demDesc.extent
    arcpy.env.extent = extent

    # Calulate the slope for the desired extent.
    outSlope = Slope(demClip, "DEGREE", "1")

    arcpy.AddMessage("Process Slope - only consider slope <= {0} degrees".format(safeSlope))
    # For terrain with slope greater than
    safeSlp = "Value > {0}".format(safeSlope)

    outSlope5=SetNull(outSlope,100,safeSlp)
    # Perform Region Group to define regions that have a slope < = 5 that are
    # at leaast 1 acre (4046 m**2) in size.
    outRgnGrp = RegionGroup(outSlope5, "FOUR", "WITHIN", "NO_LINK", 0)
    lookUpGrp = Lookup(outRgnGrp, "Count")
    setNullValue = "Value < {0}".format(CellNum)
    Slope5a = SetNull(lookUpGrp,100,setNullValue)
    Slope5a.save('Slope5')

    del outSlope, outSlope5, outRgnGrp, lookUpGrp, Slope5a
#############################################
    # Create a constant value Raster which is used in calculations when required
    # feature layers do not exist.  First a Raster with "0" value across the
    # defined "extent" is created and then converted to a NULL value raster.
    arcpy.AddMessage("Create NULL value raster")

    RstrConstA = "RstrConstA"
    RstrC = "RstrC"

    outConstRaster = CreateConstantRaster(0, "INTEGER", CellSize, extent)
    # Save the output
    outConstRaster.save(RstrConstA)

    arcpy.DefineProjection_management(RstrConstA, spatialRef)
    whereClause = "Value = 0"
    OutRstrConst=SetNull(RstrConstA, RstrConstA, whereClause)
    OutRstrConst.save(RstrC)

    # Clip the Constant Raster to ensure it is the desired size.
    RstrConst = fcClip(RstrC, RegExt)

    arcpy.Delete_management(wrkspc + '\\' + RstrConstA)
    arcpy.Delete_management(wrkspc + '\\' + RstrC)
    del OutRstrConst

#############################################
    # Generate a list of layers in the df
    layer_names=[str(f.name) for f in arcpy.mapping.ListLayers(mxd,"",df)]
    if "Water_Polygon" in layer_names:
        Water = "Water_Polygon"
    elif "WaterBodies" in layer_names:
        Water = "WaterBodies"

    # Check to make sure the follow layers exist
    fc_Lyrs = ["Assets", "Roads", "Streams", Water, "FenceLine",
                "PowerLines", "Buildings", "CellTowers"]
#############################################
    # Process the Land Cover
    arcpy.AddMessage("Process Land Cover - Reclassify for Probability for Landing Zone")
    if NLCD:
        NLCDClip = fcClip(NLCD, RegExt)
        outReclass1 = Reclassify(NLCDClip, "Value",
                             RemapValue([[11,0],[12,50],[21,100],[22,100],[23,100],
                                         [24,100],[31,75],[32,70],[41,25],[42,25],
                                         [43,25],[51,90],[52,90],[71,100],[72,90],
                                         [73,90],[74,90],[81,100],[82,90],[90,0],
                                         [92,0],[93,0],[94,0],[95,0],[96,0],
                                         [97,0],[98,0],[99,0]]),"NODATA")
        outReclass1.save("NLCD_LZ")
        del outReclass1
        arcpy.Delete_management(wrkspc + '\\' + NLCDClip)
    else:
        arcpy.CopyRaster_management(ImpdConst,'NLCD_LZ')


#############################################
    # check for existing Landing Zones and aerial hazards as defined in the
    # "Assets" layer
    arcpy.AddMessage("Process any existing Landing Zones or Aerial Hazards")
    RstrN = ['EXISTNG_LZ', 'AirHAZ_LZ']
    fcLyr = fc_Lyrs[0]

    if fcLyr in layer_names:
        arcpy.SelectLayerByAttribute_management(fcLyr,"CLEAR_SELECTION")
        fldName = "Asset_Type"
        airHaz=18
        field_names=[f.name for f in arcpy.ListFields(fcLyr)]

        if (fldName in field_names):
            # Existing Landing Zones
            where1= '"{0}" BETWEEN 9 AND 14'.format(fldName)
            BuffName = "ExstLZ_Buff"
            rValue = 100
            RstrName = RstrN[0]
            Message = "     No Existing Landing Zones Identitied"
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
            del where1, BuffName, rValue, RstrName, Message

            # Aerial Hazards
            where1= '"{0}" = {1}'.format(fldName, airHaz)
            BuffName = "AirHAZ_Buff"
            rValue = 0
            RstrName = RstrN[1]
            Message = "     No Air Hazards Identitied in Assets Layer"
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
            del where1, BuffName, rValue, RstrName, Message
        else:
            arcpy.AddMessage("     the field: {0} is missing from the {1} layer".format(fldName, fcLyr))
            for RName in RstrN:
                arcpy.CopyRaster_management(RstrConst,RName)

    else:
        arcpy.AddMessage("     The {0} LAYER is missing.  Assuming no existing LZ's or Aerial Hazards (excluding Buildings layer)".format(fc_Lyrs[0]))
        for RName in RstrN:
            arcpy.CopyRaster_management(RstrConst,RName)

    del fcLyr, RstrN
#################################################
    # Process Roads
    arcpy.AddMessage("Process Roads - Roads provide potential for LZ")
    fcLyr = fc_Lyrs[1]
    BuffName = 'ROAD_BUFF'
    rValue = 100
    RstrName = 'ROAD_LZ'
    where1=""
    fldName=""
    Message = "     The {0} LAYER is missing.".format(fcLyr)
    if fcLyr in layer_names:
        LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
    else:
        arcpy.AddMessage("     The {0} LAYER is missing.".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)

    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

###############################################
    # Process Streams
    arcpy.AddMessage("Process Streams")
    if uSeStr.upper() == "TRUE":
        arcpy.AddMessage("     Calculate Stream Order - Fill")
        pStrFill = "Str_Fill"
        pStream_Impd = "Stream_Impd"
        pStrImpd = "Str_Impd"
        pOutFlow = "Out_Flow"
        pFlowAcc = "Flow_Acc"
        pStrAcc = "Str_Acc"
        pStrOrder = "Str_Order"
        pStrExp = "Str_Exp"

        # Execute Fill
        outFill = Fill(demClip)
        # Save the output

        outFill.save(pStrFill)

        arcpy.AddMessage("     Calculate Stream Order - Flow Direction")
        outFlowDirection = FlowDirection(pStrFill, "NORMAL")
        outFlowDirection.save(pOutFlow)

        # Set local variables
        dataType = "FLOAT"
        # Execute FlowDirection
        arcpy.AddMessage("     Calculate Stream Order - Flow Accumlation")
        outFlowAccumulation = FlowAccumulation(pOutFlow, "", dataType)

        # Save the output
        outFlowAccumulation.save(pFlowAcc)
        outNull = SetNull(Raster(pFlowAcc)<500,1)
        outNull.save(pStrAcc)
        del outNull

        orderMethod = "STRAHLER"
        # Execute StreamOrder
        arcpy.AddMessage("     Calculate Stream Order - Strahler")
        outStreamOrder = StreamOrder(pStrAcc, pOutFlow, orderMethod)
        # Save the output
        outStreamOrder.save(pStrOrder)

        # Set local variables
        numberCells = 2
        zoneValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        arcpy.AddMessage("     Calculate Stream Order - Expand Strahler to 2x2 neighbors")
        # Execute Expand
        outExpand = Expand(pStrOrder, numberCells, zoneValues)

        # Save the output
        outExpand.save(pStrExp)

        arcpy.AddMessage("     Reclassify Stream Order to Stream LZ Probabilty")
        # Set local variables
        # Execute Reclassify
        outRaster = Reclassify(pStrExp, "Value",
                     RemapValue([[1,90],[2,80],[3,50],[4,25],[5,0],
                                 [6,0],[7,0],[8,0],[9,0]]),"NODATA")
        outRaster.save("STRM_LZ")
        del outRaster

        arcpy.Delete_management(wrkspc + '\\' + pStrFill)
        arcpy.Delete_management(wrkspc + '\\' + pOutFlow)
        arcpy.Delete_management(wrkspc + '\\' + pFlowAcc)
        arcpy.Delete_management(wrkspc + '\\' + pStrAcc)
        arcpy.Delete_management(wrkspc + '\\' + pStrOrder)
        arcpy.Delete_management(wrkspc + '\\' + pStrExp)
    else:
        fcLyr = fc_Lyrs[2]
        BuffName = 'STRM_BUFF'
        rValue = 0
        RstrName = 'STRM_LZ'
        where1=""
        fldName=""
        Message = "     The {0} LAYER is empty.".format(fcLyr)
        if fcLyr in layer_names:
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
        else:
            arcpy.AddMessage("     The {0} LAYER is missing.  Recommend re-processing using Stream Order".format(fcLyr))
            arcpy.CopyRaster_management(RstrConst,RstrName)

        del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

    try:
        arcpy.Delete_management(wrkspc + '\\' + demClip)
    except:
        pass
####################################################
    # Process Water Polygons
    arcpy.AddMessage("Process Waterbodies which constitute a hazard for an LZ")
    fcLyr = fc_Lyrs[3]
    BuffName = 'WTR_BUFF'
    rValue = 0
    RstrName = 'WTRBDY_LZ'
    where1=""
    fldName=""
    Message = "     The {0} LAYER is empty.".format(fcLyr)
    if fcLyr in layer_names:
        LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
    else:
        arcpy.AddMessage("     The {0} LAYER is missing.".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)

    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message


####################################################
    # Fencelines
    arcpy.AddMessage("Process Fencelines which constitute a hazard for an LZ")
    fcLyr = fc_Lyrs[4]
    BuffName = 'FENCE_BUFF'
    rValue = 0
    RstrName = 'FENCE_LZ'
    where1=""
    fldName=""
    Message = "     The {0} LAYER is empty.".format(fcLyr)
    if fcLyr in layer_names:
        LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
    else:
        arcpy.AddMessage("     The {0} LAYER is missing.".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)

    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

###############################################
    # Powerlines
    arcpy.AddMessage("Process Utility Lines which may constitute a hazard for an LZ if Above Ground")
    fcLyr = fc_Lyrs[5]
    RstrName = 'UTLY_LZ'
    if fcLyr in layer_names:
        BuffName = 'UTLY_BUFF'
        rValue = 0
        where1= ""
        Message = "     No Utilities Identified"
        arcpy.SelectLayerByAttribute_management(fcLyr,"CLEAR_SELECTION")
        fldName = "AboveGround"
        field_names=[f.name for f in arcpy.ListFields(fcLyr)]
        if (fldName in field_names):
            UTLYAG_LZ = 'UTLYAG_LZ'
            UTLYBG_LZ = 'UTLYBG_LZ'
            # Above Ground Utilities
            BuffName = 'UTLYAG_BUFF'
            rValue = 0
            RstrName = UTLYAG_LZ
            where1= '"{0}" = {1}'.format(fldName, "'Yes'")
            Message = "     No Above Ground Utility Lines Indentified"
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)

            # Below Ground Utilities
            BuffName = 'UTLYBG_BUFF'
            rValue = 75
            RstrName = UTLYBG_LZ
            where1= '"{0}" = {1}'.format(fldName, "'No'")
            Message = "     No Below Ground Utility Lines Indentified"
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)

            RstrName = 'UTLY_LZ'
            OutCon=Con(IsNull(Raster(UTLYAG_LZ)),Raster(UTLYBG_LZ),Raster(UTLYAG_LZ))
            OutCon.save(RstrName)
            del OutCon
            arcpy.Delete_management(wrkspc + '\\' + UTLYAG_LZ)
            arcpy.Delete_management(wrkspc + '\\' + UTLYBG_LZ)

        else:
            fldName=""
            LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
            del fcLyr, BuffName, rValue, RstrName, where1, fldName, Messagee

    else:
        arcpy.AddMessage("     The {0} LAYER is missing.)".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)
    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

###############################################
    # Buildings
    arcpy.AddMessage("Process Buildings which constitute a hazard for an LZ")
    fcLyr = fc_Lyrs[6]
    BuffName = 'BUILD_BUFF'
    rValue = 0
    RstrName = 'BUILD_LZ'
    where1=""
    fldName=""
    Message = "     The {0} LAYER is empty.".format(fcLyr)
    if fcLyr in layer_names:
        LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
    else:
        arcpy.AddMessage("     The {0} LAYER is missing.".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)

    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

###############################################
    # Cell Towers
    arcpy.AddMessage("Process Celltowers which constitute a hazard for an LZ")
    fcLyr = fc_Lyrs[7]
    BuffName = 'CELL_BUFF'
    rValue = 0
    RstrName = 'CELL_LZ'
    where1=""
    fldName=""
    Message = "     The {0} LAYER is empty.".format(fcLyr)
    if fcLyr in layer_names:
        LZandHAZ(where1, fcLyr, BuffName, fldName, rValue, RstrName, CellSize, Message, RstrConst, RegExt)
    else:
        arcpy.AddMessage("     The {0} LAYER is missing.".format(fcLyr))
        arcpy.CopyRaster_management(RstrConst,RstrName)

    del fcLyr, BuffName, rValue, RstrName, where1, fldName, Message

####################################################################
    # Available Raster Layers
    # SlopeFcLyr, 'NLCD_LZ', 'ROAD_LZ', 'STRM_LZ'. 'WTRBDY_LZ', 'FENCE_LZ',
    # 'UTLY_LZ','BUILD_LZ','CELL_LZ', 'Existng_LZ', 'AirHAZ_LZ']
    arcpy.AddMessage('Create a Raster of potential hazards')
    HAZARDS = 'HAZARDS'
    OutRstr=Con(IsNull(Raster('AirHAZ_LZ')),
            Con(IsNull(Raster('FENCE_LZ')),
            Con(IsNull(Raster('UTLY_LZ')),
            Con(IsNull(Raster('CELL_LZ')),
            Raster('BUILD_LZ'),
            Raster('CELL_LZ')),
            Raster('UTLY_LZ')),
            Raster('FENCE_LZ')),
            Raster('AirHAZ_LZ'))
    OutRstr.save(HAZARDS)
    del OutRstr
    arcpy.AddMessage('Add HAZARDS layer to data frame')
    HAZ_Layer=arcpy.mapping.Layer(HAZARDS)
    arcpy.mapping.AddLayer(df,HAZ_Layer,"BOTTOM")

    arcpy.AddMessage('Create a Raster of preferred Landing Zones')
    PFR_LZ = 'PFR_LZ'
    OutRstr=Con(IsNull(Raster(HAZARDS)),
           Con(IsNull(Raster('ROAD_LZ')),
           Con(IsNull(Raster('WTRBDY_LZ')),
           Con(IsNull(Raster('STRM_LZ')),
           Raster('NLCD_LZ'),
           Con(Raster('STRM_LZ')<Raster('NLCD_LZ'),Raster('STRM_LZ'),Raster('NLCD_LZ'))),
           Raster('WTRBDY_LZ')),
           Raster('ROAD_LZ')),
           Raster(HAZARDS))
    OutRstr.save(PFR_LZ)
    del OutRstr
    arcpy.AddMessage('Add PREFERRED LZ layer to data frame')
    PFR_Layer=arcpy.mapping.Layer(PFR_LZ)
    arcpy.mapping.AddLayer(df,PFR_Layer,"BOTTOM")

    arcpy.AddMessage("Create a Raster of Probable Land Zones based on Preferred LZ's and Hazards ")
    PREFR_LZ = 'Heli_LZ'
##    OutRstr = Con(IsNull(Raster('EXISTNG_LZ')),
##              Con(IsNull(Raster('Slope5')),
##              Raster('Slope5'),SetNull(Raster(PFR_LZ)==0,Raster(PFR_LZ))),
##              Raster('EXISTNG_LZ'))

    OutRstr = Con(IsNull(Raster('EXISTNG_LZ')),
              Con(IsNull(Raster('Slope5')),
              0,Raster(PFR_LZ)),
              Raster('EXISTNG_LZ'))
    OutRstr.save(PREFR_LZ)
    del OutRstr
    arcpy.AddMessage('Add PROBABLE LZ layer to data frame')
    PFRR_Layer=arcpy.mapping.Layer(PREFR_LZ)

    if "Air Operations" in layer_names:
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Air Operations*',df)[0]
        arcpy.mapping.AddLayerToGroup(df,refGroupLayer,PFRR_Layer,'TOP')
    else:
        arcpy.mapping.AddLayer(df,PFRR_Layer,"BOTTOM")

    ##############################
    fcLayer=['HAZARDS', 'PFR_LZ','Slp5dFC']
    RstList=[RstrConst,'HAZARDS','AirHAZ_LZ','UTLY_LZ','CELL_LZ','BUILD_LZ', 'PFR_LZ',
             'EXISTNG_LZ','ROAD_LZ','WTRBDY_LZ','STRM_LZ','FENCE_LZ','Slp5dFC','NLCD_LZ','Slope5']
##
    for lyr in fcLayer:
        for ii in arcpy.mapping.ListLayers(mxd, lyr):
            try:
                arcpy.mapping.RemoveLayer(df , ii)
            except:
                pass
##
    for gg in RstList:
        if arcpy.Exists(gg):
            try:
                arcpy.Delete_management(wrkspc + '\\' + gg)
            except:
                pass


