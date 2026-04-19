# Design System — Infotek IT Portal

## Stack

| Layer | Technology | Source |
|-------|-----------|--------|
| CSS framework | Tailwind CSS v3 | CDN (`cdn.tailwindcss.com`) |
| Interactivity | Alpine.js v3 | CDN (`cdn.jsdelivr.net/npm/alpinejs@3.x.x`) |
| Tables | DataTables 1.13.7 | CDN (`cdn.datatables.net`) |
| Rich text (legacy) | Quill 1.3.6 | CDN (loaded only when `needquillinput` is set) |
| Markdown editor | EasyMDE | CDN (`unpkg.com/easymde/dist/easymde.min.js`) |
| Markdown renderer | marked.js | CDN (`cdn.jsdelivr.net/npm/marked/marked.min.js`) |
| Drag-and-drop | SortableJS 1.15.0 | CDN (`cdn.jsdelivr.net/npm/sortablejs@1.15.0`) — projects + tasks |
| Fonts | DM Sans (400–700), JetBrains Mono | Google Fonts |
| Backend | Django 4.2 / Python 3.12 | Apache + mod_wsgi |

> **Note:** DataTables FixedHeader extension was evaluated and removed. It does not work reliably in sidebar layouts because `position: fixed` clones the header at viewport-relative coordinates, causing left-offset misalignment. Use `scrollY` + `"dom": "t"` instead (see DataTables section).

> **Note:** Quill is legacy — used only for displaying existing wiki articles stored in Quill JSON format. All new wiki articles are written in Markdown via EasyMDE. New pages should not use Quill.

---

## Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `slate-50` | `#f8fafc` | Page background |
| `white` | `#ffffff` | Cards, sidebar, topbar |
| `slate-100` | `#f1f5f9` | Dividers, subtle borders |
| `slate-200` | `#e2e8f0` | Card borders, table borders |
| `slate-400` | `#94a3b8` | Placeholder text, inactive icons |
| `slate-500` | `#64748b` | Secondary text, nav labels |
| `slate-700` | `#334155` | Body text |
| `slate-800` | `#1e293b` | Headings, primary text |
| `blue-600` / `brand-600` | `#2563eb` | Primary action (buttons, links, active nav) |
| `blue-700` | `#1d4ed8` | Button hover |
| `red-600` | `#dc2626` | Destructive action, delete button text |

Custom `brand` alias (maps to blue palette) is defined in `tailwind.config` in `_base.html`.

---

## Typography

- **Font family**: DM Sans (`font-sans`), JetBrains Mono for code (`font-mono`)
- **Page title**: `text-xl font-semibold text-slate-800`
- **Section subtitle**: `text-xs text-slate-500`
- **Table column headers**: `text-xs font-medium uppercase tracking-wider text-slate-500` (via DataTables CSS override in `_base.html`)
- **Body / table cells**: `text-sm text-slate-700`
- **Labels (form, detail rows)**: `text-xs font-medium text-slate-500`

---

## Layout

### Shell (`_base.html`)
```
<body>
  <aside>          ← fixed left sidebar, w-64, white, z-30
  <div.flex-col>   ← main column, lg:ml-64 when sidebar open
    <header>       ← sticky top-0 h-14, topbar with hamburger + user menu
    <main.p-3.sm:p-6> ← page content area (bg-slate-50, mobile 12px / desktop 24px)
    <footer>       ← thin border-top footer
```

**Sidebar toggle**: Alpine.js `x-data="{ sidebarOpen: window.innerWidth >= 1024 }"` on `<body>`. Open by default on desktop, closed on mobile.

### Content widths
| Template | Width | Use |
|----------|-------|-----|
| `_basenarrow.html` | `max-w-5xl mx-auto` | Edit/add forms (clients, people, tools, notes, files) |
| `_basenorm.html` | `max-w-5xl mx-auto` | List pages, wiki editor, client detail |
| `_basewide.html` | full width + inner `max-w-5xl` | View/detail pages (wiki, tools, notes, files); external public pages |

**Width rule**: All internal pages (list, view, edit) use `max-w-5xl` to maintain consistent width across all three levels. `_basenarrow` and `_basenorm` both resolve to `max-w-5xl` — the distinction is kept for semantic clarity (forms vs. lists). When using `_basewide.html`, constrain content sections and the sticky bar inner wrapper to `max-w-5xl mx-auto`.

