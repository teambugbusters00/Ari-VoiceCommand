"""STT (Speech-To-Text) backend abstraction layer."""
from __future__ import annotations

import base64
import io
import json
import logging
import os
import queue
import subprocess
import sys
import threading
import wave
from typing import Optional

from core._whisper_worker import WORKER_ARGUMENT, bundled_executable_path, normalize_language


class STTProvider:
    """Common interface for STT backends."""

    def transcribe(self, audio_data, mode: str | None = None) -> Optional[str]:
        raise NotImplementedError

    def is_healthy(self) -> bool:
        return True


class GoogleSTTProvider(STTProvider):
    """Google STT wrapper via speech_recognition, supporting English and Hindi bilingual transcription."""

    def __init__(self, language: str = "en-US"):
        import speech_recognition as sr

        self._language = language
        self._recognizer = sr.Recognizer()
        self._recognizer.operation_timeout = 10

    def transcribe(self, audio_data, mode: str | None = None) -> Optional[str]:
        import speech_recognition as sr

        del mode
        # 1. Try with the primary configured language (e.g. en-US or hi-IN)
        try:
            return self._recognizer.recognize_google(audio_data, language=self._language)
        except sr.UnknownValueError:
            # 2. Seamless fallback: Try alternate language (Hindi <-> English) for real-time bilingual recognition
            alternate_lang = "hi-IN" if not self._language.startswith("hi") else "en-US"
            try:
                return self._recognizer.recognize_google(audio_data, language=alternate_lang)
            except Exception:
                return None
        except (sr.RequestError, TimeoutError) as exc:
            logging.error("[GoogleSTT] request failed: %s", exc)
            return None


