'''
Tool Name:  GPX to Features
Source Name: GPXtoFeatures.py
Version: ArcGIS 10.0
Author: Esri (Kevin Hibma, khibma@esri.com)

Required Arguments:
         Input GPX File: path to GPX file
         Output Feature Class: path to featureclass which will be created
         
Description:
         This tool takes a .GPX file (a common output from handheld GPS receivers). The tool will parse all points
         which particpate as either a waypoint (WPT) or inside a track as a track point (TRKPT). The output feature class
         will create fields for the shape, time, and elevation and description.
'''

try:
  from xml.etree import cElementTree as ElementTree
except:
  from xml.etree import ElementTree

import arcpy
import os


def gpxToPoints(gpxfile, outFC):
    '''     Returns the attributes of the XML
    '''

    tree = ElementTree.parse(gpxfile)

    global TOPOGRAFIX_NS
    TOPOGRAFIX_NS = ''
    TOPOGRAFIX_NS10 = './/{http://www.topografix.com/GPX/1/0}'
    TOPOGRAFIX_NS11 = './/{http://www.topografix.com/GPX/1/1}'

    badPt = 0

    # Inspection of the GPX file will yield and set the appropraite namespace. If 1.0 or 1.1
    # is not found, empty output will be generated
    #
    for TRKorWPT in ['wpt', 'trk']:
        if tree.findall(TOPOGRAFIX_NS10 + TRKorWPT):
            TOPOGRAFIX_NS = TOPOGRAFIX_NS10
        elif tree.findall(TOPOGRAFIX_NS11 + TRKorWPT):
            TOPOGRAFIX_NS = TOPOGRAFIX_NS11


    if TOPOGRAFIX_NS == '':
            arcpy.AddError("Does not appear to be a valid GPX file")
            
            
    # Create the output feature class in WGS84
    #
    arcpy.CreateFeatureclass_management(os.path.dirname(outFC), os.path.basename(outFC), 'POINT', '', 'DISABLED', 'ENABLED', 4326)

    fieldList = [['Name', 'TEXT'],['Descript', 'TEXT'],['Type', 'TEXT'],['Date_Time', 'TEXT'],
                     ['Elevation', 'DOUBLE']]
    
    for props in fieldList:
      arcpy.AddField_management(outFC,  *props)
      
      
    rows = arcpy.InsertCursor(outFC)
    
    recComplete = 0

    for index, trkPoint in enumerate(GeneratePointFromXML(tree)):
      
      if trkPoint.asPoint() is not None:
        row = rows.newRow()
        row.NAME = trkPoint.name
        row.Descript = trkPoint.desc
        row.TYPE = trkPoint.gpxtype
        row.SHAPE = arcpy.Point(float(trkPoint.x), float(trkPoint.y), float(trkPoint.z))
        row.Elevation = trkPoint.z
        row.Date_Time = trkPoint.t
        
        rows.insertRow(row)
        
        recComplete += 1

        if (recComplete % 2000) == 0:
          arcpy.AddMessage("Processed %s records" %recComplete)
      
      else:
        badPt +=1

    if badPt > 0:
        arcpy.AddWarning("%s point(s) could not be created - they probably have a bad XY" %badPt)
      

class classGPXPoint(object):
    ''' Object to gather GPX information '''

    name = ''
    desc = ''
    gpxtype = 'WPT'
    x = None
    y = None
    z = 0
    t = ''


    def __init__(self, node, gpxtype, name, desc):
        self.name = name
        self.desc = desc
        self.gpxtype = gpxtype
        self.y = node.attrib.get('lat')
        self.x = node.attrib.get('lon')
        self.z = node.find(TOPOGRAFIX_NS + 'ele').text if node.find(TOPOGRAFIX_NS + 'ele') is not None else 0
        self.t = node.find(TOPOGRAFIX_NS + 'time').text if node.find(TOPOGRAFIX_NS + 'time') is not None else ''


    def asPoint(self):
        ''' Try to float X/Y. If conversion to a float fails, the X/Y is not valid and return NONE. '''

        try:
            float(self.x)
            float(self.y)   #float(self.z)
            return self.x, self.y, self.z

        except:
            return None


def GeneratePointFromXML(tree):
    ''' 1) Inspect the tree for either TRK or WPT
           TRK's have a sub node of TRKPT which are examined.
        2) Yield the information back to insertcursor from the classGPXPoint object.    '''

    def _getNameDesc(node):
        name = node.find(TOPOGRAFIX_NS + 'name').text if node.find(TOPOGRAFIX_NS + 'name') is not None else ''
        desc = node.find(TOPOGRAFIX_NS + 'desc').text if node.find(TOPOGRAFIX_NS + 'desc') is not None else ''
        return name, desc

    for node in tree.findall(TOPOGRAFIX_NS + 'trk'):
        name, desc = _getNameDesc(node)
        for node in node.findall(TOPOGRAFIX_NS + 'trkpt') :
            yield (classGPXPoint(node, 'TRKPT', name, desc))

    for node in tree.findall(TOPOGRAFIX_NS + 'wpt'):
        name, desc = _getNameDesc(node)
        yield classGPXPoint(node, 'WPT', name, desc)
        
        

if __name__ == "__main__":
    ''' Gather tool inputs and pass them to gpxToPoints(file, outputFC) '''

    gpx = arcpy.GetParameterAsText(0)
    outFC = arcpy.GetParameterAsText(1)
    gpxToPoints(gpx, outFC)        