### Sticky page header pattern — ALWAYS two divs

**Critical**: sticky bars are always two divs: outer full-bleed, inner max-width. **Never** put `flex` on the outer div.

`-mx-6 px-6` on the outer div cancels `<main>`'s padding so the bar bleeds full-width while the inner div re-centers the content. `top-14` sits just below the 56px (`h-14`) topbar.

**List pages** (title + search + optional action button):
```html
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-4">
<div class="max-w-5xl mx-auto flex items-center gap-4">
    <div class="min-w-0">
        <h1 class="text-xl font-semibold text-slate-800 leading-tight">Page Title</h1>
        <p class="text-xs text-slate-500">Subtitle</p>
    </div>
    <div class="flex-1 relative">
        <!-- search icon + <input id="my-search"> -->
    </div>
    <!-- optional: Add button (primary) -->
</div>
</div>
```

**Detail/view pages** (`_basewide.html` with `max-w-5xl` content):
```html
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-6">
<div class="max-w-5xl mx-auto flex items-center gap-3">
    <!-- ← Back link | [Page title] | flex-1 spacer | [action buttons] -->
</div>
</div>
```

**Form pages** (`_basenarrow.html` with `max-w-5xl` content):
```html
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-6">
<div class="max-w-5xl mx-auto flex items-center gap-3">
    <!-- ← Back | [Page title] | flex-1 spacer | [Cancel] [✓ Save] -->
</div>
</div>
```

The inner max-width **must match** the page content width. Mismatching max-widths cause the action bar buttons to mis-align with the content edges.

### List page scroll model

List pages lock the outer page from scrolling and let only the DataTable body scroll:

```css
/* In {% block extra_css %} of each list page */
html, body { overflow: hidden; height: 100%; }
```

After DataTable init, `fitTable()` measures the exact pixel offset of `.dataTables_scrollBody` from the top of the viewport and sets its height to fill the remainder:

```javascript
function fitTable() {
    var scrollBody = $('#mytable').closest('.dataTables_wrapper').find('.dataTables_scrollBody');
    var top = scrollBody.offset().top;
    var h = window.innerHeight - top - 8;
    scrollBody.css({ 'height': h + 'px', 'max-height': h + 'px' });
}
fitTable();
$(window).on('resize', fitTable);
```

### Editor page scroll model

The wiki editor page does **not** set `overflow: hidden` on body — doing so breaks CodeMirror's internal mouse-wheel scroll handler. Instead, `fitEditor()` sizes the CodeMirror div to exactly fill the remaining viewport height, so there is nothing below the fold and the page body has nothing to scroll. Only CodeMirror's internal `.CodeMirror-scroll` container scrolls.

```javascript
function fitEditor() {
    var cmHeight = window.innerHeight
                 - topbarH         // 56px
                 - actionBarH      // measured
                 - titleH          // measured
                 - labelH          // measured
                 - toolbarH        // measured
                 - statusH         // measured
                 - 16;             // breathing room
    document.querySelector('.CodeMirror').style.height = cmHeight + 'px';
}
setTimeout(fitEditor, 50);  // after EasyMDE renders
window.addEventListener('resize', fitEditor);
```

---

## Components

### Cards / white panels
```html
<div class="bg-white rounded-xl border border-slate-200 overflow-hidden">
```
Used for tables and content sections. Add `p-6` for padded card content.

### Primary button (Add / Save)
```html
<a class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
```

### Secondary / outline button (View)
All row-level action buttons use this style — consistent across Clients, People, Wiki pages:
```html
<button class="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-md hover:bg-slate-50 transition-colors">
    View
</button>
```
The label is **"View"** everywhere — do not use "Details" or other variants.

### Destructive button (Delete)
```html
<button class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
        onclick="if(confirm('Are you sure you want to delete?')) this.closest('form').submit()">
```
Uses native `confirm()` — no modal library required.

