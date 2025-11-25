# meeting_agent/recorder.py

import sounddevice as sd
import numpy as np
import wave
import threading
import time


class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self._recording = False
        self._thread = None
        self.audio = None

    def start(self):
        if self._recording:
            return

        print("🎙 Recording started…")

        self._recording = True
        self.audio = []

        def _record_loop():
            while self._recording:
                chunk = sd.rec(
                    int(0.5 * self.samplerate),
                    samplerate=self.samplerate,
                    channels=self.channels,
                    dtype="int16"
                )
                sd.wait()
                self.audio.append(chunk)

        self._thread = threading.Thread(target=_record_loop, daemon=True)
        self._thread.start()

    def stop(self):
        print("🛑 Recording stopped")
        self._recording = False
        if self._thread:
            self._thread.join()

    def save_wav(self, path: str):
        if not self.audio:
            return False

        audio = np.concatenate(self.audio, axis=0)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)
            wf.setframerate(self.samplerate)
            wf.writeframes(audio.astype(np.int16).tobytes())

        print("💾 Saved:", path)
        return True
