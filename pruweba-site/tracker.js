/**
 * Shared lightweight event tracker for Pruweba + RankFixer.
 * Sends beacon-style POSTs to https://hook.pruweba.com/track
 */
(function () {
  const ENDPOINT = '/api/track';
  const SEND_TIMEOUT_MS = 4000;

  function domain() {
    try { return window.location.hostname || 'unknown'; } catch (e) { return 'unknown'; }
  }
  function page() {
    try { return window.location.pathname || '/'; } catch (e) { return '/'; }
  }
  function ts() {
    try { return new Date().toISOString(); } catch (e) { return ''; }
  }
  function shortText(el) {
    try {
      const text = (el.textContent || '').replace(/\s+/g, ' ').trim();
      return text.substring(0, 50);
    } catch (e) { return ''; }
  }
  function send(payload) {
    const body = JSON.stringify(payload);
    if (navigator.sendBeacon) {
      try { navigator.sendBeacon(ENDPOINT, body); return; } catch (e) {}
    }
    fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: true,
    }).catch(() => {});
  }

  // Auto-pageview
  document.addEventListener('DOMContentLoaded', function () {
    send({ event: 'pageview', page: page(), domain: domain(), timestamp: ts() });
  });

  // Global click capture
  document.addEventListener('click', function (evt) {
    let target = evt.target;
    const trackEl = target.closest ? target.closest('a, button, [data-track]') : null;
    if (!trackEl) return;
    const id = trackEl.id || '';
    const text = shortText(trackEl);
    const href = trackEl.href || trackEl.getAttribute('href') || '';
    const explicit = trackEl.getAttribute('data-track') || '';
    let name = explicit || id || text || href || 'unknown';
    if (name.length > 50) name = name.substring(0, 50);
    send({ event: 'click', target: name, page: page(), domain: domain(), timestamp: ts() });
  });

  // Form submissions
  document.addEventListener('submit', function (evt) {
    const form = evt.target;
    if (!form || !form.tagName || form.tagName.toLowerCase() !== 'form') return;
    const id = form.id || '';
    const action = form.getAttribute('action') || '';
    const name = id || action || 'unknown_form';
    send({ event: 'form_submit', target: name, page: page(), domain: domain(), timestamp: ts() });
  });

  // Scroll depth milestones
  const milestones = { 25: false, 50: false, 75: false, 100: false };
  function onScroll() {
    try {
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) return;
      const pct = Math.round((window.scrollY / docHeight) * 100);
      for (const m of [25, 50, 75, 100]) {
        if (pct >= m && !milestones[m]) {
          milestones[m] = true;
          send({ event: 'scroll_depth', target: m + '%', page: page(), domain: domain(), timestamp: ts() });
        }
      }
    } catch (e) {}
  }
  document.addEventListener('scroll', onScroll, { passive: true });

  // RankFixer-specific scan events
  function wireRankFixerScan() {
    const runBtn = document.getElementById('runScan');
    if (!runBtn) return;
    runBtn.addEventListener('click', function () {
      send({ event: 'rankfixer_scan_executed', target: 'run_free_scan_click', page: page(), domain: domain(), timestamp: ts() });
    });
  }
  function wireRankFixerResult() {
    const results = document.getElementById('results');
    if (!results) return;
    const observer = new MutationObserver(function () {
      if (!results.classList.contains('hidden')) {
        send({ event: 'rankfixer_scan_executed', target: 'scan_results_visible', page: page(), domain: domain(), timestamp: ts() });
        observer.disconnect();
      }
    });
    observer.observe(results, { attributes: true, attributeFilter: ['class'] });
  }
  document.addEventListener('DOMContentLoaded', function () {
    wireRankFixerScan();
    wireRankFixerResult();
  });
})();
