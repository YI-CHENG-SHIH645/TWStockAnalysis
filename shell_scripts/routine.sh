#!/bin/bash
sudo docker run -d --rm \
                    --name run_analysis \
                    -v "$PWD":/usr/src/FinTech_2020 \
                    -w /usr/src/FinTech_2020 \
                    fintech_2020 /bin/bash -c \
                    " python -um data.crawler.run > output.txt 2>&1 &&
                     python -um strategies.run >> output.txt 2>&1"
##                    python -um data.crawler.brokers >> output.txt 2>&1

cp -r "$PWD/strategies/static/." "$HOME/twstock_investment_lb4/public/"
# pg_dump --no-owner financial_data > financial_data.dump
