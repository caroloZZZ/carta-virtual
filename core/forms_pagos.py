from django import forms
from django.core.validators import MinValueValidator


class PropinaForm(forms.Form):
    """Formulario para agregar propina"""

    OPCIONES_PROPINA = [
        (0, "No agregar propina"),
        (10, "10% - Excelente servicio"),
        (15, "15% - Servicio excepcional"),
        (20, "20% - ¡Increíble!"),
    ]

    porcentaje_propina = forms.ChoiceField(
        choices=OPCIONES_PROPINA, widget=forms.RadioSelect, initial=0
    )
    propina_manual = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={"placeholder": "0.00"}),
    )


class PagoTarjetaForm(forms.Form):
    """Formulario para pago con tarjeta (simulado para demo)"""

    numero_tarjeta = forms.CharField(
        max_length=19,
        widget=forms.TextInput(attrs={"placeholder": "1234 5678 9012 3456"}),
    )
    nombre_titular = forms.CharField(max_length=100)
    fecha_expiracion = forms.CharField(
        max_length=5, widget=forms.TextInput(attrs={"placeholder": "MM/YY"})
    )
    cvv = forms.CharField(
        max_length=3, widget=forms.PasswordInput(attrs={"placeholder": "123"})
    )
    guardar_tarjeta = forms.BooleanField(required=False, initial=False)


class PagoTransfermovilForm(forms.Form):
    """Formulario para pago con Transfermóvil"""

    telefono = forms.CharField(
        max_length=8, widget=forms.TextInput(attrs={"placeholder": "5xxxxxxx"})
    )
    confirmar_telefono = forms.CharField(
        max_length=8, widget=forms.TextInput(attrs={"placeholder": "5xxxxxxx"})
    )

    def clean(self):
        cleaned_data = super().clean()
        telefono = cleaned_data.get("telefono")
        confirmar = cleaned_data.get("confirmar_telefono")

        if telefono and confirmar and telefono != confirmar:
            raise forms.ValidationError("Los números de teléfono no coinciden")

        return cleaned_data
