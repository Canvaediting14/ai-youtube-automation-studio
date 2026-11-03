# Roadmap to production

## Before public launch
- Add authentication and role-based access.
- Use Postgres + Redis/Celery or a durable workflow engine.
- Add encrypted OAuth token storage and token revocation.
- Add upload chunk resume, quota-aware backoff, and idempotency.
- Add job cancellation, progress events, and structured logs.
- Add source retrieval / fact-checking and citation capture.
- Add SRT/VTT generation with word or sentence timestamps.
- Add licensed background music and audio ducking.
- Add AI video clip generation with image fallback.
- Add transitions, motion effects, safe-area captions, and thumbnail review.
- Add moderation, copyright checks, policy checks, and duplicate-topic detection.
- Add integration tests for OAuth, provider adapters, rendering, and uploads.
- Add monitoring, backups, retention controls, and HTTPS reverse proxy.

## Recommended rollout
1. Generate one test short with private output.
2. Generate one long-form test and verify the complete runtime and narration.
3. Check Hindi/Hinglish typography and captions on a real phone.
4. Verify thumbnail, description, language metadata, music licensing, and source notes.
5. Upload as private/unlisted; confirm on YouTube Studio.
6. Only then enable `AUTO_PUBLISH=true`.
