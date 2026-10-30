from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Restaurante


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro de usuario"""

    email = forms.EmailField(required=True, label="Correo electrónico")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
        labels = {
            "username": "Nombre de usuario",
            "email": "Correo electrónico",
            "password1": "Contraseña",
            "password2": "Confirmar contraseña",
        }
        help_texts = {
            "username": "Mínimo 4 caracteres. Letras, números y @/./+/-/_ solamente.",
            "password1": "Mínimo 8 caracteres. No puede ser similar a tu información personal.",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if len(username) < 4:
            raise forms.ValidationError(
                "El nombre de usuario debe tener al menos 4 caracteres."
            )
        return username


class RegistroRestauranteForm(forms.ModelForm):
    """Formulario de registro de restaurante"""

    class Meta:
        model = Restaurante
        fields = [
            "nombre",
            "tipo",
            "descripcion",
            "direccion",
            "telefono",
            "email",
            "logo",
        ]
        labels = {
            "nombre": "Nombre del restaurante",
            "tipo": "Tipo de negocio",
            "descripcion": "Descripción",
            "direccion": "Dirección",
            "telefono": "Teléfono",
            "email": "Correo electrónico",
            "logo": "Logo",
        }
        widgets = {
            "descripcion": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Describe tu restaurante..."}
            ),
            "direccion": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Dirección completa"}
            ),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data.get("telefono")
        if telefono and not telefono.replace("+", "").replace(" ", "").isdigit():
            raise forms.ValidationError(
                "El teléfono debe contener solo números y el signo + opcional."
            )
        return telefono


class RestauranteForm(forms.ModelForm):
    """Formulario para editar restaurante (usado en dashboard)"""

    class Meta:
        model = Restaurante
        fields = [
            "nombre",
            "tipo",
            "descripcion",
            "direccion",
            "telefono",
            "email",
            "logo",
            "mostrar_precios",
            "acepta_pedidos",
            "acepta_reservas",
            "activo",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "direccion": forms.Textarea(attrs={"rows": 2}),
        }
