import vtracer
import re
import time

from .modes import MODES
from .utils import img_to_bytes, load_image

def vectorize(img, colormode="color", **kw):
    return vtracer.convert_raw_image_to_svg(
        img_to_bytes(img),
        img_format="png",
        colormode=colormode,
        hierarchical="stacked" if colormode == "color" else "cutout",
        mode="spline",
        filter_speckle=kw.get("filter_speckle", 4),
        color_precision=kw.get("color_precision", 6),
        layer_difference=kw.get("layer_difference", 16),
        corner_threshold=kw.get("corner_threshold", 60),
        length_threshold=kw.get("length_threshold", 4.0),
        max_iterations=kw.get("max_iterations", 10),
        splice_threshold=kw.get("splice_threshold", 45),
        path_precision=kw.get("path_precision", 3),
    )



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
