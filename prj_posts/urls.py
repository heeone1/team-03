from django.urls import path
from . import views

urlpatterns = [
    path('', views.prj_list, name="prj_list"),
    path('<int:prj_id>/', views.prj_detail, name="prj_detail"),
    path('new/', views.prj_create, name="prj_create"),
    path('prj_update/<int:pk>/', views.prj_update, name='prj_update'),
    path('prj_delete/', views.prj_delete, name="prj_delete"),
] 