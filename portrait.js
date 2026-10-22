(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  let image = null, timer, revision = 0, latestRender = null;
  const isFunction = (x, y, n) => {
    const finder = (a, b) => x >= a - 1 && x <= a + 7 && y >= b - 1 && y <= b + 7;
    return finder(0, 0) || finder(n - 7, 0) || finder(0, n - 7) || x === 6 || y === 6 || x === 8 || y === 8;
  };
  const setError = text => { $('portraitError').textContent = text; };
  function status(snapshot, value, detail) {
    if (snapshot && latestRender !== snapshot) return;
    if (snapshot) { snapshot.verification = value; snapshot.ready = value !== 'CHECKING'; }
    $('portraitVerify').textContent = value; $('portraitVerifyInfo').textContent = detail;
    $('portraitExportInfo').textContent = value === 'VERIFIED' ? 'EXPORTS MATCH THIS BROWSER-VERIFIED RENDER.' : 'EXPORTS ARE MARKED ' + value + '. SCAN THE FINAL FILE BEFORE USE.';
  }
  function sourceCanvas() {
    const s = 840, canvas = $('portraitSource'), ctx = canvas.getContext('2d', { willReadFrequently: true });
    const zoom = +$('portraitZoom').value, w = image.width * Math.max(s / image.width, s / image.height) * zoom, h = image.height * Math.max(s / image.width, s / image.height) * zoom;
    canvas.width = canvas.height = s; ctx.fillStyle = '#fff'; ctx.fillRect(0, 0, s, s);
    ctx.drawImage(image, (s - w) / 2 + (+$('portraitPan').value * s / 100), (s - h) / 2 + (+$('portraitPanY').value * s / 100), w, h);
    const pixels = ctx.getImageData(0, 0, s, s), contrast = +$('portraitContrast').value / 100, exposure = +$('portraitExposure').value, threshold = +$('portraitThreshold').value;
    for (let i = 0; i < pixels.data.length; i += 4) {
      let l = (.2126 * pixels.data[i] + .7152 * pixels.data[i + 1] + .0722 * pixels.data[i + 2]) / 255;
      l = Math.max(0, Math.min(1, (l - .5) * contrast + .5 + exposure));
      if (threshold) l = l > threshold / 100 ? 1 : 0;
      pixels.data[i] = pixels.data[i + 1] = pixels.data[i + 2] = Math.round(255 * l);
    }
    ctx.putImageData(pixels, 0, 0); return canvas;
  }
  function safeCore(qr, source) {
    const n = qr.getModuleCount(), u = 16, total = (n + 8) * u, density = +$('portraitDensity').value / 100;
    const data = source.getContext('2d', { willReadFrequently: true }).getImageData(0, 0, source.width, source.height).data;
    const pieces = [`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${total} ${total}" width="${total}" height="${total}"><rect width="100%" height="100%" fill="#fff"/>`];
    for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
      const X = (x + 4) * u, Y = (y + 4) * u, dark = qr.isDark(y, x), l = data[(Math.floor((y + .5) * source.height / n) * source.width + Math.floor((x + .5) * source.width / n)) * 4] / 255;
      if (dark) pieces.push(`<rect x="${X}" y="${Y}" width="${u}" height="${u}" fill="#111"/>`);
      if (!dark && !isFunction(x, y, n) && l < .8) pieces.push(`<circle cx="${X + u / 2}" cy="${Y + u / 2}" r="${u * (.07 + (1 - l) * .24 * density)}" fill="#202020"/>`);
    }
    pieces.push('</svg>'); return { svg: pieces.join(''), analysis: { imageInfluence: 0, mode: 'safe' } };
  }
  function setModeCopy(mode, analysis) {
    const copy = { safe: 'Safe-core fallback: conventional data modules with a restrained image field.', balanced: 'Balanced V2: source luminance, contrast and contours shape the non-function modules while retaining a scan-oriented core.', 'image-first': 'Image-first V2: source structure determines most data-module marks. Scanning is not guaranteed.' };
    $('portraitModeNote').textContent = copy[mode];
    $('portraitEngine').textContent = mode === 'safe' ? 'SAFE-CORE HALFTONE' : `${mode.toUpperCase()} / V2 · PHOTO FIELD ${analysis.imageInfluence}%`;
    const warn = $('portraitWarning');
    warn.hidden = mode === 'safe';
    warn.textContent = mode === 'image-first' ? 'EXPERIMENTAL ARTWORK / SCANNING NOT VERIFIED UNTIL THIS EXACT OUTPUT DECODES.' : 'BALANCED V2 IS EXPERIMENTAL. EXPORT STATUS WILL REFLECT THIS CURRENT RENDER.';
  }
  function buildQR(payload) {
    if (!/^https?:\/\/\S+$/i.test(payload)) throw Error('Enter a complete http:// or https:// URL.');
    const qr = new QRCode(0, ECL.H), binary = Array.from(new TextEncoder().encode(payload), b => String.fromCharCode(b)).join('');
    qr.addData(binary); qr.make(); return qr;
  }
  async function rasterize(snapshot) {
    const im = new Image(); im.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(snapshot.svg); await im.decode();
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = snapshot.rasterSize;
    const ctx = canvas.getContext('2d'); ctx.imageSmoothingEnabled = false; ctx.drawImage(im, 0, 0, canvas.width, canvas.height);
    return canvas;
  }
  async function verify(snapshot) {
    try {
      if (!('BarcodeDetector' in window)) throw Error('Browser decoder unavailable');
      const canvas = await rasterize(snapshot);
      const found = await new BarcodeDetector({ formats: ['qr_code'] }).detect(canvas);
      if (latestRender !== snapshot) return;
      const exact = found.some(item => item.rawValue === snapshot.payload);
      status(snapshot, exact ? 'VERIFIED' : 'FAILED', exact ? 'Exact URL matched in this browser.' : 'This rendered output did not decode to the exact URL.');
      $('portraitStatus').textContent = exact ? 'RENDERED / VERIFIED' : 'RENDERED / CHECK STATUS';
    } catch (_) {
      if (latestRender === snapshot) { status(snapshot, 'UNVERIFIED', 'This browser has no usable QR decoder.'); $('portraitStatus').textContent = 'RENDERED / UNVERIFIED'; }
    }
  }
  function render() {
    if (!image) return;
    const started = performance.now(), id = ++revision, mode = $('portraitInfluence').value, payload = $('portraitUrl').value.trim();
    try {
      const snapshot = { id, mode, payload, svg: '', verification: 'CHECKING', ready: false };
      latestRender = snapshot; $('portraitStatus').textContent = 'ANALYSING PHOTO'; status(snapshot, 'CHECKING', 'Building the current photo-driven module field…');
      const qr = buildQR(payload), source = sourceCanvas();
      const result = mode === 'safe' ? safeCore(qr, source) : window.MonolithPortraitV2.render({ qr, source, mode, density: +$('portraitDensity').value / 100 });
      snapshot.svg = result.svg; const total = (qr.getModuleCount() + 8) * 16; snapshot.rasterSize = total * Math.max(2, Math.ceil(1200 / total)); $('portraitPreview').innerHTML = snapshot.svg; $('portraitMatrix').textContent = qr.getModuleCount() + ' × ' + qr.getModuleCount();
      setModeCopy(mode, result.analysis); $('portraitStatus').textContent = `RENDERED / ${(performance.now() - started).toFixed(0)}MS`; verify(snapshot); setError('');
    } catch (error) { setError(error.message); $('portraitStatus').textContent = 'CHECK INPUT'; }
  }
  function schedule() { if (image) { clearTimeout(timer); timer = setTimeout(render, 110); } }
  function load(file) {
    if (!file) return;
    if (!/^image\/(jpeg|png|webp)$/.test(file.type)) return setError('Use a JPEG, PNG, or WebP image.');
    if (file.size > 8 * 1024 * 1024) return setError('Choose an image smaller than 8 MB.');
    $('portraitStatus').textContent = 'LOADING PHOTO'; const reader = new FileReader();
    reader.onload = () => { image = new Image(); image.onload = () => { setError(''); render(); }; image.onerror = () => setError('The selected image could not be read.'); image.src = reader.result; };
    reader.onerror = () => setError('The selected file could not be read.'); reader.readAsDataURL(file);
  }
  function download(blob, name) { const a = document.createElement('a'), url = URL.createObjectURL(blob); a.href = url; a.download = name; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1500); }
  function exportedName(snapshot, extension) { return `monolith-portrait-${snapshot.mode}-${snapshot.verification.toLowerCase()}-r${snapshot.id}.${extension}`; }
  $('portraitFile').addEventListener('change', event => load(event.target.files[0]));
  $('portraitDrop').addEventListener('dragover', event => { event.preventDefault(); $('portraitDrop').classList.add('is-dragging'); });
  $('portraitDrop').addEventListener('dragleave', () => $('portraitDrop').classList.remove('is-dragging'));
  $('portraitDrop').addEventListener('drop', event => { event.preventDefault(); $('portraitDrop').classList.remove('is-dragging'); load(event.dataTransfer.files[0]); });
  ['portraitUrl', 'portraitInfluence', 'portraitZoom', 'portraitPan', 'portraitPanY', 'portraitExposure', 'portraitContrast', 'portraitThreshold', 'portraitDensity'].forEach(id => $(id).addEventListener('input', () => { revision++; latestRender = null; status(null, 'CHECKING', 'Control changed; rebuilding the preview…'); schedule(); }));
  $('portraitGenerate').onclick = () => image ? render() : setError('Upload a photo first.');
  $('portraitPng').onclick = async () => { const snapshot = latestRender; if (!snapshot) return setError('Generate a portrait first.'); if (!snapshot.ready) return setError('Wait for the latest render and verification status before exporting.'); try { const canvas = await rasterize(snapshot); canvas.toBlob(blob => blob && download(blob, exportedName(snapshot, 'png')), 'image/png'); } catch (_) { setError('PNG export could not rasterize this render.'); } };
  $('portraitSvg').onclick = () => { const snapshot = latestRender; return !snapshot ? setError('Generate a portrait first.') : !snapshot.ready ? setError('Wait for the latest render and verification status before exporting.') : download(new Blob([snapshot.svg], { type: 'image/svg+xml' }), exportedName(snapshot, 'svg')); };
})();
