# Design System — Infotek IT Portal

## Stack

| Layer | Technology | Source |
|-------|-----------|--------|
| CSS framework | Tailwind CSS v3 | CDN (`cdn.tailwindcss.com`) |
| Interactivity | Alpine.js v3 | CDN (`cdn.jsdelivr.net/npm/alpinejs@3.x.x`) |
| Tables | DataTables 1.13.7 + FixedHeader 3.4.0 | CDN (`cdn.datatables.net`) |
| Rich text | Quill 1.3.6 | CDN (loaded only when `needquillinput` is set) |
| Fonts | DM Sans (400–700), JetBrains Mono | Google Fonts |
| Backend | Django 4.2 / Python 3.12 | Apache + mod_wsgi |

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
- **Section subtitle**: `text-sm text-slate-500`
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
    <main.p-6>     ← page content area (bg-slate-50)
    <footer>       ← thin border-top footer
```

**Sidebar toggle**: Alpine.js `x-data="{ sidebarOpen: window.innerWidth >= 1024 }"` on `<body>`. Open by default on desktop, closed on mobile.

### Content widths
| Template | Width | Use |
|----------|-------|-----|
| `_basenarrow.html` | `max-w-2xl mx-auto` | Forms, single-item detail |
| `_basenorm.html` | `max-w-5xl mx-auto` | List pages (Clients, People) |
| `_basewide.html` | full width | Dashboards, statistics |

### Sticky page header pattern (list pages)
```html
<div id="page-header" class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-4 border-b border-slate-200">
    <!-- title + optional action button -->
</div>
<div class="bg-white rounded-xl border border-slate-200 overflow-hidden mt-4">
    <table>...</table>
</div>
```
`-mx-6 px-6` cancels out `<main>`'s `p-6` so the sticky bar bleeds full-width behind the content.

DataTables FixedHeader offset is calculated in JS:
```javascript
var topbarH = 56;   // h-14 = 56px, always constant
var pageHeaderH = document.getElementById('page-header').offsetHeight;
// passed to fixedHeader: { headerOffset: topbarH + pageHeaderH }
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
<a/button class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors">
```

### Secondary / outline button (View, Details, Edit)
```html
<button class="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white border border-slate-200 rounded-md hover:bg-slate-50 transition-colors">
```

### Destructive button (Delete)
```html
<button class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
        onclick="if(confirm('Are you sure you want to delete?')) this.closest('form').submit()">
```
No Foundation modals — uses native `confirm()`.

### Phone link (`views/components/phonenumber.html`)
Blue `tel:` link with phone icon. Shows national format for +1 numbers, international otherwise.

### Email link (inline)
```html
<a href="mailto:{{ person.email }}" class="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-800 transition-colors">
    <svg ...envelope icon.../>
    {{ person.email }}
</a>
```

### Person detail modal (`views/modals/personmodal.html`)
Alpine.js modal. Triggered by `x-data="{ open: false }"` on the parent `<td>`. Backdrop click and Escape key close it. Footer shows Edit button if a `clientid` is resolvable (either `clid` passed explicitly, or `person.employedby_id` as fallback).

---

## Navigation

Sidebar sections: **Main** → Home, Clients, People | **Tools** → Wiki, Tools, Secret Notes, Files (Soon) | **Work** → Projects (Soon) | **System** → Statistics, Updates, Users (staff only)

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
- Use `visible: false` on hidden-but-searchable columns — **never** `class="hidden"` (breaks column indexing)
- Hidden columns must be **last** in both `<thead>` and `<tbody>`
- FixedHeader extension always active on list pages; offset = topbar (56px) + sticky page header height
- Standard config:
```javascript
$('#mytable').DataTable({
    "lengthMenu": [[10, 25, 50, -1], [10, 25, 50, "All"]],
    "iDisplayLength": -1,
    "order": [[0, "asc"]],
    "columnDefs": [
        { "orderable": false, "targets": [...] },
        { "visible": false, "targets": [...] }   // only if hidden cols
    ],
    "fixedHeader": { "header": true, "headerOffset": topbarH + pageHeaderH }
});
```

---

## Forms (`forms/unimodelform.html`)

- Extends `_basenarrow.html`
- Renders fields via `{% for field in form %}` loop
- Skips `annoyance` field: `{% if field.html_name != 'annoyance' %}`
- CSS in `{% block extra_css %}` styles Django-generated markup (`.tw-form input`, `.tw-form label`, etc.)
- Quill editor wired up in views that pass `needquillinput: True`
- Delete button uses `confirm()` JavaScript dialog, not a modal

---

## Key template files

| File | Purpose |
|------|---------|
| `_base.html` | Root shell: sidebar, topbar, font/CDN loading, Alpine init |
| `_basenarrow.html` | `max-w-2xl` centered wrapper |
| `_basenorm.html` | `max-w-5xl` centered wrapper |
| `_basewide.html` | Full-width wrapper |
| `index.html` | Home dashboard — 3-col icon card grid |
| `views/allclients.html` | Clients list with DataTable + sticky header |
| `views/allpeople.html` | People list with DataTable + sticky header |
| `views/client.html` | Client detail: General Info + People sections only |
| `views/components/generalinfoclient.html` | Address/phone/description definition list |
| `views/components/phonenumber.html` | Phone tel: link component |
| `views/components/people.html` | People table within client detail |
| `views/oneitemrow/clientrow.html` | Single client table row |
| `views/oneitemrow/personrow.html` | Person row used inside client detail |
| `views/oneitemrow/allpeoplerow.html` | Person row used in all-people list |
| `views/modals/personmodal.html` | Alpine.js person detail/edit modal |
| `forms/unimodelform.html` | Generic add/edit form (shared across models) |
