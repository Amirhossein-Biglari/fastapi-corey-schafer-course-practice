import uuid  # for unique file names
from io import BytesIO  # for working with image bytes in memory
from pathlib import Path  # file operations

from PIL import Image, ImageOps  # main image functionality

PROFILE_PICS_DIR = Path("media/profile_pics")


# If we do cpu-bound work inside async endpoint, then it blocks the event loop and nothing else can be processed.
# then we write this as a regular sync function and then call it using run in threadpool
def process_profile_image(content: bytes) -> str:
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"
        filepath = PROFILE_PICS_DIR / filename

        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

        img.save(filepath, "JPEG", quality=85, optimize=True)

    return filename


def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return

    filepath = PROFILE_PICS_DIR / filename
    if filepath.exists():
        filepath.unlink()
