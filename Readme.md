# img2ascii 🖼 → 🔤

Convert any image into ASCII art right in your terminal.


## Features

- **Pillow**-powered image loading (JPEG, PNG, BMP, GIF, WEBP, …)
- **70-char** or **10-char** grayscale palette, Pixel brightness is mapped to character density inversely (bright → simple chars, dark → complex chars)
- Configurable output **width** (`--size`)
- Save to file with `--save`
- **Invert** brightness mapping (`-inv`)
- Structured logging via **loguru** (`-v`)
- Rich terminal output via **rich**



## Installation

**Developers**
```bash
# clone & install
git clone <repo-url>
cd Img2Ascii
uv sync --all-groups          # or: task install
```

**Users**
```sh
# on the source code
pip install -e .

pip install img2ascii
```


## Usage

```bash
img2ascii --imagepath photo.jpg
img2ascii --imagepath photo.jpg --size 80
img2ascii --imagepath photo.jpg --size 60 --output_path output.txt
img2ascii --imagepath photo.jpg --invert
img2ascii --imagepath photo.jpg --palette 10
img2ascii --help
```


## Development tasks 
```sh
make help
```

### Quick Start Guide


## Basic Usage

### 1. Display ASCII art in terminal
```bash
img2ascii --imagepath /path/to/image.jpg
```

### 2. Save ASCII art to file
```bash
img2ascii --imagepath /path/to/image.jpg --output_path output.txt
```

### 3. Adjust output width (default 120 chars)
```bash
img2ascii --imagepath photo.jpg --size 80
```

### 4. Use simple palette (10 characters instead of 70)
```bash
img2ascii --imagepath photo.jpg --palette 10
```

### 5. Invert brightness
```bash
img2ascii --imagepath photo.jpg --invert
```

##### Examples

```bash
# Large detailed ASCII art, save to file
img2ascii --imagepath photo.jpg --size 150 --output_path large.txt
```

```python
from img2ascii import ImageToAscii
from pathlib import Path

# Create converter
converter = ImageToAscii(width=80, palette='10', invert=False)

# Convert image to ASCII
ascii_art = converter.convert('photo.jpg')

# Display
print(ascii_art)

# Save to file
converter.save(ascii_art, 'output.txt')
```



###### Developer Note

