#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "pass in the profiling name (a string)"
  exit 1
fi

if docker ps --format "{{.Image}}" | grep -q profiling;  then
  docker stop profiling
  docker rm profiling
fi
if ! docker image ls --format "{{.Repository}}" | grep -q twstock_analysis; then
  cd ..
  docker build -t twstock_analysis -f compute/Dockerfile .
  cd compute || exit
fi

docker run -d --rm \
              --name profiling \
              -v "$PWD":/usr/src/twstock_analysis/compute \
              -v "$PWD/../core":/usr/src/twstock_analysis/core \
              -w /usr/src/twstock_analysis/compute \
              twstock_analysis /bin/bash -c \
              " cd ../core &&
                mkdir -p build &&
                cd build &&
                rm CMakeCache.txt;
                cmake .. && make &&
                cd ../../compute &&
               python -um strategies.run --cpp --profiling_name=\"$1\" --new_start > output.txt 2>&1";
