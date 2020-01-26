#!/usr/local/bin/python3
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from numpy import sqrt
from cv2 import rectangle, putText, FONT_HERSHEY_SIMPLEX, getRectSubPix

# ---------------------------------------------------------------------------------------------------------------
# Python structuring way:
class Struct:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

# ---------------------------------------------------------------------------------------------------------------
# Color vectors:
Colors = Struct(
    white=(255.0, 255.0, 255.0),
    green=(0.0, 255.0, 0.0),
    red=(0.0, 0.0, 255.0),
    yellow=(0.0, 255.0, 255.0)
)

# ---------------------------------------------------------------------------------------------------------------
def distance_mse(p1,p2):
    """ Auxiliary function for a MSE calculation """

    return sqrt(((p1[0] - p2[0]) ** 2) + ((p1[1] - p2[1]) ** 2))


# ---------------------------------------------------------------------------------------------------------------
def draw_roi(frame, roi):
    """ Auxiliary function for drawing a given ROI on a given frame """

    imgH, imgW, _ = frame.shape

    x1, y1, x2, y2 = 0, 0, 0, 0
    if len(roi) == 4:
        x1, y1, x2, y2 = roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3]
    elif len(roi) == 3:
        x1, y1, x2, y2 = roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[2]
    elif roi[0] == 0:
        x1, y1, x2, y2 = 0, 0, imgW, imgH

    rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
    putText(frame, "ROI", (x1 + int(0.45 * (x2 - x1)), y1 - 10), FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return frame

# ---------------------------------------------------------------------------------------------------------------
def crop_roi_from_image(frame, roi):
    """ Crop a given ROI from a given Image; ROI=(startX,startY,W,H) """

    if len(roi) == 2 and roi[0] == 0 and roi[1] == 0:
        imgCropped = frame

    else:
        roiW = roi[2]

        if len(roi) == 4:
            roiH = roi[3]
        else:
            roiH = roi[2]

        roiCx = roi[0] + roiW / 2.0
        roiCy = roi[1] + roiH / 2.0

        imgCropped = getRectSubPix(frame, (roiW, roiH), (roiCx, roiCy))

        info("ROI size: (Cx,Cy)=(%.2f,%.2f), WxH=%dx%d" % (roiCx, roiCy, roiW, roiH))

    return imgCropped

# ---------------------------------------------------------------------------------------------------------------
def debug(message, debugMode):
    """ Auxiliary function for a conditional debug printout """

    if debugMode:
        print("DEBUG: %s" % message)

# ---------------------------------------------------------------------------------------------------------------
def info(message):
    """ Auxiliary function for a info printout """

    print("INFO: %s" % message)

# ---------------------------------------------------------------------------------------------------------------
def error(message):
    """ Auxiliary function for a error printout """

    print("\033[1;31mERROR\033[0m: %s" % message)
