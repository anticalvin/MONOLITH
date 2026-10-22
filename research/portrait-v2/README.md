# QR Portrait V2 — Stage A browser prototype

This isolated experiment adds a browser-only, image-analysis renderer in `portrait-v2.js`.
It uses area-averaged luminance, local variance, Sobel-style edges, a modest centre-weighted subject estimate, and module subdivision. It leaves the QR payload and encoder matrix untouched.

## Modes

- **SAFE**: original safe-core renderer; retained as the fallback.
- **BALANCED**: preserves every QR function module, retains a central dark core for dark data modules, and uses source luminance/contours for the remaining marks.
- **IMAGE-FIRST**: source brightness and contours choose larger module marks. It is explicitly allowed to fail scanning and is shown as experimental artwork.

`portrait-v2.js` contains the version-aware protection map used by V2. It covers finder/separator regions, timing, both format-information bands, version-information regions, and every QR-version alignment pattern.

## Observed Chromium results — 2026-10-22

Payload: `https://example.com`; browser: local Chromium/BarcodeDetector; source controls unchanged between modes.

| Fixture | SAFE | BALANCED | IMAGE-FIRST |
|---|---:|---:|---:|
| Astronaut | VERIFIED | VERIFIED | FAILED |
| Camera | VERIFIED | VERIFIED | FAILED |
| Cat | FAILED | VERIFIED | FAILED |

The browser screenshots show that BALANCED is visually distinct from SAFE and retains exact browser decoding. IMAGE-FIRST has a substantially higher image-field participation (85% on astronaut) but is not decodable. Neither new result preserves a recognizable astronaut, photographer, or cat eye in the output alone. This is **functional QR success / visual prototype failure**, not a product-ready QR Portrait breakthrough.

## Reproduction

Serve the repository from a loopback static HTTP server, upload the three fixtures from `research/exact_payload_bakeoff_outputs/`, select every photo-influence mode, and read the UI status after processing. Export is deliberately disabled while the latest render is pending verification; its filename includes both the selected mode and actual verification state.

## Offline decoder spot-check of exported browser artifacts

OpenCV decoded the observed `cat-balanced-verified.png` to the exact payload. OpenCV failed the observed astronaut SAFE, cat SAFE, and cat IMAGE-FIRST exports. ZBar failed all four observed exports. These raw results are in `decoder-benchmark.json`; therefore none of these candidates is dual-decoder **VERIFIED**. The browser status is intentionally not treated as a replacement for the offline gate.

## Decision

Do not merge V2 into `main` or deploy it. The controls and renderer remain on this feature branch as a documented, truthful prototype.