### Inline search input (list page header)
```html
<div class="flex-1 relative">
    <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" ...magnifier.../>
    <input type="search" id="my-search"
           placeholder="Search…"
           class="w-full pl-9 pr-4 py-2 text-sm border border-slate-200 rounded-lg bg-white outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 font-sans transition-colors">
</div>
```
Wired to DataTables via:
```javascript
$('#my-search').on('input', function() { dt.search(this.value).draw(); });
```

### Phone link (`views/components/phonenumber.html`)
Blue `tel:` link with phone icon. Shows national format for +1 numbers, international otherwise. Always use this component — never render phone numbers as raw text.

### Email link (inline)
```html
<a href="mailto:{{ obj.email }}"
   class="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-800 transition-colors text-sm">
    <svg class="w-3.5 h-3.5 shrink-0" ...envelope icon.../>
    {{ obj.email }}
</a>
```

### Person detail modal (`views/modals/personmodal.html`)
Alpine.js modal. `x-data="{ open: false }"` goes on the parent `<td>` (not `<tr>`) to avoid breaking HTML table structure. Backdrop click and Escape key close it.

Edit button in footer resolves the client ID via:
```django
{% with editclientid=clid|default:person.employedby_id %}
{% if editclientid %}
    <form action="{% url 'clientperson' clientid=editclientid %}">
```
Works from both the client detail view (`clid` passed) and the all-people list (`person.employedby_id` fallback).

---

## Navigation

Sidebar sections: **Main** → Home, Clients, People | **Tools** → Wiki, Tools, Secret Notes, File Sharing | **Work** → Projects, My To-Do | **System** → Help, Admin Portal (staff only)

### Admin Portal nav active states
```html
{% if request.resolver_match.url_name in 'usermanagement admin_users admin_user_add admin_user_edit admin_login_logs' %}nav-item-active{% endif %}
```

### Admin Portal — User Roles
Three tiers map to Django's built-in flags (no custom model field needed):

| Role | `is_staff` | `is_superuser` | Access |
|------|-----------|----------------|--------|
| User | `False` | `False` | Standard portal access only |
| Staff | `True` | `False` | Admin Portal access |
| Admin | `True` | `True` | Full superuser access |

- Role is selected via a `<select name="role">` in `admin_user_form.html` (superusers only)
- `_role_from_user(u)` helper in `adminviews.py` converts a User instance back to `'admin'`/`'staff'`/`'user'`
- Self-demotion blocked: `edit_user != request.user` guard in `admin_user_edit`
- Staff users cannot edit or delete superuser accounts

Active state via `request.resolver_match.url_name` in templates:
```html
{% if request.resolver_match.url_name == 'allclients' %}nav-item-active{% endif %}
```
For multi-URL sections (wiki, tools, notes), use `in` check:
```html
{% if 'wiki' in request.resolver_match.url_name %}nav-item-active{% endif %}
```

---

## DataTables conventions

- Always declare `needdatatables: True` in view context to load CSS/JS
- Use `"visible": false` on hidden-but-searchable columns — **never** `class="hidden"` (breaks column indexing)
- Hidden columns must be **last** in both `<thead>` and `<tbody>`
- Do **not** use FixedHeader extension — it breaks in sidebar layouts (see Stack note above)
- Use `"dom": "t"` to suppress DataTables' built-in Show/Search controls; provide a custom search input in the sticky page header instead
- All cells left-aligned via global CSS override: `table.dataTable thead th, tbody td { text-align: left !important }`
- `autoWidth: false` prevents DataTables from fighting width overrides on `.dataTables_scrollHeadInner`

Standard config for list pages:
```javascript
var dt = $('#mytable').DataTable({
    "paging": false,
    "info": false,
    "searching": true,
    "dom": "t",
    "scrollY": "300px",       // placeholder — overridden by fitTable()
    "scrollCollapse": true,
    "autoWidth": false,
    "order": [[0, "asc"]],
    "columnDefs": [
        { "orderable": false, "targets": [N] },   // Actions column only
        { "visible": false, "targets": [N] }      // hidden search cols if any
    ]
});

$('#my-search').on('input', function() { dt.search(this.value).draw(); });
```

