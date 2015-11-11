#-------------------------------------------------------------------------------
# Name:     IGT4SAR_Weather.py
# Purpose:  This tool acquires the current weather conditions and the
#           7-day forecast for the location idenitfied.  The tool scrapes
#           the weather data from National Weather Service
#                   http://forecast.weather.gov
#           Currently the tool only works in the United States
#
# Author:   Don Ferguson
#
# Created:  10/30/2015
# Copyright:   (c) Don Ferguson 2015
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
try:
    arcpy
except NameError:
    import arcpy
from arcpy import env
import os, datetime
import bs4
from urllib2 import urlopen, HTTPError

# Environment variables
wrkspc=arcpy.env.workspace
env.overwriteOutput = "True"
arcpy.env.extent = "MAXOF"

######### Modules modified from from Jon Pedder - MapSAR #########################
def getDataframe():
    """ get current mxd and dataframe returns mxd, frame"""
    try:
        mxd = arcpy.mapping.MapDocument('CURRENT');df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

        return(mxd,df)

    except SystemExit as err:
            pass

def chckSpecialCharacters(fName):
    # Special Characters
    spChar=('@','#','$','%','&','*','-',' ')
    ######################################
    # Check for special characters in name
    for sp in spChar:
        if sp in fName:
            fName = fName.replace(sp,"")
    ######################################
    return(fName)

def getWeather(url):
    try:
        html=urlopen(url)
    except HTTPError as e:
        return None
    try:
        bsObj = bs4.BeautifulSoup(html)

        curLoc = bsObj.find("div",{'id':"current-conditions"}).h2
        curLoc = (curLoc.get_text()).strip()

        curTemp = bsObj.find("p",{'class':"myforecast-current-lrg"})
        curTemp = str((curTemp.get_text().encode('ascii', 'ignore').decode('ascii')))

        hUmdity = bsObj.find('b', text='Humidity').parent.parent
        hUmdity = hUmdity('td')[1].string

        wInds = bsObj.find('b', text='Wind Speed').parent.parent
        wInds = wInds('td')[1].string

        bArometer = bsObj.find('b', text='Barometer').parent.parent
        bArometer = bArometer('td')[1].string

        dEwpoint = bsObj.find('b', text='Dewpoint').parent.parent
        dEwpoint = (dEwpoint('td')[1].string).encode('ascii', 'ignore').decode('ascii')

        vIsibility = bsObj.find('b', text='Visibility').parent.parent
        vIsibility = vIsibility('td')[1].string

        today=bsObj.find("img",{"class":"forecast-icon"})
        todayForecast = (today.attrs['title']+'\n')
        cUrrent = {'Location':curLoc,'Temperature':curTemp,'Humidity':hUmdity,\
                   'Wind':wInds,'Visibility': vIsibility,'Forecast':todayForecast}
        future=bsObj.findAll("img",{"class":"forecast-icon"})
        k=0
        futForecast=[]
        for link in future:
            if k>0:
                futForecast.append(link.attrs['title'])
            k+=1

#        arcpy.AddMessage('Current conditions at: {0}'.format(curLoc))
#        arcpy.AddMessage("Current temp is: {0}".format(curTemp))
#        arcpy.AddMessage('Humidity:', hUmdity)
#        arcpy.AddMessage('Wind Speed:', wInds)
#        arcpy.AddMessage('Barometer:', bArometer)
#        arcpy.AddMessage('Dewpoint:', dEwpoint)
#        arcpy.AddMessage('Visibility:', vIsibility)

    except AttributeError as e:
        return None
    return (cUrrent, futForecast)

def writeToOpPeriod(opPeriod, wEather):
    opInfo = 'Operation_Period'
    where = '"Period" = {0}'.format(str(opPeriod))
    cursor = arcpy.UpdateCursor(opInfo, where)
    for row in cursor:
        row.setValue('Weather', wEather['Forecast'])
        row.setValue('Wind',wEather['Wind'])
        cursor.updateRow(row)
    del row, cursor
    arcpy.AddMessage('Operation Period Attribute Table has been updated.\n')
    return

