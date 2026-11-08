/* Stimulus method module: show material (one or more images or passages), optionally for a fixed time,
   then ask the task's own questions on the shell's rating step. Covers five-second tests, preference tests,
   concept tests, desirability (reaction words) and comprehension tests. See references/methods/stimulus.md. */
(function () {
  'use strict';
  var el = Shell.el;
  var timer = null; // ponytail: one timer, because only one task is ever on screen

  function ids(task) { return (task.stimuli || []).map(function (x) { return x.id; }); }

  Shell.register({
    id: 'stimulus', version: '1.0.0', label: 'Stimulus',
    steady: true,
    finishButton: function (task) { return !task.exposureMs; },
    finishLabel: 'Continue',
    validate: function (content) {
      var errors = [], warnings = [];
      content.tasks.forEach(function (t) {
        var id = t.id || '?', seen = {};
        (t.stimuli || []).forEach(function (x) {
          if (!x.id) errors.push(id + ': every stimulus needs an id.'); else if (seen[x.id]) errors.push(id + ': stimulus id "' + x.id + '" is used twice.'); else seen[x.id] = 1;
          if (!x.image && !x.text) errors.push(id + ': stimulus "' + x.id + '" needs an image or text.');
          if (x.image && !/^data:image\//.test(x.image)) errors.push(id + ': stimulus "' + x.id + '" must embed its image as a data: URI; the tool loads nothing from the internet.');
          if (x.image && !x.alt) errors.push(id + ': stimulus "' + x.id + '" needs alt text describing the image.');
        });
        if (!(t.stimuli || []).length) errors.push(id + ': add at least one stimulus.');
        if (t.exposureMs != null && !(t.exposureMs >= 1000)) errors.push(id + ': "exposureMs" must be at least 1000 (one second).');
        if (t.exposureMs && !(t.questions || []).length) warnings.push(id + ': a timed task with no questions records nothing but the time.');
        (t.questions || []).forEach(function (q) {
          if (q.correct != null && ['choice', 'choices'].indexOf(q.kind) < 0) errors.push(id + ': only choice questions can have a "correct" answer (question "' + q.id + '").');
        });
        if ((t.stimuli || []).length > 1 && t.shuffle === false) warnings.push(id + ': several options in a fixed order; the first shown tends to be preferred.');
      });
      return { errors: errors, warnings: warnings };
    },
    itemOrder: function (task, rand) { var o = ids(task); return o.length > 1 && task.shuffle !== false ? Shell.shuffle(o, rand) : null; },
    start: function (task, plan, ctx) {
      return { order: (plan.itemOrder && plan.itemOrder[task.id]) || ids(task), shownAt: Date.now() };
    },
    outcome: function (task, st) {
      if (timer) { clearTimeout(timer); timer = null; }
      return { success: null, shown: st.order, exposedMs: Date.now() - st.shownAt };
    },
    render: function (task, st, ctx) {
      var byId = {}; (task.stimuli || []).forEach(function (x) { byId[x.id] = x; });
      var many = st.order.length > 1;
      ctx.log('stimulus-shown', { order: st.order });
      if (task.exposureMs) {
        if (timer) clearTimeout(timer);
        var left = task.exposureMs - (Date.now() - st.shownAt);
        timer = setTimeout(function () { timer = null; ctx.log('stimulus-hidden'); ctx.announce('Time is up.'); ctx.finish('timed'); }, Math.max(0, left));
      }
      return el('div', { class: 'st-grid' + (many ? ' many' : '') }, st.order.map(function (sid, i) {
        var x = byId[sid];
        return el('figure', { class: 'st-item' },
          x.image ? el('img', { src: x.image, alt: x.alt }) : el('div', { class: 'st-text body-copy', text: x.text }),
          many || x.label ? el('figcaption', { text: x.label || 'Option ' + (i + 1) }) : null);
      }));
    },
    figures: function (task, runs) {
      var t = runs.map(function (r) { return r.outcome && r.outcome.exposedMs; }).filter(Boolean).sort(function (a, b) { return a - b; });
      return task.exposureMs || !t.length ? [] : [{ label: 'median viewing', value: Math.round(t[Math.floor(t.length / 2)] / 1000) + ' s' }];
    }
  });
})();
