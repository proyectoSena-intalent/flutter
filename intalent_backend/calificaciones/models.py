from django.db import models
from usuarios.models import Usuario


class Calificacion(models.Model):

    PUNTUACION_CHOICES = [
        (1, '1 estrella'),
        (2, '2 estrellas'),
        (3, '3 estrellas'),
        (4, '4 estrellas'),
        (5, '5 estrellas'),
    ]

    solicitud = models.ForeignKey(
        'usuarios.Solicitud',
        on_delete=models.CASCADE,
        related_name='calificaciones',
        null=True,
        blank=True
    )

    calificador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='calificaciones_realizadas'
    )

    calificado = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='calificaciones_recibidas'
    )

    puntuacion = models.PositiveSmallIntegerField(
        choices=PUNTUACION_CHOICES
    )

    comentario = models.TextField(
        blank=True,
        null=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.calificador} calificó a {self.calificado} con {self.puntuacion} estrellas"