#-------------------------------------------------------------------------------
# Name:        IGT4SAR_MapBook.py
# Purpose:     Create Task Assignment Forms from selected rows in the
#              Assignments data layer.  New TAFs are stored by Task ID in the
#              Assignments folder
#
# Author:      Don Ferguson
#
# Created:     02/15/2015
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
import geomag
from types import *

# Environment variables
wrkspc=arcpy.env.workspace
arcpy.env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"


def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def checkNoneType(variable):
    if type(variable) is NoneType:
        result = ""
    else:
        result = variable
    return result

def checkFields(fc, fldName, fldType):
    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    if fldName not in field_names:
        arcpy.AddField_management (fc, fldName, fldType)
    return

def gNorth_Check(fc, fldName, fldType,unProjCoordSys):

    checkFields(fc, fldName, fldType)
    arcpy.CalculateGridConvergenceAngle_cartography(fc,fldName, "GEOGRAPHIC")

    rows0 = arcpy.SearchCursor(fc, '', unProjCoordSys)
    k = 0.0
    gridNorth = 0.0
    for row0 in rows0:
        gridN = row0.getValue(fld_gNorth)
        arcpy.AddMessage('Grid North: {0}'.format(gridN))
        gridNorth += float(gridN)
        k+=1.0

    gridN = round((gridNorth / k),2)
    del row0
    del rows0
    del k
    # Remove field
    dropField=[fld_gNorth]
    arcpy.DeleteField_management(fc, dropField)

    if gridN > 0:
        gCard ="W"
    else:
        gCard ="E"
    return(str(abs(gridN)) + " " + gCard)

def MagDeclin(gLat, gLong):
    declin = geomag.declination(gLat,gLong)
    MagDeclinlination = round(declin,2)
    if MagDeclinlination < 0:
        Cardinal ="W"
    else:
        Cardinal ="E"
    MagDecTxt = str(abs(MagDeclinlination)) + " " + Cardinal
    return(MagDecTxt)


def GetXY(inputFC, poly_Height, poly_Width, lenConv, sCale, nCol, nRow):
    desc = arcpy.Describe(inputFC)
    shpType = desc.shapeType  ## Determine if the input Feature is Polygon, Polyline or Point
    shapefieldname = desc.ShapeFieldName
    nAme=desc.name

    centreX = []
    centreY = []
    cursor = arcpy.SearchCursor(inputFC)
    for row in cursor:
        feat = row.getValue(shapefieldname)
        if shpType.upper()=='POINT':
            centroid = feat.getPart()
        elif (shpType.upper() =="POLYGON") or (shpType.upper() == "POLYLINE"):
            centroid = feat.trueCentroid
        centreX.append(centroid.X)
        centreY.append(centroid.Y)

    meanX = int(float(sum(centreX))/len(centreX)) if len(centreX) > 0 else float('nan')
    meanY = int(float(sum(centreY))/len(centreY)) if len(centreY) > 0 else float('nan')

    arcpy.AddMessage("Check: {0}".format(str(sCale/lenConv*nRow/2.0)))


    xMin = meanX - (poly_Width/lenConv)*sCale*nCol/2.0
    yMin = meanY - (poly_Height/lenConv)*sCale*nRow/2.0

    return(xMin, yMin)

