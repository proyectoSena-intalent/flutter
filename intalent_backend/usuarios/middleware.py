from django.shortcuts import redirect
from django.urls import resolve


class AutenticacionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # Obtener la ruta actual
        nombre_url = resolve(request.path_info).url_name

        # Rutas que pueden utilizarse sin iniciar sesión
        rutas_publicas = [
            'login',
            'registro',
            'invitado',
            'api_login',
            'recuperar_contraseña',
            'restablecer_contrasena',
            'admin:login',
        ]

        # Si la ruta es pública, permitir el acceso
        if nombre_url in rutas_publicas:
            return self.get_response(request)

        # Verificar si existe una sesión de usuario
        usuario_id = request.session.get('usuario_id')

        # Si no existe sesión, enviar al login
        if not usuario_id:
            return redirect('login')

        # Usuario autenticado
        return self.get_response(request)