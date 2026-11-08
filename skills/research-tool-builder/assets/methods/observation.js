/* Observation method module: for products the tool cannot see inside (a live website, a native app, something
   physical) and for conversations (interviews, field visits). Two ways to run it, chosen by the setup:
   - moderator-logged, on a moderator copy: the device stays with the moderator, who marks moments, ticks
     observation codes and records how each task ended;
   - participant-run, on a participant copy (or with "observer": "participant"): the participant opens the product,
     does the task there and comes back; the tool records the time and how long they were away.
   See references/methods/observation.md. */
(function () {
  'use strict';
  var el = Shell.el;
  var LEVELS = [
    { id: 'completed', label: 'Completed', success: true, friction: 'none' },
    { id: 'with-help', label: 'Completed with help', success: true, friction: 'minor' },
    { id: 'failed', label: 'Did not complete', success: false, friction: 'major' },
    { id: 'not-attempted', label: 'Not attempted', success: null }
  ];
  var tick = null;     // ponytail: one clock, because only one task is ever on screen
  var current = null;  // the study's levels, kept from validate for the task screen

  function levelsOf(task) { return task.levels === false ? [] : (current || LEVELS); }
  function clock(ms) { var s = Math.floor(ms / 1000); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); }

  Shell.register({
    id: 'observation', version: '1.0.0', label: 'Observation',
    // The moderator leads on a moderator copy unless the study says the participant runs it.
    moderatorLed: function (content) { return content.observer !== 'participant'; },
    steady: true,
    giveUpLabel: 'The participant gave up',
    finishLabel: function (task, led) { return led ? (task.levels === false ? 'Next topic' : 'End task') : "I've finished"; },
    validate: function (content) {
      var errors = [], warnings = [], seen = {};
      current = content.levels || null;
      (content.levels || []).forEach(function (l) {
        if (!l.id || !l.label) errors.push('Every outcome level needs an id and a label.'); else if (seen[l.id]) errors.push('Outcome level "' + l.id + '" is used twice.'); else seen[l.id] = 1;
        if ([true, false, null].indexOf(l.success) < 0) errors.push('Outcome level "' + l.id + '" needs "success": true, false or null.');
        if (l.friction != null && ['none', 'minor', 'major'].indexOf(l.friction) < 0) errors.push('Outcome level "' + l.id + '" has an unknown friction "' + l.friction + '".');
      });
      if (content.observer && ['moderator', 'participant'].indexOf(content.observer) < 0) errors.push('"observer" must be "moderator" or "participant".');
      content.tasks.forEach(function (t) {
        if (t.link && !/^https:\/\//.test(t.link.url || '')) errors.push(t.id + ': "link.url" must be a full https:// address.');
        if (!t.scenario && !t.prompt) errors.push(t.id + ': add the task or topic wording as "scenario".');
      });
      if (!(content.codes || []).length) warnings.push('No observation codes: moderators can only mark moments and write notes.');
      return { errors: errors, warnings: warnings };
    },
    start: function (task, plan, ctx) { return { led: ctx.led(), level: null, codes: {}, markers: 0, opened: false }; },
    canFinish: function (task, st) {
      if (st.led && levelsOf(task).length && !st.level) return { ok: false, message: 'Choose how the task ended.' };
      return { ok: true };
    },
    outcome: function (task, st, reason) {
      if (tick) { clearInterval(tick); tick = null; }
      if (!st.led) return { success: null, loggedBy: 'participant', opened: st.opened };
      var lv = levelsOf(task).filter(function (l) { return l.id === st.level; })[0];
      var out = { success: reason === 'gave-up' ? false : lv ? lv.success : null, loggedBy: 'moderator', level: reason === 'gave-up' ? 'gave-up' : lv ? lv.id : null,
        codes: Object.keys(st.codes).filter(function (k) { return st.codes[k]; }), markers: st.markers };
      var fr = reason === 'gave-up' ? 'major' : lv && lv.friction; if (fr) out.friction = fr;
      return out;
    },
    render: function (task, st, ctx) {
      if (!st.led) {
        return el('div', { class: 'ob-wrap' },
          task.link ? el('p', {}, el('a', { class: 'btn primary ob-open', href: task.link.url, target: '_blank', rel: 'noopener noreferrer', 'data-k': 'open-product',
            onclick: function () { st.opened = true; ctx.log('open-product', { url: task.link.url }); ctx.save(); } }, task.link.label || 'Open it in a new tab')) : null,
          el('p', { class: 'body-copy', text: task.link ? 'Do the task there. When you have finished, come back to this page and press "I\'ve finished".' : 'Do the task as you were asked. When you have finished, come back to this page and press "I\'ve finished".' }));
      }
      var began = Date.now(), shown = el('b', { class: 'ob-clock', 'aria-hidden': 'true', text: '0:00' }), count = el('span', { class: 'muted', text: '' });
      if (tick) clearInterval(tick);
      tick = setInterval(function () { shown.textContent = clock(Date.now() - began); }, 1000);
      var note = el('input', { class: 'input', 'data-k': 'marker', 'aria-label': 'What happened (optional)', placeholder: 'What happened (optional)' });
      var mark = function () {
        var label = note.value.trim(); ctx.log('marker', { label: label }); st.markers++; note.value = '';
        count.textContent = st.markers + ' marked'; ctx.announce('Moment marked.'); ctx.save(); note.focus();
      };
      note.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); e.stopPropagation(); mark(); } });
      var codes = ctx.codes(), levels = levelsOf(task);
      return el('div', { class: 'ob-wrap' },
        el('p', { class: 'muted' }, 'For the moderator. Time on this task: ', shown),
        el('div', { class: 'ob-row' }, note, el('button', { type: 'button', class: 'btn', 'data-k': 'mark', onclick: mark }, 'Mark this moment'), count),
        codes.length ? el('fieldset', { class: 'scale' }, el('legend', { text: 'Observed' }), el('div', { class: 'ob-codes' }, codes.map(function (c) {
          return el('label', { class: 'check' }, el('input', { type: 'checkbox', 'data-k': 'code-' + c.id, checked: !!st.codes[c.id], onchange: function (e) {
            st.codes[c.id] = e.target.checked; ctx.log('code', { code: c.id, on: e.target.checked }); ctx.save();
          } }), el('span', { text: c.label }));
        }))) : null,
        levels.length ? el('fieldset', { class: 'scale' }, el('legend', { text: 'How did the task end?' }), el('div', { class: 'ob-levels' }, levels.map(function (l, i) {
          return el('label', { class: 'check' }, el('input', { type: 'radio', name: 'level', 'data-k': 'level-' + l.id, checked: st.level === l.id, onchange: function () { st.level = l.id; ctx.update(); } }), el('span', { text: l.label }));
        }))) : null);
    },
    figures: function (task, runs) {
      var n = {}; runs.forEach(function (r) { var l = r.outcome && r.outcome.level; if (l) n[l] = (n[l] || 0) + 1; });
      return Object.keys(n).map(function (k) { var l = (current || LEVELS).filter(function (x) { return x.id === k; })[0]; return { label: l ? l.label.toLowerCase() : k, value: String(n[k]) }; });
    }
  });
})();
