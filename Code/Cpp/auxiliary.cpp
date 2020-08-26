// Bracelet-Decoder algo app
// (c) Shahar Gino, September-2017, sgino209@gmail.com

#include "auxiliary.hpp"
#include "preprocess.hpp"

extern void preprocess(cv::Mat &imgOriginal, cv::Mat &imgGrayscale, cv::Mat &imgThresh, uint_xy_t PreprocessGaussKernel, 
                       unsigned int PreprocessThreshBlockSize, unsigned int PreprocessThreshweight, uint_xy_t PreprocessMorphKernel,
                       unsigned int PreprocessMedianBlurKernel, unsigned int PreprocessCannyThr);

extern void set_xy(uint_xy_t *d, std::string str);
extern void set_x4(uint_x4_t *d, std::string str);
extern void set_x6(uint_x6_t *d, std::string str);

decoder_res_t decode_frame_new(args_t args) {

  decoder_res_t res;
  std::string code;
  double rotation_angle;
  mark_list_t possible_marks;
  cv::Mat frame_orig, frame_gray, frame_thresh, imgCropped, imgResized, imgEnhanced;

  if (args.debugMode) {
    info("Starting C++ code");
  }
  
  // Load input image:
  if (!args.ImageMat.empty()) {
    frame_orig = args.ImageMat;
  }
  else {
    frame_orig = cv::imread(args.ImageFile);
  }

  // Resizing preparations:
  cv::Size s = frame_orig.size();
  cv::Size resizingVec;
  if (args.PreprocessMode == "Legacy") {
    resizingVec = resizingVec1;
    if (s.width < s.height) {
      resizingVec = resizingVec2;
    }
  }
  else if (args.PreprocessMode == "BlurAndCanny") {
    //resizingVec = resizingVec3;
    resizingVec = resizingVec4;
  }
  else {
      error("Unsupported PreprocessMode mode: " + args.PreprocessMode);
  }
  
  // Resizing and ROI cropping:
  cv::Mat image;
  if (args.PreprocessMode == "Legacy") {
    cv::resize(frame_orig.clone(), imgResized, resizingVec);
    imgCropped = crop_roi_from_image(imgResized, args.ROI);
    image = imgCropped;
  }
  else if (args.PreprocessMode == "BlurAndCanny") {
    imgCropped = crop_roi_from_image(frame_orig, args.ROI);
    cv::resize(imgCropped.clone(), imgResized, resizingVec);
    image = imgResized;
  }

  // Image enhancement:
  if (args.imgEnhancementEn) {
    imgEnhanced = imageEnhancement(image, 2, 8, 3, args.debugMode); //clahe_clipLimit=2, clahe_tileGridSize=8, gamme=3
  }
  else {
    imgEnhanced = image.clone();
  }

  unsigned int sweep_space = 0;
  std::map<std::string,unsigned int> scoreboard_winners;

  for (unsigned int MedianBlurKernel=args.PreprocessMedianBlurKernel.x; MedianBlurKernel<=args.PreprocessMedianBlurKernel.y; MedianBlurKernel+=2) {
    for (unsigned int CannyThr=args.PreprocessCannyThr.x; CannyThr<=args.PreprocessCannyThr.y; CannyThr+=10) {
        
      // Pre-processing (CSC --> contrast --> blur --> threshold):
      preprocess(imgEnhanced,
                 frame_gray,
                 frame_thresh,
                 args.PreprocessCvcSel,
                 args.PreprocessMode,
                 args.PreprocessGaussKernel,
                 args.PreprocessThreshBlockSize,
                 args.PreprocessThreshweight,
                 args.PreprocessMorphKernel,
                 MedianBlurKernel,
                 CannyThr);
  
      res.args = args;
      res.debug_imgs["frame_orig"] = draw_roi(frame_orig, args.ROI);
      res.debug_imgs["frame_gray"] = frame_gray;
      res.debug_imgs["frame_thresh"] = frame_thresh;

      // Find bracelet marks:
      rotation_angle = find_possible_marks(possible_marks,
                                           frame_gray,
                                           frame_thresh,
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
                                           args.MinTexture,
                                           args.MaxTexture,
                                           args.MaxDrift,
                                           args.PerspectiveMode,
                                           args.FindContoursMode,
                                           args.HoughParams.x1,
                                           args.HoughParams.x2,
                                           args.HoughParams.x3,
                                           args.HoughParams.x4,
                                           args.HoughParams.x5,
                                           args.HoughParams.x6,
                                           args.debugMode,
                                           &res.debug_imgs);

      // Decode marks:
      code = decode_marks(possible_marks,
                          args.MarksRows,
                          args.MarksCols,
                          frame_thresh.size(),
                          rotation_angle,
                          args.debugMode,
                          &res.debug_imgs);
        
      if (args.debugMode) {

        cv::imwrite("frame_orig.jpg", draw_roi(frame_orig, args.ROI));
        cv::imwrite("frame_gray.jpg", frame_gray);
        cv::imwrite("frame_thresh.jpg", frame_thresh);
      }
     
      if (code != "N/A") {
                      
        if (scoreboard_winners.find(code) == scoreboard_winners.end()) {
          scoreboard_winners[code] = 1;
        }
        else {
          scoreboard_winners[code]++;
        }
        sweep_space++;
      
        if (true || args.debugMode) {
          char buffer[1000];
          sprintf(buffer, "MedianBlurKernel=%d, CannyThr=%d, code=%s", MedianBlurKernel, CannyThr, code.c_str());
          debug(buffer);
        }
      }  
    }
  }
        
  unsigned int maxVal = 0;
  unsigned int maxVal2 = 0;
  for (auto it = scoreboard_winners.begin(); it != scoreboard_winners.end(); ++it) {
    std::cout << it->first << " --> " << it->second << std::endl;
    if (it->second > maxVal) {
      maxVal2 = maxVal;
      maxVal = it->second;
      code = it->first;
    }
  }

  double confidence = (maxVal - maxVal2) / double(sweep_space);
  if (confidence < 0.1) {
    code = "N/A";
  }
  
  char buffer[1000];
  sprintf(buffer, "Confidence=%.2f", confidence);
  debug(buffer);

  res.code = code;
  res.confidence = confidence;

  return res;
}

