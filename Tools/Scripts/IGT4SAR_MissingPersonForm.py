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
try:
    arcpy
except NameError:
    import arcpy
import png, pyqrcode
from types import *
from datetime import datetime
import IGT4SAR_fdf

def checkNoneType(variable, varName):
    if type(variable) is NoneType:
        arcpy.AddWarning(varName + " is not defined")
        result = " "
    else:
        result = variable
    return result

if __name__ == '__main__':

    #workspc = arcpy.GetParameterAsText(0)
    output = arcpy.GetParameterAsText(0)
    addInfo = arcpy.GetParameterAsText(1)

    #arcpy.env.workspace = workspc
    arcpy.env.overwriteOutput = "True"

    output = output.replace("'\'","/")

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
            qrFile = output + "/" + str(Subject_Name) + "_QRcode.png"
            url.png(qrFile, scale=8)
        else:
            qrFile=" "

        #QRCode = checkNoneType(row.getValue("QRCode"), '"QRCode"')

        fdfFields = {
            'MPF_Name':Subject_Name,
            'MPFAge':Age,
            'MPFSex':Gender,
            'MPF_Location':Where_Last,
            'MPF_TimeMissing':fTime,
            'MPF_DateMissing':Date_Seen,
            'MPF_Race':Race,
            'MPF_Height':Height,
            'MPF_Weight':Weight,
            'MPF_Build':Build,
            'MPF_Complex':Complex,
            'MPF_HairColor':Hair,
            'MPF_EyeColor':Eyes,
            'MPF_OtherPhy':Other,
            #'MPF_OtherPhy':Incident_Name,
            'MPF_ShirtClothing':Shirt,
            'MPF_PantsClothing':Pants,
            'MPF_JacketClothing':Jacket,
            'MPF_HatClothing':Hat,
            'MPF_FootClothing':Footwear,
            'MPF_OtherInfo':Info,
            'MPF_CallNumber':Callback
        }

        formName = 'MissingPersonForm.pdf'
        fName = "Missing_{0}.fdf".format(str(Subject_Name))

        # Create .fdf
        IGT4SAR_fdf.create_fdf3(output, fName, formName, fdfFields, conCat=False)

        row = rows.next()
    del rows
    del row
    #arcpy.DeleteFeatures_management(fc3)