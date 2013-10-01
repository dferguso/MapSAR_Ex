#################################################################
# Author: Anna Klimaszewski-Patterson
# Date: 11 April 2010
# Purpose: Convert plt file to a shapefile with feature name and description as
#          attributes
# -- Tested with file format from OziExplorer Waypoint File Version 1.1
# -- Assumes format: ID, OBJECTID, LATITIUDE, LONGITUDE.
# ---- I ignore the rest of the fields
#################################################################

import arcgisscripting, sys, re, codecs, gpsFiles as gps

try:    
#################################################################
# Function definitions
#################################################################

    #################################################################
    # Function: getData
    # Parameters: inFilename
    # Purpose: Parse data into an array
    # Returns: array
    #################################################################
    def getData(inFilename):
        # read file into variable
        contents = codecs.open(inFilename, 'rb').read()
        x = 0
        aCoords = []
        contents = contents.split("\r\n")
        for line in contents:
            if( x < 4):
                x += 1
            else:
                aLine = line.split(',')
                try:
                    aCoords.append([float(aLine[2]), float(aLine[3]), aLine[1]])
                except:
                    #don't really do anyline, new line wasn't truncated
                    y = 1
        gp.AddMessage("aCoords: %s" % aCoords)
        return aCoords

    #################################################################
    # Function: handleData
    # Parameters: featureType (what type of data to extract)
    #             xml (XML object)
    # Purpose: handle the data by directing the processing to the
    #          correct handler (point,polyline,polygon)
    # Returns: array
    #################################################################
    def handleData(featureType, aData):
        global gp
        numFeatures = 0

        aData = handleWaypoints(aData)
            
        if list(aData):
            numFeatures = len(aData)

        gp.AddMessage("%s %s features aquired" % (numFeatures, featureType))

        if numFeatures < 1:
            gp.AddMessage("Not found. Aborting...")
            sys.exit(1)

        return aData
    
    ##------------------ Waypoint processing ----------------------##

    #################################################################
    # Function: handleWaypoints
    # Parameters: array (0= lat, 1= long, 2=id (name))
    # Purpose: find waypoints and return data
    # Returns: array
    #################################################################
    def handleWaypoints(points):
        aData = []
        gp.AddMessage("points: %s" % points)
        for point in points:
#            gp.AddMessage("point: %s" % point)
            name = point[2]
            desc = ''
            coords = [point[0], point[1]]            
            aData.append([name, desc, '', coords])
        return aData
       

#################################################################
# Guts
#################################################################
    # create geoprocessor...
    gp = arcgisscripting.create()
    gp.OverwriteOutput = 1

    # script parameters...
    inFilename  = sys.argv[1]         # input file
    outFilename = sys.argv[2]         # output file
    featureType = 'POINT'
    
    # test validity of output filename (no special characters)
    gps.checkFilenameValid(outFilename, gp)

    # if validated, proceed                      
    gp.AddMessage("Retrieving %s data from WPT file..." % featureType)
    aData = getData(inFilename)
    
    # process data
    aData = handleData(featureType, aData)

    ##--------------------- Create Shapefile ------------------------##
    gp.AddMessage("Generating shapefile...")
    
    gps.createShapefile(gp, aData, sys.argv)
    gp.AddMessage("Conversion complete")

except:
    gps.handleException(sys, gp)
