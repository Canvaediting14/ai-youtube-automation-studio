# AI YouTube Automation Studio

A self-hostable starter platform for planning, generating, rendering, and publishing YouTube long-form videos and Shorts.

## Included
- FastAPI backend with SQLite persistence and a React/Vite dashboard.
- Daily schedule defaults: **2 long videos (6–7 min)** and **3 Shorts (1–2 min)**.
- English/Hindi/Hinglish language rotation.
- Provider adapters for script generation, TTS, image/video assets, and background music.
- FFmpeg render pipeline for landscape and vertical videos, captions, audio mix, and thumbnails.
- YouTube OAuth connection and upload integration.
- Job status, retryable jobs, logs, and configurable publishing mode.

> This is a production-oriented foundation, not a one-click hosted service. You must configure provider credentials, deploy it on a server with FFmpeg, connect your Google account, and test uploads before enabling unattended publishing. Provider APIs, quotas, costs, and terms can change.

## Architecture
- `backend/`: FastAPI, SQLAlchemy, scheduler, generation pipeline, YouTube integration.
- `frontend/`: React dashboard.
- `infra/`: Docker Compose.
- `scripts/`: local setup helpers.

## Quick start (Docker)
1. Install Docker Desktop.
2. Copy `.env.example` to `.env` and fill in the required values.
3. Add your Google OAuth client ID/secret and configure the callback URL:
   `http://localhost:8000/api/youtube/callback`
4. Run:
   ```bash
   docker compose up --build
   ```
5. Open `http://localhost:5173`.

For local development without Docker:
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
In another terminal:
```bash
cd frontend
npm install
npm run dev
```

## Important configuration
See `.env.example`. At minimum:
- `SECRET_KEY`: long random secret.
- `DATABASE_URL`: persistent database URL.
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`.
- At least one supported AI provider key for generation. Provider adapters deliberately fail clearly when a key is missing; they do not fabricate completed output.
- `FFMPEG_PATH`: path to FFmpeg executable.

### Google OAuth setup
In Google Cloud Console:
1. Enable **YouTube Data API v3**.
2. Configure OAuth consent screen and add your Google account as a test user while in testing.
3. Create a Web application OAuth client.
4. Add the exact redirect URI from `GOOGLE_REDIRECT_URI`.
5. Set the values in `.env`, restart, then connect YouTube from Settings.

YouTube may require OAuth verification for broad public use. Upload quota and channel restrictions apply. Never commit `.env`, client secrets, refresh tokens, or service credentials.

## Default publishing plan
The scheduler creates 5 generation jobs per day:
- 2 landscape videos, 6–7 minutes, 40–45 visual scenes.
- 3 vertical Shorts, 60–120 seconds, 15–20 visual scenes.
- Languages rotate English → Hindi → Hinglish by date and slot.
- Publishing is disabled until `AUTO_PUBLISH=true` and YouTube OAuth is connected.

**Recommendation:** begin with `AUTO_PUBLISH=false`; inspect generated videos and run private/unlisted test uploads. Enable unattended publishing only after validating copyright, factual accuracy, channel policy, audio/image licensing, and render quality.

## API
- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/settings`
- `PUT /api/settings`
- `GET /api/jobs`
- `POST /api/jobs`
- `POST /api/jobs/{id}/retry`
- `GET /api/youtube/connect`
- `GET /api/youtube/status`

Interactive API docs: `http://localhost:8000/docs`.

## Security & operations
- Store secrets only in environment variables / secret manager.
- Use HTTPS in production and set `FRONTEND_ORIGIN`.
- Persist `/data` and `/media` volumes.
- Back up the database and media.
- Add a reverse proxy, authentication, rate limiting, monitoring, and a managed database before exposing the service publicly.
- The starter dashboard is intended for a trusted single-operator deployment; add user authentication before public multi-user hosting.

## License
MIT. See `LICENSE`.
