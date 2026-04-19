"""
Admin portal views — user management + login logs.
All views require is_staff.  Superuser-only operations are guarded additionally.
"""
from functools import wraps

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from models.loginlog import LoginLog


# ── Permission decorator ─────────────────────────────────────────────────────

def staff_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/accounts/login/?next=' + request.path)
        if not request.user.is_staff:
            return render(request, 'views/admin_403.html', status=403)
        return view_func(request, *args, **kwargs)
    return wrapped


# ── Dashboard ────────────────────────────────────────────────────────────────

@staff_required
def admin_portal(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    context = {
        'total_users':    User.objects.count(),
        'staff_users':    User.objects.filter(is_staff=True).count(),
        'logins_today':   LoginLog.objects.filter(timestamp__gte=today_start, success=True).count(),
        'failures_today': LoginLog.objects.filter(timestamp__gte=today_start, success=False).count(),
        'recent_logs':    LoginLog.objects.select_related('user').order_by('-timestamp')[:12],
    }
    return render(request, 'views/admin_portal.html', context)


# ── User list ────────────────────────────────────────────────────────────────

@staff_required
def admin_users(request):
    users = User.objects.all().order_by('last_name', 'first_name', 'username')
    return render(request, 'views/admin_users.html', {'user_list': users})


# ── Delete user (POST → JSON) ─────────────────────────────────────────────────

@staff_required
def admin_user_delete(request, user_id):
    if request.method != 'POST':
        return redirect('admin_users')
    target = get_object_or_404(User, pk=user_id)
    if target.is_superuser and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': 'Cannot delete an admin account.'})
    if target == request.user:
        return JsonResponse({'success': False, 'message': 'You cannot delete your own account.'})
    name = target.get_full_name() or target.username
    target.delete()
    return JsonResponse({'success': True, 'message': name})


# ── Add user ──────────────────────────────────────────────────────────────────

def _role_from_user(u):
    """Return 'admin', 'staff', or 'user' for a User instance."""
    if u.is_superuser:
        return 'admin'
    if u.is_staff:
        return 'staff'
    return 'user'


@staff_required
def admin_user_add(request):
    errors = []
    form_data = {}

    if request.method == 'POST':
        form_data = request.POST
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name',  '').strip()
        email      = request.POST.get('email',      '').strip().lower()
        password   = request.POST.get('password',   '')
        role       = request.POST.get('role', 'user')  # 'user' | 'staff' | 'admin'

        if not first_name or not last_name:
            errors.append('First name and last name are required.')
        if not email or '@' not in email:
            errors.append('A valid email address is required.')
        elif User.objects.filter(email__iexact=email).exists():
            errors.append('A user with this email already exists.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')

        if not errors:
            user = User.objects.create_user(
                username=email[:150],
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            # Only superusers may assign elevated roles
            if request.user.is_superuser:
                user.is_staff     = role in ('staff', 'admin')
                user.is_superuser = role == 'admin'
            user.save()
            return redirect('admin_users')

    return render(request, 'views/admin_user_form.html', {
        'mode': 'add',
        'errors': errors,
        'form_data': form_data,
    })


# ── Edit user ─────────────────────────────────────────────────────────────────

@staff_required
def admin_user_edit(request, user_id):
    edit_user = get_object_or_404(User, pk=user_id)

    # Staff cannot edit superusers
    if edit_user.is_superuser and not request.user.is_superuser:
        return render(request, 'views/admin_403.html', status=403)

    errors = []

    if request.method == 'POST':
        form_data = request.POST
        first_name   = request.POST.get('first_name',   '').strip()
        last_name    = request.POST.get('last_name',    '').strip()
        email        = request.POST.get('email',        '').strip().lower()
        new_password = request.POST.get('password',     '').strip()
        role         = request.POST.get('role', 'user')  # 'user' | 'staff' | 'admin'

        if not first_name or not last_name:
            errors.append('First name and last name are required.')
        if not email or '@' not in email:
            errors.append('A valid email address is required.')
        elif User.objects.filter(email__iexact=email).exclude(pk=user_id).exists():
            errors.append('A user with this email already exists.')
        if new_password and len(new_password) < 8:
            errors.append('New password must be at least 8 characters.')

        if not errors:
            edit_user.first_name = first_name
            edit_user.last_name  = last_name
            edit_user.email      = email
            edit_user.username   = email[:150]
            # Only superusers can change roles; admins cannot demote themselves
            if request.user.is_superuser and edit_user != request.user:
                edit_user.is_staff     = role in ('staff', 'admin')
                edit_user.is_superuser = role == 'admin'
            if new_password:
                edit_user.set_password(new_password)
            edit_user.save()
            return redirect('admin_users')

    else:
        # Pre-populate form_data so the template can use form_data.fieldname
        # uniformly (avoids VariableDoesNotExist with edit_user filter args).
        form_data = {
            'first_name': edit_user.first_name,
            'last_name':  edit_user.last_name,
            'email':      edit_user.email,
            'role':       _role_from_user(edit_user),
        }

    return render(request, 'views/admin_user_form.html', {
        'mode': 'edit',
        'edit_user': edit_user,
        'errors': errors,
        'form_data': form_data,
    })


# ── Login logs ────────────────────────────────────────────────────────────────

@staff_required
def admin_login_logs(request):
    logs = LoginLog.objects.select_related('user').order_by('-timestamp')[:300]
    return render(request, 'views/admin_login_logs.html', {'logs': logs})
