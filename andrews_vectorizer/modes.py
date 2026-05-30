from .tracer import vectorize
from .preprocess import preprocess_edge_enhanced, preprocess_fine_detail, preprocess_posterized

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
