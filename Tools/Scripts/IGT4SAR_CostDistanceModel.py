#-------------------------------------------------------------------------------
# Name:        CostDistanceModel.py
# Purpose:
#  This tool creates a least cost path across a continuous surface
#  for use in modeling cross country foot traffic.  The surface is created using
#  Tobler's Hiking Function to account for the slope, access to travel aides
#  (Trails, Roads and right-of-ways).  Barriers that impose an impedance are also
#  considered and include: excessive slope, stream order, large bodies of water
#  and fencelines (real and virtual).  Given the layers and important nominal,
#  unimpeded walking speed the output is a surface representing the potential
#  walking speed (mph and kph).</p>

# Author:      Don Ferguson
#
# Created:     12/12/2012
# Copyright:   (c) Don Ferguson 2012
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
    arcpy.mapping
except NameError:
    import arcpy.mapping
import arcgisscripting, os
from arcpy import env
from arcpy.sa import *

def findField(fc, myField):
    fieldList = arcpy.ListFields(fc)
    fieldCount=0
    booln="False"
    for field in fieldList:
        if field.name == myField:
            fieldName = field.name
            booln="True"
            rows = arcpy.SearchCursor(fc,"","",myField)
            for row in rows:
                if row.getValue(fieldName):
                    fieldCount+=1
            del fieldName
    return booln,fieldCount


# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Environment variables
out_fc = os.getcwd()
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

mxd = arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

wrkspc = arcpy.GetParameterAsText(0)  # Get the subject number
arcpy.AddMessage("\nCurrent Workspace" + '\n' + wrkspc + '\n')
env.workspace = wrkspc

SubNum = arcpy.GetParameterAsText(1)  # Get the subject number
if SubNum == '#' or not SubNum:
    SubNum = "1" # provide a default value if unspecified

ippType = arcpy.GetParameterAsText(2)  # Determine to use PLS or LKP

TheoDist = arcpy.GetParameterAsText(3)
if TheoDist == '#' or not TheoDist:
    TheoDist = "0" # provide a default value if unspecified

bufferUnit = arcpy.GetParameterAsText(4) # Desired units
if bufferUnit == '#' or not bufferUnit:
    bufferUnit = "miles" # provide a default value if unspecified

uSeStr= arcpy.GetParameterAsText(5) # Desired units
if uSeStr == '#' or not uSeStr:
    uSeStr = "true" # provide a default value if unspecified

DEM2 = arcpy.GetParameterAsText(6)
if DEM2 == '#' or not DEM2:
#    DEM2 = "DEM" # provide a default value if unspecified
    arcpy.AddMessage("You need to provide a valid DEM")

NLCD = arcpy.GetParameterAsText(7)
if NLCD == '#' or not NLCD:
#    NLCD = "NLCD" # provide a default value if unspecified
    NLCD = "empty"


Roads = "Roads"
Trails = "Trails"
pStreams = "Streams"
Water = "Water_Polygon"
Fence = "FenceLine"
Electric = "PowerLines"


#Tables
cfcc = "C:\MapSAR_Ex\Template\SAR_Default.gdb\cfcc"
TrailClass = "C:\MapSAR_Ex\Template\SAR_Default.gdb\Trail_Class"
LandCoverClass = "C:\MapSAR_Ex\Template\SAR_Default.gdb\LandCover_Class"
##LandCoverClass = "LandCover_Class"
inRemapTable = "C:\MapSAR_Ex\Template\SAR_Default.gdb\StreamOrder"

#File Names:
IPP = "Planning Point"
IPP_dist = "IPPTheoDistance"
Roads_Clipped = "Roads_Clipped"
Roads_Buf = "Roads_Buffered"
Trails_Clipped = "Trails_Clipped"
Trails_Buf = "Trails_Buffered"
pStreams_Clipped = "Streams_Clipped"
pStreams_Buf = "Streams_Buffered"
Electric_Clipped = "Electric_Clipped"
Electric_Buf = "Electric_Buffered"
Fence_Clipped = "Fence_Clipped"
Fence_Buf = "Fence_Buffered"
Water_Clipped = "Water_Clipped"
clip_Block = "clip_block"
NLCD_Clip = "NLCD_clipped"
DEM_Clip = "DEM_clipped"
#
NLCD_Resample2 = "NLCD_Resample"
DEM_Resample2 = "DEM_Resample"

