#-------------------------------------------------------------------------------
# Name:        CreateAssignments_gpx.py
# Purpose:     Create Task Assignment Forms from selected rows in the
#              Assignments data layer.  New TAFs are stored by Task ID in the
#              Assignments folder
#
# Author:      Don Ferguson
#
# Created:     01/25/2012 (Updated: 01/28/2015)
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

# Take courage my friend help is on the way
import arcpy, time, sys, unicodedata
from types import *
import IGT4SAR_CreateICS204

# Environment variables
wrkspc=arcpy.env.workspace
arcpy.env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"
##arcpy.env.parallelProcessingFactor = "100%"

###############################
## Specify which TAF to use
#TAF2Use ='NMSAR'
#TAF2Use ='MD_SP'
TAF2Use ='Default_ASRC'
###############################

def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def checkNoneType(variable):
    if type(variable) is NoneType:
        result = ""
    elif variable is None:
        result=""
    else:
        result = variable
    return result

def joinCheck(FName, fc, mxd, df, TaskMap):
    lyrs=arcpy.mapping.ListLayers(mxd,fc,df)
    for lyr in lyrs:
        fList=arcpy.Describe(lyr).fields
        for f in fList:
            if FName in f.name:
                if type(TaskMap)== int:
                    return('"{0}" = {1}'.format(f.name,TaskMap))
                else:
                    return('"' + f.name + '" = ' + "'" + TaskMap + "'")
    arcpy.AddError("No field named '{0}' in {1}".format(FName,lyr))

def updateAssignmentDomain():
        # Process: Table To Domain (10)
    Assignments = "Assignments"
    try:
        cAssign=arcpy.GetCount_management(Assignments)
        if int(cAssign.getOutput(0)) > 0:
            arcpy.AddMessage("\nUpdate Assignment Numbers domain\n")
            arcpy.TableToDomain_management(Assignments, "Assignment_Number", "Assignment_Number", wrkspc, "Assignment_Number", "Assignment_Number", "REPLACE")
            try:
                arcpy.SortCodedValueDomain_management(wrkspc, "Assignment_Number", "DESCRIPTION", "ASCENDING")
            except:
                pass
        else:
            arcpy.AddMessage("No Assignment Numbers to update")
    except:
        arcpy.AddMessage("Error in Assignment Numbers update: may be two Assignments with same number or multiple blanks")
    return


def ifExist(fClass, mxd, df,TaskMap, fc, symbologyLayer, SegArea_KM, SearchTime):
    if arcpy.Exists(fClass):
        desc=arcpy.Describe(fClass)
        # Get a list of field names from the feature
        fieldsList = desc.fields
        field_names=[f.name for f in fieldsList]
        ##check for joins
        where4 = joinCheck("Area_Name",fClass, mxd, df,TaskMap)
        rows4 = arcpy.SearchCursor(fClass, where4)
        for row4 in rows4:
            if fc != "none":
                arcpy.AddWarning("Another feature has the same name")
            else:
                fc = fClass
                if "PATHLENGTH" in field_names: # fc = fc10
                    pathlength = row4.getValue("PATHLENGTH") # km
                    sweepW = row4.getValue("SWEEPWIDTH") # m
                    sweepW = sweepW / 1000.0 #convert m to km
                    SegArea_KM = pathlength*sweepW
                    SearchSpd = 50 #Assumed search speed for aircraft in km per hour
                    SearchTime = pathlength/SearchSpd
                elif "Length_miles" in field_names: # fc = fc6
                    pathlength = row4.getValue("Length_miles") # miles
                    pathlength *= 1.609344 # convert miles to km
                    sweepW = 0.01 # convert 10 m  = 0.01 km (assumed pathwidth for linear feature)
                    SegArea_KM = pathlength*sweepW
                    SearchSpd = 2.5 #Assumed search speed for ground team in km per hour
                    SearchTime = pathlength/SearchSpd
                elif "AREA_KM2" in field_names: # fc = fc7
                    SegArea_KM = row4.getValue("AREA_KM2")
                    SearchSpd = 2.5 #Assumed search speed for ground team in km per hour
                    SearchTime = SegArea_KM/0.01/SearchSpd
                else:
                    # Assume point segment fc = fc5
                    SegArea_KM = (0.1**2) * 3.141592653589793 # Area of circle with radius = 100 m
                    SearchSpd = 2.5 #Assumed search speed for ground team in km per hour
                    SearchTime = SegArea_KM/0.01/SearchSpd

                symbologyLayer = arcpy.mapping.ListLayers(mxd,fClass,df)[0]
    return(fc, symbologyLayer, SegArea_KM, SearchTime)

