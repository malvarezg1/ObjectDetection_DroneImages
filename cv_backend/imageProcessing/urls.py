from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:image_id>', views.get_image_by_id, name='index'),
]