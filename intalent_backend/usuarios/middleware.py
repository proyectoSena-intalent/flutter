
from django.shortcuts import redirect
from django.urls import resolve


class AutenticacionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Permitir todas las rutas del administrador de Django
        if request.path_info.startswith('/admin/'):
            return self.get_response(request)

        # Obtener la ruta actual
        nombre_url = resolve(request.path_info).url_name

        # Rutas públicas de InTalent
        rutas_publicas = [
            'login',
            'registro',
            'invitado',
            'api_login',
            'recuperar_contraseña',
            'restablecer_contrasena',
        ]

        # Permitir rutas públicas
        if nombre_url in rutas_publicas:
            return self.get_response(request)

        # Verificar sesión personalizada de InTalent
        usuario_id = request.session.get('usuario_id')

        # Si no existe sesión, enviar al login
        if not usuario_id:
            return redirect('login')

        # Usuario autenticado
        return self.get_response(request)
