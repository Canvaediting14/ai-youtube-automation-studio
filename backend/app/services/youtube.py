from pathlib import Path
from ..config import settings

SCOPES=["https://www.googleapis.com/auth/youtube.upload","https://www.googleapis.com/auth/youtube.readonly"]

def oauth_flow():
    if not settings.google_client_id or not settings.google_client_secret:
        raise RuntimeError("Google OAuth client ID and secret are not configured.")
    from google_auth_oauthlib.flow import Flow
    flow=Flow.from_client_config({"web":{"client_id":settings.google_client_id,"client_secret":settings.google_client_secret,
      "auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token",
      "redirect_uris":[settings.google_redirect_uri]}},scopes=SCOPES)
    flow.redirect_uri=settings.google_redirect_uri
    return flow

def save_credentials(credentials):
    path=Path(settings.google_token_file); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(credentials.to_json())
    try: path.chmod(0o600)
    except Exception: pass

def get_youtube():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    path=Path(settings.google_token_file)
    if not path.exists(): raise RuntimeError("YouTube is not connected. Connect your Google account in Settings.")
    creds=Credentials.from_authorized_user_file(str(path),SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request()); save_credentials(creds)
    return build("youtube","v3",credentials=creds)

def upload_video(video_path: str, title: str, description: str, privacy: str, thumbnail: str | None = None):
    from googleapiclient.http import MediaFileUpload
    yt=get_youtube()
    body={"snippet":{"title":title[:100],"description":description[:5000],"categoryId":"22","defaultLanguage":"en"},
          "status":{"privacyStatus":privacy,"selfDeclaredMadeForKids":False}}
    result=yt.videos().insert(part="snippet,status",body=body,
        media_body=MediaFileUpload(video_path,chunksize=-1,resumable=True)).execute()
    video_id=result["id"]
    if thumbnail and Path(thumbnail).exists():
        yt.thumbnails().set(videoId=video_id,media_body=MediaFileUpload(thumbnail)).execute()
    return video_id
