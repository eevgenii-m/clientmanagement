import json
from datetime import date as _date_type
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

from models.project import Project, Task, Todo


def _parse_date(val):
    """Parse an ISO date string (YYYY-MM-DD) or return None if blank/invalid."""
    if not val or not str(val).strip():
        return None
    try:
        return _date_type.fromisoformat(str(val).strip())
    except (ValueError, TypeError):
        return None


def _json_error(msg, status=400):
    return JsonResponse({'ok': False, 'error': msg}, status=status)


def _task_dict(task):
    """Serialize a task to a dict for JSON responses."""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'start_date': str(task.start_date) if task.start_date else '',
        'due_date': str(task.due_date) if task.due_date else '',
        'assigned_to_id': task.assigned_to_id or '',
        'assigned_to_name': (task.assigned_to.get_full_name() or task.assigned_to.username)
            if task.assigned_to else '',
        'is_overdue': task.is_overdue(),
        'is_due_soon': task.is_due_soon(),
        'parent_task_id': task.parent_task_id or '',
    }


# ══════════════════════════════════════════════════════════════════
# PROJECTS
# ══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
def all_projects(request):
    if request.method == 'POST':
        # AJAX: create new project
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            data = request.POST

        title = (data.get('title') or '').strip()
        if not title:
            return _json_error('Title is required.')

        color = data.get('color', '#2563eb')
        valid_colors = [c[0] for c in Project.COLOR_CHOICES]
        if color not in valid_colors:
            color = '#2563eb'

        valid_statuses = [s[0] for s in Project.STATUS_CHOICES]
        valid_priorities = [p[0] for p in Project.PRIORITY_CHOICES]
        status = data.get('status') or 'active'
        priority = data.get('priority') or 'medium'
        if status not in valid_statuses:
            status = 'active'
        if priority not in valid_priorities:
            priority = 'medium'

        due_date = _parse_date(data.get('due_date', ''))

        project = Project.objects.create(
            title=title,
            description=(data.get('description') or '').strip(),
            color=color,
            status=status,
            priority=priority,
            due_date=due_date,
            created_by=request.user,
            order=Project.objects.count(),
        )
        return JsonResponse({'ok': True, 'id': project.id})

    # GET: render page
    projects = (
        Project.objects
        .filter(is_archived=False)
        .prefetch_related('tasks__assigned_to', 'tasks__created_by', 'tasks__subtasks')
        .order_by('order', 'created_on')
    )
    archived_count = Project.objects.filter(is_archived=True).count()
    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')

    return render(request, 'views/allprojects.html', {
        'projects': projects,
        'archived_count': archived_count,
        'users': users,
        'project_colors': Project.COLOR_CHOICES,
        'project_status_choices': Project.STATUS_CHOICES,
        'project_priority_choices': Project.PRIORITY_CHOICES,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'today': _date_type.today(),
    })


@login_required(login_url='login')
@require_POST
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    # Handle archive / unarchive actions (form POST)
    action = data.get('action', '')
    if action == 'archive':
        project.is_archived = True
        project.save()
        return redirect('all_projects')
    elif action == 'unarchive':
        project.is_archived = False
        project.save()
        return redirect('archived_projects')

    # Normal field edit (AJAX)
    title = (data.get('title') or '').strip()
    if not title:
        return _json_error('Title is required.')

    color = data.get('color', project.color)
    valid_colors = [c[0] for c in Project.COLOR_CHOICES]
    if color not in valid_colors:
        color = project.color

    valid_statuses = [s[0] for s in Project.STATUS_CHOICES]
    valid_priorities = [p[0] for p in Project.PRIORITY_CHOICES]
    status = data.get('status') or project.status
    priority = data.get('priority') or project.priority
    if status not in valid_statuses:
        status = project.status
    if priority not in valid_priorities:
        priority = project.priority

    project.title = title
    project.description = (data.get('description') or '').strip()
    project.color = color
    project.status = status
    project.priority = priority
    project.due_date = _parse_date(data.get('due_date', ''))
    project.save()

    return JsonResponse({'ok': True})


@login_required(login_url='login')
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return redirect('all_projects')


@login_required(login_url='login')
def archived_projects(request):
    projects = (
        Project.objects
        .filter(is_archived=True)
        .prefetch_related('tasks__assigned_to', 'tasks__subtasks')
        .order_by('-created_on')
    )
    return render(request, 'views/archivedprojects.html', {
        'projects': projects,
        'today': _date_type.today(),
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
    })


