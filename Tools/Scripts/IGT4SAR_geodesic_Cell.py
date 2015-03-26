#-------------------------------------------------------------------------------
# Name:        IGT4SAR_Geodesic_Cell.py
# Purpose:     Script usess the Vincenty's formulae to create polygons representing
#              geodesic sectors on the Earth surface.  These pie sectors could
#              represent cellphone signal transmitted from a point source or
#              some for of dispersion angle from a point source.
#
#              http://en.wikipedia.org/wiki/Vincenty's_formulae
#
# Author:      Don Ferguson
#
# Created:     22/07/2014
# Copyright:   (c) ferguson 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import math, arcpy, sys, arcgisscripting
from arcpy import env
import os

# Create the Geoprocessor objects
gp = arcgisscripting.create()

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

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

def Geodesic(pnt, in_bearing, in_angle, in_dist):
    LongDD = pnt.X
    LatDD = pnt.Y

    long2DD = [LongDD]
    lat2DD = [LatDD]
    coordList =[]

    # Parameters from WGS-84 ellipsiod
    aa = 6378137.0
    bb = 6356752.3142
    ff = 1 / 298.257223563
    radius = 6372.8

    LatR = LatDD * math.pi / 180.0
    LongR = LongDD * math.pi / 180.0

    if abs(in_angle % 2.0) > 0.0:
        in_angle += 1

    strAng = int(in_bearing - in_angle/2.0)
    endAng = int(in_bearing + in_angle/2.0)

    # Vincenty's formulae
    for brng in range(strAng,endAng):
        alpha1 = brng * math.pi / 180.0  #brng.toRad();
        sinAlpha1 = math.sin(alpha1)
        cosAlpha1 = math.cos(alpha1)
        tanU1 = (1.0 - ff) * math.tan(LatR)
        cosU1 = 1.0 / math.sqrt((1.0 + tanU1**2.0))
        sinU1 = tanU1 * cosU1

        sigma1 = math.atan2(tanU1, cosAlpha1)
        sinAlpha = cosU1 * sinAlpha1
        cosSqAlpha = 1.0 - sinAlpha**2.0

        uSq = cosSqAlpha * (aa**2.0 - bb**2.0) / (bb**2.0)

        AAA = 1.0 + uSq / 16384.0 * (4096.0 + uSq * (-768.0 + uSq * (320.0 - 175.0 * uSq)))
        BBB = uSq / 1024.0 * (256.0 + uSq * (-128.0 + uSq * (74.0- 47.0 * uSq)))

        sigma = in_dist / (bb * aa)
        sigmaP = 2.0 * math.pi
        while (abs(sigma - sigmaP) > 0.000000000001):
            cos2SigmaM = math.cos(2.0 * sigma1 + sigma)
            sinSigma = math.sin(sigma)
            cosSigma = math.cos(sigma)
            deltaSigma = BBB * sinSigma * (cos2SigmaM + BBB / 4.0 * (cosSigma * (-1.0 + 2.0 * cos2SigmaM**2.0) -
                BBB / 6.0 * cos2SigmaM * (-3.0 + 4.0 * sinSigma**2.0) * (-3.0 + 4.0* cos2SigmaM**2.0)))
            sigmaP = sigma

            sigma = in_dist / (bb * AAA) + deltaSigma

        tmp = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1

        lat2 = math.atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1,(1.0 - ff) * math.sqrt(sinAlpha**2.0 + tmp**2.0))
        lamb = math.atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1)
        CC = ff / 16.0 * cosSqAlpha * (4.0 + ff * (4.0 - 3.0 * cosSqAlpha))
        LL = lamb - (1.0 - CC) * ff * sinAlpha * (sigma + CC * sinSigma * (cos2SigmaM + CC * cosSigma * (-1.0 + 2.0 * cos2SigmaM**2)))
        lon2 = (LongR + LL + 3.0 * math.pi) - (2.0 * math.pi) - math.pi  # normalise to -180...+180

        long2DD.append(lon2 * 180.0 / math.pi)
        lat2DD.append(lat2 * 180.0 / math.pi)

    long2DD.append(LongDD)
    lat2DD.append(LatDD)

    # A list of features and coordinate pairs
    for xi in range(len(lat2DD)):
        coordList.append([long2DD[xi],lat2DD[xi]])

    return coordList

