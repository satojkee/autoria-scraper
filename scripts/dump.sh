#!/bin/bash

export PGPASSWORD=$PG_PASSWORD

pg_dump -U "$PG_USER" -h "$PG_HOST" -p 5432 -d "$PG_DB" -f /app/dumps/autoria_"$(date +%F_%H-%M-%S)".sql
