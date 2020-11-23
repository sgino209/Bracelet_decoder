#!/bin/bash

bracelet_test() {
  if   [[ "$1" == "py" ]];  then executable="python3 main.py"
  elif [[ "$1" == "cpp" ]]; then executable="build/bracelet_decoder"
  else
    printf "Unsupported mode: $1"
    exit 1
  fi
  res1=$($executable -i $2 $3 | grep "Code =" | cut -d' ' -f4)
  res2=$(echo $res1 | grep -w $4)
  if [ "$res2" ]; then
    printf "$2\t PASSED!\n"
  else
    printf "$2\t \033[1;31mFAILED\033[0m! ($res1) $5\n"
  fi
}

hr() {
  for i in $(seq 100); do printf "-"; done
  printf "\n"
}

