﻿from django.urls import path
from . import views

urlpatterns = [
    path("", views.room_list, name="room_list"),
    path("<int:pk>/", views.room_detail, name="room_detail"),
    path("<int:pk>/book/", views.book_room, name="book_room"),
]

