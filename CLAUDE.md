# Claude Working Notes — Infotek IT Portal

## Project overview

Django 4.2 / Python 3.12 IT management portal for Infotek Solutions & Support.
Redesigned UI from Foundation CSS to Tailwind CSS + Alpine.js.
Runs on Apache + mod_wsgi at `https://192.168.10.35` (also `https://localhost`).
Files live on a network share: `\\192.168.10.35\website\clientmanagement\`.

---

## Versioning

Current version: **2.3.16**

Format: `MAJOR.MINOR.PATCH`
- **MAJOR** — complete UI/framework overhaul
- **MINOR** — new feature module (new model, new page group)
- **PATCH** — improvements, bug fixes, UX changes within existing features

Rules:
- Version is stored in `clientmanagement/settings/config.py` → `CLIENTMANAGEMENT_VERSION`
- Exposed to templates via `context_processors.py` as both `CLIENTMANAGEMENT_VERSION` and `VERSION`
- Displayed in footer as `v{{ VERSION }}`
- **Always** update `CLAUDE.md` (this file) and `WHATSNEW.md` when completing a session
- At the start of each session the user will say: "We are working on version X.Y.Z. Update WHATSNEW.md and CLAUDE.md DESIGN.md version when done."

## Change tracking rules
- Current version always listed at top of CLAUDE.md
- Every change made in a session must be logged in WHATSNEW.md
- Bugs fixed → add under "Bug fixes" in current version section
- New features → add under "Changes in progress"  
- When version is deployed to production → section becomes official
  (remove "current development" label, add deployment date)
- Never list features in WHATSNEW.md that are not yet built
- File is named WHATSNEW.md (not THATSNEW.md)

---

## Critical rules — read first
- Always read CLAUDE.md and DESIGN.md completely before making any changes
- Always update CLAUDE.md and DESIGN.md to reflect completed changes
- Always check if Help page needs updating when adding new features
- All file edits are pre-approved — proceed without asking for confirmation
- Do not use git worktrees or pull requests — edit files directly on the network path
- Make .bak copies before editing any existing file

## Servers
- Dev server: `\\192.168.10.35\website\clientmanagement` → https://192.168.10.35
- Production: `\\192.168.10.34\website\clientmanagement` → https://cms.isstek.com
- All development work happens on dev server (.35)
- Production gets updates via: git pull + migrate + Apache restart

## No dev server
The app runs on Apache. Never start `runserver`.
Cannot test in browser directly — human tests and reports back.

## After Python file changes always tell human to run:
```cmd
python manage.py migrate
net stop Apache2.4
net start Apache2.4
```
Template (.html) changes are immediate — no restart needed.

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
│       ├── _basenarrow.html  # max-w-5xl wrapper (forms — same width as list pages)
│       ├── _basenorm.html    # max-w-5xl wrapper (list pages, wiki editor)
│       ├── _basewide.html    # Full-width wrapper (detail/view pages + external pages)
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
│           ├── allprojects.html        # Projects list: cards, SortableJS, modals, archive
│           ├── archivedprojects.html   # Archived projects: Restore + Delete buttons
│           ├── todos.html              # To-Do List: Personal + Shared tabs, flat table, position:fixed status dropdown, edit modal, auto-archive
│           ├── archivedtodos.html      # Archived tasks: Restore + Delete, scope/priority badges
│           ├── uploadlinks.html        # Upload Links list: View action only (Edit via View page)
│           ├── createuploadlink.html   # Create upload link form
│           ├── viewuploadlink.html     # Upload link detail: shareable URL, uploaded files, Edit + Deactivate + Delete
│           ├── edituploadlink.html     # Edit upload link form: title, instructions, expiry, max files
│           ├── clientuploadpage.html   # Public client upload page (no auth required)
│           ├── uploadlinkexpired.html  # Public error page for expired/inactive links
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
│   ├── project.py            # Project, Task, Todo models + _to_date() helper
│   ├── projectviews.py       # All project/task/todo CRUD views
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

### Project
- Fields: `title`, `description`, `color` (hex from `COLOR_CHOICES`), `status` (`active`/`onhold`/`completed`/`cancelled`), `priority` (`critical`/`high`/`medium`/`low`), `due_date`, `is_archived`, `order`, `created_on`, `created_by` (FK User)
- `open_tasks_count` property → count of non-done root tasks
- Migration chain: `0058_project_task` → `0059_project_status_priority_due` → `0060_todo`
- `_to_date(val)` module-level helper in `project.py` safely coerces None/string/date to `datetime.date`

### Task
- Fields: `project` (FK Project), `title`, `description`, `status` (`notstarted`/`inprogress`/`done`/`blocked`/`onhold`), `priority`, `assigned_to` (FK User, nullable), `start_date`, `due_date`, `parent_task` (self-FK, nullable), `order`, `created_on`, `created_by`
- `is_overdue()`, `is_due_soon()`, `days_until_due()`, `timeline_percent()` — use `_to_date()` internally
- `subtasks` reverse accessor for child tasks
- Root tasks: `parent_task=None`; in templates use `{% if not task.parent_task_id %}`

### Todo
- Fields: `user` (FK User), `assigned_to` (FK User, nullable, `related_name='assigned_todos'`), `title`, `description`, `scope` (`personal`/`shared`), `status` (`todo`/`inprogress`/`done`), `priority` (`high`/`medium`/`low`), `due_date`, `order`, `created_on`, `completed_on`, `is_archived`, `archived_on`
- `STATUS_CHOICES` labels: `todo` → "Not started", `inprogress` → "In progress", `done` → "Done"
- `is_overdue()` → True if due_date < today and status != done
- `auto_archive_in_days()` → days until 14-day auto-archive fires (returns None if not applicable)
- Personal todos: filtered by `user=request.user, scope='personal'`; shared todos: `scope='shared'` (all users can edit)
- `assigned_to` is only relevant on shared todos; personal todos ignore it
- Toggle action (`action=toggle`): `done → inprogress` (not `done → todo`); `any other → done`
- Auto-archive: on page load, done todos with `completed_on <= now - 14 days` are bulk-updated `is_archived=True`
- Manual archive: `action=archive` on edit_todo view; restore: `action=unarchive`
- Archived todos page at `/todo/archived` (name `archived_todos`)
- Migration chain: `0060_todo` → `0061_todo_scope_archive` → `0062_uploadlink_clientuploadedfile` → `0063_todo_assigned_to`

### UploadLink
- Fields: `unid` (UUID), `title`, `description`, `created_by` (FK User, nullable), `created_on`, `expires_on`, `is_active`, `max_files`
- `is_expired()` → `expires_on < today`
- `is_available()` → `is_active and not is_expired()`
- `get_upload_url()` → reverse `client_upload_page` with `linkuuid=self.unid`
- File in `models/uploadlink.py`; `app_label` auto-detected as `models`

### ClientUploadedFile
- Fields: `upload_link` (FK UploadLink, `related_name='uploaded_files'`), `uplfile` (FileField, `upload_to=upload_to_client`), `original_filename`, `uploaded_at`, `ip_address`, `file_size`
- Files stored at `client_uploads/<uuid_hex>/<filename>`
- File in `models/uploadlink.py`

### LoginLog
- Fields: `user` (FK User nullable, `related_name='login_logs'`), `username_attempted`, `ip_address`, `timestamp`, `success` (bool), `user_agent`
- Auto-created via Django auth signals (`user_logged_in`, `user_login_failed`) connected in `models/apps.py` `ready()`
- Signal handlers in `models/loginlog.py`: `log_successful_login` and `log_failed_login`
- File in `models/loginlog.py`; `app_label = 'models'`

### Annoyance field
Exists on the Person model but is **not used anywhere in the UI**.
**Excluded from `PersonForm.Meta.fields`** — it is NOT in the ModelForm at all. Django uses the model's `default='0'` automatically when saving. The template filter `{% if field.html_name != 'annoyance' %}` in `unimodelform.html` is now redundant but harmless.
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
| SortableJS | 1.15.0 | `cdn.jsdelivr.net/npm/sortablejs@1.15.0` — drag-and-drop for projects/tasks |
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

<!-- Form page on _basenarrow (content is max-w-5xl — same as list pages) -->
<div class="sticky top-14 z-10 bg-slate-50 -mx-6 px-6 py-3 border-b border-slate-200 mb-6">
<div class="max-w-5xl mx-auto flex items-center gap-3">
    <!-- ← Back | title | flex-1 | [Cancel] [✓ Save] -->
</div>
</div>
```