# Rasters
Water_Impd = "Water_Impd"
pStrFill = "Str_Fill"
pStream_Impd = "Stream_Impd"
pStrImpd = "Str_Impd"
pOutFlow = "Out_Flow"
pFlowAcc = "Flow_Acc"
pStrAcc = "Str_Acc"
pStrOrder = "Str_Order"
pStrExp = "Str_Exp"
Tobler_kph = "Tobler_kph"
Tspd_kph = "Tspd_kph"

Trail_Impd = "Trail_Impd"
Road_Impd = "Road_Impd"
Utility_Impd = "Utility_Impd"
Fence_Impd = "Fence_Impd"
Veggie_Impd = "NLCD_Impd"
ImpdConst = "ImpdConst"
ImpdConstA = "ImpdConstA"
ConstImpd="ConstImpd"
#
Sloper = "Slope"
High_Slope = "High_Slope"
Impedance = "Impedance"


# Local variables:
Input_true_raster_or_constant_value = "1"
v3600 = "3600"
Miles_per_Km_Conversion = 0.6213711922

############################################
SubNum = int(SubNum)

theDist = float(TheoDist)
if bufferUnit=="km":
    bufferUnit="Kilometers"
TheoSearch = "{0} {1}".format(theDist, bufferUnit)

arcpy.Compact_management(wrkspc)

#Clip features to max distance
try:
    arcpy.Delete_management(wrkspc + '\\' + IPP_dist)
except:
    pass

# Buffer areas of impact around major roads
where1 = '"Subject_Number" = ' + str(SubNum)
where2 = ' AND "IPPType" = ' + "'" + ippType + "'"
where = where1 + where2

arcpy.SelectLayerByAttribute_management(IPP, "NEW_SELECTION", where)
arcpy.AddMessage("Buffer IPP around the " + ippType )
#############################################

maxSlope = "60"
##maxSlope = "45" #For biking

# Set the cell size environment using a raster dataset.
#arcpy.env.cellSize = DEM2

# Process: Buffer for theoretical search area
arcpy.AddMessage("Buffer IPP")
arcpy.Buffer_analysis(IPP, IPP_dist, TheoSearch)
IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")
spatialRef = arcpy.Describe(IPPDist_Layer).SpatialReference
spn =spatialRef.name

desc = arcpy.Describe(IPP_dist)
extent = desc.extent
arcpy.env.extent = IPP_dist

arcpy.AddMessage("Get Cellsize")

spRefDEM = arcpy.Describe(DEM2).SpatialReference
spnDEM =spRefDEM.name
arcpy.AddMessage("DEM Spatial Reference is: " + spnDEM)

if spnDEM.upper() != spn.upper():
    State1 = "Project DEM using 'Project Raster tool' with the output coord system:"
    State2 = "Select the appropriate coord transformation for your data and"
    State3 = "use the default Cell Size. Use the projected DEM for this tool."
    arcpy.AddError(State1)
    arcpy.AddError(spn)
    arcpy.AddError(State2)
    arcpy.AddError(State3)
    sys.exit()

XCel = arcpy.GetRasterProperties_management(DEM2,"CELLSIZEX")
XCell = float(XCel.getOutput(0))
CellSize = XCell
BuffSize = str(CellSize * 1.5)
Buff = '"'+ BuffSize + ' Meters"'
arcpy.AddMessage("Cellsize is " + str(CellSize))


arcpy.AddMessage("Clip DEM to prescribed distance")
########################
arcpy.Clip_management(DEM2, "#", DEM_Clip, IPP_dist, "", "ClippingGeometry")
##DEM_Clip = DEM2
########################
DEMClip_Layer=arcpy.mapping.Layer(DEM_Clip)
arcpy.mapping.AddLayer(df,DEMClip_Layer,"BOTTOM")

# Process: Slope (2)
arcpy.AddMessage("Get Slope from DEM")
# Execute Slope
#outSlope = Slope(DEM_Clip, "DEGREE", "0.304800609601219")
outSlope = Slope(DEM_Clip, "DEGREE", "1")
# Save the output
outSlope.save(Sloper)
del outSlope
Slope_Layer=arcpy.mapping.Layer(Sloper)
arcpy.mapping.AddLayer(df,Slope_Layer,"BOTTOM")

