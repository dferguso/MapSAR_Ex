#-------------------------------------------------------------------------------
# Name:        IGT4SAR_CreateICS204.py
# Purpose:
#
# Author:      ferguson
#
# Created:     28/01/2015
# Copyright:   (c) ferguson 2015
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
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
##import time
from os import listdir
from datetime import datetime
from math import exp

'''
Assign =[AssignNumber, PlanNumber, Period, TaskInstruct, Milage, Team,
         ResourceType, Division, Priority, PreSearch, TaskMap, mapScale, CreateMap,
         CreateGpx, CreateKml, Assign_Safety, PrepBy, TaskDate, SegArea_KM, SearchTime]
incidInfo=[Incident_Name, Incident_Numb, MapDatum, MagDec, MapCoord, Base_Phone, Base_Freq, UtmZone, UsngGrid]
OpPeriod = [Op_Safety, wEather,PrimComms] #Refer to Assign[3] for Period
Teams= [TeamType,TeamLead,Medic, TeamCell] # Refer to Assign[5] for Team Name
TeamMember[Responder]=[TeamName, SARTeam, sKills, Role, Wght]
'''

def PSARC(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    if TAF2Use in listdir(output):
        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "

        ## Incident Information
        if len(incidInfo) > 0:
            txt.write("<</T({0})/V({1})>>\n".format("IncidentName",str(incidInfo[0])))
            txt.write("<</T({0})/V({1})>>\n".format("MissNo",str(incidInfo[1])))
            txt.write("<</T({0})/V({1})>>\n".format("Phone_Base",str(incidInfo[5])))

        ## Assignment Information
        if len(Assign)>0:
            SearchTime=Assign[19]
            txt.write("<</T({0})/V({1})>>\n".format("OPPeriod",str(Assign[2])))
            if len(Assign[0])>1:
                txt.write("<</T({0})/V({1})>>\n".format("TaskNo",str(Assign[0])))
            elif len(Assign[1])>1:
                txt.write("<</T({0})/V({1})>>\n".format("TaskNo",str(Assign[1])))
            txt.write("<</T({0})/V({1})>>\n".format("ResourceType",str(Assign[6])))
            txt.write("<</T({0})/V({1})>>\n".format("Priority",str(Assign[8])))
            txt.write("<</T({0})/V({1})>>\n".format("TaskMap",str(Assign[10])))
            txt.write("<</T({0})/V({1})>>\n".format("TASKINSTRUCTIONS",str(Assign[3])))
            txt.write("<</T({0})/V({1})>>\n".format("PrepBy",str(Assign[16])))
            txt.write("<</T({0})/V({1})>>\n".format("DATE",str(Assign[17])))
            ################
            ## Team Infomration
            txt.write("<</T({0})/V({1})>>\n".format("TeamId",str(Assign[5])))
            txt.write("<</T({0})/V({1})>>\n".format("TeamId01",str(Assign[5])))
            assSafety= Assign[15]

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    txt.write("<</T({0})/V({1})>>\n".format('TeamLead',str(key)))
                    kk+=1
                elif key == Team[2]:
                    txt.write("<</T({0})/V({1})>>\n".format('Medic',str(key)))
                    kk+=1
                else:
                    txt.write("<</T(Respond{0})/V({1})>>\n".format(k,str(key)))
                    k+=1
                if k>12:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        txt.write("<</T({0})/V({1} hrs)>>\n".format("ExpectedDuration",str(SearchTime))) # SearchTime

        ## Operation Period Infomration
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            if len(OpPeriod[2])>1:
                txt.write("<</T({0})/V({1})>>\n".format("Prim_Freq",str(OpPeriod[2])))
            elif len(incidInfo[6])>0:
                txt.write("<</T({0})/V({1})>>\n".format("Prim_Freq",str(incidInfo[6])))
            txt.write("<</T({0})/V({1})>>\n".format("BaseId","BASE"))

        if len(Team)>0:
            txt.write("<</T({0})/V({1})>>\n".format("Phone_Team",str(Team[3])))

        Notes = "Specific Safety: " + str(assSafety) + "     General Safety: " + \
            str(opSafety)
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T({0})/V({1})>>\n".format("Notes",str(Notes)))

        del Notes
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return

def MD_SP(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    if TAF2Use in listdir(output):
        SearchTime = 0
        assSafety = "None "
        opSafety = "None "

        filename = output + "/" + str(AssNum) + "_TAF.fdf"
        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        ## Incident Information
        if len(incidInfo)>0:
            txt.write("<</T({0})/V({1})>>\n".format("Incident Name",str(incidInfo[0])))
            txt.write("<</T({0})/V({1})>>\n".format("MAG DECLIN",str(incidInfo[3])))
            txt.write("<</T({0})/V({1})>>\n".format("MAP DATUM",str(incidInfo[2])))
            txt.write("<</T({0})/V({1})>>\n".format("MapCoord",str(incidInfo[4])))
            txt.write("<</T({0})/V({1})>>\n".format("COMMAND POST",str(incidInfo[5])))
            ###################################
            try:
                txt.write("<</T({0})/V({1})>>\n".format("USNGZone",str(incidInfo[7])))
                txt.write("<</T({0})/V({1})>>\n".format("USNGGRID",str(incidInfo[8])))
            except:
                pass
        #################
        if len(OpPeriod)>0:
            if len(OpPeriod[2])>0:
                txt.write("<</T({0})/V({1})>>\n".format("PRIMARY FREQ",str(OpPeriod[2])))
            elif len(incidInfo[6])>0:
                txt.write("<</T({0})/V({1})>>\n".format("PRIMARY FREQ",str(incidInfo[6])))
            opSafety=OpPeriod[0]

        ## Assignment Information
        if len(Assign)>0:
            try:
                dateStamp = datetime.strftime(Assign[17], "%m/%d/%Y")
                timeStamp = datetime.strftime(Assign[17], "%H:%M %p")
            except:
                dateStamp = ""
                timeStamp = ""
            txt.write("<</T({0})/V({1})>>\n".format("DATE",str(dateStamp))) # TaskDate

            txt.write("<</T({0})/V({1})>>\n".format("Planning #",str(Assign[1])))
            txt.write("<</T({0})/V({1})>>\n".format("TASK NO",str(Assign[0])))
            txt.write("<</T({0})/V({1})>>\n".format("OPERATIONAL PERIOD",str(Assign[2])))
            txt.write("<</T({0})/V({1})>>\n".format("ResourceType",str(Assign[6])))
            txt.write("<</T({0})/V({1})>>\n".format("TYPE OF TEAM",str(Assign[6])))
            txt.write("<</T({0})/V({1})>>\n".format("Priority",str(Assign[8])))

            SearchTime=Assign[19]
            SegArea_KM=Assign[18]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)

            txt.write("<</T({0})/V({1})>>\n".format("TASK MAP",str(Assign[10])))
            txt.write("<</T({0})/V/{1}>>\n".format("Size Acres","On"))
            txt.write("<</T({0})/V({1})>>\n".format("Acres",str(SegArea_Acres)))
            txt.write("<</T({0})/V/{1}>>\n".format("Size Sq. KM","On"))
            txt.write("<</T({0})/V({1})>>\n".format("Sq KM",str(SegArea_KM)))
            txt.write("<</T({0})/V({1})>>\n".format("PreSearch",str(Assign[9])))
            txt.write("<</T({0})/V({1})>>\n".format("TASK INSTRUCTIONS",str(Assign[3])))
            txt.write("<</T({0})/V({1})>>\n".format("DISPATCHER",str(Assign[16])))
            txt.write("<</T({0})/V({1})>>\n".format("TEAM IDENTIFIER",str(Assign[5])))
            txt.write("<</T({0})/V({1})>>\n".format("TEAM CALL SIGNID",str(Assign[5])))
            assSafety=Assign[15]
        ################

        ## Team Infomration
        if len(Team)>0:
            txt.write("<</T({0})/V({1})>>\n".format("TEAM LEADERS CELL PHONE",str(Team[3])))

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    txt.write("<</T({0})/V({1})>>\n".format("Team Leader",str(key)))
                    txt.write("<</T({0})/V({1})>>\n".format("TeamLeadAg",str(TeamMember[key][1])))
                    kk+=1
                elif key == Team[2]:
                    txt.write("<</T({0})/V({1})>>\n".format("Team Medic",str(key)))
                    txt.write("<</T({0})/V({1})>>\n".format("MedicAg",str(TeamMember[key][1])))
                    kk+=1
                else:
                    txt.write("<</T(Team Member {0})/V({1})>>\n".format(str(k),str(key)))
                    txt.write("<</T(Team Member {0}Ag)/V({1})>>\n".format(str(k),str(TeamMember[key][1])))
                    k+=1
                if k>12:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        txt.write("<</T({0})/V({1})>>\n".format("EXPECTED TIME TO SEARCH",str(SearchTime)))

        ## Operation Period Infomration
        Notes = "Specific Safety: " + str(assSafety) + "     General Safety: " + \
            str(opSafety)
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T({0})/V({1})>>\n".format("SAFETY COMMENTS",str(Notes)))

        del Notes
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return

def NMSAR(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    '''
    AddFields1=["Area","ATV","Communications","Confinement","Dog",
               "Fixed Wing","Grid Line","Hasty","Helicopter","Horse",
               "Litter","Snowmobile","Technical Rope","Tracking","Vehicle"]

    AddFields2=["Text1","Name2","Name3","Name4","Name5","Name6",
                "Name7", "Name8", "Resource Name TL Comm Navigator1",
                "Resource Name TL Comm Navigator2",
                "Resource Name TL Comm Navigator2",
                "Resource Name TL Comm Navigator3",
                "Resource Name TL Comm Navigator4",
                "Resource Name TL Comm Navigator5",
                "Resource Name TL Comm Navigator6",
                "Resource Name TL Comm Navigator7",
                "Resource Name TL Comm Navigator8",
                "Skill  Equipment1",
                "Skill  Equipment2",
                "Skill  Equipment3",
                "Skill  Equipment4",
                "Skill  Equipment5",
                "Skill  Equipment6",
                "Skill  Equipment7",
                "Skill  Equipment8"
               ]
    '''
    Resource={"Ground":"Area","Air-Helicopter":"Helicopter","Air-Fixed Wing":"Fixed Wing",
              "Equine":"Horse","Swiftwater":"Technical Rope","Dive":"Technical Rope","Ground Vehicle":"Vehicle",
              "Overhead":"Technical Rope","Transportation":"Vehicle","Other":"Technical Rope","Area":"Area",
              "ATV":"ATV","Communications":"Communications","Confinement":"Confinement","Grid Line":"Grid Line",
              "Hasty/QRT":"Hasty","Investigation":"Technical Roper","K9-Area":"Dog","K9-Cadaver":"Dog",
              "K9-TrackTrail":"Dog","Litter":"Litter","Public Observation":"Technical Rope","Snowmobile":"Snowmobile",
              "Tech/Climbing":"Technical Rope","Tracking":"Tracking", "":"Area"}

    if TAF2Use in listdir(output):
        SearchTime = 0
        assSafety = "None "
        opSafety = "None "
        TeamPh = " "

        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        ## Incident Information
        if len(incidInfo)>0:
            txt.write("<</T({0})/V({1})>>\n".format("Mission NumberRow1",str(incidInfo[1]))) # MissNo

        ## Operational Period Information
        if len(OpPeriod)>0:
            if len(OpPeriod[2])>0:
                txt.write("<</T({0})/V({1})>>\n".format("Radio FrequencyRow1",str(OpPeriod[2]))) # TeamFreq
            elif len(incidInfo[6])>0:
                txt.write("<</T({0})/V({1})>>\n".format("Radio FrequencyRow1",str(incidInfo[6]))) # TeamFreq

        ## Team information
        TeamName = " "
        if len(Team)>0:
            TeamPh = Team[3]


        ##Assignemnt Information
        if len(Assign)>0:
            ## Format date and time
            try:
                dateStamp = datetime.strftime(Assign[17], "%m/%d/%Y")
                timeStamp = datetime.strftime(Assign[17], "%H:%M %p")
            except:
                dateStamp = ""
                timeStamp = ""

            txt.write("<</T({0})/V({1})>>\n".format("Operational PeriodRow1",str(Assign[2]))) # OpPeriod
            txt.write("<</T({0})/V({1})>>\n".format("DateRow1",str(dateStamp))) # TaskDate
            txt.write("<</T({0})/V({1})>>\n".format("Assignment DateRow1",str(dateStamp))) # DateOut
            txt.write("<</T({0})/V({1})>>\n".format("EstimatedDeparture TimeRow1",str(timeStamp))) # EstTime
        #    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TimeOut",str(Assign[xx]))) #TimeOut
        #    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("BriefBy",str(Assign[xx]))) # BriefBy
            txt.write("<</T({0})/V({1})>>\n".format("Reviewed byRow1",str(Assign[16]))) # ReviewBy

            SegArea_KM = Assign[18]
            SearchTime=Assign[19]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)
            if len(Assign[0])>1:
                TaskID = Assign[0]
            elif len(Assign[1])>1:
                TaskID = Assign[1]
            else:
                TaskID = " "
            TaskInstructions = "Task #: {0} \nTask: {1} \n\n Task Area: {2} Acres, {3} sq KM\nTeam Cellphone: {4}".format(TaskID, Assign[3], SegArea_Acres, SegArea_KM, TeamPh)

            # now this is nasty... NMSAR's instruction section is a bunch
            # of individual rows, and if we dump the whole string in
            # into one it doesn't flow.  So we have to break it up ourselves.
            txtStart=0
            txtEnd=min(100,len(TaskInstructions))
            txtRow=1
            while (txtEnd<=len(TaskInstructions) and txtRow<=7):
                # Let's try to do this breaking lines at spaces
                if ((txtEnd-txtStart)==100 and txtEnd<len(TaskInstructions)-1):
                    while ( TaskInstructions[txtEnd-1] != " "):
                        txtEnd = txtEnd-1

                txt.write("<</T(Assignment and or Location in the FieldRow{0})/V({1})>>\n".format(txtRow,str(TaskInstructions[txtStart:txtEnd]))) # TaskInstruct
                txtStart=txtEnd
                txtEnd=min(txtStart+100,len(TaskInstructions))
                txtRow=txtRow+1

            ## Resrouce Type
            txt.write("<</T({0})/V({1})>>\n".format("Team Number  Call SignRow1",str(Assign[5]))) #TeamID
            try:
                txt.write("<</T({0})/V({1})>>\n".format(Resource[Assign[6]],"On"))
            except:
                pass

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    txt.write("<</T({0})/V({1})>>\n".format("Text1",str(key))) # Member
                    txt.write("<</T({0})/V({1})>>\n".format("Resource Name TL Comm Navigator1",str('Team Leader'))) # LeadResource
                    txt.write("<</T({0})/V({1})>>\n".format("Skill  Equipment1",str(TeamMember[key][2]))) # LeadSkill
                    kk+=1
                else:
                    txt.write("<</T(Name{0})/V({1})>>\n".format(k,str(key))) # Member
                    txt.write("<</T(Resource Name TL Comm Navigator{0}])/V({1})>>\n".format(k,str(TeamMember[key][3]))) # Resource
                    txt.write("<</T(Skill Equipment{0})/V({1})>>\n".format(k,str(TeamMember[key][2]))) # Skill
                    k+=1
                if k>7:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        txt.write("<</T({0})/V({1})>>\n".format("Estimated Time in SegmentRow1",str(SearchTime))) # SearchTime

        del k
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return

def MapSAR(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    if TAF2Use in listdir(output):
        # Get current date and time from system
        now = datetime.now()
        todaydate = now.strftime("%m/%d/%Y")
        todaytime = now.strftime("%H:%M %p")

        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "
        phBase = " "
        phTeam = " "

        txt.write("<</T(PrepDate)/V({0})>>\n".format(todaydate))
        txt.write("<</T(PrepTime)/V({0})>>\n".format(todaytime))
        ## Incident Information
        if len(incidInfo) > 0:
            inCid = "{0} / {1}".format(str(incidInfo[0]),str(incidInfo[1]))
            mapDatum = str(incidInfo[2])
            magDec = str(incidInfo[3])
            mapCoord = str(incidInfo[4])
            phBase = str(incidInfo[5])
            baseFreq = "Base / {0}".format(str(incidInfo[6]))

            txt.write("<</T({0})/V({1})>>\n".format("IncidentName", inCid))
            txt.write("<</T({0})/V({1})>>\n".format("PrimaryComs", baseFreq))

         ## Operation Period Infomration
        #################
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            txt.write("<</T({0})/V({1})>>\n".format("AssignTeamEquipment", weaTher))
            if len(OpPeriod[2])>0:
                primFreq = str(OpPeriod[2])
            elif len(incidInfo[6])>0:
                primFreq = str(incidInfo[6])

        ## Assignment Information
        if len(Assign)>0:
            SearchTime=Assign[19]
            SegArea_KM=Assign[18]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)
            mapName = "Map: {0}".format(str(Assign[10]))
            assignSize = "Acres: {0}; Sq KM: {1}".format(str(SegArea_Acres), str(SegArea_KM))
            preSearch = "Previously Search: {0}".format(str(Assign[9]))
            teamCall = "{0} / {1}".format(str(Assign[5]), primFreq)
            aSSignment = "{0}, {1}, {2}\n{3}".format(mapName, assignSize, preSearch, str(Assign[3]))

            allTime = datetime.strptime(str(Assign[17]), "%m/%d/%y %H:%M" )
            dateStamp = datetime.strftime(allTime, "%m/%d/%Y")
            timeStamp = datetime.strftime(allTime, "%H:%M %p")

            if len(Assign[0])>1:
                txt.write("<</T({0})/V({1})>>\n".format("AssignmentNum",str(Assign[0])))
            else:
                txt.write("<</T({0})/V({1})>>\n".format("AssignmentNum",str(Assign[1])))
            txt.write("<</T({0})/V({1})>>\n".format("AssignTeam",Assign[5]))
            txt.write("<</T({0})/V({1})>>\n".format("AssignPeriod",str(Assign[2])))
            txt.write("<</T({0})/V({1})>>\n".format("StartDate",str(dateStamp))) # TaskDate
            txt.write("<</T({0})/V({1})>>\n".format("TimeBeganAssign",str(timeStamp))) # TaskDate
            txt.write("<</T({0})/V({1})>>\n".format("AssignDescription",aSSignment))
            txt.write("<</T({0})/V({1})>>\n".format("TeamCallSign",teamCall))
            txt.write("<</T({0})/V({1})>>\n".format("Assignlocation",Assign[10]))

            assSafety=Assign[15]

            txt.write("<</T({0})/V({1})>>\n".format("PreparedBy",str(Assign[16])))
        ################

        if len(Team)>0:
            phTeam = str(Team[3])
        pertPh = "Base #: {0}; Team #: {1}".format(phBase, phTeam)
        txt.write("<</T({0})/V({1})>>\n".format("PertinentPhoneNumbers", pertPh))

        Notes = "Specific Safety: {0} / General Safety: {1}".format(str(assSafety),str(opSafety) )
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T({0})/V({1})>>\n".format("AssignComInstructions",str(Notes)))
        del Notes

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if len(TeamMember[key][2])>1 and len(TeamMember[key][4])>1:
                    skillWght = "{0}, Wght={1}".format(TeamMember[key][2], TeamMember[key][4])
                elif len(TeamMember[key][2])>1:
                    skillWght = "{0}".format(TeamMember[key][2])
                elif len(TeamMember[key][4])>1:
                    skillWght = "Wght = {0}".format(TeamMember[key][4])
                else:
                    skillWght = " "

                if key==Team[1]:
                    txt.write("<</T({0}.roll)/V({1})>>\n".format('Team Leader',TeamMember[key][3]))
                    txt.write("<</T({0}.name)/V({1})>>\n".format('Team Leader',str(key)))
                    txt.write("<</T({0}.skillsandweight)/V({1})>>\n".format('Team Leader',skillWght))
                    txt.write("<</T({0}.origteam)/V({1})>>\n".format('Team Leader',str(TeamMember[key][1]))) # Agency
                    kk+=1
                else:
                    txt.write("<</T(Team Member.{0}.roll)/V({1})>>\n".format(k,TeamMember[key][3]))
                    txt.write("<</T(Team Member.{0}.name)/V({1})>>\n".format(k,str(key)))
                    txt.write("<</T(Team Member.{0}.skillsandweight)/V({1})>>\n".format(k,skillWght))
                    txt.write("<</T(Team Member.{0}.origteam)/V({1})>>\n".format(k,str(TeamMember[key][1]))) # Agency
                    k+=1
                if k>6:
                    break

        # Close and write FDF file
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()
    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return


def Arizona(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    if TAF2Use in listdir(output):
        # Get current date and time from system
        now = datetime.now()
        todaydate = now.strftime("%m/%d/%Y")
        todaytime = now.strftime("%H:%M %p")
        PrepDate = "{0}\n{1}".format(todaydate, todaytime)

        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "
        phBase = " "
        phTeam = " "
                ## Incident Information
         ## Operation Period Infomration
        #################
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            if len(OpPeriod[2])>0:
                primFreq = str(OpPeriod[2])
            elif len(incidInfo[6])>0:
                primFreq = str(incidInfo[6])
            txt.write("<</T({0})/V({1})>>\n".format("TactFreq1", primFreq))

        ## Assignment Information
        if len(Assign)>0:
            SearchSpd = Assign[20]
            SearchTime=Assign[19]
            txt.write("<</T({0})/V({1})>>\n".format("ReturnTime", SearchTime))
            SegArea_KM=Assign[18]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)

            # Assume a sweep width of 20 m (0.02km)
            arcpy.AddMessage("POD and # person required based on Coverage = 1 and Sweep Width = 20m\n")
            SearchNum = SegArea_KM/(float(SearchTime) * float(SearchSpd)*0.02)
            areaSrch = SegArea_KM
            podREQ = int((1-exp(-SegArea_KM/areaSrch))*100.0)

            mapName = "Map: {0}".format(str(Assign[10]))
            assignSize = "Acres: {0}; Sq KM: {1}".format(str(SegArea_Acres), str(SegArea_KM))
            preSearch = "Previously Search: {0}".format(str(Assign[9]))
            aSSignment = "{0}, {1}, {2}\n{3}".format(mapName, assignSize, preSearch, str(Assign[3]))

            allTime = datetime.strptime(str(Assign[17]), "%m/%d/%y %H:%M" )
            dateStamp = datetime.strftime(allTime, "%m/%d/%Y")
            timeStamp = datetime.strftime(allTime, "%H:%M %p")

            txt.write("<</T({0})/V({1})>>\n".format("TASK",str(Assign[0])))
            txt.write("<</T({0})/V({1})>>\n".format("TASK NAME",Assign[10]))
            txt.write("<</T({0})/V({1})>>\n".format("AssignName",str(Assign[1])))
            txt.write("<</T({0})/V({1})>>\n".format("TeamId",Assign[5]))
            txt.write("<</T({0})/V({1})>>\n".format("OpPeriod",str(Assign[2])))
            txt.write("<</T({0})/V({0})>>\n".format("PrepDate",PrepDate))
            txt.write("<</T({0})/V({1})>>\n".format("TaskInstruct",aSSignment))
            txt.write("<</T({0})/V({1})>>\n".format("PODreq",str(podREQ)))


            assSafety=Assign[15]

            txt.write("<</T({0})/V({1})>>\n".format("PrepBy",str(Assign[16])))
        ################
        Notes = "Specific Safety: {0};  General Safety: {1};  {2}".format(str(assSafety),str(opSafety), str(weaTher) )
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T({0})/V({1})>>\n".format("COMMENTS",str(Notes)))
        del Notes

        if len(Team)>0:
            phTeam = str(Team[3])
            txt.write("<</T({0})/V({1})>>\n".format("CELL PHONE1", phTeam))

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if len(TeamMember[key][2])>1:
                    skillWght = "{0}".format(TeamMember[key][2])
                else:
                    skillWght = " "

                if key==Team[1]:
                    txt.write("<</T({0})/V({1})>>\n".format('MEMBER1',str(key)))
                    txt.write("<</T({0})/V({1})>>\n".format('CALL SIGN1',"Leader"))
                    txt.write("<</T({0})/V({1})>>\n".format('SPECIAL SKILL',skillWght))
                    kk+=1
                else:
                    txt.write("<</T(MEMBER{0})/V({1})>>\n".format(k,str(key)))
                    txt.write("<</T(SPECIAL SKILL_{0})/V({1})>>\n".format(k,skillWght))
                    k+=1
                if k>6:
                    break

        # Close and write FDF file
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()
    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()
    return

def BASARC(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    if TAF2Use in listdir(output):
        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "

        now = datetime.now()
        todaydate = now.strftime("%m/%d/%Y")
        todaytime = now.strftime("%H:%M %p")

        ## Incident Information
        if len(incidInfo) > 0:
            if len(incidInfo[0])> 1:
                incidName = incidInfo[0]
            elif len(incidInfo[1])> 1:
                incidName = incidInfo[1]
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("incidentName",str(incidName)))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("other_radio_chan","Base Phone"))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("freqOther",str(incidInfo[5])))
            ###################################
        ## Assignment Information
        if len(Assign)>0:
            if len(Assign[0])>1:
                TaskID = Assign[0]
            elif len(Assign[1])>1:
                TaskID = Assign[1]
            else:
                TaskID = " "

            mapName = "Map: {0}".format(str(Assign[10]))
            aSSignment = "{0}\n{1}".format(mapName, str(Assign[3]))
            preSearch = "Previously Search: {0}".format(str(Assign[9]))

            allTime = datetime.strptime(str(Assign[17]), "%m/%d/%y %H:%M" )
            dateStamp = datetime.strftime(allTime, "%m/%d/%Y")
            timeStamp = datetime.strftime(allTime, "%H:%M %p")

            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("opPeriod",str(Assign[2])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("assignNumber",TaskID))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("resource_type",Assign[6]))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("asgn_description",aSSignment))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("previous_search_effort",preSearch))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("radio_call",Assign[5]))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("date_prepared", todaydate))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("time_prepared", todaytime))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("prepared_by",str(Assign[16])))

            SearchSpd = Assign[20]
            SearchTime=Assign[19]
            SegArea_KM=Assign[18]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)
            assignSize = "{0}Acres; {1}sqKM".format(str(SegArea_Acres), str(SegArea_KM))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("size_of_assignment", assignSize))

            assSafety= Assign[15]

        k=1
        if len(TeamMember)>0:
            for key in TeamMember:
                txt.write("<</T(topmostSubform[0].Page1[0].PersonnelName_{0}[0])/V({1})>>\n".format(k,str(key)))
                txt.write("<</T(topmostSubform[0].Page1[0].PersonnelAgency_{0}[0])/V({1})>>\n".format(k,str(TeamMember[key][1])))
                if key==Team[1]:
                    txt.write("<</T(topmostSubform[0].Page1[0].PersonnelFunction_{0}[0])/V({1})>>\n".format(k,"L"))
                elif key == Team[2]:
                    txt.write("<</T(topmostSubform[0].Page1[0].PersonnelFunction_{0}[0])/V({1})>>\n".format(k,"M"))
                k+=1
                if k>9:
                    break
        SearchTime = round(SearchTime/(k),2)
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1} hrs)>>\n".format("TimeAllocated",str(SearchTime))) # SearchTime

        ## Operation Period Infomration
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            if len(OpPeriod[2])>1:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("freqCommand",str(OpPeriod[2])))
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("freqTactical",str(OpPeriod[2])))
            elif len(incidInfo[6])>0:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("freqCommand",str(incidInfo[6])))
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("freqTactical",str(incidInfo[6])))


        Notes = "Specific Safety: {0};  General Safety: {1};  {2}".format(str(assSafety),str(opSafety), str(weaTher) )
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("notes",str(Notes)))

        del Notes
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return


