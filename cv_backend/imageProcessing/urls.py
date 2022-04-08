from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:image_route>', views.get_image_by_id, name='index'),
]