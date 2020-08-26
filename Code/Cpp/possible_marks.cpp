// Bracelet-Decoder algo app
// (c) Shahar Gino, September-2017, sgino209@gmail.com

#include "possible_marks.hpp"

PossibleMark :: PossibleMark(std::vector<cv::Point> _contour, cv::Mat &frame_gray, unsigned int _MinPixelWidth, unsigned int _MaxPixelWidth,
                             unsigned int _MinPixelHeight, unsigned int _MaxPixelHeight, double _MinAspectRatio, double _MaxAspectRatio,
                             unsigned int _MinPixelArea, unsigned int _MaxPixelArea, double _MinExtent, double _MaxExtent, double _MinTexture, 
                             double _MaxTexture, bool debugMode) {
  
  contour = _contour;

  boundingRect = cv::boundingRect(contour);

  intBoundingRectArea = boundingRect.width * boundingRect.height;
  dblExtent = (double)(cv::contourArea(contour)) / intBoundingRectArea;

  intCenterX = (boundingRect.x + boundingRect.x + boundingRect.width) / 2;
  intCenterY = (boundingRect.y + boundingRect.y + boundingRect.height) / 2;
        
  intCenterX_r = 0;
  intCenterY_r = 0;

  dblDiagonalSize = sqrt(pow(boundingRect.width, 2) + pow(boundingRect.height, 2));

  dblAspectRatio = (double)boundingRect.width / (double)boundingRect.height;

  dblTexture = 0.0;
  int kx, ky, kn=0;
  for (ky=-5; ky<=5; ky++) {
    for (kx=-5; kx<=5; kx++) {
      dblTexture += frame_gray.at<uchar>(intCenterY+ky, intCenterX+kx);
      kn++;
      if (debugMode) {
        frame_gray.at<uchar>(intCenterY+ky,intCenterX+kx) = 255;
      }
    }
  }
  dblTexture /= kn;
  if (debugMode) {
    cv::putText(frame_gray, std::to_string(int(dblTexture)), cv::Point(intCenterX-10, intCenterY+20) , cv::FONT_HERSHEY_SIMPLEX, 0.5, SCALAR_RED, 1);
    for (auto it=contour.begin(); it<contour.end(); it++) {
      frame_gray.at<uchar>(it->y,it->x) = 255;
    }
  }

  MinPixelWidth = _MinPixelWidth;
  MaxPixelWidth = _MaxPixelWidth;
  MinPixelHeight = _MinPixelHeight;
  MaxPixelHeight = _MaxPixelHeight;
  MinAspectRatio = _MinAspectRatio;
  MaxAspectRatio = _MaxAspectRatio;
  MinPixelArea = _MinPixelArea;
  MaxPixelArea = _MaxPixelArea;
  MinExtent = _MinExtent;
  MaxExtent = _MaxExtent;
  MinTexture = _MinTexture;
  MaxTexture = _MaxTexture;
}

// ------------------------------------------------------------------------------------------------------------------------------
bool PossibleMark :: checkIfPossibleMark() {
    
  bool res = (boundingRect.area() > MinPixelArea &&
              boundingRect.area() < MaxPixelArea &&
              boundingRect.width > MinPixelWidth &&
              boundingRect.width < MaxPixelWidth &&
              boundingRect.height > MinPixelHeight &&
              boundingRect.height < MaxPixelHeight &&
              dblAspectRatio > MinAspectRatio &&
              dblAspectRatio < MaxAspectRatio &&
              dblExtent > MinExtent &&
              dblExtent < MaxExtent &&
              dblTexture > MinTexture &&
              dblTexture < MaxTexture);
  
  //std::cout << this->to_string() << " + " << res << std::endl;

  return res;
}

// ------------------------------------------------------------------------------------------------------------------------------
double PossibleMark :: operator-(const PossibleMark& other) {
  
  cv::Point2f p1 = cv::Point2f(intCenterX, other.intCenterX);
  cv::Point2f p2 = cv::Point2f(intCenterY, other.intCenterY);

  return distance_mse(p1,p2);
}

// ------------------------------------------------------------------------------------------------------------------------------
std::string PossibleMark::to_string() {
        
  char buffer[1000];

  sprintf(buffer, "(x,y, xR,yR, w,h, BndArea,AspRatio,extent,texture)=(%d,%d, %d,%d, %d,%d, %d,%.2f.%.2f,%.2f)",
                  intCenterX, intCenterY, intCenterX_r, intCenterY_r, boundingRect.width,
                  boundingRect.height, intBoundingRectArea, dblAspectRatio, dblExtent, dblTexture);

  std::string str(buffer);

  return str;
}

