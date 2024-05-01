from sqlalchemy import select
from settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.model import *

engine = create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def save_user_values(telegram_id, values):
    async with async_session() as session:  
        async with session.begin():
            user_values = UserValues(telegram_id=telegram_id, values=values)
            session.add(user_values)
            await session.commit()

async def check_user_values(telegram_id):
    async with async_session() as session:
        async with session.begin():
            user_values = await session.execute(
                select(UserValues).where(UserValues.telegram_id == telegram_id)
            )
            user_values_obj = user_values.scalars().first()
            if user_values_obj:
                return user_values_obj.values
            else:
                return False