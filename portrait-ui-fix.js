/* File inputs keep their visible filename until reset explicitly. */
(()=> {
  const logo = document.getElementById('logo');
  document.getElementById('clearLogo')?.addEventListener('click', () => { logo.value = ''; });
  const core = document.getElementById('core');
  if (core && !core.dataset.portraitTuned) {
    core.dataset.portraitTuned = 'true';
    core.min = '52';
    core.value = '68';
    core.dispatchEvent(new Event('input', { bubbles: true }));
  }
})();
