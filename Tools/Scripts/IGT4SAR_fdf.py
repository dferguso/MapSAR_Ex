#-------------------------------------------------------------------------------
# Name:        IGT4SAR_fdf.py
#
# Purpose:     Creates the forms data format file (fdf) in order to generate
#              pdf files
#
# Author:      Eric Menendez
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
    from arcpy import AddMessage

from re import escape
from os import path, remove
import subprocess

INSTALL_DIRECTORY="C:\\MapSAR_Ex\\"

def CreatePDF(TAF2Use,fileName):
    # Initialize startupinfo for subprocess.call()
    startupInfo = subprocess.STARTUPINFO()
    startupInfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupInfo.wShowWindow = 0
        # Convert .fdf to .pdf and flatten formpy.
        #Run pdftk system command to populate the pdf file. The file "file_fdf.fdf" is pushed in to "input_pdf.pdf" thats generated as a new "output_pdf.pdf" file.
    pdftkDir=path.join(INSTALL_DIRECTORY,"Tools\\pdftk\\bin\\pdftk")
    pdftk_cmd = ("{0} {1} fill_form {2}.fdf output {2}A.pdf").format(pdftkDir,TAF2Use,fileName[:-4])
    subprocess.call(pdftk_cmd)
    pdftk_cmd = ("{0} {1}A.pdf cat output {1}.pdf").format(pdftkDir,fileName[:-4])
    subprocess.call(pdftk_cmd)
    if path.isfile("{0}.pdf".format(fileName[:-4])):
        remove("{0}.fdf".format(fileName[:-4]))
        remove("{0}A.pdf".format(fileName[:-4]))
    else:
        try:
            remove("{0}A.pdf".format(fileName[:-4]))
        except:
            pass
    return

def fdf_value(text):
	if not text:
		# Convert None to empty string
		return ''
	else:
		returnText = []
		# Split text into lines; OS independent
        if type(text)==str:
    		for line in text.splitlines():
    			# Escape non-alphanumeric characters
    			returnText.append(escape(line))
        else:
            return text
		# Return joined lines
        return '\n'.join(returnText)


def create_fdf(output, fName, formName, fields, conCat=True):
    #First create the fdf file
    fileName = path.join(output,fName)
    fdf = open(fileName, 'w')

    fdf.write("%FDF-1.2\n")
    fdf.write("%????\n")
    fdf.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(formName))
    fdf.write("endobj\n")
    fdf.write("2 0 obj[\n\n")

    for field in fields:
        fdf.write("<</T(topmostSubform[0].Page1[0].{0}[0])/V({1})>>\n".format(field, fdf_value(fields[field])))

    fdf.write("]\n")
    fdf.write("endobj\n")
    fdf.write("trailer\n")
    fdf.write("<</Root 1 0 R>>\n")
    fdf.write("%%EO\n")
    fdf.close()
    if conCat==True:
        fOrms = path.join(output,formName)
        CreatePDF(fOrms,fileName)
    return

def create_fdf2(output, fName, formName, fields, conCat=True):
    #First create the fdf file
    fileName = path.join(output,fName)
    fdf = open(fileName, 'w')

    fdf.write("%FDF-1.2\n")
    fdf.write("%????\n")
    fdf.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(formName))
    fdf.write("endobj\n")
    fdf.write("2 0 obj[\n\n")

    for field in fields:
        if field == "On":
            fdf.write("<</T({0})/V/{1}>>\n".format(field, fdf_value(fields[field])))
        else:
            fdf.write("<</T({0})/V({1})>>\n".format(field, fdf_value(fields[field])))

    fdf.write("]\n")
    fdf.write("endobj\n")
    fdf.write("trailer\n")
    fdf.write("<</Root 1 0 R>>\n")
    fdf.write("%%EO\n")
    fdf.close()

    if conCat==True:
        fOrms = path.join(output,formName)
        CreatePDF(fOrms,fileName)

    return

def create_fdf3(output, fName, formName, fields, conCat=True):
    #First create the fdf file
    fileName = path.join(output,fName)
    fdf = open(fileName, 'w')

    fdf.write("%FDF-1.2\n")
    fdf.write("%????\n")
    fdf.write("1 0 obj<</FDF<</F({0})/Fields 2 0 R>>>>\n".format(formName))
    fdf.write("endobj\n")
    fdf.write("2 0 obj[\n\n")

    for field in fields:
        fdf.write("<</T(topmostSubform[0].Page1[0].Layer[0].Layer[0].{0}[0])/V({1})>>\n".format(field, fdf_value(fields[field])))

    fdf.write("]\n")
    fdf.write("endobj\n")
    fdf.write("trailer\n")
    fdf.write("<</Root 1 0 R>>\n")
    fdf.write("%%EO\n")
    fdf.close()
    if conCat==True:
        fOrms = path.join(output,formName)
        CreatePDF(fOrms,fileName)
    return