### Sortable columns
- **Clients**: Name sortable; Phone, Actions, Emails not sortable
- **People**: Name, Company, Phone, Email sortable; Actions not sortable
- **Wiki**: Title and Updated sortable (default: Updated desc); Actions not sortable
- **Tools**: Name, Visibility, Created on sortable (default: Created on desc — newest first); Link, Description, Actions not sortable
- **Secret Notes**: Subject, Created for, Expires on sortable (default: Expires on desc — newest first); Status, Reads left, Actions not sortable

### Column text overflow model
Long text cells use CSS `-webkit-line-clamp: 2` to show the first 2 lines and hide the rest. The full text is always available in the `title` attribute (native browser tooltip on hover). This applies to Name, Link, and Description in Tools; Subject and Created for in Secret Notes.

```css
td.clamped {
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}
```
Never use `white-space: nowrap; text-overflow: ellipsis` on these — that cuts to 1 line with no wrapping. Use `-webkit-line-clamp` for 2-line wrap.

---

## Wiki — Markdown editor (EasyMDE)

### Storage format
Wiki articles are stored as plain text in `WikiArticle.article` (TextField). New articles are Markdown. Legacy articles are Quill JSON delta format (starts with `{`).

### Backward compatibility in `wikiview.html`
```django
{% if article.get_quill_object.is_quill_content %}
    {# Legacy: render via Quill pipeline #}
    {% include "forms/widget/maybequill.html" with obj=article.get_quill_object %}
{% else %}
    {# New: render markdown with marked.js #}
    <div id="article-content" class="wiki-body"></div>
{% endif %}
```
```javascript
// Only loaded for non-Quill articles
var rawMarkdown = "{{ article.article|escapejs }}";
document.getElementById('article-content').innerHTML = marked.parse(rawMarkdown);
```

### Edit form (`forms/wikieditform.html`)
- Extends `_basenorm.html` (not `_basenarrow.html` — editor needs more width)
- All action buttons (Save, Cancel, Delete) in sticky top bar — nothing at the bottom
- EasyMDE toolbar: bold, italic, heading, quote, lists, link, image, code, table, preview, side-by-side, fullscreen, import, guide
- Legacy Quill content is converted to plain text via `_get_editable_content()` in `wikiarticleform.py` when opened for editing

### Markdown import
A custom toolbar button (upload icon) triggers a hidden `<input type="file" accept=".md,.txt,.markdown">`. If the editor already has content, user is asked whether to Replace or Append (appends with `---` separator).

### Print / PDF
`window.print()` button in the action bar. Print CSS in `wikiview.html` hides:
- `aside` (sidebar)
- `header` (topbar)
- `footer`
- `.no-print` (action bar)
- Resets `margin-left: 0` on main content div
- Sets `html, body { overflow: visible; height: auto }` for multi-page pagination

---

## Tools page (`views/alltools.html`)

- Extends `_basenorm.html`. `overflow: hidden` on body (DataTable scrollY model).
- Sticky header: title + subtitle | filter tabs (All / Links / Files) | search | Add Link (outline) + Add File (primary blue)
- Filter tab active state read from URL kwargs — no Python context change needed:
  ```django
  {% with cur_type=request.resolver_match.kwargs.tool_type %}
  {% if cur_type == '' or cur_type == None %}...All active...{% endif %}
  {% if cur_type == 'l' %}...Links active...{% endif %}
  {% if cur_type == 'f' %}...Files active...{% endif %}
  ```
- Table columns (authenticated): Name | Link | Description | Visibility | Created on | Actions
- Table columns (public): Name | Link | Description
- Type (File/Link) is indicated by the All/Links/Files filter tabs — no separate Type column
- Default sort: Created on descending (newest first)
- Column widths: Name 20% | Link 17% | Description 22% | Visibility 16% | Created on 13% | Actions 12%
- Visibility column combines `public` + `publicinlist` flags into one badge:
  - `bg-emerald-50 text-emerald-700` → "Public / In list"
  - `bg-amber-50 text-amber-700` → "Public / Hidden"
  - `bg-slate-100 text-slate-500` → "Private"
- Type badge: `bg-blue-50 text-blue-700` for File; `bg-slate-100 text-slate-600` for Link
- Actions: **View** button is a GET link to `tool_view` URL (renders `views/toolview.html`)
- Name, Link, Description cells use `-webkit-line-clamp: 2` for 2-line wrap with tooltip