**All levels use `max-w-5xl`** — list pages, view/detail pages, and edit/add forms are all the same width. The inner max-width must always match the page content width so buttons align with content edges.

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
  - `_basenarrow.html`: changed from `max-w-2xl` to `max-w-5xl` — all three levels (list/view/edit) now use the same width
  - `unimodelform.html`, `uploadfile.html`: fixed action bars from old single-div to two-div pattern with `max-w-5xl mx-auto` inner wrapper
  - `editfile.html`: action bar inner wrapper updated from `max-w-2xl` to `max-w-5xl`
  - `client.html`: converted simple back-link/h1 to full sticky action bar
  - Mobile column hiding: `hidden md:table-cell` on non-essential `<th>` and `<td>` across all list pages
- [x] Statistics and Updates removed from nav and dashboard; replaced with Help
- [x] **Projects module** (`models/project.py`, `models/projectviews.py`, `views/allprojects.html`):
  - Project cards with color dot, status/priority badges, due date, open task count
  - SortableJS 1.15.0 drag-and-drop for project cards and task rows; order saved via `POST /projects/reorder`
  - localStorage per-user per-project collapse/expand state (`project_collapsed_{user_id}_{project_id}`)
  - Client-side column sorting for task tables: `sortTasks(projectId, column)` scoped per project; tbody `id="project-tasks-{id}"`; `<th class="sort-header">` with `data-col`; numeric ordering for priority (`critical/high/medium/low`) and status (`notstarted/inprogress/onhold/blocked/done`); sort indicators update within the project's own table only
  - `table-fixed` + `<colgroup>` for aligned task columns across all project cards (8 columns: drag | task | status | priority | created by | assigned | due | actions)
  - **Created by column**: shows creator avatar (initials in slate-200 circle) + full name (hidden on mobile); `data-created` attribute on `<tr>` for potential sorting; column is `hidden md:table-cell`
  - `line-clamp-2` on task titles
  - Archive/unarchive: form POST `action=archive` → `edit_project` → redirect; "Archived" link with count badge in header
  - Four modals: New Project, Edit Project, Add Task, Edit Task (all with status/priority/due date)
  - Quick inline status/priority selects on task rows (AJAX `quickUpdateTask`)
  - Mobile: icon-only buttons, hidden non-essential columns, `overflow: auto` (not hidden)
