#!/bin/bash

{
  printenv
  echo "$CRON__SCRAPER root /usr/local/bin/python3 /app/main.py >> /var/log/scraper.log 2>&1"
  echo "$CRON__PG_DUMP root /app/scripts/dump.sh >> /var/log/pg_dump.log 2>&1"
} >> /etc/crontab

sh -c cron && tail -f /var/log/scraper.log /var/log/pg_dump.log
