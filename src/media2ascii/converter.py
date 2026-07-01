"""Image to ASCII art converter."""

from __future__ import annotations

import os
import time
from pathlib import Path

import cv2
from PIL import Image
import numpy as np

class ImageToAscii:
    """Convert images to ASCII art."""

    __slots__ = ("width", "height", "invert", "palette")

    def __init__(
        self,
        width: int = 120,
        height: int | None = None,
        palette: str | int = 70,
        invert: bool = False,
    ):
        """Initialize converter.

        Args:
            width: Output width in characters
            height: Output height in characters (auto-calculated if None)
            palette: Character palette ('70', '10', or custom string)
            invert: Invert brightness mapping
        """
        self.width = width
        self.height = height
        self.invert = invert

        if isinstance(palette, int):
            palette = str(palette)

        if palette == "70":
            self.palette = "@%#*+=-:. @%#*+=-:. @%#*+=-:. @%#*+=-:. @%#*+=-:. @%#*+=-:. @%#*+=-:. "
        elif palette == "10":
            self.palette = "@%#*+=-:. "
        else:
            self.palette = palette

    def _load_image(self, source: str | Path | Image.Image) -> Image.Image:
        """Load image from path or return PIL Image."""
        if isinstance(source, Image.Image):
            img = source
        else:
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Image not found: {path}")
            img = Image.open(path)

        if img.mode != "L":
            img = img.convert("L")

        return img

    def _calculate_height(self, img: Image.Image) -> int:
        """Calculate output height maintaining aspect ratio."""
        aspect_ratio = img.height / img.width
        return max(1, int(self.width * aspect_ratio * 0.55))

    def _resize_image(self, img: Image.Image) -> Image.Image:
        """Resize image to match output dimensions."""
        height = self.height or self._calculate_height(img)
        return img.resize((self.width, height), Image.Resampling.LANCZOS)

    def _pixel_to_char(self, pixel_value: int) -> str:
        """Map pixel brightness to ASCII character."""
        palette_len = len(self.palette)
        if self.invert:
            index = pixel_value // (256 // palette_len)
        else:
            index = (255 - pixel_value) // (256 // palette_len)
        return self.palette[min(index, palette_len - 1)]

    def convert(self, source: str | Path | Image.Image) -> str:
        """Convert image to ASCII art.

        Args:
            source: Image path (str/Path) or PIL Image object

        Returns:
            ASCII art as string
        """
        img = self._load_image(source)
        img = self._resize_image(img)

        pixels = list(img.getdata())
        ascii_art = ""

        for y in range(img.height):
            for x in range(img.width):
                pixel = pixels[y * img.width + x]
                ascii_art += self._pixel_to_char(pixel)
            ascii_art += "\n"

        return ascii_art.rstrip()

    def save(self, ascii_art: str, output_path: str | Path) -> None:
        """Save ASCII art to file.

        Args:
            ascii_art: ASCII art string
            output_path: Output file path
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ascii_art, encoding="utf-8")


class VideoToAscii:
    __slots__ = ('width','ascii_chars','invert','video_path','cap','fps')
    def __init__(self, video_path, width=120,ascii_chars="@%#*+=-:. ",invert:bool=False):
        self.video_path = video_path
        self.width = width
        self.ascii_chars = ascii_chars  # Dark -> Light
        self.invert = invert

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 24

    def frame_to_ascii(self, frame):
        """Convert frame to ASCII string."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        h, w = gray.shape
        aspect_ratio = h / w

        # Character cells are taller than wide
        new_height = int(self.width * aspect_ratio * 0.55)

        resized = cv2.resize(gray, (self.width, new_height))

        palette_len = len(self.ascii_chars)

        ascii_frame = []
        for row in resized:              
            line = "".join( self.ascii_chars[ min( (int(pixel) // (256 // palette_len) if self.invert else (255 - int(pixel)) // (256 // palette_len)), palette_len - 1,)] for pixel in row )
            ascii_frame.append(line)

        return "\n".join(ascii_frame)

    def play_ascii(self):
        """Display ASCII video in terminal."""
        frame_delay = 1 / self.fps

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            ascii_art = self.frame_to_ascii(frame)

            os.system("cls" if os.name == "nt" else "clear")
            print(ascii_art)

            time.sleep(frame_delay)

        self.cap.release()

    def save_ascii_frames(self, output_dir="ascii_frames"):
        """Save each frame as text file."""
        os.makedirs(output_dir, exist_ok=True)

        frame_idx = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            ascii_art = self.frame_to_ascii(frame)

            with open(f"{output_dir}/frame_{frame_idx:05d}.txt", "w") as f:
                f.write(ascii_art)

            frame_idx += 1

        self.cap.release()
        print(f"Saved {frame_idx} frames to {output_dir}")

    def save_ascii_video(self, output_path="ascii_video.mp4"):
        """Save ASCII-rendered video as mp4."""
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Cannot read video")

        # Generate one frame to determine output size
        ascii_art = self.frame_to_ascii(frame)
        preview = self.ascii_to_image(ascii_art)
        h, w = preview.shape[:2]

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, self.fps, (w, h))

        # rewind to frame 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        frame_count = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            ascii_art = self.frame_to_ascii(frame)
            ascii_img = self.ascii_to_image(ascii_art)

            # Ensure dimensions stay constant
            ascii_img = cv2.resize(ascii_img, (w, h))

            writer.write(ascii_img)
            frame_count += 1

        writer.release()
        self.cap.release()
        print(f"Saved ASCII video: {output_path} ({frame_count} frames)")

    def ascii_to_image(self, ascii_art, font=cv2.FONT_HERSHEY_PLAIN,
                    font_scale=0.8, thickness=1):
        """Convert ASCII text into an image frame."""
        lines = ascii_art.split("\n")

        char_w = 8
        char_h = 12

        img_h = len(lines) * char_h + 10
        img_w = max(len(line) for line in lines) * char_w + 10

        canvas = np.zeros((img_h, img_w, 3), dtype=np.uint8)

        y = char_h
        for line in lines:
            cv2.putText(
                canvas,
                line,
                (5, y),
                font,
                font_scale,
                (255, 255, 255),  # white text
                thickness,
                cv2.LINE_AA
            )
            y += char_h

        return canvas