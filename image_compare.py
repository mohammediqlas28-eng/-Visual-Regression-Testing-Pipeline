from PIL import Image, ImageChops, ImageEnhance
import numpy as np

def apply_ignore_regions(image: Image.Image, regions):
    """Return a copy with configured CSS-pixel rectangles masked in neutral gray."""
    result = image.copy().convert("RGB")
    for region in regions:
        x, y = int(region["x"]), int(region["y"])
        w, h = int(region["width"]), int(region["height"])
        # Clip the rectangle to the screenshot bounds.
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(result.width, x + w), min(result.height, y + h)
        if x1 > x0 and y1 > y0:
            result.paste((127, 127, 127), (x0, y0, x1, y1))
    return result

def compare_images(baseline_path, actual_path, diff_path, pixel_threshold=0.10,
                   max_different_pixel_ratio=0.015, perceptual_mae_threshold=2.5,
                   ignore_regions=None):
    """Compare images using changed-pixel ratio and mean absolute RGB error."""
    ignore_regions = ignore_regions or []
    baseline = Image.open(baseline_path).convert("RGB")
    actual = Image.open(actual_path).convert("RGB")

    if baseline.size != actual.size:
        # Normalize actual to baseline dimensions to produce a useful diff.
        actual = actual.resize(baseline.size, Image.Resampling.LANCZOS)

    baseline = apply_ignore_regions(baseline, ignore_regions)
    actual = apply_ignore_regions(actual, ignore_regions)

    a = np.asarray(baseline, dtype=np.int16)
    b = np.asarray(actual, dtype=np.int16)
    delta = np.abs(a - b)
    pixel_changed = np.max(delta, axis=2) > int(pixel_threshold * 255)
    changed_ratio = float(pixel_changed.mean())
    mae = float(delta.mean())

    # Highlight changed pixels in red over a lightened baseline.
    base_light = ImageEnhance.Brightness(baseline).enhance(1.35)
    diff = base_light.copy()
    red_overlay = Image.new("RGB", baseline.size, (255, 0, 0))
    mask = Image.fromarray((pixel_changed * 210).astype("uint8"), mode="L")
    diff.paste(red_overlay, (0, 0), mask)
    diff.save(diff_path)

    passed = (changed_ratio <= max_different_pixel_ratio and
              mae <= perceptual_mae_threshold)
    return {
        "passed": passed,
        "changed_pixel_ratio": changed_ratio,
        "perceptual_mae": mae,
        "width": baseline.width,
        "height": baseline.height
    }
