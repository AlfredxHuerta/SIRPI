from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path
# from inicio.views import (
#     index,
#     seguidor_linea,
#     mini_zumo,
#     carrera_libre,
#     calendario,
#     capturar_equipo,

# )
from . import views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path("", views.index, name="index"),  # Página principal
    path("seguidor-linea/", views.seguidor_linea, name="seguidor_linea"),
    path("mini-zumo/", views.mini_zumo, name="mini_zumo"),
    path("carrera-libre/", views.carrera_libre, name="carrera_libre"),
    path("calendario/", views.calendario, name="calendario"),
    path('juez/dashboard_juez/', views.dashboard_juez, name='dashboard_juez'),
    path('login_juez/', views.login_juez, name='login_juez'),
    path('ranking/', views.ranking_ultima_batalla, name='ranking'),
    path("juez/crear_batalla/", views.crear_batalla, name="crear_batalla"),
    path("juez/ver_ronda/<int:batalla_id>/", views.ver_ronda, name="ver_ronda"),
    path("juez/cerrar_ronda/<int:batalla_id>/", views.cerrar_ronda, name="cerrar_ronda"),
    path('juez/seleccionar_equipo/', views.seleccionar_equipo, name='seleccionar_equipo'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
    path('batalla/publica/<int:numero>/', views.ver_detalles_general, name='ver_detalles_general'),
    path("batallas_seguidor/", views.batallas_seguidor, name="batallas"),
    path("batalla/<int:batalla_id>/", views.detalles_batalla, name="detalles_batalla"),
    path("ranking/", views.ranking, name="ranking"),
    path("batalla/<int:batalla_id>/", views.detalles_batalla, name="detalles_batalla"),
    path("capturar_equipo/", views.capturar_equipo, name="capturar_equipo"),
]
