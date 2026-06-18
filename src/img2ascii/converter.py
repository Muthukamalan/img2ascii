"""Image to ASCII art converter."""

from __future__ import annotations

from pathlib import Path
from PIL import Image


class ImageToAscii:
    """Convert images to ASCII art."""

    __slots__ = ("width", "height", "invert", "palette")

    DEFAULT_PALETTE_70 = "@%#*+=-:. "
    DEFAULT_PALETTE_10 = "@%#*+=-:. "

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
