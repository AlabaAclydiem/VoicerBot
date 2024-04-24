from settings import settings
from open_ai import STT, assistant, TTS
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile


voicer_bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dispatcher = Dispatcher()


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message) :
    await message.answer(f"Привет, {message.from_user.full_name}! Отправь голосовое или текстовое сообщение и посмотри, что я могу тебе рассказать!")


@dispatcher.message(F.text)
async def handle_text_message(message: Message):
    response = assistant(message.text)
    path = TTS(response)
    await message.answer_voice(FSInputFile(path))


@dispatcher.message(F.voice)
async def handle_voice_message(message: Message):
    dest = 'temp.ogg'
    file_info = await voicer_bot.get_file(message.voice.file_id)
    await voicer_bot.download_file(file_info.file_path, destination=dest)
    prompt = STT(dest)
    response = assistant(prompt)
    path = TTS(response)
    await message.answer_voice(FSInputFile(path))


async def main():
    await dispatcher.start_polling(voicer_bot)


if __name__ == "__main__":
    asyncio.run(main())