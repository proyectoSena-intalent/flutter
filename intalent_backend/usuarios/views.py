from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from .models import Usuario, Servicio, Solicitud
from .forms import ServicioForm


def registro(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        contraseña = request.POST.get('contraseña')
        contraseña_segura = make_password(contraseña)
        tipo_usuario = request.POST.get('tipo_usuario')

        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            contraseña=contraseña_segura,
            tipo_usuario=tipo_usuario
        )

        return redirect('registro')

    return render(request, 'registro.html')

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

    return render(
        request,
        'inicio.html',
        {'usuario': usuario}
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

    return render(
        request,
        'mis_solicitudes.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes
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

    return render(
        request,
        'solicitudes_recibidas.html',
        {
            'usuario': usuario,
            'solicitudes': solicitudes
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

        if estado in ['aceptada', 'rechazada']:

            solicitud.estado = estado
            solicitud.save()

    return redirect('solicitudes_recibidas')

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