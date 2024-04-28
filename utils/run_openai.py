from settings import voicer_bot
from service.open_ai import STT, assistant, TTS, get_thread
from aiogram.types import FSInputFile
from utils.delete_files import delete_files
import uuid

async def run_openai(message, voice=False):
    thread = await get_thread(message.from_user.id)
    dest = None
    if voice:   
        dest = f'./{uuid.uuid4()}.ogg'
        file_info = await voicer_bot.get_file(message.voice.file_id)
        await voicer_bot.download_file(file_info.file_path, destination=dest)
        prompt = await STT(dest)
    else:
        prompt = message.text
    response = await assistant(prompt, thread, message.from_user.id)
    path = await TTS(response)
    await message.answer(response)
    await message.answer_voice(FSInputFile(path))
    delete_files([dest, path])