"""Provider boundaries. Missing credentials fail explicitly; no fake media is generated."""
from pathlib import Path
from ..config import settings

def generate_script(topic: str, language: str, duration_minutes: float, scenes: int) -> dict:
    if settings.script_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is missing. Configure a script provider before generation.")
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        prompt = f"Write an engaging YouTube narration in {language} about: {topic}. Target {duration_minutes} minutes. Return JSON with title, description, narration, and scenes array of {scenes} objects containing narration_segment and visual_prompt. Avoid unsupported claims; include source notes in description."
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role":"system","content":"You are a careful YouTube scriptwriter. Return valid JSON only."},{"role":"user","content":prompt}],
            temperature=0.7
        )
        import json
        return json.loads(response.choices[0].message.content)
    raise RuntimeError(f"Unsupported SCRIPT_PROVIDER: {settings.script_provider}. Add a provider adapter in services/providers.py.")

def generate_voice(text: str, output_file: str, language: str) -> str:
    if settings.tts_provider == "elevenlabs":
        if not settings.elevenlabs_api_key:
            raise RuntimeError("ELEVENLABS_API_KEY is missing. Configure a natural TTS provider.")
        import requests
        # Use a multilingual voice ID configured by the operator.
        voice_id = __import__("os").getenv("ELEVENLABS_VOICE_ID", "")
        if not voice_id:
            raise RuntimeError("Set ELEVENLABS_VOICE_ID to a voice suitable for your language.")
        r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": settings.elevenlabs_api_key, "Content-Type":"application/json"},
            json={"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.45,"similarity_boost":0.8}},
            timeout=180)
        r.raise_for_status()
        Path(output_file).write_bytes(r.content)
        return output_file
    raise RuntimeError(f"Unsupported TTS_PROVIDER: {settings.tts_provider}. Add a provider adapter.")

def generate_visual(prompt: str, output_file: str, aspect: str) -> str:
    if settings.visual_provider == "fal":
        if not settings.fal_key:
            raise RuntimeError("FAL_KEY is missing. Configure a visual provider.")
        # fal model endpoints differ; this adapter intentionally requires an explicit model endpoint.
        import os, requests
        endpoint = os.getenv("FAL_IMAGE_ENDPOINT", "")
        if not endpoint:
            raise RuntimeError("Set FAL_IMAGE_ENDPOINT to the fal model endpoint enabled for your account.")
        r = requests.post(endpoint, headers={"Authorization": f"Key {settings.fal_key}", "Content-Type":"application/json"},
                          json={"prompt":prompt, "image_size":"landscape_16_9" if aspect=="landscape" else "portrait_9_16"},
                          timeout=240)
        r.raise_for_status()
        data = r.json()
        url = data.get("images", [{}])[0].get("url")
        if not url:
            raise RuntimeError("Visual provider response did not contain images[0].url.")
        img = requests.get(url, timeout=120); img.raise_for_status()
        Path(output_file).write_bytes(img.content)
        return output_file
    raise RuntimeError(f"Unsupported VISUAL_PROVIDER: {settings.visual_provider}. Add a provider adapter.")
