#!/usr/bin/python3
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from math import sqrt
from auxiliary import distance_mse
from cv2 import boundingRect, contourArea

# ---------------------------------------------------------------------------------------------------------------
class PossibleMark:
    """ Class for representing a contour which might be representing a possible bracelet mark (for a later analysis) """

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def __init__(self, _contour, MinPixelWidth, MaxPixelWidth, MinPixelHeight, MaxPixelHeight,
                 MinAspectRatio, MaxAspectRatio, MinPixelArea, MaxPixelArea, MinExtent, MaxExtent):
        """ Constructor """

        self.contour = _contour

        self.boundingRect = boundingRect(self.contour)

        [intX, intY, intWidth, intHeight] = self.boundingRect

        self.intBoundingRectX = intX
        self.intBoundingRectY = intY
        self.intBoundingRectWidth = intWidth
        self.intBoundingRectHeight = intHeight

        self.intBoundingRectArea = self.intBoundingRectWidth * self.intBoundingRectHeight

        self.fltExtent = float(contourArea(self.contour)) / self.intBoundingRectArea

        self.intCenterX = int((self.intBoundingRectX + self.intBoundingRectX + self.intBoundingRectWidth) / 2)
        self.intCenterY = int((self.intBoundingRectY + self.intBoundingRectY + self.intBoundingRectHeight) / 2)

        self.intCenterX_r = 0
        self.intCenterY_r = 0

        self.fltDiagonalSize = sqrt((self.intBoundingRectWidth ** 2) + (self.intBoundingRectHeight ** 2))

        self.fltAspectRatio = float(self.intBoundingRectWidth) / float(self.intBoundingRectHeight)

        self.MinPixelWidth = MinPixelWidth
        self.MaxPixelWidth = MaxPixelWidth
        self.MinPixelHeight = MinPixelHeight
        self.MaxPixelHeight = MaxPixelHeight
        self.MinAspectRatio = MinAspectRatio
        self.MaxAspectRatio = MaxAspectRatio
        self.MinPixelArea = MinPixelArea
        self.MaxPixelArea = MaxPixelArea
        self.MinExtent = MinExtent
        self.MaxExtent = MaxExtent

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def check_if_possible_mark(self):
        """ A 'first pass' over the contour, to see if it could be representing a bracelet mark """

        return (self.MinPixelArea < self.intBoundingRectArea < self.MaxPixelArea and
                self.MinPixelWidth < self.intBoundingRectWidth < self.MaxPixelWidth and
                self.MinPixelHeight < self.intBoundingRectHeight < self.MaxPixelHeight and
                self.MinAspectRatio < self.fltAspectRatio < self.MaxAspectRatio and
                self.MinExtent < self.fltExtent < self.MaxExtent)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def __sub__(self, other):
        """ Overloading the subtraction operator, with comparison that is based on centorid MSE metric (Pythagorean theorem) """

        p1 = (self.intCenterX, other.intCenterX)
        p2 = (self.intCenterY, other.intCenterY)
        return distance_mse(p1,p2)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def __str__(self):
        """ print mark method """

        return "(x,y, xR,yR, w,h, BndArea,AspRatio,extent)=(%d,%d, %d,%d, %d,%d, %d,%.2f.%.2f)" % \
               (self.intCenterX, self.intCenterY, self.intCenterX_r, self.intCenterY_r, self.intBoundingRectWidth,
                self.intBoundingRectHeight, self.intBoundingRectArea, self.fltAspectRatio, self.fltExtent)