def CreatingMap(fcOut, gRids, mxd, df, mapScale, output):
    ## Get a list of PageNames
    try:
        PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
        PlanNum.text = " "
    except:
        pass
    try:
        AssignNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
        AssignNum.text = " "
    except:
        pass
    try:
        MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
    except:
        pass

    mkLyr=arcpy.mapping.ListLayers(mxd, fcOut,df)[0]
    for llyr in arcpy.mapping.ListLayers(mxd, "*",df):
            if str(llyr.name) == "MRGS_UTM_USNG":
                mapLyr=arcpy.mapping.ListLayers(mxd, "MRGS_UTM_USNG",df)[0]
            elif str(llyr.name) == "MRGSZones_World":
                mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]


    for key in gRids:
        where4 = ('"PageName" = ' + "'" + key + "'")
        arcpy.AddMessage("{0}, MagDec = {1}".format(where4, gRids[key][2]))
        arcpy.SelectLayerByAttribute_management (mkLyr, "NEW_SELECTION", where4)
        df.zoomToSelectedFeatures()
        try:
            arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT",mkLyr)

            rows7=arcpy.SearchCursor(mapLyr)
            row7 = rows7.next()
            try:
                UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
            UTMZn.text = row7.getValue("GRID1MIL")
            except:
                pass
            try:
                USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
            UtmZone=UTMZn.text
            USNGZn.text = row7.getValue("GRID100K")
            UsngGrid = USNGZn.text
        except:
                pass
        except:
            pass

        MapName.text = key
        try:
            MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
        MagDeclin.text = gRids[key][2]
        except:
            pass

            ##arcpy.AddMessage("UTM Zone is " + UTMZn.text + " and USNG Grid is " + USNGZn.text)

        arcpy.SelectLayerByAttribute_management (mapLyr, "CLEAR_SELECTION")


        arcpy.SelectLayerByAttribute_management (mkLyr, "CLEAR_SELECTION")

        mxd.activeView='PAGE_LAYOUT'

        if mapScale > 0:
            pScaler = mapScale
            df.scale = pScaler*1.0
        else:
            df.scale = 24000.0
        mkLyr.visible = False
        arcpy.RefreshActiveView()
        outFile = output + "/" + str(key) + "_MAP.pdf"
        mkLyr.visible = True


        try:
            arcpy.mapping.ExportToPDF(mxd, outFile)
        except:
            arcpy.AddWarning("  ")
            arcpy.AddWarning("Unable to produce map for Assignment: " + str(key))
            arcpy.AddWarning("Problem with ExportToPDF")
            arcpy.AddWarning("  ")

    arcpy.SelectLayerByAttribute_management (mkLyr, "CLEAR_SELECTION")
    return



