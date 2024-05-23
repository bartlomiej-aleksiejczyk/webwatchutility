from django.urls import path
from . import views

urlpatterns = [
    path("strategy/", views.choose_strategy, name="choose_strategy"),
    path("<slug:strategy_name>/task-form/", views.schedule_task, name="schedule_task"),
]
