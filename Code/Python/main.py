#!/usr/bin/python3
# (c) Shahar Gino, July-2017, sgino209@gmail.com

from sys import argv
from ast import literal_eval
from datetime import datetime
from decode_marks import decode_marks
from getopt import getopt, GetoptError
from cv2 import imread, imwrite, resize
from os import path, makedirs, getcwd, chdir
from detect_marks import find_possible_marks
from preprocess import preprocess, imageEnhancement
from auxiliary import Struct, info, error, draw_roi, crop_roi_from_image

__version__ = "1.3"

# ---------------------------------------------------------------------------------------------------------------
def usage():
    script_name = path.basename(__file__)
    print('')
    print('%s -i [image_file]' % script_name)
    print('')
    print('Optional preprocssing flags:                  --PreprocessCvcSel --PreprocessMode --PreprocessGaussKernel --PreprocessThreshBlockSize')
    print('Optional preprocssing flags (cont.):          --PreprocessThreshweight --PreprocessMorphKernel --PreprocessMedianBlurKernel')
    print('Optional preprocssing flags (cont.):          --PreprocessCannyThr --imgEnhancementEn')
    print('Optional marks-detection flags:               --MinPixelWidth --MaxPixelWidth --MinPixelHeight --MaxPixelHeight --MinAspectRatio --MaxAspectRatio')
    print('Optional marks-detection flags (cont.):       --MinPixelArea --MaxPixelArea --MaxDrift --MarksRows --MarksCols --ROI')
    print('Optional marks-detection flags (cont.):       --FindContoursMode --HoughParams, --perspectiveMode')
    print('Optional misc. flags:                         --debug --version')
    print('')
    print('Note about HoughParams settings (relevant only when FindContoursMode="Hough"):')
    print('   HoughParams = (dp, minDist, param1, param2, minRadius, maxRadius)')
    print('   (-) dp ---------> Large dp values -->  smaller accumulator array')
    print('   (-) minDist ----> Min distance between the detected circles centers')
    print('   (-) param1 -----> Gradient value used to handle edge detection')
    print('   (-) param2 -----> Accumulator thresh val (smaller = more circles)')
    print('   (-) minRadius --> Minimum size of the radius (in pixels)')
    print('   (-) maxRadius --> Maximum size of the radius (in pixels)')
    print('')
    print('Note about ROI settings:')
    print('   (-) Option 1:  ROI = (startX, startY, width, height)')
    print('   (-) Option 2:  ROI = (startX, startY, R)  --->  width=height=R')
    print('   (-) Option 3:  ROI = (0,0) --->  ROI equals to whole input image')
    print('')
    print('Note that input image is automatically being resized for 1600x1200, so ROI shall be set accordingly')
    print('')

