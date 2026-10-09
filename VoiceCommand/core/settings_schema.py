"""Settings schema and template metadata."""

from __future__ import annotations

SETTINGS_FILE = "ari_settings.json"
SETTINGS_TEMPLATE_FILE = "ari_settings.template.json"

SENSITIVE_SETTINGS_KEYS = (
    "groq_api_key",
    "openai_api_key",
    "anthropic_api_key",
    "mistral_api_key",
    "gemini_api_key",
    "openrouter_api_key",
    "nvidia_nim_api_key",
    "google_client_secret",
    "fish_api_key",
    "fish_reference_id",
    "telegram_bot_token",
    "openai_tts_api_key",
    "elevenlabs_api_key",
    "openai_compat_tts_api_key",
)

_UNSET_CREDENTIAL = ""

DEFAULT_SETTINGS = {
    # ── LLM Provider ───────────────────────────────────────────────────
    "llm_provider": "ari_cloud",
    "llm_model": "",
    "llm_planner_provider": "",   # Empty means same as default provider
    "llm_planner_model": "",
    "llm_execution_provider": "",  # Empty means same as default provider
    "llm_execution_model": "",
    "llm_memory_extractor_provider": "",
    "llm_memory_extractor_model": "",
    "fact_extraction_suggestions_enabled": True,
    "groq_api_key": _UNSET_CREDENTIAL,
    "openai_api_key": _UNSET_CREDENTIAL,
    "anthropic_api_key": _UNSET_CREDENTIAL,
    "mistral_api_key": _UNSET_CREDENTIAL,
    "gemini_api_key": _UNSET_CREDENTIAL,
    "openrouter_api_key": _UNSET_CREDENTIAL,
    "nvidia_nim_api_key": _UNSET_CREDENTIAL,
    "ollama_base_url": "http://localhost:11434/v1",
    "ari_cloud_base_url": "https://teambugbusters00-ari-backend.hf.space/v1",
    "llm_timeout_chat_seconds": 30,
    "llm_timeout_planner_seconds": 90,
    "llm_timeout_local_seconds": 120,
    "llm_streaming_enabled": True,
    "llm_prewarm_enabled": True,
    "instant_ack_enabled": True,
    "tool_followup_policy_enabled": True,
    "local_decision_engine_enabled": True,
    "local_decision_backend": "linear",
    "local_decision_threshold": 0.92,
    "local_decision_mode": "fast",
    "local_decision_direct_execution": True,
    "local_decision_settings_version": 3,
    "vision_enabled": True,
    "embedding_remote_enabled": False,
    "max_context_tokens": 8000,
    # ── TTS Provider ───────────────────────────────────────────────────
    "tts_mode": "fish",            # fish | local | openai_compat_tts | openai_tts | elevenlabs | edge
    "fish_api_key": _UNSET_CREDENTIAL,
    "fish_reference_id": _UNSET_CREDENTIAL,
    "fish_model": "s2.1-pro-free",  # Fish Audio backend model
    "cosyvoice_reference_text": "",
    "tts_reference_wav": "",
    "cosyvoice_speed": 0.9,
    "cosyvoice_dir": "",           # CosyVoice installation path (auto-detect if empty)
    "openai_compat_tts_base_url": "",
    "openai_compat_tts_api_key": _UNSET_CREDENTIAL,
    "openai_compat_tts_model": "",
    "openai_compat_tts_voice": "",
    "openai_compat_tts_clone_mode": "none",
    "openai_compat_tts_emotion_mode": "instructions",
    "openai_tts_api_key": _UNSET_CREDENTIAL,
    "openai_tts_voice": "nova",    # alloy | echo | fable | onyx | nova | shimmer
    "openai_tts_model": "tts-1",   # tts-1 | tts-1-hd | gpt-4o-mini-tts
    "openai_tts_custom_voice_id": "",
    "elevenlabs_api_key": _UNSET_CREDENTIAL,
    "elevenlabs_voice_id": "",
    "elevenlabs_model_id": "eleven_multilingual_v2",
    "edge_tts_voice": "en-US-JennyNeural",
    "edge_tts_rate": "+0%",
    "tts_emotion_enabled": True,
    "tts_sentence_timeout_seconds": 10,
    "tts_cache_max_bytes": 50 * 1024 * 1024,
    # ── Character / Personality ─────────────────────────────────────────
    "personality": "Identity: Ari, a competent and attentive desktop voice assistant maid.",
    "personality_examples_en": "",
    "personality_examples_hi": "",
    "fixed_responses": {},
    "scenario": "Desktop companion voice assistant for Windows.",
    "system_prompt": "You are Ari, an intelligent and helpful desktop voice assistant. Respond in English or Hindi based on user preference.",
    "history_instruction": "Quietly incorporate past preferences to provide helpful suggestions.",
    "response_verbosity": "concise",  # concise | normal | chatty
    # ── Device & Audio ──────────────────────────────────────────────────
    "microphone": "",
    "audio_output_device": "",
    "speech_language": "en-US",      # Speech recognition language: en-US, en-IN, hi-IN
    "stt_provider": "google",
    "whisper_model": "small",
    "whisper_device": "auto",
    "whisper_compute_type": "int8",
    "wake_words": ["Hey Ari", "Ari", "सुनो"],
    "wake_word_enabled": True,
    "voice_activation_hotkey": "Ctrl+Alt+Space",
    "voice_activation_mode": "push_to_talk",
    "stt_energy_threshold": 300,
    "stt_dynamic_energy": False,
    "stt_settings_version": 2,
    "stt_pause_threshold": 0.6,
    "wake_pause_threshold": 0.4,
    "post_tts_listen_delay_ms": 100,
    "tts_speed": 1.0,
    "tts_volume": 1.0,
    "tts_fallback_provider": "edge",
    "character_scale": 1.0,          # Character scale (0.3 ~ 3.0)
    "character_ground_offset": 4,    # Ground alignment offset (px)
    "ui_theme_preset": "default",
    "ui_theme_scale": 1.0,
    "ui_font_family": "",
    "language": "en",               # Interface language (en | hi)
    "update_check_enabled": True,
    "update_channel": "stable",
    # ── Character Widget Extensions ─────────────────────────────────────
    "affinity_points": 0,
    "affinity_level": 0,
    "affinity_total_clicks": 0,
    "affinity_total_pets": 0,
    "affinity_total_chats": 0,
    "affinity_last_login": "",      # YYYY-MM-DD
    "focus_app_reaction_enabled": True,
    "system_monitor_enabled": True,
    "activity_idle_reaction_enabled": True,
    "activity_session_lock_reaction_enabled": True,
    "activity_quiet_reaction_enabled": True,
    "activity_app_category_reaction_enabled": False,
    "activity_away_threshold_minutes": 5,
    "activity_quiet_bubble_only_enabled": False,
    "activity_auto_game_mode_enabled": False,
    "activity_ide_long_use_reaction_enabled": True,
    "user_birthday": "",            # MM-DD
    "special_date_events_enabled": True,
    # ── AI Extensions ───────────────────────────────────────────────────
    "llm_router_enabled": True,          # LLMRouter auto-routing by task
    "agent_response_cache_ttl": 600,     # LLM response cache TTL (seconds)
    "agent_response_cache_max_size": 50, # LLM cache max entries
    "few_shot_max_examples": 3,          # FewShotInjector max examples
    "skill_library_enabled": True,       # Auto extract skill patterns
    "reflection_engine_enabled": True,   # Auto reflection on failure
    "memory_consolidation_days": 14,     # Memory consolidation threshold (days)
    "weekly_report_enabled": True,       # Weekly self-improvement report
    "agent_timeout_seconds": 120,
    "plugin_hot_reload_enabled": False,
    "audit_log_enabled": True,
    "mcp_server_enabled": False,
    "mcp_server_port": 8765,
    "telegram_enabled": False,
    "telegram_bot_token": _UNSET_CREDENTIAL,
    "telegram_allowed_chat_ids": [],
    "telegram_poll_timeout_seconds": 25,
    "agent_dashboard_enabled": True,
    "tts_wake_guard_seconds": 1.2,
    "max_subagents": 3,
    "google_calendar_enabled": False,
    "google_client_id": "",
    "google_client_secret": _UNSET_CREDENTIAL,
    "image_generation_enabled": False,
    "image_gen_provider": "openai",
}

