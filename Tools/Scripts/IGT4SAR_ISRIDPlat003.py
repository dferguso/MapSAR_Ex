#-------------------------------------------------------------------------------
# Name:        ISRIDPlat.py
# Purpose:   This tool is intended to be used to populate the ISRID platinum
#  data collection form.
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
# Copyright:   (c) Don Ferguson 2012
# License:
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
#------------------------------------------------------------------------------
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

from datetime import datetime

####################################################################################
'''  DELETE THESE WHEN FINISHED
userInfo={'PreparedBy':PreparedBy,'OrgEditor':OrgEditor,'OrigEmail':OrigEmail,'OrigPhone':OrigPhone,\
          'output':output, 'primSubject':primSubject, 'ippType':ippType, 'DateEntered':todaydate}

siFields = ['Subject_Number','Category','Group_Size','Gender','Height',\
           'Weight','Build','Complexion','Hair','Eyes','Other','Shirt',\
           'Pants','Jacket','Hat','Footwear','Info','Cellphone','Photo_Available',\
           'Age','WhereLastSeen','Race','Date_Seen','Time_Seen','QRCode',\
           'Experience','Fitness_Level','Category_MRA']

ippFields = ['Incident_Name','IPPClass','UTM_E','UTM_N','Latitude','Longitude',\
          'IPPType','Subject_Number','DESCRIPTION']

inFields = ['Incident_Number','Incident_Name','Environment','Eco_Region',\
            'Pop_Den','Terrain','LandCover','LandOwner','Comms_Freq','Base_PhoneNumber',\
            'MagDec','Lead_Agency','Incident_Type','MapDatum','USNG_GRID',\
            'MapCoord','UTM_ZONE','ICS204','IncidSummary']

opFields =['Start_Date','End_Date','Temp_Max','Temp_Min','Light','Safety_Message',\
           'Primary_Comm','Emergency_Comm','Lead_Agency','SAR_Manager','Planning_Chief',\
           'Operations_Chief','Air_Operations_Chief','Logistics_Chief','Transportation_Chief',\
           'Finance_Chief','Safety_Offc','Information_Offc','Family_lias','Op_Objectives',\
           'Rain','Snow','Period','Weather','Wind', 'Weather_Gen']

fdFields =['Subject_Number','Date_Time','Suspension','Status','Scenario','Description',\
        'Rescue_Method','UTM_Easting','UTM_Northing','Latitude','Longitude',\
        'Injury_Type','Illness_Type','Mechanism','Treatment','Detectibility',\
        'Mobility_Response','Mobility_hrs','Lost_Strategy','Intended_Destination',\
        'ID_UTM_Easting','ID_UTM_Northing','ID_Latitude','ID_Longitude',
        'How_Found','Aircraft_Used','Contact_Method','Med_Aid']

leFields=['Lead_Agency','Responsible_Auth','Lead_Phone','Lead_Address','Lead_City',\
          'Lead_State','E_Mail','Lead_Zip']

'''
#########################################################################
# Environment variables
wrkspc=arcpy.env.workspace
arcpy.env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"
#########################################################################

def getDataframe():
    ## Get current mxd and dataframe
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT'); df = arcpy.mapping.ListDataFrames(mxd)[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def ISRIDFile(siData,ippDict, inDict,opDict, fdData, leDict, userInfo):
    isRid={'Lead':leDict['Lead_Agency'],
           'IncNum':inDict['Incident_Name'],
           'MisNum':inDict['Incidet_Number'],
           'Incdate':str(opDict['Start_Date']),
           'IncTyp':inDict['Incident_Type'],
           'Prepared':str(userInfo['PreparedBy']),
           'Org':str(userInfo['OrgEditor']),
           'Email':str(userInfo['OrigEmail']),
           'Phone':str(userInfo['OrigPhone']),
           'IncEnv':inDict['Environment'],
           'CtyReg':leDict['Lead_City'],
           'State':leDict['Lead_State'],
           'EcoDom':inDict['Eco_Region'],
           'Pop':inDict['Pop_Den'],
           'Ter':inDict['Terrain'],
           'Cover':inDict['LandCover'],
           'Owner':inDict['LandOwner'],
           'Wx':opDict['Weather_Gen'],
           'Rain':opDict['Rain'],
           'Snow':opDict['Snow'],
           'Light':opDict['Light'],
           'IPPFmt':'DD',
           'IPPClass':ippDict['IPPClass'],
           'IPPLat':ippDict['Latitude'],
           'IPPLong':ippDict['Longitude']}


