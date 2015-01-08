# ---------------------------------------------------------------------------
# Name:        IPP_EuclideanDistance2.py
#
# Purpose:   Creates the Statistical Search Area around the IPP using Ring Model
#  (25%, 50%, 75% and 95%) based on historical data related to Lost Person
#  Behavior.  Specific subject category is obtained from the Subject
#  Information.  IPP Distances are provided by Robert Koester (dbs Productions -
#  Lost Person Behvaior) and are not included in this copyright.
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
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
# Import arcpy module

import arcpy
import string

def RingDistances(Subject_Category, EcoReg, Terrain):
    arcpy.AddMessage("Subject Category is " + Subject_Category)

    if Subject_Category == "Abduction":
        Distances = [0.2,1.5,12.0]

    elif Subject_Category == "Aircraft":
        Distances = [0.4,0.9,3.7,10.4]

    elif Subject_Category == "Angler":
        if EcoReg == "Temperate":
            if Terrain == "Mountainous":
                Distances = [0.2,0.9,3.4,6.1]
            else:
                Distances = [0.5,1.0,3.4,6.1]
        elif EcoReg == "Dry":
            Distances = [2.0,6.0,6.5,8.0]
        else:
            Distances = [0.5,1.0,3.4,6.1]

    elif Subject_Category == "All Terrain Vehicle":
        Distances = [1.0,2.0,3.5,5.0]

    elif Subject_Category == "Autistic":
        if EcoReg == "Urban":
            Distances = [0.2,0.6,2.4,5.0]
        else:
            Distances = [0.4,1.0,2.3,9.5]

    elif Subject_Category == "Camper":
        if Terrain == "Mountainous":
            if EcoReg == "Dry":
                Distances = [0.4,1.0,2.6,20.3]
            else:
                Distances = [0.1,1.4,1.9,24.7]
        else:
            Distances = [0.1,0.7,2.0,8.0]

    elif Subject_Category == "Child (1-3)":
        if EcoReg == "Dry":
            Distances = [0.4,0.8,2.4,5.6]
        elif EcoReg == "Urban":
            Distances = [0.1,0.3,0.5,0.7]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.1,0.2,0.6,2.0]
        else:
            Distances = [0.1,0.2,0.6,2.0]

    elif Subject_Category == "Child (4-6)":
        if EcoReg == "Dry":
            Distances = [0.4,1.2,2.0,5.1]
        elif EcoReg == "Urban":
            Distances = [0.06,0.3,0.6,2.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.1,0.5,0.9,2.3]
        else:
            Distances = [0.1,0.4,0.9,4.1]

    elif Subject_Category == "Child (7-9)":
        if EcoReg == "Dry":
            Distances = [0.3,0.8,2.0,4.5]
        elif EcoReg == "Urban":
            Distances = [0.1,0.3,0.9,3.2]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.0,2.0,7.0]
        else:
            Distances = [0.1,0.5,1.3,5.0]

    elif Subject_Category == "Child (10-12)":
        if EcoReg == "Dry":
            Distances = [0.5,1.3,4.5,10.0]
        elif EcoReg == "Urban":
            Distances = [0.2,0.9,1.8,3.6]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.0,2.0,5.6]
        else:
            Distances = [0.3,1.0,3.0,6.2]

    elif Subject_Category == "Child (13-15)":
        if EcoReg == "Dry":
            Distances = [1.5,2.0,3.0,7.4]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.5,1.3,3.0,13.3]
        else:
            Distances = [0.4,0.8,2.0,6.2]

    elif Subject_Category == "Climber":
        Distances = [0.1,1.0,2.0,9.2]

    elif Subject_Category == "Dementia":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [0.6,1.2,1.9,3.8]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.3,1.0,2.2,7.3]
        elif EcoReg == "Urban":
            Distances = [0.2,0.7,2.0,7.8]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.2,0.5,1.2,5.1]
        else:
            Distances = [0.2,0.6,1.5,7.9]

    elif Subject_Category == "Despondent":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [0.5,1.0,2.1,11.1]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.3,1.2,2.3,12.8]
        elif EcoReg == "Urban":
            Distances = [0.06,0.3,0.9,8.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.2,0.7,2.0,13.3]
        else:
            Distances = [0.2,0.5,1.4,10.7]

    elif Subject_Category == "Gatherer":
        if EcoReg == "Dry":
            Distances = [1.0,1.6,3.6,6.9]
        else:
            Distances = [0.9,2.0,4.0,8.0]

    elif Subject_Category == "Hiker":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [1.0,2.0,4.0,11.9]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [0.8,1.3,4.1,8.1]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
            Distances = [0.7,1.9,3.6,11.3]
        else:
            Distances = [0.4,1.1,2.0,6.1]

    elif Subject_Category == "Horseback Rider":
        Distances = [0.2,2.0,5.0,12.2]

    elif Subject_Category == "Hunter":
        if EcoReg == "Dry" and Terrain == "Mountainous":
            Distances = [1.3,3.0,5.0,13.8]
        elif EcoReg == "Dry" and Terrain == "Flat":
            Distances = [1.0,1.9,4.0,7.0]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.6,1.3,3.0,10.7]
        else:
            Distances = [0.4,1.0,1.9,8.5]

    elif Subject_Category == "Mental Illness":
        if EcoReg == "Urban":
            Distances = [0.2,0.4,0.9,7.7]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.4,1.4,5.1,9.0]
        else:
            Distances = [0.5,0.6,1.4,5.0]

    elif Subject_Category == "Mental Retardation":
        if EcoReg == "Dry":
            Distances = [0.7,2.5,5.4,38.9]
        elif EcoReg == "Urban":
            Distances = [0.2,0.5,2.3,6.14]
        elif EcoReg == "Temperate" and Terrain == "Mountainous":
                Distances = [0.4,1.0,2.0,7.0]
        else:
            Distances = [0.2,0.6,1.3,7.3]

    elif Subject_Category == "Mountain Biker":
        if EcoReg == "Dry":
            Distances = [1.7,4.0,8.2,18.1]
        else:
            Distances = [1.9,2.5,7.0,15.5]

    elif Subject_Category == "Other (Extreme Sport)":
        Distances = [0.3,1.6,3.5,8.3]

    elif Subject_Category == "Runner":
        Distances = [0.9,1.6,2.1,3.6]

    elif Subject_Category == "Skier-Alpine":
        Distances = [0.7,1.7,3.0,9.4]

    elif Subject_Category == "Skier-Nordic":
        if EcoReg == "Dry":
            Distances = [1.2,2.7,4.0,12.1]
        else:
            Distances = [1.0,2.2,4.0,12.2]

    elif Subject_Category == "Snowboarder":
        Distances = [1.0,2.0,3.8,9.5]

    elif Subject_Category == "Snowmobiler":
        if EcoReg == "Dry":
            Distances = [1.0,3.0,8.7,18.9]
        elif EcoReg == "Temperate" and Terrain == "Flat":
                Distances = [0.8,2.9,25.5,59.7]
        else:
            Distances = [2.0,4.0,6.9,10.0]

    elif Subject_Category == "Substance Abuse":
        Distances = [0.3,0.7,2.6,6.0]

    else:
        arcpy.AddMessage("NO SUBJECT CATEGORY PROVIDED - USING DEFAULT VALUES")
        arcpy.AddMessage("25% - 0.4, 50% - 1.1, 75% - 2.0, 95% - 6.1 : units = miles")
        Distances = [0.4,1.1,2.0,6.1]

    return(Distances)

