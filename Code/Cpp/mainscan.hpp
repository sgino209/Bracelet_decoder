// Bracelet-Decoder algo app
// (c) Shahar Gino, September-2017, sgino209@gmail.com

#ifndef MAINSCAN_HPP
#define MAINSCAN_HPP

#include <iostream>
#include <iomanip>
#include <getopt.h>
#include <dirent.h>
#include <unistd.h>
#include "auxiliary.hpp"

#define no_argument 0
#define required_argument 1
#define optional_argument 2

void set_xy(uint_xy_t *d, std::string str) {
  std::size_t found1 = str.find("(");
  std::size_t found2 = str.find(",");
  std::size_t found3 = str.find(")");
  if ((found1 != std::string::npos) && (found2 != std::string::npos)) {
    std::string x_str = str.substr(found1+1, found2-found1-1);
    d->x = atoi(x_str.c_str());
  }
  if ((found2 != std::string::npos) && (found3 != std::string::npos)) {
    std::string y_str = str.substr(found2+1, found3-found2-1);
    d->y = atoi(y_str.c_str());
  }
}

void set_x4(uint_x4_t *d, std::string str) {
  std::size_t found1 = str.find("(");
  std::size_t found2 = str.find(",");
  std::size_t found3 = 0;
  std::size_t found4 = 0;
  std::size_t found5 = str.find(")");
  std::string x_str;
  
  d->len = 2;

  if (found2 != std::string::npos) {
    found3 = str.find(",", found2 + 1);
  }
  if (found3 != std::string::npos) {
    found4 = str.find(",", found3 + 1);
  }
 
  if ((found1 != std::string::npos) && (found2 != std::string::npos)) {
    std::string x_str = str.substr(found1+1, found2-found1-1);
    d->x1 = atoi(x_str.c_str());
  }
  if ((found2 != std::string::npos) && (found3 != std::string::npos)) {
    std::string x_str = str.substr(found2+1, found3-found2-1);
    d->x2 = atoi(x_str.c_str());
  }
  if (found3 != std::string::npos) {
    std::string x_str = str.substr(found3+1, found4-found3-1);
    d->x3 = atoi(x_str.c_str());
    d->len = 3;
  }
  if ((found3 != std::string::npos) && (found4 != std::string::npos)) {
    std::string x_str = str.substr(found4+1, found5-found4-1);
    d->x4 = atoi(x_str.c_str());
    d->len = 4;
  }
}

typedef enum {
  ARG_PREPROCESSGAUSSKERNEL = 0,
  ARG_PREPROCESSTHRESHBLOCKSIZE,
  ARG_PREPROCESSTHRESHWEIGHT,
  ARG_PREPROCESSMORPHKERNEL,
  ARG_ROI,
  ARG_MINPIXELWIDTH,
  ARG_MAXPIXELWIDTH,
  ARG_MINPIXELHEIGHT,
  ARG_MAXPIXELHEIGHT,
  ARG_MINASPECTRATIO,
  ARG_MAXASPECTRATIO,
  ARG_MINPIXELAREA,
  ARG_MAXPIXELAREA,
  ARG_MINEXTENT,
  ARG_MAXEXTENT,
  ARG_MAXDRIFT,
  ARG_MARKROWS,
  ARG_MARKCOLS,
  ARG_IMGENHANCEMENTEN,
  ARG_DEBUG,
  ARGS_NUM
} bracelet_decoder_arg_t;

const struct option longopts[] =
{
  {"version",                    no_argument,       0, 'v' },
  {"help",                       no_argument,       0, 'h' },
  {"image",                      required_argument, 0, 'i' },
  {"PreprocessGaussKernel",      required_argument, 0, ARG_PREPROCESSGAUSSKERNEL },
  {"PreprocessThreshBlockSize",  required_argument, 0, ARG_PREPROCESSTHRESHBLOCKSIZE },
  {"PreprocessThreshweight",     required_argument, 0, ARG_PREPROCESSTHRESHWEIGHT },
  {"PreprocessMorphKernel",      required_argument, 0, ARG_PREPROCESSMORPHKERNEL },
  {"ROI",                        required_argument, 0, ARG_ROI },
  {"MinPixelWidth",              required_argument, 0, ARG_MINPIXELWIDTH },
  {"MaxPixelWidth",              required_argument, 0, ARG_MAXPIXELWIDTH },
  {"MinPixelHeight",             required_argument, 0, ARG_MINPIXELHEIGHT },
  {"MaxPixelHeight",             required_argument, 0, ARG_MAXPIXELHEIGHT },
  {"MinAspectRatio",             required_argument, 0, ARG_MINASPECTRATIO },
  {"MaxAspectRatio",             required_argument, 0, ARG_MAXASPECTRATIO },
  {"MinPixelArea",               required_argument, 0, ARG_MINPIXELAREA },
  {"MaxPixelArea",               required_argument, 0, ARG_MAXPIXELAREA },
  {"MinExtent",                  required_argument, 0, ARG_MINEXTENT },
  {"MaxExtent",                  required_argument, 0, ARG_MAXEXTENT },
  {"MaxDrift",                   required_argument, 0, ARG_MAXDRIFT },
  {"MarksRows",                  required_argument, 0, ARG_MARKROWS },
  {"MarksCols",                  required_argument, 0, ARG_MARKCOLS },
  {"imgEnhancementEn",           no_argument,       0, ARG_IMGENHANCEMENTEN },
  {"debug",                      no_argument,       0, ARG_DEBUG }
};

// Main function:
int main(int argc, char** argv);

// Auxiliary function - returns folder name for results to be stored at results_%d%m%y_%H%M%S_imgFile:
std::string get_envpath(std::string ImageFile);

// Auxiliary function - prints usage information:
void usage(char *script_name);

#endif	// MAINSCAN_HPP

