#-------------------------------------------------------------------------------
# Name:        OSMDownloader
# Purpose:
#
# Author:      ferguson
#
# Created:     11/08/2015
# Copyright:   (c) ferguson 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from urllib import urlopen
workspace = "D:\\GeoData\\OSMdev\\"

def main():
    # Make data queries to jXAPI
    print('\nopen url')
    #motorway|motorway_link|trunk|
    marketsXml = urlopen("http://overpass.osm.rambler.ru/cgi/xapi_meta?*"
                         "[highway=motorway|motorway_link|trunk|primary|secondary|tertiary|residential|unclassified|"
                         "service|road|living_street|pedestrian|track|bus_guideway]"
                         "[bbox=-79.85,39.62,-79.79,39.68]").read()
    #marketsXml = urlopen("http://www.overpass-api.de/api/xapi_meta?*%5Bhighway=footway%5D%5Bbbox=-79.84,39.62,-79.79,39.65%5D").read()

    # Make farmers markets file
    print('\nWrite file')
    marketsPath = workspace + "roads.osm"
    marketsFile = open(marketsPath, 'w')
    marketsFile.write(marketsXml)
    marketsFile.close()

if __name__ == '__main__':
    main()