- [x] `views/archivedprojects.html` — archived projects page: extends `_basewide.html`, ← Back to Projects, Restore (unarchive) + Delete buttons, read-only task table
- [x] **Todo module** (`views/todos.html`, `all_todos`/`add_todo`/`edit_todo`/`archived_todos`/`reorder_todos` views, `Todo` model):
  - Two tabs: **"Personal"** and "Shared" — localStorage remembers last-active tab per user (`todo_active_tab_{user_id}`)
  - **Flat table design**: single `<table>` per panel with columns: drag | task (title + description) | status | priority | assigned | due | actions; no collapsible sections
  - `tbody` IDs: `todo-tbody-personal` and `todo-tbody-shared`; rows carry `data-todo-id`, `data-title`, `data-status`, `data-priority`, `data-due`; shared rows also carry `data-assigned`
  - **Active/Done split**: `all_todos` view passes `personal_active`, `personal_done`, `shared_active`, `shared_done` separately; main tables only show active (non-done) todos
  - **Done section per panel**: collapsible `<div id="done-section-{panel}">` below each main table; `toggleDoneSection(panel)` JS function; collapse state stored in localStorage (`todo_done_{panel}_{user_id}`); shows toggle-to-inprogress checkmark, strikethrough title, archive + delete buttons
  - **Status badge dropdown** (`position:fixed; z-index:9999`): Alpine.js `x-data="{ open:false }"` per row; `x-init` + `$watch('open', …)` uses `getBoundingClientRect()` of trigger button to position dropdown after opening — avoids clipping by table `overflow:hidden`
  - **Edit modal**: single `<div id="edit-todo-modal">` (fixed overlay) at page top; `openEditTodo(id,title,desc,status,priority,due,scope,assignedId)` populates and shows it; `closeEditModal()` hides it; Assign-to row shown/hidden based on scope
  - **SortableJS drag-and-drop**: `Sortable` on each `<tbody>` (active rows only); `onEnd` sends `{todo_id, new_status:null, order:[]}` to `POST /todo/reorder` (no status change on reorder)
  - **Sort**: `sortTodos(panel, col)` per panel; reads `data-title`/`data-status`/`data-priority`/`data-due`/`data-assigned` from `<tr>`; `assigned` sort supported in shared panel; sort indicators per table header
  - **Shared Assigned column sortable**: `onclick="sortTodos('shared','assigned')"` on Assigned `<th>`; personal Assigned column header is plain (no onclick — personal has no assignee)
  - **Quick-add form** below each table; scope hidden input
  - **Assign to (Shared only)**: assignee shown as indigo avatar in Assigned column; personal column shows "—"
  - Auto-archive: done todos older than 14 days archived on page load
  - Manual archive + delete buttons per Done row; Archived link in sticky header → `archivedtodos.html`
  - `reorder_todos` endpoint: `POST /todo/reorder` — JSON `{todo_id, new_status, order:[{id,order}]}`; `new_status:null` means reorder-only
  - `users` context variable passed from `all_todos` for Assign-to select in edit modal
