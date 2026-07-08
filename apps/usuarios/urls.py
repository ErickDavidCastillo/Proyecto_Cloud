"""
URLs del módulo de autenticación (login, logout, registro).
"""

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/',   views.LoginRolView.as_view(),     name='login'),
    path('logout/',  views.logout_view,                name='logout'),
    path('registro/', views.RegistroPacienteView.as_view(), name='registro'),
]
