#!/bin/bash

images_num=${1:-0}
exec_mode=${2:-"cpp"}
  
base_path="/Users/$(whoami)/MEGA/ImageProcessing/Bracelet_decoder/Database/221120"

# -------------------------------------------------------------------------------------------

tic() {
  
  start_time=$(date +%s)
}

# -------------------------------------------------------------------------------------------

toc() {

  end_time=$(date +%s)
  runtime=$((end_time - start_time))
  hours=$((runtime / 3600));
  minutes=$(( (runtime % 3600) / 60 ));
  seconds=$(( (runtime % 3600) % 60 ));
  hours=$(printf "%02d" ${hours})
  minutes=$(printf "%02d" ${minutes})
  seconds=$(printf "%02d" ${seconds})
  echo "Runtime: ${hours}:${minutes}:${seconds} (hh:mm:ss)"
}

# -------------------------------------------------------------------------------------------

Initialize() {
  
  if   [[ "${1}" == "py" ]];  then executable="python3 main.py"
  elif [[ "${1}" == "cpp" ]]; then executable="build/bracelet_decoder"
  fi
}

# -------------------------------------------------------------------------------------------

RunTest() {
  
  local img=${1}
  local preprocess_medianblurkernel=${2}
  local preprocess_cannythr=${3}
  local preprocess_houghparams=${4}
  local expected_code=${5}

  ${executable} -i ${img} --PreprocessMode=BlurAndCanny \
                          --FindContoursMode=Hough \
                          --ROI="(0,0)" \
                          --MaxPixelWidth=${max_pixel_width} \
                          --MaxPixelHeight=${max_pixel_height} \
                          --MaxPixelArea=${max_pixel_area} \
                          --PreprocessCvcSel=${preprocess_cvc} \
                          --PreprocessMedianBlurKernel=${preprocess_medianblurkernel} \
                          --PreprocessCannyThr=${preprocess_cannythr} \
                          --HoughParams=${preprocess_houghparams}
}

# -------------------------------------------------------------------------------------------

RunTests() {

  local tests_suite=${1}
  local images_num=${2}
  local preprocess_cvc=${3}
  local preprocess_medianblurkernel=${4}
  local preprocess_cannythr=${5}
  local preprocess_houghparams_mindist=${6}
  local preprocess_houghparams_param2=${7}
  local preprocess_houghparams_minrad=${8}
  
  preprocess_medianblurkernel=(${preprocess_medianblurkernel//,/ })
  preprocess_cannythr=(${preprocess_cannythr//,/ })
  preprocess_houghparams_mindist=(${preprocess_houghparams_mindist//,/ })
  preprocess_houghparams_param2=(${preprocess_houghparams_param2//,/ })
  preprocess_houghparams_minrad=(${preprocess_houghparams_minrad//,/ })

  # Static:
  max_pixel_width=50
  max_pixel_height=50
  max_pixel_area=2500

  expected_code=$(echo ${tests_suite} | cut -d"_" -f2)

  csv="${tests_suite}.csv"
  
  echo "file, MedianBlurKernel, CannyThr, houghparams_mindist, houghparams_param2, houghparams_minrad" > ${csv}
  let imgs_num=0

  for img in $(find ${base_path}/${tests_suite} -name "IMG_*.JPG" | sort -t '\0' -n); do

    echo -n "Processing: ${img}"

    let iters=0
    for k1 in $(seq ${preprocess_medianblurkernel[0]} 2 ${preprocess_medianblurkernel[1]}); do 
    for k2 in $(seq ${preprocess_cannythr[0]} 10 ${preprocess_cannythr[1]}); do 
    for k3 in $(seq ${preprocess_houghparams_mindist[0]} 5 ${preprocess_houghparams_mindist[1]}); do 
    for k4 in $(seq ${preprocess_houghparams_param2[0]} 1 ${preprocess_houghparams_param2[1]}); do 
    for k5 in $(seq ${preprocess_houghparams_minrad[0]} 3 ${preprocess_houghparams_minrad[1]}); do 
        
      res=$(RunTest "${img}" \
                    "(${k1},${k1})" \
                    "(${k2},${k2})" \
                    "(0,${k3},0,${k4},${k5},30)" \
                    "${expected_code}" | grep "Code =" | grep ${expected_code})

      if [ -n "${res}" ]; then
          echo "$(basename ${img}), ${k1}, ${k2}, ${k3}, ${k4}, ${k5}" >> ${csv}
      fi
      
      ((iters++))
    done
    done
    done
    done
    done

    echo " (${iters} iterations)"

    ((imgs_num++))
    if [ "${images_num}" -gt 0 ] && [ "${imgs_num}" -eq "${images_num}" ]; then
      break;
    fi

  done

  echo "Processed Images: ${imgs_num}"
  echo "Pass Images: $(grep -v 'file,' ${csv} | cut -d',' -f1 | sort | uniq | wc -l | sed 's/ //g')"
}

# -------------------------------------------------------------------------------------------

tic

Initialize "${exec_mode}"
                                     
# RunTests <test_suite> <images_num> <preprocess_cvc> <preprocess_medianblurkernel> <preprocess_cannythr> <preprocess_houghparams_mindist> <preprocess_houghparams_param2> <preprocess_houghparams_minrad>
RunTests "bg_0x37d476da" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "bs_0x3b95ba4c" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "bg_0x37d476da" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "bs_0x3b95ba4c" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "db_0x3e72676c" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "dg_0x28395bda" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "dr_0x2ad4be54" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "ds_0x2612f31a" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "ds_0x275effa2" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"
RunTests "ds_0x33188fda" ${images_num} "V" "3,19" "80,130" "35,45" "11,13" "9,15"

echo "Completed Successfully"

toc