### Tool view page (`views/toolview.html`)
- Extends `_basewide.html`. Sticky action bar: ← All tools | tool name | **Edit tool** button
- Edit button submits form POST to `new_tool` URL with `action=change` and `targetid`
- Content card: Type badge | Link/Download | Description (whitespace-pre-wrap) | Visibility badge
- URL: `tool/<int:toolid>/view` → name `tool_view`

### Tool row (`views/oneitemrow/onetoolrow.html`)
Row includes `id="{{ tool.id }}"` and `hover:bg-slate-50`. View button is a GET `<a href="{% url 'tool_view' toolid=tool.id %}">`.

### File deletion warning
When editing a FileTool that already has an uploaded file, `toolsform.py` passes `has_existing_file=True` and `existing_file_name` to the context. `unimodelform.html` attaches a `change` event listener to `#id_uplfile` that fires a `confirm()` dialog before allowing the replacement. The old file is deleted server-side by `FileToolForm.__init__` when `uplfile` is in `changed_data`.

After saving (add or edit), the form redirects to `tool_view` (not back to the list).

---

## Forms (`forms/unimodelform.html`)

- Extends `_basenarrow.html`
- **Sticky action bar at top** (`sticky top-14 z-10`): Back link | page title | flex spacer | Delete (conditional) | Cancel | ✓ Submit
- Submit button uses `form="uni-form"` to associate with the form element below it
- Delete button uses `confirm()` JavaScript dialog, hidden inside its own mini `<form method="POST">`
- Form card below sticky bar with `id="uni-form"` — no buttons at the bottom of the form
- Renders fields via `{% for field in form %}` loop
- Skips `annoyance` field: `{% if field.html_name != 'annoyance' %}`
- Suppresses built-in `help_text` for phone field (replaced with custom tip): `{% if field.help_text and field.html_name != 'phone' %}`
- Custom phone tip: *"Optional country code: +1 (212) 555-1234 — or with extension: (212) 555-1234 x302"*
- CSS in `{% block extra_css %}` styles Django-generated markup (`.tw-form input`, `.tw-form label`, etc.)
- Quill editor wired up in views that pass `needquillinput: True`
- EasyMDE editor wired up when `needeasymde: True` is in context (Secret Notes form). Attaches to `#id_note_text`. Includes markdown file import toolbar button (replace or append with `---` separator).
- File deletion warning when `has_existing_file: True` — JS `confirm()` fires on file input change
- **Wiki articles do not use this form** — they use `forms/wikieditform.html` instead

### Context variables for unimodelform
| Variable | Meaning |
|----------|---------|
| `minititle` | Page heading in sticky bar and `<title>` |
| `backurl` | URL for Back link and Cancel link |
| `submbutton` | Label for the Submit button (e.g. "Save Client") |
| `deletebutton` | Label for the Delete button — omit or falsy to hide it |
| `targetid` | Record PK for edit mode; `-1` or omitted for add mode |
| `action` | `"edit"` or `"add"` (passed as hidden input) |
| `needeasymde` | Load EasyMDE CSS/JS and init on `#id_note_text` (Secret Notes) |
| `has_existing_file` | Show file replacement warning JS (FileTool edit) |
| `existing_file_name` | Filename shown in the replacement confirm dialog |

---

## Secret Notes

Five templates cover the Secret Notes module:

### List page (`views/allsecretnotes.html`)
- Extends `_basenorm.html`. `overflow: hidden` on body (DataTable scrollY model).
- Sticky header: title + subtitle | filter tabs (Available / Unavailable / All) | search | New Note button
- Filter tab active state via `request.resolver_match.kwargs.reqtype`:
  - `''` or `None` → Available tab active (default — server only sends available rows via `show_available`)
  - `'u'` → Unavailable tab active
  - `'a'` → All tab active
- Table columns: Subject | Created for | Status | Reads left | Expires on | Actions
- Status badge: `bg-emerald-50 text-emerald-700` "Available" / `bg-slate-100 text-slate-500` "Unavailable"
- Reads left shows `N/max` format only when `note.viewlimited`; Expires shows `Y-m-d` only when `note.expires`

