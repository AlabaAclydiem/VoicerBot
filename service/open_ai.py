from database.database import save_user_values, check_user_values
from settings import settings
from openai import AsyncOpenAI
import uuid
import json


openai_client = None
openai_assistant = None
vector_store = None
threads = dict()


async def init_openai():
    global openai_client, openai_assistant, vector_store

    openai_client = AsyncOpenAI(api_key=settings.API_KEY)

    openai_assistant = await openai_client.beta.assistants.create(
        name="Ассистент ценностей",
        instructions="Ты высококлассный психолог. Твоя задача - общаться с человеком, разговаривать с ним, задавать вопросы. Твоя цель - определить его главные жизненные ценности. Как только ты их определишь, перечисли их ему",
        model="gpt-4-turbo",
        tools=[
            {"type": "file_search"},
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

    vector_store = await openai_client.beta.vector_stores.create(
        name="Хранилище_Тревожности",
    )

    await openai_client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[open("././anxiety.docx", "rb")]
    )

    await openai_client.beta.assistants.update(
        assistant_id=openai_assistant.id,
        tool_resources={
            "file_search": {"vector_store_ids": [vector_store.id]}
        }
    )

    print('openai inited')



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


async def get_thread_messages(thread_id):
    return await openai_client.beta.threads.messages.list(
        thread_id=thread_id,
    )   

async def assistant(prompt, thread_id, telegram_id):
    await openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )

    run = await openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=openai_assistant.id,
        instructions="У тебя есть файл, который содержит информацию про тревожность. Если пользователь спросит что-нибудь касательно тревожности, ты можешь поискать информацию в этом файле"
    )
        
    tool_outputs = []
    if run.required_action is not None:
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "save_values":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": await save_values(json.loads(tool.function.arguments)['values'], telegram_id)
                })
                run = await openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread_id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )

    if run.status == 'completed': 
        messages = await get_thread_messages(thread_id)
        content = messages.data[0].content[0].text
        annotations = content.annotations
        for annotation in annotations:
            citation = getattr(annotation, 'file_citation', None)
            if citation is not None:
                file = await openai_client.files.retrieve(
                    citation.file_id
                )
                content.value = content.value.replace(annotation.text, f"(Из файла {file.filename})")
        return content.value
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


async def save_values(values, telegram_id):
    response = await openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "Ты квалифицированный психолог. Твоя задача определить, корректен ли перечень предлагаемых человеческих ценностей, могут ли такие существовать, есть ли в нём противоречия. Ответ давать либо true, если всё правильно, иначе false"},
            {"role": "user", "content": f"Проверь следующий перечень ценностей: {values}"}
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "validate_values",
                    "description": "Эту функцию вызываешь всегда. Её параметром указывай булево значения корректности полученных ценностей. либо True, либо False",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "correct": {
                                "type": "boolean",
                                "description": "Булево значение корректности полученных ценностей"
                                },
                            },
                        "required": ["correct"]
                    }
                }
            },
        ],
        tool_choice={"type": "function", "function": {"name": "validate_values"}}
    )
    correct = json.loads(response.choices[0].message.tool_calls[0].function.arguments)['correct']
    if correct:
        db_values = await check_user_values(telegram_id)
        if not db_values:
            await save_user_values(telegram_id, values)
            return "Ценности определены верно. Они были сохранены. Сообщи об этом пользователю, поблагодари его и заканчивай работу"
        else:
            return f"Ваши ценности уже были определены. Выведи пользователю их. Вот они: {values}"
    else:
        return "Ценности бессмысленны или некорректны. Скажи пользователю, что что-то не так, и продолжай узнавать информацию"
    

async def emotions(base64_image):
    response = await openai_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Определи эмоции человека на фотографии. Перечисли одним словом или списком слов без дополнительных комментариев"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_emotion",
                    "description": "Эту функцию вызываешь всегда. Её параметром указывай одну выявленную эмоцию человека из перечня возможных",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "emotion": {
                                "type": "string",
                                "enum": ["Радость", "Злость", "Отвращение", "Страх", "Грусть", "Удивление", "Доверие", "Предвкушение", "Презрение", "Вина", "Стыд"],
                                "description": "Строковое значение, описывающее эмоцию человека на фотографии."
                                },
                            },
                        "required": ["emotion"]
                    }
                }
            },
        ],
        tool_choice={"type": "function", "function": {"name": "get_emotion"}},
        max_tokens=300
    )

    return json.loads(response.choices[0].message.tool_calls[0].function.arguments)['emotion']
