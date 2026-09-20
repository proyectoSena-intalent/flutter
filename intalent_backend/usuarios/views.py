from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from .models import Usuario, Servicio, Solicitud
from .forms import ServicioForm

from decimal import Decimal

COMISION_IN_TALENT = Decimal('0.10')


def registro(request):
    mensaje = ''

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        contraseña = request.POST.get('contraseña')
        confirmar_contraseña = request.POST.get('confirmar_contraseña')

        if contraseña != confirmar_contraseña:
            mensaje = 'Las contraseñas no coinciden.'

            return render(
                request,
                'registro.html',
                {'mensaje': mensaje}
            )

        if Usuario.objects.filter(correo=correo).exists():
            mensaje = 'Ya existe una cuenta registrada con este correo.'

            return render(
                request,
                'registro.html',
                {'mensaje': mensaje}
            )

        contraseña_segura = make_password(contraseña)

        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            contraseña=contraseña_segura,
            tipo_usuario='cliente'
        )

        return render(
            request,
            'registro_exitoso.html'
)

    return render(
        request,
        'registro.html',
        {'mensaje': mensaje}
    )

def login(request):

    mensaje = ''

    if request.method == 'POST':

        correo = request.POST.get('correo')
        contraseña = request.POST.get('contraseña')

        try:
            usuario = Usuario.objects.get(correo=correo)

            if usuario.contraseña and check_password(
                contraseña,
                usuario.contraseña
            ):
                request.session['usuario_id'] = usuario.id
                return redirect('inicio')
            else:
                mensaje = 'Correo o contraseña incorrectos'

        except Usuario.DoesNotExist:
            mensaje = 'Correo o contraseña incorrectos'

    return render(
        request,
        'login.html',
        {'mensaje': mensaje}
    )
