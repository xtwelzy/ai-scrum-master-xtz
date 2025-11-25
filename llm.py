import json
from openai import OpenAI
from config import OPENAI_API_KEY, TEAM

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_agile_structure(text: str) -> str:
    """
    Создаём Agile структуру (Epic → Features → Stories → Tasks → Subtasks)
    Модель обязана вернуть ЧИСТЫЙ JSON.
    """

    team_list = ", ".join(TEAM.keys())

    prompt = f"""
Ты — Senior Agile Scrum Master и Tech Lead.
Сгенерируй Agile структуру в формате строгого JSON.

⚠️ ОЧЕНЬ ВАЖНО:
Используй ТОЛЬКО следующих участников команды для назначения исполнителей:
{team_list}

Не придумывай новых людей и не используй других имён.  
Если исполнитель не указан — ставь None (пустую строку), бот назначит его сам.

Добавь поле "estimate" в ЧАСАХ И МИНУТАХ: пример "4h", "30m", "1h 30m".

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
    "estimate": "string",
    "assignee": "string или пустая строка"
  }},
  "features": [
    {{
      "summary": "string",
      "estimate": "string",
      "assignee": "string или пустая строка",
      "stories": [
        {{
          "summary": "string",
          "estimate": "string",
          "assignee": "string или пустая строка",
          "tasks": [
            {{
              "summary": "string",
              "description": "string",
              "estimate": "string",
              "assignee": "string или пустая строка",
              "subtasks": [
                {{
                  "summary": "string",
                  "description": "string",
                  "estimate": "string",
                  "assignee": "string или пустая строка"
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
- НЕ ДОБАВЛЯЙ ПОЛЕ "assignee". Оно будет назначено ПОСЛЕ пользователем.
- Оценка ("estimate") обязательна.
- assignee только из списка: {team_list} или "" (пусто).
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
