from django import forms
from .models import Servicio


class ServicioForm(forms.ModelForm):

    class Meta:
        model = Servicio

        fields = [
            'nombre',
            'categoria',
            'descripcion',
            'precio',
        ]

        labels = {
            'nombre': 'Nombre del servicio',
            'categoria': 'Categoría',
            'descripcion': 'Descripción',
            'precio': 'Precio',
        }

        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': 'Ejemplo: Electricista a domicilio'
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'placeholder': 'Describe el servicio que ofreces',
                    'rows': 5
                }
            ),

            'precio': forms.NumberInput(
                attrs={
                    'placeholder': 'Ejemplo: 60000',
                    'min': '0'
                }
            ),
        }
