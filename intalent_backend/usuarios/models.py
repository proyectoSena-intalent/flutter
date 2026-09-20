from django.db import models


class Usuario(models.Model):
    TIPO_USUARIO = [
        ('cliente', 'Cliente'),
        ('profesional', 'Profesional'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=128, null=True, blank=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TIPO_USUARIO
    )
    es_profesional = models.BooleanField(default=False)

    estado_profesional = models.CharField(
        max_length=20,
        choices=[
            ('activo', 'Activo'),
            ('bloqueado', 'Bloqueado'),
    ],
    default='activo'
    )

    saldo_pendiente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Servicio(models.Model):

    CATEGORIAS = [
    ('plomeria', 'Plomería'),
    ('electricidad', 'Electricidad'),
    ('tecnologia', 'Tecnología'),
    ('limpieza', 'Limpieza'),
    ('mascotas', 'Mascotas'),
    ('abogados', 'Abogados'),
    ('construccion', 'Construcción'),
]

    categoria = models.CharField(
    max_length=30,
    choices=CATEGORIAS
)

    nombre = models.CharField(max_length=100)

    descripcion = models.TextField()

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre

    
class Solicitud(models.Model):

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('finalizada', 'Finalizada'),
    ]

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_realizadas'
    )

    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='pendiente'
    )

    precio_acordado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    comision_in_talent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    valor_profesional = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    estado_pago = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('pagado', 'Pagado'),
        ],
        default='pendiente'
    )

    referencia_pago = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    fecha_solicitud = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Solicitud de {self.cliente} - {self.servicio}"