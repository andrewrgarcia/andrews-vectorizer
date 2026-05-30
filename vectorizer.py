# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "vtracer",
#   "opencv-python",
#   "scikit-image",
#   "scipy",
#   "svgwrite",
#   "pillow",
# ]
# ///

#!/usr/bin/env python3
"""
PNG → SVG Vectorizer
Usage: uv run vectorizer.py photo.png
       uv run vectorizer.py photo.png -m edge
       uv run vectorizer.py photo.png --all
"""

import sys
import os
import cv2
import numpy as np
from PIL import Image
import vtracer
import io
import re
import time
import argparse

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def load_image(path):
    return Image.open(path).convert("RGBA")

def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ─── PREPROCESSORS ────────────────────────────────────────────────────────────

def preprocess_edge_enhanced(img):
    arr = np.array(img.convert("RGB"))
    smooth = cv2.bilateralFilter(arr, d=9, sigmaColor=75, sigmaSpace=75)
    lab = cv2.cvtColor(smooth, cv2.COLOR_RGB2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    lab[:, :, 0] = clahe.apply(lab[:, :, 0])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
    gray = cv2.cvtColor(enhanced, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 40, 120)
    edges_d = cv2.dilate(edges, np.ones((2, 2), np.uint8), iterations=1)
    edge_mask = edges_d[:, :, np.newaxis] / 255.0
    darkened = (enhanced * (1 - 0.7 * edge_mask)).astype(np.uint8)
    alpha = np.array(img)[:, :, 3:]
    return Image.fromarray(np.concatenate([darkened, alpha], axis=2), "RGBA")

def preprocess_posterized(img, levels=8):
    arr = np.array(img.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]
    pixels = arr.reshape(-1, 3)
    lab = cv2.cvtColor(pixels.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB)
    lab = lab.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    _, labels, centers = cv2.kmeans(lab, levels, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    centers_rgb = cv2.cvtColor(centers.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    quantized = centers_rgb[labels.flatten()].reshape(h, w, 3)
    for c in range(3):
        quantized[:, :, c] = cv2.medianBlur(quantized[:, :, c], 3)
    alpha = np.array(img)[:, :, 3:]
    return Image.fromarray(np.concatenate([quantized, alpha], axis=2).astype(np.uint8), "RGBA")

def preprocess_fine_detail(img):
    arr = np.array(img.convert("RGB"))
    blur = cv2.GaussianBlur(arr, (0, 0), sigmaX=3)
    sharpened = np.clip(cv2.addWeighted(arr, 1.8, blur, -0.8, 0), 0, 255).astype(np.uint8)
    result = cv2.bilateralFilter(sharpened, d=5, sigmaColor=40, sigmaSpace=40)
    alpha = np.array(img)[:, :, 3:]
    return Image.fromarray(np.concatenate([result, alpha], axis=2).astype(np.uint8), "RGBA")

# ─── VECTORIZE ────────────────────────────────────────────────────────────────

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

# ─── MODES ────────────────────────────────────────────────────────────────────

MODES = {
    "color": {
        "desc": "Full color spline trace",
        "fn": lambda img, kw: vectorize(img, "color", **kw),
    },
    "bw": {
        "desc": "Binary — logos, lineart",
        "fn": lambda img, kw: vectorize(img, "binary", filter_speckle=kw.get("filter_speckle", 4), **{k: v for k, v in kw.items() if k != "filter_speckle"}),
    },
    "edge": {
        "desc": "Bilateral + CLAHE + Canny edge boost",
        "fn": lambda img, kw: vectorize(preprocess_edge_enhanced(img), "color",
                                        filter_speckle=3, color_precision=8,
                                        layer_difference=10, corner_threshold=50,
                                        length_threshold=3.5, max_iterations=12,
                                        splice_threshold=40, **{k: v for k, v in kw.items()
                                        if k not in ("filter_speckle","color_precision","layer_difference","corner_threshold","length_threshold","max_iterations","splice_threshold")}),
    },
    "posterize": {
        "desc": "K-means LAB quantization → flat regions",
        "fn": lambda img, kw: vectorize(preprocess_posterized(img, kw.get("colors", 8)), "color",
                                        filter_speckle=8, color_precision=4,
                                        layer_difference=4, corner_threshold=60,
                                        length_threshold=4.5, path_precision=kw.get("path_precision", 3)),
    },
    "detail": {
        "desc": "Unsharp mask + tight trace params",
        "fn": lambda img, kw: vectorize(preprocess_fine_detail(img), "color",
                                        filter_speckle=2, color_precision=8,
                                        layer_difference=6, corner_threshold=45,
                                        length_threshold=2.5, max_iterations=15,
                                        splice_threshold=30, **{k: v for k, v in kw.items()
                                        if k not in ("filter_speckle","color_precision","layer_difference","corner_threshold","length_threshold","max_iterations","splice_threshold")}),
    },
}

# ─── RUN ──────────────────────────────────────────────────────────────────────

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

# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PNG → SVG vectorizer")
    parser.add_argument("input", help="Input image (PNG, JPG, WebP)")
    parser.add_argument("-o", "--output", help="Output SVG path")
    mode_help = "Mode: " + ", ".join(f"{k} ({v['desc']})" for k, v in MODES.items())
    parser.add_argument("-m", "--mode", choices=list(MODES), default="color", help=mode_help)
    parser.add_argument("--all", action="store_true", help="Run all modes")
    parser.add_argument("--colors", type=int, default=8, help="Colors for posterize mode")
    parser.add_argument("--filter-speckle", type=int, default=4)
    parser.add_argument("--color-precision", type=int, default=6)
    parser.add_argument("--corner-threshold", type=int, default=60)
    parser.add_argument("--path-precision", type=int, default=3)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        sys.exit(f"Error: file not found: {args.input}")

    base = os.path.splitext(args.input)[0]
    kwargs = {
        "colors": args.colors,
        "filter_speckle": args.filter_speckle,
        "color_precision": args.color_precision,
        "corner_threshold": args.corner_threshold,
        "path_precision": args.path_precision,
    }

    print(f"\nInput: {args.input}")
    if args.all:
        for mode in MODES:
            run(args.input, f"{base}_{mode}.svg", mode, **kwargs)
    else:
        out = args.output or f"{base}_{args.mode}.svg"
        run(args.input, out, args.mode, **kwargs)
