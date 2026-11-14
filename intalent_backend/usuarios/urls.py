from django.urls import path
from . import views


urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login, name='login'),
    path('recuperar-contrasena/',views.recuperar_contraseña,name='recuperar_contraseña'),
    path('restablecer-contrasena/<str:token>/',views.restablecer_contrasena,name='restablecer_contrasena'),
    path('api-login/', views.api_login, name='api_login'),
    path('confirmar-servicio/<int:solicitud_id>/',views.confirmar_servicio,name='confirmar_servicio'),
    path('invitado/', views.invitado, name='invitado'),
    path('inicio/', views.inicio, name='inicio'),
    path('logout/', views.logout, name='logout'),
    path('buscar-servicios/', views.buscar_servicios, name='buscar_servicios'),
    path('ofrecer-servicio/', views.ofrecer_servicio, name='ofrecer_servicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('pagar-deuda/', views.pagar_deuda, name='pagar_deuda'),
    path('activar-profesional/', views.activar_profesional, name='activar_profesional'),
    path('solicitar-servicio/<int:servicio_id>/', views.solicitar_servicio, name='solicitar_servicio'),
    path('mis-solicitudes/', views.mis_solicitudes, name='mis_solicitudes'),
    path('cancelar-solicitud/<int:solicitud_id>/',views.cancelar_solicitud,name='cancelar_solicitud'),
    path('solicitudes-recibidas/', views.solicitudes_recibidas, name='solicitudes_recibidas'),
    path('cambiar-estado-solicitud/<int:solicitud_id>/', views.cambiar_estado_solicitud, name='cambiar_estado_solicitud'),
    path('chat/<int:solicitud_id>/',views.chat,name='chat'),
    path('notificaciones-chat/',views.notificaciones_chat,name='notificaciones_chat'),
    path('mensajes-nuevos-chat/<int:solicitud_id>/',views.mensajes_nuevos_chat,name='mensajes_nuevos_chat'),
    
]