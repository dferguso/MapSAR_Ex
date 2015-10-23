#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Name:        FindLocationModel.py
# Purpose:
#  This tool reclassifies the raster from the US National Land Cover Dataset to
#  correspond with the Find Location classifications as specified in Bob
#  Koester's "Lost Person Behavior" book.  The classifications from LPB are
#  listed below along with the corresponding classifications from the NLCD.</p>
#
#  http://www.mrlc.gov/
#  http://www.dbs-sar.com/LPB/lpb.htm
#
#  NLCD Class                                        Koester Classification
#  11	Open Water                                    Water
#  12	Perennial Ice/Snow                            Fields
#  21	Developed, Open Space                         Fields
#  22	Developed, Low Intensity                      Structures
#  23	Developed, Medium Intensity                   Structures
#  24	Developed, High Intensity                     Structures
#  31	Barren Land (Rock/Sand/Clay)                  Rock
#  32	Unconsolidated Shore                          Water
#  41	Deciduous Forest                              Woods
#  42	Evergreen Forest                              Woods
#  43	Mixed Forest                                  Woods
#  51	Dwarf Scrub                                   Scrub
#  52	Shrub/Scrub                                   Scrub
#  71	Grassland/Herbaceous                          Brush
#  72	Sedge/Herbaceous                              Fields
#  73	Lichens                                       Fields
#  74	Moss                                          Fields
#  81	Pasture/Hay                                   Fields
#  82	Cultivated Crops                              Fields
#  90	Woody Wetlands                                Woods
#  91	Palustrine Forested Wetland                   Woods
#  92	Palustrine Scrub/Shrub Wetland                Woods
#  93	Estuarine Forested Wetland                    Woods
#  94	Estuarine Scrub/Shrub Wetland                 Scrub
#  95	Emergent Herbaceous Wetlands                  Brush
#  96	Palustrine Emergent Wetland (Persistent)      Water
#  97	Estuarine Emergent Wetland                    Water
#  98	Palustrine Aquatic Bed                        Water
#  99	Estuarine Aquatic Bed                         Water

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
import datetime
from arcpy import env
from arcpy.sa import *


########
# Main Program starts here
#######

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

# Set date and time vars
timestamp = ''
now = datetime.datetime.now()
todaydate = now.strftime("%m_%d")
todaytime = now.strftime("%H_%M_%p")
timestamp = '{0}_{1}'.format(todaydate,todaytime)


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

NLCD = arcpy.GetParameterAsText(5)
if NLCD == '#' or not NLCD:
#    NLCD = "NLCD" # provide a default value if unspecified
    NLCD = "empty"

Structures = eval(arcpy.GetParameterAsText(6))  # Get the subject number
if Structures == '#' or not Structures:
    Structures = "0" # provide a default value if unspecified

Rds = eval(arcpy.GetParameterAsText(7))  # Get the subject number
if Rds == '#' or not Rds:
    Rds = "0" # provide a default value if unspecified

Linear = eval(arcpy.GetParameterAsText(8))  # Get the subject number
if Linear == '#' or not Linear:
    Linear = "0" # provide a default value if unspecified

Drain = eval(arcpy.GetParameterAsText(9))  # Get the subject number
if Drain == '#' or not Drain:
    Drain = "0" # provide a default value if unspecified

pWater = eval(arcpy.GetParameterAsText(10))  # Get the subject number
if pWater == '#' or not pWater:
    pWater = "0" # provide a default value if unspecified

Brush = eval(arcpy.GetParameterAsText(11))  # Get the subject number
if Brush == '#' or not Brush:
    Brush = "0" # provide a default value if unspecified

Scrub = eval(arcpy.GetParameterAsText(12))  # Get the subject number
if Scrub == '#' or not Scrub:
    Scrub = "0" # provide a default value if unspecified

Woods = eval(arcpy.GetParameterAsText(13))  # Get the subject number
if Woods == '#' or not Woods:
    Woods = "0" # provide a default value if unspecified

