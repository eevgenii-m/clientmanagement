from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import date as _date


def _to_date(val):
    """Safely coerce a value to a date, or return None."""
    if val is None or val == '':
        return None
    if isinstance(val, _date):
        return val
    try:
        return _date.fromisoformat(str(val))
    except (ValueError, TypeError):
        return None


class Project(models.Model):
    COLOR_CHOICES = [
        ('#2563eb', 'Blue'),
        ('#059669', 'Green'),
        ('#dc2626', 'Red'),
        ('#d97706', 'Amber'),
        ('#7c3aed', 'Purple'),
        ('#0891b2', 'Cyan'),
        ('#db2777', 'Pink'),
        ('#65a30d', 'Lime'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('onhold', 'On hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField('Project title', max_length=160)
    description = models.TextField('Description', blank=True, default='')
    color = models.CharField('Color', max_length=10, default='#2563eb', choices=COLOR_CHOICES)
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='active')
    priority = models.CharField('Priority', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField('Due date', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_on = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ['order', 'created_on']

    def __str__(self):
        return self.title

    def open_tasks_count(self):
        return self.tasks.filter(parent_task=None).exclude(status='done').count()

    def all_tasks_count(self):
        return self.tasks.filter(parent_task=None).count()


class Task(models.Model):
    STATUS_CHOICES = [
        ('notstarted', 'Not started'),
        ('inprogress', 'In progress'),
        ('done', 'Done'),
        ('blocked', 'Blocked'),
        ('onhold', 'On hold'),
    ]
    PRIORITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    unid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')
    title = models.CharField('Task title', max_length=200)
    description = models.TextField('Description', blank=True, default='')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='notstarted')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_on']

    def __str__(self):
        return self.title

    def is_overdue(self):
        d = _to_date(self.due_date)
        if not d:
            return False
        from datetime import date
        return d < date.today() and self.status != 'done'

    def days_until_due(self):
        d = _to_date(self.due_date)
        if not d:
            return None
        from datetime import date
        return (d - date.today()).days

    def is_due_soon(self):
        """True if due within 3 days and not overdue and not done."""
        if self.status == 'done':
            return False
        d = _to_date(self.due_date)
        if not d:
            return False
        from datetime import date
        delta = (d - date.today()).days
        return 0 <= delta <= 3

    def timeline_percent(self):
        s = _to_date(self.start_date)
        d = _to_date(self.due_date)
        if not s or not d:
            return 0
        from datetime import date
        total = (d - s).days
        if total <= 0:
            return 100
        elapsed = (date.today() - s).days
        return min(100, max(0, int(elapsed / total * 100)))


class Todo(models.Model):
    SCOPE_CHOICES = [
        ('personal', 'Personal'),
        ('shared', 'Shared'),
    ]
    STATUS_CHOICES = [
        ('todo', 'Not started'),
        ('inprogress', 'In progress'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_todos')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default='personal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    completed_on = models.DateTimeField(null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    archived_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'created_on']

    def __str__(self):
        return self.title

    def is_overdue(self):
        d = _to_date(self.due_date)
        if not d:
            return False
        from datetime import date
        return d < date.today() and self.status != 'done'

    def auto_archive_in_days(self):
        """Days until this done todo auto-archives (14 days after completion)."""
        if self.status != 'done' or not self.completed_on:
            return None
        from django.utils import timezone
        from datetime import timedelta
        archive_at = self.completed_on + timedelta(days=14)
        delta = (archive_at - timezone.now()).days
        return max(0, delta)
