/* Presenter mode: shows each section of a report page as a full-screen slide.
   Right/Down/PageDown/Space/Enter go forward, Left/Up/PageUp/Backspace go back,
   Home/End jump, F toggles full screen, Esc leaves. Press P on the page to start. */
(function () {
  'use strict';
  var openBtn = document.querySelector('[data-present]');
  if (!openBtn) return;

  var deck, stage, countEl, fillEl, liveEl, prevBtn, nextBtn;
  var slides = [];
  var index = 0;
  var scrollBefore = 0;
  var NEXT = { ArrowRight: 1, ArrowDown: 1, PageDown: 1, ' ': 1, Enter: 1 };
  var PREV = { ArrowLeft: 1, ArrowUp: 1, PageUp: 1, Backspace: 1 };

  function isOpen() { return deck && !deck.hidden; }

  /* A copy of a node that is safe to show a second time (no duplicate ids). */
  function copy(node) {
    var c = node.cloneNode(true);
    c.removeAttribute('id');
    [].forEach.call(c.querySelectorAll('[id]'), function (e) { e.removeAttribute('id'); });
    [].forEach.call(c.querySelectorAll('[loading]'), function (e) { e.removeAttribute('loading'); });
    return c;
  }

  /* One slide for the title banner and one per section. A section marked data-slides
     is split further, one slide for every element matching that selector. */
  function collect() {
    var list = [];
    var hero = document.querySelector('.report-hero');
    if (hero) list.push({ el: copy(hero), hero: true, source: hero });
    [].forEach.call(document.querySelectorAll('main > .block'), function (block) {
      var selector = block.getAttribute('data-slides');
      if (selector) {
        var title = block.querySelector('h2');
        var sub = block.querySelector(':scope > .sub');
        [].forEach.call(block.querySelectorAll(selector), function (item) {
          var wrap = document.createElement('section');
          wrap.className = 'block deck-slide';
          if (title) wrap.appendChild(copy(title));
          if (sub) wrap.appendChild(copy(sub));
          var holder = document.createElement('div');
          holder.className = 'slide-item';
          holder.appendChild(copy(item));
          wrap.appendChild(holder);
          list.push({ el: wrap, source: item });
        });
      } else {
        var c = copy(block);
        c.classList.add('deck-slide');
        list.push({ el: c, source: block });
      }
    });
    return list;
  }

  function icon(name) {
    return '<svg class="icon" aria-hidden="true"><use href="#' + name + '"/></svg>';
  }

  function themeIcon() {
    var root = document.documentElement;
    var t = root.getAttribute('data-theme');
    var dark = t ? t === 'dark' : window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    return dark ? 'sun' : 'moon';
  }

  function build() {
    slides = collect();
    deck = document.createElement('div');
    deck.className = 'deck';
    deck.id = 'deck';
    deck.hidden = true;
    deck.tabIndex = -1;
    deck.setAttribute('role', 'dialog');
    deck.setAttribute('aria-modal', 'true');
    deck.setAttribute('aria-label', 'Presentation');
    deck.innerHTML =
      '<div class="deck-progress"><i></i></div>' +
      '<div class="deck-stage"></div>' +
      '<div class="deck-bar">' +
        '<button type="button" data-deck="prev" aria-label="Previous slide">' + icon('chevron-left') + '</button>' +
        '<span class="deck-count" aria-hidden="true"></span>' +
        '<button type="button" data-deck="next" aria-label="Next slide">' + icon('chevron-right') + '</button>' +
        '<button type="button" data-theme-toggle aria-label="Switch theme">' + icon(themeIcon()) + '</button>' +
        '<button type="button" data-deck="fullscreen" aria-label="Toggle full screen">' + icon('maximize') + '</button>' +
        '<button type="button" data-deck="exit" aria-label="Exit presentation">' + icon('x') + '</button>' +
      '</div>' +
      '<p class="sr-only" aria-live="polite"></p>';
    document.body.appendChild(deck);
    stage = deck.querySelector('.deck-stage');
    countEl = deck.querySelector('.deck-count');
    fillEl = deck.querySelector('.deck-progress i');
    liveEl = deck.querySelector('[aria-live]');
    prevBtn = deck.querySelector('[data-deck="prev"]');
    nextBtn = deck.querySelector('[data-deck="next"]');

    deck.addEventListener('click', function (e) {
      var btn = e.target.closest('[data-deck]');
      if (btn) {
        var a = btn.getAttribute('data-deck');
        if (a === 'prev') go(index - 1);
        else if (a === 'next') go(index + 1);
        else if (a === 'fullscreen') toggleFullscreen();
        else if (a === 'exit') close();
        return;
      }
      if (e.target.closest('[data-theme-toggle]')) { setTimeout(function () { fit(slides[index]); }, 0); return; }
      if (e.target.closest('a')) { e.preventDefault(); return; }
      var inStage = e.target.closest('.deck-stage');
      if (inStage) { go(e.clientX > window.innerWidth * 0.3 ? index + 1 : index - 1); }
    });

    var startX = null;
    deck.addEventListener('touchstart', function (e) { startX = e.touches[0].clientX; }, { passive: true });
    deck.addEventListener('touchend', function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      startX = null;
      if (Math.abs(dx) > 50) go(dx < 0 ? index + 1 : index - 1);
    }, { passive: true });
  }

  /* Scale a slide up or down so it fits the screen. If it still does not fit, let the stage scroll. */
  function fit(slide) {
    stage.classList.remove('scroll');
    if (!slide || slide.hero) { if (slide) slide.el.style.zoom = ''; return; }
    var el = slide.el;
    el.style.zoom = '1';
    var cs = getComputedStyle(stage);
    var availH = stage.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    var availW = stage.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var scale = Math.min(availH / el.offsetHeight, availW / el.offsetWidth, 1.3);
    var floor = window.innerWidth >= 640 ? 0.2 : 0.45;
    var applied = Math.max(floor, Math.floor(scale * 100) / 100);
    el.style.zoom = String(applied);
    if (el.offsetHeight * applied > availH + 2) stage.classList.add('scroll');
  }

  function go(i, force) {
    var next = Math.max(0, Math.min(slides.length - 1, i));
    if (next === index && !force) return;     // already at the first or last slide: nothing to redraw
    index = next;
    var slide = slides[index];
    stage.className = 'deck-stage' + (slide.hero ? ' is-hero' : '');
    stage.scrollTop = 0;
    stage.replaceChildren(slide.el);
    fit(slide);
    countEl.textContent = (index + 1) + ' / ' + slides.length;
    fillEl.style.width = ((index + 1) / slides.length * 100) + '%';
    liveEl.textContent = 'Slide ' + (index + 1) + ' of ' + slides.length;
    prevBtn.setAttribute('aria-disabled', String(index === 0));
    nextBtn.setAttribute('aria-disabled', String(index === slides.length - 1));
  }

  /* Start on the section that fills most of the screen, so you begin from where you are reading. */
  function startIndex() {
    var vh = window.innerHeight, best = 0, bestVisible = -1;
    slides.forEach(function (s, i) {
      if (!s.source) return;
      var r = s.source.getBoundingClientRect();
      var visible = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      if (visible > 0 && visible >= bestVisible) { best = i; bestVisible = visible; }
    });
    return best;
  }

  function open() {
    if (!deck) build();
    scrollBefore = window.scrollY;
    var start = startIndex();               // measure before the page is locked
    document.documentElement.classList.add('presenting');
    deck.hidden = false;
    go(start, true);
    deck.focus();
  }

  function close() {
    if (!isOpen()) return;
    if (document.fullscreenElement || document.webkitFullscreenElement) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    }
    deck.hidden = true;
    document.documentElement.classList.remove('presenting');
    window.scrollTo({ top: scrollBefore, left: 0, behavior: 'instant' });
    openBtn.focus({ preventScroll: true });
  }

  function toggleFullscreen() {
    if (document.fullscreenElement || document.webkitFullscreenElement) {
      (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    } else {
      var req = deck.requestFullscreen || deck.webkitRequestFullscreen;
      if (req) req.call(deck);
    }
  }

  openBtn.addEventListener('click', open);

  document.addEventListener('keydown', function (e) {
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target && e.target.tagName) || '';
    if (!isOpen()) {
      if ((e.key === 'p' || e.key === 'P') && !/INPUT|TEXTAREA|SELECT/.test(tag)) { e.preventDefault(); open(); }
      return;
    }
    var onButton = tag === 'BUTTON' && (e.key === 'Enter' || e.key === ' ');
    if (onButton) return;           // let a focused button do its own job
    if (NEXT[e.key]) { e.preventDefault(); go(index + 1); }
    else if (PREV[e.key]) { e.preventDefault(); go(index - 1); }
    else if (e.key === 'Home') { e.preventDefault(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); go(slides.length - 1); }
    else if (e.key === 'Escape') { e.preventDefault(); close(); }
    else if (e.key === 'f' || e.key === 'F') { e.preventDefault(); toggleFullscreen(); }
  });

  function refit() { if (isOpen()) fit(slides[index]); }
  window.addEventListener('resize', refit);
  document.addEventListener('fullscreenchange', function () { setTimeout(refit, 50); });
  document.addEventListener('webkitfullscreenchange', function () { setTimeout(refit, 50); });
})();
