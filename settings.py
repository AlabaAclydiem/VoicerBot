from pydantic_settings import BaseSettings
from pydantic import Field
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from concurrent.futures import ThreadPoolExecutor


class Settings(BaseSettings):
    API_KEY: str = Field(env='API_KEY')
    BOT_TOKEN: str = Field(env='BOT_TOKEN')
    DATABASE_URL: str = Field(env='DATABASE_URL')
    AMPLITUDE_API: str = Field(env='AMPLITUDE_API')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()

voicer_bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()

executor = ThreadPoolExecutor(max_workers=10)