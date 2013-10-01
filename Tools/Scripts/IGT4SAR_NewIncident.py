#-------------------------------------------------------------------------------
# Name:       NewIncident.py
# Purpose: Create a new Incident for IGT4SAR and Project in the correct
#  coordinate system.
#
# Author:      Don Ferguson
#
# Created:     02/18/2013
# Copyright:   (c) Don Ferguson 2013
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

#!/usr/bin/env python
import arcpy, os
import shutil, errno
import traceback
import sys
from arcpy import env
arcpy.env.overwriteOutput = True

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise


########
# Main Program starts here
#######

#in_fc  - Source Folder
in_fc = "C:\MapSAR_Ex\Template"

#out_fc  - Target Folder
out_fc = arcpy.GetParameterAsText(0)
if out_fc == '#' or not out_fc:
    arcpy.AddMessage("You need to provide a valid out_fc")

#Set the spatial reference
output_coordinate_system = arcpy.GetParameterAsText(1)
if output_coordinate_system == '#' or not output_coordinate_system:
    arcpy.AddMessage("You need to provide a valid Coordinate System")

#Set the transformation
transformation = arcpy.GetParameterAsText(2)

if (output_coordinate_system != "") and (output_coordinate_system != "#"):
    sr = output_coordinate_system

##
##srp=arcpy.SpatialReference()
##srp.loadFromString(output_coordinate_system)
##arcpy.AddMessage(srp.datumName)

copyanything(in_fc, out_fc)

# Set environment settings
templ= in_fc  + '\\SAR_Default.gdb'
wrkspc = out_fc + '\\SAR_Default.gdb'
env.workspace = wrkspc


# Set local variables
arcpy.RefreshCatalog(wrkspc)
datasetList = arcpy.ListDatasets()

try:
    for fclist in datasetList:
        # Execute GetCount and if some features have been selected, then
        #  execute DeleteFeatures to remove the selected features.
#        arcpy.AddMessage(fclist)
        arcpy.Delete_management(fclist)

except Exception as e:
    # If an error occurred, print line number and error message
    tb = sys.exc_info()[2]
    print("Line {0}".format(tb.tb_lineno))
    print(e.message)

arcpy.RefreshCatalog(wrkspc)

try:
    for fclist in datasetList:
        # Execute GetCount and if some features have been selected, then
        #  execute DeleteFeatures to remove the selected features.
        arcpy.AddMessage(fclist)
        # Determine the new output feature class path and name
        outData = os.path.join(wrkspc, fclist)
        inData = os.path.join(templ, fclist)
        arcpy.Project_management(inData, outData, sr, transformation)

except Exception as e:
    # If an error occurred, print line number and error message
    import traceback
    import sys
    tb = sys.exc_info()[2]
    print("Line {0}".format(tb.tb_lineno))
    print(e.message)

arcpy.Compact_management(templ)
arcpy.Compact_management(wrkspc)


mxd_nA = out_fc + '\\IGT4SAR.mxd'

##mxd_nB = "%r"%mxd_nA
##mxd_name = mxd_nB[2:-1]

##
mxd = arcpy.mapping.MapDocument(mxd_nA)
df = arcpy.mapping.ListDataFrames(mxd)[0]

df.spatialReference = sr

# Add the SARToolBox
arcpy.AddToolbox("C:\\MapSAR_Ex\\Tools\\SAR_Toolbox100.tbx")

mxd.save()
del mxd

##
