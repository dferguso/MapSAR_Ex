#-------------------------------------------------------------------------------
# Name:        IGT4SAR_CreateICS204.py
# Purpose:
#
# Author:      ferguson
#
# Created:     28/01/2015
# Copyright:   (c) ferguson 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
try:
    arcpy
except NameError:
    import arcpy
try:
    sys
except NameError:
    import sys
import time
from datetime import datetime
from os import listdir

'''
Assign =[AssignNumber, PlanNumber, Period, TaskInstruct, Milage, Team,
         ResourceType, Division, Priority, PreSearch, TaskMap, mapScale, CreateMap,
         CreateGpx, CreateKml, Assign_Safety, PrepBy, TaskDate, SegArea_KM, SearchTime]
incidInfo=[Incident_Name, Incident_Numb, MapDatum, MagDec, MapCoord, Base_Phone, Base_Freq, UtmZone, UsngGrid]
OpPeriod = [Op_Safety, wEather,PrimComms] #Refer to Assign[3] for Period
Teams= [TeamType,TeamLead,Medic, TeamCell] # Refer to Assign[5] for Team Name
TeamMember[Responder]=[TeamName, SARTeam, sKills, Role]
'''

def MD_SP(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod):
    TAF2Use = 'MSP Form 70-3 Task Assignment 5-15new.pdf'
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

def NMSAR(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod):
    TAF2Use = 'NMSAR_ICS204.pdf'
    '''
    AddFields1=["Chk_AreaTeam","Chk_ATVTeam","Chk_CommTeam","Chk_ConfineTeam","Chk_DogTeam",
               "Chk_FixedWing","Chk_GridTeam","Chk_HastyTeam","Chk_HeliTeam","Chk_HorseTeam",
               "Chk_LitterTeam","Chk_SnowMobile","Chk_Technical","Chk_TrackingTeam","Chk_VehicleTeam"]

    AddFields2=["Respond1","Respond2","Respond3","Respond4","Respond5","Respond6",
                "Respond7", "LeadResource","Resource1","Resource2", "Resource3", "Resource4",
                "Resource5", "Resource6","Resource7","LeadSkill", "Skill1", "Skill2", "Skill3",
                "Skill4", "Skill5","Skill6", "Skill7"]
    '''
    Resource={"Ground":"Chk_AreaTeam","Air-Helicopter":"Chk_HeliTeam","Air-Fixed Wing":"Chk_FixedWing",
              "Equine":"Chk_HorseTeam","Swiftwater":"Chk_Technical","Dive":"Chk_Technical","Ground Vehicle":"Chk_VehicleTeam",
              "Overhead":"Chk_Technical","Transportation":"Chk_VehicleTeam","Other":"Chk_Technical","Area":"Chk_AreaTeam",
              "ATV":"Chk_ATVTeam","Communications":"Chk_CommTeam","Confinement":"Chk_ConfineTeam","Grid Line":"Chk_GridTeam",
              "Hasty/QRT":"Chk_HastyTeam","Investigation":"Chk_Technical","K9-Area":"Chk_DogTeam","K9-Cadaver":"Chk_DogTeam",
              "K9-TrackTrail":"Chk_DogTeam","Litter":"Chk_LitterTeam","Public Observation":"Chk_Technical","Snowmobile":"Chk_SnowMobile",
              "Tech/Climbing":"Chk_Technical","Tracking":"Chk_TrackingTeam", "":"Chk_AreaTeam"}

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
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("MissNo",str(incidInfo[1]))) # MissNo
            txt.write("<</T(topmostSubform[0].Page2[0].{0}[0])/V({1})>>\n".format("MissNo",str(incidInfo[1]))) # MissNo

        ## Operational Period Information
        if len(OpPeriod)>0:
            if len(OpPeriod[2])>0:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(OpPeriod[2]))) # TeamFreq
            elif len(incidInfo[6])>0:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamFreq",str(incidInfo[6]))) # TeamFreq

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

            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("OpPeriod",str(Assign[2]))) # OpPeriod
            txt.write("<</T(topmostSubform[0].Page2[0].{0}[0])/V({1})>>\n".format("OpPeriod",str(Assign[2]))) # OpPeriod
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskDate",str(dateStamp))) # TaskDate
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("DateOut",str(dateStamp))) # DateOut
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("EstTime",str(timeStamp))) # EstTime
        #    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TimeOut",str(Assign[xx]))) #TimeOut
        #    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("BriefBy",str(Assign[xx]))) # BriefBy
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("ReviewBy",str(Assign[16]))) # ReviewBy

            SegArea_KM = Assign[18]
            SearchTime=Assign[19]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)
            TaskInstructions = "Task: {0}\n\nTask Area: {1} Acres, {2} sq KM\nTeam Cellphone: {3}".format(Assign[3], SegArea_Acres, SegArea_KM, TeamPh)
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TaskInstruct",str(TaskInstructions))) # TaskInstruct
            ## Resrouce Type
            txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamId",str(Assign[5]))) #TeamID
            txt.write("<</T(topmostSubform[0].Page2[0].{0}[0])/V({1})>>\n".format("TeamId",str(Assign[5]))) #TeamID
            try:
                txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format(Resource[Assign[6]],"1"))
            except:
                pass

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("TeamLead",str(key))) # Member
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("LeadResource",str('Team Leader'))) # LeadResource
                    txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("LeadSkill",str(TeamMember[key][2]))) # LeadSkill
                    kk+=1
                else:
                    txt.write("<</T(topmostSubform[0].Page1[0].Respond{0}[0])/V({1})>>\n".format(k,str(key))) # Member
                    txt.write("<</T(topmostSubform[0].Page1[0].Resource{0}[0])/V({1})>>\n".format(k,str(TeamMember[key][3]))) # Resource
                    txt.write("<</T(topmostSubform[0].Page1[0].Skill{0}[0])/V({1})>>\n".format(k,str(TeamMember[key][2]))) # Skill
                    k+=1
                if k>7:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        txt.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format("SearchTime",str(SearchTime))) # SearchTime

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

def Default_ASRC(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod):
    TAF2Use = 'TAF_Page1_Task.pdf'
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