# Process: Con
arcpy.AddMessage("High Slope")
HighSlopeImpedance = 99.0
inTrueRaster = (HighSlopeImpedance)
whereClause = "VALUE >= " + str(maxSlope)
outCon = Con(Raster(Sloper), inTrueRaster, "", whereClause)

# Save the outputs
outCon.save(High_Slope)
del outCon
HighSlope_Layer=arcpy.mapping.Layer(High_Slope)
arcpy.mapping.AddLayer(df,HighSlope_Layer,"BOTTOM")

# Execute CreateConstantRaster
arcpy.AddMessage("Create NULL value raster")
outConstRaster = CreateConstantRaster(0, "INTEGER", CellSize, extent)

# Save the output
outConstRaster.save(ImpdConstA)
arcpy.DefineProjection_management(ImpdConstA, spatialRef)
whereClause = "Value = 0"
outSetNull=SetNull(ImpdConstA, ImpdConstA, whereClause)
outSetNull.save(ImpdConst)

##arcpy.MakeRasterLayer_management(ImpdConst,ConstImpd)
##arcpy.mapping.AddLayer(df,ConstImpd,"BOTTOM")
try:
    arcpy.Delete_management(wrkspc + '\\' + ImpdConstA)
except:
    pass

try:
    if gp.GetCount_management(Roads) == 0:
        arcpy.AddMessage("No Roads")
        arcpy.CopyRaster_management(ImpdConst,Road_Impd)
    else:
        #Roads Processing
        # Process: Clip Roads
    ##        arcpy.AddMessage("Clip Roads and buffer to " + BuffSize + " meters")
        arcpy.AddMessage("Clip Roads and buffer to 15 meters")
        arcpy.Clip_analysis(Roads, IPP_dist, Roads_Clipped, "")
        # Process: Buffer for theoretical search area
        arcpy.Buffer_analysis(Roads_Clipped, Roads_Buf, "15 Meters")

    ################################
    # Need to add in code to verify Roads Layer has CFCC
    ################################

        # Process: Add Join for Roads
        RoadBuf_Layer=arcpy.mapping.Layer(Roads_Buf)
        arcpy.mapping.AddLayer(df,RoadBuf_Layer,"BOTTOM")
        arcpy.AddMessage("create Road Impedance Layer")
        #################
        # Updated June 14, 2014 - Don Ferguson
        # Update to include the use of MTFCC in addition to CFCC
        #################
        cfcc_count=0
        mtcfc_count=0
        rTable="MTFCC"

        checkMtfcc, mtfccCount=findField(Roads_Buf, "MTFCC")
        checkCfcc, cfccCount=findField(Roads_Buf, "CFCC")
        rdsCount = arcpy.GetCount_management(Roads_Buf)

        if checkCfcc==False:
            if checkMtfcc == False:
                arcpy.AddField_management(Roads_Buf, "MTFCC", TEXT)
                rows=arcpy.UpdateCursor(Roads_Buf)
                for row in rows:
                    row.MTFCC = "S1100"
                    rows.updateRow(row)
                del row
                del rows
                rTable="MTFCC"
            else:
                if mtfccCount == rdsCount:
                    rTable="MTFCC"
                else:
                    rTable="MTFCC"
                    rows=arcpy.UpdateCursor(Roads_Buf)
                    for row in rows:
                        if not row.getValue(rTable):
                            row.MTFCC = "S1100"
                        rows.updateRow(row)
                    del row
                    del rows

        else:
            if cfccCount == rdsCount:
                rTable="CFCC"
            else:
                rTable="CFCC"
                rows=arcpy.UpdateCursor(Roads_Buf)
                for row in rows:
                    if not row.getValue(rTable):
                        row.CFCC = "A00"
                    rows.updateRow(row)
                del row
                del rows



        # Process: Polyline to Raster (3)
        arcpy.AddJoin_management(Roads_Buf, rTable, cfcc, rTable, "KEEP_ALL")
        #################
        arcpy.FeatureToRaster_conversion(Roads_Buf, "cfcc.Walk_Impd", Road_Impd, CellSize)
        arcpy.RemoveJoin_management(Roads_Buf)
        arcpy.Delete_management(wrkspc + '\\' + Roads_Buf)
        arcpy.Delete_management(wrkspc + '\\' + Roads_Clipped)