Fields = eval(arcpy.GetParameterAsText(14))  # Get the subject number
if Fields == '#' or not Fields:
    Fields = "0" # provide a default value if unspecified

Rock = eval(arcpy.GetParameterAsText(15))  # Get the subject number
if Rock == '#' or not Rock:
    Rock = "0" # provide a default value if unspecified

Structures = int(Structures*100)
Rds = int(Rds*100)
Linear=int(Linear*100)
Drain=int(Drain*100)
pWater = int(pWater*100)
Brush = int(Brush*100)
Scrub = int(Scrub*100)
Woods = int(Woods*100)
Fields = int(Fields*100)
Rock = int(Rock*100)


# Generate a list of layers in the df
layer_names=[str(f.name) for f in arcpy.mapping.ListLayers(mxd,"",df)]
if "Water_Polygon" in layer_names:
    Water = "Water_Polygon"
elif "WaterBodies" in layer_names:
    Water = "WaterBodies"
Roads = "Roads"
Trails = "Trails"
pStreams = "Streams"
Fence = "FenceLine"
Electric = "PowerLines"

#File Names:
IPP = "Planning Point"
IPP_dist = "IPPTheoDistance"

Roads_Clipped = "Roads_Clipped"
Roads_Buf = "Roads_Buffered"
Road_Find = "Road_Find"

Trails_Clipped = "Trails_Clipped"
Trails_Buf = "Trails_Buffered"
Trail_Find = "Trail_Find"

pStreams_Clipped = "Streams_Clipped"
pStreams_Buf = "Streams_Buffered"
pStreams_Find = "Stream_Find"

Electric_Clipped = "Electric_Clipped"
Electric_Buf = "Electric_Buffered"
Elec_Find = "Elec_Find"

Linear_Find = "LinearFind"

Water_Clipped = "Water_Clipped"
Water_Buf = "Water_Buffered"
Water_Find = "Water_Find"

NLCD_Clip = "NLCD_clipped"
NLCD_Reclass = "NLCD_Reclass"
NLCD_Resample = "NLCD_Resample"
ConstRstr_Temp = "ConstRstr_Temp"
ConstRstr = "ConstRstr"

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
arcpy.AddMessage("Buffer IPP around the " + ippType + "\n")

# Process: Buffer for theoretical search area
arcpy.AddMessage("Buffer IPP")
arcpy.Buffer_analysis(IPP, IPP_dist, TheoSearch)

IPPDist_Layer=arcpy.mapping.Layer(IPP_dist)
arcpy.mapping.AddLayer(df,IPPDist_Layer,"BOTTOM")

spatialRef = arcpy.Describe(IPPDist_Layer).SpatialReference
spn =spatialRef.name
#arcpy.AddMessage(spn)

desc = arcpy.Describe(IPP_dist)
extent = desc.extent
arcpy.env.extent = IPP_dist

arcpy.AddMessage("Get Cellsize \n")

spRefNLCD = arcpy.Describe(NLCD).SpatialReference
spnNLCD =spRefNLCD.name
arcpy.AddMessage("NLCD Spatial Reference is: " + spnNLCD + "\n")


if spnNLCD != spn:
    State1 = "Project NLCD using 'Project Raster tool' with the output coord system:"
    State2 = "Select the appropriate coord transformation for your data and"
    State3 = "use the default Cell Size. Use the projected NLCD for this tool."
    arcpy.AddError(State1)
    arcpy.AddError(spn)
    arcpy.AddError(State2)
    arcpy.AddError(State3)
    sys.exit()

CellSize = 3.0 #XCell
arcpy.AddMessage("Cellsize is " + str(CellSize))

arcpy.AddMessage("Clip NLCD to prescribed distance\n")
########################
arcpy.Clip_management(NLCD, "#", NLCD_Clip, IPP_dist, "", "ClippingGeometry")
arcpy.Resample_management(NLCD_Clip, NLCD_Resample, CellSize, "NEAREST")
##DEM_Clip = DEM2
########################

# Set local variables
arcpy.AddMessage("Reclassify NLCD")
inRaster = NLCD_Resample
reclassField = "VALUE"

