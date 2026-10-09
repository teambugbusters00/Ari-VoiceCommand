"""Project constants definition"""

from i18n.translator import _

# Speech recognition settings
SPEECH_LANGUAGE = "en-US"
SPEECH_TIMEOUT = 5  # seconds
SPEECH_PHRASE_LIMIT = 15  # seconds
SPEECH_REPEAT_SUPPRESSION_SECONDS = 2.0
SPEECH_REPEAT_NOTICE_DURATION_MS = 2000
AMBIENT_NOISE_DURATION = 0.5  # seconds

# Wake words (English + Hindi)
WAKE_WORDS = ["Hey Ari", "Ari", "सुनो"]


def get_wake_responses() -> list[str]:
    """Return wake word response list for the current language."""
    try:
        from i18n.translator import get_language
        if get_language() == "hi":
            return ["जी?", "सुन रही हूँ", "बताइए?"]
    except Exception:
        pass
    return ["Yes?", "How can I help?"]

# Character physics settings
GRAVITY = 0.8
BOUNCE_Y = -0.2
BOUNCE_X = -0.3
FRICTION_GROUND = 0.85
FRICTION_AIR = 0.99

# Timer
GREETING_INTERVAL = 1800000  # 30 minutes (milliseconds)

# TTS settings
DEFAULT_TTS_SPEED = 1.0
DEFAULT_TTS_VOLUME = 1.0
TTS_WAKE_GUARD_BUFFER_SECONDS = 0.5
TTS_CHARS_PER_SECOND_DEFAULT = 20.0
TTS_CHARS_PER_SECOND_BY_LANGUAGE = {
    "en": 20.0,
    "hi": 12.0,
}

# File paths
SETTINGS_FILE = "ari_settings.json"
CONFIG_FILE = "config.json"
LOG_DIR = "logs"
CACHE_DIR = "tts_cache"

# Cache settings
IMAGE_CACHE_CAPACITY = 20
