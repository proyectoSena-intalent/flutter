from django.contrib import admin
from django.db.models import Sum
from .models import Usuario, Servicio, Solicitud


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
    
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'nombre',
        'categoria',
        'precio',
        'profesional',
        'fecha_registro',
    )

    search_fields = (
        'nombre',
        'descripcion',
    )

    list_filter = (
        'categoria',
    )


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'cliente',
        'servicio',
        'estado',
        'precio_acordado',
        'comision_in_talent',
        'valor_profesional',
        'estado_pago',
        'fecha_solicitud',
    )

    list_filter = (
        'estado',
        'estado_pago',
    )

    search_fields = (
        'cliente__nombre',
        'cliente__apellido',
        'servicio__nombre',
        'referencia_pago',
    )

    readonly_fields = (
        'comision_in_talent',
        'valor_profesional',
    )

    change_list_template = 'admin/usuarios/solicitud/change_list.html'

    def changelist_view(self, request, extra_context=None):

        response = super().changelist_view(
            request,
            extra_context=extra_context
        )

        try:

            queryset = response.context_data['cl'].queryset

            solicitudes_finalizadas = queryset.filter(
                estado__in=['finalizada', 'confirmada']
            )

            total_servicios = solicitudes_finalizadas.count()

            total_bruto = solicitudes_finalizadas.aggregate(
                total=Sum('precio_acordado')
            )['total'] or 0

            total_comision = solicitudes_finalizadas.aggregate(
                total=Sum('comision_in_talent')
            )['total'] or 0

            total_profesional = solicitudes_finalizadas.aggregate(
                total=Sum('valor_profesional')
            )['total'] or 0

            total_saldos_pendientes = Usuario.objects.filter(
                es_profesional=True
            ).aggregate(
                total=Sum('saldo_pendiente')
            )['total'] or 0

            response.context_data['total_servicios'] = total_servicios
            response.context_data['total_bruto'] = total_bruto
            response.context_data['total_comision'] = total_comision
            response.context_data['total_profesional'] = total_profesional
            response.context_data['total_saldos_pendientes'] = total_saldos_pendientes

        except (AttributeError, KeyError):
            pass

        return response