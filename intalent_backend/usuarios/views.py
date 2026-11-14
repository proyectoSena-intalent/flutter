from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from .models import Usuario, Servicio, Solicitud, Mensaje, Notificacion
from calificaciones.models import Calificacion
from .forms import ServicioForm

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal



COMISION_IN_TALENT = Decimal('0.10')

def contar_mensajes_no_leidos(usuario):
    estados_chat = ['aceptada', 'finalizada', 'confirmada']

    mensajes = Mensaje.objects.filter(
        leido=False,
        solicitud__estado__in=estados_chat
    ).exclude(
        remitente_id=usuario.id
    ).filter(
        models.Q(solicitud__cliente=usuario) |
        models.Q(solicitud__servicio__profesional=usuario)
    ).exclude(
        solicitud__calificaciones__isnull=False
    )

    return mensajes.values('id').distinct().count()



def notificaciones_chat(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return JsonResponse(
            {'no_leidos': 0, 'notificaciones': []},
            status=401
        )

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id
    )

    # ==========================================
    # 1. CONTAR MENSAJES NO LEÍDOS
    # ==========================================

    cantidad_mensajes = contar_mensajes_no_leidos(usuario)

    mensajes = Mensaje.objects.filter(
        leido=False,
        solicitud__estado__in=[
            'aceptada',
            'finalizada',
            'confirmada'
        ]
    ).exclude(
        remitente=usuario
    ).filter(
        Q(solicitud__cliente=usuario) |
        Q(solicitud__servicio__profesional=usuario)
    ).exclude(
        solicitud__calificaciones__isnull=False
    ).select_related(
        'remitente',
        'solicitud'
    ).order_by('-fecha_envio')

    # ==========================================
    # 2. CONSULTAR NOTIFICACIONES DE SOLICITUDES
    # ==========================================

    notificaciones_bd = Notificacion.objects.filter(
        destinatario=usuario,
        leida=False
    ).select_related(
        'solicitud'
    ).order_by('-fecha_creacion')

    cantidad_notificaciones = notificaciones_bd.count()

    # ==========================================
    # 3. UNIFICAR AMBOS TIPOS DE NOTIFICACIONES
    # ==========================================

    lista = []

    for notificacion in notificaciones_bd:

        if usuario.es_profesional:
            url = reverse('solicitudes_recibidas')
        else:
            url = reverse('mis_solicitudes')

        lista.append({
            'tipo': 'solicitud',
            'id': notificacion.id,
            'titulo': notificacion.titulo,
            'texto': notificacion.mensaje,
            'url': url,
            'fecha': notificacion.fecha_creacion
        })

    for mensaje in mensajes:

        lista.append({
            'tipo': 'mensaje',
            'id': mensaje.id,
            'titulo': 'Nuevo mensaje',
            'texto': (
                f'{mensaje.remitente.nombre}: '
                f'{mensaje.contenido[:100]}'
            ),
            'url': reverse(
                'chat',
                args=[mensaje.solicitud_id]
            ),
            'fecha': mensaje.fecha_envio
        })

    # Ordenar por fecha, del más reciente al más antiguo
    lista.sort(
        key=lambda elemento: elemento['fecha'],
        reverse=True
    )

    # Mostrar máximo 10 avisos en el desplegable
    notificaciones_json = []

    for elemento in lista[:10]:

        notificaciones_json.append({
            'tipo': elemento['tipo'],
            'id': elemento['id'],
            'titulo': elemento['titulo'],
            'texto': elemento['texto'],
            'url': elemento['url'],
            'fecha': elemento['fecha'].isoformat()
        })

    # ==========================================
    # 4. RESPUESTA JSON
    # ==========================================

    return JsonResponse({
        'no_leidos': (
            cantidad_mensajes +
            cantidad_notificaciones
        ),
        'cantidad_mensajes': cantidad_mensajes,
        'cantidad_solicitudes': cantidad_notificaciones,
        'notificaciones': notificaciones_json
    })


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

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id
    )

    # Contar solicitudes pendientes recibidas
    solicitudes_pendientes = 0

    if usuario.es_profesional:
        solicitudes_pendientes = Solicitud.objects.filter(
            servicio__profesional=usuario,
            estado='pendiente'
        ).count()

    # Contar mensajes no leídos
    mensajes_no_leidos = contar_mensajes_no_leidos(usuario)

    return render(
        request,
        'inicio.html',
        {
            'usuario': usuario,
            'solicitudes_pendientes': solicitudes_pendientes,
            'mensajes_no_leidos': mensajes_no_leidos,
        }
    )


