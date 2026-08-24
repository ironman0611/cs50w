from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Application, College, Task, UserProfile


admin.site.site_header = "College Administration"
admin.site.site_title = "College Administration"
admin.site.index_title = "College Administration"

admin.site.unregister(Group)


class TaskInline(admin.TabularInline):
    model = Task
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'college', 'status', 'created_at']
    list_filter = ['status']
    inlines = [TaskInline]


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'location', 'state', 'institution_type', 'campus_setting',
        'application_deadline',
    ]
    list_filter = ['institution_type', 'state', 'campus_setting', 'climate', 'campus_size']
    search_fields = ['name', 'location', 'state', 'search_notes', 'extracurriculars']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'application', 'completed', 'due_date']
    list_filter = ['completed']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_state', 'college_type_preferences', 'updated_at']