def Tyler_County(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    if TAF2Use in listdir(output):
        filename = output + "/" + str(AssNum) + "_TAF.fdf"
        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "
        phBase = " "
        phTeam = " "
        ## Incident Information
        Incid = "{0}\n{1}".format(incidInfo[0],incidInfo[1])
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("IncidentName",Incid))
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("BasePhone",str(incidInfo[5])))

        ## Operation Period Infomration
        #################
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            if len(OpPeriod[2])>0:
                primFreq = str(OpPeriod[2])
            elif len(incidInfo[6])>0:
                primFreq = str(incidInfo[6])
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("FrequencyChannel", primFreq))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("PredictedWeather",str(weaTher)))

        ## Assignment Information
        if len(Assign)>0:
            if len(Assign[0])>1:
                TaskID = str(Assign[0])
            elif len(Assign[1])>1:
                TaskID = str(Assign[1])
            else:
                TaskID = " "

            SegArea_KM=Assign[18]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)

            mapName = "Map: {0}".format(str(Assign[10]))
            assignSize = "Acres: {0}; Sq KM: {1}".format(str(SegArea_Acres), str(SegArea_KM))
            preSearch = "Previously Search: {0}".format(str(Assign[9]))
            aSSignment = "{0}, {1}, {2}\n{3}".format(mapName, assignSize, preSearch, str(Assign[3]))

            allTime = datetime.strptime(str(Assign[17]), "%m/%d/%y %H:%M" )
            dateStamp = datetime.strftime(allTime, "%m/%d/%Y")
            timeStamp = datetime.strftime(allTime, "%H:%M %p")

            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("AssignLocation",Assign[10]))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("OpPeriod",str(Assign[2])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskNumber",TaskID))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamId",Assign[5]))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("BaseCallSign","Base"))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamCallSign",Assign[5]))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("ResourceType",str(Assign[6])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("PrepBy",str(Assign[16])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskInstruct",aSSignment))

            assSafety=Assign[15]

         ################
        Notes = "Specific Safety: {0};  General Safety: {1}".format(str(assSafety),str(opSafety))
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("SafetyPrecautions",str(Notes)))
        del Notes

        if len(Team)>0:
            phTeam = str(Team[3])
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamPhone", phTeam))

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                txt.write("<</T(topmostSubform[0].Page1[0].TeamMembersName_{0}[0])/V({1})>>\n".format(k,str(key)))
                txt.write("<</T(topmostSubform[0].Page1[0].Agency_{0}[0])/V({1})>>\n".format(k,str(TeamMember[key][1])))
                k+=1
                if k>10:
                    break

        # Close and write FDF file
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()
    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()
    return

