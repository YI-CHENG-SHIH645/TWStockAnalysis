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
  sudo docker build -t twstock_analysis -f compute/Dockerfile .
  cd compute || exit
fi

docker run -d --rm \
              --name profiling \
              -v "$PWD":/usr/src/twstock_analysis/compute \
              -w /usr/src/twstock_analysis/compute \
              twstock_analysis /bin/bash -c \
              " cd ../core/build &&
                cmake .. && make &&
                cd ../../compute &&
               python -um strategies.run --profiling_name=\"$1\" --new_start > output.txt 2>&1";
