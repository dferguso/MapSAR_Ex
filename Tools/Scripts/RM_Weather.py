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

from arcpy import env
import os, datetime
import bs4
from urllib2 import urlopen, HTTPError

# Environment variables
env.overwriteOutput = "True"

######### Modules modified from from Jon Pedder - MapSAR #########################

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

    except AttributeError as e:
        return None
    return (cUrrent, futForecast)


def createOutputFile(cUrrent,future):
        # Output file
    wrkspc = "d:/temp"
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
    print("Output file written to: {0}\n\n".format(pRoducts))

    return

########
# Main Program starts here
#######
if __name__ == '__main__':
    # Set date and time vars
    timestamp = ''
    now = datetime.datetime.now()
    todaydate = now.strftime("%m_%d")
    todaytime = now.strftime("%H_%M_%p")
    timestamp = '{0}_{1}'.format(todaydate,todaytime)

    latLong = input("Latitude (d.dd), Longitude (d.dd)")

    longiTude=latLong[1]
    latiTude=latLong[0]

    if not latiTude:
        print('Problem with Latitude value')
    elif not longiTude:
        print('Problem with Longitude value')

    uNits = 'DEG C'

    if uNits.upper()=='DEG C':
        unitChk = 1
    else:
        unitChk = 0
    cUrrent,future=getWeather("http://forecast.weather.gov/MapClick.php?lat={0}&lon={1}&site=okx&unit={2}&lg=en&FcstType=text".format(str(latiTude),str(longiTude), str(unitChk)))
    if cUrrent == None:
        print("No weather data available for this location.")
    else:
        createOutputFile(cUrrent,future)
        forecast = ('{0}\nTemp={1}; Humidity:{2}; Wind:{3}; Visibility:{4}\n{5}').\
                  format(cUrrent['Location'], cUrrent['Temperature'], cUrrent['Humidity'],\
                  cUrrent['Wind'], cUrrent['Visibility'],cUrrent['Forecast'])
        print(forecast)
        for fut in future:
            print('{0}\n'.format(fut))