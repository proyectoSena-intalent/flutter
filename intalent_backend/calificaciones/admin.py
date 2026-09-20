from django.contrib import admin
from .models import Calificacion


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'calificador',
        'calificado',
        'puntuacion',
        'comentario',
        'fecha',
    )

    list_filter = (
        'puntuacion',
        'fecha',
    )

    search_fields = (
        'calificador__nombre',
        'calificador__apellido',
        'calificado__nombre',
        'calificado__apellido',
        'comentario',
    )