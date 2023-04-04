#!/bin/bash

if docker ps --format "{{.Image}}" | grep -q run_analysis;  then
  docker stop run_analysis
  docker rm run_analysis
fi
if ! docker image ls --format "{{.Repository}}" | grep -q twstock_analysis; then
  cd ..
  docker build -t twstock_analysis -f compute/Dockerfile .
  cd compute || exit
fi

docker run --rm \
              --name run_analysis \
              -v "$PWD":/usr/src/twstock_analysis/compute \
              -w /usr/src/twstock_analysis/compute \
              twstock_analysis /bin/bash -c \
              "python -um strategies.run --cpp --new_start > output.txt 2>&1";
#             " python -um data.crawler.run > output.txt 2>&1 &&

##              python -um data.crawler.brokers >> output.txt 2>&1

docker wait run_analysis
mkdir -p ../server/public/pictures
mv "$PWD"/strategies/info.json "$PWD"/../server/public
mv "$PWD"/strategies/*.png "$PWD"/../server/public/pictures
# pg_dump --no-owner financial_data > financial_data.dump
