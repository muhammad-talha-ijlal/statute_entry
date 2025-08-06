(() => {
  /* ───────────── DOM helpers ───────────── */
  const $  = sel => document.querySelector(sel);
  const $$ = sel => [...document.querySelectorAll(sel)];

  /* ───────── unsaved-state tracker ─────── */
  const state = {};          // id → {status, level, parent_id}

  /* ─────── boot-strap once DOM ready ───── */
  document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('click', delegatedClick,  true);   // capture
    document.addEventListener('input', delegatedInput,  false);

    initGlobalButtons();
    window.onbeforeunload = () => hasUnsaved() ? 'Unsaved changes' : null;
  });

  /* ───────────── click delegate ────────── */
  function delegatedClick (e) {
    const btn = e.target.closest('.btn-small');
    if (!btn) return;
    e.preventDefault();                                 // stop # links

    /* root-level “Add Part” is not inside a tree-node */
    if (btn.classList.contains('btn-add') && btn.dataset.level === 'part') {
      createPart();
      updateSaveBar();
      return;
    }

    const node = btn.closest('.tree-node');
    if (!node) return;

    if (node.dataset.level === 'subsection' && btn.classList.contains('btn-edit')) {
      return launchContentDialog(node);
    }

    if (btn.classList.contains('btn-add')) {
      createChild(node, btn.dataset.level);
    } else if (btn.classList.contains('btn-edit')) {
      toggleEditable(node, true);
      markEdited(node);
    } else if (btn.classList.contains('btn-delete')) {
      node.classList.toggle('deleted');
      const id = node.dataset.id;
      state[id] = { ...(state[id] || {}), status: node.classList.contains('deleted') ? 'deleted' : 'edited' };
    } else if (btn.classList.contains('btn-up') || btn.classList.contains('btn-down')) {
      moveNode(btn);
    }

    updateSaveBar();
  }

  /* ─────────── input delegate ──────────── */
  function delegatedInput (e) {
    if (e.target.matches('.name-input, .num-input')) {
      markEdited(e.target.closest('.tree-node'));
      updateSaveBar();
    }
  }

  /* ───────── helpers: editability ──────── */
  function toggleEditable (node, enable) {
    node.querySelectorAll('.name-input, .num-input').forEach(i => (i.disabled = !enable));
  }

  function markEdited (node) {
    node.classList.add('edited');
    const id = node.dataset.id;
    state[id] = state[id] || {};
    if (state[id].status !== 'new') state[id].status = 'edited';
  }

  const hasUnsaved = () => Object.values(state).some(s => s.status && s.status !== 'unchanged');

  /* ──────── create **Part** at root ─────── */
  function createPart () {
    const rootUl = $('#hierarchy-tree .parts-list.tree-root');
    if (!rootUl) return;

    const id = `new-${crypto.randomUUID()}`;
    rootUl.insertAdjacentHTML('beforeend', templateFor('part', id));
    const li = rootUl.lastElementChild;

    li.classList.add('new');
    toggleEditable(li, true);
    state[id] = { status: 'new', level: 'part', parent_id: null };
  }

  /* ─────── create any other child node ─── */
  function createChild (parentNode, level) {
    const ul = parentNode.querySelector(':scope > .tree-children') ||
               parentNode.appendChild(Object.assign(document.createElement('ul'), { className: 'tree-children' }));
    ul.dataset.parentId = parentNode.dataset.id;

    const id = `new-${crypto.randomUUID()}`;
    ul.insertAdjacentHTML('beforeend', templateFor(level, id));
    const li = ul.lastElementChild;

    li.classList.add('new');
    toggleEditable(li, true);
    state[id] = { status: 'new', level, parent_id: parentNode.dataset.id };
  }

  /* ────────── templates & maps ─────────── */
  const LABELS = { part:'PART', chapter:'CHAPTER', set:'SET', section:'SECTION', subsection:'SUBSECTION' };
  const nextLevel = lvl => ({ part:'chapter', chapter:'set', set:'section', section:'subsection' }[lvl]);

  function templateFor (level, id) {
    const next   = nextLevel(level);
    const addBtn = level !== 'subsection'
      ? `<button class="btn-small btn-add" data-level="${next}">+ Add ${LABELS[next]}</button>`
      : `<button class="btn-small btn-edit">✎ Edit</button>`;

    return /*html*/`
      <li class="tree-node ${level}-node" data-level="${level}" data-id="${id}">
        <div class="tree-item">
          ${level==='subsection'
              ? '<div class="tree-leaf-spacer"></div>'
              : '<div class="tree-toggle"><span class="toggle-icon collapsed">▶</span><span class="toggle-icon expanded">▼</span></div>'}
          <div class="tree-content">
            <span class="item-label">${LABELS[level]}</span>
            <input class="num-input  item-number" placeholder="#"  disabled>
            <input class="name-input item-name"  placeholder="Name…" disabled>
          </div>
          <div class="tree-actions">
            ${addBtn}
            <button class="btn-small btn-delete">× Delete</button>
            <button class="btn-small btn-up">▲</button>
            <button class="btn-small btn-down">▼</button>
          </div>
        </div>
        ${level==='subsection' ? '<div class="subsection-content hidden"></div>' : ''}
      </li>`;
  }