def getDataframe():
    ## Get current mxd and dataframe
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT')
        df = arcpy.mapping.ListDataFrames(mxd)[0]

        return(mxd,df)

    except SystemExit as err:
            pass


if __name__ == '__main__':

    mxd, df = getDataframe()

    # Script arguments
    SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
    IPP = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP
    UserSelect = arcpy.GetParameterAsText(2)  # Subejct Category or User Defined Values
    bufferUnit = arcpy.GetParameterAsText(3) # Desired units
    IPPDists = arcpy.GetParameterAsText(4)  # Optional - User entered distancesDetermine to use PLS or LKP

    #arcpy.env.workspace = workspc

    # Overwrite pre-existing files
    arcpy.env.overwriteOutput = True
    IPPBuffer = "Planning\StatisticalArea"

    SubNum = int(SubNum)
    fc1="Incident_Info"

    EcoReg = "Temperate"
    Terrain = "Mountainous"
    PopDen = "Wilderness"

    try:
        rows = arcpy.SearchCursor(fc1)
        row = rows.next()

        while row:
            # you need to insert correct field names in your getvalue function
            EcoReg = row.getValue("Eco_Region")
            Terrain = row.getValue("Terrain")
            PopDen = row.getValue("Pop_Den")
            row = rows.next()
        del rows
        del row

    except:
        EcoReg = "Temperate"
        Terrain = "Mountainous"
        PopDen = "Wilderness"
        arcpy.AddWarning("No Incident Information provided. Default values used.")
        arcpy.AddWarning("Eco_Region = Temperate; Terrain = Mountainous; Population Density = Wilderness.")
        arcpy.AddWarning("If inappropriate...Remove Statistical Search Area Layer, \nprovide Incident Information and re-run\n")



    fc2 = "Subject_Information"
    where = '"Subject_Number"= %d' % (SubNum)
    rows = arcpy.SearchCursor(fc2, where)
    row = rows.next()

    while row:
        # you need to insert correct field names in your getvalue function
        Subject_Category = row.getValue("Category")
        row = rows.next()
    del rows
    del row
    del where

    if UserSelect=='User Defined Values':
        Dist = IPPDists.split(',')
        Distances=map(float,Dist)
        Distances.sort()
        mult = 1.0
    else:
        if bufferUnit =='kilometers':
            mult = 1.6093472
        else:
            mult = 1.0
    #    bufferUnit = "miles"
        Distances = RingDistances(Subject_Category, EcoReg, Terrain)

    # Buffer areas of impact around major roads
    fc3 = "Planning Point"

    where1 = '"Subject_Number" = ' + str(SubNum)
    where2 = ' AND "IPPType" = ' + "'" + IPP + "'"
    where = where1 + where2

    arcpy.SelectLayerByAttribute_management(fc3, "NEW_SELECTION", where)
    arcpy.AddMessage("Buffer IPP around the " + IPP )

    dissolve_option = "ALL"

    k=0

    rows = arcpy.SearchCursor(fc3, where)
    for row in rows:
    ##row = rows.next()
        k=1
        if bufferUnit =='kilometers':
            fieldName3 = "Area_SqKm"
            fieldAlias3 = "Area (sq km)"
            expression3 = "round(!shape.area@squarekilometers!,2)"
            pDistIPP = '"IPPDist"'

        else:
            fieldName3 = "Area_SqMi"
            fieldAlias3 = "Area (sq miles)"
            expression3 = "round(!shape.area@squaremiles!,2)"
            pDistIPP = '"IPPDist"'

        perct = ['25%', '50%', '75%', '95%']
        inFeatures = IPPBuffer
        fieldName1 = "Descrip"
        fieldName2 = "Area_Ac"
        fieldName4 = "Sub_Cat"

        fieldAlias1 = "Description"
        fieldAlias2 = "Area (Acres)"
        fieldAlias4 = "Subject Category"

        expression2 = "int(!shape.area@acres!)"

        pDist=[]
        for x in Distances:
            pDist.append(round(x * mult,2))

        arcpy.AddMessage("Units = " + bufferUnit)
        arcpy.AddMessage(pDist)

        while row:
            # you need to insert correct field names in your getvalue function
            arcpy.MultipleRingBuffer_analysis(fc3, IPPBuffer, pDist, bufferUnit, "DistFrmIPP", dissolve_option, "FULL")
            row = rows.next()

        del rows
        del row
        del where

        arcpy.AddMessage('Completed multi-ring buffer')

        arcpy.AddField_management(inFeatures, fieldName1, "TEXT", "", "", "25",
                                  fieldAlias1, "NULLABLE", "","PrtRange")
        arcpy.AddField_management(inFeatures, fieldName2, "DOUBLE", "", "", "",
                                  fieldAlias2, "NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName3, "DOUBLE", "", "", "",
                                  fieldAlias3, "NULLABLE")
        arcpy.AddField_management(inFeatures, fieldName4, "TEXT", "", "", "25",
                                  fieldAlias4, "NULLABLE", "","PrtRange")

        arcpy.AddMessage('Completed AddFields')

        arcpy.CalculateField_management(IPPBuffer, fieldName2, expression2,
                                            "PYTHON")
        arcpy.CalculateField_management(IPPBuffer, fieldName3, expression3,
                                            "PYTHON")

        rows = arcpy.UpdateCursor(IPPBuffer)
        arcpy.AddMessage('Completed update cursor')
        row = rows.next()

        k=0
        while row:
            # you need to insert correct field names in your getvalue function
            row.setValue(fieldName1, perct[k])
            row.setValue(fieldName4, Subject_Category)
            arcpy.AddMessage('Completed setValues')
            rows.updateRow(row)
            k=k+1
            row = rows.next()

        del rows
        del row
        ##del where

        arcpy.AddMessage('get current map document')
        # get the map document
        mxd = arcpy.mapping.MapDocument("CURRENT")

        arcpy.AddMessage('get data frame')
        # get the data frame
        df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        # create a new layer
        arcpy.AddMessage('Insert IPPBuffer')
        insertLayer = arcpy.mapping.Layer(IPPBuffer)

        #Insert layer into Reference layer Group
        arcpy.AddMessage("Add layer to '13 Incident_Analysis\StatisticalArea'")
        refGroupLayer = arcpy.mapping.ListLayers(mxd,'*Incident_Analysis*',df)[0]
        arcpy.mapping.AddLayerToGroup(df, refGroupLayer, insertLayer,'TOP')

##        try:
        # Set layer that output symbology will be based on
        lyr = arcpy.mapping.ListLayers(mxd, insertLayer.name, df)[0]
        symbologyLayer = r"C:\MapSAR_Ex\Tools\Layers Files - Local\Layer Groups\StatisticalArea.lyr"
        # Apply the symbology from the symbology layer to the input layer
        arcpy.ApplySymbologyFromLayer_management(lyr, symbologyLayer)
        arcpy.AddMessage("Add default symbology")
##        except:
##            pass

    if k == 0:
        arcpy.AddMessage("There was no " + IPP + " defined")



