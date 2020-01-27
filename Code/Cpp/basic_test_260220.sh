#!/bin/sh

base='/Users/shahargino/MEGA/ImageProcessing'

bracelet_test() {
  res=`build/bracelet_decoder -i $1 $2 | grep -w $3`
  if [ "$res" ]; then
    echo "$1\t PASSED!"
  else
    printf "$1\t \033[1;31mFAILED\033[0m! $4\n"
  fi
} 

#---------------------------------------- I M A G E ---------------------------------------|------- Arguments ------|-- Expected --|---- Waivers ----
bracelet_test "$base/Bracelet_decoder/Database/260220/1.jpg"   "--ROI=(650,400,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/2.jpg"   "--ROI=(500,450,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/3.jpg"   "--ROI=(550,300,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/4.jpg"   "--ROI=(400,400,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/5.jpg"   "--ROI=(575,350,650)"  "0x1010f503"  "(hard lightening)"
bracelet_test "$base/Bracelet_decoder/Database/260220/6.jpg"   "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/7.jpg"   "--ROI=(650,300,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/8.jpg"   "--ROI=(100,800,650)"  "0x1010f503"  "(hard lightening)"
bracelet_test "$base/Bracelet_decoder/Database/260220/9.jpg"   "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/10.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/11.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/12.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/13.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/14.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/15.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
bracelet_test "$base/Bracelet_decoder/Database/260220/16.jpg"  "--ROI=(575,350,650)"  "0x1010f503"
