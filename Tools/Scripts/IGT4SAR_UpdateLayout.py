#-------------------------------------------------------------------------------
# Name:        UpdateLayout.py
# Purpose: Updates the following fields on the map layout: UTM Zone, USNG 100k
#  Zone and Magnestic Declination (from Incident Information Layer).
#
# Author:      Don Ferguson
#
# Created:     06/18/ 2012
# Copyright:   (c) Don Ferguson 2012
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

# Take courage my friend help is on the way
import arcpy
import geomag

mxd=arcpy.mapping.MapDocument("CURRENT")
df=arcpy.mapping.ListDataFrames(mxd,"*")[0]

# Get UTM and USNG Zones
# Get declination from Incident Information

fc1 = "Plan_Point"
unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
desc = arcpy.Describe(fc1)
shapefieldname = desc.ShapeFieldName

arcpy.AddMessage("Checking for Planning Point\n")
try:
    cPlanPt =arcpy.GetCount_management(fc1)
    if int(cPlanPt.getOutput(0)) > 0:
        rows1 = arcpy.SearchCursor(fc1, '', unProjCoordSys)
        k = 0
        declin = 0
        for row1 in rows1:
            feat = row1.getValue(shapefieldname)
            pnt = feat.getPart()
            latitude = pnt.Y
            longitude = pnt.X
            declin = geomag.declination(latitude,longitude) + declin
            k+=1
        del rows1
        del row1

        declin_avg = declin / k
        MagDeclinlination = round(declin_avg,2)
        if MagDeclinlination < 0:
            Cardinal ="W"
        else:
            Cardinal ="E"
        MagDecTxt = str(abs(MagDeclinlination)) + " " + Cardinal
        arcpy.AddMessage(MagDecTxt)

        try:
            cIncident=arcpy.GetCount_management("Incident_Information")
            arcpy.AddMessage("Checking Incident Information")
            if int(cIncident.getOutput(0)) > 0:
                fc2 = "Incident_Information"
                field = "MagDec"
                MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
                cursor = arcpy.UpdateCursor(fc2)
                for row in cursor:
                    row.setValue(field, MagDecTxt)
                    cursor.updateRow(row)
                MagDeclin.text = MagDecTxt
                arcpy.AddMessage("Magnetic Declination is " + MagDeclin.text + "\n")
                del row
                del MagDeclin
            else:
                arcpy.AddWarning("No Incident Information provided\n")
        except:
            arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")

        try:
            arcpy.AddMessage("Updating UTM and USNG grid info")
            mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]
            arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT","1 Incident_Group\Planning Point")
            UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
            USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
            arcpy.AddMessage("Maplayers: " + mapLyr.name)
            rows=arcpy.SearchCursor(mapLyr)
            row = rows.next()
            UTMZn.text = row.getValue("GRID1MIL")
            USNGZn.text = row.getValue("GRID100K")
            arcpy.AddMessage("UTM Zone is " + UTMZn.text + " and USNG Grid is " + USNGZn.text + "\n")
            del rows
            del row
            del mapLyr
            del UTMZn
            del USNGZn
            arcpy.AddMessage("Refresh display when complete, View > Refresh or F5\n")
        except:
            arcpy.AddMessage("Error: Update USNG Grid and UTM Zone text fields on map layout manually\n")
    else:
        arcpy.AddWarning("Warning: Need to add Planning Point prior to updating map layout\n")
except:
    arcpy.AddWarning("There was an error")
del mxd
del df