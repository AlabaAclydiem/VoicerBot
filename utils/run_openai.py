from settings import voicer_bot
from service.open_ai import STT, assistant, TTS, emotions, get_thread
from aiogram.types import FSInputFile
from utils.delete_files import delete_files
from utils.download_file import download_file
from utils.convert_to_base64 import convert_to_base64
import uuid

async def run_voice(message, thread_id):
    dest = f'./{uuid.uuid4()}.ogg'
    await download_file(dest, message.voice.file_id)
    prompt = await STT(dest)
    response = await assistant(prompt, thread_id, message.from_user.id)
    path = await TTS(response)
    await message.answer(response)
    await message.answer_voice(FSInputFile(path))
    delete_files([dest, path])
    
async def run_text(message, thread_id):
    prompt = message.text
    response = await assistant(prompt, thread_id, message.from_user.id)
    path = await TTS(response)
    await message.answer(response)
    await message.answer_voice(FSInputFile(path))
    delete_files([path])

async def run_photo(message):
    dest = f'./{uuid.uuid4()}.jpeg'
    await download_file(dest, message.photo[-1].file_id)
    response = await emotions(convert_to_base64(dest))
    await message.answer(response)
    delete_files([dest])
