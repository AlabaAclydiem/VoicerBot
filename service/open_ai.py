from settings import settings
from openai import AsyncOpenAI
from utils.save_values import save_values
import uuid
import json


openai_client = None
openai_assistant = None
threads = dict()


async def init_openai():
    global openai_client, openai_assistant
    openai_client = AsyncOpenAI(api_key=settings.API_KEY)

    openai_assistant = await openai_client.beta.assistants.create(
        name="Ассистент ценностей",
        instructions="Ты высококлассный психолог. Твоя задача - общаться с человеком, разговаривать с ним, задавать вопросы. Твоя цель - определить его главные жизненные ценности. Как только ты их определишь, перечисли их ему",
        model="gpt-4-turbo",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "save_values",
                    "description": "Вызови эту функцию тогда, когда определишь основные ценности человека, с которым разговариваешь",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "values": {
                                "type": "string",
                                "description": "Ценности человека, перечисленные через запятую. Например 'любовь, семья, деньги'"
                                },
                            },
                        "required": ["values"]
                    }
                }
            },
        ]
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


async def get_thread_messages(thread):
    return await openai_client.beta.threads.messages.list(
        thread_id=thread.id,
    )   

async def assistant(prompt, thread):
    await openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt,
    )

    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=openai_assistant.id,
    )
        
    tool_outputs = []
    if run.required_action is not None:
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "save_values":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": save_values(json.loads(tool.function.arguments)['values'])
                })
                run = await openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

    if run.status == 'completed': 
        messages = await get_thread_messages(thread)
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