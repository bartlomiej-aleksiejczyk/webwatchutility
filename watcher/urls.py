from django.urls import path
from . import views

urlpatterns = [
    path("strategy/", views.choose_strategy, name="choose_strategy"),
    path("<slug:strategy_name>/task-form/", views.schedule_task, name="schedule_task"),
    path("", views.list_tasks, name="list_tasks"),
    path("<int:task_id>/", views.task_detail, name="task_detail"),
    path("<int:task_id>/delete/", views.task_delete, name="task_delete"),
    path(
        "<int:task_id>/toggle_enabled/",
        views.toggle_task_enabled,
        name="toggle_task_enabled",
    ),
]
