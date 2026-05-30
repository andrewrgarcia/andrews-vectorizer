"""
PNG → SVG Vectorizer
Usage: uv run vectorizer.py photo.png
       uv run vectorizer.py photo.png -m edge
       uv run vectorizer.py photo.png --all
"""
from andrews_vectorizer.cli import main

if __name__ == "__main__":
    main()