- [x] `views/archivedtodos.html` — archived tasks list: ← To-Do, Restore + Delete buttons, scope/priority badges, completed/archived dates
- [x] Sidebar & dashboard: "Files" renamed to "File Sharing"; Projects nav item made live (removed "Soon" badge); "To-Do List" nav item added; Todo dashboard card added (indigo, shows "To-Do List"); Projects dashboard card made live (violet)
- [x] **Upload Links module** (`models/uploadlink.py`, `models/sharedfileviews.py`, `views/uploadlinks.html`, `views/createuploadlink.html`, `views/viewuploadlink.html`, `views/edituploadlink.html`, `views/clientuploadpage.html`, `views/uploadlinkexpired.html`):
  - Staff create upload links at `/files/links/` → accessible via "Upload Links" button in File Sharing header
  - Public clients upload to `/upload/<uuid>/` without auth — no login required
  - Link has: title, instructions, expiry date (1–90 days), max files limit (1–50)
  - Deactivate/Activate toggle on view page; Edit button → `edituploadlink.html`; Delete removes all uploaded files + link
  - View page shows shareable URL with Copy button, uploaded file table with Download buttons
  - Edit page: pre-filled title, instructions (textarea), expiry extension (leave blank to keep current), max files
  - Models: `UploadLink`, `ClientUploadedFile` — `app_label = 'models'`
  - File storage: `client_uploads/<uuid_hex>/<filename>`
  - URLs: `all_upload_links`, `create_upload_link`, `view_upload_link`, `delete_upload_link`, `edit_upload_link`, `client_upload_page`
  - Upload links list (`uploadlinks.html`) has View button only per row (Edit accessible from View page sticky header)
- [x] **Delete buttons moved from edit forms to view pages** for Clients, Wiki, Tools, Secret Notes:
  - `client.html`: Edit client + Delete client buttons added to sticky header
  - `wikiview.html`: Delete button added next to Edit article
  - `toolview.html`: Delete button added next to Edit tool
  - `secretnoteinternal.html`: Delete button added next to Edit note
  - `unimodelform.html`: `{% if deletebutton %}` block removed entirely
- [x] **File Sharing list** (`allfiles.html`): Actions column shows View only (Copy and Delete removed — both available on file detail page); Upload Links button added to header (orange: `bg-orange-600`)
- [x] `views/help.html` — updated: File Sharing split into Shared Files + Upload Links subsections; Projects updated (column sort, archive, drag-drop); To-Do List updated (flat table, Personal/Shared tabs, assignee, auto-archive 14 days)
- [x] `views/edituploadlink.html` — edit form for upload links: extends `_basenarrow.html`, pre-filled title/instructions/max_files, optional expiry extension with current expiry hint
- [x] `edit_upload_link` view in `models/sharedfileviews.py`; URL `files/links/<uuid>/edit` → name `edit_upload_link`; Edit button added to `viewuploadlink.html` sticky header and `uploadlinks.html` actions column
- [x] Migration chain: `0058_project_task` → `0059_project_status_priority_due` → `0060_todo` → `0061_todo_scope_archive` → `0062_uploadlink_clientuploadedfile` → `0063_todo_assigned_to`
- [x] **Bug fixes (Session 2)**:
  - `models/personform.py`: Removed `'annoyance'` from `PersonForm.Meta.fields` and `order` tuple — was causing silent form validation failure (field required but never rendered, so POST data had no value). Django now uses model default (`0`) automatically.
  - `models/uploadlink.py`: Fixed `upload_to_client()` — `instance.unid` → `instance.upload_link.unid` (`ClientUploadedFile` doesn't have `unid`; it's on the FK `UploadLink`). Also added `file_size_display` property to `ClientUploadedFile`.
  - `clientmanagement/settings/local.py`: Added SSL context patch after email settings load — bypasses hostname verification for `smtp.emailsrvr.com` (SMTP server certificate has hostname mismatch). Patches `ssl.create_default_context` to return an unverified context.
  - `views/alltools.html`: "Add Link" button changed to dark green (`bg-emerald-700 hover:bg-emerald-800`).
  - `views/allfiles.html`: "Upload Links" button changed from orange to dark green (`bg-emerald-700 hover:bg-emerald-800`).
  - `views/todos.html`: Overdue task titles show `text-red-600 font-medium`; Assigned column removed from Personal panel (both active and done tables, colgroup updated, colspan 8→7); Esc key closes both edit-todo and add-todo modals.
  - `views/allprojects.html`: Overdue task titles show `text-red-600` (already had Esc key support via `.modal-backdrop` keydown listener).
  - `registration/password_change_form.html` and `password_change_done.html`: Fully restyled to match login page (standalone HTML, Tailwind CDN, DM Sans font, card layout, field-input class, branded header).
