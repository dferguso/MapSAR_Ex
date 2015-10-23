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
try:
    sys
except NameError:
    import sys
import geomag

def getDataframe():
    ## Get current mxd and dataframe
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT'); df = arcpy.mapping.ListDataFrames(mxd)[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def checkFields(fc, fldName, fldType):
    desc=arcpy.Describe(fc)
    # Get a list of field names from the feature
    fieldsList = desc.fields
    field_names=[f.name for f in fieldsList]
    if fldName not in field_names:
        arcpy.AddField_management (fc, fldName, fldType)
    return

def gNorth_Check(fc, fldName, fldType):
    checkFields(fc, fldName, fldType)
    arcpy.CalculateGridConvergenceAngle_cartography(fc,fldName, "GEOGRAPHIC")
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
        intLyr = "1 Incident_Group\Planning Point"
    elif int(cBasePt.getOutput(0)) > 0:
        cPlanPt = cBasePt
        fc1 = fc3
        intLyr = "2 Incident Assets\Assets"
    else:
        arcpy.AddError("Warning: Need to add Planning Point or ICP prior to updating map layout.\n")
        arcpy.AddError("Warning: Map Layout COULD NOT be updated.\n")
        sys.exit(0)

    desc = arcpy.Describe(fc1)

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    shapefieldname = desc.ShapeFieldName

    #First determine the grid north value
    fld_gNorth = "gNORTH"
    field_type = "FLOAT"
    gNorth_Check(fc1, fld_gNorth, field_type)
    if fc1 == "Assets":
        where0 = '"Asset_Type" = 1'
    else:
        where0 = ""
    rows0 = arcpy.SearchCursor(fc1, where0, unProjCoordSys)
    k = 0.0
    gridNorth = 0.0
    for row0 in rows0:
        gridN = row0.getValue(fld_gNorth)
        arcpy.AddMessage('Grid North: {0}'.format(gridN))
        gridNorth += float(gridN)
        k+=1.0
    del row0
    del rows0
    del k


    rows1 = arcpy.SearchCursor(fc1, where0, unProjCoordSys)
    k = 0
    declin = 0.0
    for row1 in rows1:
        feat = row1.getValue(shapefieldname)
        pnt = feat.getPart()
        latitude = pnt.Y
        longitude = pnt.X
        declin = geomag.declination(latitude,longitude) + declin
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
    # Grid North is parallel with the edge of the page.  The "True North" arrow
    # should be rotated to TRUE NORTH.
    try:
        df.rotation = 0.0
        if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth"):
            gridNorth=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "gNorth")[0]
            gridNorth.text = gNorthTxt
        # Remove field
        dropField=[fld_gNorth]
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

##    try:  #Update Incident Name and Number with the file name and dataframe name
    IncName = df.name
    IncNumA = mxd.filePath.split("\\")
    IncNum=IncNumA[-1].strip(".mxd")
    arcpy.AddMessage("\nThe Incident Name is " + IncName)
    arcpy.AddMessage("The Incident Number is: " + IncNum + "\n")
    if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName"):
        MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
        MapName.text = " "

    if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum"):
        PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
        PlanNum.text = " "

    if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum"):
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
##    except:
##        arcpy.AddMessage("Error: Update Incident Name and Number manually\n")

    arcpy.AddMessage("The Coordinate System for the dataframe is: " + dfSpatial_Type)
    arcpy.AddMessage("The Datum for the dataframe is: " + dfSpatial_Ref)
    if dfSpatial_Type=='Projected':
        arcpy.AddMessage("Be sure to turn on USNG Grid in Data Frame Properties.\n")

    arcpy.AddMessage("Updating UTM and USNG grid info on map layout")
##    try:
    for llyr in arcpy.mapping.ListLayers(mxd, "*",df):
        if str(llyr.name) == "MRGS_UTM_USNG":
            mapLyr=arcpy.mapping.ListLayers(mxd, "MRGS_UTM_USNG",df)[0]
        elif str(llyr.name) == "MRGSZones_World":
            mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]
    arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT", intLyr) #"1 Incident_Group\Planning Point")
    cursor=arcpy.SearchCursor(mapLyr)
    for row in cursor:
        if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone"):
            UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
            UTMZn.text = row.getValue("GRID1MIL")
            UTMzone = str(UTMZn.text)
        else:
            UTMzone = ""

        if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone"):
            USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
            USNGZn.text = row.getValue("GRID100K")
            USNGzone = str(USNGZn.text)
        else:
            USNGzone =""
        arcpy.AddMessage("UTM Zone is {0} and USNG Grid is {1}".format(UTMzone,USNGzone))
    del cursor
    try:
        del row
    except:
        pass
    del mapLyr
##    except:
##        arcpy.AddMessage("Error: Update USNG Grid and UTM Zone text fields on map layout manually\n")

    arcpy.AddMessage("Grid North correction to True North based on location of IPP or ICP is: {0}".format(gNorthTxt))
    try:
        cIncident=arcpy.GetCount_management("Incident_Information")
        # Get list of fields in Incident Information
        fieldList = arcpy.ListFields(fc2)
        field=[]
        for fld in fieldList:
            field.append(fld.name.encode('ascii','ignore'))

        fld_gNorth = "gNORTH"
        fldType = "STRING"
        checkFields(fc2, fld_gNorth, fldType)

        fld_MagDec = "MagDec"
        fldType = "STRING"
        checkFields(fc2, fld_MagDec, fldType)


        if int(cIncident.getOutput(0)) > 0:
            cursor = arcpy.UpdateCursor(fc2)
            for row in cursor:
                row.setValue(fld_MagDec, MagDecTxt)
                row.setValue(fld_gNorth, gNorthTxt)
                cursor.updateRow(row)
            if arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl"):
                MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
                MagDeclin.text = MagDecTxt
                arcpy.AddMessage("Magnetic Declination is {0}\n".format(MagDeclin.text))
                del MagDeclin
            del cursor, row

        else:
            arcpy.AddWarning("No Incident Information provided\n")

        try:
            if arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT","bearingConv"):
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
