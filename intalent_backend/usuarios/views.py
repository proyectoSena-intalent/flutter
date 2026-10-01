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

        # Obtener la foto enviada
        foto = request.FILES.get('foto')

        # Verificar que se haya seleccionado una foto
        if not foto:
            mensaje = 'Debes seleccionar una foto de perfil.'

            return render(
                request,
                'registro.html',
                {'mensaje': mensaje}
            )

        # Verificar que las contraseñas coincidan
        if contraseña != confirmar_contraseña:
            mensaje = 'Las contraseñas no coinciden.'

            return render(
                request,
                'registro.html',
                {'mensaje': mensaje}
            )

        # Verificar si el correo ya existe
        if Usuario.objects.filter(correo=correo).exists():
            mensaje = 'Ya existe una cuenta registrada con este correo.'

            return render(
                request,
                'registro.html',
                {'mensaje': mensaje}
            )

        # Encriptar contraseña
        contraseña_segura = make_password(contraseña)

        # Crear usuario y guardar foto
        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            contraseña=contraseña_segura,
            tipo_usuario='cliente',
            foto=foto
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

    # Cambiar foto de perfil
    if request.method == 'POST':

        foto = request.FILES.get('foto')

        if foto:
            usuario.foto = foto
            usuario.save()

        return redirect('perfil')

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

    # Verificar qué solicitudes ya fueron calificadas
    from calificaciones.models import Calificacion

    calificaciones_realizadas = Calificacion.objects.filter(
        calificador=usuario
    ).values_list(
        'solicitud_id',
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

def cancelar_solicitud(request, solicitud_id):

    usuario_id = request.session.get('usuario_id')

    try:
        solicitud = Solicitud.objects.get(
            id=solicitud_id,
            cliente_id=usuario_id
        )

    except Solicitud.DoesNotExist:

        return redirect('mis_solicitudes')

    # Solo se puede cancelar una solicitud pendiente
    if solicitud.estado == 'pendiente':

        solicitud.estado = 'cancelada'
        solicitud.save()

    return redirect('mis_solicitudes')

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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
import json

import secrets

from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

from .models import RecuperacionContraseña


@csrf_exempt
def api_login(request):

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'mensaje': 'Método no permitido'
        }, status=405)

    try:
        datos = json.loads(request.body)

        correo = datos.get('correo')
        contraseña = datos.get('contraseña')

        if not correo or not contraseña:
            return JsonResponse({
                'success': False,
                'mensaje': 'Correo y contraseña son obligatorios'
            }, status=400)

        try:
            usuario = Usuario.objects.get(correo=correo)

        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'mensaje': 'Correo o contraseña incorrectos'
            }, status=401)

        if not usuario.contraseña or not check_password(
            contraseña,
            usuario.contraseña
        ):
            return JsonResponse({
                'success': False,
                'mensaje': 'Correo o contraseña incorrectos'
            }, status=401)

        return JsonResponse({
            'success': True,
            'mensaje': 'Inicio de sesión correcto',
            'usuario': {
                'id': usuario.id,
                'nombre': usuario.nombre,
                'apellido': usuario.apellido,
                'correo': usuario.correo,
                'tipo_usuario': usuario.tipo_usuario,
                'es_profesional': usuario.es_profesional,
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'Los datos enviados no son válidos'
        }, status=400)

def recuperar_contraseña(request):

    mensaje = ''

    if request.method == 'POST':

        correo = request.POST.get('correo')

        try:
            usuario = Usuario.objects.get(correo=correo)

            # Invalidar recuperaciones anteriores
            RecuperacionContraseña.objects.filter(
                usuario=usuario,
                usado=False
            ).update(
                usado=True
            )

            # Crear token seguro
            token = secrets.token_urlsafe(48)

            RecuperacionContraseña.objects.create(
                usuario=usuario,
                token=token
            )

            enlace = (
                request.build_absolute_uri(
                    f'/restablecer-contrasena/{token}/'
                )
            )

            send_mail(
                'Recuperación de contraseña - InTalent',
                f'''
Hola {usuario.nombre},

Has solicitado recuperar tu contraseña de InTalent.

Ingresa al siguiente enlace para establecer una nueva contraseña:

{enlace}

Si tú no solicitaste este cambio, puedes ignorar este mensaje.
''',
                None,
                [usuario.correo],
            )

            mensaje = (
                'Si el correo está registrado, '
                'recibirás instrucciones para recuperar tu contraseña.'
            )

        except Usuario.DoesNotExist:

            # No revelar si el correo existe o no
            mensaje = (
                'Si el correo está registrado, '
                'recibirás instrucciones para recuperar tu contraseña.'
            )

    return render(
        request,
        'recuperar_contrasena.html',
        {
            'mensaje': mensaje
        }
    )

def restablecer_contrasena(request, token):

    try:
        recuperacion = RecuperacionContraseña.objects.get(
            token=token,
            usado=False
        )

    except RecuperacionContraseña.DoesNotExist:

        return render(
            request,
            'restablecer_contrasena.html',
            {
                'error': 'El enlace de recuperación no es válido.'
            }
        )

    # Verificar que el token no tenga más de 30 minutos
    tiempo_limite = timezone.now() - timedelta(minutes=30)

    if recuperacion.fecha_creacion < tiempo_limite:

        recuperacion.usado = True
        recuperacion.save()

        return render(
            request,
            'restablecer_contrasena.html',
            {
                'error': 'El enlace de recuperación ha expirado.'
            }
        )

    if request.method == 'POST':

        nueva_contrasena = request.POST.get(
            'nueva_contrasena'
        )

        confirmar_contrasena = request.POST.get(
            'confirmar_contrasena'
        )

        if not nueva_contrasena or not confirmar_contrasena:

            return render(
                request,
                'restablecer_contrasena.html',
                {
                    'error': 'Debes completar todos los campos.',
                    'token': token
                }
            )

        if nueva_contrasena != confirmar_contrasena:

            return render(
                request,
                'restablecer_contrasena.html',
                {
                    'error': 'Las contraseñas no coinciden.',
                    'token': token
                }
            )

        if len(nueva_contrasena) < 8:

            return render(
                request,
                'restablecer_contrasena.html',
                {
                    'error': (
                        'La contraseña debe tener '
                        'mínimo 8 caracteres.'
                    ),
                    'token': token
                }
            )

        # Guardar la nueva contraseña de forma segura
        recuperacion.usuario.contraseña = make_password(
            nueva_contrasena
        )

        recuperacion.usuario.save()

        # Marcar el token como utilizado
        recuperacion.usado = True
        recuperacion.save()

        return render(
            request,
            'restablecer_contrasena.html',
            {
                'exito': (
                    'Tu contraseña fue cambiada correctamente. '
                    'Ya puedes iniciar sesión.'
                )
            }
        )

    return render(
        request,
        'restablecer_contrasena.html',
        {
            'token': token
        }
    )