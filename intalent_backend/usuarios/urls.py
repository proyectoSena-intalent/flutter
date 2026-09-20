from django.urls import path
from . import views


urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout, name='logout'),
    path('buscar-servicios/', views.buscar_servicios, name='buscar_servicios'),
    path('ofrecer-servicio/', views.ofrecer_servicio, name='ofrecer_servicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('activar-profesional/', views.activar_profesional, name='activar_profesional'),
    path('solicitar-servicio/<int:servicio_id>/', views.solicitar_servicio, name='solicitar_servicio'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('solicitudes-recibidas/', views.solicitudes_recibidas, name='solicitudes_recibidas'),
    path('cambiar-estado-solicitud/<int:solicitud_id>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
]