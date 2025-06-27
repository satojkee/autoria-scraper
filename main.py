"""Application `main.py` file.

How to start?
```shell
python main.py
```
"""


import asyncio

from autoria_scraper import start


if __name__ == '__main__':
    asyncio.run(start())