remap = RemapValue([[11,pWater],[12,Fields],[21,Fields],\
                    [22,Structures],[23,Structures],[24,(Structures)],\
                    [31,Rock],[32,pWater],[41,Woods],[42,Woods],\
                    [43,Woods],[51,Scrub],[52,Scrub],[71,Brush],[72,Fields],\
                    [73,Fields],[74,Fields],[81,Fields],[82,Fields],\
                    [90,Woods],[91,Woods],[92,Woods],[93,Woods],[94,Scrub],\
                    [95,Brush],[96,pWater],[97,pWater],[98,pWater],[99,pWater]])

# Execute Reclassify
outReclassify = Reclassify(inRaster, reclassField, remap, "NODATA")
# Save the output
outReclassify.save(NLCD_Reclass)


arcpy.Delete_management(wrkspc + '\\' + NLCD_Resample)
arcpy.Delete_management(wrkspc + '\\' + NLCD_Clip)

# Execute CreateConstantRaster
arcpy.AddMessage("Create NULL value raster")
outConstRaster = CreateConstantRaster(0, "INTEGER", CellSize, extent)

# Save the output
outConstRaster.save(ConstRstr_Temp)
arcpy.DefineProjection_management(ConstRstr_Temp, spatialRef)
whereClause = "Value = 0"
outSetNull=SetNull(ConstRstr_Temp, ConstRstr_Temp, whereClause)
outSetNull.save(ConstRstr)

try:
    arcpy.Delete_management(wrkspc + '\\' + ConstRstr_Temp)
except:
    pass

if Rds > 0.0:
    try:
        if gp.GetCount_management(Roads) == 0:
            arcpy.AddMessage("No Roads")
            Road_Find = ConstRstr
        else:
            ##FeatureRst(Roads, Road_Lyr, IPP_dist, Roads_Clipped,Roads_Buf, df, RoadBuf_Layer, CellSize, Rds, Road_Find,wrkspc)
            #Roads Processing
            # Process: Clip Roads
            arcpy.AddMessage("Clip Roads Feature and buffer\n")
            arcpy.Clip_analysis(Roads, IPP_dist, Roads_Clipped, "")
            arcpy.Buffer_analysis(Roads_Clipped, Roads_Buf, "10 Meters")

            # Add field for find feature value

            arcpy.AddField_management(Roads_Buf, "FindFeat", "SHORT", "", "")
            arcpy.CalculateField_management(Roads_Buf, "FindFeat",Rds, "PYTHON")

            # Process: Polyline to Raster (3)
            arcpy.FeatureToRaster_conversion(Roads_Buf, "FindFeat", Road_Find, CellSize)
            arcpy.Delete_management(wrkspc + '\\' + Roads_Buf)
            arcpy.Delete_management(wrkspc + '\\' + Roads_Clipped)

    except:
        arcpy.AddMessage("No Road Layer")
        Road_Find = ConstRstr
else:
    Road_Find = ConstRstr

##RoadFind_Layer=arcpy.mapping.Layer(Road_Find)
##arcpy.mapping.AddLayer(df,RoadFind_Layer,"BOTTOM")


if Linear > 0.0:
    try:
        if gp.GetCount_management(Trails) == 0:
            arcpy.AddMessage("No Trails")
            Trail_Find = ConstRstr
        else:
            ##FeatureRst(Roads, Road_Lyr, IPP_dist, Roads_Clipped,Roads_Buf, df, RoadBuf_Layer, CellSize, Rds, Road_Find,wrkspc)
            # Set local variables
            #Roads Processing
            # Process: Clip Trails
            arcpy.AddMessage("Clip Trails Feature and buffer\n")
            arcpy.Clip_analysis(Trails, IPP_dist, Trails_Clipped, "")
            arcpy.Buffer_analysis(Trails_Clipped, Trails_Buf, "10 Meters")

            # Add field for find feature value
            arcpy.AddField_management(Trails_Buf, "FindFeat", "SHORT", "", "")
            arcpy.CalculateField_management(Trails_Buf, "FindFeat",Linear, "PYTHON")

            # Process: Polyline to Raster (3)
            arcpy.FeatureToRaster_conversion(Trails_Buf, "FindFeat", Trail_Find, CellSize)
            arcpy.Delete_management(wrkspc + '\\' + Trails_Buf)
            arcpy.Delete_management(wrkspc + '\\' + Trails_Clipped)

    except:
        arcpy.AddMessage("No Trail Layer")
        Trail_Find = ConstRstr

