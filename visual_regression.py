import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from image_compare import compare_images

ROOT = Path(__file__).resolve().parent
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
BASELINES = ROOT / "baselines"
ARTIFACTS = ROOT / "artifacts"

def safe_name(value):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in value)

def capture_all():
    ARTIFACTS.mkdir(exist_ok=True)
    results = []
    with sync_playwright() as p:
        browser_types = {
            "chromium": p.chromium,
            "firefox": p.firefox,
            "webkit": p.webkit
        }
        for browser_name in CONFIG["browsers"]:
            if browser_name not in browser_types:
                print(f"Skipping unknown browser: {browser_name}")
                continue
            browser = browser_types[browser_name].launch(headless=True)
            for viewport in CONFIG["viewports"]:
                context = browser.new_context(
                    viewport={"width": viewport["width"], "height": viewport["height"]},
                    device_scale_factor=1
                )
                page = context.new_page()
                page.goto(CONFIG["base_url"], wait_until="networkidle")
                page.add_style_tag(content="*, *::before, *::after { animation: none !important; transition: none !important; caret-color: transparent !important; }")
                page.evaluate("document.fonts.ready")
                page.wait_for_timeout(CONFIG.get("wait_after_load_ms", 300))
                name = f"{browser_name}__{safe_name(viewport['name'])}.png"
                actual_path = ARTIFACTS / name
                page.screenshot(path=str(actual_path), full_page=True, animations="disabled")
                context.close()
                results.append({
                    "browser": browser_name,
                    "viewport": viewport["name"],
                    "actual": actual_path,
                    "baseline": BASELINES / name,
                    "diff": ARTIFACTS / f"diff__{name}"
                })
            browser.close()
    return results

def write_report(rows, update_mode=False):
    status = "BASELINES UPDATED" if update_mode else (
        "PASSED" if all(r.get("passed", False) for r in rows) else "FAILED")
    parts = [f"""<!doctype html><html><head><meta charset="utf-8"><title>Visual Regression Report</title>
<style>body{{font:15px Arial;margin:30px;background:#f5f7fb;color:#182230}}h1{{margin-bottom:5px}}
.badge{{display:inline-block;padding:7px 12px;border-radius:8px;background:#e6efff;color:#2457d6;font-weight:bold}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:18px;margin-top:25px}}
article{{background:white;border:1px solid #e4e7ec;border-radius:12px;padding:16px}}
img{{width:100%;border:1px solid #ddd;border-radius:6px}}small{{color:#667085}}</style></head><body>
<h1>Visual Regression Testing Report</h1><span class="badge">{status}</span>
<p>Generated: {datetime.now(timezone.utc).isoformat()}</p><div class="grid">"""]
    for r in rows:
        metrics = ("Baseline created / updated" if update_mode else
                   f"Changed pixels: {r.get('changed_pixel_ratio', 0):.3%} · Perceptual MAE: {r.get('perceptual_mae', 0):.3f}")
        state = "UPDATED" if update_mode else ("PASS" if r.get("passed") else "FAIL")
        actual = Path(r["actual"]).name
        diff = Path(r["diff"]).name
        parts.append(f"""<article><h2>{r['browser']} / {r['viewport']} — {state}</h2><p>{metrics}</p>
<h3>Captured screenshot</h3><img src="{actual}" alt="Screenshot">
{"<h3>Difference image</h3><img src='"+diff+"' alt='Difference'>" if not update_mode else ""}</article>""")
    parts.append("</div></body></html>")
    (ARTIFACTS / "report.html").write_text("\n".join(parts), encoding="utf-8")

def main():
    parser = argparse.ArgumentParser(description="Playwright visual regression pipeline")
    parser.add_argument("--update-baselines", action="store_true",
                        help="Approve current screenshots as new baselines")
    args = parser.parse_args()
    BASELINES.mkdir(exist_ok=True)
    ARTIFACTS.mkdir(exist_ok=True)
    print("Capturing pages with Playwright...")
    captures = capture_all()
    rows = []
    for item in captures:
        if args.update_baselines:
            import shutil
            shutil.copy2(item["actual"], item["baseline"])
            item["passed"] = True
            rows.append(item)
            print(f"BASELINE UPDATED: {item['baseline'].name}")
            continue
        if not item["baseline"].exists():
            item["passed"] = False
            item["error"] = "Baseline missing. Run with --update-baselines first."
            print(f"FAIL: {item['baseline'].name} — baseline missing")
        else:
            metrics = compare_images(
                item["baseline"], item["actual"], item["diff"],
                pixel_threshold=CONFIG["pixel_threshold"],
                max_different_pixel_ratio=CONFIG["max_different_pixel_ratio"],
                perceptual_mae_threshold=CONFIG["perceptual_mae_threshold"],
                ignore_regions=CONFIG.get("ignore_regions", [])
            )
            item.update(metrics)
            print(f"{'PASS' if item['passed'] else 'FAIL'}: {item['browser']}/{item['viewport']} "
                  f"changed={item['changed_pixel_ratio']:.3%}, MAE={item['perceptual_mae']:.3f}")
        rows.append(item)
    write_report(rows, args.update_baselines)
    failures = sum(not r.get("passed", False) for r in rows)
    print(f"\nReport: {ARTIFACTS / 'report.html'}")
    print(f"Results: {len(rows) - failures}/{len(rows)} passed")
    return 0 if args.update_baselines or failures == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
