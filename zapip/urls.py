"""
Zapip URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
"""
from typing import List

from django.urls import path
from django.urls.resolvers import URLPattern

from zapip import views

urlpatterns: List[URLPattern] = [
    path("zoom/v2/users/<str:user_id>/meetings", views.CreateMeeting.as_view()),
    path("zoom/v2/meetings/<int:meeting_id>", views.ReadUpdateDeleteMeeting.as_view()),
]
