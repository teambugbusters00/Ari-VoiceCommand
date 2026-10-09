---
title: Ari VoiceCommand Backend
emoji: 🎙️
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Ari VoiceCommand Cloud Backend

Cloud proxy backend for the Ari Windows Voice Assistant desktop application.

## Endpoints
- `GET /health` - Health check status
- `GET /v1/models` - Available models list
- `POST /v1/chat/completions` - OpenAI-compatible Chat Completions endpoint (streaming + non-streaming)

## Environment Variables
Set these secrets in Hugging Face Space Settings or hosting provider:
- `GROQ_API_KEY`: Groq Cloud API key (recommended for high-speed free inference)
- `GEMINI_API_KEY`: Google Gemini API key (optional fallback)
- `OPENAI_API_KEY`: OpenAI API key (optional fallback)
- `DEFAULT_MODEL`: Default model (default: `llama-3.3-70b-versatile`)
