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

### Make backups before editing
Before modifying any file that is not a simple CSS/text fix, create a `.bak` copy:
```bash
cp path/to/file.html path/to/file.html.bak
cp path/to/file.py path/to/file.py.bak
```
This allows restoring originals if something breaks.

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
│   ├── widget/
│   │   └── quill.py          # Quill widget + QuillObject class (legacy)
│   └── templates/
│       ├── _base.html        # Root shell (sidebar, topbar, CDN loading)
│       ├── _basenarrow.html  # max-w-2xl wrapper (forms)
│       ├── _basenorm.html    # max-w-5xl wrapper (list pages, wiki editor)
│       ├── _basewide.html    # Full-width wrapper (external/public pages only)
│       ├── index.html        # Home dashboard
│       ├── forms/
│       │   ├── unimodelform.html     # Shared add/edit form (clients, people, etc.)
│       │   ├── wikieditform.html     # Wiki-specific EasyMDE editor
│       │   └── widget/
│       │       ├── maybequill.html   # Renders Quill JSON or plain text (legacy)
│       │       ├── maybequilltext.html
│       │       └── quill.html        # Quill widget template
│       └── views/
│           ├── allclients.html
│           ├── allpeople.html
│           ├── allwiki.html
│           ├── alltools.html
│           ├── toolview.html
│           ├── allsecretnotes.html
│           ├── allfiles.html
│           ├── uploadfile.html
│           ├── fileview.html
│           ├── editfile.html
│           ├── fileexpired.html
│           ├── client.html
│           ├── wikiview.html
│           ├── secretnoteinternal.html
│           ├── secretnoteopen.html
│           ├── secretnoteclose.html
│           ├── help.html
│           ├── components/
│           │   ├── generalinfoclient.html
│           │   ├── people.html
│           │   └── phonenumber.html
│           ├── modals/
│           │   └── personmodal.html
│           └── oneitemrow/
│               ├── clientrow.html
│               ├── personrow.html      # Used in client detail
│               ├── allpeoplerow.html   # Used in all-people list
│               ├── wikirow.html        # Used in wiki list
│               ├── onetoolrow.html     # Used in tools list
│               └── secretnoterow.html  # Used in secret notes list
├── models/
│   ├── wikiarticleform.py    # Wiki create/edit/delete logic + EasyMDE routing
│   ├── wikiarticle.py        # WikiArticle model
│   └── ...
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

### WikiArticle
- Fields: `title`, `article` (TextField), `keywords` (M2M → Keywords), `postedon`, `updatedon`, `unid` (UUID)
- `article` stores either Quill JSON delta (legacy, starts with `{`) or plain Markdown (new)
- `get_quill_object()` → returns `QuillObject(self.article)` for display
- `QuillObject.is_quill_content()` → `True` if text is valid Quill JSON with `ops` key
- `get_link()` → `reverse("wiki_art", kwargs={"wikiuuid": self.unid})`
- `keywords` is ManyToMany — access in templates with `article.keywords.all`, each has `.word`

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
| EasyMDE | latest | `unpkg.com/easymde/dist/easymde.min.js` — wiki editor |
| marked.js | latest | `cdn.jsdelivr.net/npm/marked/marked.min.js` — markdown render |
| Quill | 1.3.6 | Legacy only. Loaded when `needquillinput: True` in context |
| Google Fonts | — | DM Sans, JetBrains Mono |

---

## Context variables conventions

| Variable | Where set | Meaning |
|----------|-----------|---------|
| `needdatatables` | view context | Load DataTables CDN; render `<script>` init block |
| `needquillinput` | view context | Load Quill CDN (legacy — wiki no longer uses this) |
| `clid` | personmodal include | Client ID for "Edit person" form action |
| `fullinfo` | personrow/allpeoplerow include | Show Company column in row and modal |
| `article_initial` | wikiarticleform.py | Pre-fill EasyMDE with existing article content (plain text) |
| `minititle` | wikiarticleform.py | Page/form heading text |

---

## Common patterns

### Sticky action bar pattern (CRITICAL — always use two-div structure)

