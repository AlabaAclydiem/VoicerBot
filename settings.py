from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    API_KEY: str = Field(env='API_KEY')
    BOT_TOKEN: str = Field(env='BOT_TOKEN')

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