except:
    arcpy.AddMessage("No Road Layer")
    arcpy.CopyRaster_management(ImpdConst,Road_Impd)

RoadImpd_Layer=arcpy.mapping.Layer(Road_Impd)
arcpy.mapping.AddLayer(df,RoadImpd_Layer,"BOTTOM")


try:
    if gp.GetCount_management(Trails) == 0:
        arcpy.AddMessage("No Trails")
        arcpy.CopyRaster_management(ImpdConst,Trail_Impd)
    else:
        #Trail Processing
        # Process: Clip Trails
##        arcpy.AddMessage("Clip Trails and buffer to " + BuffSize + " meters")
        arcpy.AddMessage("Clip Trails and buffer to 15 meters")
        arcpy.Clip_analysis(Trails, IPP_dist, Trails_Clipped, "")

        # Process: Buffer for theoretical search area
        arcpy.Buffer_analysis(Trails_Clipped, Trails_Buf, "15 Meters")

        # Process: Add Join for Trails
        TrailBuf_Layer=arcpy.mapping.Layer(Trails_Buf)
        arcpy.mapping.AddLayer(df,TrailBuf_Layer,"BOTTOM")
        arcpy.AddJoin_management(Trails_Buf, "MAINT_LVL", TrailClass, "Trail_Class", "KEEP_ALL")

        # Process: Polyline to Raster
        arcpy.AddMessage("create Trail Impedance Layer")
        arcpy.FeatureToRaster_conversion(Trails_Buf, "Trail_Class.Walk_Impd", Trail_Impd, CellSize)
        arcpy.RemoveJoin_management(Trails_Buf)
        arcpy.Delete_management(wrkspc + '\\' + Trails_Buf)
        arcpy.Delete_management(wrkspc + '\\' + Trails_Clipped)

except:
    arcpy.AddMessage("No Trails Layer")
    arcpy.CopyRaster_management(ImpdConst,Trail_Impd)

TrailImpd_Layer=arcpy.mapping.Layer(Trail_Impd)
arcpy.mapping.AddLayer(df,TrailImpd_Layer,"BOTTOM")


try:
    if gp.GetCount_management(pStreams) == 0:
        arcpy.AddMessage("No Streams")
        arcpy.CopyRaster_management(ImpdConst,pStream_Impd)
    else:
        # Streams Processing
        # Process: Clip Streams
        arcpy.AddMessage("Clip Streams and buffer to 15 meters")
    ############################################
        arcpy.Clip_analysis(pStreams, IPP_dist, pStreams_Clipped, "")

    ############################################

        # Process: Buffer for theoretical search area
        arcpy.Buffer_analysis(pStreams_Clipped, pStreams_Buf, "15 Meters")

        # Check to see if the Streams polyline already has a "Impd" field.  If not create on
        pStreamImpedance = 20
        if len(arcpy.ListFields(pStreams_Buf,"Impedance")) > 0:
            arcpy.CalculateField_management(pStreams_Buf,"Impedance",pStreamImpedance)
        else:
            # Add the new field and calculate the value
            arcpy.AddField_management(pStreams_Buf, "Impedance", "SHORT")
            arcpy.CalculateField_management(pStreams_Buf,"Impedance",pStreamImpedance)

        # Process: Polyline to Raster
        arcpy.FeatureToRaster_conversion(pStreams_Buf, "Impedance", pStrImpd, CellSize)

        if uSeStr == "true":
            arcpy.AddMessage("Calculate Stream Order - Fill")
            # Execute Fill
            outFill = Fill(DEM_Clip)
            # Save the output
            outFill.save(pStrFill)

            arcpy.AddMessage("Calculate Stream Order - Flow Direction")
            outFlowDirection = FlowDirection(pStrFill, "NORMAL")
            outFlowDirection.save(pOutFlow)

            # Set local variables
            dataType = "FLOAT"
            # Execute FlowDirection
            arcpy.AddMessage("Calculate Stream Order - Flow Accumlation")
            ##May 07, 2013#########################
            ##outFlowAccumulation = FlowAccumulation(pOutFlow, pStrImpd, dataType)
            outFlowAccumulation = FlowAccumulation(pOutFlow, "", dataType)
            ##May 07, 2013#########################

            # Save the output
            outFlowAccumulation.save(pFlowAcc)
            outNull = SetNull(Raster(pFlowAcc)<500,1)
            outNull.save(pStrAcc)
            del outNull

            orderMethod = "STRAHLER"
            # Execute StreamOrder
            arcpy.AddMessage("Calculate Stream Order - Strahler")
            outStreamOrder = StreamOrder(pStrAcc, pOutFlow, orderMethod)
            # Save the output
            outStreamOrder.save(pStrOrder)

            # Set local variables
            numberCells = 2
            zoneValues = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            arcpy.AddMessage("Calculate Stream Order - Expand Strahler to 2x2 neighbors")
            # Execute Expand
            outExpand = Expand(pStrOrder, numberCells, zoneValues)

            # Save the output
            outExpand.save(pStrExp)


            arcpy.AddMessage("Reclassify Stream Order to Stream Impedance")
            # Set local variables
            StreamImpd_Layer=arcpy.mapping.Layer(pStrExp)
            arcpy.mapping.AddLayer(df,StreamImpd_Layer,"BOTTOM")
            # Execute Reclassify
            ##May 07, 2013#########################
            outRaster = ReclassByTable(pStrExp, inRemapTable,"ORDER_","ORDER_","IMPEDANCE","NODATA")
            ##May 07, 2013#########################


            # Save the output
            outRaster.save(pStream_Impd)
            del outRaster

            arcpy.Delete_management(wrkspc + '\\' + pStrFill)
            arcpy.Delete_management(wrkspc + '\\' + pOutFlow)
            arcpy.Delete_management(wrkspc + '\\' + pFlowAcc)
            arcpy.Delete_management(wrkspc + '\\' + pStrAcc)
            arcpy.Delete_management(wrkspc + '\\' + pStrOrder)
            arcpy.Delete_management(wrkspc + '\\' + pStrExp)

        else:
            outDivide = Raster(pStrImpd)*75.0
            outDivide.save(pStream_Impd)
            del outDivide

        arcpy.Delete_management(wrkspc + '\\' + pStreams_Clipped)
        arcpy.Delete_management(wrkspc + '\\' + pStreams_Buf)
        arcpy.Delete_management(wrkspc + '\\' + pStrImpd)

