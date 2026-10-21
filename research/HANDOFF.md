# QR Portrait research handoff — 2026-10-21

## Production boundary

The supplied MONOLITH archive is restored as the production foundation. QR Portrait research belongs under research/ until it reaches the stated dual-decoder and visual-recognition milestone.

## Supplied archive findings

| Archive | What executed before handoff | Result |
|---|---|---|
| Portrait laboratory | Python fixed-core/micro-pattern search | Core 7 was the only dual-decoder-safe setting; best dual-pass similarity 0.4361. |
| V3 sprint | 120 fixed-core candidates | 44 dual passes, but output remained QR-dominated. |
| V4 sprint | 200 candidates / 5 skimage samples / OpenCV + ZBar | Baseline: 40/40 dual passes; image-first: 0/120; conservative core-5: 0/40. |

None of those archives executed true QArt/Reed--Solomon-aware optimization.

## Reference execution status

| Reference | Commit | License | Execution |
|---|---|---|---|
| andrewyur/qart | 6e0e00804a1994db7098432c19fadfc552071e30 | repository LICENSE present | Built locally after a research-only image 0.24.9 compatibility pin; generated research/outputs/qart_astronaut.png from the supplied astronaut source in 14.48 ms. Independent decoder verification is pending. |
| ychalier/halftone-qrcode | 9b498e4844d9a1730533ab58b36cf6ddfc9f62f3 | not yet audited | cloned, not executed |
| zhengkyl/fuqr | 456a598a3630bb0b1d74421c1f9f0c769b542608 | repository LICENSE present | cloned, not executed |
| Kaminyou/Halftone-Color-QR-Codes | de1a0ac622a2a5530fa97825795c7cced0d0adae | MIT | cloned, not executed |

The initial QArt build failed because image 0.25 resolved a transitive edition-2024 crate unsupported by local Cargo 1.82. Pinning image 0.24.9 in the research clone allowed the reference binary to build. Local OpenCV/ZBar Python packages were absent; an install was started but did not finish, so no dual-decoder claim is made.

## Next reproducible milestone

1. Complete isolated decoder environment installation.
2. Execute all four references without modifying production files.
3. Generate and inspect three portrait contact sheets.
4. Require exact payload from OpenCV and ZBar, then run the transformation matrix. Only then compare a genuine padding/RS-aware QArt track against the fixed-core baseline.