- [x] **Annoyance field note**: `PersonForm.Meta.fields` no longer includes `'annoyance'`. The field still exists on the Person model but is excluded from all form processing. Django uses the model's `default='0'` when saving.
- [x] **Todo personal tab**: Assigned column is completely hidden (removed from colgroup, thead, active tbody, done tbody). Shared tab Assigned column is unchanged.
- [x] **Session 3 — Mobile fixes**:
  - `views/todos.html`: Mobile 3-column view — on `< md` breakpoint shows only Task, Status, Edit button; Drag handle, Priority, Start (was already hidden), Due all hidden with `hidden md:table-cell` / `hidden md:table-column` in all 4 tables (personal active, personal done, shared active, shared done)
  - `views/todos.html`: Shared panel Assigned column — initials-only avatar (`title` attr for full name tooltip), removed full name `<span>` text; applies to both active and done rows
  - `views/allprojects.html`: Created by and Assigned columns — initials-only avatars (`title` attr for full name tooltip), removed full name `<span>` text beside them
  - `views/uploadlinks.html`: "Create Upload Link" button — full text shown always; `flex-wrap` on header inner div allows button to wrap to next line on mobile
  - `views/edituploadlink.html`: "Back to link" nav link — full text always visible (no hidden span)
- [x] **Session 3 — Admin portal** (`models/adminviews.py`, `models/loginlog.py`, `clientmanagement/emailbackend.py`):
  - **Email-based login**: `clientmanagement/emailbackend.py` — `EmailOrUsernameBackend` tries username first then case-insensitive email lookup; added to `AUTHENTICATION_BACKENDS` in `settings/base.py` before the default backend; login.html and loginform.py updated to show "Email" label and `type="email"` input
  - **Login logs**: `models/loginlog.py` — `LoginLog` model (user FK nullable, username_attempted, ip_address, timestamp, success, user_agent); signal handlers `log_successful_login` and `log_failed_login` connected to Django auth signals in `models/apps.py` `ready()` method; migration `0065_loginlog.py`
  - **Admin portal views**: `models/adminviews.py` — `admin_portal` (dashboard with stats + recent logs), `admin_users` (user list), `admin_user_add`, `admin_user_edit`, `admin_user_delete` (JSON), `admin_login_logs`; all gated by `@staff_required` decorator; superusers can toggle `is_staff` on other users; staff cannot edit superusers
  - **URLs**: `usermanagement/` → `admin_portal` (kept name `usermanagement`); `/usermanagement/users/`, `/users/add`, `/users/<id>/edit`, `/users/<id>/delete`, `/login-logs/` added
  - **Templates**: `views/admin_portal.html` (dashboard), `views/admin_users.html` (user table, JS delete), `views/admin_user_form.html` (add/edit form), `views/admin_login_logs.html` (log table), `views/admin_403.html` (access denied)
  - **Sidebar**: `_base.html` — nav link changed from "Users" to "Admin Portal" with settings gear icon; active state check updated to include all admin URL names; still `{% if user.is_staff %}` gated
  - **Migration chain**: `0064_todo_start_date` → `0065_loginlog`
  - **User accounts**: email is now used as both `email` and `username` when creating/editing users via admin portal (email truncated to 150 chars for username field)
