from django.urls import path
from . import views

app_name = 'departments'

urlpatterns = [
    path('', views.department_list_view, name='list'),
    path('create/', views.department_create_view, name='create'),
    path('update/<int:pk>/', views.department_update_view, name='update'),
    path('delete/<int:pk>/', views.department_delete_view, name='delete'),
]
