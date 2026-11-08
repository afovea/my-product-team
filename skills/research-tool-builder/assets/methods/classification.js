/* Classification method module: put each item into one of the study's categories, one item at a time.
   Used to test whether a set of categories is clear enough that different people classify the same way.
   See references/methods/classification.md. */
(function () {
  'use strict';
  var el = Shell.el;
  var NONE = 'NONE';

  function itemOf(task, id) { return task.items.filter(function (x) { return x.id === id; })[0]; }
  function answered(task, a) { return a && a.choice && (a.choice !== NONE || (a.note || '').trim()); }
  function tick(st) { var now = Date.now(), id = st.order[st.i]; st.itemMs[id] = (st.itemMs[id] || 0) + (now - st.enteredAt); st.enteredAt = now; }

  Shell.register({
    id: 'classification', version: '1.0.0', label: 'Classification',
    tour: [
      { title: 'One item at a time', body: 'You will see a series of items. For each one, choose the category it belongs in, using the descriptions given.' },
      { title: 'Not sure? Say so', body: 'Tick "Unsure" when you are guessing, and "Unfamiliar" if you do not know what the item means. If nothing fits, choose "None of these" and say why.' }
    ],
    validate: function (content) {
      var errors = [], warnings = [];
      content.tasks.forEach(function (t) {
        var id = t.id || '?', codes = {}, items = {};
        (t.categories || []).forEach(function (c) {
          if (!c.code || !c.label) errors.push(id + ': every category needs a code and a label.');
          if (c.code === NONE) errors.push(id + ': the code NONE is reserved for "None of these".');
          if (codes[c.code]) errors.push(id + ': category code "' + c.code + '" is used twice.'); codes[c.code] = 1;
          if (!c.definition) warnings.push(id + ': category "' + c.label + '" has no description; raters will guess from the name.');
        });
        if ((t.categories || []).length < 2) errors.push(id + ': add at least two categories.');
        (t.items || []).forEach(function (it) { if (!it.id || !it.text) errors.push(id + ': every item needs an id and text.'); if (items[it.id]) errors.push(id + ': item id "' + it.id + '" is used twice.'); items[it.id] = 1; });
        if ((t.items || []).length < 2) errors.push(id + ': add at least two items.');
        if ((t.items || []).length > 60) warnings.push(id + ': more than 60 items is tiring; consider splitting the set.');
      });
      return { errors: errors, warnings: warnings };
    },
    itemOrder: function (task, rand) { var ids = task.items.map(function (x) { return x.id; }); return task.shuffle === false ? ids : Shell.shuffle(ids, rand); },
    start: function (task, plan) {
      var order = (plan.itemOrder && plan.itemOrder[task.id]) || task.items.map(function (x) { return x.id; });
      return { order: order, i: 0, answers: {}, itemMs: {}, enteredAt: Date.now() };
    },
    canFinish: function (task, st) {
      var left = st.order.filter(function (id) { return !answered(task, st.answers[id]); }).length;
      if (left) return { ok: false, message: left + ' item' + (left === 1 ? '' : 's') + ' still to classify.' };
      return { ok: true };
    },
    outcome: function (task, st) {
      tick(st);
      return { success: null, answers: JSON.parse(JSON.stringify(st.answers)), itemMs: st.itemMs };
    },
    figures: function (task, runs) {
      var none = 0, unsure = 0, total = 0;
      runs.forEach(function (r) { var a = r.outcome.answers || {}; Object.keys(a).forEach(function (k) { total++; if (a[k].choice === NONE) none++; if (a[k].unsure) unsure++; }); });
      return total ? [{ label: 'marked unsure', value: Math.round(unsure / total * 100) + '%' }, { label: 'none of these', value: Math.round(none / total * 100) + '%' }] : [];
    },
    render: function (task, st, ctx) {
      var id = st.order[st.i], item = itemOf(task, id), a = st.answers[id] || (st.answers[id] = { choice: null, unsure: false, unfamiliar: false, note: '' });
      var go = function (d) { tick(st); st.i += d; ctx.log('item', { item: st.order[st.i], index: st.i }); ctx.update(); };
      var opts = task.categories.map(function (c) { return { code: c.code, label: c.label, definition: c.definition }; })
        .concat(task.allowNone === false ? [] : [{ code: NONE, label: task.noneLabel || 'None of these', definition: 'It does not belong in any of the categories above.' }]);
      var done = st.order.filter(function (x) { return answered(task, st.answers[x]); }).length;
      return el('div', { class: 'cl-wrap' },
        el('div', { class: 'cl-top' }, el('span', { class: 'muted', text: 'Item ' + (st.i + 1) + ' of ' + st.order.length + ' · ' + done + ' answered' })),
        el('div', { class: 'cl-item' }, el('p', { class: 'cl-text', lang: item.lang || null, text: item.text }), item.gloss ? el('p', { class: 'muted', text: item.gloss }) : null),
        el('fieldset', { class: 'cl-cats' }, el('legend', { text: 'Which category does it belong in?' }),
          opts.map(function (o) {
            return el('label', { class: 'cl-cat' + (a.choice === o.code ? ' on' : '') + (o.code === NONE ? ' none' : '') },
              el('input', { type: 'radio', name: 'cat-' + id, value: o.code, checked: a.choice === o.code, 'data-k': 'cat-' + o.code, onchange: function () {
                a.choice = o.code; ctx.log('choose', { item: id, choice: o.code }); ctx.update();
              } }),
              el('span', {}, el('b', { text: o.label }), o.definition ? el('span', { class: 'muted', text: o.definition }) : null));
          })),
        el('div', { class: 'cl-flags' },
          [['unsure', 'Unsure: I am guessing'], ['unfamiliar', "Unfamiliar: I don't know what this means"]].map(function (f) {
            return el('label', { class: 'check' }, el('input', { type: 'checkbox', 'data-k': 'flag-' + f[0], checked: a[f[0]], onchange: function (e) { a[f[0]] = e.target.checked; ctx.log('flag', { item: id, flag: f[0], on: e.target.checked }); ctx.update(); } }), el('span', { text: f[1] }));
          })),
        el('div', { class: 'field' }, el('label', { for: 'note-' + id, text: a.choice === NONE ? 'Why does nothing fit? (needed)' : 'Note (optional)' }),
          el('input', { id: 'note-' + id, class: 'input', 'data-k': 'note', value: a.note, 'aria-invalid': a.choice === NONE && !a.note.trim() ? 'true' : null,
            oninput: function (e) { a.note = e.target.value; ctx.save(); }, onchange: function () { ctx.log('note', { item: id }); ctx.update(); } })),
        el('div', { class: 'actions' },
          el('button', { type: 'button', class: 'btn', 'data-k': 'prev-item', disabled: st.i === 0, onclick: function () { go(-1); } }, '← Previous item'),
          el('button', { type: 'button', class: 'btn', 'data-k': 'next-item', disabled: st.i === st.order.length - 1 || !answered(task, a), onclick: function () { go(1); } }, 'Next item →')));
    }
  });
})();
