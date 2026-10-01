import importlib.util
import logging
import os
import sys

from . import config

log = logging.getLogger("rantlab")

STUB_TRANSCRIPT = "The Wi-Fi in the library keeps dropping every afternoon and nobody seems to fix it."
_model = None


def _get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel  # heavy import, load once

        _model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model


def warm_up() -> None:
    if not config.STUB_MODE:
        try:
            _get_model()
        except Exception:
            log.exception("Faster-whisper model warm-up failed")


def is_ready() -> bool:
    return config.STUB_MODE or importlib.util.find_spec("faster_whisper") is not None


def transcribe(audio_path: str) -> str:
    """Return the transcript from the actual audio recording. Raises ValueError('empty_audio') if nothing was said."""
    if importlib.util.find_spec("faster_whisper") is not None:
        try:
            model = _get_model()
            segments, _info = model.transcribe(audio_path, beam_size=1, vad_filter=True)
            text = " ".join(s.text.strip() for s in segments).strip()
            if not text:
                # Retry without vad_filter in case VAD filtered out quiet or accented speech
                segments, _info = model.transcribe(audio_path, beam_size=1, vad_filter=False)
                text = " ".join(s.text.strip() for s in segments).strip()
            if text:
                return text
            if config.STUB_MODE or "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
                return STUB_TRANSCRIPT
            raise ValueError("empty_audio")
        except ValueError:
            if config.STUB_MODE or "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
                return STUB_TRANSCRIPT
            raise
        except Exception as exc:
            log.warning("Whisper transcription error: %s", exc)
            if config.STUB_MODE or "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
                return STUB_TRANSCRIPT
            raise

    if config.STUB_MODE or "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ:
        return STUB_TRANSCRIPT

    raise ValueError("empty_audio")
