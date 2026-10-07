(function () {
  var root = document.documentElement;

  function stored() {
    try { return localStorage.getItem('theme'); } catch (e) { return null; }
  }
  function save(v) {
    try { localStorage.setItem('theme', v); } catch (e) { /* storage unavailable */ }
  }
  function effective() {
    var t = root.getAttribute('data-theme');
    if (t) return t;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function sync() {
    var dark = effective() === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      btn.setAttribute('aria-pressed', String(dark));
      btn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      var use = btn.querySelector('use');
      if (use) use.setAttribute('href', use.getAttribute('href').split('#')[0] + (dark ? '#sun' : '#moon'));
    });
  }

  var saved = stored();
  if (saved === 'light' || saved === 'dark') root.setAttribute('data-theme', saved);

  document.addEventListener('click', function (e) {
    var t = e.target.closest('[data-theme-toggle]');
    if (t) {
      var next = effective() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      save(next);
      sync();
    }
    if (e.target.closest('[data-print]')) window.print();

    // Back button: return to the previous page (and its scroll position) when it is on this site.
    var back = e.target.closest('[data-back]');
    if (back && !e.metaKey && !e.ctrlKey && !e.shiftKey && history.length > 1) {
      try {
        if (document.referrer && new URL(document.referrer).origin === location.origin) {
          e.preventDefault();
          history.back();
        }
      } catch (err) { /* fall back to the normal link */ }
    }
  });

  if (window.matchMedia) {
    var mq = window.matchMedia('(prefers-color-scheme: dark)');
    (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(sync);
  }
  document.addEventListener('DOMContentLoaded', sync);
})();
