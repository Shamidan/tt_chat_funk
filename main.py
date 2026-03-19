import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

MODEL = "gemini-2.0-flash-exp"


# Функция для получения времени
def get_current_time():
    """Возвращает текущее время в формате ЧЧ:ММ:СС"""
    return datetime.now().strftime("%H:%M:%S")


# Описание функции для API
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Получить текущее время. Используй эту функцию, когда пользователь спрашивает 'сколько времени', 'который час', 'текущее время' и т.д.",
            "parameters": {
                "type": "object",
                "properties": {},  # Функция без параметров
                "required": []
            }
        }
    }
]

# Системный промпт с инструкцией
system_prompt = """Ты - полезный ассистент.
У тебя есть функция get_current_time, которая возвращает текущее время.
Используй её, когда пользователь спрашивает про время (например: "сколько времени?", "который час?", "текущее время").
Для обычных вопросов просто отвечай как обычно."""

# История сообщений
messages = [
    {"role": "system", "content": system_prompt}
]

print("🤖 Чат-бот запущен! (Напиши 'пока' для выхода)")
print("-" * 50)

while True:
    # Получаем сообщение от пользователя
    user_input = input("\n👤 Вы: ").strip()

    # Проверка на выход
    if user_input.lower() in ["пока", "выход", "exit", "quit", "bye"]:
        print("🤖 Бот: До свидания! 👋")
        break

    if not user_input:
        continue

    # Добавляем сообщение в историю
    messages.append({"role": "user", "content": user_input})

    try:
        # Отправляем запрос в Gemini
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        # Получаем ответ от модели
        assistant_message = response.choices[0].message

        # Проверяем, хочет ли модель вызвать функцию
        if assistant_message.tool_calls:
            print("🔧 [Вызываю функцию get_current_time...]")

            # Вызываем функцию
            time_result = get_current_time()

            # Добавляем запрос на вызов функции в историю
            messages.append(assistant_message)

            # Отправляем результат функции обратно
            function_call_result_message = {
                "role": "tool",
                "content": time_result,
                "tool_call_id": assistant_message.tool_calls[0].id
            }
            messages.append(function_call_result_message)

            # Получаем финальный ответ от модели
            second_response = client.chat.completions.create(
                model=MODEL,
                messages=messages
            )
            final_message = second_response.choices[0].message.content
        else:
            # Обычный ответ без вызова функции
            final_message = assistant_message.content

        # Выводим ответ
        print(f"🤖 Бот: {final_message}")

        # Добавляем ответ в историю
        messages.append({"role": "assistant", "content": final_message})

    except Exception as e:
        print(f"❌ Ошибка: {e}")

print("\n" + "-" * 50)
print("Чат завершен")