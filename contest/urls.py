from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('contest/', views.contest_list, name='contest_list'),
    path('contest/<int:contest_id>', views.contest_detail, name='contest_detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)