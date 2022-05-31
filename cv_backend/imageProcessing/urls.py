from django.urls import path

from . import views

urlpatterns = [
    path('images/', views.index, name='index'),
    path('images/<str:image_route>', views.get_image_by_id, name='index'),
    path('videos/<str:video_route>', views.get_video_by_id, name='index'),
]