// ------------------------------------------------------------------------------------------------------------------------------

std::string decode_frame(args_t args) {

  return decode_frame_new(args).code.c_str();
}

// ------------------------------------------------------------------------------------------------------------------------------
void generic_message(std::string message, std::string severity) {
    
  char buffer[1000];
  sprintf(buffer, "%s: %s", severity.c_str(), message.c_str());
  
  std::cout << buffer << std::endl << std::flush;
}

void info(std::string message)  { generic_message(message, "INFO");  }
void debug(std::string message) { generic_message(message, "DEBUG"); }
void error(std::string message) { generic_message(message, "ERROR"); }

// ------------------------------------------------------------------------------------------------------------------------------
cv::Mat draw_roi(cv::Mat &frame, uint_x4_t roi) {
    
  cv::Size s = frame.size();
  int imgH = s.height;
  int imgW = s.width;
  unsigned int x1=0, y1=0, x2=0, y2=0;

  if (roi.len >= 3) {
    x1 = roi.x1;
    y1 = roi.x2;
    x2 = roi.x3;
    y2 = (roi.len == 4) ? roi.x4 : roi.x3;
  }
  else if (roi.x1 == 0) {
    x2 = imgW;
    y2 = imgH;
  }

  cv::rectangle(frame, cv::Rect(x1, y1, x2, y2), SCALAR_RED, 2);
  cv::putText(frame, "ROI", cv::Point(x1 + (int)(0.45 * x2), y1 - 10) , cv::FONT_HERSHEY_SIMPLEX, 1, SCALAR_RED, 2);

  return frame;
}

// ------------------------------------------------------------------------------------------------------------------------------
cv::Mat crop_roi_from_image(cv::Mat &frame, uint_x4_t roi) {
    
    cv::Mat imgCropped;
    
    if (roi.len == 2 && roi.x1 == 0 && roi.x2 == 0) {

      imgCropped = frame;
    }
    else {
        
      unsigned int roiW = roi.x3;
      unsigned int roiH = (roi.len == 4) ? roi.x4 : roi.x3;

      double roiCx = roi.x1 + roiW / 2.0;
      double roiCy = roi.x2 + roiH / 2.0;
   
      //if (frame.dims == 2) {
      //  cv::cvtColor(frame.clone(), frame, cv::COLOR_RGB2BGR);    
      //}
      cv::getRectSubPix(frame, 
                        cv::Size2f((float)roiW, (float)roiH),
                        cv::Point2f((float)roiCx, (float)roiCy),
                        imgCropped);

      char buffer[1000];
      sprintf(buffer, "ROI size: (Cx,Cy)=(%.2f,%.2f), WxH=%dx%d", roiCx, roiCy, roiW, roiH);
      info(buffer);
    }
     
    return imgCropped;
}

// ------------------------------------------------------------------------------------------------------------------------------
// Auxiliary function for a MSE calculation
double distance_mse(cv::Point2f p1, cv::Point2f p2) {

  return (double)(sqrt(pow((p1.x - p2.x),2) + pow((p1.y - p2.y),2)));
}

