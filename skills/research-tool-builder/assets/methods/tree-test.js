/* Tree test method module: find where something lives in a text-only menu.
   The participant chooses an answer themselves, so the task ends when they confirm one.
   See references/methods/tree-test.md. */
(function () {
  'use strict';
  var el = Shell.el;

  function treeOf(task, content) { return task.tree || content.tree || []; }
  function childrenAt(tree, path) {
    var level = tree;
    for (var i = 0; i < path.length; i++) { var n = level.filter(function (x) { return x.label === path[i]; })[0]; if (!n) return []; level = n.children || []; }
    return level;
  }
  function norm(p) { return p.map(function (x) { return String(x).trim().toLowerCase(); }).join(' › '); }
  function exists(tree, path) {
    var level = tree;
    for (var i = 0; i < path.length; i++) { var n = level.filter(function (x) { return x.label === path[i]; })[0]; if (!n) return false; level = n.children || []; }
    return true;
  }
  var CONTENT = null;

  Shell.register({
    id: 'tree-test', version: '1.0.0', label: 'Tree test', finishButton: false,
    tour: [
      { title: 'Find where you would look', body: 'You will see a menu with no design, just words. Open the sections you would look in to complete the task.' },
      { title: 'Choose your answer', body: 'When you reach the place you would expect to find it, choose it and confirm. You can go back up at any time before you confirm.' }
    ],
    validate: function (content) {
      CONTENT = content;
      var errors = [], warnings = [];
      content.tasks.forEach(function (t) {
        var id = t.id || '?', tree = treeOf(t, content);
        if (!tree.length) errors.push(id + ': no menu tree. Add "tree" to the study or the task.');
        (t.accepted || []).forEach(function (p) { if (!exists(tree, p)) errors.push(id + ': accepted answer "' + p.join(' › ') + '" is not in the tree.'); });
        if (!(t.accepted || []).length) warnings.push(id + ': no accepted answer, so success cannot be worked out automatically.');
      });
      return { errors: errors, warnings: warnings };
    },
    start: function () { return { path: [], trail: [[]], backtracks: 0, choosing: null, chosen: null }; },
    onEscape: function (st) { if (!st.choosing) return false; st.choosing = null; return true; },
    outcome: function (task, st, reason) {
      var chosen = st.chosen, acc = (task.accepted || []).map(norm);
      var success = reason === 'gave-up' ? false : !acc.length ? null : acc.indexOf(norm(chosen || [])) >= 0;
      var tol = task.backtrackTolerance == null ? 0 : task.backtrackTolerance;
      return { success: success, path: chosen, direct: success === true ? st.backtracks <= tol : false, backtracks: st.backtracks, trail: st.trail };
    },
    figures: function (task, runs) {
      var direct = runs.filter(function (r) { return r.outcome.direct; }).length;
      return runs.length ? [{ label: 'direct success', value: direct + ' of ' + runs.length }] : [];
    },
    render: function (task, st, ctx) {
      var tree = treeOf(task, CONTENT || {}), here = childrenAt(tree, st.path);
      var go = function (path, how) {
        if (path.length < st.path.length) st.backtracks++;
        st.path = path; st.choosing = null; st.trail.push(path.slice());
        ctx.log(how, { path: path.slice() }); ctx.update();
      };
      var crumbs = el('nav', { class: 'tt-crumbs', 'aria-label': 'Where you are' }, el('ol', {},
        el('li', {}, st.path.length ? el('button', { type: 'button', class: 'tt-crumb', 'data-k': 'crumb-0', onclick: function () { go([], 'jump'); } }, 'Home') : el('span', { 'aria-current': 'location', text: 'Home' })),
        st.path.map(function (p, i) {
          var last = i === st.path.length - 1;
          return el('li', {}, last ? el('span', { 'aria-current': 'location', text: p }) : el('button', { type: 'button', class: 'tt-crumb', 'data-k': 'crumb-' + (i + 1), onclick: function () { go(st.path.slice(0, i + 1), 'jump'); } }, p));
        })));
      return el('div', { class: 'tt-wrap' }, crumbs,
        st.path.length ? el('button', { type: 'button', class: 'btn quiet', 'data-k': 'up', onclick: function () { go(st.path.slice(0, -1), 'up'); } }, '← Back up') : null,
        el('ul', { class: 'tt-list', 'aria-label': st.path.length ? st.path[st.path.length - 1] : 'Home' }, here.map(function (n, i) {
          var leaf = !(n.children && n.children.length), on = st.choosing === n.label;
          return el('li', {}, el('button', { type: 'button', class: 'tt-node' + (leaf ? ' leaf' : '') + (on ? ' on' : ''), 'data-k': 'node-' + i, 'aria-expanded': leaf ? null : 'false', 'aria-pressed': leaf ? (on ? 'true' : 'false') : null,
            onclick: function () {
              if (!leaf) return go(st.path.concat([n.label]), 'open');
              st.choosing = n.label; ctx.log('select', { path: st.path.concat([n.label]) }); ctx.update();
            } }, el('span', { text: n.label }), el('span', { class: 'tt-chev', 'aria-hidden': 'true', text: leaf ? '' : '›' })),
            on ? el('div', { class: 'tt-confirm', role: 'group', 'aria-label': 'Confirm your answer' },
              el('span', {}, 'Is ', el('b', { text: n.label }), ' your answer?'),
              el('button', { type: 'button', class: 'btn primary', 'data-k': 'confirm', onclick: function () {
                st.chosen = st.path.concat([n.label]); ctx.log('answer', { path: st.chosen }); ctx.finish('finished');
              } }, 'This is my answer'),
              el('button', { type: 'button', class: 'btn', 'data-k': 'node-' + i, onclick: function () { st.choosing = null; ctx.log('unselect', {}); ctx.update(); } }, 'Keep looking')) : null);
        })));
    }
  });
})();
