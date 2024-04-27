from settings import settings
from openai import AsyncOpenAI
import uuid


openai_client = None
openai_assistant = None
threads = dict()


async def init_openai():
    global openai_client, openai_assistant
    openai_client = AsyncOpenAI(api_key=settings.API_KEY)

    openai_assistant = await openai_client.beta.assistants.create(
        name="General Assistant",
        instructions="You are a wise person whose purpose is to answer different questions of different people. Share your wisdom with others.",
        model="gpt-4-turbo",
    )


async def get_thread(id):
    if id not in threads.keys():
        threads[id] = await openai_client.beta.threads.create()
    return threads[id]


async def STT(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = await openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
        )
        return transcription.text
    

async def assistant(prompt, thread):
    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=openai_assistant.id,
        instructions="Answer user's questions. Be polite and kind."
    )
        
    if run.status == 'completed': 
        messages = await openai_client.beta.threads.messages.list(
            thread_id=thread.id,
        )   
        return messages.data[0].content[0].text.value
    else:
        return 'Sorry, some troubles occured'
    
    
async def TTS(text):
    path = f"./{uuid.uuid4()}.mp3"
    async with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1-hd",
        voice="echo",
        input=text,
    ) as response:
        await response.stream_to_file(path)
    return path