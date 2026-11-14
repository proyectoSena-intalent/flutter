from .models import Calificacion
from usuarios.models import Usuario, Solicitud
from django.shortcuts import render, redirect, get_object_or_404


def crear_calificacion(request):

    usuario_id = request.session.get('usuario_id')

    if not usuario_id:
        return redirect('login')

    usuario = get_object_or_404(
        Usuario,
        id=usuario_id
    )

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

        solicitud_id = request.POST.get('solicitud_id')
        calificado_id = request.POST.get('calificado')
        puntuacion = request.POST.get('puntuacion')
        comentario = request.POST.get('comentario', '').strip()

        if not solicitud_id or not calificado_id or not puntuacion:

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'Debe seleccionar una solicitud y una puntuación.'
                }
            )

        # Validar que la puntuación sea de 1 a 5
        try:
            puntuacion = int(puntuacion)
            solicitud_id = int(solicitud_id)
            calificado_id = int(calificado_id)

        except (ValueError, TypeError):

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'Los datos de la calificación no son válidos.'
                }
            )

        if puntuacion not in [1, 2, 3, 4, 5]:

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'La puntuación debe estar entre 1 y 5.'
                }
            )

        # Buscar la solicitud exacta entre las pendientes
        pendiente_seleccionado = next(
            (
                pendiente for pendiente in pendientes
                if pendiente['solicitud'].id == solicitud_id
                and pendiente['persona'].id == calificado_id
            ),
            None
        )

        if pendiente_seleccionado is None:

            return render(
                request,
                'calificaciones.html',
                {
                    'usuario': usuario,
                    'pendientes': pendientes,
                    'error': 'No tienes permiso para realizar esta calificación.'
                }
            )

        solicitud_calificada = pendiente_seleccionado['solicitud']
        persona_calificada = pendiente_seleccionado['persona']

        # Evitar calificaciones duplicadas
        ya_existe = Calificacion.objects.filter(
            solicitud=solicitud_calificada,
            calificador=usuario,
            calificado=persona_calificada
        ).exists()

        if ya_existe:

            return redirect('crear_calificacion')

        # Guardar la calificación
        Calificacion.objects.create(
            solicitud=solicitud_calificada,
            calificador=usuario,
            calificado=persona_calificada,
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