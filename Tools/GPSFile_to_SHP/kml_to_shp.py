#################################################################
# Author: Anna Klimaszewski-Patterson
# Date: 08 February 2010
# Purpose: Convert kml file to a shapefile with feature name and description as
#          attributes
# -- tested on KML files created by Android apps "Maverick", "OruxMaps", and
#    "MyTracks", and Google's KML sample
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
            aData = handleTracks('LineString', xml)
        elif featureType == "POLYGON":
            aData = handleTracks('Polygon', xml)

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
        global gp
        tmp = point.split(',') #typically longitude,latitude,elevation
        if tmp[0]:
            return [float(tmp[1]),float(tmp[0])]
        else:
            return

    ##------------------ Waypoint processing ----------------------##

    #################################################################
    # Function: handleWaypoints
    # Parameters: xml (XML Element object)
    # Purpose: find waypoints and return data
    # Returns: array
    #################################################################
    def handleWaypoints(xml):
        global gp
        aData = []
        folderName = ''

        main = xml.find("Document")
        if not main:
            tmp  = xml.find("Folder")
            main = tmp.find("Document")
            
        folder = main.find('Folder')
        waypoints = main.find('Placemark')

        if folder:
            # if folder exists, get the name for it
            subfolder = folder.find('Folder')
            if subfolder:
                folderName = subfolder.findtext('name', '')
                points     = subfolder.findall('Placemark')
            else:
                folderName = folder.findtext('name', '')
                points = folder.findall('Placemark')
        elif waypoints:
            # get the waypoints directly under Documents
            points = main.findall('Placemark')
        else:
            # catch all, get waypoints from anywhere
            points = main.getiterator('Placemark')

        # process Waypoints
        for point in points:
            name   = point.findtext("name", '')
            desc   = point.findtext("description", '')
            pt     = point.find("Point")
            if not pt:
                continue
            
            coords = pt.findtext("coordinates", '')
            if not coords:
                continue
            coords = getCoords(coords)
            aData.append([name, desc, folderName, coords])
        return aData
    
    ##------------------- Track processing -----------------------##
    
    #################################################################
    # Function: handleTracks
    # Parameters: trackType - 'LineString' or 'Polygon'
    #             xml (XML object)
    # Purpose: Find tracks and return the data
    # Returns: array
    #################################################################
    def handleTracks(trackType, xml):
        global gp
        
        # check to see if there's a folder name
        # can't access parent(s) directly, so iterate from higher up
        folder = xml.getiterator('Folder')
        if folder:
            for item in folder:
                tmps = item.findall('Placemark')
                if tmps:
                    for tmp in tmps:
                        folderName = item.findtext('name', '')
                        # process any tracks
                        aData = handleTrack(trackType, xml, folderName)
                    if aData:
                        return aData
            return
        else:
            # process any tracks
            return handleTrack(trackType, xml)
        
        return
        
    #################################################################
    # Function: handleTrack
    # Parameters: trackType - 'LineString' or 'Polygon'
    #             xml (XML object)
    #             folder (optional) - folder name
    # Purpose: Find an individual track and process. Called by
    #          handleTracks()
    # Returns: array
    #################################################################
    def handleTrack(trackType, xml, folder=''):
        aCoord = []
        aData = []
        global gp
        waypoints = xml.getiterator('Placemark')
        if waypoints[0]:
            # loop through Placemarks until a LineString is found
            for waypoint in waypoints:
                name   = waypoint.findtext("name", '')
                desc   = waypoint.findtext("description", '')
                lineStrings = waypoint.getiterator(trackType)

                if list(lineStrings):
                    for line in lineStrings:
                        # process any line segments
                        aCoord = handleTrackPoints(line)
                        aData.append([name, desc, folder, aCoord])
            return aData
        else:
            return
        
    #################################################################
    # Function: handleTrackPoints
    # Parameters: line (XML object)
    # Purpose: extract the coordinate data from the track and return
    # Returns: array
    #################################################################
    def handleTrackPoints(line):
        aCoords = []
        points = line.getiterator('coordinates')
        points = points[0].text.strip()
        if not points:
            return
        
        points = re.sub("\n", ' ', points)
        aCoordLine = points.split(" ")
        
        for coords in aCoordLine:
            #get the coordinates for the line vertices
            tmp = getCoords(coords)
            if tmp:
                aCoords.append(tmp)
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
    gp.AddMessage("Retrieving %s data from KML file..." % featureType)

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
