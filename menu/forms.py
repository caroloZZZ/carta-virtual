from django import forms
from .models import Categoria, Plato


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion", "orden", "icono", "activa"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "icono": forms.Select(
                choices=[
                    ("", "Seleccionar icono"),
                    ("fa-utensils", "Utensilios"),
                    ("fa-hamburger", "Hamburguesa"),
                    ("fa-pizza-slice", "Pizza"),
                    ("fa-fish", "Pescado"),
                    ("fa-ice-cream", "Helado"),
                    ("fa-coffee", "Café"),
                    ("fa-cocktail", "Coctel"),
                    ("fa-wine-glass", "Vino"),
                    ("fa-lemon", "Limón"),
                    ("fa-seedling", "Vegetariano"),
                    ("fa-fire", "Picante"),
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["orden"].widget.attrs.update({"min": "0", "max": "100"})


class PlatoForm(forms.ModelForm):
    class Meta:
        model = Plato
        fields = [
            "categoria",
            "nombre",
            "descripcion",
            "precio",
            "imagen",
            "disponible",
            "destacado",
            "es_vegetariano",
            "es_picante",
            "contiene_gluten",
            "calorias",
            "tiempo_preparacion",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "calorias": forms.NumberInput(attrs={"min": "0"}),
            "tiempo_preparacion": forms.NumberInput(attrs={"min": "1"}),
        }

    def __init__(self, *args, **kwargs):
        restaurante = kwargs.pop("restaurante", None)
        super().__init__(*args, **kwargs)

        if restaurante:
            self.fields["categoria"].queryset = Categoria.objects.filter(
                restaurante=restaurante, activa=True
            )

        # Estilizar campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})
