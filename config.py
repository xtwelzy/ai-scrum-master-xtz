import os
from dotenv import load_dotenv

load_dotenv()

# Jira
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

# Telegram Bot
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Jira project
PROJECT_KEY = os.getenv("PROJECT_KEY", "SMAI")
PROJECT_ID = os.getenv("PROJECT_ID", "10033")

# Team assignees
TEAM = {
    "xtwelzy": "712020:6b7b2f59-89aa-464e-9f14-31fdf4845ccf",
    "xtwelzy serafiel": "712020:2be6d4c8-e476-454d-83d4-035d35549384",
    "xtwenbe": "712020:2b602b15-4c17-4b1a-bc72-9ec39b84eec9",
}