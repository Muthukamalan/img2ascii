from pathlib import Path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif"}
VIDEO_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def detect_media_type(path: str) -> str:
    ext = Path(path).suffix.lower()

    if ext in IMAGE_EXTS:
        return "image"
    elif ext in VIDEO_EXTS:
        return "video"
    else:
        raise ValueError(f"Unsupported file type: {ext}")