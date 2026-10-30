# download_images.py
import os
import requests
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
import django

# Configurar Django para poder usar los modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from menu.models import Plato, Categoria
from restaurantes.models import Restaurante

# Definir imágenes (nombre del plato y URL)
# Estas URLs son de Unsplash y son libres de uso (dominio público)
IMAGENES = [
    (
        "Pizza Margherita",
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
    ),
    (
        "Ensalada César",
        "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
    ),
    (
        "Pasta Carbonara",
        "https://images.unsplash.com/photo-1556761223-4c4282c73f77?w=400&h=300&fit=crop",
    ),
    (
        "Hamburguesa Clásica",
        "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400&h=300&fit=crop",
    ),
    (
        "Tacos al Pastor",
        "https://images.unsplash.com/photo-1599974579688-8dbdd335c77f?w=400&h=300&fit=crop",
    ),
    (
        "Salmón a la Plancha",
        "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400&h=300&fit=crop",
    ),
    (
        "Tiramisú",
        "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400&h=300&fit=crop",
    ),
    (
        "Batido de Frutas",
        "https://images.unsplash.com/photo-1534685785745-60e2a1f8d6b9?w=400&h=300&fit=crop",
    ),
    (
        "Café Expreso",
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=400&h=300&fit=crop",
    ),
    (
        "Pulpo a la Gallega",
        "https://images.unsplash.com/photo-1561998338-13ad7883b831?w=400&h=300&fit=crop",
    ),
    (
        "Paella Valenciana",
        "https://images.unsplash.com/photo-1534080564583-6be75777b70a?w=400&h=300&fit=crop",
    ),
    (
        "Croquetas Caseras",
        "https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=400&h=300&fit=crop",
    ),
]

# Crear directorio si no existe
os.makedirs(settings.MEDIA_ROOT / "menu" / "platos", exist_ok=True)

# Para cada plato, descargar la imagen y guardarla
for nombre, url in IMAGENES:
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        # Crear un archivo temporal
        temp = NamedTemporaryFile(delete=True)
        for chunk in response.iter_content(chunk_size=1024):
            temp.write(chunk)
        temp.flush()

        # Generar nombre de archivo basado en el nombre del plato
        slug = (
            nombre.lower()
            .replace(" ", "_")
            .replace("á", "a")
            .replace("é", "e")
            .replace("í", "i")
            .replace("ó", "o")
            .replace("ú", "u")
        )
        filename = f"{slug}.jpg"

        # Guardar en el modelo Plato correspondiente (si existe)
        # Primero, necesitamos tener los platos creados.
        # Esto solo descarga, luego asignaremos las imágenes desde el admin o un comando.
        # Guardamos físicamente el archivo
        with open(settings.MEDIA_ROOT / "menu" / "platos" / filename, "wb") as f:
            temp.seek(0)
            f.write(temp.read())
        print(f"Imagen guardada: {filename}")

print("Descarga completada.")
