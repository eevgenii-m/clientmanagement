from django.contrib import admin
from models import sharedfile
from models.project import Project, Task, Todo

admin.site.register(sharedfile.SharedFile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Todo)
