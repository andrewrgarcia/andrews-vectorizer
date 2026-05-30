from PIL import Image
import io

def load_image(path):
    return Image.open(path).convert("RGBA")

def img_to_bytes(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