All sticky bars use an **outer** full-bleed div and an **inner** max-width div. Never put `flex` on the outer div:

```html
<!-- List page (basenorm, max-w-5xl content) -->
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-4">
<div class="max-w-5xl mx-auto flex items-center gap-4">
    <!-- title | search | button -->
</div>
</div>

<!-- Detail page on _basewide (content is max-w-5xl) -->
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-6">
<div class="max-w-5xl mx-auto flex items-center gap-3">
    <!-- ← Back | title | flex-1 | [action buttons] -->
</div>
</div>

<!-- Detail page on _basenarrow (content is max-w-2xl) -->
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-6">
<div class="max-w-2xl mx-auto flex items-center gap-3">
    <!-- ← Back | title | flex-1 | [action buttons] -->
</div>
</div>
```

The inner max-width **must match** the page content width so buttons align with content edges. Using `_basewide.html` for detail pages: set inner wrapper to `max-w-5xl` and content sections also to `max-w-5xl` (matches list pages).

### Adding a new list page
1. Create `views/allXXX.html` extending `_basenorm.html`
2. Add sticky header div: `sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-4`
3. Include `html, body { overflow: hidden; height: 100%; }` in `{% block extra_css %}`
4. Create table with thead; hidden search columns go **last**
5. Create `views/oneitemrow/XXXrow.html` with exactly matching column count
6. Set `needdatatables: True` in view, add DataTable init with `dom: "t"` and `fitTable()`

### Alpine.js modal pattern
```html
<td x-data="{ open: false }">
    <button @click="open = true" class="...outline button...">View</button>
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
{ "visible": false, "targets": [N] }
```
Never use `class="hidden"`.

### Phone display
Always use `{% include "views/components/phonenumber.html" with phone=obj.phone %}`.
Do not render phone numbers as raw text.

### Email display (inline)
```html
<a href="mailto:{{ obj.email }}" class="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-800 transition-colors text-sm">
    <svg class="w-3.5 h-3.5 shrink-0" ...envelope icon.../>
    {{ obj.email }}
</a>
```

### Wiki content display (backward-compat)
```django
{% if article.get_quill_object.is_quill_content %}
    {% include "forms/widget/maybequill.html" with obj=article.get_quill_object %}
{% else %}
    <div id="article-content" class="wiki-body"></div>
    {# marked.js renders this in {% block extra_javascript %} #}
{% endif %}
```

### Editor page scroll (no overflow:hidden on body)
Do NOT use `overflow: hidden` on `body` for editor pages — it breaks CodeMirror mouse-wheel events. Instead size the `.CodeMirror` div to fill the viewport via `fitEditor()` so there's nothing to page-scroll.

---

## Wiki system — important notes

### Content storage
`WikiArticle.article` is a plain TextField. It stores either:
- **Quill JSON** (legacy): starts with `{`, has `ops` key — detected by `QuillObject.is_quill_content()`
- **Markdown** (new): plain text — rendered with `marked.js` in the browser

### `_get_editable_content(raw_text)` in `wikiarticleform.py`
Converts Quill JSON to editable plain text when opening old articles in EasyMDE. Extracts text from `ops[].insert` string values. New markdown content is passed through unchanged.

### Wiki edit form routing
`wikiarticleform.py` renders `forms/wikieditform.html` (NOT `forms/unimodelform.html`). It does not set `needquillinput`.

### EasyMDE markdown import
Custom toolbar button triggers `<input type="file" accept=".md,.txt,.markdown">`. FileReader reads file → replaces or appends to editor content.

### Print / PDF
`wikiview.html` print CSS hides `aside`, `header`, `footer`, `.no-print`. Resets sidebar margin offset. Sets `overflow: visible` for multi-page print.

---

## Planned features (not yet built)

- **Projects** — task/project management module (nav shows "Soon" badge)
- **Person edit modal** — inline modal instead of full-page form (decided: yes for person, keep full-page for client due to Quill description field)
- **Claude AI wiki assistant** — AI helper for wiki content

---

## What's been completed

