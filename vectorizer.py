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



# vectorizer.py

from andrews_vectorizer.cli import main

if __name__ == "__main__":
    main()