<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
                version="1.0">

<xsl:import href = "MdDlgContent.xsl" />
<xsl:output method="html"/>

<!-- Overwrite Select Variable Definitions -->
<xsl:variable name="BackgroundColor">buttonface</xsl:variable>
<xsl:variable name="BackgroundImage">url(C:\MapSAR\LostPersonBehavior\LostPersonBehavior_Small.jpg)</xsl:variable>
<xsl:variable name="BackgroundPosition">bottom center</xsl:variable>
<xsl:variable name="CaptionFont">arial,verdana</xsl:variable>
<xsl:variable name="CaptionSize">10pt</xsl:variable>
<xsl:variable name="CaptionColor">DarkGreen</xsl:variable>
<xsl:variable name="CaptionWeight">Bold</xsl:variable>
<xsl:variable name="cellsPerRow" select="2"/>
<xsl:variable name="imageWidth" select="120"/>
<xsl:variable name="imageHeight" select="160"/>


<!-- Add Web link -->
<xsl:template match="MdElementDialogInfo">
    <xsl:apply-imports/>
    
<table border="0" cellspacing="0" cellpadding="0" width="98%" onmousedown="parent.ShowHelpTopic('Intro');">

      <tr align="center">
        <td><span style="font-family:arial; font-size:10pt;">*Distances based on categorical subject profiles and data provided by:</span></td></tr> 
	 
      <tr align="center">
        <td><span style="font-family:arial; font-size:10pt;"><i>Koester, R., "Lost Person Behavior", dbS Publications, Charlottesville, VA, 2008.</i></span></td></tr>
      
      <tr align="center">
        <td><span style="font-family:arial; font-size:10pt;"><i>Based upon a landmark study, this book is the definitive guide to the latest subject categories, behavioral profiles, up to date statistics, suggested initial tasks and specialized investigative questions.</i></span></td></tr>

	
	 <tr align="center">
        <td><span style="font-family:arial; font-size:10pt; color:blue;"><a href="http://www.dbs-sar.com/LPB/lpb.htm" target="dbS Productions">Get it from dbS Productions</a></span></td></tr>
	<tr align="center">
        <td><span style="font-family:arial; font-size:10pt; color:blue;"><a href="http://www.amazon.com" target="Amazon">Get it from Amazon.com</a></span></td></tr>

<!--      <tr align="center">	
        <td><span style="font-family:arial; font-size:10pt; color:blue;"><a href="http://www.amazon.com/Lost-Person-Behavior-search-rescue/dp/1879471396/ref=sr_1_1?ie=UTF8&qid=1337131533&sr=8-1" target="Amazon">Get it from Amazon</a></span></td></tr> -->

    </table>
</xsl:template>
</xsl:stylesheet>