##           isrid={'SF':'','IClosed':'','TTL':'','TST':'','TLSdate':'','TLSTime':'',\
##           'SARNotTime':'','SubFoundTime':'','ClosedTime':'','CntMtd':'','DesLong':'',\
##           'DesLat':'','DesFmt':'','RPLSFmt':'','RPLSLat':'','RPLSLong':'','DECLat':'',\
##           'DECLong':'','DECFmt':'','DOT':'','DOThow':'','RevPLS':'','DECTyp':'',\
##           'RevDOT':'','Dec':'','Comment':'','Outcm':'','Scen':'','Susp':'','SubjNum':'',\
##           'Well':'','Inj':'','DOA':'','Saves':'','FFmt':'','FLong':'','FLat':'','DisIPP':'',\
##           'Ffeat':'','Ffeat2':'','Det':'','MobRes':'','Strat':'','Mob':'','TrkOff':'',\
##           'ElvFt':'','BFnd':'','SrchInj':'','SrchInjDet':'','Tasks':'','VehNum':'',\
##           'Peop':'','MilesDrv':'','Cost':'','Manhrs':'','DogNum':'', 'AirNum':'','AirTsk':'',\
##           'AirHrs':'','FndRes':'','EVol':'','Peop':'','Manhrs':'','VehNum':'','MilesDrv':'',\
##           'Cost':'','AirHrs':'','AirNum':'','AirTsk':'','DogNum':'','Tasks':'','Elv':'',\
##           'Sig':'','Aeromedical':'','Helicopter':'','Swiftwater':'','Boat':'','Vehicle':'',\
##           'Technical':'','SemiTech':'','Carryout':'','Walkout':'','Other':'','OtherRescue':'',\
##           'Swiftwater':'','USARCert':'','FixedWing':'','Helo':'','Parks':'','Cave':'','Boats':'',\
##           'Divers':'','Law':'','Tracker':'','CheckBox3':'', 'EMS':'', 'Dogs':'','TextField1':'',
##           'GSAR':''}
##
##           'TSN':'','InciTimeRp':'','SubCat':'','SubCatSub':'', 'SubAct':'','EcoDiv':'',
##
##           ['Age','Sex','Local','Wgt','Hgt','Bld','Fit','Exp','Eq','Cl','Sur','Mnt']
##           'GrpTyp':'',
##           ['Status','Mech','Inj','Ill','Tx']
##
##            if opDict['Snow'] != 'None' or opDict['Snow'] != 'Drizzle':
##                isRid['SnowGrd']='Yes'
##
##
##    filename = output + "/" + str(args[List_elements[1]]) + "_ISRID.fdf"
##
##    txt= open (filename, "w")
##    txt.write("%FDF-1.2\n")
##    txt.write("%????\n")
##    txt.write("1 0 obj<</FDF<</F(ISRID_Data_Form.pdf)/Fields 2 0 R>>>>\n")
##    txt.write("endobj\n")
##    txt.write("2 0 obj[\n")
##
##    txt.write ("\n")
##
##    for elems in List_elements:
##        if argNum < 94:
##            txt.write("<</T(form1[0].#subform[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
##        elif 94 <= argNum <= 174:
##            txt.write("<</T(form1[0].#subform[6]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
##        elif argNum == 175:
##            txt.write("<</T(form1[0].#subform[6].Subform2[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
##        elif 175 < argNum <= 187:
##            txt.write("<</T(form1[0].#subform[6].Subform3[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
##        else:
##            txt.write("<</T(form1[0].#subform[6].Subform4[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
##        argNum+=1
##
##    txt.write("]\n")
##    txt.write("endobj\n")
##    txt.write("trailer\n")
##    txt.write("<</Root 1 0 R>>\n")
##    txt.write("%%EO\n")
##    txt.close ()
    return()

def MRA_Data(siData,ippDict, inDict,opDict, fdData, leDict, userInfo):

    ippLocation = 'Lat: {0}, Long:{1} - {2}'.format(ippDict['Latitude'],ippDict['Longitude'],ippDict['DESCRIPTION'])
    xy = [ippDict['Longitude'],ippDict['Latitude']]
