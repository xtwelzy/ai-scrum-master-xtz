<h1 align="center">🤖 AI Scrum Master – Intelligent Agile Automation Bot</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Aiogram-3.x-0096FF?style=for-the-badge">
  <img src="https://img.shields.io/badge/OpenAI_API-Enabled-412991?style=for-the-badge&logo=openai">
  <img src="https://img.shields.io/badge/Jira-Integration-2684FF?style=for-the-badge&logo=jira">
  <br>
  <img src="https://img.shields.io/badge/Status-Production-ready-brightgreen?style=for-the-badge">
</p>

<p align="center">
  <strong>Полностью автоматизированный Agile-бот для Telegram</strong><br>
  Генерация Epics → Features → Stories → Tasks → Subtasks<br>
  Автоматическое распределение исполнителей, оценка времени и создание задач в Jira
</p>

---

<h2 align="center">✨ Основные возможности</h2>

<div align="center">
  
<table>
<tr><td>

### 🤖 Генерация Agile структуры (LLM)
- Полный пайплайн: **Epic → Feature → Story → Task → Subtask**
- Жёсткая JSON-структура (валидируется)
- Автоматические оценки времени: `15m`, `1h`, `2h`, `1d`  
- Чистые описания задач

</td><td>

### 👥 Распределение исполнителей
- Умное round-robin распределение
- Выбор исполнителей вручную через Telegram кнопки
- Каскадная логика Feature → Subtasks

</td></tr>

<tr><td>

### 🟦 Синхронизация с Jira
- Создание Epic
- Feature → Story
- Story → Task
- Task → Subtask  
✔ Полностью сохраняет иерархию  
✔ Устанавливает оценку времени  
✔ Привязывает исполнителей

</td><td>

### 🎙 Интеграция с Meeting EXE
- `/start_meeting` — запуск локальной записи
- `/stop_meeting` — автогенерация summary
- Готово к использованию в реальных созвонах

</td></tr>
</table>

</div>

---

<h2 align="center">📁 Структура проекта</h2>

ai-scrum-master/
│── main.py                # Точка входа
│── bot.py                 # Telegram логика, FSM, маршруты
│── config.py              # Конфигурация (.env)
│── jira_client.py         # Создание задач в Jira
│── llm.py                 # Работа с OpenAI (Agile генератор)
│── utils.py               # Парсер JSON, форматирование
│── config.example.py      # Пример конфигурации
│── requirements.txt       # Python зависимости
└── README.md
<h2 align="center">🎨 UI Showcase</h2> <div align="center"> <img width="800" src="https://github.com/xtwelzy/ai-scrum-master/assets/preview-example.png" alt="preview">
<sub><i>Если хочешь — сделаю для тебя прям настоящие UI скрины и вставим сюда.</i></sub>

</div>
<h2 align="center">🧠 Как работает система</h2>
🟩 1. Пользователь вызывает команду
/create <описание фичи>
🟩 2. Бот отправляет запрос в OpenAI
Генерация строгого JSON

Добавление estimate

Создание многоуровневой структуры

🟩 3. Telegram Bot показывает пользователю красивые меню
Inline-кнопки

Выбор исполнителей

Выбор времени

Просмотр полной структуры

🟩 4. По нажатию кнопки → структура автоматически создаётся в Jira
Создаётся Epic

Затем каждая Feature → Story

Каждая Story → Task

Каждая Task → Subtask

Привязываются исполнители и время

🟩 5. Пользователь получает сообщение:
✅ Все задачи успешно созданы!
<h2 align="center">🔐 Установка и запуск</h2>
1️⃣ Клонировать репозиторий
git clone https://github.com/xtwelzy/ai-scrum-master.git
cd ai-scrum-master
2️⃣ Установить зависимости
pip install -r requirements.txt
3️⃣ Создать файл .env
JIRA_DOMAIN=https://your.atlassian.net
JIRA_EMAIL=you@gmail.com
JIRA_API_TOKEN=token

TELEGRAM_BOT_TOKEN=your_tg_token
OPENAI_API_KEY=sk-xxxx

PROJECT_KEY=SMAI
PROJECT_ID=10033
⚠️ .env добавлен в .gitignore, ключи не попадут в репозиторий.

4️⃣ Запустить бота
python main.py
<h2 align="center">📲 Команды Telegram-бота</h2>
Команда	Описание
/start	Приветствие
/create <текст>	Генерация Agile структуры
/start_meeting	Запуск записи встречи
/stop_meeting	Остановка + summary
(автоматически)	Умное распределение исполнителей

<h2 align="center">🔧 Технологии</h2> <div align="center"> <img src="https://skillicons.dev/icons?i=python,idea,git,github" height="60"> <br> <img src="https://skillicons.dev/icons?i=aiogram" height="60"> <br> <img src="https://img.shields.io/badge/OpenAI_API-Enabled-000?logo=openai&style=for-the-badge"> <img src="https://img.shields.io/badge/Jira_API-Active-2684FF?style=for-the-badge&logo=jira"> </div>
<h2 align="center">❤️ Автор</h2> <p align="center"> <b>Разработчик:</b> Братуха (xtwelzy)<br> <b>Проект для:</b> ForteBank AI Hackathon<br> </p>
<h2 align="center">📄 Лицензия</h2>
MIT — свободно для использования.
