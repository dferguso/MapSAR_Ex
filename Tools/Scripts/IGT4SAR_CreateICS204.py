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
    sys
except NameError:
    import sys
##import time
from os import listdir, path
from datetime import datetime
from math import exp
import IGT4SAR_fdf

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
    fdfFields={}
    ## Incident Information
    if len(incidInfo) > 0:
        fdfFields['IncidentName']=str(incidInfo[0])
        fdfFields['MissNo']=str(incidInfo[1])
        fdfFields['Phone_Base']=str(incidInfo[5])

    ## Assignment Information
    SearchTime = 0
    assSafety = "None "
    opSafety = "None "

    if len(Assign)>0:
        SearchTime=Assign[19]
        fdfFields['OPPeriod']=str(Assign[2])
    if len(Assign[0])>1:
        fdfFields['TaskNo']=str(Assign[0])
    elif len(Assign[1])>1:
        fdfFields['TaskNo']=str(Assign[1])
        fdfFields['ResourceType']=str(Assign[6])
        fdfFields['Priority']=str(Assign[8])
        fdfFields['TaskMap']=str(Assign[10])
        fdfFields['TASKINSTRUCTIONS']=str(Assign[3])
        fdfFields['PrepBy']=str(Assign[16])
        fdfFields['DATE']=str(Assign[17])
        ################
        ## Team Infomration
        fdfFields['TeamId']=str(Assign[5])
        fdfFields['TeamId01']=str(Assign[5])
        assSafety= Assign[15]

    k=1
    kk=0
    if len(TeamMember)>0:
        for key in TeamMember:
            if key==Team[1]:
                fdfFields['TeamLead']=str(key)
                kk+=1
            elif key == Team[2]:
                fdfFields['Medic']=str(key)
                kk+=1
            else:
                team='Respond{0}'.format(k)
                fdfFields[team]=str(key)
                k+=1
            if k>12:
                break
    SearchTime = round(SearchTime/(k+kk),2)
    fdfFields['ExpectedDuration']=str(SearchTime) # SearchTime

    ## Operation Period Infomration
    if len(OpPeriod)>0:
        opSafety = OpPeriod[0]
        weaTher = OpPeriod[1]
        if len(OpPeriod[2])>1:
            fdfFields['Prim_Freq']=str(OpPeriod[2])
        elif len(incidInfo[6])>0:
            fdfFields['Prim_Freq']=str(incidInfo[6])
        fdfFields['BaseId']="BASE"

    if len(Team)>0:
        fdfFields['Phone_Team']=str(Team[3])

    Notes = "Specific Safety: {0}; General Safety: {1};  {2}".format(str(assSafety),str(opSafety),str(weaTher) )
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['Notes']=str(Notes)
    del Notes

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    IGT4SAR_fdf.create_fdf2(output, fName, TAF2Use, fdfFields, conCat=True)

    return

