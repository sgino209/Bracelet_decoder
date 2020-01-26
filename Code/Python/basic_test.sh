#!/bin/sh

base='/Users/shahargino/Documents/ImageProcessing'

bracelet_test() {
  res=`python main.py -i $1 $2 | grep -w $3`
  if [ "$res" ]; then
    echo "$1\t PASSED!"
  else
    printf "$1\t \033[1;31mFAILED\033[0m! $4\n"
  fi
} 

#---------------------------------------- I M A G E ---------------------------------------|------- Arguments ------|-- Expected --|---- Waivers ----
bracelet_test "$base/Bracelet_decoder/Database/1.jpg"   "--ROI=(650,400,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/2.jpg"   "--ROI=(500,450,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/3.jpg"   "--ROI=(550,300,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/4.jpg"   "--ROI=(400,400,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/5.jpg"   "--ROI=(575,350,650)"  "0x27166f5e"  "(hard lightening)"
bracelet_test "$base/Bracelet_decoder/Database/6.jpg"   "--ROI=(575,350,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/7.jpg"   "--ROI=(650,300,650)"  "0x27166f5e"
bracelet_test "$base/Bracelet_decoder/Database/8.jpg"   "--ROI=(100,800,650)"  "0x27166f5e"  "(hard lightening)"
                                                                                    
bracelet_test "$base/Bracelet_decoder/Database/9.jpg"   "--ROI=(450,550,650)"  "0x3cfad75a"  "(Hard shooting angle)"
bracelet_test "$base/Bracelet_decoder/Database/10.jpg"  "--ROI=(400,300,650) --PreprocessThreshBlockSize=21"  "0x3cfad75a"
bracelet_test "$base/Bracelet_decoder/Database/11.jpg"  "--ROI=(200,300,650)"  "0x3cfad75a"
bracelet_test "$base/Bracelet_decoder/Database/12.jpg"  "--ROI=(450,450,650)"  "0x3cfad75a"

bracelet_test "$base/Bracelet_decoder/Database/13.jpg"  "--ROI=(10,450,650)"   "0x2a3c464c"  "(hard lightening)"
bracelet_test "$base/Bracelet_decoder/Database/15.jpg"  "--ROI=(400,450,650)"  "0x2a3c464c"

# Special cases (poor quality images):
bracelet_test "$base/Bracelet_decoder/Database/14.jpg"  "--ROI=(450,450,650) --MinPixelArea=100"  "0x2a3c464c"
bracelet_test "$base/Bracelet_decoder/Database/16.jpg"  "--ROI=(400,350,650) --MinPixelArea=120"  "0x3cfad75a"
bracelet_test "$base/Bracelet_decoder/Database/17.jpg"  "--ROI=(450,300,650) --MinExtent=0.3"     "0x2a3c464c"

# Authentic Images (RedID):
bracelet_test "$base/Bracelet_decoder/Database/24.png"  "--ROI=(200,500,650)"  "0x3cfad75a"
bracelet_test "$base/Bracelet_decoder/Database/25.jpg"  "--ROI=(200,300,650)"  "0x3cfad75a"

