import subprocess, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from ..config import settings

def _run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"FFmpeg failed: {p.stderr[-2500:]}")

def render_slideshow(images: list[str], narration: str, output: str, aspect: str, captions: str | None = None):
    if not images:
        raise RuntimeError("No generated visual assets were returned.")
    w,h = (1080,1920) if aspect=="portrait" else (1920,1080)
    out = Path(output); out.parent.mkdir(parents=True, exist_ok=True)
    # Create normalized stills; FFmpeg concatenates them with a gentle zoom.
    normalized=[]
    for i, path in enumerate(images):
        target=out.parent/f"frame_{i:03d}.jpg"
        im=Image.open(path).convert("RGB")
        im.thumbnail((w,h))
        canvas=Image.new("RGB",(w,h),(12,16,28))
        canvas.paste(im,((w-im.width)//2,(h-im.height)//2))
        canvas.save(target,quality=90); normalized.append(target)
    # Scene duration is estimated; voice track determines final video duration.
    concat=out.parent/"frames.txt"
    with concat.open("w") as f:
        for p in normalized:
            f.write(f"file '{p.as_posix()}'\n")
            f.write("duration 4\n")
        f.write(f"file '{normalized[-1].as_posix()}'\n")
    args=[settings.ffmpeg_path,"-y","-f","concat","-safe","0","-i",str(concat),"-i",narration,
          "-vf",f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},format=yuv420p",
          "-c:v","libx264","-preset","veryfast","-r","30","-c:a","aac","-b:a","192k",
          "-shortest",str(out)]
    if captions and Path(captions).exists():
        # Caption burn-in can be enabled with a compatible FFmpeg build.
        args[args.index("-c:v")] = "-vf"
        # Keep caption file handling explicit rather than guessing subtitle escaping.
        args.insert(args.index("-c:v")+1, f"subtitles={captions}")
    _run(args)
    return str(out)

def create_thumbnail(image_path: str, title: str, output: str):
    im=Image.open(image_path).convert("RGB").resize((1280,720))
    draw=ImageDraw.Draw(im)
    try: font=ImageFont.truetype("DejaVuSans-Bold.ttf",58)
    except Exception: font=ImageFont.load_default()
    # Add dark translucent panel for readable title.
    overlay=Image.new("RGBA", im.size,(0,0,0,0))
    od=ImageDraw.Draw(overlay); od.rounded_rectangle((45,500,1235,680),radius=28,fill=(0,0,0,180))
    im=Image.alpha_composite(im.convert("RGBA"),overlay)
    ImageDraw.Draw(im).text((75,535),title[:55],font=font,fill="white")
    im.convert("RGB").save(output,quality=92)
    return output