##
##    missionFields=['Number','Type','Team','Date','In_County','Number_Personel','Total_Hours',\
##               'Number_Subjects','Gender_Sub_1','Age_Sub_1','Fitness_Sub_1','Experience_Sub_1',\
##               'Category','Area_Type','Land_Ownership','IPP_Location','Mental_Rating',\
##               'How_Found','Number_Well','Number_DOA','Number_Injured','Number_Not_Found',\
##               'Subject_Injury','Rescuer_Injury','Aircraft','Aircraft_Type_1','Aircraft_Type_2',\
##               'Aircraft_Type_3','Comments','GlobalID','CreationDate','Creator','EditDate',\
##               'Editor','Gender_Sub_2','Gender_Sub_3','Gender_Sub_4','Gender_Sub_5','Age_Sub_2',\
##               'Age_Sub_3','Age_Sub_4','Age_Sub_5','Fitness_Sub_2','Fitness_Sub_3','Fitness_Sub_4',\
##               'Fitness_Sub_5','Experience_Sub_2','Experience_Sub_3','Experience_Sub_4',\
##               'Experience_Sub_5','Mental_Factor']


##    fFields = ['Mission_Number','Subject_Number','Found_Location','Found_Date','Detectability',\
##               'Signaling','Comments','GlobalID','CreationDate','Creator','EditDate','Editor']
##

    mFields={'Number':inDict['Incident_Number'],'Type':inDict['Incident_Type'],'Team':userInfo['OrgEditor'],\
             'Date':opDict['Start_Date'],'Area_Type':inDictct['Pop_Den'],'Land_Ownership':inDict['LandOwner'],\
             'IPP_Location':ippLocation,'How_Found':fdDict['How_found'],'Comments':inDict['IncidSummary'],\
             'CreationDate':userInfo['DateEntered'],'Creator':userInfo['PreparedBy']}

    siList=['Gender_Sub_', 'Age_Sub_','Fitness_Sub_','Experience_Sub_']
    mFactor={'Autistic':'AUTISM', 'Dementia':'ALZHEIMERS/DEMENTIA', 'Mental retardation':'INTELLECTUAL DISABILITY',\
             'Mental Illness':'MENTAL ILLNESS','Substance Abuse':'SUBSTANCE INTOXICATION'}
    k=0
    for si  in siData:
        k+=1
        if k<5:
            mFields['Gender_Sub_'+str(k)] = si[3]
            mFields['Age_Sub_'+str(k)] = si[19]
            mFields['Fitness_Sub_'+str(k)] = si[26]
            mFields['Experience_Sub_'+str(k)] = si[25]
            mFields['Number_Subjects']=k
            if k==userInfo['primSubject']:
                mFields['Category']=si[27]
                mFields['Mental_Rating']=si[27]
                if si[1] in mFactor:
                    mFields['Mental_Factor']=mFactor[si[1]]
                else:
                    mFields['Mental_Factor']='NONE'

            else:
                break

    st0 = 0  #not found counter
    st1 = 0  #Status 1 Counter
    st2 = 0  #Status 2 Counter
    st3 = 0  #Status 3 Counter

    for fi in fdData:
        if fi[3] == 'Well':
            st1+=1
        elif fi[3] == 'Injured':
            st2+=1
        elif fi[3] == 'DOA':
            st3+=1
        else:
            st0+=1
        if fi[1]==1:
            mFields['Subject_Injury']=fi[27]

    mFields['Number_Not_Found']=st0
    mFields['Number_Well']=st1
    mFields['Number_Injured']=st2
    mFields['Number_DOA']=st3
    mFields['Number_Personel'] = userInfo['Number_Personel']

    cursor = arcpy.InsertCursor("Mission_MRA")

    cursor = arcpy.InsertCursor("Found_MRA")
    for fd in fdData:
        row = cursor.newRow()
        pnt = arcpy.Point(fdData[10],fdData[9])
        row.shape = pnt
        fdLocation = 'Lat: {0}, Long:{1} - {2}'.format(fdData[9],fdData[10],fdData[5])
        row.setValue('Mission_Number',inDict['Incident_Number'])
        row.setValue('Subject_Number',fd[0])
        row.setValue('Found_Location',fdLocation)
        row.setValue('Found_Date',fd[1])
        row.setValue('Detectability',fd[16])
        row.setValue('Signaling',fd[26])
        row.setValue('CreationDate',userInfo['DateEntered'])
        row.setValue('Creator',userInfo['PreparedBy'])
        cursor.insertRow(row)

