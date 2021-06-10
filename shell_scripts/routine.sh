#!/bin/bash
sudo docker run -d --rm \
                    --name run_analysis \
                    -v "$PWD":/usr/src/twstock_analysis \
                    -w /usr/src/twstock_analysis \
                    twstock_analysis /bin/bash -c \
                    " python -um data.crawler.run > output.txt 2>&1 &&
                     python -um strategies.run >> output.txt 2>&1"
##                    python -um data.crawler.brokers >> output.txt 2>&1

cp -r "$PWD/strategies/static/." "$HOME/twstock_investment_lb4/public/"
# pg_dump --no-owner financial_data > financial_data.dump
