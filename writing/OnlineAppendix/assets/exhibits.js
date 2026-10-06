/* The online appendix's exhibit groups (python/paper/onlineAppendix.py writes their HTML).
 *
 * A group holds the paper's figure(s) as inline SVG beside the tables that print their numbers. This script adds:
 * the calibration switch (common X / vector X_i), the table tabs, the value of a marker on hover or focus, a click
 * on a marker that brings up its table with the row highlighted (or opens the page that holds it), the markers of
 * a table row lit when the row is pointed at, a switch that marks the cells differing from the other calibration,
 * and the selection kept in the address (?g=&variant=&tab=&row=#anchor), so a link opens the same table and row.
 *
 * Progressive: the styles that hide inactive figures and panels key on html.oa-js, so without this script every
 * figure and table of a group is shown, one after another. `?oatest=1` runs a self-check and writes its result
 * into <pre id="oa-test">, for a headless browser to read.
 */
(function () {
  'use strict';
  var root = document.documentElement;
  root.classList.add('oa-js');
  var errors = [];
  window.addEventListener('error', function (e) { errors.push(String(e.message || e)); });

  function all(el, sel) { return Array.prototype.slice.call(el.querySelectorAll(sel)); }
  function norm(s) { return (s || '').replace(/\s+/g, ' ').trim(); }

  // ---- the tooltip: one for the page --------------------------------------------------------------------
  var tip = null;
  function showTip(node, m) {
    if (!tip) {
      tip = document.createElement('div');
      tip.className = 'oa-tip';
      tip.setAttribute('role', 'tooltip');
      document.body.appendChild(tip);
    }
    tip.textContent = '';
    var head = document.createElement('div');
    head.className = 'oa-tip-head';
    head.textContent = [m.label, m.series].filter(Boolean).join(' · ');
    var val = document.createElement('div');
    val.className = 'oa-tip-value';
    val.textContent = (m.panel ? m.panel + ': ' : '') + (m.text || String(m.value));
    tip.appendChild(head);
    tip.appendChild(val);
    if (m.href || m.tab) {
      var foot = document.createElement('div');
      foot.className = 'oa-tip-foot';
      foot.textContent = m.href ? 'Click to open the table that prints it' : 'Click to show its row in the table';
      tip.appendChild(foot);
    }
    tip.style.display = 'block';
    var r = node.getBoundingClientRect(), w = tip.offsetWidth, h = tip.offsetHeight;
    var x = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
    var y = r.top - h - 10;
    if (y < 8) { y = r.bottom + 10; }
    tip.style.left = x + 'px';
    tip.style.top = y + 'px';
  }
  function hideTip() { if (tip) { tip.style.display = 'none'; } }

  // ---- one exhibit group --------------------------------------------------------------------------------
  function Group(el) {
    this.el = el;
    this.id = el.getAttribute('data-group');
    this.variants = (el.getAttribute('data-variants') || 'commonX').split(/\s+/).filter(Boolean);
    this.variant = this.variants[0] || 'commonX';
    var firstTab = el.querySelector('.oa-tabs [role=tab]') || el.querySelector('.oa-panel');
    this.tab = firstTab ? firstTab.getAttribute('data-tab') : null;
    this.row = null;
    this.diff = false;
    this.marks = {};
    this.nodes = [];
    var data = el.querySelector('script.oa-marks');
    if (data) {
      try { this.marks = JSON.parse(data.textContent); } catch (e) { errors.push('marks of ' + this.id + ': ' + e); }
    }
    this.bind();
    this.fromUrl();
    this.apply(false);
  }

  Group.prototype.available = function (selector, attr, value) {
    // the variants in which a figure base or a table tab exists in this group
    return all(this.el, selector).filter(function (n) { return n.getAttribute(attr) === value; })
      .map(function (n) { return n.getAttribute('data-variant'); });
  };

  Group.prototype.pick = function (vs) { return vs.indexOf(this.variant) >= 0 ? this.variant : vs[0]; };

  Group.prototype.bind = function () {
    var g = this;
    all(g.el, '.oa-control [data-variant]').forEach(function (b) {
      b.addEventListener('click', function () { g.set({ variant: b.getAttribute('data-variant'), row: null }); });
    });
    var tabs = all(g.el, '.oa-tabs [role=tab]');
    tabs.forEach(function (b, k) {
      b.addEventListener('click', function () { g.set({ tab: b.getAttribute('data-tab'), row: null }); });
      b.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0;
        if (!d) { return; }
        e.preventDefault();
        var next = tabs[(k + d + tabs.length) % tabs.length];
        next.focus();
        g.set({ tab: next.getAttribute('data-tab'), row: null });
      });
    });
    var box = g.el.querySelector('.oa-diff input');
    if (box) { box.addEventListener('change', function () { g.diff = box.checked; g.apply(false); }); }
    all(g.el, '.oa-figure').forEach(function (fig) {
      var list = g.marks[fig.getAttribute('data-name')] || [];
      var svg = fig.querySelector('svg');
      if (!svg) { return; }
      list.forEach(function (m) {
        var node = svg.querySelector('[id="' + m.id + '"]');
        if (!node) { return; }
        node.classList.add('oa-mark');
        node.setAttribute('tabindex', '0');
        node.setAttribute('role', 'button');
        node.setAttribute('aria-label', [m.label, m.series, m.panel, m.text].filter(Boolean).join(', '));
        node.oaMark = m;
        g.nodes.push(node);
        node.addEventListener('mouseenter', function () { showTip(node, m); });
        node.addEventListener('focus', function () { showTip(node, m); });
        node.addEventListener('mouseleave', hideTip);
        node.addEventListener('blur', hideTip);
        node.addEventListener('click', function () { g.follow(m); });
        node.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); g.follow(m); }
        });
      });
    });
    all(g.el, '.oa-panel tr[data-row]').forEach(function (tr) {
      var panel = tr.closest('.oa-panel');
      tr.addEventListener('mouseenter', function () {
        g.brush(panel.getAttribute('data-tab'), panel.getAttribute('data-variant'), tr.getAttribute('data-row'));
      });
      tr.addEventListener('mouseleave', function () { g.brush(null); });
    });
  };

  Group.prototype.follow = function (m) {
    hideTip();
    if (m.href) { window.location.href = m.href; return; }
    if (!m.tab) { return; }
    this.set({ tab: m.tab, variant: m.variant || this.variant, row: m.row || null });
    var p = this.active();
    var hl = p && p.querySelector('tr.oa-row-hl');
    if (hl) { hl.scrollIntoView({ block: 'nearest', behavior: 'smooth' }); }
  };

  Group.prototype.brush = function (tab, variant, row) {
    var on = !!tab;
    this.nodes.forEach(function (n) {
      var m = n.oaMark;
      n.classList.toggle('oa-hl', on && m.tab === tab && (m.variant || 'commonX') === variant && m.row === row);
    });
    all(this.el, '.oa-svg').forEach(function (s) { s.classList.toggle('oa-brushing', on); });
  };

  Group.prototype.set = function (s) {
    for (var k in s) { if (Object.prototype.hasOwnProperty.call(s, k)) { this[k] = s[k]; } }
    this.apply(true);
  };

  Group.prototype.active = function () {
    var vs = this.available('.oa-panel', 'data-tab', this.tab);
    var v = this.pick(vs), t = this.tab;
    return all(this.el, '.oa-panel').filter(function (p) {
      return p.getAttribute('data-tab') === t && p.getAttribute('data-variant') === v;
    })[0] || null;
  };

  Group.prototype.apply = function (toUrl) {
    var g = this;
    all(g.el, '.oa-control [data-variant]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-variant') === g.variant));
    });
    all(g.el, '.oa-figure').forEach(function (f) {
      var vs = g.available('.oa-figure', 'data-base', f.getAttribute('data-base'));
      f.classList.toggle('is-active', f.getAttribute('data-variant') === g.pick(vs));
    });
    var act = g.active();
    all(g.el, '.oa-panel').forEach(function (p) { p.classList.toggle('is-active', p === act); });
    all(g.el, '.oa-text').forEach(function (d) {          // the exhibit's text follows its figure's variant or its panel
      var on;
      if (d.getAttribute('data-kind') === 'figure') {
        var fv = g.available('.oa-figure', 'data-base', d.getAttribute('data-tab'));
        on = d.getAttribute('data-variant') === g.pick(fv);
      } else {
        on = !!act && d.getAttribute('data-tab') === act.getAttribute('data-tab')
          && d.getAttribute('data-variant') === act.getAttribute('data-variant');
      }
      d.classList.toggle('is-active', on);
    });
    all(g.el, '.oa-tabs [role=tab]').forEach(function (b) {
      var on = b.getAttribute('data-tab') === g.tab;
      b.setAttribute('aria-selected', String(on));
      b.tabIndex = on ? 0 : -1;
    });
    all(g.el, 'tr.oa-row-hl').forEach(function (tr) { tr.classList.remove('oa-row-hl'); });
    if (act && g.row) {
      var tr = act.querySelector('tr[data-row="' + g.row + '"]');
      if (tr) { tr.classList.add('oa-row-hl'); }
    }
    g.compare(act);
    if (toUrl) { g.toUrl(); }
  };

  Group.prototype.compare = function (act) {
    var status = this.el.querySelector('.oa-diff-status');
    all(this.el, '.oa-diff-cell').forEach(function (c) { c.classList.remove('oa-diff-cell'); });
    if (!this.diff || !act) { if (status) { status.textContent = ''; } return; }
    var v = act.getAttribute('data-variant'), t = act.getAttribute('data-tab');
    var other = all(this.el, '.oa-panel').filter(function (p) {
      return p.getAttribute('data-tab') === t && p.getAttribute('data-variant') !== v;
    })[0];
    if (!other) { if (status) { status.textContent = 'This table has no counterpart under the other calibration.'; } return; }
    var ra = all(act, 'tbody tr'), rb = all(other, 'tbody tr');
    if (ra.length !== rb.length) {
      if (status) { status.textContent = 'The two calibrations print different rows here.'; }
      return;
    }
    var n = 0, total = 0;
    ra.forEach(function (tr, i) {
      var ca = all(tr, 'td, th'), cb = all(rb[i], 'td, th');
      ca.forEach(function (c, j) {
        total += 1;
        if (!cb[j] || norm(c.textContent) !== norm(cb[j].textContent)) { c.classList.add('oa-diff-cell'); n += 1; }
      });
    });
    if (status) {
      status.textContent = n ? n + ' of ' + total + ' cells differ from the other calibration.'
        : 'No cell differs from the other calibration.';
    }
  };

  Group.prototype.fromUrl = function () {
    var p = new URLSearchParams(window.location.search);
    var mine = p.get('g') ? p.get('g') === this.id : window.location.hash === '#' + this.id;
    if (!mine) { return; }
    var v = p.get('variant'), t = p.get('tab'), r = p.get('row');
    if (v && this.variants.indexOf(v) >= 0) { this.variant = v; }
    if (t && this.el.querySelector('.oa-panel[data-tab="' + t + '"]')) { this.tab = t; }
    if (r) { this.row = r; }
  };

  Group.prototype.toUrl = function () {
    if (!window.history || !window.history.replaceState) { return; }
    var p = new URLSearchParams();
    p.set('g', this.id);
    if (this.variants.length > 1) { p.set('variant', this.variant); }
    if (this.tab) { p.set('tab', this.tab); }
    if (this.row) { p.set('row', this.row); }
    window.history.replaceState(null, '', window.location.pathname + '?' + p.toString() + '#' + this.id);
  };

  // ---- start --------------------------------------------------------------------------------------------
  var groups = all(document, '.oa-group[data-group]').filter(function (el) { return el.querySelector('.oa-figure, .oa-panel'); })
    .map(function (el) { return new Group(el); });
  window.addEventListener('scroll', hideTip, { passive: true });

  if (/[?&]oatest=1\b/.test(window.location.search)) {
    var out = { groups: groups.length, marks: 0, followed: null, row: null, diff: null, errors: errors };
    groups.forEach(function (g) { out.marks += g.nodes.length; });
    var g0 = groups.filter(function (g) { return g.nodes.some(function (n) { return n.oaMark.tab && !n.oaMark.href; }); })[0];
    if (g0) {
      var node = g0.nodes.filter(function (n) { return n.oaMark.tab && !n.oaMark.href; })[0];
      node.dispatchEvent(new MouseEvent('mouseenter'));
      out.tip = tip ? tip.textContent : null;
      node.dispatchEvent(new MouseEvent('click'));
      out.followed = node.oaMark.id;
      var act = g0.active();
      var hl = act && act.querySelector('tr.oa-row-hl');
      out.row = hl ? hl.getAttribute('data-row') : null;
    }
    var g1 = groups.filter(function (g) { return g.variants.length > 1 && g.el.querySelector('.oa-diff input'); })[0];
    if (g1) {
      g1.set({ variant: g1.variants[1] });
      g1.diff = true;
      g1.apply(false);
      var st = g1.el.querySelector('.oa-diff-status');
      out.diff = { group: g1.id, status: st ? st.textContent : null };
    }
    out.viewport = window.innerWidth;
    out.page = document.documentElement.scrollWidth;
    out.wide = all(document, 'main *').filter(function (n) {
      return n.getBoundingClientRect().right > window.innerWidth + 1;
    }).slice(0, 4).map(function (n) {
      return n.tagName + '.' + String(n.className && n.className.baseVal !== undefined ? n.className.baseVal : n.className)
        .split(' ').slice(0, 2).join('.') + ':' + Math.round(n.getBoundingClientRect().width);
    });
    var pre = document.createElement('pre');
    pre.id = 'oa-test';
    pre.textContent = JSON.stringify(out);
    document.body.appendChild(pre);
  }
})();
