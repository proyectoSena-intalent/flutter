from django.urls import path
from . import views


urlpatterns = [
    path('', views.crear_calificacion, name='crear_calificacion'),
    path('usuario/<int:usuario_id>/',views.ver_calificaciones,name='ver_calificaciones'),
]