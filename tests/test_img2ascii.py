"""unittest tests for img2ascii."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from img2ascii import ImageToAscii
from img2ascii.cli import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_image(width: int = 64, height: int = 32, color: int = 128) -> Image.Image:
    """Create a simple grayscale test image in memory."""
    return Image.new("L", (width, height), color=color)


def _save_image(tmp_path: Path, name: str = "test.png", **kwargs) -> Path:
    img = _make_image(**kwargs)
    p = tmp_path / name
    img.save(p)
    return p


# ---------------------------------------------------------------------------
# Unit tests – ImageToAscii
# ---------------------------------------------------------------------------


class TestImageToAscii(unittest.TestCase):
    def test_convert_pil_image(self):
        converter = ImageToAscii(width=40)
        img = _make_image(width=64, height=32, color=200)
        result = converter.convert(img)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_output_width(self):
        width = 50
        converter = ImageToAscii(width=width)
        img = _make_image(width=100, height=50)
        result = converter.convert(img)
        for row in result.splitlines():
            self.assertEqual(len(row), width)

    def test_convert_from_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            converter = ImageToAscii(width=30)
            result = converter.convert(p)
            self.assertIn("\n", result)

    def test_convert_from_string_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            converter = ImageToAscii(width=30)
            result = converter.convert(str(p))
            self.assertIsInstance(result, str)

    def test_missing_file_raises(self):
        converter = ImageToAscii()
        with self.assertRaises(FileNotFoundError):
            converter.convert("/nonexistent/image.png")

    def test_invert_differs(self):
        img = _make_image(width=64, height=32, color=100)
        normal = ImageToAscii(width=40).convert(img)
        inverted = ImageToAscii(width=40, invert=True).convert(img)
        self.assertNotEqual(normal, inverted)

    def test_custom_height(self):
        img = _make_image(width=100, height=100)
        converter = ImageToAscii(width=50, height=20)
        result = converter.convert(img)
        self.assertEqual(len(result.splitlines()), 20)

    def test_palette_10(self):
        palette = "@%#*+=-:. "
        converter = ImageToAscii(width=40, palette=palette)
        img = _make_image(width=64, height=32, color=50)
        result = converter.convert(img)

        for ch in result:
            self.assertTrue(ch in palette or ch == "\n")

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            img = _make_image(width=40, height=20)
            converter = ImageToAscii(width=30)
            art = converter.convert(img)
            out = tmp_path / "output.txt"

            converter.save(art, out)

            self.assertTrue(out.exists())
            self.assertEqual(out.read_text(encoding="utf-8"), art)

    def test_save_creates_parent_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            img = _make_image()
            converter = ImageToAscii(width=20)
            art = converter.convert(img)
            nested = tmp_path / "a" / "b" / "c" / "out.txt"

            converter.save(art, nested)

            self.assertTrue(nested.exists())

    def test_rgb_image_handled(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            img = Image.new("RGB", (64, 32), color=(255, 0, 128))
            p = tmp_path / "rgb.png"
            img.save(p)

            result = ImageToAscii(width=40).convert(p)
            self.assertIsInstance(result, str)

    def test_various_widths(self):
        for width in [10, 50, 120, 200]:
            with self.subTest(width=width):
                img = _make_image(width=256, height=128)
                result = ImageToAscii(width=width).convert(img)
                for row in result.splitlines():
                    self.assertEqual(len(row), width)


# ---------------------------------------------------------------------------
# Integration tests – CLI
# ---------------------------------------------------------------------------


class TestCLI(unittest.TestCase):
    runner = CliRunner()

    def test_help(self):
        result = self.runner.invoke(app, ["--help"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--imagepath", result.output)

    def test_basic_convert(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            result = self.runner.invoke(app, ["--imagepath", str(p), "--size", "40"])
            self.assertEqual(result.exit_code, 0)

    def test_save_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            p = _save_image(tmp_path)
            out = tmp_path / "output.txt"

            result = self.runner.invoke(
                app,
                ["--imagepath", str(p), "--size", "30", "--output_path", str(out)],
            )

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(out.exists())
            self.assertGreater(len(out.read_text()), 0)

    def test_missing_path_exits_nonzero(self):
        result = self.runner.invoke(app, ["--imagepath", "/no/such/image.png"])
        self.assertNotEqual(result.exit_code, 0)

    def test_size_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            result = self.runner.invoke(app, ["--imagepath", str(p), "--size", "60"])
            self.assertEqual(result.exit_code, 0)

    def test_invert_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            result = self.runner.invoke(app, ["--imagepath", str(p), "--invert"])
            self.assertEqual(result.exit_code, 0)

    def test_palette_10(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            result = self.runner.invoke(app, ["--imagepath", str(p), "--palette", "10"])
            self.assertEqual(result.exit_code, 0)

    def test_verbose_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = _save_image(Path(tmp))
            result = self.runner.invoke(app, ["--imagepath", str(p), "--verbose"])
            self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
