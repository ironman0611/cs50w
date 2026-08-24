from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('colleges', views.all_colleges, name='all_colleges'),
    path('colleges/<int:college_id>', views.college_detail, name='college_detail'),
    path('my-colleges', views.my_colleges, name='my_colleges'),
    path(
        'my-colleges/remove/<int:application_id>',
        views.remove_application,
        name='remove_application',
    ),
    path(
        'my-colleges/status/<int:application_id>',
        views.update_application_status,
        name='update_application_status',
    ),
    path('apply', views.apply_college, name='apply_college'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),
    path('api/tasks/<int:application_id>', views.get_tasks, name='get_tasks'),
    path(
        'api/tasks/<int:application_id>/create',
        views.create_task,
        name='create_task',
    ),
    path('api/task/<int:task_id>/toggle', views.toggle_task, name='toggle_task'),
    path('api/task/<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('preferences', views.preferences, name='preferences'),
]
