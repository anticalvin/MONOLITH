/* MONOLITH QR Portrait V2 — client-side image-first module renderer.
   It never changes the encoded QR payload or matrix. */
(() => {
  'use strict';
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const alignmentPositions = [[],[],[6,18],[6,22],[6,26],[6,30],[6,34],[6,22,38],[6,24,42],[6,26,46],[6,28,50],[6,30,54],[6,32,58],[6,34,62],[6,26,46,66],[6,26,48,70],[6,26,50,74],[6,30,54,78],[6,30,56,82],[6,30,58,86],[6,34,62,90],[6,28,50,72,94],[6,26,50,74,98],[6,30,54,78,102],[6,28,54,80,106],[6,32,58,84,110],[6,30,58,86,114],[6,34,62,90,118],[6,26,50,74,98,122],[6,30,54,78,102,126],[6,26,52,78,104,130],[6,30,56,82,108,134],[6,34,60,86,112,138],[6,30,58,86,112,142],[6,34,62,90,118,146],[6,30,54,78,102,126,150],[6,24,50,76,102,128,154],[6,28,54,82,110,138,158],[6,32,58,86,114,142,162],[6,26,54,82,110,138,166],[6,30,58,86,114,142,170]];
  const functionCell = (x, y, n) => {
    const version = (n - 17) / 4;
    const finder = (a, b) => x >= a - 1 && x <= a + 7 && y >= b - 1 && y <= b + 7;
    if (finder(0, 0) || finder(n - 7, 0) || finder(0, n - 7) || x === 6 || y === 6 || x === 8 || y === 8) return true;
    const positions = alignmentPositions[version] || [];
    for (const ay of positions) for (const ax of positions) {
      const overlapsFinder = (ax === 6 && ay === 6) || (ax === 6 && ay === n - 7) || (ax === n - 7 && ay === 6);
      if (!overlapsFinder && Math.abs(x - ax) <= 2 && Math.abs(y - ay) <= 2) return true;
    }
    return version >= 7 && ((x < 6 && y >= n - 11) || (y < 6 && x >= n - 11));
  };
  function analyse(canvas, n) {
    const { data, width: w, height: h } = canvas.getContext('2d', { willReadFrequently: true }).getImageData(0, 0, canvas.width, canvas.height);
    const lum = (x, y) => {
      const p = (Math.max(0, Math.min(h - 1, y)) * w + Math.max(0, Math.min(w - 1, x))) * 4;
      return (.2126 * data[p] + .7152 * data[p + 1] + .0722 * data[p + 2]) / 255;
    };
    const cells = Array.from({ length: n }, () => Array(n));
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
      const x0 = Math.floor(x * w / n), x1 = Math.max(x0 + 1, Math.floor((x + 1) * w / n));
      const y0 = Math.floor(y * h / n), y1 = Math.max(y0 + 1, Math.floor((y + 1) * h / n));
      let sum = 0, sum2 = 0, count = 0;
      for (let py = y0; py < y1; py += Math.max(1, Math.floor((y1 - y0) / 5))) for (let px = x0; px < x1; px += Math.max(1, Math.floor((x1 - x0) / 5))) {
        const v = lum(px, py); sum += v; sum2 += v * v; count++;
      }
      const cx = Math.floor((x + .5) * w / n), cy = Math.floor((y + .5) * h / n);
      const gx = lum(cx + 2, cy) - lum(cx - 2, cy), gy = lum(cx, cy + 2) - lum(cx, cy - 2);
      const edge = clamp(Math.hypot(gx, gy) * 1.7);
      const variance = clamp((sum2 / count) - (sum / count) ** 2) * 8;
      const radial = 1 - Math.min(1, Math.hypot(x / (n - 1) - .5, y / (n - 1) - .5) / .71);
      cells[y][x] = { l: sum / count, edge, contrast: clamp(variance), subject: clamp(.72 * edge + .22 * variance + .06 * radial) };
    }
    return cells;
  }
  function render({ qr, source, mode, density }) {
    const n = qr.getModuleCount(), u = 16, q = 4, total = (n + 2 * q) * u, cells = analyse(source, n);
    const cutoff = mode === 'balanced' ? .52 : .58;
    const parts = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${total} ${total}" width="${total}" height="${total}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="#fdfcf8"/>`];
    let imageMarks = 0, eligible = 0;
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
      const X = (x + q) * u, Y = (y + q) * u, isDark = qr.isDark(y, x), fixed = functionCell(x, y, n), c = cells[y][x];
      if (fixed) { if (isDark) parts.push(`<rect x="${X}" y="${Y}" width="${u}" height="${u}" fill="#111"/>`); continue; }
      eligible++;
      const targetDark = c.l < cutoff - (c.subject - .4) * .12;
      const emphasis = clamp(.25 + .75 * c.subject) * density;
      if (mode === 'balanced') {
        if (isDark) {
          const inset = targetDark ? .06 : .14;
          parts.push(`<rect x="${X + u * inset}" y="${Y + u * inset}" width="${u * (1 - inset * 2)}" height="${u * (1 - inset * 2)}" fill="#111"/>`);
          if (targetDark && c.edge > .13) parts.push(`<rect x="${X + u * .05}" y="${Y + u * .43}" width="${u * .9}" height="${u * .14}" fill="#111"/>`);
        } else if (targetDark) {
          const r = u * (.12 + .18 * emphasis);
          parts.push(`<circle cx="${X + u / 2}" cy="${Y + u / 2}" r="${r}" fill="#151515"/>`); imageMarks++;
        }
      } else {
        // Image-first: the source decides the larger module mark; the QR matrix remains a constrained scaffold.
        const size = targetDark ? (.38 + .18 * emphasis) : (.16 + .14 * (1 - c.l));
        const mustHold = isDark ? .34 : 0;
        const side = Math.max(size, mustHold) * u;
        const shift = c.edge > .18 ? (c.l < .5 ? .07 : -.07) : 0;
        if (targetDark || isDark) {
          parts.push(`<rect x="${X + (u - side) / 2 + u * shift}" y="${Y + (u - side) / 2}" width="${side}" height="${side}" fill="#111"/>`);
          imageMarks++;
        }
        if (c.edge > .22 && targetDark) parts.push(`<circle cx="${X + u / 2}" cy="${Y + u / 2}" r="${u * .1}" fill="#111"/>`);
      }
    }
    parts.push('</svg>');
    return { svg: parts.join(''), analysis: { imageMarks, eligible, imageInfluence: Math.round(100 * imageMarks / Math.max(1, eligible)), mode } };
  }
  window.MonolithPortraitV2 = { render };
})();
