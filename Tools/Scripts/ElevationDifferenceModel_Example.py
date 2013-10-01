#-------------------------------------------------------------------------------
# Name:        ElevationDifferenceModel_Example
# Purpose:  This is not an actual script but examples of the calculations that
#  would be performed inside of the Raster Calculator to complete the Elevation
#  Model as described in Koester's Lost Person Behavior.
#
# Author:      Don Ferguson
#
# Created:     06/12/2012
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

#####
# IPP Elevation = 640
# Same Elevation
Con((((640-10) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+10))),16,0)

# Down
Con((((640-40) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (640-10))),36,0)
Con((((640-86) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (640-40))),36,0)
Con((((640-203) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (640-86))),36,0)

# Up
Con((((640+10) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+48))),33,0)
Con((((640+48) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+100))),33,0)
Con((((640+100) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+370))),33,0)

# Overall up - 32%
Con((((640+10) < "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  <= (640+1905))),42,0)

# Overall down - 52%
Con((((640-1607) <= "14 Base_Data_Group\Elevation\crsf_dem")  &  ("14 Base_Data_Group\Elevation\crsf_dem"  < (640-20))),55,0)




##### Land Cover - Find Location
Con(IsNull("road_find"),Con(IsNull("linear_find"),Con(IsNull("Water_Reclass"),Con(IsNull("drain_find"),"NLCD_Clipped",5),11),2),1)


Con(IsNull("Models\Mobility\road_find"),Con(IsNull("Models\Mobility\linear_find"),Con(IsNull("Models\Mobility\Water_Reclass"),Con(IsNull("Models\Mobility\highslopeA"),Con(IsNull("Models\Mobility\drain_find"),"Models\Mobility\Veggie_Impd",45),99),80),33),1)