/* ---------- move node up / down ---------- */
function moveNode(btn) {
  const li   = btn.closest('.tree-node');
  const list = [...li.parentNode.children];

  const up   = btn.classList.contains('btn-up');
  const idx  = list.indexOf(li);
  const swap = up ? idx - 1 : idx + 1;
  if (swap < 0 || swap >= list.length) return;

  li.parentNode.insertBefore(li, up ? list[swap] : list[swap].nextSibling);

  /* after the move, walk ALL siblings and refresh order + state */
  [...li.parentNode.children].forEach((node, i) => {
    node.dataset.order = i + 1;               // purely visual
    const id = node.dataset.id;

    /* always keep an entry in state so buildPayload pushes it to `order` */
    state[id] = { ...(state[id] || {}), status: state[id]?.status || 'unchanged' };
  });

  markEdited(li);   // only the moved row is visually red
  updateSaveBar();
}



  /* ──────── subsection modal ───────────── */
  function launchContentDialog (subNode) {
    const dlg  = $('#subContentDlg');
    const area = $('#dlgContent');
    const div  = subNode.querySelector('.subsection-content');

    area.value = div.innerHTML.trim();
    dlg.showModal();

    $('#dlgOk').onclick = () => {
      div.innerHTML = area.value;
      markEdited(subNode);
      dlg.close();
      updateSaveBar();
    };
  }

  /* ─────── Save / Cancel toolbar ───────── */
  function initGlobalButtons () {
    $('#statute-save')  .addEventListener('click', saveAll);
    $('#statute-cancel').addEventListener('click', () => location.reload());
  }
  function updateSaveBar () {
    const dirty = hasUnsaved();
    $('#statute-save').disabled   = !dirty;
    $('#statute-cancel').disabled = !dirty;
  }

  /* ─────── build payload & POST ───────── */
  async function saveAll () {
    const payload = buildPayload();

    try {
      const r = await fetch(`${location.pathname}/bulk-save`, {
        method : 'POST',
        headers: { 'Content-Type':'application/json',
                   'X-CSRFToken' : $('meta[name=csrf-token]')?.content || '' },
        body   : JSON.stringify(payload)
      });
      if (!r.ok) throw await r.text();

      const map = await r.json();
Object.entries(map).forEach(([tmp, real]) => {
  const n = document.querySelector(`.tree-node[data-id="${tmp}"]`);
  if (n) n.dataset.id = real;
});

/* remove rows that were actually deleted */
document.querySelectorAll('.tree-node.deleted').forEach(n => n.remove());

/* reset state & colours */
Object.keys(state).forEach(k => delete state[k]);
document.querySelectorAll('.tree-node').forEach(n => n.classList.remove('new','edited'));
updateSaveBar();
alert('Save successful');

    } catch (err) {
      console.error(err);
      alert(`Save failed:\n${err}`);
    }
  }

  /* ─────── payload helper ─────────────── */
  function buildPayload () {
    const created=[], updated=[], deleted=[], order=[];
    Object.entries(state).forEach(([id, st]) => {
      const node = $(`.tree-node[data-id="${id}"]`);
      if (!node) return;

      const level = node.dataset.level;
      const fields = {
        number   : node.querySelector('.num-input') ?.value.trim() || null,
        name     : node.querySelector('.name-input')?.value.trim() || null,
        content  : level==='subsection'
                    ? node.querySelector('.subsection-content').innerHTML.trim()
                    : null,
        order_no : [...node.parentNode.children].indexOf(node)+1,
        parent_id: node.parentNode.dataset.parentId || null
      };

      if (st.status==='new')      created.push({temp_id:id, level, ...fields});
      else if (st.status==='edited') updated.push({id, level, ...fields});
      else if (st.status==='deleted') deleted.push({id, level});
      if (st.status!=='deleted') order.push({id, order_no: fields.order_no});
    });
    return {created, updated, deleted, order};
  }
})();