### Internal admin view (`views/secretnoteinternal.html`)
- Extends `_basewide.html`. Sticky action bar: ← All notes | note subject | **Edit note** button
- Amber warning banner when note expires; blue banner when read-limited (shows reads_left)
- Content card: sharing link row + contact email row in header; body renders Quill (legacy) or marked.js (new markdown) depending on `is_quill_content()`
- Unavailable state: centered lock-icon card with contextual message (expired / out of reads / generic)
- Note: `needquillinput: True` is set by the view — Quill CDN is loaded for backward-compat display

### External gated view (`views/secretnoteopen.html`)
- Extends `_basewide.html`. Centered `max-w-2xl` layout. No auth required.
- Shows note subject, expiry/read-limit warnings, lock icon, and "Read note now" button → `note.generate_link_external_open`
- Unavailable state: same lock-icon card pattern

### External content view (`views/secretnoteclose.html`)
- Extends `_basewide.html`. Centered `max-w-2xl` layout. No auth required.
- Shows note subject + Quill content via `note.get_external_object` (increments read counter)
- Unavailable state: same lock-icon card pattern

### Note form
- Uses `forms/unimodelform.html` (the shared generic form) — no custom template needed
- `needeasymde: True` loads EasyMDE for `note_text` (plain Textarea field, stores Markdown)
- EasyMDE toolbar includes markdown file import button (replace or append)
- Display templates check `is_quill_content()` for backward compat — legacy Quill JSON renders via `maybequill.html`, new markdown renders via `marked.js`
- Context: `minititle`, `submbutton`, `backurl`, `deletebutton` (on edit), `targetid`, `action`

---

## Projects module (`views/allprojects.html`, `views/archivedprojects.html`)

- Extends `_basenorm.html` (projects list) / `_basewide.html` (archived).  `overflow: auto; height: auto` — NOT `overflow:hidden` (page-level scroll, not DataTable scroll model).
- Sticky header: Projects | Archived (with count badge) | flex-1 | Refresh | New Project
- Project cards: `id="proj-{id}" data-project-id="{id}"` for SortableJS targeting
- **SortableJS 1.15.0**: `Sortable` on `#projects-sortable` (project cards) and each `tbody.tasks-sortable` (task rows); `onEnd` POSTs `{type:'project'|'task', order:[{id,order},...]}` to `/projects/reorder`
- **localStorage collapse state**: key `project_collapsed_{user_id}_{project_id}`; restored in DOMContentLoaded; chevron rotated `-90deg` when collapsed
- **Client-side column sort** (`sortTasks(projectId, col)`): reads `data-title`/`data-status`/`data-priority`/`data-assigned`/`data-due` from `<tr>` rows, appends sorted rows back into `<tbody id="task-list-{id}">`; sort indicator `▲`/`▼` shown in header `<span class="sort-indicator">`
- **Table structure**: `table-fixed` + `<colgroup>` (28px drag | flex title | 130px status | 100px priority | 130px assigned | 90px due | 58px actions); columns hidden with `hidden md:table-cell` / `hidden lg:table-cell` on mobile
- **Archive**: form POST `action=archive` → `edit_project` → `redirect('all_projects')`; Restore: `action=unarchive` → `redirect('archived_projects')`
- **Task status dropdown**: status column uses Alpine.js `position:fixed` badge dropdown (same pattern as Todo status — see below); `quickUpdateTaskStatus(taskId, value, label)` updates badge DOM + `row.dataset.status` + fires AJAX; `refreshBadge(pid)` counts open tasks via `row.dataset.status !== 'done'`
- **Task priority quick-edit**: inline `<select class="inline-select priority-{val}">` for priority POSTs via `quickUpdateTask()` AJAX; color class updated via `refreshBadge()`
- **Two-letter initials**: task rows show creator avatar (slate, 2 initials) `→` assignee avatar (blue, 2 initials) above task title; `title` attr shows full name on hover; `projectviews.py` uses `prefetch_related('tasks__created_by')` to avoid N+1
- **Sort persistence**: `sortTasks(projectId, col)` saves `{col, dir}` to localStorage key `project_tasks_sort_{user_id}_{project_id}`; DOMContentLoaded restores sort for each project via `_applySortTasks(tbody, col, dir)` helper
- **Four modals**: New Project / Edit Project (title, description, status, priority, due date, color swatches) / Add Task / Edit Task (title, description, status, priority, assigned to, created by read-only, start date, due date); all reload page on success

