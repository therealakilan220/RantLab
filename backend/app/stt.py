"""Speech to text with faster-whisper (Member 2).

faster-whisper decodes webm/ogg itself through PyAV, so ffmpeg is usually not needed.
Install ffmpeg only if a browser recording fails to decode.
"""
import importlib.util

from . import config

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
        _get_model()


def is_ready() -> bool:
    return config.STUB_MODE or importlib.util.find_spec("faster_whisper") is not None


def transcribe(audio_path: str) -> str:
    """Return the transcript. Raises ValueError('empty_audio') if nothing was said."""
    if config.STUB_MODE:
        return STUB_TRANSCRIPT
    segments, _info = _get_model().transcribe(audio_path, beam_size=1, vad_filter=True)
    text = " ".join(s.text.strip() for s in segments).strip()
    if not text:
        raise ValueError("empty_audio")
    return text
