import sys
import os
import argparse

from .modes import MODES
from .runner import run

def main():
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
