# QR Portrait: engineering decision record

## Chosen baseline

QR Portrait keeps the QR encoder's complete matrix unchanged. All ISO/IEC 18004 function modules are rendered as ordinary solid QR modules: finder patterns and separators, timing, alignment, format/version information, and the fixed dark module. Data modules retain a configurable square centre (default 82% of the module width) with the encoded polarity. Photograph detail is expressed only as module-local decoration outside that core. This is a camera-oriented heuristic, not a QR standard guarantee.

The supplied encoder uses Reed--Solomon error correction and its normal mask selection; Portrait does not spend or modify the error-correction budget. High correction is the default.

## Methods considered

QArt-style encoders alter selected encoded bits then rely on error correction. They can have a strong image likeness, but require exact codeword/interleaving accounting and a decoder-tested damage budget. They are not used in the production mode. Mask selection changes legal data appearance but is not a license to overwrite modules.

Halftone and ordered/error-diffusion approaches make image tones visible through dot density. They are useful here only in the decoration ring. Adaptive thresholding and local contrast help portrait legibility, but can make output less stable if they reduce core contrast.

## Rendering modes

- **Core Dot**: one luminance-weighted surrounding dot.
- **Adaptive Halftone**: two smaller, luminance-weighted dots for finer tone.
- **Hybrid Portrait**: lower-opacity decoration for the safest visual mode.

## Validation strategy and limits

The live check uses BarcodeDetector when supplied by the browser and requires an exact payload match. It is deliberately reported as UNVERIFIED when unavailable. The final exported PNG/SVG must also be tested with independent decoders (for example ZXing and OpenCV) and real iOS/Android cameras before printing. Blur, downsampling, JPEG, rotation, contrast and perspective should be separate hard-gate cases; a similarity score never compensates for one decode failure.

For a later optimizer, candidates should be hard-gated on exact decode, then ranked as 0.55 robustness + 0.30 blurred/downsampled portrait similarity + 0.15 visual clarity. Similarity should be measured after blur/downsampling: SSIM is useful for comparison but does not establish recognizability.

## Advanced work

An experimental QArt path may enumerate payload padding and all legal masks, recompute every Reed--Solomon block, interleave correctly, render each candidate, then independently decode its exported bytes. It should remain experimental until that full pipeline is proven.