def getFeatData(fc,fieldList):
    fldMatrix=[]
    fldNames = [f.name for f in arcpy.ListFields(fc)]
    cursor = arcpy.SearchCursor(fc)
    for row in cursor:
        fldData=[]
        for fld in fieldList:
            if fld in fldNames:
                chkData=row.getValue(fld)
                if chkData:
                    fldData.append(chkData)
                else:
                    fldData.append('')
            else:
                fldData.append('')
        fldMatrix.append(fldData)
    return(fldMatrix)

########
# Main Program starts here
#######

if __name__ == '__main__':
    output = arcpy.GetParameterAsText(0)
    primSubject = arcpy.GetParameterAsText(1)
    ippType = arcpy.GetParameterAsText(2)
    PreparedBy = arcpy.GetParameterAsText(3)
    OrgEditor = arcpy.GetParameterAsText(4)
    OrigEmail = arcpy.GetParameterAsText(5)
    OrigPhone = arcpy.GetParameterAsText(6)

    fc1 = "Subject Information" #Subject_Information
    fc2 = "Planning Point"  #Plan_Point
    fc3 = "Incident_Information"
    fc4 = "Operation_Period"
    fc5 = "Found"
    fc6 = 'Lead_Agency'
    fc7 = 'Incident_Staff'
    fc8 = 'Team_Members'

    now = datetime.now()
    todaydate = now.strftime("%m/%d/%Y")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    result = arcpy.GetCount_management(fc7)
    staffCount = int(result.getOutput(0))

    result = arcpy.GetCount_management(fc8)
    teamCount = int(result.getOutput(0))

    totalPersonnel = staffCount + teamCount

    userInfo={'PreparedBy':PreparedBy,'OrgEditor':OrgEditor,'OrigEmail':OrigEmail,'OrigPhone':OrigPhone,\
              'output':output, 'primSubject':primSubject, 'ippType':ippType, 'DateEntered':todaydate,\
              'Number_Personel':totalPersonnel}

    siFields = ['Subject_Number','Category','Group_Size','Gender','Height',\
               'Weight','Build','Complexion','Hair','Eyes','Other','Shirt',\
               'Pants','Jacket','Hat','Footwear','Info','Cellphone','Photo_Available',\
               'Age','WhereLastSeen','Race','Date_Seen','Time_Seen','QRCode',\
               'Experience','Fitness_Level','Category_MRA']

    ippFields = ['Incident_Name','IPPClass','UTM_E','UTM_N','Latitude','Longitude',\
              'IPPType','Subject_Number','DESCRIPTION']

    inFields = ['Incident_Number','Incident_Name','Environment','Eco_Region',\
                'Pop_Den','Terrain','LandCover','LandOwner','Comms_Freq','Base_PhoneNumber',\
                'MagDec','Lead_Agency','Incident_Type','MapDatum','USNG_GRID',\
                'MapCoord','UTM_ZONE','ICS204','IncidSummary']

    opFields =['Start_Date','End_Date','Temp_Max','Temp_Min','Light','Safety_Message',\
               'Primary_Comm','Emergency_Comm','Lead_Agency','SAR_Manager','Planning_Chief',\
               'Operations_Chief','Air_Operations_Chief','Logistics_Chief','Transportation_Chief',\
               'Finance_Chief','Safety_Offc','Information_Offc','Family_lias','Op_Objectives',\
               'Rain','Snow','Period','Weather','Wind', 'Weather_Gen']

    fdFields =['Subject_Number','Date_Time','Suspension','Status','Scenario','Description',\
            'Rescue_Method','UTM_Easting','UTM_Northing','Latitude','Longitude',\
            'Injury_Type','Illness_Type','Mechanism','Treatment','Detectibility',\
            'Mobility_Response','Mobility_hrs','Lost_Strategy','Intended_Destination',\
            'ID_UTM_Easting','ID_UTM_Northing','ID_Latitude','ID_Longitude',
            'How_Found','Aircraft_Used','Contact_Method','Med_Aid']

    leFields=['Lead_Agency','Responsible_Auth','Lead_Phone','Lead_Address','Lead_City',\
              'Lead_State','E_Mail','Lead_Zip']

    siData = getFeatData(fc1,siFields)
    fdData = getFeatData(fc5,fdFields)

    ippData = getFeatData(fc2,ippFields)
    ippDict={}
    for ip in ippData:
        k=0
        if ip[6]==ippType and ip[7]==primSubject:
            for ipp in ippFields:
                ipDict[ipp] = ip[k]
                k+=1

    inData = getFeatData(fc3,inFields)
    inDict={}
    k=0
    Incident = inData[-1]
    for inIndx in inFields:
        inDict[inIndx]=Incident[k]
        k+=1

    opData = getFeatData(fc4,opFields)
    opDict={}
    k=0
    opPeriod = opData[-1]
    for op in opFields:
        opDict[op]=opPeriod[k]
        k+=1

    leData = getFeatData(fc6,leFields)
    leDict={}
    k=0
    LegalAg = leData[-1]
    for lg in leFields:
        leDict[lg]=LegalAg[k]
        k+=1

    MRA_Data(siData,ippDict, inDict,opDict, fdData, leDict, userInfo)