if __name__ == '__main__':
    #######
    #Automate map production - July 27, 2012
    mxd, df = getDataframe()

    ## Input parameters
    ## inputFC - This is the feature you wish to build the mapbook around.  Preferrably this could be the PLS or LKP.  If the desired feature class contains mulitple features than you must
    ##           select a single feature otherwise mapbooks will be created around each feature.  Can be points, lines, polygons, or rasters.
    ## sCale = Scale must be specified in real world inches (e.g 24000 for 1:24000)
    ##
    ## nRow = Number of rows to create in the y direction from the point of origin.
    ## nCol = Number of columns to create in the x direction from the point of origin.
    ##

    inputFC = arcpy.GetParameterAsText(0)
    sCale = float(arcpy.GetParameterAsText(1))
    nRow = float(arcpy.GetParameterAsText(2))
    nCol = float(arcpy.GetParameterAsText(3))
    output = arcpy.GetParameterAsText(4)
    output = output.replace("'\'","/")

    ## First we need to build the grid
    dfSpatial_Type = df.spatialReference.type
    if dfSpatial_Type.upper() != 'PROJECTED':
        arcpy.AddError('Must have a projected coordinate system')
        sys.exit(1)

    ## Check to see if the layer exists...if so delete it


    poly_Width= df.elementWidth
    poly_Height = df.elementHeight

    mapUnits = df.mapUnits
    lenConv=1.0
    if mapUnits == 'Meters':
        lenConv = 39.37  #inches to meters
    elif mapUnits == 'Feet':
        lenConv = 12.0  #inches to feet
    elif mapUnits == 'Inches':
        lenConv = 1.0  #inches to inches
    else:
        sys.exit(0)


    xMin, yMin = GetXY(inputFC, poly_Height, poly_Width, lenConv, int(sCale), nCol, nRow)

    originCoord = "{0} {1}".format(str(xMin), str(yMin))
    arcpy.AddMessage("SW coordinates are: {0}".format(originCoord))
    desc=arcpy.Describe(inputFC)
    nAme = desc.name
    fcOut = "GRID_{0}_{1}".format(nAme, str(int(sCale)))

    arcpy.GridIndexFeatures_cartography (fcOut, "", "", "USEPAGEUNIT", sCale, "", "", originCoord, nRow, nCol)

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"

    #First determine the grid north value
    fld_gNorth = "gNORTH"
    field_type = "FLOAT"
    gNorthTxt=gNorth_Check(inputFC, fld_gNorth, field_type, unProjCoordSys)
    try:
        df.rotation = 0.0
        if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth"):
            gridNorth=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth")[0]
            gridNorth.text = gNorthTxt
    except:
        pass

    layerOn=False

    if arcpy.Exists(fcOut):
        arcpy.MakeFeatureLayer_management(fcOut,fcOut)
        mkLyr = arcpy.mapping.Layer(fcOut)
        mkLyr.name=fcOut
        arcpy.mapping.RemoveLayer(df,mkLyr)
        arcpy.mapping.AddLayer(df,mkLyr,"TOP")

        try:
            lyr = arcpy.mapping.ListLayers(mxd, mkLyr.name, df)[0]
            symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\MapBookGrid.lyr"
            refGroupLayerA = "Grids"
            if refGroupLayerA in arcpy.mapping.ListLayers(mxd,"",df)[0].name:
                arcpy.mapping.AddLayerToGroup(df,refGroupLayerA,lyr,'TOP')
            arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
            ext=lyr.getExtent()
            df.extent = ext
            outFile = output + "/" + "MapBookGrid.pdf"
            if lyr.supports("LABELCLASSES"):
                for lblclass in lyr.labelClasses:
                    lblclass.showClassLabels = True
            lblclass.expression = '"%s" & [PageName] & "%s"' % ("<CLR red='255'><FNT size = '16'>", "</FNT></CLR>")
            layerOn=True
            lyr.visible = True
            lyr.showLabels = True
            if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName"):
                MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
                MapName.text = "Mapbook Index"
            arcpy.RefreshActiveView()
            try:
                arcpy.mapping.ExportToPDF(mxd, outFile)
            except:
                pass
            lyr.visible = False
            lyr.showLabels = False
        except:
            pass


    #Get the Lat / Long, magDeclination for each GRID
    desc = arcpy.Describe(fcOut)
    shapefieldname = desc.ShapeFieldName
    gRids={}
    cGrid=arcpy.GetCount_management(fcOut)
    if int(cGrid.getOutput(0)) > 0:
        cursor1 = arcpy.SearchCursor(fcOut, '', unProjCoordSys)
        for row1 in cursor1:
            gName = row1.getValue("PageName")
            feat = row1.getValue(shapefieldname)
            centroid = feat.trueCentroid
            gLat = centroid.Y
            gLong = centroid.X
            magDec = MagDeclin(gLat, gLong)
            gRids[gName]=[gLat, gLong, magDec]
            arcpy.AddMessage("{0}, magDec = {1}".format(gName, magDec))



    ##############################
    # Print Maps for each grid
    ##############################
## Need to do some major re-work.  Need to determine the MagDec and UTM details for each
## grid square within the GRID.  Once the GRID is created, get a list of coordinates for the centroid
## of each grid.  Run the Mag Dec (see IGT4SAR_updateLayout.py) for each and create the following dictionary:
## GRID[PageName]={magDec, UTM Zone, USNG Zone, Incident Name, Incident Number}
## Send this info to module for printing map

    CreatingMap(fcOut, gRids, mxd, df, int(sCale), output)

    try:
        PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
        PlanNum.text = " "
    except:
        pass
    try:
        AssignNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
        AssignNum.text = " "
    except:
        pass
    try:
        MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
        MapName.text=" "
    except:
        pass


    if layerOn==True:
        lyr.visible = True
        lyr.showLabels = True


## Zom to the extent of the Fishnet and create  index map






    ## Print Index map