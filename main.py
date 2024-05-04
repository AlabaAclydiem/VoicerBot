from settings import voicer_bot, dispatcher
from service.open_ai import init_openai
from utils.thread_pool_executor import process_event
from utils.run_openai import run_photo, run_text, run_voice
import asyncio
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message) :
    await message.answer("Привет! Я активирован")
    process_event("UserStartedBot", str(message.from_user.id), "Пользователь выполнил команду /start")


@dispatcher.message(F.text)
async def handle_text_message(message: Message):
    await run_text(message)
    process_event("UserSendText", str(message.from_user.id), "Пользователь предполёл общаться с ботом посредством текста")


@dispatcher.message(F.photo)
async def handle_photo_message(message: Message):
    await run_photo(message)
    process_event("UserSendPhoto", str(message.from_user.id), "Пользователь сбросил боту фотографию для распознавания эмоции на нём")


@dispatcher.message(F.voice)
async def handle_voice_message(message: Message):
    await run_voice(message)   
    process_event("UserSendVoice", str(message.from_user.id), "Пользователь предполёл общаться с ботом посредством голоса")


async def main():
    await init_openai()
    await dispatcher.start_polling(voicer_bot)


if __name__ == "__main__":
    asyncio.run(main()) 