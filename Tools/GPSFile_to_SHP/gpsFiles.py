import arcgisscripting, re, os, sys, traceback, codecs
from xml.etree.ElementTree import (ElementTree as etree, XML)

#################################################################
# Function: checkFilename
# Parameters: filename
#             gp
# Purpose: Only accept output filenames if there are no special
#          characters.
# Returns: 1 or string
#################################################################
def checkFilenameValid(filename, gp):
    re.UNICODE

    # extract just the filename for validation
    name = filename.split('\\') 
    name = name.pop()

    tmp = re.sub("\.", '', name) #remove the dots to not interfere
    tmp = re.search("\W", tmp)
    if tmp:
        gp.AddMessage("Your output filename " + name +
                      " contains invalid characters. " +
                      "Please remove any spaces, dashes, etc. and try again.")
        sys.exit(1)

#################################################################
# Function: getData
# Parameters: inFilename
# Purpose: load
# Returns: XML Element object
#################################################################
def getData(inFilename):
    # read file into variable
    contents = codecs.open(inFilename, 'rb').read()

    # clean data
    
    # in case XML file has goofy attributes in <kml> or <gpx>
    # (ie: a MyTracks-generated file), clean out any attributes
    # (causes parser to think XML is malformed)
    pattern = r'''<(/*)(gpx|kml)([^>]+)>'''
    replace = r'''<\1\2>'''
    contents = re.sub(pattern, replace, contents)

    # clean any tagnames with : in them (ex: <atom:author>) or parser's
    # unhappy
    pattern = r'''<([^>]+):([^>]+)>'''
    replace = r'''<\1\2>'''
    contents = re.sub(pattern, replace, contents)

    # parse the file into an XML object
    xml = XML(contents)
    
    return xml

#################################################################
# Function: createShapefile
# Parameters: gp (geoprocessing object)
#             aData (array of generated data to add to shapefile)
#             sys (system object, storing program inputs)
# Purpose: create an ArcGIS shapefile from the provided data
# Returns: none
#################################################################
def createShapefile(gp, aData, sys):
    featureType = sys[2]                # POLYGON, POLYLINE, POINT
    outFilename = sys[3]                # output file name
    featureType = featureType.upper()   # convert to uppercase
    numFeatures = len(aData)            # number of features

    # factory code for GCS_WGS_1984...
    spatialRef = "4326"

    # get output file data
    gp.workspace = os.path.dirname(outFilename) + "\\"
    basename = os.path.basename(outFilename)

    # create shapefile output
    gp.CreateFeatureClass_management(gp.workspace, basename, featureType,
                                      "", "", "", spatialRef)

    # add fields
    gp.addfield(outFilename, 'NAME',   'TEXT', '#', '#', 100)
    gp.addfield(outFilename, 'DESCR',  'TEXT', '#', '#', 255)
    gp.addfield(outFilename, 'FOLDER', 'TEXT', '#', '#', 100)

    # instantiate insertion cursor
    cursor = gp.InsertCursor(outFilename)
    
    #loop through each feature
    count = 0
    for item in aData:
        count += 1
        name     = item[0]
        descr    = item[1]
        folder   = item[2]
        aCoords  = item[3]

        if not aCoords:
            gp.AddWarning("Cannot convert %s to shapefile, no coordinates found"
                          % name)
            continue
        
        # create new row in memory
        newRow = cursor.newRow()
        
        # instantiate point object
        oPoint = gp.CreateObject("point")

        if featureType == 'POLYLINE' or featureType == 'POLYGON':
            # instantiate poly object

            feature = gp.CreateObject("array")  #feature array
            part    = gp.CreateObject("array")  #part array
            
            # loop through points
            for pt in aCoords:
                if pt:
                    oPoint.x, oPoint.y = pt[1],pt[0] #assign point to Point obj
                    part.add(oPoint)                 #add point to part array
                else:                                #interior poly||missing pt
                    feature.add(part)
                    part.removeall()

            feature.add(part)
            part.removeall()
            del part

            newRow.Shape = feature
            feature.removeall()

        else:
            oPoint.x, oPoint.y = aCoords[1],aCoords[0]
            newRow.Shape = oPoint

        newRow.NAME     = name
        newRow.DESCR    = descr
        newRow.FOLDER   = folder
        # insert row to shapefile (write)
        cursor.InsertRow(newRow)
        del oPoint

        # if large number of items, give status report every 100 items
        if count % 100 == 0:
            gp.AddMessage("Processed %s of %s features" % (count,numFeatures))

    # clean up
    del cursor, newRow
    
    return

#################################################################
# Function: handleException
# Parameters: sys (system object, storing program inputs)
#             gp (geoprocessing object)
# Purpose: handle program exceptions
# Returns: none
#################################################################
def handleException(sys, gp):
    if not str(sys.exc_value) == str(1):
        trace = traceback.format_tb(sys.exc_info()[2])[0]
        traceMsg = trace + "\n" + str(sys.exc_type) + ': ' + str(sys.exc_value)
        gp.AddError(traceMsg)
        print traceMsg
