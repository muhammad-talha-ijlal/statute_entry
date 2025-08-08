// JavaScript for inline hierarchy management

document.addEventListener('DOMContentLoaded', function() {
    initComponentHandlers();
    initSortableLists();
});

function initComponentHandlers() {
    // Add
    document.querySelectorAll('.component-add').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const type = this.dataset.type;
            const parentId = this.dataset.parentId;
            const name = prompt(`Enter ${type} name:`);
            if (name === null) return;
            const number = prompt(`Enter ${type} number (optional):`);
            let content = null;
            if (type === 'subsection') {
                content = prompt('Enter content:');
                if (content === null) return;
            }
            const res = await fetch('/hierarchy/component', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'add', type, parent_id: parentId, name, number, content })
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Error adding component');
            }
        });
    });

    // Edit
    document.querySelectorAll('.component-edit').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const type = this.dataset.type;
            const id = this.dataset.id;
            const name = prompt(`Edit ${type} name:`, this.dataset.name || '');
            if (name === null) return;
            const number = prompt(`Edit ${type} number (optional):`, this.dataset.number || '');
            let content = null;
            if (type === 'subsection') {
                content = prompt('Edit content:', this.dataset.content || '');
                if (content === null) return;
            }
            const res = await fetch('/hierarchy/component', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'edit', type, id, name, number, content })
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Error updating component');
            }
        });
    });

    // Delete
    document.querySelectorAll('.component-delete').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            if (!confirm('Are you sure you want to delete this item?')) return;
            const type = this.dataset.type;
            const id = this.dataset.id;
            const res = await fetch('/hierarchy/component', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'delete', type, id })
            });
            const data = await res.json();
            if (data.success) {
                location.reload();
            } else {
                alert(data.message || 'Error deleting component');
            }
        });
    });
}

function initSortableLists() {
    document.querySelectorAll('.sortable-list').forEach(list => {
        new Sortable(list, {
            group: list.dataset.groupName,
            handle: '.tree-item',
            animation: 150,
            onEnd: async function() {
                const type = list.dataset.level;
                const parentId = list.dataset.parentId;
                const order = Array.from(list.children).map(li => li.dataset.id);
                await fetch('/hierarchy/component', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'reorder', type, parent_id: parentId, order })
                });
            }
        });
    });
}
