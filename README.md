# Visual Regression Testing Pipeline

An end-to-end, beginner-friendly visual regression testing project using **Python, Playwright, Pillow, and GitHub Actions**.

It captures screenshots of a demo web page across Chromium/Firefox/WebKit and desktop/mobile viewports, compares them with approved baseline images, creates visual diff images, supports ignored regions, and can update baselines after review.

## 1. Requirements

- Windows 10/11, macOS, or Linux
- Python 3.10+
- VS Code
- Git (optional, required for GitHub Actions)

## 2. Run in VS Code (Windows)

Open this folder in VS Code. Open **Terminal → New Terminal**, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install
```

If PowerShell blocks activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Install all three browsers (Chromium, Firefox, WebKit):

```powershell
playwright install chromium firefox webkit
```

## 3. First run: create approved baselines

Start the demo website in Terminal 1:

```powershell
python -m http.server 8000
```

Keep it running. In Terminal 2, activate the virtual environment and run:

```powershell
python visual_regression.py --update-baselines
```

This creates approved reference screenshots under `baselines/`.

## 4. Run visual tests

```powershell
python visual_regression.py
```

- Exit code `0`: all comparisons passed.
- Exit code `1`: one or more visual changes exceeded the configured threshold.
- Captured screenshots and diff images are saved under `artifacts/`.

Open `artifacts/report.html` in your browser to view the results.

## 5. Try a deliberate UI change

Edit `index.html`, for example change the heading text or button color. Run:

```powershell
python visual_regression.py
```

The changed screenshots will fail comparison and produce diff images. This demonstrates how the pipeline catches unintended UI changes.

## 6. Ignore dynamic regions

Edit `config.json`. Each ignore region is `[x, y, width, height]` in CSS pixels. Example:

```json
"ignore_regions": [
  {"x": 20, "y": 20, "width": 220, "height": 60}
]
```

The sample configuration ignores the live clock area. Ignored areas are masked before comparison.

## 7. Approve a new baseline

After reviewing the screenshots and confirming the change is intentional:

```powershell
python visual_regression.py --update-baselines
```

This replaces the approved baseline screenshots with the latest captures. Review and commit the changed files in `baselines/`.

## 8. GitHub Actions

The included workflow runs on every pull request and on pushes to `main`:

1. Installs Python and Playwright browsers.
2. Starts the demo web server.
3. Captures screenshots on all configured browser/viewport combinations.
4. Compares them with the committed baseline images.
5. Uploads screenshots, diffs, and the HTML report as workflow artifacts.
6. Adds/updates a pull-request comment with pass/fail details and artifact instructions.

To approve baselines in GitHub, review the visual artifacts first, check out the PR branch locally, run `python visual_regression.py --update-baselines`, commit the updated `baselines/` folder, and push. The PR workflow runs again against the new approved images.

## 9. Configuration

`config.json` controls:
- Target URL
- Browsers: chromium, firefox, webkit
- Viewports
- Pixel-difference threshold
- Perceptual mean absolute error threshold
- Ignore regions
- Screenshot wait time

The demo runs locally at `http://127.0.0.1:8000`. Change `base_url` if testing another locally accessible application.

## Project structure

```text
visual-regression-testing-pipeline/
├── .github/workflows/visual-regression.yml
├── baselines/                 # Approved reference screenshots
├── artifacts/                 # Generated screenshots, diffs, report
├── tests/
│   └── test_image_compare.py  # Unit tests for comparison engine
├── config.json
├── index.html                 # Demo application
├── requirements.txt
├── visual_regression.py       # Main pipeline
├── image_compare.py           # Pixel/perceptual comparison
├── approve_baselines.py       # Explicit baseline approval helper
└── README.md
```

## Troubleshooting

- **Browser executable missing:** run `playwright install chromium firefox webkit`.
- **Port 8000 busy:** start the server on another port, e.g. `python -m http.server 8001`, then update `base_url` in `config.json`.
- **First run fails because baselines do not exist:** run `python visual_regression.py --update-baselines` first.
- **Firefox/WebKit install fails:** try Chromium first by setting `"browsers": ["chromium"]` in `config.json`.
- **Large diffs due to animation/font loading:** the runner disables animations, waits for fonts, and uses stable demo content. For your own app, use deterministic test data and wait for the page to finish loading.

## Notes

This is an educational starter project. For production use, add authentication-safe test URLs, deterministic test data, and project-specific selectors/wait conditions. Baselines should be reviewed by a human before approval.