@never_cache
def inicio(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    # Contar solicitudes pendientes recibidas
    solicitudes_pendientes = 0

    if usuario.es_profesional:

        solicitudes_pendientes = Solicitud.objects.filter(
            servicio__profesional=usuario,
            estado='pendiente'
        ).count()

    return render(
        request,
        'inicio.html',
        {
            'usuario': usuario,
            'solicitudes_pendientes': solicitudes_pendientes
        }
    )
def logout(request):

    request.session.flush()

    return redirect('login')

def buscar_servicios(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    texto_busqueda = request.GET.get('buscar', '')
    categoria = request.GET.get('categoria', '')

    servicios = Servicio.objects.all()

    if texto_busqueda:
        servicios = servicios.filter(
        models.Q(nombre__icontains=texto_busqueda) |
        models.Q(descripcion__icontains=texto_busqueda)
    )

    if categoria:
        servicios = servicios.filter(
        categoria=categoria
    )

    return render(
        request,
        'buscar_servicios.html',
        {
            'usuario': usuario,
            'servicios': servicios
        }
    )


def ofrecer_servicio(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.es_profesional:
        return redirect('perfil')

    if request.method == 'POST':

        formulario = ServicioForm(request.POST)

        if formulario.is_valid():

            servicio = formulario.save(commit=False)

            servicio.profesional = usuario

            servicio.save()

            return redirect('buscar_servicios')

    else:

        formulario = ServicioForm()

    return render(
        request,
        'ofrecer_servicio.html',
        {
            'usuario': usuario,
            'formulario': formulario
        }
    )

def perfil(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    return render(
        request,
        'perfil.html',
        {
            'usuario': usuario
        }
    )

def pagar_deuda(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.es_profesional:
        return redirect('perfil')

    if request.method == 'POST':

        usuario.saldo_pendiente = Decimal('0.00')
        usuario.estado_profesional = 'activo'

        usuario.save()

        return redirect('perfil')

    return render(
        request,
        'pagar_deuda.html',
        {
            'usuario': usuario
        }
    )

def activar_profesional(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    usuario.es_profesional = True
    usuario.save()

    return redirect('perfil')


def solicitar_servicio(request, servicio_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    servicio = Servicio.objects.get(id=servicio_id)

    # No permitir solicitar el propio servicio
    if servicio.profesional == usuario:
        return redirect('buscar_servicios')

    # Verificar si ya existe una solicitud activa
    solicitud_existente = Solicitud.objects.filter(
        cliente=usuario,
        servicio=servicio,
        estado__in=['pendiente', 'aceptada']
    ).exists()

    if solicitud_existente:
        return redirect('mis_solicitudes')

    # Crear la solicitud
    Solicitud.objects.create(
        cliente=usuario,
        servicio=servicio
    )

    return redirect('mis_solicitudes')

def mis_solicitudes(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    solicitudes = Solicitud.objects.filter(
        cliente=usuario
    ).select_related(
        'servicio',
        'servicio__profesional'
    ).order_by('-fecha_solicitud')

    # Verificar cuáles servicios ya fueron calificados
    from calificaciones.models import Calificacion

    calificaciones_realizadas = Calificacion.objects.filter(
        calificador=usuario
    ).values_list(
        'calificado_id',
        flat=True
    )

    return render(
        request,
        'mis_solicitudes.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes,
            'calificaciones_realizadas': list(
                calificaciones_realizadas
            )
        }
    )
def solicitudes_recibidas(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.es_profesional:
        return redirect('perfil')

    solicitudes = Solicitud.objects.filter(
        servicio__profesional=usuario
    ).select_related(
        'cliente',
        'servicio'
    ).order_by('-fecha_solicitud')

    # Verificar cuáles clientes ya fueron calificados
    from calificaciones.models import Calificacion

    calificaciones_realizadas = Calificacion.objects.filter(
        calificador=usuario
    ).values_list(
        'calificado_id',
        flat=True
    )

    return render(
        request,
        'solicitudes_recibidas.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes,
            'calificaciones_realizadas': list(
                calificaciones_realizadas
            )
        }
    )

def cambiar_estado_solicitud(request, solicitud_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.es_profesional:
        return redirect('perfil')

    solicitud = Solicitud.objects.get(
        id=solicitud_id
    )

    if solicitud.servicio.profesional != usuario:
        return redirect('solicitudes_recibidas')

    if request.method == 'POST':

        estado = request.POST.get('estado')

        print("ESTADO RECIBIDO:", estado)

        if estado in ['aceptada', 'rechazada', 'finalizada']:

            # Verificar si el profesional tiene deuda pendiente
            if estado == 'aceptada' and usuario.saldo_pendiente > 0:

                return render(
                    request,
                    'solicitudes_recibidas.html',
                    {
                        'usuario': usuario,
                        'solicitudes': Solicitud.objects.filter(
                            servicio__profesional=usuario
                        ).select_related(
                            'cliente',
                            'servicio'
                        ).order_by('-fecha_solicitud'),
                        'calificaciones_realizadas': [],
                        'error_pago': True,
                        'mensaje_pago': (
                            'No puedes aceptar esta solicitud porque '
                            'tienes un saldo pendiente con InTalent.'
                        )
                    }
                )

            solicitud.estado = estado

            if estado == 'finalizada':

                if solicitud.precio_acordado is None:
                    solicitud.precio_acordado = solicitud.servicio.precio

                solicitud.comision_in_talent = (
                    solicitud.precio_acordado * COMISION_IN_TALENT
                )

                solicitud.valor_profesional = (
                    solicitud.precio_acordado
                    - solicitud.comision_in_talent
                )

            solicitud.save()

    return redirect('solicitudes_recibidas')

def confirmar_servicio(request, solicitud_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    solicitud = Solicitud.objects.get(id=solicitud_id)

    if solicitud.cliente != usuario:
        return redirect('mis_solicitudes')

    if solicitud.estado == 'finalizada':

        profesional = solicitud.servicio.profesional

        # Sumar la comisión pendiente al profesional
        profesional.saldo_pendiente += solicitud.comision_in_talent

        # Mantener al profesional activo hasta que se implemente
        # el bloqueo por deuda
        profesional.estado_profesional = 'activo'

        profesional.save()

        solicitud.estado = 'confirmada'
        solicitud.estado_pago = 'pendiente'
        solicitud.save()

    return redirect('mis_solicitudes')

def invitado(request):

    texto_busqueda = request.GET.get('buscar', '')
    categoria = request.GET.get('categoria', '')

    servicios = Servicio.objects.all()

    if texto_busqueda:
        servicios = servicios.filter(
            models.Q(nombre__icontains=texto_busqueda) |
            models.Q(descripcion__icontains=texto_busqueda)
        )

    if categoria:
        servicios = servicios.filter(
            categoria=categoria
        )

    return render(
        request,
        'buscar_servicios.html',
        {
            'usuario': None,
            'invitado': True,
            'servicios': servicios
        }
    )