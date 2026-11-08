/* Card sort method module: open, closed or hybrid. See references/methods/card-sort.md.
   Placing a card always works three ways: drag it, tap it then tap a group's "Place here", or the same with the keyboard. */
(function () {
  'use strict';
  var el = Shell.el;
  var MODES = ['open', 'closed', 'hybrid'];

  function labelOf(task, id) { var c = task.cards.filter(function (x) { return x.id === id; })[0]; return c ? c.label : id; }
  function where(st, card) {
    if (st.deck.indexOf(card) >= 0) return 'deck';
    if (st.other.some(function (o) { return o.card === card; })) return 'other';
    var g = st.groups.filter(function (g) { return g.cards.indexOf(card) >= 0; })[0];
    return g ? g.id : null;
  }
  function groupName(task, st, id) {
    if (id === 'deck') return 'the cards to sort'; if (id === 'other') return "Doesn't fit";
    var g = st.groups.filter(function (g) { return g.id === id; })[0]; return g ? (g.name || 'a new group') : id;
  }
  function take(st, card) {
    st.deck = st.deck.filter(function (c) { return c !== card; });
    st.other = st.other.filter(function (o) { return o.card !== card; });
    st.groups.forEach(function (g) { g.cards = g.cards.filter(function (c) { return c !== card; }); });
  }
  function place(task, st, ctx, card, to) {
    var from = where(st, card);
    if (to === from) { st.holding = null; return ctx.update(); }
    take(st, card);
    if (to === 'new') { st.counter++; var g = { id: 'n' + st.counter, name: '', fixed: false, cards: [card] }; st.groups.push(g); ctx.log('group-add', { group: g.id }); to = g.id; st.focusName = g.id; }
    else if (to === 'deck') st.deck.push(card);
    else if (to === 'other') st.other.push({ card: card, reason: '' });
    else st.groups.filter(function (g) { return g.id === to; })[0].cards.push(card);
    st.holding = null; st.moves++;
    ctx.log(to === 'deck' ? 'return' : 'place', { item: card, from: from, to: to });
    ctx.announce(labelOf(task, card) + ' placed in ' + groupName(task, st, to) + '.');
    ctx.update();
  }
  function pick(task, st, ctx, card) {
    if (st.holding === card) { st.holding = null; ctx.announce('Put down ' + labelOf(task, card) + '.'); return ctx.update(); }
    st.holding = card; ctx.log('pick', { item: card, from: where(st, card) });
    ctx.announce('Holding ' + labelOf(task, card) + '. Choose where to place it.');
    ctx.update();
  }

  // Pointer drag on top of the tap path. A 6 px threshold keeps taps as taps.
  function draggable(btn, task, st, ctx, card) {
    btn.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      var sx = e.clientX, sy = e.clientY, ghost = null, over = null;
      function moveTo(ev) {
        if (!ghost) {
          if (Math.abs(ev.clientX - sx) + Math.abs(ev.clientY - sy) < 6) return;
          ghost = btn.cloneNode(true); ghost.className = 'cs-card cs-ghost'; ghost.removeAttribute('data-k'); document.body.appendChild(ghost);
          try { btn.setPointerCapture(e.pointerId); } catch (x) {}
        }
        ghost.style.transform = 'translate(' + (ev.clientX + 10) + 'px,' + (ev.clientY + 10) + 'px)';
        var t = document.elementFromPoint(ev.clientX, ev.clientY), d = t && t.closest('[data-drop]');
        if (over && over !== d) over.classList.remove('cs-over'); if (d) d.classList.add('cs-over'); over = d;
      }
      function up(ev) {
        document.removeEventListener('pointermove', moveTo); document.removeEventListener('pointerup', up); document.removeEventListener('pointercancel', up);
        if (over) over.classList.remove('cs-over');
        if (!ghost) return;
        ghost.remove(); btn.dataset.dragged = '1';
        var t = document.elementFromPoint(ev.clientX, ev.clientY), d = t && t.closest('[data-drop]');
        if (d) { ctx.log('pick', { item: card, from: where(st, card), via: 'drag' }); place(task, st, ctx, card, d.getAttribute('data-drop')); }
      }
      document.addEventListener('pointermove', moveTo); document.addEventListener('pointerup', up); document.addEventListener('pointercancel', up);
    });
  }
  function cardButton(task, st, ctx, card, where_) {
    var held = st.holding === card;
    var b = el('button', { type: 'button', class: 'cs-card' + (held ? ' held' : ''), 'aria-pressed': held ? 'true' : 'false', 'data-k': 'card-' + card,
      'aria-label': labelOf(task, card) + (where_ ? ', in ' + where_ : '') + (held ? ', picked up' : ''),
      onclick: function () { if (b.dataset.dragged) { delete b.dataset.dragged; return; } pick(task, st, ctx, card); } }, labelOf(task, card));
    draggable(b, task, st, ctx, card);
    return b;
  }
  function placeHere(task, st, ctx, to, label) {
    return st.holding ? el('button', { type: 'button', class: 'btn cs-place', 'data-k': 'place-' + to, onclick: function () { place(task, st, ctx, st.holding, to); } }, label || 'Place here') : null;
  }

  Shell.register({
    id: 'card-sort', version: '1.0.0', label: 'Card sort',
    tour: [
      { title: 'Sort the cards into groups', body: 'Put each card with the others you think belong with it. There are no right or wrong answers.' },
      { title: 'Two ways to move a card', body: 'Drag a card onto a group. Or tap a card to pick it up, then tap "Place here" on the group you want. Tap a placed card to move it again.' },
      { title: "When you're done", body: "Press \"I've finished\" when every card is where you want it. If a card doesn't fit anywhere, you can say so." }
    ],
    validate: function (content) {
      var errors = [], warnings = [];
      content.tasks.forEach(function (t) {
        var id = t.id || '?';
        if (MODES.indexOf(t.mode) < 0) errors.push(id + ': mode must be open, closed or hybrid.');
        var cards = t.cards || [], cats = t.categories || [], seen = {}, labels = {};
        if (cards.length < 2) errors.push(id + ': add at least two cards.');
        cards.forEach(function (c) {
          if (!c.id || !c.label) errors.push(id + ': every card needs an id and a label.');
          if (seen[c.id]) errors.push(id + ': card id "' + c.id + '" is used twice.'); seen[c.id] = 1;
          var l = (c.label || '').trim().toLowerCase(); if (labels[l]) errors.push(id + ': two cards are both called "' + c.label + '".'); labels[l] = 1;
        });
        if (t.mode !== 'open' && cats.length < 2) errors.push(id + ': a ' + t.mode + ' sort needs at least two categories.');
        var cs = {}; cats.forEach(function (c) { if (!c.id || !c.label) errors.push(id + ': every category needs an id and a label.'); if (cs[c.id]) errors.push(id + ': category id "' + c.id + '" is used twice.'); cs[c.id] = 1; });
        if (t.mode === 'open' && cats.length) warnings.push(id + ': an open sort ignores its categories.');
        if (cards.length > 40) warnings.push(id + ': ' + cards.length + ' cards is a lot for one sort; 30 to 40 is a common ceiling.');
      });
      return { errors: errors, warnings: warnings };
    },
    itemOrder: function (task, rand) { var ids = task.cards.map(function (c) { return c.id; }); return task.shuffle === false ? ids : Shell.shuffle(ids, rand); },
    start: function (task, plan) {
      var order = (plan.itemOrder && plan.itemOrder[task.id]) || task.cards.map(function (c) { return c.id; });
      var fixed = task.mode === 'open' ? [] : (task.categories || []).map(function (c) { return { id: 'c-' + c.id, name: c.label, fixed: true, cards: [] }; });
      return { deck: order.slice(), groups: fixed, other: [], holding: null, moves: 0, counter: 0 };
    },
    onEscape: function (st, ctx) { if (!st.holding) return false; st.holding = null; ctx.announce('Card put back.'); return true; },
    canFinish: function (task, st) {
      var unnamed = st.groups.filter(function (g) { return !g.fixed && g.cards.length && !g.name.trim(); }).length;
      var noReason = st.other.filter(function (o) { return !o.reason.trim(); }).length;
      if (unnamed) return { ok: false, message: 'Give every group you made a name.' };
      if (noReason) return { ok: false, message: "Say why each card in \"Doesn't fit\" doesn't fit." };
      if (st.deck.length) return { ok: false, message: st.deck.length + ' card' + (st.deck.length === 1 ? ' is' : 's are') + ' not sorted yet.', confirm: 'Finish with ' + st.deck.length + ' unsorted' };
      return { ok: true };
    },
    outcome: function (task, st) {
      return {
        success: null,
        groups: st.groups.filter(function (g) { return g.cards.length || g.fixed; }).map(function (g) { return { id: g.id, name: g.name, fixed: g.fixed, cards: g.cards.slice() }; }),
        other: st.other.map(function (o) { return { card: o.card, reason: o.reason }; }),
        unsorted: st.deck.slice(),
        moves: st.moves
      };
    },
    figures: function (task, runs) {
      if (!runs.length) return [];
      var made = runs.map(function (r) { return (r.outcome.groups || []).filter(function (g) { return g.cards.length; }).length; }).sort(function (a, b) { return a - b; });
      var left = runs.filter(function (r) { return (r.outcome.unsorted || []).length; }).length;
      return [{ label: 'median groups used', value: made[made.length >> 1] }, { label: 'left cards unsorted', value: left + ' of ' + runs.length }];
    },
    render: function (task, st, ctx) {
      var canMake = task.mode !== 'closed';
      var holdingBar = st.holding ? el('div', { class: 'cs-holding', role: 'status' },
        el('span', {}, 'Holding: ', el('b', { text: labelOf(task, st.holding) })),
        el('button', { type: 'button', class: 'btn', 'data-k': 'put-back', onclick: function () { st.holding = null; ctx.announce('Card put back.'); ctx.update(); } }, 'Put it back')) : null;

      var deck = el('section', { class: 'cs-deck', 'data-drop': 'deck', 'aria-labelledby': 'cs-deck-h' },
        el('h2', { id: 'cs-deck-h', class: 'cs-h', text: 'Cards to sort (' + st.deck.length + ')' }),
        st.deck.length ? el('div', { class: 'cs-cards' }, st.deck.map(function (c) { return cardButton(task, st, ctx, c, null); }))
          : el('p', { class: 'muted', text: 'All cards are placed. Check your groups, then finish.' }),
        st.holding && where(st, st.holding) !== 'deck' ? placeHere(task, st, ctx, 'deck', 'Put back in the cards to sort') : null);

      var groups = st.groups.map(function (g) {
        var head = g.fixed ? el('h3', { class: 'cs-h', text: g.name })
          : el('div', { class: 'field' }, el('label', { for: 'name-' + g.id, class: 'sr-only', text: 'Group name' }),
              el('input', { id: 'name-' + g.id, class: 'input', 'data-k': 'name-' + g.id, placeholder: 'Name this group', value: g.name, 'aria-invalid': g.cards.length && !g.name.trim() ? 'true' : null,
                oninput: function (e) { g.name = e.target.value; },
                onchange: function (e) { ctx.log('group-name', { group: g.id, name: e.target.value }); ctx.update(); } }));
        return el('section', { class: 'cs-group', 'data-drop': g.id, 'aria-label': g.fixed ? g.name : (g.name || 'New group') },
          head,
          g.cards.length ? el('div', { class: 'cs-cards' }, g.cards.map(function (c) { return cardButton(task, st, ctx, c, g.name || 'new group'); })) : el('p', { class: 'muted cs-empty', text: 'Empty' }),
          el('div', { class: 'actions' }, placeHere(task, st, ctx, g.id),
            !g.fixed ? el('button', { type: 'button', class: 'btn quiet', 'data-k': 'remove-' + g.id, onclick: function () {
              st.deck = st.deck.concat(g.cards); st.groups = st.groups.filter(function (x) { return x !== g; }); ctx.log('group-remove', { group: g.id, returned: g.cards.length });
              ctx.announce('Group removed. Its cards are back in the cards to sort.'); ctx.update();
            } }, 'Remove group') : null));
      });
      if (canMake) groups.push(el('section', { class: 'cs-group cs-new', 'data-drop': 'new', 'aria-label': 'New group' },
        el('h3', { class: 'cs-h', text: 'New group' }),
        el('p', { class: 'muted', text: st.holding ? 'Place the card here to start a new group.' : 'Drag a card here, or pick one up and place it here, to start a new group.' }),
        el('div', { class: 'actions' }, placeHere(task, st, ctx, 'new', 'Start a new group with it'))));

      var other = task.allowOther ? el('section', { class: 'cs-other', 'data-drop': 'other', 'aria-labelledby': 'cs-other-h' },
        el('h3', { id: 'cs-other-h', class: 'cs-h', text: "Doesn't fit anywhere" }),
        st.other.length ? st.other.map(function (o) {
          return el('div', { class: 'cs-other-row' }, cardButton(task, st, ctx, o.card, "doesn't fit"),
            el('label', { class: 'sr-only', for: 'why-' + o.card, text: 'Why does ' + labelOf(task, o.card) + " not fit?" }),
            el('input', { id: 'why-' + o.card, class: 'input', 'data-k': 'why-' + o.card, placeholder: 'Why not?', value: o.reason, 'aria-invalid': o.reason.trim() ? null : 'true',
              oninput: function (e) { o.reason = e.target.value; }, onchange: function (e) { ctx.log('other-reason', { item: o.card }); ctx.update(); } }));
        }) : el('p', { class: 'muted', text: "If a card doesn't belong in any group, put it here and say why." }),
        el('div', { class: 'actions' }, placeHere(task, st, ctx, 'other'))) : null;

      var wrap = el('div', { class: 'cs-board' }, holdingBar, deck, el('div', { class: 'cs-groups' }, groups), other);
      if (st.focusName) { var id = st.focusName; st.focusName = null; setTimeout(function () { var i = document.getElementById('name-' + id); if (i) i.focus(); }, 0); }
      return wrap;
    }
  });
})();
