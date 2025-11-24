# utils.py

import json


def parse_agile_json(llm_output):

    try:
        return json.loads(llm_output)
    except:
        print("Ошибка парсинга JSON!")
        return None


def format_agile_preview(data):

    text = f"📌 EPIC: {data['epic']['summary']}\n"
    text += f"   {data['epic']['description']}\n\n"

    for feature in data["features"]:
        text += f"⭐ Feature: {feature['summary']}\n"
        for story in feature["stories"]:
            text += f"   🔶 Story: {story['summary']}\n"
            for task in story["tasks"]:
                text += f"      ✔ Task: {task['summary']}\n"
                for sub in task["subtasks"]:
                    text += f"         ▫ Subtask: {sub['summary']}\n"

        text += "\n"

    return text