class WhisperSTTProvider(STTProvider):
    """Offline STT based on faster-whisper (subprocess isolated).

    Runs Whisper model in a separate process (_whisper_worker.py) to avoid DLL conflicts
    between CTranslate2(MKL) and torch/numpy(MKL).
    Communicates with main process via stdin/stdout JSON (base64 audio).
    """

    _WORKER = os.path.join(os.path.dirname(__file__), "_whisper_worker.py")
    _STARTUP_TIMEOUT_SECONDS = 30.0
    _MODEL_PREPARATION_TIMEOUT_SECONDS = 300.0
    _TRANSCRIBE_TIMEOUT_SECONDS = 20.0

    def __init__(
        self,
        model_size: str = "small",
        device: str = "auto",
        compute_type: str = "int8",
        language: str = "en",
    ):
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._language = normalize_language(language)
        self._lock = threading.Lock()
        self._proc: Optional[subprocess.Popen] = None
        self._start_worker()

    def transcribe(self, audio_data, mode: str | None = None) -> Optional[str]:
        try:
            wav_bytes = audio_data.get_wav_data()
            b64 = base64.b64encode(wav_bytes).decode("ascii")
        except Exception as exc:
            logging.error("[WhisperSTT] audio serialization failed: %s", exc)
            return None

        with self._lock:
            if not self._ensure_worker_locked():
                return None
            try:
                assert self._proc is not None and self._proc.stdin is not None and self._proc.stdout is not None
                request = json.dumps({"audio": b64, "mode": mode})
                self._proc.stdin.write((request + "\n").encode("ascii"))
                self._proc.stdin.flush()
                line = self._read_process_line(self._proc.stdout, self._TRANSCRIBE_TIMEOUT_SECONDS)
                if line is None:
                    logging.error("[WhisperSTT] transcription timeout; restarting worker.")
                    self._restart_worker_locked("transcribe timeout")
                    return None
                line = line.strip()
                if not line or line == "__NONE__":
                    return None
                return line
            except Exception as exc:
                logging.error("[WhisperSTT] transcription failed: %s", exc)
                self._restart_worker_locked("transcribe failure")
                return None

    def is_healthy(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def __del__(self):
        try:
            with self._lock:
                self._terminate_worker_locked()
        except Exception as exc:
            logging.debug("[WhisperSTT] Error during worker termination (ignored): %s", exc)

    def _start_worker(self) -> None:
        actual_device = _resolve_device(self._device)
        logging.info("[WhisperSTT] Worker starting: %s / %s / %s", self._model_size, actual_device, self._compute_type)
        env = {**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"}
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            worker_command = [
                bundled_executable_path(),
                WORKER_ARGUMENT,
                self._model_size,
                actual_device,
                self._compute_type,
                self._language,
            ]
        else:
            worker_command = [
                sys.executable,
                self._WORKER,
                self._model_size,
                actual_device,
                self._compute_type,
                self._language,
            ]
        self._proc = subprocess.Popen(  # nosemgrep
            worker_command,  # nosemgrep
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        startup_line = self._read_process_line(self._proc.stdout, self._STARTUP_TIMEOUT_SECONDS) if self._proc.stdout else None
        ready_line = (
            self._read_process_line(self._proc.stdout, self._MODEL_PREPARATION_TIMEOUT_SECONDS)
            if startup_line == "PREPARING" and self._proc.stdout
            else None
        )
        if ready_line != "READY":
            failed_proc = self._proc
            self._terminate_worker_locked()
            stderr_out = self._read_stderr_snapshot(failed_proc)
            reason = stderr_out or "Did not receive READY signal."
            raise RuntimeError(f"[WhisperSTT] worker initialization failed:\n{reason}")
        logging.info("[WhisperSTT] Worker ready")

    def _ensure_worker_locked(self) -> bool:
        if self.is_healthy():
            return True
        logging.warning("[WhisperSTT] Unhealthy worker detected — restarting.")
        return self._restart_worker_locked("worker unhealthy")

    def _restart_worker_locked(self, reason: str) -> bool:
        logging.warning("[WhisperSTT] Worker restarting: %s", reason)
        self._terminate_worker_locked()
        try:
            self._start_worker()
            return True
        except Exception as exc:
            logging.error("[WhisperSTT] Worker restart failed: %s", exc)
            return False

    def _terminate_worker_locked(self) -> None:
        proc = self._proc
        self._proc = None
        if proc is None:
            return
        try:
            if proc.poll() is None and proc.stdin is not None:
                proc.stdin.write(b"QUIT\n")
                proc.stdin.flush()
                proc.wait(timeout=3)
        except Exception as exc:
            logging.debug("[STT] Normal termination failed, trying terminate: %s", exc)
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception as terminate_exc:
                logging.debug("[STT] terminate failed, trying kill: %s", terminate_exc)
                try:
                    proc.kill()
                    proc.wait(timeout=3)
                except Exception as kill_exc:
                    logging.debug("[STT] kill failed: %s", kill_exc)

    def _read_stderr_snapshot(self, proc=None) -> str:
        try:
            proc = proc or self._proc
            if proc is None or proc.stderr is None:
                return ""
            if proc.poll() is None:
                return ""
            return proc.stderr.read().decode("utf-8", errors="replace").strip()
        except Exception:
            return ""

    def _read_process_line(self, stream, timeout_seconds: float) -> Optional[str]:
        if stream is None:
            return None
        result_queue: "queue.Queue[Optional[bytes]]" = queue.Queue(maxsize=1)

        def _reader() -> None:
            try:
                result_queue.put(stream.readline())
            except Exception:
                result_queue.put(None)

        threading.Thread(target=_reader, daemon=True).start()
        try:
            raw = result_queue.get(timeout=max(float(timeout_seconds or 0.0), 0.1))
        except queue.Empty:
            return None
        if raw is None:
            return None
        return raw.decode("utf-8", errors="replace").strip()


def _resolve_device(device: str) -> str:
    if device != "auto":
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def _wav_bytes_to_numpy(wav_bytes: bytes):
    """WAV to numpy array conversion for testing."""
    import numpy as np

    with wave.open(io.BytesIO(wav_bytes), "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
        sample_width = wav_file.getsampwidth()
        channels = wav_file.getnchannels()
        sample_rate = wav_file.getframerate()

        if sample_width == 1:
            audio = (np.frombuffer(frames, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
        elif sample_width == 2:
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
        elif sample_width == 4:
            audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32) / 2147483648.0
        else:
            raise ValueError(f"Unsupported audio sample width: {sample_width} bytes")

        if channels > 1:
            audio = audio.reshape(-1, channels).mean(axis=1)
        if sample_rate != 16000 and audio.size:
            from math import gcd
            from scipy.signal import resample_poly

            divisor = gcd(sample_rate, 16000)
            audio = resample_poly(audio, 16000 // divisor, sample_rate // divisor).astype(np.float32)
        return audio


def create_stt_provider(settings: dict) -> STTProvider:
    provider_name = settings.get("stt_provider", "google")
    speech_lang = settings.get("speech_language") or "en-US"
    if provider_name == "whisper":
        return WhisperSTTProvider(
            model_size=settings.get("whisper_model", "small"),
            device=settings.get("whisper_device", "auto"),
            compute_type=settings.get("whisper_compute_type", "int8"),
            language=speech_lang,
        )
    return GoogleSTTProvider(language=speech_lang)
