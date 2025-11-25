import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN, TEAM
from llm import generate_agile_structure
from utils import parse_agile_json


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# =====================================================
# LOCAL CLIENT (EXE API)
# =====================================================

CLIENT_API = "http://127.0.0.1:5678"


# =====================================================
# FSM STATES
# =====================================================

class AssignStates(StatesGroup):
    choosing_assignee = State()
    choosing_time = State()
    custom_time_input = State()


class MeetingStates(StatesGroup):
    waiting_action = State()


# =====================================================
# EXECUTOR DISTRIBUTION
# =====================================================

rr_index = 0


def next_assignee():
    global rr_index
    members = list(TEAM.values())
    assignee = members[rr_index % len(members)]
    rr_index += 1
    return assignee


def get_assignee(raw):
    """ Мягкая и безопасная нормализация """
    if not raw:
        return next_assignee()

    if isinstance(raw, list):
        raw = raw[0]

    if isinstance(raw, dict):
        raw = raw.get("name", "")

    if isinstance(raw, str):
        clean = raw.strip().lower()

        if clean in TEAM:
            return TEAM[clean]

        for key in TEAM:
            if clean == key.lower().strip():
                return TEAM[key]

    return next_assignee()


# =====================================================
# REMOVE ALL LLM ASSIGNEES (важно!)
# =====================================================

def strip_assignees(js):
    """ Удаляем любые assignee, которые мог сгенерировать LLM """
    for f in js["features"]:
        f.pop("assignee", None)
        for s in f["stories"]:
            s.pop("assignee", None)
            for t in s["tasks"]:
                t.pop("assignee", None)
                for sub in t["subtasks"]:
                    sub.pop("assignee", None)
    return js


# =====================================================
# CASCADE ASSIGNEE — жёсткое назначение
# =====================================================

def cascade_assignee(feature):
    """ ВСЕ story/task/subtask получают исполнителя Feature """
    root = feature.get("assignee")
    if not root:
        return

    for story in feature["stories"]:
        story["assignee"] = root
        for task in story["tasks"]:
            task["assignee"] = root
            for sub in task["subtasks"]:
                sub["assignee"] = root


# =====================================================
# NORMALIZER
# =====================================================

def normalize_structure(js):
    js["epic"].setdefault("estimate", "1h")

    for f in js["features"]:
        f.setdefault("estimate", "1h")
        f.setdefault("stories", [])
        for s in f["stories"]:
            s.setdefault("estimate", "1h")
            s.setdefault("tasks", [])
            for t in s["tasks"]:
                t.setdefault("estimate", "1h")
                t.setdefault("subtasks", [])
                for sub in t["subtasks"]:
                    sub.setdefault("estimate", "1h")
    return js


# =====================================================
# KEYBOARDS
# =====================================================

def kb_start_assignment():
    kb = InlineKeyboardBuilder()
    kb.button(text="👥 Выбрать исполнителей", callback_data="start_assignees")
    kb.button(text="❌ Отменить", callback_data="cancel_all")
    kb.adjust(1)
    return kb.as_markup()


def kb_features_assignees(features):
    kb = InlineKeyboardBuilder()
    for i, f in enumerate(features):
        label = f"Изменить ({f.get('assignee')})" if f.get("assignee") else "Назначить"
        kb.button(
            text=f"{i + 1}. {f['summary']} — [{label}]",
            callback_data=f"assf_{i}",
        )
    kb.adjust(1)
    return kb.as_markup()


def kb_assignees(fid: int):
    kb = InlineKeyboardBuilder()
    for name in TEAM.keys():
        kb.button(text=name, callback_data=f"assa_{fid}_{name}")
    kb.adjust(1)
    return kb.as_markup()


def kb_preview_actions():
    kb = InlineKeyboardBuilder()
    kb.button(text="⏱ Назначить время", callback_data="edit_time")
    kb.button(text="🔄 Изменить исполнителей", callback_data="edit_assignees")
    kb.button(text="❌ Отменить", callback_data="cancel_all")
    kb.adjust(1)
    return kb.as_markup()


def kb_final_actions():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Создать Jira", callback_data="create_jira")
    kb.button(text="⏱ Изменить время", callback_data="edit_time")
    kb.button(text="🔄 Изменить исполнителей", callback_data="edit_assignees")
    kb.button(text="❌ Отменить", callback_data="cancel_all")
    kb.adjust(1)
    return kb.as_markup()


def kb_features_time(features):
    kb = InlineKeyboardBuilder()
    for i, f in enumerate(features):
        kb.button(
            text=f"{i + 1}. {f['summary']} — {f['estimate']}",
            callback_data=f"timef_{i}",
        )
    kb.adjust(1)
    return kb.as_markup()


def kb_time_options(fid: int):
    options = ["15m", "30m", "45m", "1h", "1h 30m", "2h", "3h", "4h", "6h", "8h", "1d"]
    kb = InlineKeyboardBuilder()
    for o in options:
        kb.button(text=o, callback_data=f"time_{fid}_{o}")
    kb.button(text="⌨ Свое время", callback_data=f"time_custom_{fid}")
    kb.adjust(2)
    return kb.as_markup()


