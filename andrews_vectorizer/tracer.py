import vtracer

from .utils import img_to_bytes

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