// ------------------------------------------------------------------------------------------------------------------------------
args_t load_default_args() {

  args_t args;

  args.ImageFile = "/Users/shahargino/Documents/ImageProcessing/Bracelet_decoder/Database/180717/24.jpg";
  args.PreprocessCvcSel = "V";
  args.PreprocessMode = "Legacy";
  set_xy(&args.PreprocessGaussKernel, "(5,5)");
  args.PreprocessThreshBlockSize = 19;
  args.PreprocessThreshweight = 7;
  set_xy(&args.PreprocessMorphKernel, "(3,3)");
  set_xy(&args.PreprocessMedianBlurKernel, "(13,13)");
  set_xy(&args.PreprocessCannyThr, "(80,80)");
  args.imgEnhancementEn = false;
  args.MinPixelWidth = 7;
  args.MaxPixelWidth = 30;
  args.MinPixelHeight = 7;
  args.MaxPixelHeight = 30;
  args.MinAspectRatio = 0.6;
  args.MaxAspectRatio = 2.5;
  args.MinPixelArea = 150;
  args.MaxPixelArea = 600;
  args.MinExtent = 0.4;
  args.MaxExtent = 0.9;
  args.MinTexture = 0;
  args.MaxTexture = 255;
  args.MaxDrift = 2.5;
  args.MarksRows = 3;
  args.MarksCols = 10;
  set_x4(&args.ROI, "(0,0)"); // if set_x4 is not recognized, simply replace with args.ROI.x1=0 args.ROI.x2=0;
  args.FindContoursMode = "Legacy";
  set_x6(&args.HoughParams, "(-1,-1,-1,-1,-1,-1)");
  args.PerspectiveMode = 0;
  args.debugMode = false;

  return args;
}

// ------------------------------------------------------------------------------------------------------------------------------
void print_args(args_t args) {

  printf("args.ImageFile = %s\n", args.ImageFile.c_str());
  printf("args.PreprocessCvcSel = %s\n", args.PreprocessCvcSel.c_str());
  printf("args.PreprocessMode = %s\n", args.PreprocessMode.c_str());
  printf("args.PreprocessGaussKernel = (%d,%d)\n", args.PreprocessGaussKernel.x, args.PreprocessGaussKernel.y);
  printf("args.PreprocessThreshBlockSize = %d\n", args.PreprocessThreshBlockSize);
  printf("args.PreprocessThreshweight = %d\n", args.PreprocessThreshweight);
  printf("args.PreprocessMorphKernel = (%d,%d)\n", args.PreprocessMorphKernel.x, args.PreprocessMorphKernel.y);
  printf("args.PreprocessMedianBlurKernel = (%d,%d)\n", args.PreprocessMedianBlurKernel.x, args.PreprocessMedianBlurKernel.y);
  printf("args.PreprocessCannyThr = (%d,%d)\n", args.PreprocessCannyThr.x, args.PreprocessCannyThr.y);
  printf("args.imgEnhancementEn = %d\n", args.imgEnhancementEn);
  printf("args.MinPixelWidth = %d\n", args.MinPixelWidth);
  printf("args.MaxPixelWidth = %d\n", args.MaxPixelWidth);
  printf("args.MinPixelHeight = %d\n", args.MinPixelHeight);
  printf("args.MaxPixelHeight = %d\n", args.MaxPixelHeight);
  printf("args.MinAspectRatio = %.1f\n", args.MinAspectRatio);
  printf("args.MaxAspectRatio = %.1f\n", args.MaxAspectRatio);
  printf("args.MinPixelArea = %d\n", args.MinPixelArea);
  printf("args.MaxPixelArea = %d\n", args.MaxPixelArea);
  printf("args.MinExtent = %.1f\n", args.MinExtent);
  printf("args.MaxExtent = %.1f\n", args.MaxExtent);
  printf("args.MinTexture = %.1f\n", args.MinTexture);
  printf("args.MaxTexture = %.1f\n", args.MaxTexture);
  printf("args.MaxDrift = %.1f\n", args.MaxDrift);
  printf("args.MarksRows = %d\n", args.MarksRows);
  printf("args.MarksCols = %d\n", args.MarksCols);
  printf("args.ROI = (%d,%d,%d,%d,%d)\n", args.ROI.x1, args.ROI.x2, args.ROI.x3, args.ROI.x4, args.ROI.len);
  printf("args.FindContoursMode = %s\n", args.FindContoursMode.c_str());
  printf("args.HoughParams = (%d,%d,%d,%d,%d,%d)\n", args.HoughParams.x1, args.HoughParams.x2, args.HoughParams.x3, args.HoughParams.x4, args.HoughParams.x5, args.HoughParams.x6 );
  printf("args.PerspectiveMode = %d\n", args.PerspectiveMode);
  printf("args.debugMode = %d\n", args.debugMode);
}