def MD_SP(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    fdfFields={}
    SearchTime = 0
    assSafety = "None "
    opSafety = "None "

    ## Incident Information
    if len(incidInfo)>0:
        fdfFields['Incident Name']=str(incidInfo[0])
        fdfFields['MAG DECLIN']=str(incidInfo[3])
        fdfFields['MAP DATUM']=str(incidInfo[2])
        fdfFields['MapCoord']=str(incidInfo[4])
        fdfFields['COMMAND POST']=str(incidInfo[5])
        ###################################
        try:
            fdfFields['USNGZone']=str(incidInfo[7])
            fdfFields['USNGGRID']=str(incidInfo[8])
        except:
            pass
    #################
    if len(OpPeriod)>0:
        if len(OpPeriod[2])>0:
            fdfFields['PRIMARY FREQ']=str(OpPeriod[2])
        elif len(incidInfo[6])>0:
            fdfFields['PRIMARY FREQ']=str(incidInfo[6])
        opSafety=OpPeriod[0]
        weaTher = OpPeriod[1]

    ## Assignment Information
    if len(Assign)>0:
        try:
            dateStamp = datetime.strftime(Assign[17], "%m/%d/%Y")
            timeStamp = datetime.strftime(Assign[17], "%H:%M %p")
        except:
            dateStamp = ""
            timeStamp = ""
        fdfFields['DATE']=str(dateStamp) # TaskDate

        fdfFields['Planning #']=str(Assign[1])
        fdfFields['TASK NO']=str(Assign[0])
        fdfFields['OPERATIONAL PERIOD']=str(Assign[2])
        fdfFields['ResourceType']=str(Assign[6])
        fdfFields['TYPE OF TEAM']=str(Assign[6])
        fdfFields['Priority']=str(Assign[8])

        SearchTime=Assign[19]
        SegArea_KM=Assign[18]
        SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
        SegArea_KM = round(SegArea_KM,3)

        fdfFields['TASK MAP']=str(Assign[10])
        fdfFields['Size Acres']="On"
        fdfFields['Acres']=str(SegArea_Acres)
        fdfFields['Size Sq. KM']="On"
        fdfFields['Sq KM']=str(SegArea_KM)
        fdfFields['PreSearch']=str(Assign[9])
        fdfFields['TASK INSTRUCTIONS']=str(Assign[3])
        fdfFields['DISPATCHER']=str(Assign[16])
        fdfFields['TEAM IDENTIFIER']=str(Assign[5])
        fdfFields['TEAM CALL SIGNID']=str(Assign[5])
        assSafety=Assign[15]
    ################

    ## Team Infomration
    if len(Team)>0:
        fdfFields['TEAM LEADERS CELL PHONE']=str(Team[3])

    k=1
    kk=0
    if len(TeamMember)>0:
        for key in TeamMember:
            if key==Team[1]:
                fdfFields['Team Leader']=str(key)
                fdfFields['TeamLeadAg']=str(TeamMember[key][1])
                kk+=1
            elif key == Team[2]:
                fdfFields['Team Medic']=str(key)
                fdfFields['MedicAg']=str(TeamMember[key][1])
                kk+=1
            else:
                team='Team Member {0}'.format(k)
                fdfFields[team]=str(key)
                teamAg='{0}Ag'.format(team)
                fdfFields[teamAg]=str(TeamMember[key][1]) # Agency
                k+=1
            if k>12:
                break
    SearchTime = round(SearchTime/(k+kk),2)
    fdfFields['EXPECTED TIME TO SEARCH']=str(SearchTime)

    ## Operation Period Infomration
    Notes = "Specific Safety: {0}; General Safety: {1};  {2}".format(str(assSafety),str(opSafety),str(weaTher) )
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['SAFETY COMMENTS']=str(Notes)
    del Notes

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    IGT4SAR_fdf.create_fdf2(output, fName, TAF2Use, fdfFields, conCat=True)

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

    fdfFields={}

    SearchTime = 0
    assSafety = "None "
    opSafety = "None "
    TeamPh = " "

    ## Incident Information
    if len(incidInfo)>0:
        fdfFields['Mission NumberRow1']=str(incidInfo[1]) # MissNo

    ## Operational Period Information
    if len(OpPeriod)>0:
        opSafety = OpPeriod[0]
        weaTher = OpPeriod[1]
        if len(OpPeriod[2])>0:
            fdfFields['Radio FrequencyRow1']=str(OpPeriod[2]) # TeamFreq
        elif len(incidInfo[6])>0:
            fdfFields['Radio FrequencyRow1']=str(incidInfo[6]) # TeamFreq

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

        assSafety= Assign[15]
        fdfFields['Operational PeriodRow1']=str(Assign[2]) # OpPeriod
        fdfFields['DateRow1']=str(dateStamp) # TaskDate
        fdfFields['Assignment DateRow1']=str(dateStamp) # DateOut
        fdfFields['EstimatedDeparture TimeRow1']=str(timeStamp) # EstTime
        fdfFields['Reviewed byRow1']=str(Assign[16]) # ReviewBy

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

            NMassign='Assignment and or Location in the FieldRow{0}'.format(txtRow)
            fdfFields[NMassign]=str(TaskInstructions[txtStart:txtEnd])

            txtStart=txtEnd
            txtEnd=min(txtStart+100,len(TaskInstructions))
            txtRow=txtRow+1

        ## Resrouce Type
        fdfFields['Team Number  Call SignRow1']=str(Assign[5]) #TeamID
        try:
            reSource = Resource[Assign[6]]
            fdfFields[reSource]="On"
        except:
            pass

    k=1
    kk=0
    if len(TeamMember)>0:
        for key in TeamMember:
            if key==Team[1]:
                fdfFields['Text1']=str(key) # Member
                fdfFields['Resource Name TL Comm Navigator1']=str('Team Leader') # LeadResource
                fdfFields['Skill  Equipment1']=str(TeamMember[key][2]) # LeadSkill
                kk+=1
            else:
                memName = 'Name{0}'.format(k+1)
                fdfFields[memName]=str(key) # Member
                resName ='Resource Name TL Comm Navigator{0}'.format(k+1)
                fdfFields[resName]=str(TeamMember[key][3]) # Resource
                skilEq = 'Skill Equipment{0}'.format(k+1)
                fdfFields[skilEq] = str(TeamMember[key][2]) # Skill
                k+=1
            if k>7:
                break
    SearchTime = round(SearchTime/(k+kk),2)
    fdfFields['Estimated Time in SegmentRow1']=str(SearchTime) # SearchTime

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    # Create .pdf
    IGT4SAR_fdf.create_fdf2(output, fName, TAF2Use, fdfFields, conCat=True)

    return

def MapSAR(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    fdfFields={}
    # Get current date and time from system
    now = datetime.now()
    todaydate = now.strftime("%m/%d/%Y")
    todaytime = now.strftime("%H:%M %p")

    SearchTime = 0
    assSafety = "None "
    opSafety = "None "
    phBase = " "
    phTeam = " "

    fdfFields['PrepDate']=todaydate
    fdfFields['PrepTime']=todaytime
    ## Incident Information
    if len(incidInfo) > 0:
        inCid = "{0} / {1}".format(str(incidInfo[0]),str(incidInfo[1]))
        mapDatum = str(incidInfo[2])
        magDec = str(incidInfo[3])
        mapCoord = str(incidInfo[4])
        phBase = str(incidInfo[5])
        baseFreq = "Base / {0}".format(str(incidInfo[6]))

        fdfFields['IncidentName']= inCid
        fdfFields['PrimaryComs']= baseFreq

     ## Operation Period Infomration
    #################
    if len(OpPeriod)>0:
        opSafety = OpPeriod[0]
        weaTher = OpPeriod[1]
        fdfFields['AssignTeamEquipment']= weaTher
        if len(OpPeriod[2])>0:
            primFreq = str(OpPeriod[2])
        elif len(incidInfo[6])>0:
            primFreq = str(incidInfo[6])
        else:
            primFreq = ''

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
            fdfFields['AssignmentNum']=str(Assign[0])
        else:
            fdfFields['AssignmentNum']=str(Assign[1])
        fdfFields['AssignTeam']=Assign[5]
        fdfFields['AssignPeriod']=str(Assign[2])
        fdfFields['StartDate']=str(dateStamp) # TaskDate
        fdfFields['TimeBeganAssign']=str(timeStamp) # TaskDate
        fdfFields['AssignDescription']=aSSignment
        fdfFields['TeamCallSign']=teamCall
        fdfFields['Assignlocation']=Assign[10]

        assSafety=Assign[15]

        fdfFields['PreparedBy']=str(Assign[16])
    ################

    if len(Team)>0:
        phTeam = str(Team[3])
    pertPh = "Base #: {0}; Team #: {1}".format(phBase, phTeam)
    fdfFields['PertinentPhoneNumbers']= pertPh

    Notes = "Specific Safety: {0}; General Safety: {1}".format(str(assSafety),str(opSafety))
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['AssignComInstructions']=str(Notes)
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
                tlRoll ="{0}.roll".format('Team Leader')
                fdfFields[tlRoll]=TeamMember[key][3]
                tlName ="{0}.name".format('Team Leader')
                fdfFields[tlName]=str(key)
                tlWeight="{0}.skillsandweight".format('Team Leader')
                fdfFields[tlWeight]=skillWght
                tlOrg ="{0}.origteam".format('Team Leader')
                fdfFields[tlOrg] = str(TeamMember[key][1]) # Agency
                kk+=1
            else:
                txt.write("<</T(Team Member.{0}.roll)/V({1})>>\n".format(k,TeamMember[key][3]))
                tlRoll ="Team Member.{0}.roll".format(k)
                fdfFields[tlRoll]=TeamMember[key][3]
                tlName ="Team Member.{0}.name".format(k)
                fdfFields[tlName]=str(key)
                tlWeight="Team Member.{0}.skillsandweight".format(k)
                fdfFields[tlWeight]=skillWght
                tlOrg ="Team Member.{0}.origteam".format(k)
                fdfFields[tlOrg] = str(TeamMember[key][1]) # Agency
                k+=1
            if k>6:
                break

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    # Create .pdf
    IGT4SAR_fdf.create_fdf2(output, fName, TAF2Use, fdfFields, conCat=True)

    return


def Arizona(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    fdfFields={}
    # Get current date and time from system
    now = datetime.now()
    todaydate = now.strftime("%m/%d/%Y")
    todaytime = now.strftime("%H:%M %p")
    PrepDate = "{0}\n{1}".format(todaydate, todaytime)

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
        else: primFreq=""
        fdfFields['TactFreq1'] = primFreq

    ## Assignment Information
    if len(Assign)>0:
        SearchSpd = Assign[20]
        SearchTime=Assign[19]
        fdfFields['ReturnTime']=round(SearchTime,3)
        SegArea_KM=Assign[18]
        SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
        SegArea_KM = round(SegArea_KM,3)

        ## Assume a sweep width of 20 m (0.02km)
        ##AddMessage("POD and # person required based on Coverage = 1 and Sweep Width = 20m\n")
        sTime = (float(SearchTime) * float(SearchSpd)*0.02)
        if sTime == 0:
            SearchNum = 0
        else:
            SearchNum = SegArea_KM/sTime
        areaSrch = SegArea_KM
        if areaSrch == 0:
            podREQ = 0
        else:
            podREQ = int((1-exp(-SegArea_KM/areaSrch))*100.0)

        mapName = "Map: {0}".format(str(Assign[10]))
        assignSize = "Acres: {0}; Sq KM: {1}".format(str(SegArea_Acres), str(SegArea_KM))
        preSearch = "Previously Search: {0}".format(str(Assign[9]))
        aSSignment = "{0}, {1}, {2}\n{3}".format(mapName, assignSize, preSearch, str(Assign[3]))

        allTime = datetime.strptime(str(Assign[17]), "%m/%d/%y %H:%M" )
        dateStamp = datetime.strftime(allTime, "%m/%d/%Y")
        timeStamp = datetime.strftime(allTime, "%H:%M %p")

        fdfFields['TASK']=str(Assign[0])
        fdfFields['TASK NAME']=Assign[10]
        fdfFields['AssignName']=str(Assign[1])
        fdfFields['TeamId']=Assign[5]
        fdfFields['OpPeriod']=str(Assign[2])
        fdfFields['PrepDate']=PrepDate
        fdfFields['TaskInstruct']=aSSignment
        fdfFields['PODreq']=str(podREQ)


        assSafety=Assign[15]

        fdfFields['PrepBy']=str(Assign[16])
    ################
    Notes = "Specific Safety: {0};  General Safety: {1};  {2}".format(str(assSafety),str(opSafety), str(weaTher) )
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['COMMENTS']=str(Notes)
    del Notes

    if len(Team)>0:
        phTeam = str(Team[3])
        fdfFields['CELL PHONE1']= phTeam

    k=1
    kk=0
    if len(TeamMember)>0:
        for key in TeamMember:
            if len(TeamMember[key][2])>1:
                skillWght = "{0}".format(TeamMember[key][2])
            else:
                skillWght = " "

            if key==Team[1]:
                fdfFields['MEMBER1']=str(key)
                fdfFields['CALL SIGN1']="Leader"
                fdfFields['SPECIAL SKILL']=skillWght
                kk+=1
            else:
                tMember="MEMBER{0}".format(k)
                fdfFields[tMember] = str(key)
                tSkill ="SPECIAL SKILL_{0}".format(k)
                fdfFields[tSkill]=skillWght
                k+=1
            if k>6:
                break

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    IGT4SAR_fdf.create_fdf2(output, fName, TAF2Use, fdfFields, conCat=True)

    return

def BASARC(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    fdfFields={}

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
        fdfFields['incidentName']=str(incidName)
        fdfFields['other_radio_chan']="Base Phone"
        fdfFields['freqOther']=str(incidInfo[5])
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

        fdfFields['opPeriod']=str(Assign[2])
        fdfFields['assignNumber']=TaskID
        fdfFields['resource_type']=Assign[6]
        fdfFields['asgn_description']=aSSignment
        fdfFields['previous_search_effort']=preSearch
        fdfFields['radio_call']=Assign[5]
        fdfFields['date_prepared']= todaydate
        fdfFields['time_prepared']= todaytime
        fdfFields['prepared_by']=str(Assign[16])

        SearchSpd = Assign[20]
        SearchTime=Assign[19]
        SegArea_KM=Assign[18]
        SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
        SegArea_KM = round(SegArea_KM,3)
        assignSize = "{0}Acres; {1}sqKM".format(str(SegArea_Acres), str(SegArea_KM))
        fdfFields['size_of_assignment']= assignSize

        assSafety= Assign[15]

    k=1
    if len(TeamMember)>0:
        for key in TeamMember:
            tmName ="PersonnelName_{0}".format(k)
            fdfFields[tmName]=str(key)
            tmAgency ="PersonnelAgency_{0}".format(k)
            fdfFields[tmAgency]=str(TeamMember[key][1])
            tmFunc ="PersonnelFunction_{0}".format(k)
            if key==Team[1]:
                fdfFields[tmFunc] = "L"
            elif key == Team[2]:
                fdfFields[tmFunc] = "M"
            k+=1
            if k>9:
                break
    SearchTime = round(SearchTime/(k),2)
    fdfFields["TimeAllocated"]="{0} hrs".format(str(SearchTime)) # SearchTime

    ## Operation Period Infomration
    if len(OpPeriod)>0:
        opSafety = OpPeriod[0]
        weaTher = OpPeriod[1]
        if len(OpPeriod[2])>1:
            fdfFields['freqCommand']=str(OpPeriod[2])
            fdfFields['freqTactical']=str(OpPeriod[2])
        elif len(incidInfo[6])>0:
            fdfFields['freqCommand']=str(incidInfo[6])
            fdfFields['freqTactical']=str(incidInfo[6])

    Notes = "Specific Safety: {0};  General Safety: {1};  {2}".format(str(assSafety),str(opSafety), str(weaTher) )
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['notes']=str(Notes)

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    IGT4SAR_fdf.create_fdf(output, fName, TAF2Use, fdfFields, conCat=True)

    return


def Tyler_County(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod,TAF2Use):
    fdfFields={}

    SearchTime = 0
    assSafety = "None "
    opSafety = "None "
    phBase = " "
    phTeam = " "
    ## Incident Information
    Incid = "{0}\n{1}".format(incidInfo[0],incidInfo[1])
    fdfFields['IncidentName']=Incid
    fdfFields['BasePhone']=str(incidInfo[5])

    ## Operation Period Infomration
    #################
    if len(OpPeriod)>0:
        opSafety = OpPeriod[0]
        weaTher = OpPeriod[1]
        primFreq = str(OpPeriod[2])
        if len(OpPeriod[2])>0:
            primFreq = str(OpPeriod[2])
        elif len(incidInfo[6])>0:
            primFreq = str(incidInfo[6])
        fdfFields['FrequencyChannel']= primFreq
        fdfFields['PredictedWeather']=str(weaTher)

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

        fdfFields['AssignLocation']=Assign[10]
        fdfFields['OpPeriod']=str(Assign[2])
        fdfFields['TaskNumber']=TaskID
        fdfFields['TeamId']=Assign[5]
        fdfFields['BaseCallSign']="Base"
        fdfFields['TeamCallSign']=Assign[5]
        fdfFields['ResourceType']=str(Assign[6])
        fdfFields['PrepBy']=str(Assign[16])
        fdfFields['TaskInstruct']=aSSignment

        assSafety=Assign[15]

     ################
    Notes = "Specific Safety: {0};  General Safety: {1}".format(str(assSafety),str(opSafety))
    Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
    fdfFields['SafetyPrecautions']=str(Notes)
    del Notes

    if len(Team)>0:
        phTeam = str(Team[3])
        fdfFields['TeamPhone']= phTeam

    k=1
    kk=0
    if len(TeamMember)>0:
        for key in TeamMember:
            tmName ="TeamMembersName_{0}".formatt(k)
            fdfFields[tmName]=str(key)
            tmAgency ="Agency_{0}".format(k)
            fdfFields[tmAgency]=str(TeamMember[key][1])
            k+=1
            if k>10:
                break

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    # Create .pdf
    IGT4SAR_fdf.create_fdf(output, fName, TAF2Use, fdfFields, conCat=True)

    return

def Default(Assign, Team, TeamMember, AssNum, incidInfo, output, OpPeriod, TAF2Use):
    fdfFields={}
    if TAF2Use in listdir(output):
        AssNumber="{0}{1}".format(AssNum,"_TAF.fdf")
        fileName = path.join(output,str(AssNumber))
        tafPath=path.join(output,TAF2Use)

        SearchTime = 0
        assSafety = "None "
        opSafety = "None "

        ## Incident Information
        if len(incidInfo) > 0:
            fdfFields['MissNo']=str(incidInfo[1])
            fdfFields['MagDec']=str(incidInfo[3])
            fdfFields['MapDatum']=str(incidInfo[2])
            fdfFields['MapCoord']=str(incidInfo[4])
            fdfFields['Phone_Base']=str(incidInfo[5])
            ###################################
            try:
                fdfFields['UTMZONE']=str(incidInfo[7])
                fdfFields['USNGGRID']=str(incidInfo[8])
            except:
                pass
            #################
        ## Assignment Information
        if len(Assign)>0:
            SegArea_KM=Assign[18]
            SearchTime=Assign[19]
            SegArea_Acres = round((SegArea_KM * 247.104393),2) # Convert km**2 to Acres
            SegArea_KM = round(SegArea_KM,3)

            fdfFields['TaskNo']=str(Assign[0])
            fdfFields['PlanNo']=str(Assign[1])
            fdfFields['ResourceType']=str(Assign[6])
            fdfFields['Priority']=str(Assign[8])
            fdfFields['TaskMap']=str(Assign[10])
            fdfFields['PreSearch']=str(Assign[9])

            fdfFields['TaskInstruct']=str(Assign[3])
            fdfFields['SegArea_Acres']=str(SegArea_Acres)
            fdfFields['SegArea_KM']=str(SegArea_KM)
            fdfFields['PrepBy']=str(Assign[16])
            ################
            ## Team Infomration
            fdfFields['TeamId']=str(Assign[5])
            fdfFields['TaskId']=str(Assign[5])
            assSafety= Assign[15]

        k=1
        kk=0
        if len(TeamMember)>0:
            for key in TeamMember:
                if key==Team[1]:
                    fdfFields['TeamLead']=str(key)
                    fdfFields['TeamLeadAg']=str(TeamMember[key][1]) # Agency
                    kk+=1
                elif key == Team[2]:
                    fdfFields['Medic']=str(key)
                    fdfFields['MedicAg']=str(TeamMember[key][1]) # Agency
                    kk+=1
                else:
                    team='Respond{0}'.format(k)
                    fdfFields[team]=str(key)
                    teamAg='{0}Ag[0]'.format(team)
                    fdfFields[teamAg]=str(TeamMember[key][1]) # Agency
                    k+=1
                if k>12:
                    break
        SearchTime = round(SearchTime/(k+kk),2)
        fdfFields['SearchTime']=str(SearchTime) # SearchTime

        ## Operation Period Infomration
        if len(OpPeriod)>0:
            opSafety = OpPeriod[0]
            weaTher = OpPeriod[1]
            if len(OpPeriod[2])>1:
                fdfFields['TeamFreq']=str(OpPeriod[2])
            elif len(incidInfo[6])>0:
                fdfFields['TeamFreq']=str(incidInfo[6])

        if len(Team)>0:
            fdfFields['Phone_Team']=str(Team[3])

        Notes = "Specific Safety: {0}; General Safety: {1};  {2}".format(str(assSafety),str(opSafety),str(weaTher) )
        Notes = "\n".join(Notes.splitlines()) # os-specific newline conversion
        fdfFields['Notes']=str(Notes)

    ##CREATE THE TAF in fdf than pdf
    fName = "{0}_TAF.fdf".format(str(AssNum))
    IGT4SAR_fdf.create_fdf(output, fName, TAF2Use, fdfFields, conCat=True)

    return

if __name__ == '__main__':
    CreateICS204(Assign, Team, TeamMember, AssNum, incidInfo, IncidIdx, output, OpPeriod)
