# meeting_agent/server.py

import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from recorder import AudioRecorder
from whisper_client import transcribe_audio, summarize_transcript
from jira_sync import send_meeting_summary_to_jira  # если нужно Jira

load_dotenv()

app = FastAPI()

# Один глобальный рекордер на процесс
recorder = AudioRecorder()
AUDIO_PATH = "meeting_record.wav"  # файл, куда будем писать


@app.post("/start_record")
def start_record():
    """
    Старт записи митинга.
    Вызывается из Telegram-бота командой /start_meeting.
    """
    try:
        recorder.start()
        return JSONResponse({"status": "ok", "message": "recording_started"})
    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )


@app.post("/stop_record")
def stop_record():
    """
    Стоп записи + транскрибация + summary.
    Возвращает summary в JSON, которое бот покажет в чате.
    """
    try:
        recorder.stop()
        ok = recorder.save_wav(AUDIO_PATH)
        if not ok:
            return JSONResponse(
                {"status": "error", "message": "no audio captured"},
                status_code=500
            )

        # 1) Транскрибация
        transcript = transcribe_audio(AUDIO_PATH)

        # 2) Summary
        summary = summarize_transcript(transcript)

        # 3) (опционально) отправить в Jira как комментарий
        try:
            send_meeting_summary_to_jira(summary)
        except Exception:
            # Не роняем сервис, если Jira упала
            pass

        # 4) Вернём данные боту
        return JSONResponse({
            "status": "ok",
            "summary": summary,
            "transcript": transcript
        })

    except Exception as e:
        return JSONResponse(
            {"status": "error", "message": str(e)},
            status_code=500
        )
