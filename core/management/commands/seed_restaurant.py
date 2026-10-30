from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato
from django.contrib.auth.models import User
import os


class Command(BaseCommand):
    help = "Crea un restaurante de ejemplo con categorías y platos"

    def handle(self, *args, **options):
        # Crear usuario si no existe
        user, created = User.objects.get_or_create(
            username="restaurante_ejemplo", defaults={"email": "ejemplo@mail.com"}
        )
        if created:
            user.set_password("admin123")
            user.save()
            self.stdout.write(
                self.style.SUCCESS("Usuario creado: restaurante_ejemplo / admin123")
            )
        else:
            self.stdout.write("Usuario ya existe")

        # Crear restaurante
        restaurante, created = Restaurante.objects.get_or_create(
            usuario=user,
            defaults={
                "nombre": "El Buen Sabor",
                "slug": "el-buen-sabor",
                "tipo": "restaurante",
                "descripcion": "Sabores auténticos de la cocina cubana e internacional.",
                "direccion": "Calle 23 #456, La Habana",
                "telefono": "+53 7 123 4567",
                "email": "info@elbuensabor.cu",
                "activo": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Restaurante creado: El Buen Sabor"))
        else:
            self.stdout.write("Restaurante ya existe")

        # Categorías
        categorias_data = [
            {"nombre": "Entradas", "orden": 1, "icono": "bi-egg-fried"},
            {"nombre": "Platos Principales", "orden": 2, "icono": "bi-egg-fried"},
            {"nombre": "Postres", "orden": 3, "icono": "bi-cake"},
            {"nombre": "Bebidas", "orden": 4, "icono": "bi-cup-straw"},
        ]
        categorias = {}
        for cat in categorias_data:
            categoria, created = Categoria.objects.get_or_create(
                restaurante=restaurante,
                nombre=cat["nombre"],
                defaults={"orden": cat["orden"], "icono": cat["icono"], "activa": True},
            )
            categorias[cat["nombre"]] = categoria
            if created:
                self.stdout.write(f'Categoría creada: {cat["nombre"]}')

        # Platos (nombre, categoría, precio, descripción, imagen)
        platos_data = [
            (
                "Croquetas de Jamón",
                "Entradas",
                4.50,
                "Croquetas cremosas de jamón ibérico.",
            ),
            (
                "Tostones Rellenos",
                "Entradas",
                5.00,
                "Tostones de plátano macho rellenos de ropa vieja.",
            ),
            (
                "Pizza Margherita",
                "Platos Principales",
                12.00,
                "Mozzarella, tomate y albahaca.",
            ),
            (
                "Ropa Vieja",
                "Platos Principales",
                14.00,
                "Carne desmechada en salsa criolla.",
            ),
            (
                "Arroz con Pollo",
                "Platos Principales",
                11.50,
                "Arroz amarillo con pollo, vegetales y aceitunas.",
            ),
            (
                "Pasta Carbonara",
                "Platos Principales",
                12.50,
                "Pasta con huevo, queso pecorino, guanciale y pimienta.",
            ),
            (
                "Hamburguesa Clásica",
                "Platos Principales",
                10.00,
                "Carne de res, lechuga, tomate, queso y salsa especial.",
            ),
            (
                "Tacos al Pastor",
                "Platos Principales",
                9.00,
                "Tortilla de maíz con cerdo adobado, piña, cilantro y cebolla.",
            ),
            (
                "Salmón a la Plancha",
                "Platos Principales",
                16.00,
                "Salmón fresco con verduras asadas.",
            ),
            (
                "Tiramisú",
                "Postres",
                5.00,
                "Postre italiano con café, mascarpone y cacao.",
            ),
            ("Flan de Queso", "Postres", 4.50, "Flan cremoso con caramelo."),
            ("Batido de Frutas", "Bebidas", 3.50, "Batido natural de mango o guayaba."),
            ("Café Expreso", "Bebidas", 2.00, "Café cubano intenso."),
            (
                "Pulpo a la Gallega",
                "Platos Principales",
                18.00,
                "Pulpo cocido con aceite de oliva, pimentón y sal gruesa.",
            ),
            (
                "Paella Valenciana",
                "Platos Principales",
                20.00,
                "Arroz con mariscos, pollo y verduras.",
            ),
        ]

        for nombre, cat_nombre, precio, desc in platos_data:
            categoria = categorias[cat_nombre]
            # Buscar imagen descargada
            slug = (
                nombre.lower()
                .replace(" ", "_")
                .replace("á", "a")
                .replace("é", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ú", "u")
            )
            ruta_imagen = settings.MEDIA_ROOT / "menu" / "platos" / f"{slug}.jpg"
            imagen_content = None
            if ruta_imagen.exists():
                with open(ruta_imagen, "rb") as f:
                    imagen_content = ContentFile(f.read(), name=f"{slug}.jpg")

            plato, created = Plato.objects.get_or_create(
                categoria=categoria,
                nombre=nombre,
                defaults={
                    "descripcion": desc,
                    "precio": precio,
                    "disponible": True,
                    "destacado": nombre
                    in ["Ropa Vieja", "Paella Valenciana", "Tiramisú"],
                    "es_vegetariano": nombre in ["Pizza Margherita"],
                    "es_picante": nombre in ["Tacos al Pastor"],
                    "tiempo_preparacion": 15 if "Croquetas" in nombre else 25,
                },
            )
            if created:
                self.stdout.write(f"Plato creado: {nombre}")
            if imagen_content and not plato.imagen:
                plato.imagen.save(f"{slug}.jpg", imagen_content, save=True)
                self.stdout.write(f"  Imagen asignada: {slug}.jpg")

        self.stdout.write(
            self.style.SUCCESS("¡Restaurante de ejemplo creado con éxito!")
        )
