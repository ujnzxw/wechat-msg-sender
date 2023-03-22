#! /usr/bin/env bash

# start to run schedule spider
set -ex
ROOT=/root/bihu24h

cd ${ROOT}/bihu/
/usr/bin/scrapy crawl article-week-loop | tee -a ${ROOT}/logs/spider.log
cd ${ROOT}