def Geodesic_Main(in_fc, out_fc, in_bearing, in_angle, in_dist, wrkspc, UncertBuff, out_fcUNC):
    inDataset = os.path.join(wrkspc,"Sector")
    inDatasetUNC = os.path.join(wrkspc,"Uncert")
    out_Line=out_fc+'UNC_Temp'
    # Use Describe to get a SpatialReference object
    desc = arcpy.Describe(in_fc)
    shapefieldname = desc.ShapeFieldName
    outCS = desc.SpatialReference

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    # Execute CreateFeatureclass

    coordList = []
    k=0
    rows = arcpy.SearchCursor(in_fc, '', unProjCoordSys)

    for row in rows:
        feat = row.getValue(shapefieldname)
        pnt = feat.getPart()
        k+=1
    ###################################################
        # A list of features and coordinate pairs
        pnt.X=pnt.X
        pnt.Y=pnt.Y
        coordList1 = Geodesic(pnt, float(in_bearing), float(in_angle), float(in_dist))
        coordList.append(coordList1)

    del row
    del rows
    # Create empty Point and Array objects
    #
    array = arcpy.Array()

    # A list that will hold each of the Polygon objects
    #
    featureList = []
    featureListUNC=[]

    for feature in coordList:
        for coordPair in feature:
            # For each coordinate pair, set the x,y properties and add to the
            #  Array object.
            #
            point = arcpy.Point(float(coordPair[0]),float(coordPair[1]))

            array.add(point)
        ######################################################
        # Create a Polygon object based on the array of points
        #
        polygon = arcpy.Polygon(array, unProjCoordSys)
        # Clear the array for future use
        #
        array.removeAll()

        # Append to the list of Polygon objects
        #
        featureList.append(polygon)

        if len(UncertBuff)>0:
            for coordPair in feature[1:-1]:
                point = arcpy.Point(float(coordPair[0]),float(coordPair[1]))
                array.add(point)
            polyline=arcpy.Polyline(array,unProjCoordSys)
            array.removeAll()
            featureListUNC.append(polyline)

    # Create a copy of the Polygon objects, by using featureList as input to
    #  the CopyFeatures tool.
    #
    arcpy.CopyFeatures_management(featureList, inDataset)
    arcpy.Project_management(inDataset, out_fc, outCS)
    arcpy.Delete_management(inDataset)

    if len(featureListUNC)>0:
        arcpy.CopyFeatures_management(featureListUNC, inDatasetUNC)
        arcpy.Project_management(inDatasetUNC, out_Line, outCS)

        # Buffer areas of impact around major roads
        arcpy.AddMessage("Create Uncertainty Buffer")
        if str(arcpy.ProductInfo()) == ("ArcInfo"):
            arcpy.Buffer_analysis(out_Line, out_fcUNC, UncertBuff, "FULL", "FLAT")
        else:
            arcpy.Buffer_analysis(out_Line, out_fcUNC, UncertBuff)

        arcpy.Delete_management(inDatasetUNC)
        arcpy.Delete_management(wrkspc + '\\' + out_Line)
        del featureListUNC

    del coordList
    del polygon
    del featureList
    del feature


########
# Main Program starts here
#######
if __name__ == '__main__':

    mxd, df = getDataframe()

    #in_fc  - this is a point feature used to get the latitude and longitude of point.
    in_fc = arcpy.GetParameterAsText(0)
    if in_fc == '#' or not in_fc:
        arcpy.AddMessage("You need to provide a valid in_fc")

    #out_fc - this will be the output feature for the sector.  May allow user to decide name or I may specify.
    out_fc = arcpy.GetParameterAsText(1)
    if out_fc == '#' or not out_fc:
        arcpy.AddMessage("You need to provide a valid out_fc")

    in_bearing = arcpy.GetParameterAsText(2)
    if in_bearing == '#' or not in_bearing:
        in_bearing = "empty"

    in_angle = arcpy.GetParameterAsText(3)
    if in_angle == '#' or not in_angle:
        in_angle = "empty"

    in_dist = arcpy.GetParameterAsText(4)
    if in_dist == '#' or not in_dist:
        in_dist = "empty"

    UncertBuff=""
    out_fcUNC =""
    Geodesic_Main(in_fc, out_fc, float(in_bearing), float(in_angle), float(in_dist), wrkspc,UncertBuff, out_fcUNC)

