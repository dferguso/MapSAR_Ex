#-------------------------------------------------------------------------------
# Name:        IGT4SAR_Geodesic.py
# Purpose:     Script usess the Vincenty's formulae to create polygons representing
#              geodesic sectors on the Earth surface.  These pie sectors could
#              represent cellphone signal transmitted from a point source or
#              some for of dispersion angle from a point source.
#
#              http://en.wikipedia.org/wiki/Vincenty's_formulae
#
# Author:      Don Ferguson
#
# Created:     22/07/2014
# Copyright:   (c) ferguson 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
try:
    sys
except NameError:
    import sys
try:
    math
except NameError:
    import math

def Geodesic(pnt, in_bearing, in_angle, in_dist):
    LongDD = pnt.X
    LatDD = pnt.Y

    long2DD = [LongDD]
    lat2DD = [LatDD]
    coordList =[]

    # Parameters from WGS-84 ellipsiod
    aa = 6378137.0
    bb = 6356752.3142
    ff = 1 / 298.257223563
    radius = 6372.8

    LatR = LatDD * math.pi / 180.0
    LongR = LongDD * math.pi / 180.0

    if abs(in_angle % 2.0) > 0.0:
        in_angle += 1

    strAng = int(in_bearing - in_angle/2.0)
    endAng = int(in_bearing + in_angle/2.0)

    # Vincenty's formulae
    for brng in range(strAng,endAng):
        alpha1 = brng * math.pi / 180.0  #brng.toRad();
        sinAlpha1 = math.sin(alpha1)
        cosAlpha1 = math.cos(alpha1)
        tanU1 = (1.0 - ff) * math.tan(LatR)
        cosU1 = 1.0 / math.sqrt((1.0 + tanU1**2.0))
        sinU1 = tanU1 * cosU1

        sigma1 = math.atan2(tanU1, cosAlpha1)
        sinAlpha = cosU1 * sinAlpha1
        cosSqAlpha = 1.0 - sinAlpha**2.0

        uSq = cosSqAlpha * (aa**2.0 - bb**2.0) / (bb**2.0)

        AAA = 1.0 + uSq / 16384.0 * (4096.0 + uSq * (-768.0 + uSq * (320.0 - 175.0 * uSq)))
        BBB = uSq / 1024.0 * (256.0 + uSq * (-128.0 + uSq * (74.0- 47.0 * uSq)))

        sigma = in_dist / (bb * aa)
        sigmaP = 2.0 * math.pi
        while (abs(sigma - sigmaP) > 0.000000000001):
            cos2SigmaM = math.cos(2.0 * sigma1 + sigma)
            sinSigma = math.sin(sigma)
            cosSigma = math.cos(sigma)
            deltaSigma = BBB * sinSigma * (cos2SigmaM + BBB / 4.0 * (cosSigma * (-1.0 + 2.0 * cos2SigmaM**2.0) -
                BBB / 6.0 * cos2SigmaM * (-3.0 + 4.0 * sinSigma**2.0) * (-3.0 + 4.0* cos2SigmaM**2.0)))
            sigmaP = sigma

            sigma = in_dist / (bb * AAA) + deltaSigma

        tmp = sinU1 * sinSigma - cosU1 * cosSigma * cosAlpha1

        lat2 = math.atan2(sinU1 * cosSigma + cosU1 * sinSigma * cosAlpha1,(1.0 - ff) * math.sqrt(sinAlpha**2.0 + tmp**2.0))
        lamb = math.atan2(sinSigma * sinAlpha1, cosU1 * cosSigma - sinU1 * sinSigma * cosAlpha1)
        CC = ff / 16.0 * cosSqAlpha * (4.0 + ff * (4.0 - 3.0 * cosSqAlpha))
        LL = lamb - (1.0 - CC) * ff * sinAlpha * (sigma + CC * sinSigma * (cos2SigmaM + CC * cosSigma * (-1.0 + 2.0 * cos2SigmaM**2)))
        lon2 = (LongR + LL + 3.0 * math.pi) - (2.0 * math.pi) - math.pi  # normalise to -180...+180

        long2DD.append(lon2 * 180.0 / math.pi)
        lat2DD.append(lat2 * 180.0 / math.pi)

    long2DD.append(LongDD)
    lat2DD.append(LatDD)

    # A list of features and coordinate pairs
    for xi in range(len(lat2DD)):
        coordList.append([long2DD[xi],lat2DD[xi]])

    return coordList

def main():
    pass

if __name__ == '__main__':
    main()
