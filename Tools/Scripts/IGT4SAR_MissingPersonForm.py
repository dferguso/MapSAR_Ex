#-------------------------------------------------------------------------------
# Name:        MissingPersomForm.py
#
# Purpose:     Create Missing Person Flyer from data stored in the Subject
#              Information data layer within MapSAR
#
# Author:      Don Ferguson
#
# Created:     12/12/2011
# Copyright:   (c) Don Ferguson 2011
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

import arcpy, png, pyqrcode
from types import *
from datetime import datetime

def checkNoneType(variable, varName):
    if type(variable) is NoneType:
        arcpy.AddWarning(varName + " is not defined")
        result = " "
    else:
        result = variable
    return result

#workspc = arcpy.GetParameterAsText(0)
output = arcpy.GetParameterAsText(0)
addInfo = arcpy.GetParameterAsText(1)

#arcpy.env.workspace = workspc
arcpy.env.overwriteOutput = "True"

fc3="Incident_Information"
fc2="Lead Agency"


rows = arcpy.SearchCursor(fc3)
row = rows.next()
arcpy.AddMessage("Get Incident Info")
k=0
while row:
    # you need to insert correct field names in your getvalue function
    k+=1
    if type(row.getValue("Lead_Agency")) is NoneType:
        LeadAgency = " "
    else:
        LeadAgency = row.getValue("Lead_Agency")
        where2 = '"Lead_Agency" = ' + "'" + LeadAgency + "'"
        arcpy.AddMessage(where2)
        rows2 = arcpy.SearchCursor(fc2, where2)
        row2 = rows2.next()

        while row2:
            # you need to insert correct field names in your getvalue function
            Phone = checkNoneType(row2.getValue("Lead_Phone"), '"Reporting Phone Number"')
            email = checkNoneType(row2.getValue("E_Mail"), '"Reporting e-mail"')
            row2 = rows2.next()
        del rows2
        del row2
    Callback = "If you have information please call: " + str(LeadAgency) + " at phone: " + str(Phone) + " or e-mail:" + str(email)

    row = rows.next()
del rows
del row

if k==0:
    arcpy.AddWarning('"Reporting Information (Lead Agency: call in phone # or e-mail)" is not defined')
    Callback =" "

arcpy.AddMessage("\nSubject Information")

fc1="Subject_Information"
rows = arcpy.SearchCursor(fc1)
row = rows.next()
while row:
    # you need to insert correct field names in your getvalue function
    Subject_Name = checkNoneType(row.getValue("Name"),"Subject Name")
    Subject_Name = row.getValue("Name")
    if Subject_Name is not None:

        arcpy.AddMessage("Subject Name: {0}".format(Subject_Name))
    else:
        arcpy.AddWarning('Need to provide a Subject Name ~ "Subject" was used')
        Subject_Name="Subject"

    if type(row.getValue("Date_Seen")) is NoneType:
        arcpy.AddWarning('"Date last seen" is not defined')
        Date_Seen = " "
    else:
        fDate = row.getValue("Date_Seen")
        Date_Seen = fDate.strftime("%m/%d/%Y")

    fTime = checkNoneType(row.getValue("Time_Seen"), '"Time Last Seen"')

    Where_Last = checkNoneType(row.getValue("WhereLastSeen"), '"Where Last Seen"')
    Age = checkNoneType(row.getValue("Age"), "Subject Age")
    Gender = checkNoneType(row.getValue("Gender"), "Subject Gender")
    Race = checkNoneType(row.getValue("Race"), "Subject Race")

    Height2 =checkNoneType(row.getValue("Height"), "Subject Height")
##  Bug fix...object type "int" has not length, so changed "if len(Height)>1" to if "Height2>1"
    if len(str(Height2))>1:
        Height1 = Height2/12.0
        feet = int(Height1)
        inches = int((Height1 - feet)*12.0)
        fInches = "%1.0f" %inches
        Height = str(feet) + " ft " + fInches +" in"
    else:
        Height = " "

    Weight = checkNoneType(row.getValue("Weight"), '"Subject Weight"')
    Build = checkNoneType(row.getValue("Build"), '"Subject Build"')
    Complex =checkNoneType(row.getValue("Complexion"), '"Subject Complexion"')
    Hair = checkNoneType(row.getValue("Hair"), '"Subject Hair"')
    Eyes = checkNoneType(row.getValue("Eyes"), '"Subject Eye Color"')
    Other = checkNoneType(row.getValue("Other"), '"Other Clothing Information"')
    Shirt = checkNoneType(row.getValue("Shirt"), '"Subject Shirt"')
    Pants = checkNoneType(row.getValue("Pants"), '"Subject Pants"')
    Jacket = checkNoneType(row.getValue("Jacket"), '"Subject Jacket"')
    Hat = checkNoneType(row.getValue("Hat"), '"Subject Hat"')
    Footwear = checkNoneType(row.getValue("Footwear"), '"Subject Footwear"')
    if addInfo.upper()=="TRUE":
        Info = checkNoneType(row.getValue("Info"), '"Additonal Information"')
    else:
        Info = checkNoneType("", '"Additonal Information"')

    qrCode = row.getValue("QRCode")
    if qrCode is not None:
        url=pyqrcode.create(qrCode)
        qrFile = output + "/" + str(Subject_Name) + ".png"
        url.png(qrFile, scale=8)
    else:
        qrFile=" "

    #QRCode = checkNoneType(row.getValue("QRCode"), '"QRCode"')

    filename = output + "/" + str(Subject_Name) + ".fdf"
    txt= open (filename, "w")
    txt.write("%FDF-1.2\n")
    txt.write("%????\n")
    txt.write("1 0 obj<</FDF<</F(MissingPersonForm.pdf)/Fields 2 0 R>>>>\n")
    txt.write("endobj\n")
    txt.write("2 0 obj[\n")

    txt.write ("\n")

    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Name[0])/V(" + str(Subject_Name) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPFAge[0])/V(" + str(Age) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPFSex[0])/V(" + str(Gender) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Location[0])/V(" + str(Where_Last) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_TimeMissing[0])/V(" + fTime + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_DateMissing[0])/V(" + str(Date_Seen) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Race[0])/V(" + str(Race) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Height[0])/V(" + Height + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Weight[0])/V(" + str(Weight) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Build[0])/V(" + str(Build) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_Complex[0])/V(" + str(Complex) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_HairColor[0])/V(" + str(Hair) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_EyeColor[0])/V(" + str(Eyes) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherPhy[0])/V(" + str(Other) + ")>>\n")
    #txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherPhy[1])/V(" + str(Incident_Name) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_ShirtClothing[0])/V(" + str(Shirt) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_PantsClothing[0])/V(" + str(Pants) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_JacketClothing[0])/V(" + str(Jacket) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_HatClothing[0])/V(" + str(Hat) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_FootClothing[0])/V(" + str(Footwear) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_OtherInfo[0])/V(" + str(Info) + ")>>\n")
    txt.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].MPF_CallNumber[0])/V(" + str(Callback) + ")>>\n")

    txt.write("]\n")
    txt.write("endobj\n")
    txt.write("trailer\n")
    txt.write("<</Root 1 0 R>>\n")
    txt.write("%%EO\n")
    txt.close ()

    row = rows.next()
del rows
del row
#arcpy.DeleteFeatures_management(fc3)