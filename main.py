from settings import voicer_bot, dispatcher
from service.open_ai import init_openai, STT, assistant, TTS
from utils.run_openai import run_openai
import asyncio
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message) :
    await message.answer("Привет! Я активирован")


@dispatcher.message(F.text)
async def handle_text_message(message: Message):
    await run_openai(message, voice=False)


@dispatcher.message(F.voice)
async def handle_voice_message(message: Message):
    await run_openai(message, voice=True)


async def main():
    await init_openai()
    await dispatcher.start_polling(voicer_bot)


if __name__ == "__main__":
    asyncio.run(main()) 