##    TrailFind_Layer=arcpy.mapping.Layer(Trail_Find)
##    arcpy.mapping.AddLayer(df,TrailFind_Layer,"BOTTOM")
######################################
##Utility ROW
    try:
        if gp.GetCount_management(Electric) == 0:
            arcpy.AddMessage("No Utility Lines")
            Elec_Find = ConstRstr
        else:
            ##FeatureRst(Roads, Road_Lyr, IPP_dist, Roads_Clipped,Roads_Buf, df, RoadBuf_Layer, CellSize, Rds, Road_Find,wrkspc)
            # Set local variables
            #Roads Processing
            # Process: Clip Trails
            arcpy.AddMessage("Clip Powerline Feature and buffer\n")
            arcpy.Clip_analysis(Electric, IPP_dist, Electric_Clipped, "")
            arcpy.Buffer_analysis(Electric_Clipped, Electric_Buf, "10 Meters")

            arcpy.AddField_management(Electric_Buf, "FindFeat", "SHORT", "", "")
            arcpy.CalculateField_management(Electric_Buf, "FindFeat",Linear, "PYTHON")

            # Process: Polyline to Raster (3)
            arcpy.FeatureToRaster_conversion(Electric_Buf, "FindFeat", Elec_Find, CellSize)
            arcpy.Delete_management(wrkspc + '\\' + Electric_Buf)
            arcpy.Delete_management(wrkspc + '\\' + Electric_Clipped)

    except:
        arcpy.AddMessage("No Utilities Layer")
        Elec_Find = ConstRstr

##    ElecFind_Layer=arcpy.mapping.Layer(Elec_Find)
##    arcpy.mapping.AddLayer(df,ElecFind_Layer,"BOTTOM")

    outCon = Con(IsNull(Raster(Trail_Find)),Raster(Elec_Find), Raster(Trail_Find))

    outCon.save(Linear_Find)

    del outCon

else:
    Linear_Find = ConstRstr

##LinearFind_Layer=arcpy.mapping.Layer(Linear_Find)
##arcpy.mapping.AddLayer(df,LinearFind_Layer,"BOTTOM")

if Drain > 0.0:
    try:
        if gp.GetCount_management(pStreams) == 0:
            arcpy.AddMessage("No Streams")
            pStreams_Find = ConstRstr
        else:
            ##FeatureRst(Roads, Road_Lyr, IPP_dist, Roads_Clipped,Roads_Buf, df, RoadBuf_Layer, CellSize, Rds, Road_Find,wrkspc)
            # Process: Clip
            arcpy.AddMessage("Clip Drainage Feature and buffer\n")
            arcpy.Clip_analysis(pStreams, IPP_dist, pStreams_Clipped, "")
            arcpy.Buffer_analysis(pStreams_Clipped, pStreams_Buf, "10 Meters")

            # Add field for find feature value

            arcpy.AddField_management(pStreams_Buf, "FindFeat", "SHORT", "", "")
            arcpy.CalculateField_management(pStreams_Buf, "FindFeat",Drain, "PYTHON")

            # Process: Polyline to Raster (3)
            arcpy.FeatureToRaster_conversion(pStreams_Buf, "FindFeat", pStreams_Find, CellSize)
            arcpy.Delete_management(wrkspc + '\\' + pStreams_Buf)
            arcpy.Delete_management(wrkspc + '\\' + pStreams_Clipped)

    except:
        arcpy.AddMessage("No Streams Layer")
        pStreams_Find = ConstRstr
else:
    pStreams_Find = ConstRstr

