from PIL import Image
from image_compare import compare_images

def test_identical_images_pass(tmp_path):
    baseline = tmp_path / "base.png"
    actual = tmp_path / "actual.png"
    diff = tmp_path / "diff.png"
    Image.new("RGB", (40, 40), "white").save(baseline)
    Image.new("RGB", (40, 40), "white").save(actual)
    result = compare_images(baseline, actual, diff)
    assert result["passed"] is True
    assert result["changed_pixel_ratio"] == 0
    assert diff.exists()

def test_changed_images_fail(tmp_path):
    baseline = tmp_path / "base.png"
    actual = tmp_path / "actual.png"
    diff = tmp_path / "diff.png"
    Image.new("RGB", (40, 40), "white").save(baseline)
    Image.new("RGB", (40, 40), "black").save(actual)
    result = compare_images(baseline, actual, diff)
    assert result["passed"] is False
    assert result["changed_pixel_ratio"] > 0.9

def test_ignore_region_masks_changes(tmp_path):
    baseline = tmp_path / "base.png"
    actual = tmp_path / "actual.png"
    diff = tmp_path / "diff.png"
    Image.new("RGB", (40, 40), "white").save(baseline)
    changed = Image.new("RGB", (40, 40), "white")
    for x in range(10, 30):
        for y in range(10, 30):
            changed.putpixel((x, y), (0, 0, 0))
    changed.save(actual)
    result = compare_images(
        baseline, actual, diff,
        ignore_regions=[{"x": 10, "y": 10, "width": 20, "height": 20}]
    )
    assert result["passed"] is True
