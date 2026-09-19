from django.shortcuts import render, redirect
from .models import Usuario


def registro(request):

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        tipo_usuario = request.POST.get('tipo_usuario')

        Usuario.objects.create(
            nombre=nombre,
            apellido=apellido,
            correo=correo,
            telefono=telefono,
            tipo_usuario=tipo_usuario
        )

        return redirect('registro')

    return render(request, 'registro.html')