def logout(request):

    request.session.flush()

    response = redirect('inicio')

    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


def chat(request, solicitud_id):
    usuario_id = request.session.get('usuario_id')

    # Verificar que haya una sesión iniciada
    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Buscar la solicitud y sus participantes
    solicitud = get_object_or_404(
        Solicitud.objects.select_related(
            'cliente',
            'servicio',
            'servicio__profesional'
        ),
        id=solicitud_id
    )

    # Verificar que el usuario sea participante
    es_cliente = solicitud.cliente_id == usuario.id

    es_profesional = (
        solicitud.servicio.profesional_id == usuario.id
    )

    if not es_cliente and not es_profesional:
        return HttpResponseForbidden(
            "No tienes permiso para acceder a este chat."
        )

    # Estados en los que el chat puede utilizarse
    estados_chat = [
        'aceptada',
        'finalizada',
        'confirmada',
    ]

    # Comprobar si cualquiera de las partes ya calificó
    calificacion_realizada = Calificacion.objects.filter(
        solicitud_id=solicitud.id
    ).exists()

    # El chat permite escribir solo si cumple ambas condiciones
    chat_habilitado = (
        solicitud.estado in estados_chat
        and not calificacion_realizada
    )

    # Procesar el envío de mensajes en el servidor
    if request.method == 'POST':

        # Bloquear cualquier intento de escribir
        # cuando el chat está cerrado
        if not chat_habilitado:
            return redirect(
                'chat',
                solicitud_id=solicitud.id
            )

        contenido = request.POST.get(
            'contenido',
            ''
        ).strip()

        if contenido:
            Mensaje.objects.create(
                solicitud=solicitud,
                remitente=usuario,
                contenido=contenido
            )

        return redirect(
            'chat',
            solicitud_id=solicitud.id
        )

        # Al abrir la conversación, marcar como leídos
    # los mensajes recibidos de la otra persona.
    if request.method == 'GET':
        Mensaje.objects.filter(
            solicitud=solicitud,
            leido=False
        ).exclude(
            remitente_id=usuario.id
        ).update(
            leido=True
        )

    # Recuperar el historial completo sin eliminar mensajes
    mensajes = Mensaje.objects.filter(
        solicitud=solicitud
    ).select_related(
        'remitente'
    ).order_by(
        'fecha_envio'
    )

    return render(
        request,
        'admin/usuarios/chat.html',
        {
            'usuario': usuario,
            'solicitud': solicitud,
            'mensajes': mensajes,
            'chat_habilitado': chat_habilitado,
            'calificacion_realizada': calificacion_realizada,
        }
    )

from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone


def mensajes_nuevos_chat(request, solicitud_id):
    # Verificar sesión
    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return JsonResponse(
            {'error': 'Sesión no iniciada'},
            status=401
        )

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Buscar solicitud y participantes
    solicitud = get_object_or_404(
        Solicitud.objects.select_related(
            'cliente',
            'servicio',
            'servicio__profesional'
        ),
        id=solicitud_id
    )

    # Verificar que sea cliente o profesional
    es_cliente = solicitud.cliente_id == usuario.id

    es_profesional = (
        solicitud.servicio.profesional_id == usuario.id
    )

    if not es_cliente and not es_profesional:
        return JsonResponse(
            {'error': 'No tienes permiso para consultar este chat'},
            status=403
        )

    # Obtener el último ID recibido por el navegador
    try:
        ultimo_id = int(request.GET.get('desde', 0))
    except (TypeError, ValueError):
        return JsonResponse(
            {'error': 'Identificador de mensaje inválido'},
            status=400
        )

    if ultimo_id < 0:
        return JsonResponse(
            {'error': 'Identificador de mensaje inválido'},
            status=400
        )

    # Consultar mensajes posteriores al último recibido
    mensajes = Mensaje.objects.filter(
        solicitud=solicitud,
        id__gt=ultimo_id
    ).select_related(
        'remitente'
    ).order_by(
        'fecha_envio',
        'id'
    )

    resultado = []

    for mensaje in mensajes:
        resultado.append({
            'id': mensaje.id,
            'remitente_id': mensaje.remitente_id,
            'remitente_nombre': (
                mensaje.remitente.nombre
                + ' '
                + mensaje.remitente.apellido
            ),
            'contenido': mensaje.contenido,
            'fecha': timezone.localtime(
                mensaje.fecha_envio
            ).strftime('%d/%m/%Y %H:%M'),
            'propio': mensaje.remitente_id == usuario.id,
        })

    # Marcar como leídos los mensajes recibidos
    Mensaje.objects.filter(
        solicitud=solicitud,
        id__gt=ultimo_id,
        leido=False
    ).exclude(
        remitente_id=usuario.id
    ).update(
        leido=True
    )

    return JsonResponse({
        'mensajes': resultado
    })


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


