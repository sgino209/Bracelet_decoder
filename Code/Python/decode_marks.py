#!/usr/local/bin/python3
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from numpy import zeros, uint8, array, sort
from auxiliary import debug, error
from cv2 import putText, FONT_HERSHEY_SIMPLEX, imwrite

# ---------------------------------------------------------------------------------------------------------------
def decode_marks(marks_list, MarksRows, MarksCols, frame_shape, rotation_angle_deg, debugMode=False):

    if len(marks_list) < MarksRows:
        return

    # Extract XY min/max for the given marks:
    X = array([[x.intCenterX_r, x.intCenterY_r] for x in marks_list])

    min_x = min(X[:, 0])
    max_x = max(X[:, 0])
    min_y = min(X[:, 1]) + 5
    max_y = max(X[:, 1])
    if (max_y > 310):
        max_y -= 5

    # Prepare KNN origins:
    if 80 < abs(rotation_angle_deg) < 100:   # Adaptive scale fix
        min_x -= 1
        max_x += 1

    radius_y = (max_y - min_y) / (MarksRows - 1)
    radius_x = (max_x - min_x) / (MarksCols - 1)

    y_scale = list(range(min_y, max_y, int(radius_y))) if radius_y > 0 else [1]
    x_scale = list(range(min_x, max_x, int(radius_x))) if radius_x > 0 else [1]

    if len(y_scale) < MarksRows:
        y_scale.append(max_y)

    if len(x_scale) < MarksCols:
        x_scale.append(max_x)

    # For each KNN origin, seek for closest mark:
    debug("x_scale = " + str(x_scale), debugMode)
    debug("y_scale = " + str(y_scale), debugMode)

    code_str = ""
    for y in y_scale:
        for x in x_scale:
            ret = seek_for_mark(x, y, marks_list, int(radius_x), int(radius_y))
            code_str += "%s" % ret

    debug("code before flip: %s" % code_str, debugMode)

    # Code must start with '1' and end with '0', flip if not:
    if code_str[0] == '0' and code_str[-1] == '1':
        code_str = code_str[::-1]
        debug("code after flip:  %s" % code_str, debugMode)
    elif code_str[0] == code_str[-1]:
        error("Invalid code detected! (first mark equals to last mark)")

    code_hex_str = hex(int(code_str, 2))

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    # Debug:
    if debugMode:

        height, width = frame_shape
        aligned_frame = zeros((height, width, 3), uint8)

        for x in x_scale:
            for y in y_scale:
                aligned_frame[y-2:y+2,
                              x-2:x+2, 1] = 255
        for mark in marks_list:
            aligned_frame[mark.intCenterY-3:mark.intCenterY+3,
                          mark.intCenterX-3:mark.intCenterX+3, 2] = 255

            aligned_frame[mark.intCenterY_r-3:mark.intCenterY_r+3,
                          mark.intCenterX_r-3:mark.intCenterX_r+3, 0] = 255

        putText(aligned_frame, "Original", (10, 30), FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        putText(aligned_frame, "Rotation fix (SVD)", (10, 70), FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        putText(aligned_frame, "KNN origins", (10, 110), FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        imwrite("img_possible_marks_aligned.jpg", aligned_frame)

    return code_hex_str

# ---------------------------------------------------------------------------------------------------------------
def seek_for_mark(x, y, marks, w, h):
    """ Seek for a mark existence in a WxH neighbourhood around (x,y) coordinate """

    for mark in marks:
        x_range = range(x - int(w/2), x + int(w/2)+1)
        y_range = range(y - int(h/2), y + int(h/2)+1)
        for yy in y_range:
            for xx in x_range:
                if mark.intCenterX_r == xx and mark.intCenterY_r == yy:
                    return 1
    return 0
