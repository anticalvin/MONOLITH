#!/usr/bin/env python3
"""Offline SAFE export regression: browser PNG, SVG rasterization, OpenCV and ZBar.

Run after placing controlled browser exports in export-regression/<subject>-browser-fixed.png
and <subject>-direct.svg. The script never alters QR encoding; it only rasterizes and decodes.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import cv2

RESEARCH = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "export-regression"
PAYLOAD = "https://example.com"
SUBJECTS = ("astronaut", "camera", "cat")


def decode_opencv(path: Path) -> str:
    image = cv2.imread(str(path))
    if image is None:
        return "UNVERIFIED / unreadable image"
    value, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    return value or "DECODE FAILED"


def decode_zbar(path: Path) -> str:
    zbar = shutil.which("zbarimg")
    if not zbar:
        return "UNVERIFIED / zbarimg unavailable"
    result = subprocess.run([zbar, "--quiet", str(path)], text=True, capture_output=True, check=False)
    if result.returncode != 0:
        return "DECODE FAILED"
    return result.stdout.strip().removeprefix("QR-Code:") or "DECODE FAILED"


def rasterize(svg: Path, png: Path) -> str:
    magick = shutil.which("magick")
    if not magick:
        return "UNVERIFIED / ImageMagick unavailable"
    result = subprocess.run([magick, "-background", "white", "-density", "192", str(svg), "-resize", "1776x1776!", str(png)], text=True, capture_output=True, check=False)
    return "OK" if result.returncode == 0 else "FAILED / " + result.stderr.strip()


def classify(values: dict[str, str]) -> str:
    answers = [v for v in values.values() if not v.startswith("UNVERIFIED")]
    return "PASS" if answers and all(v == PAYLOAD for v in answers) else "FAIL" if answers else "INCONCLUSIVE"


def main() -> None:
    results = {"payload": PAYLOAD, "subjects": {}}
    for subject in SUBJECTS:
        browser = OUT / f"{subject}-browser-fixed.png"
        svg = OUT / f"{subject}-direct.svg"
        raster = OUT / f"{subject}-rasterized-1776.png"
        known = RESEARCH / "benchmark_outputs" / f"{subject}_safe_core.png"
        if svg.exists():
            rasterize(svg, raster)
        rows = {}
        for name, path in {"known_good_research_png": known, "browser_png": browser, "svg_rasterized_1776": raster}.items():
            if path.exists():
                rows[name] = {"opencv": decode_opencv(path), "zbar": decode_zbar(path)}
            else:
                rows[name] = {"opencv": "INCONCLUSIVE / missing", "zbar": "INCONCLUSIVE / missing"}
        flat = {f"{artifact}:{decoder}": value for artifact, row in rows.items() for decoder, value in row.items()}
        results["subjects"][subject] = {"results": rows, "classification": classify(flat)}
    (OUT / "regression-results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
