from django.shortcuts import render, redirect
from .models import Calificacion
from usuarios.models import Usuario, Solicitud


def crear_calificacion(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = Usuario.objects.get(id=usuario_id)

    pendientes = []

    # ==========================================
    # SI EL USUARIO ES CLIENTE
    # ==========================================

    solicitudes_cliente = Solicitud.objects.filter(
        cliente=usuario,
        estado='confirmada'
    ).select_related(
        'servicio',
        'servicio__profesional'
    )

    for solicitud in solicitudes_cliente:

        profesional = solicitud.servicio.profesional

        ya_califico = Calificacion.objects.filter(
            solicitud=solicitud,
            calificador=usuario,
            calificado=profesional
        ).exists()

        if not ya_califico:

            pendientes.append({
                'solicitud': solicitud,
                'persona': profesional,
                'rol': 'Profesional'
            })

    # ==========================================
    # SI EL USUARIO ES PROFESIONAL
    # ==========================================

    solicitudes_profesional = Solicitud.objects.filter(
        servicio__profesional=usuario,
        estado='confirmada'
    ).select_related(
        'cliente',
        'servicio'
    )

    for solicitud in solicitudes_profesional:

        cliente = solicitud.cliente

        ya_califico = Calificacion.objects.filter(
            solicitud=solicitud,
            calificador=usuario,
            calificado=cliente
        ).exists()

        if not ya_califico:

            pendientes.append({
                'solicitud': solicitud,
                'persona': cliente,
                'rol': 'Cliente'
            })

    # ==========================================
    # GUARDAR CALIFICACIÓN
    # ==========================================

    if request.method == 'POST':

        calificado_id = request.POST.get('calificado')
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario')

        if not calificado_id or not puntuacion:

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'Debe seleccionar un usuario y una puntuación.'
                }
            )

        # Buscar la solicitud correspondiente
        solicitud_calificada = None

        for pendiente in pendientes:

            if pendiente['persona'].id == int(calificado_id):

                solicitud_calificada = pendiente['solicitud']

                break

        if solicitud_calificada is None:

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'No se encontró la solicitud.'
                }
            )

        # Crear la calificación asociada a la solicitud
        Calificacion.objects.create(
            solicitud=solicitud_calificada,
            calificador=usuario,
            calificado_id=calificado_id,
            puntuacion=puntuacion,
            comentario=comentario
        )

        return redirect('crear_calificacion')

    return render(
        request,
        'calificaciones.html',
        {
            'usuario': usuario,
            'pendientes': pendientes,
            'error': None
        }
    )
def ver_calificaciones(request, usuario_id):

    usuario = Usuario.objects.get(id=usuario_id)

    calificaciones = Calificacion.objects.filter(
        calificado=usuario
    ).select_related(
        'calificador'
    ).order_by('-fecha')

    promedio = 0

    if calificaciones.exists():

        total = sum(
            calificacion.puntuacion
            for calificacion in calificaciones
        )

        promedio = round(
            total / calificaciones.count(),
            1
        )

    return render(
        request,
        'ver_calificaciones.html',
        {
            'usuario': usuario,
            'calificaciones': calificaciones,
            'promedio': promedio,
        }
    )