# Claude Working Notes — Infotek IT Portal

## Project overview

Django 4.2 / Python 3.12 IT management portal for Infotek Solutions & Support.
Redesigned UI from Foundation CSS to Tailwind CSS + Alpine.js.
Runs on Apache + mod_wsgi at `https://192.168.10.35` (also `https://localhost`).
Files live on a network share: `\\192.168.10.35\website\clientmanagement\`.

---

## Critical constraints

### No dev server
The app runs on Apache. There is no `runserver` — never start one.
Test by visiting `https://192.168.10.35` directly in the browser.

### mod_wsgi bytecode caching
**Python file changes require an Apache restart to take effect.**
Template (`.html`) changes are immediate — no restart needed.

When you need to change logic that would normally require Python:
- Prefer template-only solutions using Django template tags and ORM accessors
- Example: rendering person emails in the client list uses `{% for p in obj.employees.all %}{{ p.email }}{% endfor %}` directly in the template rather than passing data from `modelgetters.py`

### No git worktrees or pull requests
Edit files directly on the network path. No git workflow.

### No Foundation CSS/JS
Foundation has been completely removed. Do not add it back.
Replace any remaining Foundation patterns:
- Reveal modals → Alpine.js `x-show="open"` modals
- Foundation confirm dialogs → `onclick="if(confirm('...')) this.closest('form').submit()"`
- Foundation accordion → Tailwind card sections
- `$.fn.foundation` shim exists in `_base.html` to silence any lingering JS errors

---

## File locations

```
\\192.168.10.35\website\clientmanagement\
├── clientmanagement/
│   ├── modelgetters.py       # Data-gathering functions for views
│   ├── views.py              # Django views
│   ├── urls.py               # URL routing
│   └── templates/
│       ├── _base.html        # Root shell (sidebar, topbar, CDN loading)
│       ├── _basenarrow.html  # max-w-2xl wrapper (forms)
│       ├── _basenorm.html    # max-w-5xl wrapper (list pages)
│       ├── _basewide.html    # Full-width wrapper
│       ├── index.html        # Home dashboard
│       ├── forms/
│       │   └── unimodelform.html   # Shared add/edit form
│       └── views/
│           ├── allclients.html
│           ├── allpeople.html
│           ├── client.html
│           ├── components/
│           │   ├── generalinfoclient.html
│           │   ├── people.html
│           │   └── phonenumber.html
│           ├── modals/
│           │   └── personmodal.html
│           └── oneitemrow/
│               ├── clientrow.html
│               ├── personrow.html      # Used in client detail
│               └── allpeoplerow.html   # Used in all-people list
├── models/                   # Django model files (one per entity)
├── CLAUDE.md                 # This file
└── DESIGN.md                 # Design system reference
```

---

## Django model key facts

### Person
- Fields: `firstname`, `lastname`, `email`, `phone` (django-phonenumber-field), `description`, `annoyance` (not used), `employedby` (FK to Client)
- `name` property → `firstname + lastname`
- `employedby` reverse accessor on Client: `client.employees` (related_name='employees')

### Client
- Fields: `name`, `phone`, `address`, `description`
- `client.employees.all()` → all Person objects for that client
- `client.employees.values_list('email', flat=True)` → email list

### Annoyance field
Exists on the Person model but is **not used anywhere in the UI**.
Excluded from form rendering via: `{% if field.html_name != 'annoyance' %}` in `unimodelform.html`.
Do not display it in any view.

---

## CDN versions (do not change without testing)

| Library | Version | Notes |
|---------|---------|-------|
| Tailwind CSS | CDN (latest) | `cdn.tailwindcss.com` — no build step |
| Alpine.js | 3.x.x | `cdn.jsdelivr.net/npm/alpinejs@3.x.x` |
| jQuery | 3.7.0 | Required by DataTables |
| DataTables | 1.13.7 | `cdn.datatables.net/1.13.7` |
| DataTables FixedHeader | 3.4.0 | `cdn.datatables.net/fixedheader/3.4.0` |
| Quill | 1.3.6 | Loaded only when `needquillinput: True` in context |
| Google Fonts | — | DM Sans, JetBrains Mono |

---

## Context variables conventions

| Variable | Where set | Meaning |
|----------|-----------|---------|
| `needdatatables` | view context | Load DataTables CDN; render `<script>` init block |
| `needquillinput` | view context | Load Quill CDN |
| `clid` | personmodal include | Client ID for "Edit person" form action |
| `fullinfo` | personrow/allpeoplerow include | Show Company column in row and modal |

---

## Common patterns

### Adding a new list page
1. Create `views/allXXX.html` extending `_basenorm.html`
2. Add sticky `id="page-header"` div with `sticky top-14 z-10 bg-slate-50 -mx-6 px-6`
3. Create table with thead; hidden search columns go **last**
4. Create `views/oneitemrow/XXXrow.html` with exactly matching column count
5. Set `needdatatables: True` in view, add DataTable init with FixedHeader

### Alpine.js modal pattern
```html
<!-- Trigger cell -->
<td x-data="{ open: false }">
    <button @click="open = true" class="...outline button...">Details</button>
    {% include "views/modals/personmodal.html" with person=person %}
</td>
```
`x-data` goes on `<td>`, not `<tr>`, to avoid breaking HTML table structure.

### Searchable hidden column (DataTables)
```html
<!-- thead: declare column -->
<th>Emails</th>

<!-- tbody row: render data, no CSS hiding -->
<td>{% for p in obj.employees.all %}{% if p.email %}{{ p.email }} {% endif %}{% endfor %}</td>
```
```javascript
// DataTable config: hide via JS only
{ "visible": false, "targets": [N] }
```
Never use `class="hidden"` — DataTables reads DOM before Tailwind would hide it in normal usage, but FixedHeader and other extensions can be confused.

### Phone display
Always use `{% include "views/components/phonenumber.html" with phone=obj.phone %}`.
Do not render phone numbers as raw text.

### Email display (inline, not component)
```html
<a href="mailto:{{ obj.email }}" class="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-800 transition-colors text-sm">
    <svg class="w-3.5 h-3.5 shrink-0" ...envelope icon.../>
    {{ obj.email }}
</a>
```

---

## Planned features (not yet built)

- **Files** — temporary file sharing module (nav shows "Soon" badge)
- **Projects** — task/project management module (nav shows "Soon" badge)
- **Wiki styling** — wiki pages need Tailwind redesign
- **Tools page styling** — tools list needs Tailwind redesign
- **Secret Notes styling** — notes pages need Tailwind redesign
- **Claude AI wiki assistant** — AI helper for wiki content

---

## What's been completed

- [x] `_base.html` — full Tailwind sidebar shell
- [x] `_basenarrow.html`, `_basenorm.html`, `_basewide.html`
- [x] `index.html` — home dashboard with icon cards
- [x] `views/allclients.html` — clients list, DataTable, sticky header, email search
- [x] `views/allpeople.html` — people list, DataTable, sticky header, modal details
- [x] `views/client.html` — client detail (General Info + People only)
- [x] `views/components/generalinfoclient.html` — address, phone, description
- [x] `views/components/phonenumber.html` — phone tel: link
- [x] `views/components/people.html` — people table in client detail
- [x] `views/oneitemrow/clientrow.html` — client row with outline View button
- [x] `views/oneitemrow/personrow.html` — person row in client detail
- [x] `views/oneitemrow/allpeoplerow.html` — person row in all-people list
- [x] `views/modals/personmodal.html` — Alpine.js modal, Edit works from both views
- [x] `forms/unimodelform.html` — shared form, skips annoyance field