##pStreamsFind_Layer=arcpy.mapping.Layer(pStreams_Find)
##arcpy.mapping.AddLayer(df,pStreamsFind_Layer,"BOTTOM")

if pWater > 0.0:
    try:
        if gp.GetCount_management(Water) == 0:
            arcpy.AddMessage("No Water Polygons")
            Water_Find = ConstRstr
        else:
            ##FeatureRst(Roads, Road_Lyr, IPP_dist, Roads_Clipped,Roads_Buf, df, RoadBuf_Layer, CellSize, Rds, Road_Find,wrkspc)
            # Process: Clip
            arcpy.AddMessage("Clip Water Feature and buffer \n")
            arcpy.Clip_analysis(Water, IPP_dist, Water_Clipped, "")
            arcpy.Buffer_analysis(Water_Clipped, Water_Buf, "10 Meters")

            # Add field for find feature value

            arcpy.AddField_management(Water_Buf, "FindFeat", "SHORT", "", "")
            arcpy.CalculateField_management(Water_Buf, "FindFeat",pWater, "PYTHON")

            # Process: Polyline to Raster (3)
            arcpy.FeatureToRaster_conversion(Water_Buf, "FindFeat", Water_Find, CellSize)
            arcpy.Delete_management(wrkspc + '\\' + Water_Buf)
            arcpy.Delete_management(wrkspc + '\\' + Water_Clipped)

    except:
        arcpy.AddMessage("No Water Layer")
        Water_Find = ConstRstr
else:
    Water_Find = ConstRstr

WaterFind_Layer=arcpy.mapping.Layer(Water_Find)
arcpy.mapping.AddLayer(df,WaterFind_Layer,"BOTTOM")

##

##
OutRaster = Con(IsNull(Raster(Road_Find)),Con(IsNull(Raster(Linear_Find)), \
    Con(IsNull(Raster(Water_Find)), Con(IsNull(Raster(pStreams_Find)), \
    Raster(NLCD_Reclass),Raster(pStreams_Find)), Raster(Water_Find)), \
    Raster(Linear_Find)), Raster(Road_Find))

FindFeat_Name="FindFeatures_{0}".format(timestamp)

OutRaster.save(FindFeat_Name)

FindLayer=arcpy.mapping.Layer(FindFeat_Name)

#Insert layer into Reference layer Group
arcpy.AddMessage("Add layer to '13 Incident_Analysis\FindFeatures\{0}'".format(FindFeat_Name))
refGroupLayer = arcpy.mapping.ListLayers(mxd,'*FindFeatures*',df)[0]
arcpy.mapping.AddLayerToGroup(df, refGroupLayer, FindLayer,'TOP')


##try:
arcpy.AddField_management(FindFeat_Name, "Area_", "FLOAT")
arcpy.AddField_management(FindFeat_Name, "POA", "FLOAT")
arcpy.AddField_management(FindFeat_Name, "Pden", "FLOAT")
YCell=arcpy.GetRasterProperties_management(FindFeat_Name, "CELLSIZEY")
XCell=arcpy.GetRasterProperties_management(FindFeat_Name, "CELLSIZEX")
metersUnit=arcpy.Describe(FindFeat_Name).spatialReference.metersPerUnit
cellArea=int(YCell[0])*int(XCell[0])*metersUnit
calcArea="!Count!/1000./1000.*" + str(cellArea)
arcpy.CalculateField_management(FindFeat_Name,"POA","!Value!/100.0","PYTHON_9.3")
arcpy.CalculateField_management(FindFeat_Name,"Area_",calcArea,"PYTHON_9.3")
arcpy.CalculateField_management(FindFeat_Name,"Pden","!POA!/!Area_!","PYTHON_9.3")
##except:
##    pass

fcList=[IPP_dist, Water_Find, pStreams_Find, Road_Find, Trail_Find, Elec_Find, ConstRstr, ConstRstr_Temp, Linear_Find, NLCD_Reclass]
fcLayer=["IPPTheoDistance", "SetNull_Cons1", WaterFind_Layer]

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

