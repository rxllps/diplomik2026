from django.urls import path
from . import views

app_name = 'otziv'

urlpatterns = [
    path('review/<int:room_id>/', views.add_review, name='add_review'),
]