## Todo module (`views/todos.html`)

- Extends `_basenorm.html`. No DataTables. Natural page scroll (`overflow: auto`).
- **Two tabs**: "Personal" and "Shared" — `localStorage` per user remembers active tab (`todo_active_tab_{user_id}`).
- **Flat table per panel**: single `<table>` with columns: drag | task | status | priority | assigned | due | actions. No collapsible sections.
- `tbody` IDs: `todo-tbody-personal` / `todo-tbody-shared`. Rows carry `data-todo-id`, `data-title`, `data-status`, `data-priority`, `data-due`.
- **Status badge dropdown** — `position:fixed` z-index pattern (see below): Alpine.js `x-data="{ open:false }"` per row; `x-init` + `$watch('open', …)` positions the dropdown via `getBoundingClientRect()` when opened.
- **Add/Edit modals**: project-task modal style — `.modal-backdrop` (fixed overlay), `.modal-header` (title + X button), `.modal-body` (mf-* labelled fields), `.modal-footer` (action buttons); `openAddTodoModal()` resets all fields + focuses title; `openEditTodo()` populates fields + focuses title; Assign-to row visible for shared scope only.
- **SortableJS drag-drop**: `Sortable` on each `<tbody>`; drag handles visible on all screen sizes (mobile included); `onEnd` sends `{todo_id, new_status:null, order:[]}` to `POST /todo/reorder` (reorder only, no status change).
- **Column sort**: `sortTodos(panel, col)` saves `{col, dir}` to localStorage key `todo_sort_{user_id}_{panel}`; restored in DOMContentLoaded via `_applyTodoSort(tbody, col, dir)` helper; priority order: high→medium→low; sort indicators per table.
- **Two-letter initials (shared panel)**: rows show creator avatar (slate, 2 initials) `→` assignee avatar (blue, 2 initials); personal panel has no assignee column.
- **Quick-add form**: below each table; `scope` hidden input.
- **Auto-archive**: `all_todos` view bulk-archives done todos with `completed_on <= now - 14 days`.
- **Shared Assign-to**: assignee shown as avatar (2 initials) in Assigned column; personal column shows "—".

### Status dropdown z-index fix (`position:fixed` + Alpine.js `x-init`)

Dropdowns inside `<td>` elements are clipped by `overflow:hidden` on ancestor elements. Fix: render the dropdown with `position:fixed; z-index:9999` and use Alpine.js to position it to match the trigger button when opened.

```html
<div x-data="{ open: false }" class="inline-block relative">
    <button @click="open = !open" class="...badge...">Label <svg chevron/></button>
    <div x-show="open"
         x-cloak
         @click.outside="open = false"
         x-init="$watch('open', function(v){
             if(v){
                 var r = $el.previousElementSibling.getBoundingClientRect();
                 $el.style.top  = r.bottom + 'px';
                 $el.style.left = r.left   + 'px';
             }
         })"
         style="position:fixed; z-index:9999;"
         class="bg-white border border-slate-200 rounded-lg shadow-lg py-1 min-w-[120px]">
        <!-- dropdown items -->
    </div>
</div>
```

Use this pattern for any status/priority dropdown inside a table row. The `x-init` + `$watch` approach re-measures position every time the dropdown opens, keeping it correct after scroll or resize.

---

## Key template files

