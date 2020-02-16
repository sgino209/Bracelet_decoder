#!/bin/bash

base="/Users/shahargino/MEGA/ImageProcessing"
mode="$1"

common_args="--PreprocessMode=BlurAndCanny --FindContoursMode=Hough --MaxPixelWidth=50 --MaxPixelHeight=50 --MaxPixelArea=2500"

source $(dirname $0)/basic_test_common.sh

#---------------------------------- I M A G E ----------------------------|-- Arguments --|-- Expected --|---- Waivers ----
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/1.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(150,300,700)" "0x203bff22"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/2.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,50,0,13,20,30) --ROI=(550,400,700)" "0x203bff22"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/3.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,50,0,13,20,30) --ROI=(540,400,700)" "0x203bff22"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/4.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,50,0,13,20,30) --ROI=(550,500,700)" "0x203bff22"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/5.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(600,450,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/6.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(600,350,650)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/7.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(700,350,650)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/8.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=17 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(200,700,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/9.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=21 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(200,700,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/10.jpg" "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=60  --HoughParams=(0,50,0,10,20,30) --ROI=(220,550,400)" "0xdeadbeef" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type1/11.jpg" "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=17 --PreprocessCannyThr=140 --HoughParams=(0,50,0,10,20,30) --ROI=(200,600,750)" "0xdeadbeef" "Illegal Code!"
hr
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type2/1.jpg"  "$common_args --PreprocessCvcSel=H --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,40,0,10,20,30) --ROI=(400,400,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type2/2.jpg"  "$common_args --PreprocessCvcSel=H --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,40,0,8,20,30)  --ROI=(450,550,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type2/3.jpg"  "$common_args --PreprocessCvcSel=H --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,40,0,10,20,30) --ROI=(150,550,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type2/4.jpg"  "$common_args --PreprocessCvcSel=H --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=40  --HoughParams=(0,40,0,10,20,30) --ROI=(200,350,700)" "0xbadcoffe" "Illegal Code!"
hr
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type3/1.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=90  --HoughParams=(0,60,0,10,20,30) --ROI=(500,450,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type3/2.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=13 --PreprocessCannyThr=90  --HoughParams=(0,50,0,10,20,30) --ROI=(600,450,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type3/3.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=21 --PreprocessCannyThr=90  --HoughParams=(0,60,0,10,20,30) --ROI=(300,700,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type3/4.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=21 --PreprocessCannyThr=90  --HoughParams=(0,60,0,10,20,30) --ROI=(300,700,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type3/5.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=21 --PreprocessCannyThr=90  --HoughParams=(0,60,0,10,20,30) --ROI=(300,500,700)" "0x27166f5e"
hr
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type4/1.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=80  --HoughParams=(0,40,0,12,15,30) --ROI=(450,450,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type4/2.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=80  --HoughParams=(0,40,0,12,15,30) --ROI=(600,450,700)" "0x27166f5e"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type4/3.jpg"  "$common_args --PreprocessCvcSel=V --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=80  --HoughParams=(0,40,0,12,15,30) --ROI=(200,650,700)" "0x27166f5e"
hr
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type5/1.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=90  --HoughParams=(0,47,0,12,15,30) --ROI=(150,450,700)" "0xbadcoffe" "Illegal Code!"
bracelet_test "$mode" "$base/Bracelet_decoder/Database/260220_high/type5/2.jpg"  "$common_args --PreprocessCvcSel=S --PreprocessMedianBlurKernel=19 --PreprocessCannyThr=90  --HoughParams=(0,47,0,12,15,30) --ROI=(150,400,700)" "0xbadcoffe" "Illegal Code!"
