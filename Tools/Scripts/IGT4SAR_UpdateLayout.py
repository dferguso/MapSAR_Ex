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
try:
    arcpy
except NameError:
    import arcpy
import geomag

def getDataframe():
    ## Get current mxd and dataframe
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT'); df = arcpy.mapping.ListDataFrames(mxd)[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def gNorth_Check(fc, fname):
    field_type = "FLOAT"
    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    if fname not in field_names:
        arcpy.AddField_management (fc, fname, field_type)
    arcpy.CalculateGridConvergenceAngle_cartography(fc,fname, "GEOGRAPHIC")
    return

def updateMapLayout():
    mxd, df = getDataframe()

    dfSpatial_Ref = df.spatialReference.name
    dfSpatial_Type = df.spatialReference.type

    # Get UTM and USNG Zones
    # Get declination from Incident Information

    fc1 = "Plan_Point"
    fc2 = "Incident_Information"
    fc3 = "Assets"

    cPlanPt = arcpy.GetCount_management(fc1)
    cBasePt = arcpy.GetCount_management(fc3)
    if int(cPlanPt.getOutput(0)) > 0:
        cPlanPt = cPlanPt
    elif int(cBasePt.getOutput(0)) > 0:
        cPlanPt = cBasePt
        fc1 = fc3
    else:
        arcpy.AddError("Warning: Need to add Planning Point or ICP prior to updating map layout\n")

    desc = arcpy.Describe(fc1)

    #First determine the grid north value
    fname = "gNORTH"
    gNorth_Check(fc1, fname)
    gridNorth = 0.0

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    shapefieldname = desc.ShapeFieldName

    rows1 = arcpy.SearchCursor(fc1, '', unProjCoordSys)
    k = 0
    declin = 0.0

    for row1 in rows1:
        gridN = row1.getValue(fname)
        feat = row1.getValue(shapefieldname)
        pnt = feat.getPart()
        latitude = pnt.Y
        longitude = pnt.X
        declin = geomag.declination(latitude,longitude) + declin
        gridNorth += gridN
        k+=1
    del rows1
    del row1

    gridN = round((gridNorth / k),2)
    if gridN > 0:
        gCard ="W"
    else:
        gCard ="E"
    gNorthTxt = str(abs(gridN)) + " " + gCard

    # Rotate data frame to adjust map layout for True North vs Grid North.
    try:
        df.rotation = gridN
        if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth")[0]:
            gridNorth=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth")[0]
            gridNorth.text = gNorthTxt
        # Remove field
        dropField=[field_name]
        arcpy.DeleteField_management(fc1, dropField)
    except:
        pass

    declin_avg = declin / k
    MagDeclinlination = round(declin_avg,2)
    if MagDeclinlination < 0:
        Cardinal ="W"
        bearingTuple=('ADD','SUBTRACT')
    else:
        Cardinal ="E"
        bearingTuple=('SUBTRACT','ADD')
    MagDecTxt = str(abs(MagDeclinlination)) + " " + Cardinal

    try:  #Update Incident Name and Number with the file name and dataframe name
        IncName = df.name
        IncNumA = mxd.filePath.split("\\")
        IncNum=IncNumA[-1].strip(".mxd")
        arcpy.AddMessage("\nThe Incident Name is " + IncName)
        arcpy.AddMessage("The Incident Number is: " + IncNum + "\n")
        MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
        MapName.text = " "

        PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
        PlanNum.text = " "

        AssignNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
        AssignNum.text = " "

        fld2 = "Incident_Name"
        fld3 = "Incident_Number"
        cursor = arcpy.UpdateCursor(fc2)
        for row in cursor:
            incidName=row.getValue(fld2)
            if incidName != IncName:
                row.setValue(fld2, IncName)
                row.setValue(fld3, IncNum)
                cursor.updateRow(row)
            del incidName
        del cursor, row
        del IncName, IncNum, fld2, fld3
    except:
        arcpy.AddMessage("Error: Update Incident Name and Number manually\n")

    arcpy.AddMessage("The Coordinate System for the dataframe is: " + dfSpatial_Type)
    arcpy.AddMessage("The Datum for the dataframe is: " + dfSpatial_Ref)
    if dfSpatial_Type=='Projected':
        arcpy.AddMessage("Be sure to turn on USNG Grid in Data Frame Properties.\n")

    arcpy.AddMessage("Updating UTM and USNG grid info on map layout")
    try:
        mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]
        arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT","1 Incident_Group\Planning Point")
        UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
        USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
        arcpy.AddMessage("Maplayers: " + mapLyr.name)
        rows=arcpy.SearchCursor(mapLyr)
        row = rows.next()
        UTMZn.text = row.getValue("GRID1MIL")
        USNGZn.text = row.getValue("GRID100K")
        arcpy.AddMessage("UTM Zone is {0} and USNG Grid is {1}".format(UTMZn.text,USNGZn.text))
        del rows
        del row
        del mapLyr
    except:
        arcpy.AddMessage("Error: Update USNG Grid and UTM Zone text fields on map layout manually\n")

    arcpy.AddMessage("Grid North correction to True North based on location of IPP or ICP is: {0}".format(gNorthTxt))
    try:
        cIncident=arcpy.GetCount_management("Incident_Information")
        # Get list of fields in Incident Information
        fieldList = arcpy.ListFields(fc2)
        field=[]
        for fld in fieldList:
            field.append(fld.name.encode('ascii','ignore'))

        if int(cIncident.getOutput(0)) > 0:
            if "MagDec" in field:
                fld1 = "MagDec"
                MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]

                try:
                    bearingConv=arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","bearingConv")[0]
                    bcText=bearingConv.text
                    # Even though the templates have %s in them, we may have
                    # clobbered them in a previous run.  So put 'em back.
                    bcText=bcText.replace('ADD','%s')
                    bcText=bcText.replace('SUBTRACT','%s')
                    bearingConv.text= bcText % bearingTuple
                    del bearingConv
                except:
                    arcpy.AddMessage("Failed to update bearing conversion text.")

                cursor = arcpy.UpdateCursor(fc2)
                for row in cursor:
                    row.setValue(fld1, MagDecTxt)
                    cursor.updateRow(row)
                MagDeclin.text = MagDecTxt
                arcpy.AddMessage("Magnetic Declination is {0}".format(MagDeclin.text))
                del cursor, row
                del MagDeclin
            else:
                arcpy.AddMessage("Magnetic Declination is not in the field list for Incident Information")
        else:
            arcpy.AddWarning("No Incident Information provided\n")
    except:
        arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")

    try:
        fld2 = "MapDatum"
        fld3 = "MapCoord"
        cursor = arcpy.UpdateCursor(fc2)
        for row in cursor:
            row.setValue(fld2, dfSpatial_Ref)
        ##                row.setValue(fld3, dfSpatial_Type)
            if "UTM_ZONE" in field:
                row.setValue("UTM_ZONE", UTMZn.text)
            if "USNG_GRID" in field:
                row.setValue("USNG_GRID", USNGZn.text)
            cursor.updateRow(row)
        del cursor, row
    except:
        arcpy.AddMessage("Error: Update Map Datum and Map Coordinates (Projected/Geogrpahic) Manually\n")

    try:
        del UTMZn
        del USNGZn
    except:
        pass

    del mxd
    del df, dfSpatial_Ref, dfSpatial_Type
    return

###########Main############
if __name__ == '__main__':
    updateMapLayout()
