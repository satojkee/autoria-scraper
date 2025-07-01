# [AutoRia.com](https://auto.ria.com) web-scraper
* Author: [satojkee](https://github.com/satojkee)


## Short structure description
There are 2 main scrapers:
- `autoria_scraper.core.scrapers.listing.ListingScraper` - this one is executed first and its goal is: **obtaining direct links to the listed cars**
  - Returns a collection of links (approx. 350k);
  - Total execution time ~ 1-2 hours (based on hardware and settings).

- `autoria_scraper.core.scrapers.direct.DirectScraper` - this one waits for the `ListingScraper` to complete and then **obtains data from the direct links**
  - Processes each link (approx. 350k links) obtained from the previous scraper;
  - Total execution time ~ 10+ hours (based on hardware and settings).


## Cron jobs
Cron jobs are managed by the `cron` - linux package. Define cron jobs in `/scripts/start.sh` script-file.
- `printenv` is used to apply project environment variables for cron jobs, otherwise those variables won't be accessible by cron. 
- Define `CRON__SCRAPER` and `CRON__PG_DUMP` in the same `.env` file used by **docker-compose**.

```shell
#!/bin/bash

{
  printenv
  echo "$CRON__SCRAPER root /usr/local/bin/python3 /app/main.py >> /var/log/scraper.log 2>&1"
  echo "$CRON__PG_DUMP root /app/scripts/dump.sh >> /var/log/pg_dump.log 2>&1"
} >> /etc/crontab

```


## Project requirements
- Python 3.11
- Packages: 
    - SQLAlchemy[async]==2.0.41
    - pydantic==2.11.7
    - pydantic-settings==2.10.1
    - asyncpg==0.30.0
    - aiohttp==3.12.13
    - beautifulsoup4==4.13.4
    - fake-useragent==2.2.0
    - lxml==5.4.0

  
## Settings
> Configuration is loaded from `.env` file.

### Default settings
```dotenv
# PostgresDsn = "dialect+driver://user:password@host:port/dbname"
DATABASE__URL="postgresql+asyncpg://postgres:postgres@localhost:5432/autoria"
# Use this one for testing purposes, ! remove in production !
SCRAPER__PAGES_LIMIT="100"
# Required for `autoria_scraper.core.scrapers.listing.ListingScraper` as root url to obtain listings
SCRAPER__ROOT_URL="https://auto.ria.com/uk/car/used/"
# Required for `autoria_scraper.core.scrapers.direct.DirectScraper` as root url to collect sellers' phone numbers
SCRAPER__PHONE_URL="https://auto.ria.com/bff/final-page/public/auto/popUp/"
# Required for both scrapers, defines an amount of concurrent tasks (the higher this values is, the more network/RAM application consumes)
SCRAPER__BATCH_SIZE="200"
# Replaces `aiohttp` default request timeout value (300 -> 60), throws `TimeoutError` if exceeded
SCRAPER__AIOHTTP__TIMEOUT="60"
# Retries amount for each `aiohttp` request (om failure)
SCRAPER__AIOHTTP__ATTEMPTS_LIMIT="3"
# Delay between each `aiohttp` request reattempt (on failure, in seconds)
SCRAPER__AIOHTTP__ATTEMPT_DELAY="2"

# Required for `autoria-postgres` and `pg_dump` cron task
PG_USER="postgres"
PG_PASSWORD="postgres"
PG_DB="autoria"
PG_HOST="autoria-postgres"  # postgres container name or remote host

# Cron schedule settings
# https://crontab.guru/
CRON__PG_DUMP="0 12 * * *"
CRON__SCRAPER="0 12 * * *"
```

### Description
> Project uses `pydantic_settings` package to manage configuration. \
> `__` is used as nesting delimiter.

| Variable                           | Recommended value                                                    | Description                                                                                                                                                                   |
|------------------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `SCRAPER__PAGES_LIMIT`             | 100 - 500                                                            | **Use this option to test web-scraper.** Limits total amount of pages with a specified value for `ListingScraper` (approx. 18k+ pages for unlimited). `remove for production` |       
| `SCRAPER__ROOT_URL`                | https://auto.ria.com/uk/car/used/                                    | `Constant!` Base url (crucial to obtain direct links to the listed cars)                                                                                                      |
| `SCRAPER__PHONE_URL`               | https://auto.ria.com/bff/final-page/public/auto/popUp/               | `Constant!` This one is used to dynamically obtain phone numbers                                                                                                              |
| `SCRAPER__BATCH_SIZE`              | 200                                                                  | Amount of concurrent tasks (the higher this value is, the more network/RAM is consumed).                                                                                      |
| `SCRAPER__AIOHTTP__ATTEMPTS_LIMIT` | 3                                                                    | Number of reattempts for `aiohttp` requests                                                                                                                                   |
| `SCRAPER__AIOHTTP__TIMEOUT`        | 60                                                                   | Timeout for `aiohttp` requests (in seconds), default value provided by `aiohttp` = 60 * 5 = 300                                                                               |
| `SCRAPER__AIOHTTP__ATTEMPT_DELAY`  | 2                                                                    | Delay between each reattempt (in seconds)                                                                                                                                     |
| `DATABASE__URL`                    | postgresql+asyncpg://postgres:postgres@autoria-postgres:5432/autoria | Database url, `postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{host/container_name)}:5432/{PG_DB}`                                                                              |
| `PG_USER`                          | postgres                                                             | Database username (used by `autoria-postgres` and `pg_dump` util)                                                                                                             |
| `PG_PASSWORD`                      | postgres                                                             | Database password (used by `autoria-postgres` and `pg_dump` util)                                                                                                             |
| `PG_DB`                            | autoria                                                              | Database name (used by `autoria-postgres` and `pg_dump` util)                                                                                                                 |
| `PG_HOST`                          | autoria-postgres                                                     | Database host (used by `autoria-postgres` and `pg_dump` util, use db container name: `autoria-postgres`)                                                                      |


## Output data example (10 rows)
> Go to: `/examples/output_data_example.csv` for 100-row example

| id | url                                                                   | title                          | price_usd  | odometer | username          | phone_number | image_url                                                                              | images_count   | car_number   | car_vin               | datetime_found               |
|----|-----------------------------------------------------------------------|--------------------------------|------------|----------|-------------------|--------------|----------------------------------------------------------------------------------------|----------------|--------------|-----------------------|------------------------------|
| 1  | https://auto.ria.com/uk/auto_infiniti_qx80_38398716.html              | Infiniti QX80 2019             | 42999      | 110000   | Антон             | 380751132773 | https://cdn4.riastatic.com/photosnew/auto/photo/infiniti_qx80__601801019f.webp         | 19             | KA 6330 MO   | JN1JANZ62U0101530     | 2025-06-27 14:22:01.84235    |
| 2  | https://auto.ria.com/uk/auto_bmw_5_series_38397166.html               | BMW 5 Series 2006              | 9000       | 220000   | Ігор              | 380974974041 | https://cdn4.riastatic.com/photosnew/auto/photo/bmw_5-series__601603434f.webp          | 18             | KE 9677 AK   | WBANL51040CN08802     | 2025-06-27 14:22:01.842354   |
| 3  | https://auto.ria.com/uk/auto_fiat_freemont_38504589.html              | Fiat Freemont 2016             | 15990      | 201000   | Роман             | 380505202504 | https://cdn2.riastatic.com/photosnew/auto/photo/fiat_freemont__604717302f.webp         | 180            | NULL         | 3C4PFBCY5FT656460     | 2025-06-27 14:22:01.842354   |
| 4  | https://auto.ria.com/uk/auto_audi_a6_38145898.html                    | Audi A6 2019                   | 39400      | 184000   | Віталій           | 380967062649 | https://cdn4.riastatic.com/photosnew/auto/photo/audi_a6__594640804f.webp               | 74             | BO 0504 EP   | WAUZZZF26LN009042     | 2025-06-27 14:22:01.842355   |
| 5  | https://auto.ria.com/uk/auto_lexus_lx_38432047.html                   | Lexus LX 2022                  | 122900     | 25000    | Роман             | 380981524869 | https://cdn2.riastatic.com/photosnew/auto/photo/lexus_lx__602956452f.webp              | 77             | NULL         | JTJPABCXx04xxxx81     | 2025-06-27 14:22:01.842357   |
| 6  | https://auto.ria.com/uk/auto_volkswagen_passat_38490280.html          | Volkswagen Passat 2021         | 18900      | 195000   | IZI AUTO LUTSK    | 380970102233 | https://cdn2.riastatic.com/photosnew/auto/photo/volkswagen_passat__604316732f.webp     | 91             | NULL         | WVWZZZ3CZME011380     | 2025-06-27 14:22:01.842358   |
| 7  | https://auto.ria.com/uk/auto_peugeot_3008_38475871.html               | Peugeot 3008 2009              | 7499       | 189000   | Олег              | 380687327801 | https://cdn0.riastatic.com/photosnew/auto/photo/peugeot_3008__603907420f.webp          | 51             | NULL         | VF30U9HZH9S052141     | 2025-06-27 14:22:01.842358   |
| 8  | https://auto.ria.com/uk/auto_renault_grand_scenic_38486303.html       | Renault Grand Scenic 2015      | 10499      | 237000   | Сергій            | 380964133388 | https://cdn0.riastatic.com/photosnew/auto/photo/renault_grand-scenic__604203510f.webp  | 199            | NULL         | VF1JZ03Bx53xxxx44     | 2025-06-27 14:22:01.842359   |
| 9  | https://auto.ria.com/uk/auto_nissan_leaf_38487156.html                | Nissan Leaf 2019               | 13200      | 120000   | Ім’я не вказане   | 380976708990 | https://cdn1.riastatic.com/photosnew/auto/photo/nissan_leaf__604227721f.webp           | 24             | NULL         | SJNFAAZE1U0050013     | 2025-06-27 14:22:01.842359   |
| 10 | https://auto.ria.com/uk/auto_mercedes_benz_s_class_36816934.html      | Mercedes-Benz S-Class 2013     | 25000      | 221000   | Андрей            | 380500554866 | https://cdn1.riastatic.com/photosnew/auto/photo/mercedes-benz_s-class__557748121f.webp | 32             | BC 1777 EP   | WDDNG9EB0DA533729     | 2025-06-27 14:22:01.84236    |


## How to build?
> **Don't forget** to configure necessary variables in [`.env`](#settings) file.

### Build and run using `docker-compose`
```shell
docker-compose up -d
```
