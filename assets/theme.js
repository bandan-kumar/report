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

  // Jump bar: mark the link for the section currently in view.
  document.addEventListener('DOMContentLoaded', function () {
    var links = [].slice.call(document.querySelectorAll('.jump a[href^="#"]'));
    if (!links.length) return;
    var bar = document.querySelector('.jump .wrap');
    var sections = links.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    var current = -1, queued = false;

    /* Scroll only the link bar sideways. scrollIntoView can also move the page, which fights the reader. */
    function centerInBar(a) {
      if (!bar || bar.scrollWidth <= bar.clientWidth) return;
      var r = a.getBoundingClientRect(), b = bar.getBoundingClientRect();
      var delta = (r.left + r.width / 2) - (b.left + b.width / 2);
      if (Math.abs(delta) > 4) bar.scrollTo({ left: bar.scrollLeft + delta, behavior: 'smooth' });
    }

    function update() {
      queued = false;
      var line = window.innerHeight * 0.375, active = -1;
      sections.forEach(function (el, i) { if (el && el.getBoundingClientRect().top <= line) active = i; });
      if (active === current) return;
      current = active;
      links.forEach(function (a, i) {
        if (i === active) { a.setAttribute('aria-current', 'true'); centerInBar(a); }
        else a.removeAttribute('aria-current');
      });
    }

    function schedule() { if (!queued) { queued = true; setTimeout(update, 60); } }
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', schedule);
    update();
  });
})();
