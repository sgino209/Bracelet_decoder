#!/bin/sh

base='/Users/shahargino/MEGA/ImageProcessing'

bracelet_test() {
  res=`python3 main.py -i $1 $2 | grep -w $3`
  if [ "$res" ]; then
    echo "$1\t PASSED!"
  else
    printf "$1\t \033[1;31mFAILED\033[0m! $4\n"
  fi
} 

#---------------------------------- I M A G E ----------------------------|-- Arguments --|-- Expected --|---- Waivers ----
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/1.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/2.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/3.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/4.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/5.jpg"   "--ROI=(0,0)"  "0x1010f503"  "place_holder"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/6.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/7.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/8.jpg"   "--ROI=(0,0)"  "0x1010f503"  "place_holder"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/9.jpg"   "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/10.jpg"  "--ROI=(0,0)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220_high/type1/11.jpg"  "--ROI=(0,0)"  "0x1010f503"