LOCAL_DECISION_SETTINGS_VERSION = 3
STT_SETTINGS_VERSION = 2
LOCAL_DECISION_MODES = ("off", "shadow", "fast")


def normalize_local_decision_settings(settings: dict) -> bool:
    """Normalize local decision engine settings. Returns True if modified."""
    changed = False
    mode = settings.get("local_decision_mode")
    direct = settings.get("local_decision_direct_execution") is True
    if mode == "adaptive":
        mode = "fast" if direct else "off"
    elif mode is not None and mode not in LOCAL_DECISION_MODES:
        mode = "off"
    if mode is not None and mode != settings.get("local_decision_mode"):
        settings["local_decision_mode"] = mode
        changed = True
    if mode in ("off", "shadow") and settings.get("local_decision_direct_execution") is True:
        settings["local_decision_direct_execution"] = False
        changed = True
    return changed


def migrate_local_decision_settings(settings: dict) -> bool:
    """Migrate local decision settings across versions. Returns True if modified."""
    changed = False
    try:
        version = int(settings.get("local_decision_settings_version") or 0)
    except (TypeError, ValueError):
        version = 0

    if version < 2:
        settings["local_decision_settings_version"] = 2
        version = 2
        changed = True
    if version < LOCAL_DECISION_SETTINGS_VERSION:
        if settings.get("local_decision_mode") == "off":
            settings["local_decision_mode"] = "fast"
            settings["local_decision_direct_execution"] = True
        settings["local_decision_settings_version"] = LOCAL_DECISION_SETTINGS_VERSION
        changed = True
    return normalize_local_decision_settings(settings) or changed


def migrate_stt_settings(settings: dict) -> bool:
    """Validate and preserve STT threshold settings."""
    changed = False
    if "stt_energy_threshold" in settings:
        try:
            threshold = float(settings["stt_energy_threshold"])
        except (TypeError, ValueError, OverflowError):
            threshold = 0.0
        if not 1 <= threshold < float("inf"):
            settings["stt_energy_threshold"] = DEFAULT_SETTINGS["stt_energy_threshold"]
            changed = True
    version = settings.get("stt_settings_version")
    if version == STT_SETTINGS_VERSION:
        return changed
    if version != 1 and settings.get("stt_dynamic_energy") is True:
        settings["stt_dynamic_energy"] = False
    settings["stt_settings_version"] = STT_SETTINGS_VERSION
    return True
