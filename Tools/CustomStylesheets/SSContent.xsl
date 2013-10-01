<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                version="1.0">

<xsl:import href = "MdDlgContent.xsl" />
<xsl:output method="html"/>

<!-- Overwrite Select Variable Definitions -->
<xsl:variable name="BackgroundColor">honeydew</xsl:variable>
<xsl:variable name="BackgroundImage">url(<xsl:value-of select="MdElementDialogInfo/CommonPath"/>/../Stylesheets/mygraphic.jpg)</xsl:variable>
<xsl:variable name="BackgroundPosition">bottom center</xsl:variable>
<xsl:variable name="CaptionFont">arial,verdana</xsl:variable>
<xsl:variable name="CaptionSize">10pt</xsl:variable>
<xsl:variable name="CaptionColor">DarkGreen</xsl:variable>
<xsl:variable name="CaptionWeight">Bold</xsl:variable>

<!-- Add Web link -->
<xsl:template match="MdElementDialogInfo">
    <xsl:apply-imports/>
    <table border="0" cellspacing="0" cellpadding="0" width="98%" onmousedown="parent.ShowHelpTopic('Intro');">
      <tr align="center">
        <td><span style="font-family:arial; font-size:7pt;">*This tool is described in</span></td></tr> <tr align="center">
        <td><span style="font-family:arial; font-size:7pt;"><i>The ESRI Guide to GIS Analysis</i>, Volume 2.</span></td></tr>
      <tr align="center">
        <td><span style="font-family:arial; font-size:7pt; color:blue;"><a href="http://gis.esri.com/esripress/display/index.cfm" target="esripress">Other books from ESRI Press</a></span></td></tr>
    </table>
</xsl:template>
</xsl:stylesheet>
