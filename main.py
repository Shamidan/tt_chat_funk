import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

dotenv_patch = r"tt_chat_funk/.env"
load_dotenv(dotenv_patch)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


tools = [{
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Возвращает текущее время",
        "parameters": {"type": "object", "properties": {}}
    }
}]

messages = [{
    "role": "system",
    "content": """Ты - ассистент с функцией get_current_time.

ВАЖНО: Для получения времени используй ТОЛЬКО механизм function calling

Ответы в формате:
<tool_call>
<function=get_current_time>
</function>
</tool_call>

Принимаются как неправильные
"""
}]

print("Бот запущен. Введите 'выход' для завершения.")

while True:
    user_input = input("Вы: ")

    if user_input.lower() in ["выход", "exit"]:
        print("Бот: Пока")
        break

    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            time = get_current_time()
            messages.append(msg)
            messages.append({
                "role": "tool",
                "content": time,
                "tool_call_id": msg.tool_calls[0].id
            })

            final = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            print(f"Бот: {final.choices[0].message.content}")
        else:
            print(f"Бот: {msg.content}")
            messages.append(msg)

    except Exception as e:
        print(f"Ошибка: {e}")
