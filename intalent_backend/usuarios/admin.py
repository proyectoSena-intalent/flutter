from django.contrib import admin
from .models import Usuario, Servicio, Solicitud


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'apellido',
        'correo',
        'telefono',
        'tipo_usuario',
        'fecha_registro',
    )

    search_fields = (
        'nombre',
        'apellido',
        'correo',
    )

    list_filter = (
        'tipo_usuario',
    )
    
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'categoria',
        'precio',
        'profesional',
        'fecha_registro',
    )

    search_fields = (
        'nombre',
        'descripcion',
    )

    list_filter = (
        'categoria',
    )


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cliente',
        'servicio',
        'estado',
        'fecha_solicitud',
    )

    list_filter = (
        'estado',
    )

    search_fields = (
        'cliente__nombre',
        'cliente__apellido',
        'servicio__nombre',
    )