except:
    arcpy.AddMessage("No Streams Layer")
    arcpy.CopyRaster_management(ImpdConst,pStream_Impd)

pStreamsImpd_Layer=arcpy.mapping.Layer(pStream_Impd)
arcpy.mapping.AddLayer(df,pStreamsImpd_Layer,"BOTTOM")


try:
    if gp.GetCount_management(Water) == 0:
        arcpy.AddMessage("No Water Polygons")
        arcpy.CopyRaster_management(ImpdConst,Water_Impd)


    else:
        # Water Processing
        # Process: Clip Water
        arcpy.AddMessage("Clip water features")

    ############################################
        arcpy.Clip_analysis(Water, IPP_dist, Water_Clipped, "")

    ############################################

        # Check to see if the water polygon already has a "Impd" field.  If not create one
        WaterImpedance = 99
        if len(arcpy.ListFields(Water_Clipped,"Impedance")) > 0:
            arcpy.CalculateField_management(Water_Clipped,"Impedance",WaterImpedance)
        else:
            # Add the new field and calculate the value
            arcpy.AddField_management(Water_Clipped, "Impedance", "SHORT")
            arcpy.CalculateField_management(Water_Clipped,"Impedance",WaterImpedance)

        # Process: Polygon to Raster
        arcpy.AddMessage("create Water Impedance Layer")
        arcpy.FeatureToRaster_conversion(Water_Clipped, "Impedance", Water_Impd, CellSize)
        arcpy.Delete_management(wrkspc + '\\' + Water_Clipped)
except:
    arcpy.AddMessage("No water Layer")
    arcpy.CopyRaster_management(ImpdConst,Water_Impd)

WaterImpd_Layer=arcpy.mapping.Layer(Water_Impd)
arcpy.mapping.AddLayer(df,WaterImpd_Layer,"BOTTOM")

