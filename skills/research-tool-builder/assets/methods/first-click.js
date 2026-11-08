/* First-click method module: where do people click first in a prototype?
   The prototype is a self-contained HTML page in the study content ("prototype"). It runs in a sandboxed frame
   at a named device size, scaled to fit. A small bridge inside the frame reports clicks, routes and searches;
   the tool ignores any message without this session's code. See references/methods/first-click.md. */
(function () {
  'use strict';
  var el = Shell.el;
  var DEVICES = { desktop: [1440, 1024], tablet: [768, 1024], mobile: [390, 844] };
  var CONTENT = null, listener = null;

  function bridge(nonce, start) {
    // Runs inside the prototype. Plain ES5, no access to the tool.
    return '<script>(function(){var N=' + JSON.stringify(nonce) + ',S=' + JSON.stringify(start || '') + ';' +
      'function send(m){m.src="rt-proto";m.nonce=N;parent.postMessage(m,"*");}' +
      'if(S&&!location.hash)location.hash=S;' +
      'document.addEventListener("click",function(e){var t=e.target.closest("a,button,[data-zone],input,select,[role=button],[role=link]")||e.target;' +
      'var z=e.target.closest("[data-zone]"),a=e.target.closest("a");var h=a?a.getAttribute("href"):null;' +
      'if(a&&h&&h.charAt(0)!=="#")e.preventDefault();' +
      'send({type:"click",zone:z?z.getAttribute("data-zone"):null,href:h,label:((t.innerText||t.value||t.getAttribute("aria-label")||"")+"").trim().slice(0,80),x:Math.round(e.clientX),y:Math.round(e.clientY)});},true);' +
      'document.addEventListener("submit",function(e){e.preventDefault();var q=e.target.querySelector("input[type=search],input[name=q],input");send({type:"search",query:q?(q.value||"").slice(0,80):""});},true);' +
      'function route(){send({type:"route",path:location.hash||"/"});}' +
      'addEventListener("hashchange",route);' +
      'if(document.readyState==="complete"){send({type:"ready"});route();}else addEventListener("load",function(){send({type:"ready"});route();});' +
      '})();<\/script>';
  }
  function withBridge(html, nonce, start) {
    var b = bridge(nonce, start);
    return /<\/body>/i.test(html) ? html.replace(/<\/body>/i, b + '</body>') : html + b;
  }
  function classify(task, click) {
    var t = task.targets || {}, hit = function (list) { return (list || []).some(function (x) { return (x.zone && x.zone === click.zone) || (x.href && x.href === click.href); }); };
    if (!(t.main || []).length && !(t.acceptable || []).length) return 'unclassified';
    return hit(t.main) ? 'main' : hit(t.acceptable) ? 'acceptable' : 'wrong';
  }

  Shell.register({
    id: 'first-click', version: '1.0.0', label: 'First click', steady: true,
    finishButton: function (task) { return task.endOn === 'finish'; },
    tour: [
      { title: 'A working prototype', body: 'You will see a version of a website. It is not finished, so not everything works. That is expected.' },
      { title: 'Click where you would start', body: 'Read the task, press Begin, then click where you would go first to do it. Do what you would really do.' }
    ],
    validate: function (content) {
      CONTENT = content;
      var errors = [], warnings = [];
      if (!content.prototype || typeof content.prototype !== 'string') errors.push('Add the prototype as a self-contained HTML page in "prototype".');
      else {
        if (/<script[^>]+src=|<link[^>]+href=["']https?:|src=["']https?:/i.test(content.prototype)) errors.push('The prototype loads files from the internet. Inline its scripts, styles and images so it works offline.');
        if (content.prototype.length > 3000000) warnings.push('The prototype is over 3 MB; compress its images.');
      }
      content.tasks.forEach(function (t) {
        var id = t.id || '?';
        if (t.device && !DEVICES[t.device]) errors.push(id + ': device must be desktop, tablet or mobile.');
        if (t.endOn && ['first-click', 'finish'].indexOf(t.endOn) < 0) errors.push(id + ': endOn must be "first-click" or "finish".');
        var tg = t.targets || {};
        ['main', 'acceptable'].forEach(function (k) { (tg[k] || []).forEach(function (x) { if (!x.zone && !x.href) errors.push(id + ': every ' + k + ' target needs a zone or an href.'); }); });
        if (!(tg.main || []).length) warnings.push(id + ': no main target, so first clicks will not be scored.');
        (tg.main || []).concat(tg.acceptable || []).forEach(function (x) {
          if (content.prototype && x.zone && content.prototype.indexOf('data-zone="' + x.zone + '"') < 0) warnings.push(id + ': no element in the prototype has data-zone="' + x.zone + '".');
        });
      });
      return { errors: errors, warnings: warnings };
    },
    start: function (task) { return { first: null, clicks: 0, lastRoute: null, nonce: Math.random().toString(36).slice(2) + Date.now().toString(36) }; },
    canFinish: function (task, st) { return st.first ? { ok: true } : { ok: false, message: 'Click in the prototype first.' }; },
    outcome: function (task, st, reason) {
      if (listener) { window.removeEventListener('message', listener); listener = null; }
      var tier = st.first ? classify(task, st.first) : null;
      return {
        success: reason === 'gave-up' ? false : tier === 'main' || tier === 'acceptable' ? true : tier === 'wrong' ? false : null,
        tier: reason === 'gave-up' ? null : tier, firstTarget: st.first ? (st.first.zone || st.first.href || st.first.label) : null,
        firstInteractionMs: st.first ? st.first.t : null, endHref: st.lastRoute, clicks: st.clicks
      };
    },
    figures: function (task, runs) {
      var main = runs.filter(function (r) { return r.outcome.tier === 'main'; }).length;
      var t = runs.map(function (r) { return r.outcome.firstInteractionMs; }).filter(function (x) { return x != null; }).sort(function (a, b) { return a - b; });
      return runs.length ? [{ label: 'main target first', value: main + ' of ' + runs.length }, { label: 'median time to first click', value: t.length ? ((t.length % 2 ? t[t.length >> 1] : (t[t.length / 2 - 1] + t[t.length / 2]) / 2) / 1000).toFixed(1) + 's' : '–' }] : [];
    },
    render: function (task, st, ctx) {
      var device = task.device || (CONTENT && CONTENT.device) || 'desktop', size = DEVICES[device] || DEVICES.desktop;
      var endOn = task.endOn || 'first-click';
      var frame = el('iframe', { title: 'Prototype', sandbox: 'allow-scripts', referrerpolicy: 'no-referrer', style: 'width:' + size[0] + 'px;height:' + size[1] + 'px' });
      frame.srcdoc = withBridge((CONTENT && CONTENT.prototype) || '<p>No prototype.</p>', st.nonce, task.start);
      var box = el('div', { class: 'fc-box' }, frame);
      var fit = function () {
        if (!box.isConnected || !box.parentElement.clientWidth) return; // the task has ended or the stage is hidden
        var w = box.parentElement.clientWidth, scale = Math.min(1, w / size[0]);
        frame.style.transform = 'scale(' + scale + ')'; box.style.height = Math.round(size[1] * scale) + 'px'; box.style.width = Math.round(size[0] * scale) + 'px';
        ctx.setRun({ device: device, scale: Math.round(scale * 100) / 100 });
      };
      if (listener) window.removeEventListener('message', listener);
      listener = function (e) {
        var m = e.data;
        if (e.source !== frame.contentWindow || !m || m.src !== 'rt-proto' || m.nonce !== st.nonce) return;
        var data = {}; ['zone', 'href', 'label', 'x', 'y', 'path', 'query'].forEach(function (k) { if (m[k] != null) data[k] = m[k]; });
        if (m.type === 'route') st.lastRoute = m.path;
        if (m.type === 'click') {
          st.clicks++;
          if (!st.first) { st.first = { zone: m.zone, href: m.href, label: m.label, t: Date.now() - st.begun }; data.first = true; }
        }
        ctx.log(m.type === 'ready' ? 'frame-ready' : m.type, data); ctx.save();
        if (m.type === 'click' && data.first && endOn === 'first-click') ctx.finish('target');
        else if (m.type === 'click' && data.first) ctx.update();
      };
      window.addEventListener('message', listener);
      st.begun = Date.now();
      var stage = el('div', { class: 'fc-stage', 'data-device': device }, box);
      requestAnimationFrame(fit);
      if (window.ResizeObserver) new ResizeObserver(fit).observe(stage);
      return el('div', { class: 'fc-wrap' },
        el('p', { class: 'muted fc-hint', text: endOn === 'first-click' ? 'Click where you would go first. The task ends with your first click.' : 'Click where you would go, then press "I\'ve finished".' }),
        stage);
    }
  });
})();
