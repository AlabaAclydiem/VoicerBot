from pydantic_settings import BaseSettings
from pydantic import Field
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from concurrent.futures import ThreadPoolExecutor
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

class Settings(BaseSettings):
    API_KEY: str = Field(env='API_KEY')
    BOT_TOKEN: str = Field(env='BOT_TOKEN')
    DATABASE_URL: str = Field(env='DATABASE_URL')
    AMPLITUDE_API: str = Field(env='AMPLITUDE_API')
    REDISHOST: str = Field(env='REDISHOST')
    REDISPASSWORD: str = Field(env='REDISPASSWORD')
    REDISUSER: str = Field(env='REDISUSER')
    REDISPORT: str = Field(env='REDISPORT')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
if settings.REDISPASSWORD == 'None':
    settings.REDISPASSWORD = None
if settings.REDISUSER == 'None':
    settings.REDISUSER = None
if settings.REDISPORT == 'None':
    settings.REDISPORT = None

voicer_bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
redis_client = Redis(
    host=settings.REDISHOST, 
    username=settings.REDISUSER, 
    password=settings.REDISPASSWORD,
    port=settings.REDISPORT)
dispatcher = Dispatcher(storage=RedisStorage(redis=redis_client))

executor = ThreadPoolExecutor(max_workers=10)