# ---------------------------------------------------------------------------------------------------------------
def main(_argv):

    # Default parameters:
    args = Struct(
        ImageFile="/Users/shahargino/Documents/ImageProcessing/Bracelet_decoder/Database/180717/24.png",
        PreprocessCvcSel = "V",
        PreprocessMode = "Legacy",
        PreprocessGaussKernel=(5, 5),
        PreprocessThreshBlockSize=19,
        PreprocessThreshweight=7,
        PreprocessMorphKernel=(3, 3),
        PreprocessMedianBlurKernel=13,
        PreprocessCannyThr=80,
        ROI=(0, 0),
        MinPixelWidth=7,
        MaxPixelWidth=30,
        MinPixelHeight=7,
        MaxPixelHeight=30,
        MinAspectRatio=0.6,
        MaxAspectRatio=2.5,
        MinPixelArea=150,
        MaxPixelArea=600,
        MinExtent=0.4,
        MaxExtent=0.9,
        MaxDrift=2.5,
        MarksRows=3,
        MarksCols=10,
        imgEnhancementEn=False,
        perspectiveMode=0,
        FindContoursMode="Legacy",
        HoughParams=(-1, -1, -1, -1, -1, -1),
        debugMode=False
    )

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..
    # User-Arguments parameters (overrides Defaults):
    try:
        opts, user_args = getopt(_argv, "hvi:", ["PreprocessCvcSel=", "PreprocessMode=", "PreprocessGaussKernel=",
                                                 "PreprocessThreshBlockSize=", "PreprocessThreshweight=",
                                                 "PreprocessMorphKernel=", "PreprocessMedianBlurKernel=",
                                                 "PreprocessCannyThr=", "ROI=",
                                                 "MinPixelWidth=", "MaxPixelWidth=",
                                                 "MinPixelHeight=", "MaxPixelHeight=",
                                                 "MinAspectRatio=", "MaxAspectRatio=",
                                                 "MinPixelArea=", "MaxPixelArea=",
                                                 "MinExtent=", "MaxExtent=",
                                                 "MaxDrift=", "MarksRows=", "MarksCols=", "imgEnhancementEn",
                                                 "perspectiveMode=", "FindContoursMode=", "HoughParams=",
                                                 "debug", "version"])

        for opt, user_arg in opts:
            if opt == '-h':
                usage()
                exit()
            elif opt in "-i":
                args.ImageFile = user_arg
            elif opt in "--PreprocessCvcSel":
                args.PreprocessCvcSel = user_arg
            elif opt in "--PreprocessMode":
                args.PreprocessMode = user_arg
            elif opt in "--PreprocessGaussKernel":
                args.PreprocessGaussKernel = literal_eval(user_arg)
            elif opt in "--PreprocessThreshBlockSize":
                args.PreprocessThreshBlockSize = int(user_arg)
            elif opt in "--PreprocessThreshweight":
                args.PreprocessThreshweight = int(user_arg)
            elif opt in "--PreprocessMorphKernel":
                args.PreprocessMorphKernel = literal_eval(user_arg)
            elif opt in "--PreprocessMedianBlurKernel":
                args.PreprocessMedianBlurKernel = int(user_arg)
            elif opt in "--PreprocessCannyThr":
                args.PreprocessCannyThr = int(user_arg)
            elif opt in "--ROI":
                args.ROI = literal_eval(user_arg)
            elif opt in "--MinPixelWidth":
                args.MinPixelWidth = float(user_arg)
            elif opt in "--MaxPixelWidth":
                args.MaxPixelWidth = float(user_arg)
            elif opt in "--MinPixelHeight":
                args.MinPixelHeight = float(user_arg)
            elif opt in "--MaxPixelHeight":
                args.MaxPixelHeight = float(user_arg)
            elif opt in "--MinAspectRatio":
                args.MinAspectRatio = float(user_arg)
            elif opt in "--MaxAspectRatio":
                args.MaxAspectRatio = float(user_arg)
            elif opt in "--MinPixelArea":
                args.MinPixelArea = float(user_arg)
            elif opt in "--MaxPixelArea":
                args.MaxPixelArea = float(user_arg)
            elif opt in "--MinExtent":
                args.MinExtent = float(user_arg)
            elif opt in "--MaxExtent":
                args.MaxExtent = float(user_arg)
            elif opt in "--MaxDrift":
                args.MaxDrift = float(user_arg)
            elif opt in "--MarksRows":
                args.MarksRows = int(user_arg)
            elif opt in "--MarksCols":
                args.MarksCols = int(user_arg)
            elif opt in "--imgEnhancementEn":
                args.imgEnhancementEn = True
            elif opt in "--perspectiveMode":
                args.perspectiveMode = int(user_arg)
            elif opt in "--FindContoursMode":
                args.FindContoursMode = user_arg
            elif opt in "--HoughParams":
                args.HoughParams = literal_eval(user_arg)
            elif opt in "--debug":
                args.debugMode = True
            elif opt in "--version" or opt == '-v':
                info("BraceletDecoder version: %s" % __version__)
                exit()

    except GetoptError as e:
        error(str(e))
        usage()
        exit(2)

    # -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- .. -- ..

    # Load input image:
    frame_orig = imread(args.ImageFile)
    height, width, _ = frame_orig.shape

    # Create a working environment (debugMode):
    if args.debugMode:
        envpath = datetime.now().strftime("results_%d%m%y_%H%M%S_") + args.ImageFile.split('/')[-1].replace('.', '_')
        if not path.exists(envpath):
            makedirs(envpath)
        cwd = getcwd()
        chdir(envpath)

    # Resizing:
    if args.PreprocessMode == "Legacy":
        resizingVec = (1600,1200)
        if (width < height):
            resizingVec = resizingVec[::-1]
    elif args.PreprocessMode == "BlurAndCanny":
        resizingVec = (1120,840)
    else:
        error("Unsupported PreprocessMode mode: %s" % args.PreprocessMode)

    # ROI cropping:
    if args.PreprocessMode == "Legacy":
        imgResized = resize(frame_orig, resizingVec)
        imgCropped = crop_roi_from_image(imgResized, args.ROI)
        image = imgCropped
    elif args.PreprocessMode == "BlurAndCanny":
        imgCropped = crop_roi_from_image(frame_orig, args.ROI)
        imgResized = resize(imgCropped, resizingVec)
        image = imgResized

    # Image enhancement:
    if (args.imgEnhancementEn):
        imgEnhanced = imageEnhancement(image, 2, (8,8), 3, args.debugMode)
    else:
        imgEnhanced = image

    # Preprocess:
    frame_gray, frame_thresh = preprocess(imgEnhanced,
                                          args.PreprocessCvcSel,
                                          args.PreprocessMode,
                                          args.PreprocessGaussKernel,
                                          args.PreprocessThreshBlockSize,
                                          args.PreprocessThreshweight,
                                          args.PreprocessMorphKernel,
                                          args.PreprocessMedianBlurKernel,
                                          args.PreprocessCannyThr)

    # Find bracelet marks:
    possible_marks, rotation_angle = find_possible_marks(frame_thresh,
                                                         args.MinPixelWidth,
                                                         args.MaxPixelWidth,
                                                         args.MinPixelHeight,
                                                         args.MaxPixelHeight,
                                                         args.MinAspectRatio,
                                                         args.MaxAspectRatio,
                                                         args.MinPixelArea,
                                                         args.MaxPixelArea,
                                                         args.MinExtent,
                                                         args.MaxExtent,
                                                         args.MaxDrift,
                                                         args.perspectiveMode,
                                                         args.FindContoursMode,
                                                         args.HoughParams,
                                                         args.debugMode)

    # Encode marks:
    code = decode_marks(possible_marks,
                        args.MarksRows,
                        args.MarksCols,
                        frame_thresh.shape,
                        rotation_angle,
                        args.debugMode)

    info("Code = %s" % code)

    if args.debugMode:

        imwrite("frame_orig.jpg", draw_roi(frame_orig, args.ROI))
        imwrite("frame_gray.jpg", frame_gray)
        imwrite("frame_thresh.jpg", frame_thresh)

        # Restore path:
        chdir(cwd)

if __name__ == "__main__":

    main(argv[1:])
