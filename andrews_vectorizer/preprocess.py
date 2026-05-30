import cv2
import numpy as np
from PIL import Image

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
