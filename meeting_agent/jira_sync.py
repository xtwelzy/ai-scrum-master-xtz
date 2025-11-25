# meeting_agent/jira_sync.py

import os
import sys

# Добавляем путь к корню проекта
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from dotenv import load_dotenv
from jira_client import add_comment  # теперь работает

load_dotenv()

MEETING_ISSUE_KEY = os.getenv("MEETING_ISSUE_KEY")


def send_meeting_summary_to_jira(summary_text: str):
    """
    Отправляет summary митинга в Jira как комментарий.
    """
    if not MEETING_ISSUE_KEY:
        return None

    comment = f"📝 Meeting summary:\n\n{summary_text}"
    return add_comment(MEETING_ISSUE_KEY, comment)
