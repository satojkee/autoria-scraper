FROM python:3.11-slim

# Install cron and postgresql-client (includes pg_dump)
RUN apt-get update && apt-get install -y cron postgresql-client && apt-get clean

WORKDIR /app

COPY . /app

# Create dumps directory in project root
RUN mkdir /app/dumps

# Set proper rights for start/dump scripts
RUN chmod +x /app/scripts/dump.sh
RUN chmod +x /app/scripts/start.sh

# Install python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Create log files for scraper and pg_dump
RUN touch /var/log/scraper.log /var/log/pg_dump.log

ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Kyiv

CMD ["/app/scripts/start.sh"]