def CreatingMap(fc, symbologyLayer, Assign, AssNum, mxd, df, MagDec, output):
    try:
        PrintMap = Assign[12]
        TaskMap = Assign[10]
        TaskNo = Assign[0]
        PlanNo = Assign[1]

        arcpy.AddMessage("Creating task map for Assignment Number: " +str(AssNum))

        if fc == "none":
            arcpy.AddWarning("No features had this area name and No map created.")
        else:
            try:
                reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
                arcpy.mapping.RemoveLayer(df,reMoveLyr)
                del reMoveLyr
            except:
                pass

            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            where4 = joinCheck("Area_Name",fc, mxd, df,TaskMap)
            arcpy.MakeFeatureLayer_management (fc, "FgTrzG", where4)
            mkLyr = arcpy.mapping.Layer("FgTrzG")
            arcpy.mapping.AddLayer(df,mkLyr,"TOP")
            updateLayer = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
            arcpy.mapping.UpdateLayer(df,updateLayer,symbologyLayer,True)
            selectLayer = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
            ## Set transparency for the assigned area to 30% - Sept 13, 2013 - DHF
            selectLayer.transparency = 30
            try:
                ##Label Features
                ##arcpy.AddMessage("Attempt labeling")
                if selectLayer.supports("LABELCLASSES"):
                    ##arcpy.AddMessage("Supports Labelclasses\n")
                    for lblclass in selectLayer.labelClasses:
                        lblclass.showClassLabels = True
                    desc=arcpy.Describe("FgTrzG")
                    # Get a list of field names from the feature
                    shapeType = desc.shapeType
                    fieldsList = desc.fields
                    field_names=[f.name for f in fieldsList]
                    if "Area_Name" in field_names:
                        lblclass.expression = "[Area_Name]"
                    elif "AREA_NAME" in field_names:
                        lblclass.expression = "[AREA_NAME]"
                    else:
                        lblclass.expression = ""
                    updateLayer.showLabels = True
                ###########
            except:
                pass

            ##########################
            ## Add segment points to map to help define segment borders
            ##Add June 11, 2014
            try:
                mapLyr002=arcpy.mapping.ListLayers(mxd, "Segment_Points",df)[0]
                arcpy.SelectLayerByLocation_management(mapLyr002,"WITHIN_A_DISTANCE",selectLayer,"20 meters","NEW_SELECTION")
                arcpy.MakeFeatureLayer_management ("Segment_Points", "FgTrzPt")
                mkLyr002 = arcpy.mapping.Layer("FgTrzPt")
                arcpy.mapping.AddLayer(df,mkLyr002,"TOP")
                updateLayer002 = arcpy.mapping.ListLayers(mxd,"FgTrzPt",df)[0]
                ##Label Features
                ##arcpy.AddMessage("Attempt labeling")
                if updateLayer002.supports("LABELCLASSES"):
                    ##arcpy.AddMessage("Supports Labelclasses\n")
                    for lblclass in updateLayer002.labelClasses:
                        lblclass.showClassLabels = True
                    desc=arcpy.Describe("FgTrzPt")
                    # Get a list of field names from the feature
                    shapeType = desc.shapeType
                    fieldsList = desc.fields
                    field_names=[f.name for f in fieldsList]
                    if "NAME" in field_names:
                        lblclass.expression = "[NAME]"
                    else:
                        lblclass.expression = ""
                    updateLayer002.showLabels = True
                ###########

                arcpy.mapping.UpdateLayer(df,updateLayer002,"Segment_Points",True)
            except:
                pass
            ##########################
            where4 = joinCheck("Area_Name",selectLayer, mxd, df,TaskMap)
            arcpy.SelectLayerByAttribute_management (selectLayer, "NEW_SELECTION", where4)
            try:
                mapLyr=arcpy.mapping.ListLayers(mxd, "MGRSZones_World",df)[0]
                arcpy.SelectLayerByLocation_management(mapLyr,"INTERSECT",selectLayer)
                UTMZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "UTMZone")[0]
                USNGZn=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "USNGZone")[0]
                rows7=arcpy.SearchCursor(mapLyr)
                row7 = rows7.next()
                UTMZn.text = row7.getValue("GRID1MIL")
                UtmZone=UTMZn.text
                USNGZn.text = row7.getValue("GRID100K")
                UsngGrid = USNGZn.text
                ##arcpy.AddMessage("UTM Zone is " + UTMZn.text + " and USNG Grid is " + USNGZn.text)

                arcpy.SelectLayerByAttribute_management (mapLyr, "CLEAR_SELECTION")

                del mapLyr
                del UTMZn
                del USNGZn
                del row7
                del rows7
            except:
                arcpy.AddMessage("No update to UTM Zone or USNG Grid")
                pass
            where4 = joinCheck("Area_Name",selectLayer, mxd, df,TaskMap)
            arcpy.SelectLayerByAttribute_management (selectLayer, "NEW_SELECTION", where4)
            df.zoomToSelectedFeatures()
            arcpy.RefreshActiveView()
            arcpy.SelectLayerByAttribute_management (selectLayer, "CLEAR_SELECTION")

            mxd.activeView='PAGE_LAYOUT'

            mapScale = Assign[11]

            if mapScale > 0:
                pScaler = mapScale
                df.scale = pScaler*1.0
            else:
                df.scale = 24000.0

            del symbologyLayer
            del mkLyr
            del updateLayer
            del mapScale
            del pScaler

            try:
                cIncident=arcpy.GetCount_management("Incident_Information")
                if int(cIncident.getOutput(0)) > 0:
                    mapLyr = arcpy.mapping.ListLayers(mxd, "Incident_Information")[0]
                    MagDeclin=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MagDecl")[0]
                    if not MagDec:
                        arcpy.AddWarning("No Magnetic Declination provided in Incident Information")
                    else:
                        MagDeclin.text = str(MagDec)
                    del MagDeclin
                else:
                    arcpy.AddWarning("No Magnetic Declination provided in Incident Information")
            except:
                arcpy.AddMessage("Error: Update Magnetic Declination Manually\n")

            if TaskMap:
                MapName=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "MapName")[0]
                MapName.text = "  " + TaskMap
            if PlanNo:
                PlanNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "PlanNum")[0]
                PlanNum.text = "  " + PlanNo
            if TaskNo:
                TaskNum=arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "AssignNum")[0]
                TaskNum.text = "  " + TaskNo

            outFile = output + "/" + str(AssNum) + "_MAP.pdf"
    ##          outFile = output + "/" + str(AssNum) + "_aerial.pdf"

            try:
                arcpy.mapping.ExportToPDF(mxd, outFile)
            except:
                arcpy.AddWarning("  ")
                arcpy.AddWarning("Unable to produce map for Assignment: " + str(AssNum))
                arcpy.AddWarning("Problem with ExportToPDF")
                arcpy.AddWarning("  ")

            reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
            arcpy.mapping.RemoveLayer(df,reMoveLyr)

            ###############################
            ## Add June 11, 2014
            try:
                reMoveLyr002 = arcpy.mapping.ListLayers(mxd,"FgTrzPt",df)[0]
                arcpy.mapping.RemoveLayer(df,reMoveLyr002)
            except:
                pass
            ##############################

            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()

            del selectLayer
            del outFile
            del PlanNo, TaskNo, TaskMap, PrintMap
            del reMoveLyr
    except:
        arcpy.AddWarning("Unable to produce map for Assignment: " + str(AssNum))
        pass
    return

