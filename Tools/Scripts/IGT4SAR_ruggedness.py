# Ruggedness.py
# Description: This tool measures terrain ruggedness by calculating the vector ruggedness measure
#                   described in Sappington, J.M., K.M. Longshore, and D.B. Thomson. 2007. Quantifiying
#                   Landscape Ruggedness for Animal Habitat Anaysis: A case Study Using Bighorn Sheep in
#                   the Mojave Desert. Journal of Wildlife Management. 71(5): 1419 -1426.
# Requirements: Spatial Analyst 
# Author: Mark Sappington
# Revision History: 2/1/2008 		original Python version
#			  12/17/2010	updated for Windows 7 and ArcGIS 9.3.x/10

# Import system modules
import string, arcgisscripting

# Create the geoprocessor object
gp = arcgisscripting.create(9.3)

# Check out any necessary licenses
gp.CheckOutExtension("spatial")

# Script arguments
InRaster = gp.getparameterastext(0)
Neighborhood_Size = gp.getparameterastext(1)
OutWorkspace = gp.getparameterastext(2)
OutRaster = gp.getparameterastext(3)

# Local variables
AspectRaster = OutWorkspace + "\\aspect"
SlopeRaster = OutWorkspace + "\\slope"
SlopeRasterRad = OutWorkspace + "\\sloperad"
AspectRasterRad = OutWorkspace + "\\aspectrad"
xRaster = OutWorkspace + "\\x"
yRaster = OutWorkspace + "\\y"
zRaster = OutWorkspace + "\\z"
xyRaster = OutWorkspace + "\\xy"
xSumRaster = OutWorkspace + "\\xsum"
ySumRaster = OutWorkspace + "\\ysum"
zSumRaster = OutWorkspace + "\\zsum"
ResultRaster = OutWorkspace + "\\result"

try:
    # Create Slope and Aspect rasters
    gp.AddMessage("Calculating aspect...")
    gp.Aspect_sa(InRaster, AspectRaster)
    gp.AddMessage("Calculating slope...")
    gp.Slope_sa(InRaster, SlopeRaster, "DEGREE")

    # Convert Slope and Aspect rasters to radians
    gp.AddMessage("Converting slope and aspect to radians...")
    gp.times_sa(SlopeRaster,(3.14/180), SlopeRasterRad)
    gp.times_sa(AspectRaster,(3.14/180), AspectRasterRad)

    # Calculate x, y, and z rasters
    gp.AddMessage("Calculating x, y, and z rasters...")
    gp.sin_sa(SlopeRasterRad, xyRaster)
    gp.cos_sa(SlopeRasterRad, zRaster)
    gp.SingleOutputMapAlgebra_sa("con(" + AspectRaster + " == -1, 0, sin(" + AspectRasterRad + ") * " + xyRaster + ")", xRaster)
    gp.SingleOutputMapAlgebra_sa("con(" + AspectRaster + " == -1, 0, cos(" + AspectRasterRad + ") * " + xyRaster + ")", yRaster)

    # Calculate sums of x, y, and z rasters for selected neighborhood size
    gp.AddMessage("Calculating sums of x, y, and z rasters in selected neighborhood...")
    gp.FocalStatistics_sa(xRaster, xSumRaster, "Rectangle " + str(Neighborhood_Size) + " " + str(Neighborhood_Size) + " CELL", "SUM", "NODATA") 
    gp.FocalStatistics_sa(yRaster, ySumRaster, "Rectangle " + str(Neighborhood_Size) + " " + str(Neighborhood_Size) + " CELL", "SUM", "NODATA")
    gp.FocalStatistics_sa(zRaster, zSumRaster, "Rectangle " + str(Neighborhood_Size) + " " + str(Neighborhood_Size) + " CELL", "SUM", "NODATA")

    # Calculate the resultant vector
    gp.AddMessage("Calculating the resultant vector...")
    gp.SingleOutputMapAlgebra_sa("sqrt(sqr(" + xSumRaster + ") + sqr(" + ySumRaster  + ") + sqr(" + zSumRaster + "))", ResultRaster)

    # Calculate the Ruggedness raster
    gp.AddMessage("Calculating the final ruggedness raster...")
    maxValue = int(Neighborhood_Size) * int(Neighborhood_Size)
    gp.SingleOutputMapAlgebra_sa("1 - (" + ResultRaster + " / " + str(maxValue) + ")", OutRaster)

    # Delete all intermediate raster data sets
    gp.AddMessage("Deleting intermediate data...")
    gp.Delete(AspectRaster)
    gp.Delete(SlopeRaster)
    gp.Delete(SlopeRasterRad)
    gp.Delete(AspectRasterRad)
    gp.Delete(xRaster)
    gp.Delete(yRaster)
    gp.Delete(zRaster)
    gp.Delete(xyRaster)
    gp.Delete(xSumRaster)
    gp.Delete(ySumRaster)
    gp.Delete(zSumRaster)
    gp.Delete(ResultRaster)

# Check in any necessary licenses
    gp.CheckInExtension("spatial")    
    
except:
# Print error message if an error occurs
    gp.GetMessages()
