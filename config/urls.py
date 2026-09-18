"""
URL Configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from packaging.views import APIRootView

urlpatterns = [
    path('', APIRootView.as_view(), name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('packaging.urls')),
]