| File | Purpose |
|------|---------|
| `_base.html` | Root shell: sidebar, topbar, font/CDN loading, Alpine init |
| `_basenarrow.html` | `max-w-2xl` centered wrapper |
| `_basenorm.html` | `max-w-5xl` centered wrapper |
| `_basewide.html` | Full-width wrapper |
| `index.html` | Home dashboard — 3-col icon card grid |
| `views/allclients.html` | Clients list: DataTable + scrollY + inline search |
| `views/allpeople.html` | People list: DataTable + scrollY + inline search |
| `views/allwiki.html` | Wiki list: DataTable + scrollY + inline search |
| `views/alltools.html` | Tools list: DataTable + filter tabs (All/Links/Files) + inline search |
| `views/client.html` | Client detail: General Info + People sections only |
| `views/wikiview.html` | Wiki article view: sticky action bar, Quill/Markdown compat |
| `views/components/generalinfoclient.html` | Address/phone/description definition list |
| `views/components/phonenumber.html` | Phone tel: link component |
| `views/components/people.html` | People table within client detail |
| `views/oneitemrow/clientrow.html` | Single client table row |
| `views/oneitemrow/personrow.html` | Person row used inside client detail |
| `views/oneitemrow/allpeoplerow.html` | Person row used in all-people list |
| `views/oneitemrow/wikirow.html` | Wiki article row in list |
| `views/toolview.html` | Tool detail view: sticky bar with Edit tool button, type/link/description/visibility |
| `views/oneitemrow/onetoolrow.html` | Tool row: name, link (2-line clamp), description (2-line clamp), visibility badge, created on, View button |
| `views/allsecretnotes.html` | Secret notes list: DataTable + filter tabs (Available/Unavailable/All) + search |
| `views/secretnoteinternal.html` | Internal admin note view: sticky bar, warnings, sharing link, Quill content |
| `views/secretnoteopen.html` | External gated view: subject + "Read note now" button |
| `views/secretnoteclose.html` | External content view: shows note text or unavailable state |
| `views/oneitemrow/secretnoterow.html` | Note row: subject, email link, status badge, reads, expiry, View |
| `views/modals/personmodal.html` | Alpine.js person detail/edit modal |
| `forms/unimodelform.html` | Generic add/edit form with sticky top action bar (clients, people, tools, etc.) |
| `forms/wikieditform.html` | Wiki-specific editor with EasyMDE + sticky action bar |
| `forms/widget/maybequill.html` | Renders Quill JSON or plain text (legacy wiki only) |
| `views/allfiles.html` | Shared files list: DataTable, search, View action only (Copy/Delete on detail page), Upload Links button |
| `views/uploadlinks.html` | Upload Links list: Title, Created, Expires, Files, Status, View + Edit actions |
| `views/createuploadlink.html` | Create Upload Link form: title, instructions, expiry days, max files (default: 1) |
| `views/viewuploadlink.html` | Upload Link detail: shareable URL with copy, file table with downloads, Edit + deactivate + delete |
| `views/edituploadlink.html` | Edit Upload Link form: pre-filled title, instructions, optional expiry extension, max files |
| `views/clientuploadpage.html` | Public upload page (no auth): multi-file upload form, success state |
| `views/uploadlinkexpired.html` | Public error page for expired/inactive upload links |
| `views/uploadfile.html` | File upload form: file, description, expires_days (1–90), max_downloads |
| `views/fileview.html` | File detail: info grid, public URL with copy button, download log table (last 50) |
| `views/editfile.html` | File edit form: description, expiry extension, download limit (extends `_basenarrow.html`) |
| `views/fileexpired.html` | Public error page for expired / limit-reached / not-found shared files |
| `views/help.html` | Help page: full portal guide rendered from inline Markdown via marked.js |
| `views/allprojects.html` | Projects list: cards, SortableJS drag-drop, modals, archive, column sort |
| `views/archivedprojects.html` | Archived projects: ← Back, Restore (unarchive) + Delete, read-only tasks |
| `views/todos.html` | To-Do List: Personal + Shared tabs, flat table per panel, `position:fixed` status dropdown, centralized edit modal, SortableJS drag-drop, assignee avatars, auto-archive |
| `views/archivedtodos.html` | Archived tasks: ← To-Do, Restore + Delete, scope/priority badges, completed/archived dates |
| `views/admin_portal.html` | Admin dashboard: stats cards, quick-action cards, recent login activity table |
| `views/admin_users.html` | User management: table of all users, add/edit/delete, role badges, JS delete via fetch |
| `views/admin_user_form.html` | Add / edit user form: first/last name, email (= username), password, role select (User/Staff/Admin — superuser only); amber warning when editing own account |
| `views/admin_login_logs.html` | Login log viewer: timestamp, user/email, IP, success/fail badge; last 300 records |
| `views/admin_403.html` | Access denied page for non-staff users attempting to reach admin URLs |
