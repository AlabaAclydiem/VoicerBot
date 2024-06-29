from settings import voicer_bot, dispatcher
from service.open_ai import get_thread, init_openai
from utils.thread_pool_executor import process_event
from utils.run_openai import run_photo, run_text, run_voice
from utils.state import ThreadState
import asyncio
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey


@dispatcher.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext):
    thread = await get_thread(message.from_user.id)
    await state.set_state(ThreadState.thread)
    await state.storage.set_data(key=StorageKey(bot_id=voicer_bot.id, user_id=message.from_user.id, chat_id=message.chat.id), data={'thread': thread.id})
    await message.answer("Привет! Я активирован")
    process_event("UserStartedBot", str(message.from_user.id), "Пользователь выполнил команду /start")


@dispatcher.message(ThreadState.thread, F.text)
async def handle_text_message(message: Message, state: FSMContext):
    data = await state.storage.get_data(StorageKey(bot_id=voicer_bot.id, user_id=message.from_user.id, chat_id=message.chat.id))
    await run_text(message, data['thread'])
    process_event("UserSendText", str(message.from_user.id), "Пользователь предпочёл общаться с ботом посредством текста")


@dispatcher.message(ThreadState.thread, F.photo)    
async def handle_photo_message(message: Message):
    await run_photo(message)
    process_event("UserSendPhoto", str(message.from_user.id), "Пользователь сбросил боту фотографию для распознавания эмоции на нём")


@dispatcher.message(ThreadState.thread, F.voice)
async def handle_voice_message(message: Message, state: FSMContext):
    data =  await state.storage.get_data(StorageKey(bot_id=voicer_bot.id, user_id=message.from_user.id, chat_id=message.chat.id))
    await run_voice(message, data['thread'])   
    process_event("UserSendVoice", str(message.from_user.id), "Пользователь предпочёл общаться с ботом посредством голоса")


async def main():
    await init_openai()
    await dispatcher.start_polling(voicer_bot)


if __name__ == "__main__":
    asyncio.run(main()) 