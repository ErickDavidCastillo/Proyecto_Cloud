"""
URLs del dashboard de administración.
Separado para mantener modularidad y aplicar namespace 'dashboard'.
"""

from django.urls import path
from apps.usuarios.views import AdminDashboardView

app_name = 'dashboard'

urlpatterns = [
    path('admin/', AdminDashboardView.as_view(), name='admin'),
]