def Default(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    if TAF2Use in listdir(output):
        filename = output + "/" + str(AssNum) + "_TAF.fdf"

        txt= open (filename, "w")
        txt.write("%FDF-1.2\n")
        txt.write("%????\n")
        txt.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(TAF2Use))
        txt.write("endobj\n")
        txt.write("2 0 obj[\n")
        txt.write ("\n")

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "

        ## Incident Information
        if len(incidInfo) > 0:
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MissNo",str(incidInfo[1])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MagDec",str(incidInfo[3])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MapDatum",str(incidInfo[2])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MapCoord",str(incidInfo[4])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Phone_Base",str(incidInfo[5])))
            ###################################
            try:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("UTMZONE",str(incidInfo[7])))
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("USNGGRID",str(incidInfo[8])))
            except:
                pass
            #################
        ## Assignment Information
        if len(Assign)>0:
            SegArea_KM=Assign[18]
            SearchTime=Assign[19]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)

            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskNo",str(Assign[0])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("PlanNo",str(Assign[1])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("ResourceType",str(Assign[6])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Priority",str(Assign[8])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskMap",str(Assign[10])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("PreSearch",str(Assign[9])))

            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskInstruct",str(Assign[3])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("SegArea_Acres",str(SegArea_Acres)))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("SegArea_KM",str(SegArea_KM)))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("PrepBy",str(Assign[16])))
            ################
            ## Team Infomration
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamId",str(Assign[5])))
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskId",str(Assign[5])))
            assSafety= Assign[15]

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format('TeamLead',str(key)))
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamLeadAg",str(TeamMember[key][1]))) # Agency
                    kk+=1
                elif key == Team[2]:
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format('Medic',str(key)))
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MedicAg",str(TeamMember[key][1]))) # Agency
                    kk+=1
                else:
                    txt.write("<</T(topmostSubform[0].Page1[0].Respond{0}[0])/V({1})>>\n".format(k,str(key)))
                    txt.write("<</T(topmostSubform[0].Page1[0].Respond{0}Ag[0])/V({1})>>\n".format(k,str(TeamMember[key][1]))) # Agency
                    k+=1
                if k>12:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("SearchTime",str(SearchTime))) # SearchTime

        ## Operation Period Infomration
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            if len(OpPeriod[2])>1:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(OpPeriod[2])))
            elif len(incidInfo[6])>0:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(incidInfo[6])))

        if len(Team)>0:
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Phone_Team",str(Team[3])))


        Notes = "Specific Safety: {0}; General Safety: {1};  {2}".format(str(assSafety),str(opSafety),str(weaTher) )
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Notes",str(Notes)))

        del Notes
        txt.write("]\n")
        txt.write("endobj\n")
        txt.write("trailer\n")
        txt.write("<</Root 1 0 R>>\n")
        txt.write("%%EO\n")
        txt.close ()

    else:
        arcpy.AddError('The Task Assignment Form: {0} is not in the output folder'.format(TAF2Use))
        sys.exit()

    return

if __name__ == '__main__':
    CreateICS204(Assign, Team, TeamMember, AssNum, incidInfo, IncidIdx, output, OpPeriod)
