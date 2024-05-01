from settings import voicer_bot

async def download_file(dest, file_id):
    file_info = await voicer_bot.get_file(file_id)
    await voicer_bot.download_file(file_info.file_path, destination=dest)