# ══════════════════════════════════════════════════════════════════
# TASKS
# ══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
@require_POST
def add_task(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    title = (data.get('title') or '').strip()
    if not title:
        return _json_error('Title is required.')

    valid_statuses = [s[0] for s in Task.STATUS_CHOICES]
    valid_priorities = [p[0] for p in Task.PRIORITY_CHOICES]
    status = data.get('status') or 'notstarted'
    priority = data.get('priority') or 'medium'
    if status not in valid_statuses:
        status = 'notstarted'
    if priority not in valid_priorities:
        priority = 'medium'

    assigned_to = None
    assigned_to_id = data.get('assigned_to_id')
    if assigned_to_id:
        try:
            assigned_to = User.objects.get(id=int(assigned_to_id))
        except (User.DoesNotExist, ValueError, TypeError):
            pass

    start_date = _parse_date(data.get('start_date', ''))
    due_date = _parse_date(data.get('due_date', ''))

    task = Task.objects.create(
        project=project,
        title=title,
        description=(data.get('description') or '').strip(),
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        start_date=start_date,
        due_date=due_date,
        created_by=request.user,
        order=project.tasks.filter(parent_task=None).count(),
    )
    return JsonResponse({'ok': True, 'task': _task_dict(task)})


@login_required(login_url='login')
@require_POST
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    title = (data.get('title') or '').strip()
    if not title:
        return _json_error('Title is required.')

    valid_statuses = [s[0] for s in Task.STATUS_CHOICES]
    valid_priorities = [p[0] for p in Task.PRIORITY_CHOICES]
    status = data.get('status', task.status)
    priority = data.get('priority', task.priority)
    if status not in valid_statuses:
        status = task.status
    if priority not in valid_priorities:
        priority = task.priority

    assigned_to = task.assigned_to
    assigned_to_id = data.get('assigned_to_id')
    if assigned_to_id == '' or assigned_to_id is None:
        assigned_to = None
    elif assigned_to_id:
        try:
            assigned_to = User.objects.get(id=int(assigned_to_id))
        except (User.DoesNotExist, ValueError, TypeError):
            pass

    task.title = title
    task.description = (data.get('description') or '').strip()
    task.status = status
    task.priority = priority
    task.assigned_to = assigned_to
    task.start_date = _parse_date(data.get('start_date', ''))
    task.due_date = _parse_date(data.get('due_date', ''))
    task.save()

    return JsonResponse({'ok': True, 'task': _task_dict(task)})


@login_required(login_url='login')
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return JsonResponse({'ok': True})


@login_required(login_url='login')
@require_POST
def reorder_projects(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return _json_error('Invalid JSON.')

    order_type = data.get('type')
    if order_type == 'project':
        for item in data.get('order', []):
            try:
                Project.objects.filter(id=int(item['id'])).update(order=int(item['order']))
            except (KeyError, ValueError, TypeError):
                pass
    elif order_type == 'task':
        for item in data.get('order', []):
            try:
                Task.objects.filter(id=int(item['id'])).update(order=int(item['order']))
            except (KeyError, ValueError, TypeError):
                pass

    return JsonResponse({'ok': True})


# ══════════════════════════════════════════════════════════════════
# TODOS
# ══════════════════════════════════════════════════════════════════

@login_required(login_url='login')
def all_todos(request):
    from django.utils import timezone
    from datetime import timedelta

    # Auto-archive done todos older than 14 days
    Todo.objects.filter(
        status='done',
        is_archived=False,
        completed_on__lte=timezone.now() - timedelta(days=14)
    ).update(is_archived=True, archived_on=timezone.now())

    # Personal active todos — only current user, not archived, not done
    personal_active = (
        Todo.objects
        .filter(user=request.user, scope='personal', is_archived=False)
        .exclude(status='done')
        .order_by('order', 'created_on')
    )

    # Personal done todos — separate, sorted by completion date descending
    personal_done = (
        Todo.objects
        .filter(user=request.user, scope='personal', is_archived=False, status='done')
        .order_by('-completed_on')
    )

    # Shared active todos — all users, not archived, not done
    shared_active = (
        Todo.objects
        .filter(scope='shared', is_archived=False)
        .exclude(status='done')
        .select_related('user', 'assigned_to')
        .order_by('order', 'created_on')
    )

    # Shared done todos — separate, sorted by completion date descending
    shared_done = (
        Todo.objects
        .filter(scope='shared', is_archived=False, status='done')
        .select_related('user', 'assigned_to')
        .order_by('-completed_on')
    )

    users = User.objects.filter(is_active=True).order_by('first_name', 'last_name')

    return render(request, 'views/todos.html', {
        'personal_active': personal_active,
        'personal_done': personal_done,
        'shared_active': shared_active,
        'shared_done': shared_done,
        'users': users,
        'priority_choices': Todo.PRIORITY_CHOICES,
        'todo_statuses': Todo.STATUS_CHOICES,
        'today': _date_type.today(),
        'personal_todo_count':       personal_active.filter(status='todo').count(),
        'personal_inprogress_count': personal_active.filter(status='inprogress').count(),
        'personal_done_count':       personal_done.count(),
        'shared_todo_count':         shared_active.filter(status='todo').count(),
        'shared_inprogress_count':   shared_active.filter(status='inprogress').count(),
        'shared_done_count':         shared_done.count(),
    })


@login_required(login_url='login')
def archived_todos(request):
    todos = (
        Todo.objects
        .filter(user=request.user, is_archived=True)
        .order_by('-archived_on', '-completed_on')
    )
    return render(request, 'views/archivedtodos.html', {
        'todos': todos,
    })


@login_required(login_url='login')
@require_POST
def add_todo(request):
    title = (request.POST.get('title') or '').strip()
    scope = request.POST.get('scope', 'personal')
    if scope not in ('personal', 'shared'):
        scope = 'personal'
    if title:
        status = request.POST.get('status', 'todo')
        if status not in ('todo', 'inprogress', 'done'):
            status = 'todo'
        priority = request.POST.get('priority', 'medium')
        if priority not in ('high', 'medium', 'low'):
            priority = 'medium'
        assigned_to = None
        if scope == 'shared':
            assigned_id = request.POST.get('assigned_to', '')
            if assigned_id:
                try:
                    assigned_to = User.objects.get(id=int(assigned_id))
                except (User.DoesNotExist, ValueError, TypeError):
                    assigned_to = None
        Todo.objects.create(
            user=request.user,
            title=title,
            description=(request.POST.get('description') or '').strip(),
            scope=scope,
            status=status,
            priority=priority,
            assigned_to=assigned_to,
            start_date=_parse_date(request.POST.get('start_date', '')),
            due_date=_parse_date(request.POST.get('due_date', '')),
            order=Todo.objects.filter(user=request.user, scope=scope).count(),
        )
    return redirect('all_todos')


@login_required(login_url='login')
@require_POST
def edit_todo(request, todo_id):
    from django.utils import timezone

    # Personal todos — only owner; shared todos — any logged-in user
    try:
        todo = Todo.objects.get(id=todo_id)
        if todo.scope == 'personal' and todo.user != request.user:
            return redirect('all_todos')
    except Todo.DoesNotExist:
        return redirect('all_todos')

    action = request.POST.get('action', '')

    if action == 'delete':
        todo.delete()

    elif action == 'archive':
        todo.is_archived = True
        todo.archived_on = timezone.now()
        todo.save()

    elif action == 'unarchive':
        todo.is_archived = False
        todo.archived_on = None
        todo.save()

    elif action == 'toggle':
        if todo.status == 'done':
            todo.status = 'inprogress'
            todo.completed_on = None
        else:
            todo.status = 'done'
            todo.completed_on = timezone.now()
        todo.save()

    else:
        # Full edit
        title = (request.POST.get('title') or '').strip()
        if title:
            todo.title = title
        todo.description = (request.POST.get('description') or todo.description)
        valid_statuses = [s[0] for s in Todo.STATUS_CHOICES]
        valid_priorities = [p[0] for p in Todo.PRIORITY_CHOICES]
        status = request.POST.get('status', todo.status)
        priority = request.POST.get('priority', todo.priority)
        if status in valid_statuses:
            todo.status = status
            if status == 'done' and not todo.completed_on:
                todo.completed_on = timezone.now()
            elif status != 'done':
                todo.completed_on = None
        if priority in valid_priorities:
            todo.priority = priority
        todo.start_date = _parse_date(request.POST.get('start_date', ''))
        todo.due_date = _parse_date(request.POST.get('due_date', ''))
        if todo.scope == 'shared':
            assigned_id = request.POST.get('assigned_to', '').strip()
            todo.assigned_to = User.objects.filter(id=assigned_id).first() if assigned_id else None
        todo.save()

    return redirect('all_todos')


@login_required(login_url='login')
@require_POST
def reorder_todos(request):
    from django.utils import timezone
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    todo_id    = data.get('todo_id')
    new_status = data.get('new_status')
    order_list = data.get('order', [])

    # Update the dragged todo's status
    if todo_id and new_status:
        valid_statuses = [s[0] for s in Todo.STATUS_CHOICES]
        if new_status in valid_statuses:
            try:
                todo = Todo.objects.get(id=int(todo_id))
                if todo.scope == 'personal' and todo.user != request.user:
                    return JsonResponse({'ok': False}, status=403)
                todo.status = new_status
                if new_status == 'done' and not todo.completed_on:
                    todo.completed_on = timezone.now()
                elif new_status != 'done':
                    todo.completed_on = None
                todo.save()
            except (Todo.DoesNotExist, ValueError, TypeError):
                pass

    # Update order for all items in the target section
    for item in order_list:
        try:
            Todo.objects.filter(id=int(item['id'])).update(order=int(item['order']))
        except (KeyError, ValueError, TypeError):
            pass

    return JsonResponse({'ok': True})