arcpy.RefreshActiveView()
try:
    if gp.GetCount_management(Electric) == 0:
        arcpy.AddMessage("No Utility Lines")
        arcpy.CopyRaster_management(ImpdConst,Utility_Impd)
    else:
        #Utility Line Processing
        # Process: Clip PowerLines
        arcpy.AddMessage("Clip Power Lines and buffer to 15 meters")
        arcpy.Clip_analysis(Electric, IPP_dist, Electric_Clipped, "")
        # Process: Buffer for theoretical search area
        arcpy.Buffer_analysis(Electric_Clipped, Electric_Buf, "15 Meters")

        # Check to see if the Utility polyline already has a "Impd" field.  If not create on
        UtilityImpedance = 30
        if len(arcpy.ListFields(Electric_Buf,"Impedance")) > 0:
            arcpy.CalculateField_management(Electric_Buf,"Impedance",UtilityImpedance)
        else:
            # Add the new field and calculate the value
            arcpy.AddField_management(Electric_Buf, "Impedance", "SHORT")
            arcpy.CalculateField_management(Electric_Buf,"Impedance",UtilityImpedance)

        # Process: Polyline to Raster
        arcpy.AddMessage("create Utility Impedance Layer")
        arcpy.FeatureToRaster_conversion(Electric_Buf, "Impedance", Utility_Impd, CellSize)
        arcpy.Delete_management(wrkspc + '\\' + Electric_Clipped)
        arcpy.Delete_management(wrkspc + '\\' + Electric_Buf)

except:
    arcpy.AddMessage("No utility Layer")
    arcpy.CopyRaster_management(ImpdConst,Utility_Impd)

UtilityImpd_Layer=arcpy.mapping.Layer(Utility_Impd)
arcpy.mapping.AddLayer(df,UtilityImpd_Layer,"BOTTOM")


try:
    if gp.GetCount_management(Fence) == 0:
        arcpy.AddMessage("No Fence lines")
        arcpy.CopyRaster_management(ImpdConst,Fence_Impd)
    else:
        # Fence line processing
        # Process: Clip Fences
        arcpy.AddMessage("Clip Fences and buffer to 10 meters")
        arcpy.Clip_analysis(Fence, IPP_dist, Fence_Clipped, "")
        # Process: Buffer for theoretical search area
        arcpy.Buffer_analysis(Fence_Clipped, Fence_Buf, "10 Meters")

        # Check to see if the Fence polyline already has a "Impd" field.  If not create on
        FenceImpedance = 99
        if len(arcpy.ListFields(Fence_Buf,"Impedance")) > 0:
##            arcpy.CalculateField_management(Fence_Buf,"Impedance",FenceImpedance)
            arcpy.AddMessage("User provider fence impedance")
        else:
            # Add the new field and calculate the value
            arcpy.AddField_management(Fence_Buf, "Impedance", "SHORT")
            arcpy.CalculateField_management(Fence_Buf,"Impedance",FenceImpedance)

        # Process: Polyline to Raster
        arcpy.AddMessage("create Fence Impedance Layer")
        arcpy.FeatureToRaster_conversion(Fence_Buf, "Impedance", Fence_Impd, CellSize)
        arcpy.Delete_management(wrkspc + '\\' + Fence_Clipped)
        arcpy.Delete_management(wrkspc + '\\' + Fence_Buf)
except:
    arcpy.AddMessage("No Fence Layer")
    arcpy.CopyRaster_management(ImpdConst,Fence_Impd)

FenceImpd_Layer=arcpy.mapping.Layer(Fence_Impd)
arcpy.mapping.AddLayer(df,FenceImpd_Layer,"BOTTOM")

arcpy.RefreshActiveView()
try:
    if not NLCD:
        arcpy.AddMessage("No Land Cover Data")
        arcpy.CopyRaster_management(ImpdConst,Veggie_Impd)
    else:
        # Process: Clip Raster NLCD
        arcpy.AddMessage("Clip NLCD")

    ############################################
        arcpy.Clip_management(NLCD, "#", NLCD_Clip, IPP_dist, "", "ClippingGeometry")
    ############################################


        NLCDClip_Layer=arcpy.mapping.Layer(NLCD_Clip)
        arcpy.mapping.AddLayer(df,NLCDClip_Layer,"BOTTOM")

        # Process: Resample
        arcpy.AddMessage("Resample NLCD if needed")

        NLCDCel = arcpy.GetRasterProperties_management(NLCD_Clip,"CELLSIZEX")
        NLCDCell = float(NLCDCel.getOutput(0))
        NLCDCellSize = NLCDCell
        if NLCDCellSize != CellSize:
            arcpy.Resample_management(NLCD_Clip, NLCD_Resample2, CellSize, "NEAREST")
        else:
            NLCD_Resample2 = NLCD_Clip

        NLCDResamp=arcpy.mapping.Layer(NLCD_Resample2)
        arcpy.Delete_management(NLCD_Clip)
        arcpy.mapping.AddLayer(df,NLCDResamp,"BOTTOM")
        # Process: Add Join (3)
        arcpy.AddMessage("Land Cover Impedance - Join Table w/ NLCD")
        arcpy.AddJoin_management(NLCD_Resample2, "VALUE", LandCoverClass, "LCCC", "KEEP_ALL")
        arcpy.AddMessage("Done")
        #####################

        # Process: Lookup
        arcpy.AddMessage("Create Veggie Impedance Layer")
