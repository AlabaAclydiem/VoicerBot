from settings import settings
from openai import OpenAI

openai_client = OpenAI(api_key=settings.API_KEY)

openai_assistant = openai_client.beta.assistants.create(
    name="General Assistant",
    instructions="You are a wise person whose purpose is to answer different questions of different people. Share your wisdom with others.",
    model="gpt-4-turbo",
)

thread = openai_client.beta.threads.create()

def STT(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
        )
        return transcription.text
    
def assistant(prompt):
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=openai_assistant.id,
        instructions="Answer user's questions. Be polite and kind."
    )
        
    if run.status == 'completed': 
        messages = openai_client.beta.threads.messages.list(
            thread_id=thread.id,
        )   
        return messages.data[0].content[0].text.value
    else:
        return 'Sorry, some troubles occured'
    
def TTS(text):
    path = "speech.mp3"
    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1-hd",
        voice="echo",
        input=text,
    ) as response:
        response.stream_to_file(path)
    return path