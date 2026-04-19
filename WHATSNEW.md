# Infotek Portal — What's New

## Version 2.3.16 (April 2026) — current development

### Improvements
- **Admin Portal — User Roles**: Role management replaced the `is_staff` checkbox with a three-tier role selector: User (standard access), Staff (Admin Portal access), Admin (full superuser). Only Admins can change roles; Admins cannot change their own role.
- **Sort persistence — Projects tasks**: Task sort column and direction is now remembered per user per project in localStorage; restored automatically on page reload.
- **Sort persistence — To-Do list**: Todo sort column and direction remembered per user per panel (Personal/Shared) in localStorage; restored on page reload.
- **Todo add/edit modals redesigned**: Modals now use the same styled layout as project task modals (header, body, footer, labelled fields with mf-* classes, close X button, focus on title field on open).
- **Two-letter initials throughout**: All user avatars now show 2-letter initials (first letter of first name + first letter of last name, e.g. EM, VK). Creator→Assignee chain shown in task/todo rows (slate avatar → blue avatar with arrow).
- **Mobile drag-and-drop for To-Do list**: Drag handles are now visible on all screen sizes (was previously hidden on mobile). SortableJS touch events work natively.
- **Project task status — badge dropdown**: Status column in project task rows replaced the `<select>` element with an Alpine.js badge dropdown using `position:fixed` positioning (same pattern as To-Do status). Dropdown items update the badge and fire AJAX without page reload.
- **Upload Links — default max files**: Create Upload Link page now defaults max files to 1 (was 10).

---

## Version 2.3.15 (April 2026)

### Bug fixes
- **User dropdown behind sticky header** — root cause was CSS stacking context: `<header class="sticky z-10">` creates a z:10 stacking context that constrains all children (even `position:fixed z-[99999]`) to paint at z:10 on the root, equal to page sticky bars which come later in DOM. Fix: changed header from `z-10` to `z-20` so the entire header stacking context paints above all z:10 page sticky headers.

### Improvements
- **List page headers — title+search always on same line** — on all list pages the page name and search bar are now always on the same line (including mobile); all other controls (buttons, filter tabs) wrap to a second line on mobile. Applies to: Clients, People, Wiki, Shared Files, Tools, Secret Notes.
- **Tools header** — search bar moved next to page title; filter tabs (All/Links/Files) moved to the second line alongside Add Link/Add File buttons.
- **Secret Notes header** — search bar moved next to page title; filter tabs (Available/Unavailable/All) moved to the second line alongside New Note button.

---

## Version 2.3.14 (April 2026)

### Bug fixes
- **User dropdown hidden behind sticky bars on mobile** — changed from `position:absolute z-[9999]` to `position:fixed` with Alpine.js `x-init`+`$watch` positioning via `getBoundingClientRect()`; dropdown now always appears above all page content
- **Password reset SMTP error (535)** — template was clean (no portal variables); this is a server credential issue. Check `private/email-settings.cnf` on production — email password may have changed. For Gmail use an App Password; for Office 365 ensure SMTP AUTH is enabled.

### Improvements
- **Personal page redesigned** (`/me`) — replaced old Foundation layout with Tailwind card design: avatar + user info card (name, email, role, member since date), Security section (change password link), API Key section (delete key with confirmation); extends `_basenarrow.html`
- **Mobile headers — 2-line layout** — all list page sticky headers now use `flex flex-wrap` with search taking full width (`w-full sm:flex-1`) on mobile and action buttons wrapping to a grouped second line (`w-full sm:w-auto`); applied to: Clients, People, Wiki, Tools, Secret Notes, Shared Files, Projects, To-Do; subtitle text hidden on mobile (`hidden sm:block`) to save space
- **Clients subtitle** — changed from "All managed client companies" to "All client companies"

---

## Version 2.3.13 (April 2026)
### Changes in progress
- Clickable rows across all list pages — no Actions column
- User dropdown z-index fix — no longer overlapped by content
- Admin Portal link moved to user dropdown (staff only)
- Button style standardization: Edit=blue, Delete=red, Add=blue primary
- Todo: Add task modal in header
- Todo: Refresh button added
- Todo: Start date added to tasks
- People: can be added without a company
- Versioning system: version shown in footer
- Registration pages redesigned to match new UI

### Bug fixes
- Person form save not working without company
- Upload link page showing portal sidebar to clients
- File upload path error (ClientUploadedFile had no unid)
- Project task date string vs date object comparison error
- Status dropdown overlapping tasks in todo list
- Duplicate Edit button on client detail page

---

## Version 2.3.12 (April 2026)
### New features
- Complete UI redesign: Tailwind CSS + Alpine.js sidebar layout
- Project management module: tasks, subtasks, drag-drop, 
  status/priority/due dates, archive, column sorting
- To-Do List: personal and shared tabs, drag between sections,
  assignees on shared tasks, auto-archive after 14 days
- File Sharing: upload files with expiry and download limits,
  download tracking with IP logging
- Upload Links: clients upload files via one-time link, no login needed
- Wiki: Markdown editor (EasyMDE), PDF/print export,
  backward compatible with old Quill content
- Secret Notes: auto-expiry by date and read count
- Version number displayed in footer (v{{ VERSION }})

### Improvements
- Python 3.7 → 3.12 upgrade
- Django 2.2 → 4.2 upgrade
- Mobile-responsive design across all pages
- Delete buttons moved from edit forms to view pages
- Help page added

### Infrastructure
- Apache + mod_wsgi on Windows Server 2019
- Dev server: 192.168.10.35
- Production: cms.isstek.com (192.168.10.34)
- Git repository: github.com/eevgenii-m/clientmanagement

---

## Version 1.3.0 (2019) — Original build by Igal
### Features
- Client management with network equipment tracking
- Ticket system with comments and file attachments
- Wiki with Quill rich text editor
- Tools: links and file downloads with public/private toggle
- Secret Notes with expiry
- API with per-client agent software generation (C# MSBuild)
- Django 2.2 / Python 3.7 / Foundation CSS