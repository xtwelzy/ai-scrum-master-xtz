# meeting_agent/whisper_client.py

import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def transcribe_audio(file_path: str) -> str:
    """
    Отправляем аудио в Whisper-модель, получаем текст.
    """
    with open(file_path, "rb") as f:
        # Название модели — пример, уточни в доке/консоли OpenAI
        result = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",  # или "whisper-1", если такой используешь
            file=f,
            response_format="text"
        )
    # result обычно уже строка, но можно обернуть в str
    return str(result)


def summarize_transcript(transcript: str) -> str:
    from config import TEAM   # импортируем команду из твоего проекта

    team_list = ", ".join(TEAM.keys())

    prompt = f"""
Ты — Senior Scrum Master банка.

Вот транскрипт части встречи:

{transcript}

Сгенерируй структурированное резюме.

⚠️ Жёсткое правило:
Action items должны использовать ТОЛЬКО участников команды:
{team_list}

НЕ придумывай других людей.
Если невозможно определить исполнителя — укажи "" (пусто).

Формат ответа:
1) Summary
2) Ключевые решения
3) Action items (только имена из списка выше)
"""

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return resp.choices[0].message.content.strip()