##        arcpy.gp.Lookup_sa(NLCD_Resample2, "LandCover_Class.Snow_Impd", Veggie_Impd)
        arcpy.gp.Lookup_sa(NLCD_Resample2, "LandCover_Class.Walk_Impd", Veggie_Impd)
        arcpy.RemoveJoin_management(NLCD_Resample2)
        arcpy.mapping.RemoveLayer(df,NLCDResamp)

except:
    arcpy.AddMessage("No NLCD Layer")
    arcpy.CopyRaster_management(ImpdConst,Veggie_Impd)

#arcpy.mapping.RemoveLayer(df,NLCDResamp)
VeggieImpd_Layer=arcpy.mapping.Layer(Veggie_Impd)
arcpy.mapping.AddLayer(df,VeggieImpd_Layer,"BOTTOM")


# Process: Raster Calculator (9)
arcpy.Compact_management(wrkspc)
arcpy.AddMessage("Get Impedance layer")
try:
    arcpy.env.extent = "MINOF" #IPP_dist
    outCon = Con(IsNull(Raster(Fence_Impd)),Con(IsNull(Raster(Road_Impd)), Con(IsNull(Raster(Trail_Impd)), \
    Con(IsNull(Raster(High_Slope)), Con(IsNull(Raster(Water_Impd)), Con(IsNull(Raster(pStream_Impd)), \
    Con(IsNull(Raster(Utility_Impd)), Raster(Veggie_Impd), Raster(Utility_Impd)), Raster(pStream_Impd)), \
    Raster(Water_Impd)),Raster(High_Slope)), Raster(Trail_Impd)), Raster(Road_Impd)), Raster(Fence_Impd))

    outCon.save(Impedance)
    del outCon

except:
    arcpy.AddMessage("No Impedance layer")
    pass

###################################
## Add Feb 18, 2014 - Temporary for Search Speed Study -Tobler Hiking Function
arcpy.AddMessage("Tobler Slope Speed")
Div1 = 57.29578
outDivide = Exp(-3.5*Abs(Tan(Raster(Sloper)/Div1)+0.05))*6.0
outDivide.save(Tobler_kph)
del outDivide

arcpy.AddMessage("Traveling Speed - kph")
outDivide = Raster(Tobler_kph)/Exp(0.0212*Float(Raster(Impedance)))
outDivide.save(Tspd_kph)
del outDivide
##############################

fcList=[DEM_Clip,IPP_dist, Water_Impd,pStream_Impd,Trail_Impd,Road_Impd,\
        Utility_Impd,Fence_Impd,Veggie_Impd,High_Slope,ImpdConst,ImpdConstA,\
        Sloper, NLCD_Resample2, NLCD_Clip, Tobler_kph]
fcLayer=["IPPTheoDistance", "DEM_clipped", "High_Slope", "ImpdConst",\
         "Road_Impd", "Trails_Buffered", "Trail_Impd", "Stream_Impd",\
         "Water_Impd", "Utility_Impd", "Fence_Impd", "NLCD_Resample", "NLCD_Impd",\
         "Str_Exp", "NLCD_clipped", "Slope", "Roads_Buffered","Expand_Str_O1"]

for lyr in fcLayer:
    for ii in arcpy.mapping.ListLayers(mxd, lyr):
        try:
            print "Deleting layer", ii
            arcpy.mapping.RemoveLayer(df , ii)
        except:
            pass

for gg in fcList:
    if arcpy.Exists(gg):
        try:
            arcpy.Delete_management(wrkspc + '\\' + gg)
        except:
            pass



