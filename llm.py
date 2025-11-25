
import json
from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_agile_structure(text: str) -> str:
    """
    Создаём Agile структуру (Epic → Features → Stories → Tasks → Subtasks)
    Модель обязана вернуть ЧИСТЫЙ JSON.
    Добавлены оценки времени (estimate).
    """

    prompt = f"""
Ты — Senior Agile Scrum Master и Tech Lead.
Сгенерируй Agile структуру в формате строгого JSON.

ДОБАВЬ поле "estimate" в ЧАСАХ И МИНУТАХ: пример "4h", "30m", "1h 30m".

Правила оценки:
- Простые действия → 15–60 минут
- Маленькие задачи → 1–2 часа
- Средние → 4–8 часов
- Большие → 1–2 дня (8–16 часов)
- Очень большие → 2–5 дней (16–40 часов)

Формат JSON (СТРОГО):
{{
  "epic": {{
    "summary": "string",
    "description": "string",
    "estimate": "string"
  }},
  "features": [
    {{
      "summary": "string",
      "estimate": "string",
      "stories": [
        {{
          "summary": "string",
          "estimate": "string",
          "tasks": [
            {{
              "summary": "string",
              "description": "string",
              "estimate": "string",
              "subtasks": [
                {{
                  "summary": "string",
                  "description": "string",
                  "estimate": "string"
                }}
              ]
            }}
          ]
        }}
      ]
    }}
  ]
}}

ПРАВИЛА:
- Верни ТОЛЬКО JSON.
- НЕ используй markdown.
- НЕ используй ```json.
- НЕ добавляй текст до или после JSON.
- Оценка ("estimate") обязательна.
- Значения estimate: только форматы "4h", "30m", "1h 30m".

Техническое задание:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    raw = response.choices[0].message.content

    cleaned = raw.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    return cleaned
