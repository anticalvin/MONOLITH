# MONOLITH® QR Design Instrument

Self-contained, client-side QR designer. Open `index.html` in a modern browser or run `python -m http.server 8000` from this folder and visit http://localhost:8000.

## Features
- QR payloads for URLs, text, email, phone, SMS, Wi-Fi, and vCard.
- 8 visual presets, 3 module styles, color controls, error correction levels, optional raster logo.
- Real QR matrix encoding, 4-module quiet zone, PNG and SVG exports.
- Browser-native `BarcodeDetector` attempts local verification when supported. If unavailable, the UI says UNVERIFIED, not VERIFIED.

## Limitations
- Not the full original Next.js specification. This is a dependency-free, static implementation.
- Browser-native BarcodeDetector is not available in all browsers. Verify with actual phone cameras.
- Logos and experimental dot patterns may reduce scan reliability. Center logos have no automatic damage-budget analysis.
- Exports are not blocked when unverified. Check exported files on devices before printing.
- SVG embeds a raster logo if provided; without a logo, SVG is vector geometry.
- No automated Playwright suite or phone-camera tests were executed.
- The QR engine is adapted from Kazuhiko Arase's QRCode for JavaScript (MIT), distributed via qrcode-terminal. See THIRD_PARTY_LICENSE.txt.

