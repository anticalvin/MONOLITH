# MONOLITH release readiness

## Working product

- **Standard QR** remains the production default. It generates byte-exact local QR payloads and exports matching PNG and SVG artwork.
- **Portrait Effect** is explicitly experimental: it accepts JPEG, PNG, and WebP under 8 MB, supports crop/zoom and tonal controls, and reports `VERIFIED`, `FAILED`, or `UNVERIFIED` from the browser decoder.
- Exports include the verification state in their filename and export feedback. `UNVERIFIED` is never presented as verified.

## Decoder evidence

The preserved safe-core astronaut, camera, and cat exports decoded to `https://example.com` with OpenCV and ZBar in the Sprint 12 release audit. The exact-payload bake-off results are retained under `research/exact_payload_bakeoff_outputs/` and are not production code.

## Standard QR export hardening

- Standard exports now bind an immutable payload/SVG/render snapshot to verification and download filenames.
- PNG exports use an integer QR-module pitch and disable smoothing. A Chromium-generated URL PNG (`1036×1036`, 28px pitch including quiet zone) decoded to exact `https://example.com` with OpenCV and ZBar.
- The corresponding downloaded SVG, independently rasterized at `1036×1036`, decoded with ZBar; OpenCV returned a false negative. Browser `BarcodeDetector` remains supplementary evidence only.
- The currently completed release evidence covers the production URL/default appearance. The remaining content-format and browser/device matrix is documented as incomplete in the RC1 report.

## Experimental / excluded

- Portrait Effect is visual QR artwork, not a photorealistic portrait promise.
- QArt and fragment-modified URLs remain offline research only and are not reachable from the interface.

## Known limitations

- Browser verification relies on `BarcodeDetector`; browsers without it show `UNVERIFIED`.
- Browser verification is not a camera-device guarantee. Test exported artwork before printing.
- Portrait effect requires a local user-supplied image; no uploads leave the browser.

## Launch blockers

None for the standard QR product. Portrait Effect should retain its experimental label until tested across the intended browser/device matrix.
