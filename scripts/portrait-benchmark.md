# Portrait benchmark protocol

Run the site with \`python3 -m http.server 8000\`, upload each licensed test image, export 1024px PNG and SVG, rasterize the SVG, then decode both artifacts with two independent decoders. Record an exact string comparison to the requested payload for: original, 50% downsample, Gaussian blur, JPEG quality 70, 3-degree rotation, reduced contrast, and a mild perspective warp.

Use five photographs: high-contrast front-facing, low-contrast, side-lit, detailed hair/features, and a non-portrait geometric scene. Keep their source licenses and generated contact sheets in \`artifacts/\` (ignored by default). Do not describe this protocol as completed until those exported artifacts and device-camera observations exist.
