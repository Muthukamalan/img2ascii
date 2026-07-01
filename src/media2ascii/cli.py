"""CLI for media2ascii"""

from __future__ import annotations

import typer
from loguru import logger
from rich.console import Console

from media2ascii.converter import ImageToAscii,VideoToAscii
from media2ascii.utils import detect_media_type



app = typer.Typer(
    name="Media2Ascii",
    help="Convert images to ASCII art",
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)
console = Console()


@app.command()
def main(
    sourcepath: str = typer.Option(..., "-i", "--sourcepath", help="Path to input image (required)"),
    output_path: str | None = typer.Option(
        None, "-o", "--output_path", help="Path to save ASCII output (optional)"
    ),
    size: int = typer.Option(60, "--size", "-s", help="Output width in characters"),
    invert: bool = typer.Option(False, "-inv", "--invert", help="Invert brightness"),
    palette: str = typer.Option("70", "-p", "--palette", help="Palette: '70' or '10'"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Enable debug logging"),
) -> None:
    """Convert an image to ASCII art and display or save it."""
    if verbose:
        logger.enable("media2ascii")
    else:
        logger.disable("media2ascii")


        logger.debug(f"Loading image from: {sourcepath}")

        src = detect_media_type(sourcepath)
        match src:
            case "image":
                try:
                    converter = ImageToAscii(width=size, palette=palette, invert=invert)
                    ascii_art = converter.convert(sourcepath)

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
            case "video":
                try:
                    converter = VideoToAscii(sourcepath,invert=invert)

                    if output_path:
                        converter.save_ascii_video(output_path)
                    else:
                        converter.play_ascii()
                except FileNotFoundError as e:
                    console.print(f"[red]Error: {e}[/red]")
                    raise typer.Exit(code=1)
                except Exception as e:
                    console.print(f"[red]Unexpected error: {e}[/red]")
                    raise typer.Exit(code=1)
                

if __name__ == "__main__":
    app()
