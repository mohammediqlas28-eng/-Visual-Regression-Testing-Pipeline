# Project Overview

## Objective
Detect unintended visual changes in a web interface by comparing screenshots from the current build against approved baseline screenshots.

## Workflow
1. Playwright opens the target page in each configured browser and viewport.
2. The runner captures a PNG screenshot.
3. Pillow/NumPy compare the current image with its baseline.
4. Pixel-difference ratio and perceptual mean absolute error are calculated.
5. Ignore regions are masked to avoid false alarms from dynamic UI.
6. A red diff image and HTML report are generated.
7. GitHub Actions runs the pipeline on pull requests and uploads the report.
8. A developer reviews the report and explicitly approves intentional changes by updating and committing baselines.

## Technologies
- Python: pipeline orchestration
- Playwright: cross-browser screenshot automation
- Pillow + NumPy: image processing and comparison
- pytest: comparison-engine tests
- GitHub Actions: CI automation

## Evaluation checklist
- [x] Screenshot capture on pull requests
- [x] Pixel-level image comparison
- [x] Perceptual MAE metric
- [x] Configurable ignore regions
- [x] Diff image generation
- [x] HTML report
- [x] Multiple viewports
- [x] Chromium, Firefox, and WebKit configuration
- [x] Baseline approval/update workflow
- [x] CI artifact upload and PR comment
