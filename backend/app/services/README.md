# Provider adapters

`providers.py` is the integration boundary for external AI services. It currently includes:
- OpenAI JSON script generation.
- ElevenLabs multilingual text-to-speech.
- fal.ai image generation using an explicitly configured model endpoint.

Set `ELEVENLABS_VOICE_ID` and `FAL_IMAGE_ENDPOINT` in the backend environment. Check the selected provider model's accepted request schema and response format; different fal.ai models do not share one universal payload. Extend these adapters when using another provider.

The render pipeline currently creates a still-image slideshow with narration audio. It does not yet implement AI video-clip generation, animated transitions, background music selection, word-level subtitle alignment, or automatic source research. Those are deliberate next integrations rather than simulated features.
