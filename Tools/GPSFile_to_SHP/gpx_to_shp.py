#################################################################
# Author: Anna Klimaszewski-Patterson
# Date: 08 February 2010
# Purpose: Convert gpx file to a shapefile with feature name and description as
#          attributes
# -- tested on GPX files created by Android apps "Maverick", "OruxMaps", and
#    "MyTracks"
#################################################################

import arcgisscripting, sys, re, gpsFiles as gps

try:    
#################################################################
# Function definitions
#################################################################

    #################################################################
    # Function: handleData
    # Parameters: featureType (what type of data to extract)
    #             xml (XML object)
    # Purpose: handle the data by directing the processing to the
    #          correct handler (point,polyline,polygon)
    # Returns: array
    #################################################################
    def handleData(featureType, xml):
        global gp
        aData = []
        numFeatures = 0

        if featureType == "POINT":
            aData = handleWaypoints(xml)
        elif featureType == "POLYLINE":
            aData = handleTracks(xml)
            
        if list(aData):
            numFeatures = len(aData)

        gp.AddMessage("%s %s features aquired" % (numFeatures, featureType))

        if numFeatures < 1:
            gp.AddMessage("Not found. Aborting...")
            sys.exit(1)

        return aData
    
    #################################################################
    # Function: getCoords
    # Parameters: point (ex: longitude,latitude)
    # Purpose: extract the coordinate data and return as array
    # Returns: array
    #################################################################
    def getCoords(point):
        return [float(point.get('lat')),float(point.get('lon'))]

    ##------------------ Waypoint processing ----------------------##

    #################################################################
    # Function: handleWaypoints
    # Parameters: xml (XML Element object)
    # Purpose: find waypoints and return data
    # Returns: array
    #################################################################
    def handleWaypoints(xml):
        aData = []
        points = xml.findall("wpt")

        for point in points:
            name = point.findtext("name", '')
            desc = point.findtext("desc", '')
            coords = getCoords(point)            
            aData.append([name, desc, '', coords])
        return aData
    
    ##------------------- Track processing -----------------------##
    
    #################################################################
    # Function: handleTracks
    # Parameters: xml (XML object)
    # Purpose: Find tracks and return the data
    # Returns: array
    #################################################################
    def handleTracks(xml):
        aCoord = []
        aData  = []
        all = xml.findall('trk')

        for main in all:
            name = main.findtext("name", '')
            desc = main.findtext("desc", '')

            # process track segments
            seg = main.findall('trkseg')
            for line in seg:
                aCoord = handleTrack(line)
            aData.append([name, desc, '', aCoord])
        return aData

    #################################################################
    # Function: handleTrack
    # Parameters: xml (XML object)
    # Purpose: Find an individual track and process. Called by
    #          handleTracks()
    # Returns: array
    #################################################################
    def handleTrack(line):
        aCoords = []
        points = line.findall('trkpt')
        for point in points:
            aCoords.append(getCoords(point))
        return aCoords
            

#################################################################
# Guts
#################################################################
    # create geoprocessor...
    gp = arcgisscripting.create()
    gp.OverwriteOutput = 1

    # script parameters...
    inFilename  = sys.argv[1]         # input file
    outFilename = sys.argv[3]         # output file
    featureType = sys.argv[2].upper() # POLYGON, POLYLINE, POINT

    # test validity of output filename (no special characters)
    gps.checkFilenameValid(outFilename, gp)

    # if validated, proceed                      
    gp.AddMessage("Retrieving %s data from GPX file..." % featureType)

    # get cleaned data as an XML Element
    xml = gps.getData(inFilename)
    
    # process data
    aData = handleData(featureType, xml)

    ##--------------------- Create Shapefile ------------------------##
    gp.AddMessage("Generating shapefile...")
    
    gps.createShapefile(gp, aData, sys.argv)
    gp.AddMessage("Conversion complete")

except:
    gps.handleException(sys, gp)