def CreatingGPX(fc, mxd, df, TaskMap, AssNum, output):
    try:
        arcpy.AddMessage("Creating gpx file for Assignment Number: " +str(AssNum))
        where4 = joinCheck("Area_Name",fc, mxd, df,TaskMap)

        if fc == "none":
            arcpy.AddWarning("No features had this area name and No gpx created.")
        else:
            desc = arcpy.Describe(fc)
            shapeName = desc.shapeFieldName

            rows6 = arcpy.SearchCursor(fc, where4, \
                r'GEOGCS["GCS_WGS_1984",' + \
                'DATUM["D_WGS_1984",' + \
                'SPHEROID["WGS_1984",6378137,298.257223563]],' + \
                'PRIMEM["Greenwich",0],' + \
                'UNIT["Degree",0.017453292519943295]]')

            filegpx = output + "/" + str(AssNum) + "_GPX.gpx"
            txt= open (filegpx, "w")
            txt.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            txt.write('<gpx xmlns="http://www.topografix.com/GPX/1/1" version="1.1" creator="IGT4SAR" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.topografix.com/GPX/gpx_overlay/0/3 http://www.topografix.com/GPX/gpx_overlay/0/3/gpx_overlay.xsd http://www.topografix.com/GPX/gpx_modified/0/1 http://www.topografix.com/GPX/gpx_modified/0/1/gpx_modified.xsd">\n')

            shpType = desc.featureClass.shapeType
            if shpType == "Point":
                for row6 in rows6:
                    feat = row6.getValue(shapeName)
                    #pnt = row6[0].getPart()
                    pnt = feat.getPart()
                    txt.write('<wpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '">\n')
                    txt.write('<desc>' + str(AssNum) + '</desc>\n')
                    txt.write('<sym>WAYPOINT</sym>\n')
                    txt.write('<extensions>\n')
                    txt.write('<label xmlns="http://www.topografix.com/GPX/gpx_overlay/0/3">\n')
                    txt.write('<label_text>' + str(AssNum) + '</label_text>\n')
                    txt.write('</label>\n')
                    txt.write('</extensions>\n')
                    txt.write('</wpt>\n')
                    del feat
                    del pnt

            else:
                txt.write('<trk>\n')
                k=1
                for row6 in rows6:
                    txt.write('<name>' + str(AssNum) + '</name>\n')
                    txt.write('<desc>' + str(AssNum) + '</desc>\n')
                    txt.write('<number>' + str(k) + '</number>\n')
                    txt.write('<extensions>\n')
                    txt.write('<label xmlns="http://www.topografix.com/GPX/gpx_overlay/0/3">\n')
                    txt.write('<label_text>' + str(AssNum) + '</label_text>\n')
                    txt.write('</label>\n')
                    txt.write('</extensions>\n')

                    #for part in row6[0].getPart():
                    for part in row6.getValue(shapeName):
                        txt.write('<trkseg>\n')
                        for pnt in part:
                            if pnt is not None:
                                txt.write('<trkpt lat="' + str(pnt.Y) + '" lon= "'+ str(pnt.X) + '"/>\n')
                        txt.write('</trkseg>\n')
                        k+=1
                    txt.write('</trk>\n')
                del k
                del rows6
                del row6

            txt.write('</gpx>')

            del shpType
            del filegpx

    except:
        arcpy.AddWarning("Unable to produce gpx for Assignment: " + where4)
        pass
    return

def CreatingKML(fc, mxd, df, TaskMap, AssNum, output):
    try:
        if fc == "none":
            arcpy.AddWarning("No features had this area name and no KML/KMZ created.")
        else:
            filekml = output + "/" + str(AssNum) + "_KML.kmz"
            fc_lyr = arcpy.mapping.Layer(fc)
            where4 = joinCheck("Area_Name",fc, mxd, df,TaskMap)
            arcpy.SelectLayerByAttribute_management(fc_lyr,"NEW_SELECTION",where4)
            fc_lyr.visible=True
            arcpy.AddMessage("Creating KML/KMZ file for Assignment Number: " +str(AssNum))
            arcpy.LayerToKML_conversion(fc_lyr,filekml,ignore_zvalue="CLAMPED_TO_GROUND")
            fc_lyr.visible=False
            arcpy.SelectLayerByAttribute_management(fc_lyr, "CLEAR_SELECTION")
    except:
        arcpy.AddWarning("Unable to produce KML/KMZ for Assignment: " + where4)
        pass
    return

if __name__ == '__main__':
    #######
    #Automate map production - July 27, 2012
    mxd, df = getDataframe()

    output = arcpy.GetParameterAsText(0)
    AssignNumber = arcpy.GetParameterAsText(1)

    output = output.replace("'\'","/")

    if arcpy.Exists("QRT_Points"):
        fc5 = "QRT_Points"
    elif arcpy.Exists("Hasty_Points"):
        fc5 = "Hasty_Points"

    if arcpy.Exists("QRT_Lines"):
        fc6 = "QRT_Lines"
    elif arcpy.Exists("Hasty_Line"):
        fc6 = "Hasty_Line"

    if arcpy.Exists("QRT_Segments"):
        fc7 = "QRT_Segments"
    elif arcpy.Exists("Hasty_Segments"):
        fc7 = "Hasty_Segments"

    fc10 = "Air Search Pattern"
    fc4 = "Search Segments"

    kmlMap = 'No'
    gpxMap = 'No'

    updateAssignmentDomain()

    clearLyrs = [fc4, fc5, fc6, fc7, fc10]
    lyrvis = [0,0,0,0,0]
    disView = mxd.activeView

    kk=0
    for clearLyr in clearLyrs:
        try:
            lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
            arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
            if lyr.visible == True:
                lyrvis[kk]=1
            else:
                lyrvis[kk]=0
            kk+=1
            lyr.visible = False
        except:
            arcpy.AddWarning("Problem clearing layer {0}".format(clearLyr))
            pass
    del kk

    ###############
    # break up the "Assignments" string to generate a list
    AssignNum = AssignNumber.split(";")

    fc1="Incident_Info"
    # Create a dictionary for Incident Information
    incidInfo={}
    cAssign=arcpy.GetCount_management(fc1)
    if int(cAssign.getOutput(0)) > 0:
        rows = arcpy.SearchCursor(fc1)
        row = rows.next()
        arcpy.AddMessage("Get Incident Info")
        zk=1
        while row:
            # you need to insert correct field names in your getvalue function
            Incident_Name = row.getValue("Incident_Name")
            Incident_Numb = row.getValue("Incident_Number")
            if Incident_Numb:
                IncidIdx = Incident_Numb
            elif Incident_Name:
                IncidIdx = Incident_Name
            else:
                arcpy.AddError("Please update incident information")
                sys.exit()

            MapDatum = checkNoneType(row.getValue("MapDatum"))
            MagDec = checkNoneType(row.getValue("MagDec"))
            MapCoord = checkNoneType(row.getValue("MapCoord"))
            Base_Phone = checkNoneType(row.getValue("Base_PhoneNumber"))
            Base_Freq = checkNoneType(row.getValue("Comms_Freq"))
            UtmZone = checkNoneType(row.getValue("UTM_Zone"))
            UsngGrid = checkNoneType(row.getValue("USNG_GRID"))
            incidInfo[IncidIdx]=[Incident_Name, Incident_Numb, MapDatum, MagDec, MapCoord, Base_Phone, Base_Freq, UtmZone, UsngGrid]

            zk+=1
            row = rows.next()
        del rows, row

    if zk == 0:
        arcpy.AddError("Please update incident information")
        sys.exit()

    fc3 = "Operation_Period"
    OpPeriod= {}
    cAssign=arcpy.GetCount_management(fc3)
    if int(cAssign.getOutput(0)) > 0:
        arcpy.AddMessage("Get Operational Period Information")
        rows3 = arcpy.SearchCursor(fc3)
        row3 = rows3.next()

        k=1
        while row3:
            Period = row3.getValue("Period")
            if not Period:
                Period = k
            Op_Safety = checkNoneType(row3.getValue("Safety_Message"))
            wEather = checkNoneType(row3.getValue("Weather"))
            PrimComms = checkNoneType(row3.getValue("Primary_Comm"))
            OpPeriod[Period] = [Op_Safety, wEather,PrimComms]
            del Period, Op_Safety, wEather
            k+=1
            row3 = rows3.next()
        del row3, rows3

###########################
    fc8 = "Teams"
    Teams={}
    cAssign=arcpy.GetCount_management(fc8)
    if int(cAssign.getOutput(0)) > 0:
        arcpy.AddMessage("Get Teams Information")
        rows3 = arcpy.SearchCursor(fc8)
        row3 = rows3.next()
        k=0
        while row3:
            TeamName = row3.getValue("Team_Name")
            TeamName = k if not TeamName else TeamName
            TeamLead = checkNoneType(row3.getValue("Leader"))
            Medic = checkNoneType(row3.getValue("Medic"))
            TeamType = checkNoneType(row3.getValue("Team_Type"))
            TeamCell = checkNoneType(row3.getValue("Cellphone_Number"))
            Teams[TeamName]= [TeamType,TeamLead,Medic,TeamCell]
            k+=1
            del TeamName, TeamLead, Medic
            row3 = rows3.next()
        del row3, rows3

##################################
    fc9 = "Team_Members"
    TeamMembers={}
    cAssign=arcpy.GetCount_management(fc9)
    if int(cAssign.getOutput(0)) > 0:
        arcpy.AddMessage("Get Team Member Information")
        rows4 = arcpy.SearchCursor(fc9)
        row4 = rows4.next()
        k=1
        while row4:
            Respond = row4.getValue("Name")
            Respond = unicodedata.normalize('NFD', Respond).encode('ascii', 'ignore')
            Respond = k if not Respond else Respond

            SARTeam =checkNoneType(row4.getValue("Originating_Team"))
            sKills = checkNoneType(row4.getValue('Skills'))
            TeamName = checkNoneType(row4.getValue("Team_Name"))
            Role =checkNoneType(row4.getValue("Role"))
            TeamMembers[Respond]=[TeamName, SARTeam, sKills, Role]

            k+=1
            del Respond, SARTeam, sKills, TeamName
            row4 = rows4.next()

        del row4, rows4
        del k
##################################
    fc2="Assignments"
    Assignment={}
    cAssign=arcpy.GetCount_management(fc2)
    if int(cAssign.getOutput(0)) > 0:
        arcpy.AddMessage("Get Assignment Information")
        rows0 = arcpy.SearchCursor(fc2)
        row0 = rows0.next()
        while row0:
            # Assign either the Assignment number (preferred) or Planning Number as the index
            AssignNumber = row0.getValue("Assignment_Number")
            PlanNumber = row0.getValue("Planning_Number")
            if AssignNumber:
                AssignIdx = AssignNumber
                PlanNumber = checkNoneType(row0).getValue("Planning_Number")
            elif PlanNumber:
                AssignNumber=''
                AssignIdx = PlanNumber
            else:
                arcpy.AddError("Assignments need to have either an Assignemnt or Planning Number")
                sys.exit()

            Period = checkNoneType(row0.getValue("Period"))

            TaskInstruct = checkNoneType(row0.getValue("Description"))
            TaskInstruct = "\n".join(TaskInstruct.splitlines()) # os-specific newline conversion
            Milage = checkNoneType(row0.getValue("Milage"))

            Team=checkNoneType(row0.getValue("Team"))
            ResourceType = checkNoneType(row0.getValue("Resource_Type"))
            Division = checkNoneType(row0.getValue("Division"))

            Priority = row0.getValue("Priority")
            Priority='High' if not Priority else Priority

            PreSearch = row0.getValue("Previous_Search")
            PreSearch='No' if not PreSearch else PreSearch

            TaskMap = checkNoneType(row0.getValue("Area_Name"))
            CreateMap = row0.getValue("Create_Map")
            CreateMap = 'Yes' if not CreateMap else CreateMap

            CreateGpx = checkNoneType(row0.getValue("Create_gpx"))
            CreateGpx = 'Yes' if not CreateGpx else CreateGpx

            CreateKml = checkNoneType(row0.getValue("Create_KML"))
            CreateKml = 'Yes' if not CreateKml else CreateKml

            mapScale = row0.getValue("Map_Scale")
            if not mapScale or mapScale <=0:
                mapScale = 24000
            df.scale = int(mapScale)

            Assign_Safety = checkNoneType(row0.getValue("Safety_note"))
            PrepBy = checkNoneType(row0.getValue("Prepared_By"))
            TaskDate =checkNoneType(row0.getValue("TimeOut"))

            Assignment[AssignIdx]=[AssignNumber, PlanNumber, Period, TaskInstruct, Milage, Team,
                       ResourceType, Division, Priority, PreSearch, TaskMap, mapScale, CreateMap,
                       CreateGpx, CreateKml, Assign_Safety, PrepBy, TaskDate]

            row0=rows0.next()
        del row0, rows0

################################################################################################
    if len(AssignNum)>0:
        arcpy.AddMessage("\n\nCreating Documentation for Task Assignments\n")
    for AssNum in AssignNum:
        AssNum=AssNum.split(",")[0]
        AssNum = AssNum.replace("'","")
        Assign = Assignment[AssNum]
        TaskMap = Assign[10]

        fc_lyr = "none"
        fc = "none"
        SegArea_KM=0
        SearchSpd=0
        SearchTime=0
        symbologyLayer = arcpy.mapping.ListLayers(mxd,"Search Boundary",df)[0]

##        try:
        if arcpy.Exists(fc4):
            ##check for joins
            where4 = joinCheck("Area_Name",fc4, mxd, df,TaskMap)
            rows4 = arcpy.UpdateCursor(fc4, where4)
            for row4 in rows4:
                if fc != "none":
                    arcpy.AddWarning("Another feature has the same name")
                else:
                    fc = fc4
                    symbologyLayer = arcpy.mapping.ListLayers(mxd,"Search Boundary",df)[0]
                    row4.Status = "Planned"
                    SegArea_Acres = row4.getValue('Area_seg')  # Area is Acres
                    SegArea_KM = SegArea_Acres / 247.104393 # Area in km**2
                    SearchSpd = checkNoneType(row4.getValue('SearchSpd'))
                    if SearchSpd == "":
                        SearchSpd = 2.5 #Assumed search speed in km per hour
                    SearchTime = SegArea_KM/0.01/SearchSpd #Assumes a sweep width of 10 m
                    rows4.updateRow(row4)


        fc, symbologyLayer, SegArea_KM, SearchTime = ifExist(fc5, mxd, df,TaskMap, fc, symbologyLayer, SegArea_KM, SearchTime)
        fc, symbologyLayer, SegArea_KM, SearchTime = ifExist(fc6, mxd, df,TaskMap, fc, symbologyLayer, SegArea_KM, SearchTime)
        fc, symbologyLayer, SegArea_KM, SearchTime = ifExist(fc7, mxd, df,TaskMap, fc, symbologyLayer, SegArea_KM, SearchTime)
        fc, symbologyLayer, SegArea_KM, SearchTime = ifExist(fc10, mxd, df,TaskMap, fc, symbologyLayer, SegArea_KM, SearchTime)

##        except:
##            arcpy.AddError("failed to get feature layer")
##            sys.exit(1)
        Assign.append(SegArea_KM); Assign.append(SearchTime)
    ###Create ICS204 - Moved June 23, 2014 by Don Ferguson to accomodate USNG_GRID and UTM_ZONE
        arcpy.AddMessage("Creating Task Assignment Form for Assignment Number: " +str(AssNum))
        incInfo = incidInfo[IncidIdx]
        OpPd=[]
        if OpPeriod[Assign[2]]:
            OpPd = OpPeriod[Assign[2]]
        Team=[]
        Respd=[]
        TeamMember={}
        if Assign[5]!="":
            if Teams[Assign[5]]:
                Team=Teams[Assign[5]]
            Respd=[key for key in TeamMembers if TeamMembers[key][0]==Assign[5]]
            for Rsp in Respd:
                TeamMember[Rsp]=TeamMembers[Rsp]
        if len(Respd)==0:
            arcpy.AddMessage("Time estimates based on single searcher - divide by total number of searchers assigned")
        mod_name = TAF2Use
        CreateICS204 = "IGT4SAR_CreateICS204.{0}(Assign, Team, TeamMember, AssNum, incInfo, output, OpPd)".format(mod_name)
        exec CreateICS204
##########################################
    ##Create Map for Task Assignment
    ##
        if Assign[12] == 'Yes':
            CreatingMap(fc, symbologyLayer, Assign, AssNum, mxd, df, MagDec, output)
        else:
            arcpy.AddMessage('No map created')

    ## Create gpx file for task
        if Assign[13] == 'Yes':
            CreatingGPX(fc, mxd, df, TaskMap, AssNum, output)
        else:
            arcpy.AddMessage('No gpx file created')

    ## Create kml file for task
    ##Automate map production - July 27, 2012
        if Assign[14] == 'Yes':
            CreatingKML(fc, mxd, df, TaskMap, AssNum, output)
        else:
            arcpy.AddMessage('No KML/KMZ file created')


        arcpy.AddMessage("\n")
##########################################

    mxd.activeView = disView
    arcpy.RefreshActiveView()

    try:
        reMoveLyr = arcpy.mapping.ListLayers(mxd,"FgTrzG",df)[0]
        arcpy.mapping.RemoveLayer(df,reMoveLyr)
        del reMoveLyr
    except:
        pass

    kk=0
    for clearLyr in clearLyrs:
        lyr = arcpy.mapping.ListLayers(mxd, clearLyr,df)[0]
        arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
        if lyrvis[kk] == 1:
            lyr.visible = 1
        else:
            lyr.visible = 0
        kk+=1

    del kk
    del lyr, clearLyr, clearLyrs
    del AssNum, Assign, TaskMap
    del fc, fc1, fc2, fc3, fc4,fc5,fc6,fc7,fc8,fc9, fc10
    del lyrvis, disView
    #######
    del mxd
    del df
