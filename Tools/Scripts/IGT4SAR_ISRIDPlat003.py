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
import arcpy
import sys


#########################################################################
def ISRIDFile(args):

    argNum=0
    List_elements=('Lead','IncNum','MisNum','Incdate','IncTyp','Prepared','Org',
        'Email','Phone','IncEnv','CtyReg','State','InciTimeRp','SubCat',
        'SubCatSub','SubAct','IPPClass','IPPLat','IPPLong','IPPFmt','EcoDom',
        'EcoDiv','Pop','Ter','Cover','Owner','Wx','Tmax','Tmin','Wind','Rain',
        'SnowGrd','Snow','Light','TLSdate','TSN','SF','IClosed','TTL','TST',
        'TLSTime','SARNotTime','SubFoundTime','ClosedTime','Age1','Sex1',
        'Local1','Wgt1','Hgt1','Bld1','Fit1','Exp1','Eq1','Cl1','Sur1','Mnt1',
        'Age2','Sex2','Sex3','Sex4','Age3','Age4','Local2','Local3','Local4',
        'GrpTyp','Wgt2','Wgt3','Wgt4','Hgt2','Hgt3','Hgt4','Bld2','Bld3','Bld4',
        'Fit2','Fit3','Fit4','Exp2','Exp3','Exp4','Eq2','Eq3','Eq4','Cl2','Cl3',
        'Cl4','Sur2','Sur3','Sur4','Mnt2','Mnt3','Mnt4','CntMtd','DesLong',
        'DesLat','DesFmt','RPLSFmt','RPLSLat','RPLSLong','DECLat','DECLong',
        'DECFmt','DOT','DOThow','RevPLS','DECTyp','RevDOT','Dec','Comment',
        'Outcm','Scen','Susp','SubjNum','Well','Inj','DOA','Saves','FFmt',
        'FLong','FLat','DisIPP','Ffeat','Ffeat2','Det','MobRes','Strat','Mob',
        'TrkOff','ElvFt','BFnd','Status1','Mech1','Inj1','Ill1','Tx1','Status2',
        'Status3','Status4','Mech2','Mech3','Mech4','Inj2','Inj3','Inj4','Ill2',
        'Ill3','Ill4','Tx2','Tx3','Tx4','SrchInj','SrchInjDet','Tasks','VehNum',
        'Peop','MilesDrv','Cost','Manhrs','DogNum','AirNum','AirTsk','AirHrs',
        'FndRes','EVol','Peop','Manhrs','VehNum','MilesDrv','Cost','AirHrs',
        'AirNum','AirTsk','DogNum','Tasks','Elv','Sig','Aeromedical','Helicopter',
        'Swiftwater','Boat','Vehicle','Technical','SemiTech','Carryout','Walkout',
        'Other','OtherRescue','Swiftwater','USARCert','FixedWing','Helo','Parks',
        'Cave','Boats','Divers','Law','Tracker','CheckBox3','EMS','Dogs','TextField1','GSAR')

    filename = output + "/" + str(args[List_elements[1]]) + "_ISRID.fdf"

    txt= open (filename, "w")
    txt.write("%FDF-1.2\n")
    txt.write("%????\n")
    txt.write("1 0 obj<</FDF<</F(ISRID_Data_Form.pdf)/Fields 2 0 R>>>>\n")
    txt.write("endobj\n")
    txt.write("2 0 obj[\n")

    txt.write ("\n")

    for elems in List_elements:
        if argNum < 94:
            txt.write("<</T(form1[0].#subform[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
        elif 94 <= argNum <= 174:
            txt.write("<</T(form1[0].#subform[6]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
        elif argNum == 175:
            txt.write("<</T(form1[0].#subform[6].Subform2[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
        elif 175 < argNum <= 187:
            txt.write("<</T(form1[0].#subform[6].Subform3[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
        else:
            txt.write("<</T(form1[0].#subform[6].Subform4[0]." + elems + "[0])/V(" + str(args[elems]) + ")>>\n")
        argNum+=1

    txt.write("]\n")
    txt.write("endobj\n")
    txt.write("trailer\n")
    txt.write("<</Root 1 0 R>>\n")
    txt.write("%%EO\n")
    txt.close ()

####################################################################################


########
# Main Program starts here
#######

if __name__ == '__main__':

    #arcpy.env.workspace = workspc
    arcpy.env.overwriteOutput = "True"

    LE={'Lead':'','IncNum':'','MisNum':'','Incdate':'','IncTyp':'','Prepared':'','Org':'',
        'Email':'','Phone':'','IncEnv':'','CtyReg':'','State':'','InciTimeRp':'','SubCat':'',
        'SubCatSub':'','SubAct':'','IPPClass':'','IPPLat':'','IPPLong':'','IPPFmt':'','EcoDom':'',
        'EcoDiv':'','Pop':'','Ter':'','Cover':'','Owner':'','Wx':'','Tmax':'','Tmin':'','Wind':'','Rain':'',
        'SnowGrd':'','Snow':'','Light':'','TLSdate':'','TSN':'','SF':'','IClosed':'','TTL':'','TST':'',
        'TLSTime':'','SARNotTime':'','SubFoundTime':'','ClosedTime':'','Age1':'','Sex1':'',
        'Local1':'','Wgt1':'','Hgt1':'','Bld1':'','Fit1':'','Exp1':'','Eq1':'','Cl1':'','Sur1':'','Mnt1':'',
        'Age2':'','Sex2':'','Sex3':'','Sex4':'','Age3':'','Age4':'','Local2':'','Local3':'','Local4':'',
        'GrpTyp':'','Wgt2':'','Wgt3':'','Wgt4':'','Hgt2':'','Hgt3':'','Hgt4':'','Bld2':'','Bld3':'','Bld4':'',
        'Fit2':'','Fit3':'','Fit4':'','Exp2':'','Exp3':'','Exp4':'','Eq2':'','Eq3':'','Eq4':'','Cl2':'','Cl3':'',
        'Cl4':'','Sur2':'','Sur3':'','Sur4':'','Mnt2':'','Mnt3':'','Mnt4':'','CntMtd':'','DesLong':'',
        'DesLat':'','DesFmt':'','RPLSFmt':'','RPLSLat':'','RPLSLong':'','DECLat':'','DECLong':'',
        'DECFmt':'','DOT':'','DOThow':'','RevPLS':'','DECTyp':'','RevDOT':'','Dec':'','Comment':'',
        'Outcm':'','Scen':'','Susp':'','SubjNum':'','Well':'','Inj':'','DOA':'','Saves':'','FFmt':'',
        'FLong':'','FLat':'','DisIPP':'','Ffeat':'','Ffeat2':'','Det':'','MobRes':'','Strat':'','Mob':'',
        'TrkOff':'','ElvFt':'','BFnd':'','Status1':'','Mech1':'','Inj1':'','Ill1':'','Tx1':'','Status2':'',
        'Status3':'','Status4':'','Mech2':'','Mech3':'','Mech4':'','Inj2':'','Inj3':'','Inj4':'','Ill2':'',
        'Ill3':'','Ill4':'','Tx2':'','Tx3':'','Tx4':'','SrchInj':'','SrchInjDet':'','Tasks':'','VehNum':'',
        'Peop':'','MilesDrv':'','Cost':'','Manhrs':'','DogNum':'','AirNum':'','AirTsk':'','AirHrs':'',
        'FndRes':'','EVol':'','Peop':'','Manhrs':'','VehNum':'','MilesDrv':'','Cost':'','AirHrs':'',
        'AirNum':'','AirTsk':'','DogNum':'','Tasks':'', 'Elv':'', 'Sig':'', 'Aeromedical':'',
        'Helicopter':'','Swiftwater':'','Boat':'','Vehicle':'','Technical':'','SemiTech':'',
        'Carryout':'','Walkout':'','Other':'','OtherRescue':'','Swiftwater':'','USARCert':'','FixedWing':'',
         'Helo':'','Parks':'','Cave':'','Boats':'','Divers':'','Law':'','Tracker':'','CheckBox3':'','EMS':'','Dogs':'',
         'TextField1':'','GSAR':''}

    #workspc = arcpy.GetParameterAsText(0)
    output = arcpy.GetParameterAsText(0)
    IPPType = arcpy.GetParameterAsText(1)
    LE['Prepared'] = arcpy.GetParameterAsText(2)
    LE['Org'] = arcpy.GetParameterAsText(3)
    LE['Email'] = arcpy.GetParameterAsText(4)
    LE['Phone'] = arcpy.GetParameterAsText(5)





    fc1="Incident_Info"
    fc2 = 'Lead_Agency'
    rows = arcpy.SearchCursor(fc1)
    row = rows.next()

    while row:
        # you need to insert correct field names in your getvalue function
        LE['IncNum'] = row.getValue("Incident_Name")
        LE['MisNum'] = row.getValue("Incident_Number")
        LE['IncType'] = row.getValue("Incident_Type")
        LE['IncEnv'] = row.getValue("Environment")
        LE['EcoDom'] = row.getValue("Eco_Region")
        LE['Pop'] = row.getValue("Pop_Den")
        LE['Ter'] = row.getValue("Terrain")
        LE['Cover'] = row.getValue("LandCover")
        LE['Owner'] = row.getValue("LandOwner")
        MapDatum = row.getValue("MapDatum")
        MapCoord = row.getValue("MapCoord")
        MagDec = row.getValue("MagDec")


        LE['Lead'] = row.getValue("Lead_Agency")


        where2 = '"Lead_Agency" = ' + "'" + LE['Lead'] + "'"
        arcpy.AddMessage(where2)
        rows2 = arcpy.SearchCursor(fc2, where2)
        row2 = rows2.next()

        while row2:
            # you need to insert correct field names in your getvalue function
            LE['CtyReg'] = row2.getValue("Lead_City")
            LE['State'] = row2.getValue("Lead_State")
            row2 = rows2.next()
        del rows2
        del row2

        row = rows.next()
    del rows
    del row


    fc2="Operation_Period"
    rows = arcpy.SearchCursor(fc2)
    row = rows.next()

    while row:
        # you need to insert correct field names in your getvalue function
        Start_Date = row.getValue("Start_Date")
        End_Date = row.getValue("End_Date")
        LE['Wx'] = row.getValue("Weather")
        LE['Tmax'] = row.getValue("Temp_max")
        LE['Tmin'] = row.getValue("Temp_min")
        LE['Wind'] = row.getValue("Wind")
        LE['Rain'] = row.getValue("Rain")
        LE['SnowGrd'] = row.getValue("Snow")
        LE['Light'] = row.getValue("Light")
        row = rows.next()
    del rows
    del row


## Subject Information, IPP and Find
    Age_All=[]
    Hgt_All=[]
    Wgt_All=[]
    Gender_All =[]
    Status_All = []
    Mechanism_All = []
    Treatment_All = []
    Illness_All = []
    Injury_All = []
    Bld_All = []
    Susp =""
    Status =''
    Mechanism =""
    Treatment =''
    Illness =''
    Injury =''

    fc1="Subject_Information"
    fc2="Plan_Point"
    fc3 = "Found"

    where2 = '"IPPType" = ' + "'" + IPPType + "'"

    rows = arcpy.SearchCursor(fc1)
    row = rows.next()
    while row:
        # you need to insert correct field names in your getvalue function
        SubNum = row.getValue("Subject_Number")
        where3 = '"Subject_Number" = ' + "'" + str(SubNum) + "'"

        try:
            fDate = row.getValue("Date_Seen")
            LE['Incdate'] = fDate.strftime("%m/%d/%Y")
        except:
            LE['Incdate'] = " "

        try:
            LE['InciTimeRp'] = row.getValue("Time_Seen")
        except:
            LE['InciTimeRp'] = " "
        LE['Where_Last'] = row.getValue("WhereLastSeen")


        Age = [row.getValue("Age")]
        Gender = [row.getValue("Gender")]
        Race = [row.getValue("Race")]
        try:
            Hgt = [(row.getValue("Height"))/12.0]
        except:
            Hgt = ""
        Wgt = [row.getValue("Weight")]
        Bld = [row.getValue("Build")]
        LE['SubCat'] = [row.getValue("Category")]
        LE['SubCatSub']= ''
        LE['SubAct']= ''
##################################################

        arcpy.AddMessage(where2)
        rows2 = arcpy.SearchCursor(fc2, where2)
        row2 = rows2.next()

        while row2:
            # you need to insert correct field names in your getvalue function
            LE['IPPClass'] = row2.getValue("IPPClass")
            LE['IPPFmt']= 'DD'
            LE['IPPLat'] = row2.getValue("Latitude")
            LE['IPPLong'] = row2.getValue("Longitude")

            try:
                rows3 = arcpy.SearchCursor(fc3, where3)
                row3 = rows3.next()
                while row2:
                    Susp =row.getValue("Suspension")
                    Status =[row.getValue("Status")]
                    Mechanism =[row.getValue("Mechanism")]
                    Treatment =[row.getValue("Treatment")]
                    Illness =[row.getValue("Illness_Type")]
                    Injury =[row.getValue("Injury_Type")]

                    LE['Comment']=row.getValue("Description")
                    LE['Scen'] =row.getValue("Scenario")
                    LE['Ffeat'] = ""
                    LE['Ffeat2'] = ""
                    LE['FFmt'] = 'DD'
                    LE['FLat'] = row2.getValue("Latitude")
                    LE['FLong'] = row2.getValue("Longitude")
                    LE['Det'] = row2.getValue("Detectibility")
                    LE['MobRes'] = row2.getValue("Mobility_Response")

                    try:
                        fDate = row.getValue("Date_Time")
                        LE['SF'] = fDate.strftime("%m/%d/%Y")
                    except:
                        LE['SF'] = " "
                    try:
                        LE['SubFoundTime'] = row.getValue("Date_Time")
                    except:
                        LE['SubFoundTime'] = " "
            except:
                pass

            row2 = rows2.next()
        del rows2
        del row2
        del fc2

###################################################
        Age_All.append(Age)
        Gender_All.append(Gender)
        Wgt_All.append(Wgt)
        Hgt_All.append(Hgt)
        Status_All.append(Status)
        Mechanism_All.append(Mechanism)
        Treatment_All.append(Treatment)
        Illness_All.append(Illness)
        Injury_All.append(Injury)
        Bld_All.append(Bld)


        row = rows.next()

    del rows
    del row
    del fc1
    lengh = len(Age_All)
    LE['SubjNum'] = lengh
    LE['Outcm']=''
    LE['Well'] = ''
    LE['Inj'] = ''
    LE['DOA'] = ''
    LE['Saves'] = ''
    k=0
    while k<=lengh-1:
        if k ==0:
            arcpy.AddMessage(Status_All[k])
            LE['Age1'] = str(Age_All[k])
            LE['Sex1'] = Gender_All[k]
            LE['Wgt1'] = Wgt_All[k]
            LE['Hgt1'] = Hgt_All[k]
            LE['Bld1'] = Bld_All[k]
            LE['Status1'] = Status_All[k]
            LE['Mech1'] = Mechanism_All[k]
            LE['Inj1'] = Injury_All[k]
            LE['Ill1'] = Illness_All[k]
            LE['Tx1'] = Treatment_All[k]
            LE['Local1'] = ''
            LE['Fit1'] = ''
            LE['Exp1'] = ''
            LE['Eq1'] = ''
            LE['Cl1'] = ''
            LE['Sur1'] = ''
            LE['Mnt1'] = ''

        elif k ==1:
            LE['Age2'] = Age_All[k]
            LE['Sex2'] = Gender_All[k]
            LE['Wgt2'] = Wgt_All[k]
            LE['Hgt2'] = Hgt_All[k]
            LE['Bld2'] = Bld_All[k]
            LE['Status2'] = Status_All[k]
            LE['Mech2'] = Mechanism_All[k]
            LE['Inj2'] = Injury_All[k]
            LE['Ill2'] = Illness_All[k]
            LE['Tx2'] = Treatment_All[k]
            LE['Local2'] = ''
            LE['Fit2'] = ''
            LE['Exp2'] = ''
            LE['Eq2'] = ''
            LE['Cl2'] = ''
            LE['Sur2'] = ''
            LE['Mnt2'] = ''
        elif k ==2:
            LE['Age3'] = Age_All[k]
            LE['Sex3'] = Gender_All[k]
            LE['Wgt3'] = Wgt_All[k]
            LE['Hgt3'] = Hgt_All[k]
            LE['Bld3'] = Bld_All[k]
            LE['Status3'] = Status_All[k]
            LE['Mech3'] = Mechanism_All[k]
            LE['Inj3'] = Injury_All[k]
            LE['Ill3'] = Illness_All[k]
            LE['Tx3'] = Treatment_All[k]
            LE['Local3'] = ''
            LE['Fit3'] = ''
            LE['Exp3'] = ''
            LE['Eq3'] = ''
            LE['Cl3'] = ''
            LE['Sur3'] = ''
            LE['Mnt3'] = ''
        elif k ==3:
            LE['Age4'] = Age_All[k]
            LE['Sex4'] = Gender_All[k]
            LE['Wgt4'] = Wgt_All[k]
            LE['Hgt4'] = Hgt_All[k]
            LE['Bld4'] = Bld_All[k]
            LE['Status4'] = Status_All[k]
            LE['Mech4'] = Mechanism_All[k]
            LE['Inj4'] = Injury_All[k]
            LE['Ill4'] = Illness_All[k]
            LE['Tx4'] = Treatment_All[k]
            LE['Local4'] = ''
            LE['Fit4'] = ''
            LE['Exp4'] = ''
            LE['Eq4'] = ''
            LE['Cl4'] = ''
            LE['Sur4'] = ''
            LE['Mnt4'] = ''
        else:
            pass
        k+=1

    LE['DisIPP'] = ''
    LE['Ffeat']= ''
    LE['Ffeat2']= ''
    LE['Strat']= ''
    LE['Mob']= ''
    LE['TrkOff']= ''
    LE['ElvFt']= ''
    LE['BFnd']= ''
    LE['SrchInj']= ''
    LE['SrchInjDet']= ''
    LE['Tasks']= ''
    LE['VehNum']= ''
    LE['Peop']= ''
    LE['MilesDrv']= ''
    LE['Cost']= ''
    LE['Manhrs']= ''
    LE['DogNum']= ''
    LE['AirNum']= ''
    LE['AirTsk']= ''
    LE['AirHrs']= ''
    LE['FndRes']= ''
    LE['EVol']= ''
    LE['Peop']= ''
    LE['Manhrs']= ''
    LE['VehNum']= ''
    LE['MilesDrv']= ''
    LE['Cost']= ''
    LE['AirHrs']= ''
    LE['AirNum']= ''
    LE['AirTsk']= ''
    LE['DogNum ']= ''
    LE['Tasks ']= ''

    #Incidentstatus
    LE['IncStat']= ''
    #PrimaryResponseArea
    LE['PrimeArea']= ''
    LE['IPPType']= ''
    #Subform1
    LE['SubGrp']= ''
    #Subform2
    LE['Elv']= ''
    #Subform3
    LE['Sig']= ''
    LE['Aeromedical']= ''
    LE['Helicopter']= ''
    LE['Swiftwater']= ''
    LE['Boat']= ''
    LE['Vehicle']= ''
    LE['Technical']= ''
    LE['SemiTech']= ''
    LE['Carryout']= ''
    LE['Walkout']= ''
    LE['Other']= ''
    LE['OtherRescue']= ''
    #Subform4
    LE['Swiftwater']= ''
    LE['Other']= ''
    LE['USARCert']= ''
    LE['FixedWing']= ''
    LE['Helo']= ''
    LE['Other']= ''
    LE['Parks']= ''
    LE['Cave']= ''
    LE['Boats']= ''
    LE['Divers']= ''
    LE['Law']= ''
    LE['Tracker']= ''
    LE['CheckBox3']= ''
    LE['EMS']= ''
    LE['Dogs']= ''
    LE['TextField1']= ''
    LE['GSAR']= ''


##    tupl = (Lead,IncNum,MisNum,Incdate,IncTyp,Prepared,Org,Email,Phone,IncEnv,
##        CtyReg,State,InciTimeRp,SubCat,SubCatSub,SubAct,IPPClass,IPPLat,IPPLong,
##        IPPFmt,EcoDom,EcoDiv,Pop,Ter,Cover,Owner,Wx,Tmax,Tmin,Wind,Rain,SnowGrd,
##        Snow,Light,TLSdate,TSN,SF,IClosed,TTL,TST,TLSTime,SARNotTime,
##        SubFoundTime,ClosedTime,Age1,Sex1,Local1,Wgt1,Hgt1,Bld1,Fit1,Exp1,Eq1,
##        Cl1,Sur1,Mnt1,Age2,Sex2,Sex3,Sex4,Age3,Age4,Local2,Local3,Local4,GrpTyp,
##        Wgt2,Wgt3,Wgt4,Hgt2,Hgt3,Hgt4,Bld2,Bld3,Bld4,Fit2,Fit3,Fit4,Exp2,Exp3,
##        Exp4,Eq2,Eq3,Eq4,Cl2,Cl3,Cl4,Sur2,Sur3,Sur4,Mnt2,Mnt3,Mnt4,CntMtd,
##        DesLong,DesLat,DesFmt,RPLSFmt,RPLSLat,RPLSLong,DECLat,DECLong,DECFmt,
##        DOT,DOThow,RevPLS,DECTyp,RevDOT,Dec,Comment,Outcm,Scen,Susp,SubjNum,
##        Well,Inj,DOA,Saves,FFmt,FLong,FLat,DisIPP,Ffeat,Ffeat2,Det,MobRes,Strat,
##        Mob,TrkOff,ElvFt,BFnd,Status1,Mech1,Inj1,Ill1,Tx1,Status2,Status3,
##        Status4,Mech2,Mech3,Mech4,Inj2,Inj3,Inj4,Ill2,Ill3,Ill4,Tx2,Tx3,Tx4,
##        SrchInj,SrchInjDet,Tasks,VehNum,Peop,MilesDrv,Cost,Manhrs,DogNum,
##        AirNum,AirTsk,AirHrs,FndRes,EVol,Peop,Manhrs,VehNum,MilesDrv,Cost,
##        AirHrs,AirNum,AirTsk,DogNum,Tasks,IncStat,PrimeArea,IPPType,SubGrp,Elv,
##        Sig,Aeromedical,Helicopter,Swiftwater,Boat,Vehicle,Technical,SemiTech,
##        Carryout,Walkout,Other,OtherRescue,Swiftwater,Other,USARCert,FixedWing,
##        Helo,Other,Parks,Cave,Boats,Divers,Law,Tracker,CheckBox3,EMS,Dogs,
##        TextField1,GSAR)

    ISRIDFile(LE)


