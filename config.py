import os

from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.DEBUG)

aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

OPEN_WEATHER_BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?units=metric'
OPEN_WEATHER_API_KEY_START = '&appid='
API_OPEN_WEATHER_KEY = os.getenv("API_OPEN_WEATHER_KEY")
