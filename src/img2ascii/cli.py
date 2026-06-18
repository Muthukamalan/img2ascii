"""CLI for img2ascii."""

from __future__ import annotations

from pathlib import Path

import typer
from loguru import logger
from rich.console import Console

from img2ascii.converter import ImageToAscii

app = typer.Typer(
    name="Img2Ascii",
    help="Convert images to ASCII art",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
console = Console()


@app.command()
def main(
    imagepath: str = typer.Option(..., "-i", "--imagepath", help="Path to input image (required)"),
    output_path: str | None = typer.Option(None, "-o", "--output_path", help="Path to save ASCII output (optional)"),
    size: int = typer.Option(60, "--size", "-s", help="Output width in characters"),
    invert: bool = typer.Option(False, "-inv", "--invert", help="Invert brightness"),
    palette: str = typer.Option("70","-p", "--palette", help="Palette: '70' or '10'"),
    verbose: bool = typer.Option(False, "-v", "--verbose",  help="Enable debug logging"),
) -> None:
    """Convert an image to ASCII art and display or save it."""
    if verbose:
        logger.enable("img2ascii")
    else:
        logger.disable("img2ascii")

    try:
        logger.debug(f"Loading image from: {imagepath}")
        converter = ImageToAscii(width=size, palette=palette, invert=invert)
        ascii_art = converter.convert(imagepath)

        if output_path:
            converter.save(ascii_art, output_path)
            logger.debug(f"Saved to: {output_path}")
            console.print(f"\n✓ Saved to [cyan]{output_path}[/cyan]")
        else:
            console.print(ascii_art)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