- [x] **Session 4 — Bug fixes**:
  - **Bug 1 — Admin add user 500 error**: Root cause: `edit_user.first_name` used as a `default` filter argument in `admin_user_form.html` when `edit_user` is not in context (add mode); Django raises `VariableDoesNotExist` for undefined filter arguments. Fix: `admin_user_edit` now pre-populates `form_data` dict on GET (`first_name`, `last_name`, `email`, `is_staff`); template simplified to use `{{ form_data.fieldname }}` without any `edit_user.X` filter args.
  - **Bug 2 — Remove "Created by" from projects task table**: Removed colgroup `<col>`, thead `<th>`, and tbody `<td>` for "Created by" column from all project task tables. Added "Created by" as a read-only display field in the Edit Task modal alongside "Assign to" (2-column row using `mf-2col`). Added `created_by` to `taskCache` JS object; `openEditTaskModal` populates `et-created-by` div.
  - **Bug 3 — Tools buttons size parity**: "Add Link" button updated from `px-3 py-2 text-xs w-3.5 h-3.5` to `px-4 py-2 text-sm w-4 h-4` — now matches "Add File" button exactly.
  - **Bug 4 — Site-wide button wrapping on mobile**: Added `flex-wrap` to the inner `max-w-5xl` div of ALL sticky action bars across the entire portal. Pages updated: `allclients.html`, `allpeople.html`, `allwiki.html`, `uploadlinks.html`, `client.html`, `wikiview.html`, `secretnoteinternal.html`, `toolview.html`, `fileview.html`, `viewuploadlink.html`, `archivedprojects.html`, `archivedtodos.html`, `admin_portal.html`, `admin_users.html`, `admin_user_form.html`, `admin_login_logs.html`, `unimodelform.html`, `editfile.html`, `uploadfile.html`, `createuploadlink.html`, `edituploadlink.html`, `wikieditform.html`. With `flex-wrap`, buttons naturally move to the next row when horizontal space is insufficient on mobile.
- [x] **Session 5 — Version 2.3.12**:
  - **Versioning system**: `config.py` updated to `CLIENTMANAGEMENT_VERSION = '2.3.12'`; `context_processors.py` now exposes `VERSION` alias; `_base.html` footer shows `v{{ VERSION }}`; `THATSNEW.md` created; `## Versioning` section added to `CLAUDE.md`
  - **Fix A — User dropdown**: z-index changed from `z-50` to `z-[9999]`; Admin Portal link (staff only) added to user dropdown above "Personal page"; Admin Portal sidebar nav link removed entirely (now only in dropdown)
  - **Fix B — Site-wide clickable rows**: Actions/View column removed from all list pages; entire row navigates to detail (or opens modal for people); updated pages: `allclients.html`+`clientrow.html`, `allpeople.html`+`allpeoplerow.html`, `allwiki.html`+`wikirow.html`, `alltools.html`+`onetoolrow.html`, `allsecretnotes.html`+`secretnoterow.html`, `allfiles.html`, `todos.html`; DataTables `columnDefs` indices updated on all affected pages; `openTodoRow()` JS helper added to todos.html; `data-todo-desc` and `data-todo-scope` added to active todo `<tr>` elements; `x-data`+`@click` moved to `<tr>` on allpeoplerow.html for row-click modal opening
  - **Fix C — Client detail duplicate Edit button**: Removed the entire `<div class="mt-5 pt-4...">` form block from `views/components/generalinfoclient.html` (Edit button in sticky header is the only one now)
- [x] **Session 7 — Version 2.3.15**:
  - **FIX 1 — User dropdown stacking context bug**: Root cause identified — `<header class="sticky z-10">` creates a CSS stacking context; all children (even `position:fixed z-[99999]`) paint at z:10 on the root, equal to page sticky bars that come later in DOM. Fix: changed `z-10` → `z-20` on the `<header>` element in `_base.html` so the entire header context paints above all z:10 page sticky headers.
  - **FIX 2 — Tools header restructure** (`alltools.html`): Title + search bar now always on the same line; filter tabs (All/Links/Files) and action buttons (Add Link, Add File) moved to a second line on mobile (`w-full sm:w-auto` container with `flex-wrap`).
  - **FIX 3 — Secret Notes header restructure** (`allsecretnotes.html`): Same pattern — title + search on line 1; filter tabs (Available/Unavailable/All) + New Note button on line 2 on mobile.
  - **FIX 4 — All list pages: title+search always same line** (`allclients.html`, `allpeople.html`, `allwiki.html`, `allfiles.html`): Wrapped title and search in a single `flex-1` div so they are always on the same row; action buttons remain `w-full sm:w-auto` so they wrap below on mobile.
  - **config.py**: Version bumped to `2.3.15`; Apache restart required
  - **WHATSNEW.md**: 2.3.15 section added; 2.3.14 section finalized