# =====================================================
# FULL STRUCTURE PREVIEW
# =====================================================

def render_full_preview(js):
    txt = "📋 *ПОЛНАЯ СТРУКТУРА ПРОЕКТА*\n\n"
    txt += f"*EPIC:* {js['epic']['summary']} — время: {js['epic']['estimate']}\n\n"

    for i, f in enumerate(js["features"]):
        txt += f"*{i + 1}) Feature:* {f['summary']}\n"
        txt += f"👤 Исполнитель: `{f.get('assignee', '—')}`\n"
        txt += f"⏱ Время: {f['estimate']}\n"

        for s in f["stories"]:
            txt += f"   • Story: {s['summary']} — {s['estimate']}\n"
            for t in s["tasks"]:
                txt += f"       - Task: {t['summary']} — {t['estimate']}\n"
                for sub in t["subtasks"]:
                    txt += f"           · Subtask: {sub['summary']} — {sub['estimate']}\n"
        txt += "\n"
    return txt


# =====================================================
# START
# =====================================================

@dp.message(Command("start"))
async def start_cmd(msg: types.Message):
    await msg.answer("👋 Привет! Отправь /create <ТЗ>.")


# =====================================================
# CREATE
# =====================================================

@dp.message(Command("create"))
async def create_cmd(msg: types.Message, state: FSMContext):
    raw = msg.text.replace("/create", "").strip()

    await msg.answer("⏳ Генерация структуры...")

    js = parse_agile_json(generate_agile_structure(raw))
    js = normalize_structure(js)
    js = strip_assignees(js)

    await state.update_data(structure=js)

    preview_text = render_full_preview(js)

    await msg.answer(
        preview_text,
        parse_mode="Markdown",
        reply_markup=kb_start_assignment(),
    )


# =====================================================
# ASSIGNMENT FLOW
# =====================================================

@dp.callback_query(lambda c: c.data == "start_assignees")
async def start_assignees(cb: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    js = data["structure"]

    await cb.message.answer(
        "👥 Выбери исполнителей:",
        reply_markup=kb_features_assignees(js["features"]),
    )

    await state.set_state(AssignStates.choosing_assignee)


@dp.callback_query(lambda c: c.data.startswith("assf_"))
async def choose_feature_assignee(cb: types.CallbackQuery, state: FSMContext):
    fid = int(cb.data.split("_")[1])
    await state.update_data(current_feature=fid)

    await cb.message.answer(
        "Выбери исполнителя:",
        reply_markup=kb_assignees(fid),
    )


@dp.callback_query(lambda c: c.data.startswith("assa_"))
async def apply_assignee(cb: types.CallbackQuery, state: FSMContext):
    _, fid, name = cb.data.split("_")
    fid = int(fid)

    data = await state.get_data()
    js = data["structure"]

    js["features"][fid]["assignee"] = name
    await state.update_data(structure=js)

    txt = render_full_preview(js)

    if all(f.get("assignee") for f in js["features"]):
        await cb.message.answer(
            txt,
            parse_mode="Markdown",
            reply_markup=kb_final_actions(),
        )
    else:
        await cb.message.answer(
            txt,
            parse_mode="Markdown",
            reply_markup=kb_features_assignees(js["features"]),
        )


# =====================================================
# TIME FLOW
# =====================================================

@dp.callback_query(lambda c: c.data == "edit_time")
async def edit_time_start(cb, state: FSMContext):
    data = await state.get_data()
    js = data["structure"]

    await cb.message.answer(
        "⏱ Выбери Feature для установки времени:",
        reply_markup=kb_features_time(js["features"]),
    )

    await state.set_state(AssignStates.choosing_time)


@dp.callback_query(lambda c: c.data.startswith("timef_"))
async def choose_time_feature(cb, state: FSMContext):
    fid = int(cb.data.split("_")[1])
    await state.update_data(current_feature=fid)

    await cb.message.answer(
        "⏱ Выбери время:",
        reply_markup=kb_time_options(fid),
    )


@dp.callback_query(lambda c: c.data.startswith("time_") and "custom" not in c.data)
async def apply_time(cb, state: FSMContext):
    _, fid, value = cb.data.split("_")
    fid = int(fid)

    data = await state.get_data()
    js = data["structure"]

    js["features"][fid]["estimate"] = value
    await state.update_data(structure=js)

    txt = render_full_preview(js)
    await cb.message.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb_final_actions(),
    )


@dp.callback_query(lambda c: c.data.startswith("time_custom_"))
async def custom_time_start(cb, state: FSMContext):
    fid = int(cb.data.split("_")[2])
    await state.update_data(current_feature=fid)

    await state.set_state(AssignStates.custom_time_input)
    await cb.message.answer("⌨ Введи своё время (например: `1h 45m`):")


@dp.message(AssignStates.custom_time_input)
async def custom_time_set(msg, state: FSMContext):
    value = msg.text.strip()

    data = await state.get_data()
    fid = data["current_feature"]
    js = data["structure"]

    js["features"][fid]["estimate"] = value
    await state.update_data(structure=js)

    txt = render_full_preview(js)
    await msg.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb_final_actions(),
    )

    await state.set_state(AssignStates.choosing_time)


