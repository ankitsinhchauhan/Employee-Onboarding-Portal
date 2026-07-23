from django.urls import path

from employees.views.dashboard import dashboard

urlpatterns = [

    path(
        "dashboard/",
        dashboard,
        name="dashboard"
    ),

]