- [x] **Session 6 — Version 2.3.14**:
  - **FIX 1 — User dropdown `position:fixed`**: Changed dropdown from `position:absolute z-[9999]` to `position:fixed z-[99999]` with Alpine.js `x-init`+`$watch` using `getBoundingClientRect()` to position relative to viewport — always appears above all page content on mobile
  - **FIX 2 — Personal page redesign**: `user/personal/main.html` rewritten — Tailwind card layout with user info (avatar, name, email, role, member since), Security section (change password), API Key section (delete with confirm); extends `_basenarrow.html`; uses context: `user`, `api_key`, `deleted`, `del_page`
  - **FIX 3 — Mobile 2-line headers**: All list page headers updated with `flex flex-wrap`; search takes `w-full sm:flex-1`; action buttons wrapped in `<div class="flex items-center gap-2 w-full sm:w-auto">`; subtitle hidden on mobile (`hidden sm:block`); applied to allclients, allpeople, allwiki, alltools, allsecretnotes, allfiles, allprojects, todos
  - **FIX 4 — Clients subtitle**: Changed from "All managed client companies" to "All client companies"
  - **FIX 5 — Password reset template check**: No portal-specific variables found in `registration/` templates — they are clean standalone files. SMTP 535 error is a server credential issue; `private/email-settings.cnf` on production needs to be verified
  - **config.py**: Version bumped to `2.3.14`; Apache restart required
  - **WHATSNEW.md**: 2.3.14 section added; 2.3.13 section finalized
- [x] **Session 8 — Version 2.3.16**:
  - **FIX 1 — Admin Portal Roles**: `models/adminviews.py` — added `_role_from_user()` helper; `admin_user_add` and `admin_user_edit` read `role` POST field and set `is_staff`/`is_superuser` flags accordingly (superusers only); self-demotion blocked via `edit_user != request.user` guard. `admin_user_form.html` — replaced `is_staff` checkbox with role `<select>` (User/Staff/Admin); amber warning shown when editing own account.
  - **FIX 2 — Sort persistence**: `allprojects.html` — `sortTasks()` refactored to `_applySortTasks()` + `sortTasks()`; sort state saved in localStorage key `project_tasks_sort_<user_id>_<project_id>`; DOMContentLoaded loop restores sort for each project. `todos.html` — `sortTodos()` refactored with `_applyTodoSort()` helper; sort state saved in localStorage key `todo_sort_<user_id>_<panel>`; restored in DOMContentLoaded.
  - **FIX 3 — Todo modal redesign**: `todos.html` — Add and Edit todo modals rewritten using project-task modal style (`.modal-backdrop`, `.modal-header`, `.modal-body`, `.modal-footer`, `mf-*` classes, close X button, `focus()` on title on open).
  - **FIX 4 — Two-letter initials**: `allprojects.html` — task rows show creator avatar (2 initials, slate) + arrow + assignee avatar (2 initials, blue) above task title. `todos.html` — shared panel rows show creator + arrow + assignee avatars with 2-letter initials; Edit Task modal displays creator name in read-only field. `projectviews.py` — `prefetch_related('tasks__created_by')` added.
  - **FIX 5 — Todo mobile drag**: `todos.html` — drag handle `<th>` in shared panel thead: removed `hidden md:table-cell`; drag handle `<td>` in personal and shared active tables: removed `hidden md:table-cell` from colgroup and tbody.
  - **FIX 6 — Project task status badge dropdown**: `allprojects.html` — inline `<select class="inline-select">` replaced with Alpine.js fixed-position badge dropdown; `quickUpdateTaskStatus()` function updates badge DOM and `row.dataset.status` then fires AJAX; `refreshBadge()` updated to count open tasks via `row.dataset.status !== 'done'` instead of querying `<select>`.
  - **Upload Links default max files**: `createuploadlink.html` — default changed from 10 to 1.
  - **config.py**: Version bumped to `2.3.16`; Apache restart required (Python files changed)
  - **WHATSNEW.md**: 2.3.16 section added
