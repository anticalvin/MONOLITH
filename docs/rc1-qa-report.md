# MONOLITH RC1 browser QA

Date: 2026-10-22 (Africa/Johannesburg)

## Environment

- Served locally: `python3 -m http.server 8080 --bind 127.0.0.1`
- Browser automation: Brave/Chromium on macOS, `http://127.0.0.1:8080/index.html`
- Device hardware: not tested.

## Observed pass

| Area | Result | Evidence |
|---|---|---|
| Standard QR initial render | PASS | 29×29 matrix, version 3, H correction shown in live browser |
| Standard exact URL | PASS | Browser `BarcodeDetector` reported `VERIFIED` / `Local decode matched` for `https://example.com` |
| Production page runtime | PASS | Page loaded over HTTP without observed startup/runtime failure |
| Standard controls | PASS (smoke) | Encoding, geometry, error-correction, raster-size and export controls were exposed and keyboard-focusable in browser accessibility tree |
| Standard query/fragment input | PASS | Chromium accepted `https://example.com/path?alpha=1&name=monolith#section` and regenerated the live design before export automation timed out |

## Automated evidence retained from prior release work

- Safe-core astronaut, camera and cat outputs decoded to exact `https://example.com` with OpenCV and ZBar.
- Exact-payload export gate evidence is retained in `research/exact_payload_bakeoff_outputs/results.json`; it is research QA, not a replacement for product-browser testing.

## Not tested in this RC1 browser pass

- PNG and SVG download/reopen/decode cycle.
- URL edge cases, long payload, rapid changes, and empty input.
- Portrait JPEG/PNG/WebP upload, drag/drop, invalid, oversized and corrupt files.
- Portrait export status states after a real upload.
- 1440/1024/768/390/320 layout screenshots.
- Safari, Firefox, iPhone, and Android device testing.
- Complete keyboard-only traversal and touch-device interaction.

## Browser automation blocker

The real Chromium session loaded the local HTTP app and accepted the query/fragment payload. The export test began by registering a download listener and activating the PNG/SVG export controls, but the browser automation kernel reset while waiting for the download event. No downloaded file path was returned, so PNG/SVG reopen-and-decode is correctly left **NOT TESTED**. This is an automation-session failure, not evidence that the application export failed.

## Known limitations

- Portrait Effect remains experimental and browser verification depends on `BarcodeDetector`.
- Browser verification is not a physical-device scanning guarantee.
- QArt remains offline research only and is not a product feature.
- QR Portrait V2 browser prototype results are retained on `feature/qr-portrait-v2`; this failed the visual-recognisability gate and must not be released as a product feature.

## Launch blockers

Complete the untested export, portrait upload, responsive, keyboard, Safari, and mobile-device matrix before a full public launch.

## Recommendation

**CONDITIONAL GO**