def createOutputFile(cUrrent,future):
        # Output file
    dirNm = os.path.dirname(wrkspc)
    pRoducts = os.path.join(dirNm,"Documents")
    if not os.path.exists(pRoducts):
        os.makedirs(pRoducts)
    fileName = os.path.join(pRoducts, "WeatherForecast_{0}.txt".format(timestamp))
    target = open(fileName, 'w')
    target.write("Weather Forecast: {0}".format(timestamp))
    forecast = ('{0}\nTemp={1}; Humidity:{2}; Wind:{3}; Visibility:{4}\n{5}').\
              format(cUrrent['Location'], cUrrent['Temperature'], cUrrent['Humidity'],\
              cUrrent['Wind'], cUrrent['Visibility'],cUrrent['Forecast'])

    lIne01 = ("{0}").format(cUrrent['Location'])
    lIne02 = ("Temp={0}; Humidity:{1}; Wind:{2}; Visibility:{3}").\
             format(cUrrent['Temperature'], cUrrent['Humidity'],\
             cUrrent['Wind'], cUrrent['Visibility'])
    lIne02b = ("{0}").format(cUrrent['Forecast'])

    target.write(lIne01)
    target.write("\n")
    target.write(lIne02)
    target.write("\n")
    target.write(lIne02b)
    target.write("\n")
    for fut in future:
        target.write(fut)
        target.write("\n")

    target.close()
    arcpy.AddMessage("Output file written to: {0}\n\n".format(pRoducts))

    return

########
# Main Program starts here
#######
if __name__ == '__main__':
    ## Script arguments
    mxd,df = getDataframe()
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    SubNum = arcpy.GetParameterAsText(0)  # Get the subject number
    if SubNum == '#' or not SubNum:
        SubNum = "1" # provide a default value if unspecified

    ippType = arcpy.GetParameterAsText(1)  # Determine to use PLS or LKP

    opPeriod = arcpy.GetParameterAsText(2)  # Operation Period

    uNits = arcpy.GetParameterAsText(3)  # Select English or Metric units

    fc = "Planning Point"
    desc = arcpy.Describe(fc)
    shapefieldname = desc.ShapeFieldName

    unProjCoordSys = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"
    coordList = []
    where1 = '"Subject_Number" = {0}'.format(str(SubNum))
    where2 = ' AND "IPPType" = ' + "'" + str(ippType) + "'"
    where = where1 + where2

    rows = arcpy.SearchCursor(fc, where, unProjCoordSys)
    for row in rows:
        feat = row.getValue(shapefieldname)
        pnt = feat.getPart()
        # A list of features and coordinate pairs
        longiTude=pnt.X
        latiTude=pnt.Y
    if not latiTude:
        arcpy.AddError('Problem with Latitude value')
    elif not longiTude:
        arcpy.AddError('Problem with Longitude value')

    if uNits.upper()=='DEG C':
        unitChk = 1
    else:
        unitChk = 0
    cUrrent,future=getWeather("http://forecast.weather.gov/MapClick.php?lat={0}&lon={1}&site=okx&unit={2}&lg=en&FcstType=text".format(str(latiTude),str(longiTude), str(unitChk)))
    if cUrrent == None:
        arcpy.AddMessage("No weather data available for this location.")
    else:
        writeToOpPeriod(opPeriod, cUrrent)
        createOutputFile(cUrrent,future)
        forecast = ('{0}\nTemp={1}; Humidity:{2}; Wind:{3}; Visibility:{4}\n{5}').\
                  format(cUrrent['Location'], cUrrent['Temperature'], cUrrent['Humidity'],\
                  cUrrent['Wind'], cUrrent['Visibility'],cUrrent['Forecast'])
        arcpy.AddMessage(forecast)
        for fut in future:
            arcpy.AddMessage('{0}\n'.format(fut))