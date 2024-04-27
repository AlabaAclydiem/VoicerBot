from pydantic_settings import BaseSettings
from pydantic import Field
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

class Settings(BaseSettings):
    API_KEY: str = Field(env='API_KEY')
    BOT_TOKEN: str = Field(env='BOT_TOKEN')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()

voicer_bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()