##
##
##
##
##
##    while row:
##        # you need to insert correct field names in your getvalberue function
##        LE['IncNum'] = row.getValue("Incident_Name")
##        LE['MisNum'] = row.getValue("Incident_Number")
##        LE['IncType'] = row.getValue("Incident_Type")
##        LE['IncEnv'] = row.getValue("Environment")
##        LE['EcoDom'] = row.getValue("Eco_Region")
##        LE['Pop'] = row.getValue("Pop_Den")
##        LE['Ter'] = row.getValue("Terrain")
##        LE['Cover'] = row.getValue("LandCover")
##        LE['Owner'] = row.getValue("LandOwner")
##        MapDatum = row.getValue("MapDatum")
##        MapCoord = row.getValue("MapCoord")
##        MagDec = row.getValue("MagDec")
##
##
##        LE['Lead'] = row.getValue("Lead_Agency")
##
##
##        where2 = '"Lead_Agency" = ' + "'" + LE['Lead'] + "'"
##        arcpy.AddMessage(where2)
##        rows2 = arcpy.SearchCursor(fc2, where2)
##        row2 = rows2.next()
##
##        while row2:
##            # you need to insert correct field names in your getvalue function
##            LE['CtyReg'] = row2.getValue("Lead_City")
##            LE['State'] = row2.getValue("Lead_State")
##            row2 = rows2.next()
##        del rows2
##        del row2
##
##        row = rows.next()
##    del rows
##    del row
##
##
##    fc2="Operation_Period"
##    rows = arcpy.SearchCursor(fc2)
##    row = rows.next()
##
##    while row:
##        # you need to insert correct field names in your getvalue function
##        Start_Date = row.getValue("Start_Date")
##        End_Date = row.getValue("End_Date")
##        LE['Wx'] = row.getValue("Weather")
##        LE['Tmax'] = row.getValue("Temp_max")
##        LE['Tmin'] = row.getValue("Temp_min")
##        LE['Wind'] = row.getValue("Wind")
##        LE['Rain'] = row.getValue("Rain")
##        LE['SnowGrd'] = row.getValue("Snow")
##        LE['Light'] = row.getValue("Light")
##        row = rows.next()
##    del rows
##    del row
##
##
#### Subject Information, IPP and Find
##    Age_All=[]
##    Hgt_All=[]
##    Wgt_All=[]
##    Gender_All =[]
##    Status_All = []
##    Mechanism_All = []
##    Treatment_All = []
##    Illness_All = []
##    Injury_All = []
##    Bld_All = []
##    Susp =""
##    Status =''
##    Mechanism =""
##    Treatment =''
##    Illness =''
##    Injury =''
##
##    fc1="Subject_Information"
##    fc2="Plan_Point"
##    fc3 = "Found"
##
##    where2 = '"IPPType" = ' + "'" + IPPType + "'"
##
##    rows = arcpy.SearchCursor(fc1)
##    row = rows.next()
##    while row:
##        # you need to insert correct field names in your getvalue function
##        SubNum = row.getValue("Subject_Number")
##        where3 = '"Subject_Number" = ' + "'" + str(SubNum) + "'"
##
##        try:
##            fDate = row.getValue("Date_Seen")
##            LE['Incdate'] = fDate.strftime("%m/%d/%Y")
##        except:
##            LE['Incdate'] = " "
##
##        try:
##            LE['InciTimeRp'] = row.getValue("Time_Seen")
##        except:
##            LE['InciTimeRp'] = " "
##        LE['Where_Last'] = row.getValue("WhereLastSeen")
##
##
##        Age = [row.getValue("Age")]
##        Gender = [row.getValue("Gender")]
##        Race = [row.getValue("Race")]
##        try:
##            Hgt = [(row.getValue("Height"))/12.0]
##        except:
##            Hgt = ""
##        Wgt = [row.getValue("Weight")]
##        Bld = [row.getValue("Build")]
##        LE['SubCat'] = [row.getValue("Category")]
##        LE['SubCatSub']= ''
##        LE['SubAct']= ''
####################################################
##
##        arcpy.AddMessage(where2)
##        rows2 = arcpy.SearchCursor(fc2, where2)
##        row2 = rows2.next()
##
##        while row2:
##            # you need to insert correct field names in your getvalue function
##            LE['IPPClass'] = row2.getValue("IPPClass")
##            LE['IPPFmt']= 'DD'
##            LE['IPPLat'] = row2.getValue("Latitude")
##            LE['IPPLong'] = row2.getValue("Longitude")
##
##            try:
##                rows3 = arcpy.SearchCursor(fc3, where3)
##                row3 = rows3.next()
##                while row2:
##                    Susp =row.getValue("Suspension")
##                    Status =[row.getValue("Status")]
##                    Mechanism =[row.getValue("Mechanism")]
##                    Treatment =[row.getValue("Treatment")]
##                    Illness =[row.getValue("Illness_Type")]
##                    Injury =[row.getValue("Injury_Type")]
##
##                    LE['Comment']=row.getValue("Description")
##                    LE['Scen'] =row.getValue("Scenario")
##                    LE['Ffeat'] = ""
##                    LE['Ffeat2'] = ""
##                    LE['FFmt'] = 'DD'
##                    LE['FLat'] = row2.getValue("Latitude")
##                    LE['FLong'] = row2.getValue("Longitude")
##                    LE['Det'] = row2.getValue("Detectibility")
##                    LE['MobRes'] = row2.getValue("Mobility_Response")
##
##                    try:
##                        fDate = row.getValue("Date_Time")
##                        LE['SF'] = fDate.strftime("%m/%d/%Y")
##                    except:
##                        LE['SF'] = " "
##                    try:
##                        LE['SubFoundTime'] = row.getValue("Date_Time")
##                    except:
##                        LE['SubFoundTime'] = " "
##            except:
##                pass
##
##            row2 = rows2.next()
##        del rows2
##        del row2
##        del fc2
##
#####################################################
##        Age_All.append(Age)
##        Gender_All.append(Gender)
##        Wgt_All.append(Wgt)
##        Hgt_All.append(Hgt)
##        Status_All.append(Status)
##        Mechanism_All.append(Mechanism)
##        Treatment_All.append(Treatment)
##        Illness_All.append(Illness)
##        Injury_All.append(Injury)
##        Bld_All.append(Bld)
##
##
##        row = rows.next()
##
##    del rows
##    del row
##    del fc1
##    lengh = len(Age_All)
##    LE['SubjNum'] = lengh
##    LE['Outcm']=''
##    LE['Well'] = ''
##    LE['Inj'] = ''
##    LE['DOA'] = ''
##    LE['Saves'] = ''
##    k=0
##    while k<=lengh-1:
##        if k ==0:
##            arcpy.AddMessage(Status_All[k])
##            LE['Age1'] = str(Age_All[k])
##            LE['Sex1'] = Gender_All[k]
##            LE['Wgt1'] = Wgt_All[k]
##            LE['Hgt1'] = Hgt_All[k]
##            LE['Bld1'] = Bld_All[k]
##            LE['Status1'] = Status_All[k]
##            LE['Mech1'] = Mechanism_All[k]
##            LE['Inj1'] = Injury_All[k]
##            LE['Ill1'] = Illness_All[k]
##            LE['Tx1'] = Treatment_All[k]
##            LE['Local1'] = ''
##            LE['Fit1'] = ''
##            LE['Exp1'] = ''
##            LE['Eq1'] = ''
##            LE['Cl1'] = ''
##            LE['Sur1'] = ''
##            LE['Mnt1'] = ''
##
##        elif k ==1:
##            LE['Age2'] = Age_All[k]
##            LE['Sex2'] = Gender_All[k]
##            LE['Wgt2'] = Wgt_All[k]
##            LE['Hgt2'] = Hgt_All[k]
##            LE['Bld2'] = Bld_All[k]
##            LE['Status2'] = Status_All[k]
##            LE['Mech2'] = Mechanism_All[k]
##            LE['Inj2'] = Injury_All[k]
##            LE['Ill2'] = Illness_All[k]
##            LE['Tx2'] = Treatment_All[k]
##            LE['Local2'] = ''
##            LE['Fit2'] = ''
##            LE['Exp2'] = ''
##            LE['Eq2'] = ''
##            LE['Cl2'] = ''
##            LE['Sur2'] = ''
##            LE['Mnt2'] = ''
##        elif k ==2:
##            LE['Age3'] = Age_All[k]
##            LE['Sex3'] = Gender_All[k]
##            LE['Wgt3'] = Wgt_All[k]
##            LE['Hgt3'] = Hgt_All[k]
##            LE['Bld3'] = Bld_All[k]
##            LE['Status3'] = Status_All[k]
##            LE['Mech3'] = Mechanism_All[k]
##            LE['Inj3'] = Injury_All[k]
##            LE['Ill3'] = Illness_All[k]
##            LE['Tx3'] = Treatment_All[k]
##            LE['Local3'] = ''
##            LE['Fit3'] = ''
##            LE['Exp3'] = ''
##            LE['Eq3'] = ''
##            LE['Cl3'] = ''
##            LE['Sur3'] = ''
##            LE['Mnt3'] = ''
##        elif k ==3:
##            LE['Age4'] = Age_All[k]
##            LE['Sex4'] = Gender_All[k]
##            LE['Wgt4'] = Wgt_All[k]
##            LE['Hgt4'] = Hgt_All[k]
##            LE['Bld4'] = Bld_All[k]
##            LE['Status4'] = Status_All[k]
##            LE['Mech4'] = Mechanism_All[k]
##            LE['Inj4'] = Injury_All[k]
##            LE['Ill4'] = Illness_All[k]
##            LE['Tx4'] = Treatment_All[k]
##            LE['Local4'] = ''
##            LE['Fit4'] = ''
##            LE['Exp4'] = ''
##            LE['Eq4'] = ''
##            LE['Cl4'] = ''
##            LE['Sur4'] = ''
##            LE['Mnt4'] = ''
##        else:
##            pass
##        k+=1
##
##    LE['DisIPP'] = ''
##    LE['Ffeat']= ''
##    LE['Ffeat2']= ''
##    LE['Strat']= ''
##    LE['Mob']= ''
##    LE['TrkOff']= ''
##    LE['ElvFt']= ''
##    LE['BFnd']= ''
##    LE['SrchInj']= ''
##    LE['SrchInjDet']= ''
##    LE['Tasks']= ''
##    LE['VehNum']= ''
##    LE['Peop']= ''
##    LE['MilesDrv']= ''
##    LE['Cost']= ''
##    LE['Manhrs']= ''
##    LE['DogNum']= ''
##    LE['AirNum']= ''
##    LE['AirTsk']= ''
##    LE['AirHrs']= ''
##    LE['FndRes']= ''
##    LE['EVol']= ''
##    LE['Peop']= ''
##    LE['Manhrs']= ''
##    LE['VehNum']= ''
##    LE['MilesDrv']= ''
##    LE['Cost']= ''
##    LE['AirHrs']= ''
##    LE['AirNum']= ''
##    LE['AirTsk']= ''
##    LE['DogNum ']= ''
##    LE['Tasks ']= ''
##
##    #Incidentstatus
##    LE['IncStat']= ''
##    #PrimaryResponseArea
##    LE['PrimeArea']= ''
##    LE['IPPType']= ''
##    #Subform1
##    LE['SubGrp']= ''
##    #Subform2
##    LE['Elv']= ''
##    #Subform3
##    LE['Sig']= ''
##    LE['Aeromedical']= ''
##    LE['Helicopter']= ''
##    LE['Swiftwater']= ''
##    LE['Boat']= ''
##    LE['Vehicle']= ''
##    LE['Technical']= ''
##    LE['SemiTech']= ''
##    LE['Carryout']= ''
##    LE['Walkout']= ''
##    LE['Other']= ''
##    LE['OtherRescue']= ''
##    #Subform4
##    LE['Swiftwater']= ''
##    LE['Other']= ''
##    LE['USARCert']= ''
##    LE['FixedWing']= ''
##    LE['Helo']= ''
##    LE['Other']= ''
##    LE['Parks']= ''
##    LE['Cave']= ''
##    LE['Boats']= ''
##    LE['Divers']= ''
##    LE['Law']= ''
##    LE['Tracker']= ''
##    LE['CheckBox3']= ''
##    LE['EMS']= ''
##    LE['Dogs']= ''
##    LE['TextField1']= ''
##    LE['GSAR']= ''
##
##
####    tupl = (Lead,IncNum,MisNum,Incdate,IncTyp,Prepared,Org,Email,Phone,IncEnv,
####        CtyReg,State,InciTimeRp,SubCat,SubCatSub,SubAct,IPPClass,IPPLat,IPPLong,
####        IPPFmt,EcoDom,EcoDiv,Pop,Ter,Cover,Owner,Wx,Tmax,Tmin,Wind,Rain,SnowGrd,
####        Snow,Light,TLSdate,TSN,SF,IClosed,TTL,TST,TLSTime,SARNotTime,
####        SubFoundTime,ClosedTime,Age1,Sex1,Local1,Wgt1,Hgt1,Bld1,Fit1,Exp1,Eq1,
####        Cl1,Sur1,Mnt1,Age2,Sex2,Sex3,Sex4,Age3,Age4,Local2,Local3,Local4,GrpTyp,
####        Wgt2,Wgt3,Wgt4,Hgt2,Hgt3,Hgt4,Bld2,Bld3,Bld4,Fit2,Fit3,Fit4,Exp2,Exp3,
####        Exp4,Eq2,Eq3,Eq4,Cl2,Cl3,Cl4,Sur2,Sur3,Sur4,Mnt2,Mnt3,Mnt4,CntMtd,
####        DesLong,DesLat,DesFmt,RPLSFmt,RPLSLat,RPLSLong,DECLat,DECLong,DECFmt,
####        DOT,DOThow,RevPLS,DECTyp,RevDOT,Dec,Comment,Outcm,Scen,Susp,SubjNum,
####        Well,Inj,DOA,Saves,FFmt,FLong,FLat,DisIPP,Ffeat,Ffeat2,Det,MobRes,Strat,
####        Mob,TrkOff,ElvFt,BFnd,Status1,Mech1,Inj1,Ill1,Tx1,Status2,Status3,
####        Status4,Mech2,Mech3,Mech4,Inj2,Inj3,Inj4,Ill2,Ill3,Ill4,Tx2,Tx3,Tx4,
####        SrchInj,SrchInjDet,Tasks,VehNum,Peop,MilesDrv,Cost,Manhrs,DogNum,
####        AirNum,AirTsk,AirHrs,FndRes,EVol,Peop,Manhrs,VehNum,MilesDrv,Cost,
####        AirHrs,AirNum,AirTsk,DogNum,Tasks,IncStat,PrimeArea,IPPType,SubGrp,Elv,
####        Sig,Aeromedical,Helicopter,Swiftwater,Boat,Vehicle,Technical,SemiTech,
####        Carryout,Walkout,Other,OtherRescue,Swiftwater,Other,USARCert,FixedWing,
####        Helo,Other,Parks,Cave,Boats,Divers,Law,Tracker,CheckBox3,EMS,Dogs,
####        TextField1,GSAR)
##
##    ISRIDFile(LE)
##
##
