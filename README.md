# Andrew's Vectorizer

Turn raster images into clean SVG vector graphics.

No virtualenvs. No pip install. No Docker. No ritual sacrifice to dependency management.

Just:

```bash
uv run vectorizer.py image.png
```

<p align="center">
<img width="802"  alt="comparison" src="https://github.com/user-attachments/assets/09295f46-a57c-4410-960b-5433e9a20e3d" />  
</p>



Convert logos, illustrations, mascots, sprites, UI assets, sketches, and photos into scalable SVGs using multiple preprocessing pipelines and VTracer's spline-based vectorization.

---

## Features

- One-file tool
- Zero setup beyond `uv`
- Five vectorization modes
- Smooth spline output (not blocky polygon traces)
- Automatic dependency management
- Compare all modes with a single command
- SVG output suitable for web, print, design tools, and further editing

---

## Example

Using Blorbo, because every respectable software project eventually develops a mascot.

| Input PNG | Output SVG |
|------------|------------|
| ![](examples/blorbo_wow.png) | ![](examples/blorbo_wow.svg) |

---

## Quick Start

Install uv:

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Run the vectorizer:

```bash
uv run vectorizer.py image.png
```

Output:

```text
image_color.svg
```

---

## Modes

Different images benefit from different preprocessing pipelines.

| Mode | Best For | Command |
|--------|--------|--------|
| color | Photos, illustrations, mascots | `uv run vectorizer.py image.png` |
| bw | Logos, sketches, line art | `uv run vectorizer.py image.png -m bw` |
| edge | Strong contours and silhouettes | `uv run vectorizer.py image.png -m edge` |
| posterize | Icons, UI assets, flat design | `uv run vectorizer.py image.png -m posterize` |
| detail | Texture-rich images | `uv run vectorizer.py image.png -m detail` |

Not sure?

Run all modes:

```bash
uv run vectorizer.py image.png --all
```

Outputs:

```text
image_color.svg
image_bw.svg
image_edge.svg
image_posterize.svg
image_detail.svg
```

---

## Usage

```text
usage: vectorizer.py [-h] [-o OUTPUT] [-m {color,bw,edge,posterize,detail}]
                     [--all] [--colors COLORS]
                     [--filter-speckle N] [--color-precision N]
                     [--corner-threshold N] [--path-precision N]
                     input
```

### Arguments

| Argument | Description |
|-----------|------------|
| input | Input image (PNG, JPG, WebP) |
| -o OUTPUT | Output SVG path |
| -m MODE | Vectorization mode |
| --all | Generate all modes |
| --colors N | Posterize color count |
| --filter-speckle N | Remove tiny traced regions |
| --color-precision N | Color quantization depth |
| --corner-threshold N | Corner sensitivity |
| --path-precision N | SVG decimal precision |

---

## Examples

### Default color trace

```bash
uv run vectorizer.py logo.png
```

### Black-and-white logo

```bash
uv run vectorizer.py logo.png -m bw
```

### Posterized illustration

```bash
uv run vectorizer.py illustration.png -m posterize --colors 12
```

### Clean up noisy scans

```bash
uv run vectorizer.py scan.png -m edge --filter-speckle 12
```

### High precision output

```bash
uv run vectorizer.py artwork.png --path-precision 6
```

---

## How It Works

Each mode applies a different OpenCV preprocessing pipeline before tracing.

### color

Passes the image directly to the tracer with perceptual color clustering.

Best for:

- General artwork
- Mascots
- Illustrations
- Photos

### bw

Converts the image into a binary silhouette before tracing.

Best for:

- Logos
- Sketches
- Ink drawings
- Line art

### edge

Pipeline:

```text
Bilateral Filter
    ↓
CLAHE Contrast Enhancement
    ↓
Canny Edge Detection
    ↓
Edge Composite
    ↓
Trace
```

Best for:

- Architecture
- Product photos
- Strong contours

### posterize

Pipeline:

```text
K-Means Clustering (Lab)
    ↓
Median Blur
    ↓
Trace
```

Best for:

- Icons
- UI assets
- Flat illustrations
- Stickers

### detail

Pipeline:

```text
Unsharp Mask
    ↓
Light Bilateral Denoise
    ↓
Trace
```

Best for:

- Textures
- Detailed artwork
- High-frequency imagery

---

## Tuning

### Too noisy?

Increase:

```bash
--filter-speckle
```

Example:

```bash
--filter-speckle 12
```

### Too simplified?

Lower:

```bash
--corner-threshold
```

and/or

```bash
--filter-speckle
```

### Flat illustrations

Usually best results:

```bash
-m posterize --colors 6
```

to

```bash
-m posterize --colors 12
```

---

## Dependencies

Nothing needs to be installed manually beyond uv.

Dependencies are declared directly in the script and automatically resolved into uv's cache.

Your system Python remains untouched.

A rare and beautiful event.

---

## Credits

Vector tracing is powered by VTracer:

https://github.com/visioncortex/vtracer

Example artwork uses Blorbo, an open-source penguin mascot from the Blorbo Scrapbook brand kit:

https://github.com/iambecomeblorbo/scrapbook

---

## License

MIT

Use it, modify it, fork it, improve it, accidentally create a vectorized penguin empire with it.

The license permits all of those things.
