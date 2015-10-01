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

'''
Assign =[AssignNumber, PlanNumber, Period, TaskInstruct, Milage, Team,
         ResourceType, Division, Priority, PreSearch, TaskMap, mapScale, CreateMap,
         CreateGpx, CreateKml, Assign_Safety, PrepBy, TaskDate, SegArea_KM, SearchTime]
incidInfo=[Incident_Name, Incident_Numb, MapDatum, MagDec, MapCoord, Base_Phone, Base_Freq, UtmZone, UsngGrid]
OpPeriod = [Op_Safety, wEather,PrimComms] #Refer to Assign[3] for Period
Teams= [TeamType,TeamLead,Medic, TeamCell] # Refer to Assign[5] for Team Name
TeamMember[Responder]=[TeamName, SARTeam, sKills, Role]
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
            if len(OpPeriod[2])>1:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(OpPeriod[2])))
            elif len(incidInfo[6])>0:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(incidInfo[6])))

        if len(Team)>0:
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Phone_Team",str(Team[3])))

        Notes = "Specific Safety: " + str(assSafety) + "     General Safety: " + \
            str(opSafety)
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("Notes",str(Notes)))

        del Notes
        ## txt.write("<</T(topmostSubform[0].Page1[0].Table2[0].Row1[1].TactFreq1[0])/V(" + str(TactFreq1) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].EquipIssued[0])/V(" + str(EquipIssued) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].Phone_Team[0])/V(" + str(Phone_Team) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSIdOut[0])/V(" + str(GPSIdOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].BriefBy[0])/V(" + str(BriefBy) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].DateOut[0])/V(" + str(DateOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].TimeOut[0])/V(" + str(TimeOut) + ")>>\n")
        ## txt.write("<</T(topmostSubform[0].Page1[0].GPSDatumOut[0])/V(" + str(GPSDatumOut) + ")>>\n")
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
    CreateICS204(Assign, Teams, TeamMember, AssNum, incidInfo, IncidIdx, output, OpPeriod)
