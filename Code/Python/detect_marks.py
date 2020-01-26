#!/usr/bin/python
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from copy import deepcopy
from possible_mark import PossibleMark
from auxiliary import Colors, distance_mse, debug, error
from numpy import zeros, uint8, median, array, linalg, mean, arctan2, pi, cos, sin, float32, sqrt
from cv2 import findContours, RETR_LIST, CHAIN_APPROX_SIMPLE, drawContours, imwrite, putText, FONT_HERSHEY_SIMPLEX, \
    findHomography, perspectiveTransform, polylines, LINE_AA

# ---------------------------------------------------------------------------------------------------------------
def find_possible_marks(frame_thresh, MinPixelWidth, MaxPixelWidth, MinPixelHeight, MaxPixelHeight,
                        MinAspectRatio, MaxAspectRatio, MinPixelArea, MaxPixelArea, MinExtent, MaxExtent,
                        MaxDrift, perspectiveMode, debugMode=False):
    """ Find all possible bracelet marks (finds all contours that could be representing marks) """

    # Initialization:
    possible_marks_list = []
    frame_thresh_copy = frame_thresh.copy()

    # Find all contours in the image:
    _, contours, _ = findContours(frame_thresh_copy, RETR_LIST, CHAIN_APPROX_SIMPLE)

    # Foreach contour, check if it describes a possible character:
    height, width = frame_thresh_copy.shape
    frame_contours = zeros((height, width, 3), uint8)
    possible_marks_cntr = 0
    for i in range(0, len(contours)):

        # Register the contour as a possible character (+calculate intrinsic metrics):
        possible_mark = PossibleMark(contours[i],
                                     MinPixelWidth, MaxPixelWidth,
                                     MinPixelHeight, MaxPixelHeight,
                                     MinAspectRatio, MaxAspectRatio,
                                     MinPixelArea, MaxPixelArea,
                                     MinExtent, MaxExtent)

        # If contour is a possible char, increment count of possible chars and add to list of possible chars:
        if possible_mark.check_if_possible_mark():
            possible_marks_cntr += 1
            possible_marks_list.append(possible_mark)

        if debugMode:
            drawContours(frame_contours, contours, i, Colors.white)

    if len(possible_marks_list) == 0:
        return possible_marks_list, 0

    # Remove outliers in a PCA scheme, i.e. possible marks which are too faraway from the group or interiors:
    possible_marks_wo_outliers = remove_outliers(possible_marks_list, MaxDrift, debugMode)

    # Rotation and Perspective alignments:
    rotation_angle_deg = 0
    if len(possible_marks_wo_outliers) > 0:

        # Rotation Alignment (SVD decomposition):
        rotation_angle_deg, centroid = rotation_alignment(possible_marks_wo_outliers, debugMode)

        # Perspective Alignment (Homography+PerspectiveWarp):
        possible_marks_final = deepcopy(possible_marks_wo_outliers)
        rect_src, rect_dst = perspective_alignment(possible_marks_final, perspectiveMode, rotation_angle_deg, debugMode)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    if debugMode:
        frame_possible_marks = zeros((height, width, 3), uint8)

        for possible_mark in possible_marks_wo_outliers:
            drawContours(frame_possible_marks, [possible_mark.contour], 0, Colors.white)
            frame_possible_marks[possible_mark.intCenterY-3:possible_mark.intCenterY+3,
                                 possible_mark.intCenterX-3:possible_mark.intCenterX+3, 2] = 255
            frame_possible_marks[possible_mark.intCenterY_r-3:possible_mark.intCenterY_r+3,
                                 possible_mark.intCenterX_r-3:possible_mark.intCenterX_r+3, 0] = 255

        for possible_mark in possible_marks_final:
            frame_possible_marks[possible_mark.intCenterY_r - 3:possible_mark.intCenterY_r + 3,
                                 possible_mark.intCenterX_r - 3:possible_mark.intCenterX_r + 3, 1:3] = 255

        putText(frame_possible_marks, "Original", (10, 30), FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        putText(frame_possible_marks, "Rotation fix (SVD)", (10, 70), FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        putText(frame_possible_marks, "Centroid", (10, 110), FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        putText(frame_possible_marks, "Perspective fix", (10, 150), FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        if perspectiveMode == 1:
            frame_possible_marks = polylines(frame_possible_marks, array([rect_src]), True, (255, 0, 0), 1, LINE_AA)
            frame_possible_marks = polylines(frame_possible_marks, array([rect_dst]), True, (0, 255, 255), 1, LINE_AA)

        if len(frame_possible_marks) > 0:
            X_xc, X_yc = centroid
            frame_possible_marks[X_yc-3:X_yc+3, X_xc-3:X_xc+3, 1] = 255

        debug("Amount of detected contours: %d" % len(contours), True)
        debug("Amount of possible marks: %d" % possible_marks_cntr, True)
        debug("Amount of possible marks w/o outliers: %d" % len(possible_marks_wo_outliers), True)
        debug("Rotation: %.2f" % rotation_angle_deg, True)
        imwrite("img_contours_all.jpg", frame_contours)
        imwrite("img_possible_marks_.jpg", frame_possible_marks)

    return possible_marks_final, rotation_angle_deg

# ---------------------------------------------------------------------------------------------------------------
def remove_outliers(possible_marks_list, MaxDrift, debugMode):
    """ Remove outliers in a given 2D data-set of possible-marks """

    possible_marks_list_final = []

    # Extract marks relevant data:
    X = array([[x.intCenterX, x.intCenterY] for x in possible_marks_list])
    median_x = median(X[:, 0])
    median_y = median(X[:, 1])

    dist = []
    for possible_mark in possible_marks_list:
        p1 = (possible_mark.intCenterX, possible_mark.intCenterY)
        p2 = (median_x, median_y)
        d = distance_mse(p1,p2)
        dist.append(d)

    median_dist = median(dist)

    debug("median_x=%.2f, median_y=%.2f, median_dist=%.2f" % (median_x, median_y, median_dist), debugMode)

    # Exclude marks with a too-high drift or interiors:
    for k in range(len(possible_marks_list)):

        dbg = ""

        possible_mark = possible_marks_list[k]
        dr = dist[k]/median_dist if median_dist else 0.

        is_interior = False
        for l in range(len(possible_marks_list)):
            if l == k:
                continue
            p1 = (possible_mark.intCenterX, possible_mark.intCenterY)
            p2 = (possible_marks_list[l].intCenterX, possible_marks_list[l].intCenterY)
            d = distance_mse(p1, p2)
            if d < 2*MaxDrift and possible_mark.intBoundingRectArea < possible_marks_list[l].intBoundingRectArea:
                is_interior = True
                dbg = "(X)"

        if dr < MaxDrift and not is_interior:
            possible_marks_list_final.append(possible_mark)
            dbg = "(*)"

        debug("possible_mark=%s, dist[%d]=%.2f, disr_r=%.2f %s" % (possible_mark, k, dist[k], dr, dbg), debugMode)

    return possible_marks_list_final

# ---------------------------------------------------------------------------------------------------------------
def rotation_alignment(possible_marks_list, debugMode):
    """ SVD decomposition for rotation alignment, adds intCenterX/Y_r attributes and returns angle and centroid estimation """

    # Extract marks relevant data:
    X = array([[x.intCenterX, x.intCenterY] for x in possible_marks_list])

    # Calculate Centroid:
    X_xc = int(mean(X[:, 0]))
    X_yc = int(mean(X[:, 1]))
    centroid = [X_xc, X_yc]

    # Calculate covariance matrix (H):
    H = X - array(centroid)
    debug("Covariance matrix (H):", debugMode)
    if debugMode:
      print(H.T)

    # SVD decomposition:
    U, S, Vt = linalg.svd(H, full_matrices=True)

    # Calculate rotation angle:
    rotation_angle = arctan2([Vt[0, 1], Vt[1, 1]],
                             [Vt[0, 0], Vt[1, 0]])[0]
    rotation_angle_deg = rotation_angle * (180 / pi)

    # Rotation alignment:
    R = array([[cos(rotation_angle), -sin(rotation_angle)],
               [sin(rotation_angle), cos(rotation_angle)]])

    X_fixed = H.dot(R) + array([X_xc, X_yc])

    for k in range(len(possible_marks_list)):
        possible_marks_list[k].intCenterX_r = int(X_fixed[k][0])
        possible_marks_list[k].intCenterY_r = int(X_fixed[k][1])
        debug("possible_mark=%s" % possible_marks_list[k], debugMode)

    return rotation_angle_deg, centroid

# ---------------------------------------------------------------------------------------------------------------
def perspective_alignment(possible_marks_list, perspectiveMode, rotation_angle_deg, debugMode):
    """ Wrapper function for Perspective Alignment """

    if perspectiveMode == 0:
        return perspective_alignment_opt0(possible_marks_list, rotation_angle_deg, debugMode)

    elif perspectiveMode == 1:
        return perspective_alignment_opt1(possible_marks_list, debugMode)

    else:
        error("Invalid perspectiveMode (%d)" % perspectiveMode)

    return [],[]

# ---------------------------------------------------------------------------------------------------------------
def perspective_alignment_opt0(possible_marks_list, rotation_angle_deg, debugMode):
    """ TBD """

    rect_src = []
    rect_dst = []

    # Extract marks relevant data:
    X = array([[x.intCenterX_r, x.intCenterY_r] for x in possible_marks_list])

    # Calculate meanX:
    mean_x = int(mean(X[:, 0]))

    # Update marks coordinates (adaptive with angle):
    for mark in possible_marks_list:
        dist_x = abs(mark.intCenterX_r - mean_x)
        if abs(rotation_angle_deg) > 90:
            if abs(rotation_angle_deg) < 170:
                mark.intCenterY_r -= int(2 * sqrt(dist_x))
            else:
                mark.intCenterY_r -= int(1 * sqrt(dist_x))
        else:
            mark.intCenterY_r += int(2 * sqrt(dist_x))

    debug("(xR,yR) after Perspective Fix:", debugMode)
    if debugMode:
        X = array([[x.intCenterX_r, x.intCenterY_r] for x in possible_marks_list])
        print X.T

    return rect_src, rect_dst

# ---------------------------------------------------------------------------------------------------------------
def perspective_alignment_opt1(possible_marks_list, debugMode):
    """ Calculate the src2dst homography and apply a Perspective Warp, in order to fix camera lens geometric distortion """

    # Option1:        |   Option2:
    #                 |
    #   -   ...  X2   |     X3  ...  X1
    #   .   ...   .   |     .  ...  .
    #   X1  ...  X3   |     X2  ...  -
    #
    # 1. Find two largest Xs neighbours (<W/2), which are vertically spaced by at least 2*H --> if found, we're in Option1
    #    Else --> Find two smallest Xs neighbours (<W/2), which are vertically spaced by at least 2*H --> if found, we're in Option2
    #    Else --> ERROR
    #
    # 2. If we're in Option1 -->  X1 = smallest X with largest Y coordinate
    #                             P0 (marked with '-'): { X0, Y0 - 4*H }
    #    Else (option2) ------->  X1 = largest X with smallest Y coordinate
    #                             P0 (marked with '-'): { X0, Y0 + 4*H }
    #
    # 3. Calculate Homography (src2dst):   {P0,P1,P2,P3} --> rectangle, based on min/max combinations
    #
    # 4. Perspective Warp
    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    # Extract marks relevant data:
    X = [[x.intCenterX_r, x.intCenterY_r, x.intBoundingRectWidth, x.intBoundingRectHeight] for x in possible_marks_list]
    X.sort()
    X = array(X)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    # Option1:
    if perspective_warp_x23_dist_check(X[-1,:], X[-3,:]):

        option_num = 1

        p2 = X[-1, 0:2]
        p3 = X[-3, 0:2]
        if X[-3,1] < X[-1,1]:
            p2 = X[-3, 0:2]
            p3 = X[-1, 0:2]

    elif perspective_warp_x23_dist_check(X[-1,:], X[-2,:]):

        option_num = 1

        p2 = X[-1, 0:2]
        p3 = X[-2, 0:2]
        if X[-2, 1] < X[-1, 1]:
            p2 = X[-2, 0:2]
            p3 = X[-1, 0:2]

    elif perspective_warp_x23_dist_check(X[-2,:], X[-3,:]):

        option_num = 1

        p2 = X[-2, 0:2]
        p3 = X[-3, 0:2]
        if X[-3, 1] < X[-2, 1]:
            p2 = X[-3, 0:2]
            p3 = X[-2, 0:2]

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Option2:
    elif perspective_warp_x23_dist_check(X[0,:], X[2,:]):

        option_num = 2

        p2 = X[0, 0:2]
        p3 = X[2, 0:2]
        if X[2,1] > X[0,1]:
            p2 = X[2,0:2]
            p3 = X[0,0:2]

    elif perspective_warp_x23_dist_check(X[0,:], X[1,:]):

        option_num = 2

        p2 = X[0, 0:2]
        p3 = X[1, 0:2]
        if X[1, 1] > X[0, 1]:
            p2 = X[1, 0:2]
            p3 = X[0, 0:2]

    elif perspective_warp_x23_dist_check(X[1,:], X[2,:]):

        option_num = 2

        p2 = X[1, 0:2]
        p3 = X[2, 0:2]
        if X[2, 1] > X[1, 1]:
            p2 = X[2, 0:2]
            p3 = X[1, 0:2]

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Error (unexpected state):
    else:
        error("Unexpected perspective option! (neither 1 or 2)")
        return

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # P1:
    if option_num == 1:

        p0 = array([X[0,0], X[0,1] - 4*X[0,3]])
        p1 = X[0,0:2]
        if (abs(X[0,0] - X[1,0]) < mean([X[0,2], X[1,2]]) / 1.5) and X[1,1] > X[0,1]:
            p0 = array([X[1, 0], X[1, 1] - X[1, 3]])
            p1 = X[1, 0:2]

    else:

        p0 = array([X[-1, 0], X[-1, 1] + 4*X[-1, 3]])
        p1 = X[-1,0:2]
        if (abs(X[-1,0] - X[-2,0]) < mean([X[-1,2], X[-2,2]]) / 1.5) and X[-2,1] < X[-1,1]:
            p0 = array([X[-2, 0], X[0, 1] + X[-2, 3]])
            p1 = X[-2, 0:2]

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # Source rectangle:
    if option_num == 1:

        rect_src = [list(p0),
                    list(p1),
                    list(p3),
                    list(p2)]
    else:
        rect_src = [list(p3),
                    list(p2),
                    list(p0),
                    list(p1)]

    # Destination rectangle:
    min_x = min(X[:, 0])
    max_x = max(X[:, 0])
    min_y = min(X[:, 1])
    max_y = max(X[:, 1])

    rect_dst = [[min_x, min_y],
                [min_x, max_y],
                [max_x, max_y],
                [max_x, min_y]]

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    # Homography calculation:
    H, _ = findHomography(array(rect_src), array(rect_dst))
    src = float32(X[:,0:2]).reshape(-1,1,2)
                                                     # w = H_31 * src[i].x + H_32 * src[i].y + H_33 * 1
    # Perspective Warp (src-->dst):                  # dst[i].x = (H_11 * src[i].x + H_12 * src[i].y + H_13 * 1) / w
    dst = perspectiveTransform(src, H).astype(int)   # dst[i].y = (H_21 * src[i].x + H_22 * src[i].y + H_23 * 1) / w

    # Update marks coordinates:
    for mark in possible_marks_list:
        for k in range(len(X)):
            if X[k,0] == mark.intCenterX_r and X[k,1] == mark.intCenterY_r:
                mark.intCenterX_r = dst[k,0][0]
                mark.intCenterY_r = dst[k,0][1]

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    debug("Perspective: Option=%d" % option_num, debugMode)
    debug("Perspective: Rect_Src: p0=%s, p1=%s, p2=%s, p3=%s" % (rect_src[0], rect_src[1], rect_src[2], rect_src[3]), debugMode)
    debug("Perspective: Rect_Dst: p0=%s, p1=%s, p2=%s, p3=%s" % (rect_dst[0], rect_dst[1], rect_dst[2], rect_dst[3]), debugMode)

    if debugMode:
        debug("Perspective Homography Matrix (H):", True)
        print H
        debug("Perspective SRC points (marks):", True)
        print X[:,0:2].T
        debug("Perspective DST points (~H*SRC):", True)
        print dst[:,0].T

    return rect_src, rect_dst

# -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
def perspective_warp_x23_dist_check(x1,x2):
    """ Auxiliary function for Perspective Warp fix """

    return (abs(x1[0] - x2[0]) < mean([x1[2], x2[2]])/1.5) and (abs(x1[1] - x2[1]) > 2*mean([x1[3], x2[3]]))
