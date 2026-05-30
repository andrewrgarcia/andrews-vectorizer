import re
import time

from .modes import MODES
from .utils import load_image

def run(input_path, output_path, mode, **kwargs):
    img = load_image(input_path)
    w, h = img.size
    t0 = time.time()
    svg = MODES[mode]["fn"](img, dict(kwargs))
    elapsed = time.time() - t0
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    paths = len(re.findall(r"<path", svg))
    kb = round(len(svg.encode()) / 1024, 1)
    print(f"  {mode:12s} → {output_path}  [{elapsed:.2f}s | {paths} paths | {kb} KB]")
    return svg
