#-------------------------------------------------------------------------------
# Name:        IGT4SAR_FeatureExport.py
# Purpose: Export feature class layers from the current map
#
# Author:      Don Ferguson
#
# Created:     04/09/2015
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


'''
for lyr in arcpy.mapping.Lfor lyr in arcpy.mapping.ListLayers(mxd, "*", df):
...     if lyr.isFeatureLayer:
...         print lyr.name
'''
try:
    arcpy
except NameError:
    import arcpy
from arcpy import env
import os

arcpy.env.overwriteOutput = "True"

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def joinCheck(FName, fc, mxd, df, TaskMap):
    lyrs=arcpy.mapping.ListLayers(mxd,fc,df)
    for lyr in lyrs:
        fList=arcpy.Describe(lyr).fields
        for f in fList:
            if FName in f.name:
                if type(TaskMap)== int:
                    return('"{0}" <> {1}'.format(f.name,TaskMap))
                else:
                    return('"' + f.name + '" <> ' + "'" + TaskMap + "'")
    arcpy.AddError("No field named '{0}' in {1}".format(FName,lyrs))
    return()

########
# Main Program starts here
#######
if __name__ == '__main__':
    #in_fc  - this is a point feature used to get the latitude and longitude of point.
    mxd, df = getDataframe()

    outFolder = arcpy.GetParameterAsText(0)
    if outFolder == '#' or not outFolder:
        arcpy.AddMessage("You need to provide a valid output folder")

    layerNames = arcpy.GetParameterAsText(1)
    createKMZ = arcpy.GetParameterAsText(2)
    excludeROW = arcpy.GetParameterAsText(3)

    expLayers=[]
    layerNames = layerNames.split(";")
    arcpy.AddMessage("\n")
    for lyrs in layerNames:
        try:
            lyrs = lyrs.replace("'","")
        except:
            pass

        lyrFile = arcpy.mapping.Layer(lyrs)
        outName = str(lyrFile.name)
        arcpy.AddMessage("Process {0}".format(outName))
        if lyrFile.isRasterLayer:
            outFC = os.path.join(outFolder,outName + '.tif')
            arcpy.CopyRaster_management(lyrs,outFC)#,"DEFAULTS","0","-3.402823e+038","","","16_BIT_UNSIGNED")
        else:
            outFC = os.path.join(outFolder,outName)
            if excludeROW:
                if lyrFile.name=='Probability Regions':
                    where=joinCheck('Region_Name', lyrFile.name, mxd, df, 'ROW')
                elif lyrFile.name=='Search Segments':
                    where=joinCheck('Area_Name', lyrFile.name, mxd, df, 'ROW')
                else:
                    where=""
            else:
                where=""
            arcpy.FeatureClassToFeatureClass_conversion(lyrs, outFolder,outName,where)

        if createKMZ.upper() == 'TRUE':
            outKML = "{0}.kmz".format(outFC)
            if outName=='Probability_Regions':
                where=joinCheck('Region_Name', lyrFile.name, mxd, df, 'ROW')
                arcpy.SelectLayerByAttribute_management (lyrs, "NEW_SELECTION", where)
            elif outName=='Search_Segments':
                where=joinCheck('Area_Name', lyrFile.name, mxd, df, 'ROW')
                arcpy.SelectLayerByAttribute_management (lyrs, "NEW_SELECTION", where)
            if lyrFile.visible:
                arcpy.LayerToKML_conversion(lyrs, outKML,0,"","","","",'CLAMPED_TO_GROUND')
            else:
                lyrs.visible = 1
                arcpy.LayerToKML_conversion(lyrs, outKML,0,"","","","",'CLAMPED_TO_GROUND')
                lyrs.visible = 0
            if not lyrFile.isRasterLayer:
                arcpy.SelectLayerByAttribute_management (lyrs, "CLEAR_SELECTION")
    arcpy.AddMessage("\n")
