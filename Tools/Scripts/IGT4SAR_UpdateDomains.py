# ---------------------------------------------------------------------------
# UpdateDomains.py
# Purpose:  This tools is used repeatedly to update information stored in the
#  SAR_Default.gbd domains.  Use this tool whenever new information is entered
#  into the following feature classes:
# Lead Agency</br>
# Incident Information</br>
# Operation Period</br>
# Incident Staff</br>
# Teams</br>
# Subject Information</br>
# Scenario</br>
# Probability_Regions</br>
# Assignments</br>
# Clues_Point<
#
# Author:      Don Ferguson
#
# Created:     01/25/2012
# Copyright:   (c) Don Ferguson 2012
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
import arcpy

# Script arguments
Workspace = arcpy.GetParameterAsText(0)
if Workspace == '#' or not Workspace:
    Workspace = "SAR_Default.gdb" # provide a default value if unspecified

# Local variables:

Lead_Agency = "Lead_Agency"
Incident_Information = "Incident_Info"
Operation_Period = "Operation_Period"
Incident_Staff = "Incident_Staff"
Teams = "Teams"
TeamMemb = "Team_Members"
Subject_Information = "Subject_Information"
Scenarios = "Scenarios"
Probability_Regions = "Probability_Regions"
Assignments = "Assignments"
Clues_Point = "Clues_Point"

# Process: Table To Domain (1)
cLead=arcpy.GetCount_management(Lead_Agency)
if int(cLead.getOutput(0)) > 0:
    arcpy.AddMessage("update Lead Agency domain")
    arcpy.TableToDomain_management(Lead_Agency, "Lead_Agency", "Lead_Agency", Workspace, "Lead_Agency", "Lead_Agency", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Lead_Agency", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Lead Agency information to update")

# Process: Table To Domain (2)
cIncident=arcpy.GetCount_management(Incident_Information)
if int(cIncident.getOutput(0)) > 0:
    arcpy.AddMessage("update Incident Information domain")
    arcpy.TableToDomain_management(Incident_Information, "Incident_Name", "Incident_Name", Workspace, "Incident_Name", "Incident_Name", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Incident_Name", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Incident information to update")

cOpPeriod=arcpy.GetCount_management(Operation_Period)
if int(cOpPeriod.getOutput(0)) > 0:
    # Process: Calculate Field
    arcpy.CalculateField_management(Operation_Period, "Period_Text", "!Period!", "PYTHON_9.3", "")

    # Process: Table To Domain (3)
    arcpy.AddMessage("update Operation Period domain")
    arcpy.TableToDomain_management(Operation_Period, "Period", "Period_Text", Workspace, "Period", "Period_Text", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Period", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Operations Period information to update")

# Process: Table To Domain (4)
cStaff=arcpy.GetCount_management(Incident_Staff)
if int(cStaff.getOutput(0)) > 0:
    arcpy.AddMessage("update Incident Staff domain")
    arcpy.TableToDomain_management(Incident_Staff, "Staff_Name", "Staff_Name", Workspace, "StaffName", "Incident Staff Names", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "StaffName", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Incident Staff information to update")

# Process: Table To Domain (5)
cTeams=arcpy.GetCount_management(Teams)
if int(cTeams.getOutput(0)) > 0:
    arcpy.AddMessage("update Teams domain")
    arcpy.TableToDomain_management(Teams, "Team_Name", "Team_Name", Workspace, "Teams", "Teams", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Teams", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Team information to update")

# Process: Table To Domain (6)
cTeamMemb=arcpy.GetCount_management(TeamMemb)
if int(cTeamMemb.getOutput(0)) > 0:
    arcpy.AddMessage("update Team Members domain")
    arcpy.TableToDomain_management(TeamMemb, "Name", "Name", Workspace, "TeamMember", "Responder names", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "TeamMember", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Team Member information to update")

# Process: Table To Domain (7)
cSub=arcpy.GetCount_management(Subject_Information)
if int(cSub.getOutput(0)) > 0:
    arcpy.AddMessage("update Subject Information domain")
    arcpy.TableToDomain_management(Subject_Information, "Subject_Number", "Name", Workspace, "Subject_Number", "Subject_Number", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Subject_Number", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Subject Information to update")

# Process: Table To Domain (8)
cScen=arcpy.GetCount_management(Scenarios)
if int(cScen.getOutput(0)) > 0:
    arcpy.AddMessage("update Scenario Numbers domain")
    arcpy.TableToDomain_management(Scenarios, "Scenario_Number", "Description", Workspace, "Scenario_Number", "Description", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Scenario_Number", "CODE", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Scenario information to update")

cProb=arcpy.GetCount_management(Probability_Regions)
if int(cProb.getOutput(0)) > 0:
    # Process: Region Area
    arcpy.CalculateField_management(Probability_Regions, "Area", "!shape.area@acres!", "PYTHON_9.3", "")
# Process: Table To Domain (9)
    arcpy.AddMessage("update Probability Region Name domain")
    arcpy.TableToDomain_management(Probability_Regions, "Region_Name", "Region_Name", Workspace, "Region_Name", "Region_Name", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Region_Name", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Probability Region information to update")


# Process: Table To Domain (10)
try:
    cAssign=arcpy.GetCount_management(Assignments)
    if int(cAssign.getOutput(0)) > 0:
        arcpy.AddMessage("update Assignment Numbers domain")
        arcpy.TableToDomain_management(Assignments, "Assignment_Number", "Assignment_Number", Workspace, "Assignment_Number", "Assignment_Number", "REPLACE")
        try:
            arcpy.SortCodedValueDomain_management(Workspace, "Assignment_Number", "DESCRIPTION", "ASCENDING")
        except:
            pass
    else:
        arcpy.AddMessage("No Assignment Numbers to update")
except:
    arcpy.AddMessage("Error in Assignment Numbers update: may be two Assignments with same number or multiple blanks")

cClues=arcpy.GetCount_management(Clues_Point)
if int(cClues.getOutput(0)) > 0:
    # Process: Get Clue Number
    arcpy.CalculateField_management(Clues_Point, "Clue_NumText", "!Clue_Number!", "PYTHON_9.3", "")

# Process: Table To Domain (11)
    arcpy.AddMessage("update Clue Number domain")
    arcpy.TableToDomain_management(Clues_Point, "Clue_Number", "Clue_NumText", Workspace, "Clue_Number", "Clue_NumText", "REPLACE")
    try:
        arcpy.SortCodedValueDomain_management(Workspace, "Clue_Number", "DESCRIPTION", "ASCENDING")
    except:
        pass
else:
    arcpy.AddMessage("No Clue information to update")









