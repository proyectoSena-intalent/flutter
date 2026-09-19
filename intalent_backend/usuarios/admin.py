from django.contrib import admin
from .models import Usuario


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