- [x] `_base.html` — full Tailwind sidebar shell
- [x] `_basenarrow.html`, `_basenorm.html`, `_basewide.html`
- [x] `index.html` — home dashboard with icon cards
- [x] `views/allclients.html` — clients list, DataTable, sticky header, email search
- [x] `views/allpeople.html` — people list, DataTable, sticky header, modal details
- [x] `views/allwiki.html` — wiki list, DataTable, sticky header, search
- [x] `views/alltools.html` — tools list, DataTable, filter tabs (All/Links/Files), sticky header, search, 2-line clamp on Name/Link/Description, Visibility + Created on sortable, default sort Created on desc, no Type column
- [x] `views/toolview.html` — tool detail view: sticky action bar with Edit tool button, type/link/description/visibility
- [x] `views/client.html` — client detail (General Info + People only)
- [x] `views/wikiview.html` — wiki article view, sticky action bar, Quill/Markdown compat, print CSS
- [x] `views/components/generalinfoclient.html` — address, phone, description
- [x] `views/components/phonenumber.html` — phone tel: link
- [x] `views/components/people.html` — people table in client detail
- [x] `views/oneitemrow/clientrow.html` — client row with outline View button
- [x] `views/oneitemrow/personrow.html` — person row in client detail
- [x] `views/oneitemrow/allpeoplerow.html` — person row in all-people list
- [x] `views/oneitemrow/wikirow.html` — wiki article row
- [x] `views/oneitemrow/onetoolrow.html` — tool row: View button (GET to tool_view), 2-line clamp on Name/Link/Description, visibility badge, created on date (no Type column)
- [x] `views/allsecretnotes.html` — notes list, DataTable, filter tabs, 2-line clamp on Subject/Created for, default sort Expires on desc
- [x] `views/secretnoteinternal.html` — internal admin note view: sticky action bar, "Edit note" button, Quill/Markdown compat
- [x] `views/secretnoteopen.html` — external gated view: shows subject + "Read note now" button
- [x] `views/secretnoteclose.html` — external open view: shows note content or unavailable state
- [x] `views/oneitemrow/secretnoterow.html` — note row: subject, email link, status badge, reads, expiry, View button
- [x] `views/modals/personmodal.html` — Alpine.js modal, Edit works from both views
- [x] `forms/unimodelform.html` — sticky action bar at top; EasyMDE support (`needeasymde`) with .md import; file deletion warning (`has_existing_file`)
- [x] `forms/wikieditform.html` — EasyMDE editor, sticky action bar, markdown import, fitEditor()
- [x] `models/wikiarticleform.py` — routes wiki to EasyMDE form, legacy Quill→text conversion
- [x] `views/allfiles.html` — shared files list, DataTable, sticky header, search, Copy/View/Delete actions
- [x] `views/uploadfile.html` — file upload form: file, description, expires_days (1-90), max_downloads
- [x] `views/fileview.html` — file detail: info grid, public download URL with copy button, download log table
- [x] `views/editfile.html` — file edit form: description, expiry extension, download limit
- [x] `views/fileexpired.html` — public error page for expired/limit-reached/not-found files
- [x] `views/help.html` — Help page: full portal guide in markdown rendered with marked.js; URL `help/`, view `helpview` in views.py
- [x] Layout fixes applied globally:
  - `_base.html` main tag: `p-3 sm:p-6` (mobile padding)
  - `_basenarrow.html`, `_basenorm.html`: added `w-full` to max-width wrappers
  - All sticky action bars: outer div is full-bleed (`-mx-6 px-6`), inner div has explicit max-width matching page content (`max-w-5xl` or `max-w-2xl`) + `flex items-center gap-3`
  - Detail pages (`wikiview`, `toolview`, `secretnoteinternal`, `fileview`): content sections changed from `max-w-4xl` to `max-w-5xl` to match list page width
  - `client.html`: converted simple back-link/h1 to full sticky action bar
  - Mobile column hiding: `hidden md:table-cell` on non-essential `<th>` and `<td>` across all list pages
- [x] Statistics and Updates removed from nav and dashboard; replaced with Help