@never_cache
def perfil(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # Cambiar foto de perfil
    if request.method == 'POST':

        foto = request.FILES.get('foto')

        if foto:
            usuario.foto = foto
            usuario.save()

        return redirect('perfil')

    # Historial de solicitudes del cliente y del profesional
    conversaciones = Solicitud.objects.filter(
        Q(cliente=usuario) |
        Q(servicio__profesional=usuario)
    ).select_related(
        'cliente',
        'servicio',
        'servicio__profesional'
    ).annotate(
        total_mensajes=Count('mensajes', distinct=True),
        mensajes_no_leidos=Count(
            'mensajes',
            filter=(
                Q(mensajes__leido=False) &
                ~Q(mensajes__remitente=usuario)
            ),
            distinct=True
        )
    ).order_by('-fecha_solicitud')

    # Último mensaje para controlar las notificaciones
    ultimo_mensaje = Mensaje.objects.filter(
        solicitud__in=conversaciones
    ).order_by('-id').values_list(
        'id',
        flat=True
    ).first() or 0

    return render(
        request,
        'perfil.html',
        {
            'usuario': usuario,
            'conversaciones': conversaciones,
            'mensajes_no_leidos': contar_mensajes_no_leidos(usuario),
            'ultimo_mensaje_id': ultimo_mensaje,
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
    solicitud = Solicitud.objects.create(
        cliente=usuario,
        servicio=servicio
    )

    # Notificar al profesional
    Notificacion.objects.create(
        destinatario=servicio.profesional,
        solicitud=solicitud,
        tipo='solicitud',
        titulo='Nueva solicitud de servicio',
        mensaje=(
            f'{usuario.nombre} ha solicitado tu servicio: '
            f'{servicio.nombre}.'
        )
    )

    return redirect('mis_solicitudes')


def mis_solicitudes(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id
    )

    solicitudes = list(
        Solicitud.objects.filter(
            cliente=usuario
        ).select_related(
            'servicio',
            'servicio__profesional'
        ).order_by(
            '-fecha_solicitud'
        )
    )

    from calificaciones.models import Calificacion

    # Calificaciones realizadas por el cliente
    calificaciones_realizadas = set(
        Calificacion.objects.filter(
            calificador=usuario
        ).values_list(
            'solicitud_id',
            flat=True
        )
    )

    # Solicitudes en las que cualquiera de las partes calificó
    solicitudes_con_calificacion = set(
        Calificacion.objects.filter(
            solicitud__in=solicitudes
        ).values_list(
            'solicitud_id',
            flat=True
        ).distinct()
    )

    estados_chat = [
        'aceptada',
        'finalizada',
        'confirmada',
    ]

    # Determinar si cada conversación permite escribir
    for solicitud in solicitudes:

        solicitud.calificacion_realizada = (
            solicitud.id in solicitudes_con_calificacion
        )

        solicitud.chat_habilitado = (
            solicitud.estado in estados_chat
            and not solicitud.calificacion_realizada
        )

    return render(
        request,
        'mis_solicitudes.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes,
            'calificaciones_realizadas': calificaciones_realizadas,
            'solicitudes_con_calificacion': solicitudes_con_calificacion,
        }
    )


def solicitudes_recibidas(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id
    )

    if not usuario.es_profesional:
        return redirect('perfil')

    solicitudes = list(
        Solicitud.objects.filter(
            servicio__profesional=usuario
        ).select_related(
            'cliente',
            'servicio',
            'servicio__profesional'
        ).order_by(
            '-fecha_solicitud'
        )
    )

    # Obtener los identificadores de las solicitudes
    ids_solicitudes = [
        solicitud.id for solicitud in solicitudes
    ]

    # Solicitudes en las que el profesional ya calificó
    calificaciones_realizadas = list(
        Calificacion.objects.filter(
            calificador=usuario,
            solicitud_id__in=ids_solicitudes
        ).values_list(
            'solicitud_id',
            flat=True
        ).distinct()
    )

    # Solicitudes en las que cualquiera de las partes calificó
    solicitudes_con_calificacion = list(
        Calificacion.objects.filter(
            solicitud_id__in=ids_solicitudes
        ).values_list(
            'solicitud_id',
            flat=True
        ).distinct()
    )

    # Determinar si cada chat permite escribir
    estados_chat = [
        'aceptada',
        'finalizada',
        'confirmada',
    ]

    for solicitud in solicitudes:

        solicitud.calificacion_realizada = (
            solicitud.id in solicitudes_con_calificacion
        )

        solicitud.chat_habilitado = (
            solicitud.estado in estados_chat
            and not solicitud.calificacion_realizada
        )

    return render(
        request,
        'solicitudes_recibidas.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes,
            'calificaciones_realizadas': calificaciones_realizadas,
            'solicitudes_con_calificacion': solicitudes_con_calificacion,
        }
    )


def cambiar_estado_solicitud(request, solicitud_id):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    if not usuario.es_profesional:
        return redirect('perfil')

    solicitud = Solicitud.objects.get(id=solicitud_id)

    if solicitud.servicio.profesional != usuario:
        return redirect('solicitudes_recibidas')

    if request.method == 'POST':

        estado = request.POST.get('estado')

        if estado in ['aceptada', 'rechazada', 'finalizada']:

            # Verificar si el profesional tiene deuda pendiente
            if estado == 'aceptada' and usuario.saldo_pendiente > 0:

                solicitudes = list(
                    Solicitud.objects.filter(
                        servicio__profesional=usuario
                    ).select_related(
                        'cliente',
                        'servicio',
                        'servicio__profesional'
                    ).order_by('-fecha_solicitud')
                )

                ids_solicitudes = [s.id for s in solicitudes]

                calificaciones_realizadas = list(
                    Calificacion.objects.filter(
                        calificador=usuario,
                        solicitud_id__in=ids_solicitudes
                    ).values_list(
                        'solicitud_id',
                        flat=True
                    ).distinct()
                )

                solicitudes_con_calificacion = list(
                    Calificacion.objects.filter(
                        solicitud_id__in=ids_solicitudes
                    ).values_list(
                        'solicitud_id',
                        flat=True
                    ).distinct()
                )

                estados_chat = ['aceptada', 'finalizada', 'confirmada']

                for sol in solicitudes:
                    sol.calificacion_realizada = sol.id in solicitudes_con_calificacion
                    sol.chat_habilitado = (
                        sol.estado in estados_chat
                        and not sol.calificacion_realizada
                    )

                return render(
                    request,
                    'solicitudes_recibidas.html',
                    {
                        'usuario': usuario,
                        'solicitudes': solicitudes,
                        'calificaciones_realizadas': calificaciones_realizadas,
                        'solicitudes_con_calificacion': solicitudes_con_calificacion,
                        'error_pago': True,
                        'mensaje_pago': (
                            'No puedes aceptar esta solicitud porque '
                            'tienes un saldo pendiente con InTalent.'
                        )
                    }
                )

            # Guardar el estado anterior
            estado_anterior = solicitud.estado

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

            if estado_anterior != estado:

                mensajes = {
                    'aceptada': 'Tu solicitud ha sido aceptada por el profesional.',
                    'rechazada': 'El profesional ha rechazado tu solicitud.',
                    'finalizada': 'El profesional ha marcado tu servicio como finalizado. Ya puedes confirmar el servicio.'
                }

                titulos = {
                    'aceptada': 'Solicitud aceptada',
                    'rechazada': 'Solicitud rechazada',
                    'finalizada': 'Servicio finalizado'
                }

                Notificacion.objects.create(
                    destinatario=solicitud.cliente,
                    solicitud=solicitud,
                    tipo=estado,
                    titulo=titulos[estado],
                    mensaje=mensajes[estado]
                )

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

        # Mantener al profesional activo
        profesional.estado_profesional = 'activo'

        profesional.save()

        solicitud.estado = 'confirmada'
        solicitud.estado_pago = 'pendiente'
        solicitud.save()

        # Notificar al profesional
        Notificacion.objects.create(
            destinatario=profesional,
            solicitud=solicitud,
            tipo='confirmada',
            titulo='Servicio confirmado',
            mensaje=(
                f'El cliente {usuario.nombre} ha confirmado '
                f'el servicio: {solicitud.servicio.nombre}.'
            )
        )

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