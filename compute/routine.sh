#!/bin/bash
if docker ps --format "{{.Image}}" | grep -q run_analysis;  then
  docker stop run_analysis
  docker rm run_analysis
fi
if ! docker image ls --format "{{.Repository}}" | grep -q twstock_analysis; then
  sudo docker build . -t twstock_analysis
fi
sudo docker run -d --rm \
                    --name run_analysis \
                    -v "$PWD":/usr/src/twstock_analysis \
                    -w /usr/src/twstock_analysis \
                    twstock_analysis /bin/bash -c \
                    " python -um data.crawler.run > output.txt 2>&1 &&
                     python -um strategies.run >> output.txt 2>&1";
##                    python -um data.crawler.brokers >> output.txt 2>&1
sudo docker wait run_analysis
mkdir -p ../backend_api/public/pictures
mv "$PWD"/strategies/info.json "$PWD"/../backend_api/public
mv "$PWD"/strategies/*.png "$PWD"/../backend_api/public/pictures
# pg_dump --no-owner financial_data > financial_data.dump