# =====================================================
# CANCEL
# =====================================================

@dp.callback_query(lambda c: c.data == "cancel_all")
async def cancel_all(cb, state: FSMContext):
    await state.clear()
    await cb.message.answer("❌ Операция отменена.")


# =====================================================
# CREATE JIRA
# =====================================================

@dp.callback_query(lambda c: c.data == "create_jira")
async def jira_create(cb, state: FSMContext):
    from jira_client import create_epic, create_story, create_task, create_subtask

    data = await state.get_data()
    js = data["structure"]

    for f in js["features"]:
        cascade_assignee(f)

    await cb.message.answer("📌 Создаю задачи...")

    epic = js["epic"]
    epic_res = create_epic(
        epic["summary"],
        epic["description"],
        None,
        epic["estimate"],
    )

    if "id" not in epic_res:
        return await cb.message.answer("❌ Ошибка создания Epic")

    epic_key = epic_res["key"]

    for feature in js["features"]:
        feature_assignee = get_assignee(feature.get("assignee"))

        feature_story = create_story(
            feature["summary"],
            "",
            epic_key,
            feature_assignee,
            feature["estimate"],
        )

        if "id" not in feature_story:
            continue

        for story in feature["stories"]:
            story_assignee = get_assignee(story.get("assignee"))

            story_task = create_task(
                story["summary"],
                story.get("description", ""),
                story_assignee,
                story["estimate"],
            )

            if "id" not in story_task:
                continue

            story_task_id = story_task["id"]

            for task in story["tasks"]:
                task_assignee = get_assignee(task.get("assignee"))

                task_res = create_task(
                    task["summary"],
                    task.get("description", ""),
                    task_assignee,
                    task["estimate"],
                )

                if "id" not in task_res:
                    continue

                task_id = task_res["id"]

                for sub in task["subtasks"]:
                    sub_assignee = get_assignee(sub.get("assignee"))

                    create_subtask(
                        sub["summary"],
                        sub.get("description", ""),
                        task_id,
                        sub_assignee,
                        sub["estimate"],
                    )

    await cb.message.answer("✅ Все задачи успешно созданы!")
    await state.clear()


# =====================================================
# STOP MEETING → как /create
# =====================================================

@dp.message(Command("stop_meeting"))
async def stop_meeting(msg, state):
    try:
        r = requests.post(f"{CLIENT_API}/stop_record")
        if r.status_code != 200:
            return await msg.answer("❌ Клиент не ответил.")

        data = r.json()
        transcript = data.get("transcript", "")
        summary = data.get("summary", "")

        if not transcript.strip():
            return await msg.answer("❌ Не удалось распознать речь.")

        await state.update_data(
            meet_transcript=transcript,
            meet_summary=summary,
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="✅ Всё верно, продолжить", callback_data="meeting_confirm")
        kb.button(text="❌ Отменить", callback_data="meeting_cancel")
        kb.adjust(1)

        await msg.answer(
            f"🎧 *Вот что я услышал:*\n`{transcript}`\n\n"
            f"🎯 *Основные цели встречи:*\n{summary}",
            parse_mode="Markdown",
            reply_markup=kb.as_markup(),
        )

    except Exception as e:
        await msg.answer(f"❌ Ошибка: `{e}`")


@dp.callback_query(lambda c: c.data == "meeting_confirm")
async def meeting_confirm(cb, state):
    data = await state.get_data()
    transcript = data.get("meet_transcript", "")

    await cb.message.answer("⏳ Генерирую структуру проекта...")

    js = parse_agile_json(generate_agile_structure(transcript))
    js = normalize_structure(js)
    js = strip_assignees(js)

    await state.update_data(structure=js)

    txt = render_full_preview(js)

    await cb.message.answer(
        txt,
        parse_mode="Markdown",
        reply_markup=kb_start_assignment(),
    )


@dp.callback_query(lambda c: c.data == "edit_assignees")
async def edit_assignees(cb, state):
    data = await state.get_data()
    js = data["structure"]

    await cb.message.answer(
        "👥 Выбери Feature для редактирования исполнителя:",
        reply_markup=kb_features_assignees(js["features"]),
    )

    await state.set_state(AssignStates.choosing_assignee)


@dp.callback_query(lambda c: c.data == "meeting_cancel")
async def meeting_cancel(cb, state):
    await state.clear()
    await cb.message.answer("❌ Действие отменено.")


# =====================================================
# START MEETING
# =====================================================

@dp.message(Command("start_meeting"))
async def start_meeting(msg):
    try:
        r = requests.post(f"{CLIENT_API}/start_record")
        if r.status_code == 200:
            await msg.answer(
                "🎙 *Локальная запись встречи запущена.*",
                parse_mode="Markdown",
            )
        else:
            await msg.answer("❌ Клиент не ответил.")
    except Exception as e:
        await msg.answer(f"❌ Ошибка: `{e}`")


# =====================================================
# RUN BOT
# =====================================================

def run_bot():
    dp.run_polling(bot)


if __name__ == "__main__":
    run_bot()
