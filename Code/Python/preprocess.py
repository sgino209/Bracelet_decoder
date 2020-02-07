#!/usr/bin/python3
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from cv2 import split, merge, GaussianBlur, medianBlur, adaptiveThreshold, getStructuringElement, morphologyEx, add, \
    subtract, cvtColor, createCLAHE, addWeighted, imwrite, resize, Canny, LUT, COLOR_BGR2HSV, COLOR_HSV2BGR,\
    ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY_INV, MORPH_RECT, MORPH_TOPHAT, MORPH_BLACKHAT
from scipy.interpolate import UnivariateSpline
from numpy import uint8, array, arange
from auxiliary import error

# ---------------------------------------------------------------------------------------------------------------
def preprocess(imgOriginal, PreprocessCvcSel, PreprocessMode, PreprocessGaussKernel, PreprocessThreshBlockSize,
               PreprocessThreshweight, PreprocessMorphKernel, PreprocessMedianBlurKernel, PreprocessCannyThr):
    """ CSC, Contrast stretch (morph.), Blurring and Adaptive-Threshold """

    # Color-Space-Conversion (CSC): switch from BGR to HSV and take "V" component:
    imgHSV = cvtColor(imgOriginal, COLOR_BGR2HSV)
    imgHSV_H, imgHSV_S, imgHSV_V = split(imgHSV)

    if PreprocessCvcSel == "H":
        imgGrayscale = imgHSV_H
    elif PreprocessCvcSel == "S":
        imgGrayscale = imgHSV_S
    elif PreprocessCvcSel == "V":
        imgGrayscale = imgHSV_V
    else:
        error("Unsupported PreprocessCvcSel mode: %s" % PreprocessCvcSel)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    if PreprocessMode == "Legacy":

        # Increase Contrast (morphological):
        imgMaxContrastGrayscale = maximizeContrast(imgGrayscale, PreprocessMorphKernel)

        # Blurring:
        imgBlurred = GaussianBlur(imgMaxContrastGrayscale, PreprocessGaussKernel, 0)

        # Adaptive Threshold:
        imgThresh = adaptiveThreshold(imgBlurred, 255.0, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY_INV, PreprocessThreshBlockSize, PreprocessThreshweight)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    elif PreprocessMode == "BlurAndCanny":

        # Blurring:
        imgBlurred = medianBlur(imgGrayscale, PreprocessMedianBlurKernel)

        # Canny Edge Detection:
        imgThresh = Canny(imgBlurred, PreprocessCannyThr/2, PreprocessCannyThr)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    else:
        error("Unsupported PreprocessMode mode: %s" % PreprocessMode)

    return imgBlurred, imgThresh

# ---------------------------------------------------------------------------------------------------------------
def maximizeContrast(imgGrayscale, PreprocessMorphKernel):
    """ Morphological filtering for increasing contrast: OutputImage = InputImage + TopHat - BlackHat """

    structuringElement = getStructuringElement(MORPH_RECT, PreprocessMorphKernel)

    imgTopHat = morphologyEx(imgGrayscale, MORPH_TOPHAT, structuringElement)      # = Image - Opening[Image] = Image - dilate[erode[Image]] --> "lowFreq"
    imgBlackHat = morphologyEx(imgGrayscale, MORPH_BLACKHAT, structuringElement)  # = Closing[Image] - Image = erode[dilate[Image]] - Image --> "highFreq"

    imgGrayscalePlusTopHat = add(imgGrayscale, imgTopHat)
    imgGrayscalePlusTopHatMinusBlackHat = subtract(imgGrayscalePlusTopHat, imgBlackHat)

    return imgGrayscalePlusTopHatMinusBlackHat

# ---------------------------------------------------------------------------------------------------------------
def imageEnhancement(imgOriginal, clahe_clipLimit, clahe_tileGridSize, gamma, debugMode=False):
    """ Image enhancement, applies Warming effect (+CLAHE) and Saturation effect (+Gamma) """

    # Refs: (1) http://www.askaswiss.com/2016/02/how-to-manipulate-color-temperature-opencv-python.html
    #       (2) http://www.pyimagesearch.com/2015/10/05/opencv-gamma-correction
    #       (3) http://docs.opencv.org/trunk/d3/dc1/tutorial_basic_linear_transform.html
    #       (4) http://docs.opencv.org/2.4/doc/tutorials/core/basic_linear_transform/basic_linear_transform.html

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def adjust_gamma(image, gamma=1.0):
        """ Build and apply a lookup table mapping the pixel values [0, 255] to their adjusted gamma values """

        invGamma = 1.0 / gamma
        table = array([((i / 255.0) ** invGamma) * 255 for i in arange(0, 256)]).astype("uint8")

        return LUT(image, table)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    def create_LUT_8UC1(x, y):
        """" Basic LUT generation, returns a 256-element list of the interpolated f(x) values for every value of x. """

        spl = UnivariateSpline(x, y)
        return spl(range(256))

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    incr_ch_lut = create_LUT_8UC1([0, 64, 128, 192, 256],
                                  [0, 70, 140, 210, 256])
    decr_ch_lut = create_LUT_8UC1([0, 64, 128, 192, 256],
                                  [0, 30, 80, 120, 192])

    # Warming effect (R,G incr.) + CLAHE:
    b, g, r = split(imgOriginal)
    c_r = LUT(r, incr_ch_lut).astype(uint8)
    c_b = LUT(b, decr_ch_lut).astype(uint8)
    clahe = createCLAHE(clipLimit=clahe_clipLimit, tileGridSize=clahe_tileGridSize)
    B = clahe.apply(c_b)
    G = clahe.apply(g)
    R = clahe.apply(c_r)
    imgWarm = merge((B, G, R))

    # Saturation effect (S incr.) + Gamma:
    h, s, v = split(cvtColor(imgWarm, COLOR_BGR2HSV))
    c_s = LUT(s, incr_ch_lut).astype(uint8)
    imgSat = cvtColor(merge((h, c_s, v)), COLOR_HSV2BGR)
    imgGamma = adjust_gamma(imgSat, gamma=gamma)
    
    # Sharpening:                                          # Using a gaussian smoothing filter and subtracting the
    imgOut = GaussianBlur(imgGamma, (0,0), 3)              # smoothed version from the original image (in a weighted
    imgOut = addWeighted(imgGamma, 1.5, imgOut, -0.5, 0)   # way so the values of a constant area remain constant)

    # Debug:
    if (debugMode):
        imwrite("img_original_before_enhancement.jpg", imgOriginal)
        imwrite("img_original_after_enhancement.jpg",  imgOut)

    return imgOut

