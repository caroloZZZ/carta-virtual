#!/usr/bin/env python3
"""
Script para crear datos de prueba (categorías, platos, pedidos)
Ejecutar: python crear_datos_prueba.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from restaurantes.models import Restaurante
from menu.models import Categoria, Plato
from pedidos.models import Pedido, ItemPedido

# Colores
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
NC = "\033[0m"

print(f"{BLUE}{'='*60}{NC}")
print(f"{BLUE}📊 CREANDO DATOS DE PRUEBA{NC}")
print(f"{BLUE}{'='*60}{NC}")

# Buscar usuario existente
try:
    user = User.objects.get(username="testuser")
    restaurante = user.restaurante
    print(f"{GREEN}✅ Usuario encontrado: {user.username}{NC}")
except User.DoesNotExist:
    print(f"{YELLOW}⚠️ Usuario testuser no encontrado. Creando...{NC}")
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )
    restaurante = Restaurante.objects.create(
        usuario=user,
        nombre="Restaurante La Prueba",
        descripcion="El mejor restaurante de pruebas",
        direccion="Calle 123, La Habana",
        telefono="+53 7 1234567",
        email="contacto@laprueba.com",
    )
    print(f"{GREEN}✅ Usuario y restaurante creados{NC}")

# Crear categorías
categorias_data = [
    {"nombre": "Entradas", "orden": 1, "icono": "bi-egg-fried"},
    {"nombre": "Platos Principales", "orden": 2, "icono": "bi-egg-fried"},
    {"nombre": "Mariscos", "orden": 3, "icono": "bi-egg-fried"},
    {"nombre": "Carnes", "orden": 4, "icono": "bi-egg-fried"},
    {"nombre": "Pastas", "orden": 5, "icono": "bi-egg-fried"},
    {"nombre": "Ensaladas", "orden": 6, "icono": "bi-egg-fried"},
    {"nombre": "Postres", "orden": 7, "icono": "bi-egg-fried"},
    {"nombre": "Bebidas", "orden": 8, "icono": "bi-egg-fried"},
    {"nombre": "Cafés", "orden": 9, "icono": "bi-egg-fried"},
    {"nombre": "Cócteles", "orden": 10, "icono": "bi-egg-fried"},
]

print(f"\n{YELLOW}📌 Creando categorías...{NC}")
categorias = []
for cat_data in categorias_data:
    cat, created = Categoria.objects.get_or_create(
        restaurante=restaurante,
        nombre=cat_data["nombre"],
        defaults={
            "orden": cat_data["orden"],
            "icono": cat_data["icono"],
            "activa": True,
        },
    )
    categorias.append(cat)
    status = "✅ Creada" if created else "🔄 Ya existe"
    print(f"  {status}: {cat.nombre}")

# Platos por categoría
platos_data = [
    # Entradas
    {
        "categoria": "Entradas",
        "nombre": "Tostones con Mojo",
        "precio": 3.50,
        "descripcion": "Crujientes tostones con mojo criollo",
    },
    {
        "categoria": "Entradas",
        "nombre": "Yuca con Mojo",
        "precio": 4.00,
        "descripcion": "Yuca hervida con mojo de ajo y limón",
    },
    {
        "categoria": "Entradas",
        "nombre": "Tamales",
        "precio": 3.00,
        "descripcion": "Tamales de maíz con cerdo",
    },
    {
        "categoria": "Entradas",
        "nombre": "Croquetas de Jamón",
        "precio": 3.50,
        "descripcion": "Croquetas cremosas de jamón (6 unidades)",
    },
    {
        "categoria": "Entradas",
        "nombre": "Bolitas de Yuca Rellenas",
        "precio": 4.50,
        "descripcion": "Bolitas de yuca rellenas de queso",
    },
    # Platos Principales
    {
        "categoria": "Platos Principales",
        "nombre": "Ropa Vieja",
        "precio": 12.50,
        "descripcion": "Carne desmechada en salsa criolla",
    },
    {
        "categoria": "Platos Principales",
        "nombre": "Lechón Asado",
        "precio": 14.00,
        "descripcion": "Cerdo asado con mojo",
    },
    {
        "categoria": "Platos Principales",
        "nombre": "Arroz con Pollo",
        "precio": 11.00,
        "descripcion": "Arroz amarillo con pollo y vegetales",
    },
    {
        "categoria": "Platos Principales",
        "nombre": "Pollo a la Plancha",
        "precio": 10.50,
        "descripcion": "Pechuga de pollo a la plancha",
    },
    {
        "categoria": "Platos Principales",
        "nombre": "Picadillo a la Criolla",
        "precio": 11.50,
        "descripcion": "Picadillo de res con papas y aceitunas",
    },
    # Mariscos
    {
        "categoria": "Mariscos",
        "nombre": "Camarones al Ajillo",
        "precio": 16.00,
        "descripcion": "Camarones salteados con ajo y vino blanco",
    },
    {
        "categoria": "Mariscos",
        "nombre": "Pescado a la Plancha",
        "precio": 14.50,
        "descripcion": "Filete de pescado fresco a la plancha",
    },
    {
        "categoria": "Mariscos",
        "nombre": "Langosta Enchilada",
        "precio": 22.00,
        "descripcion": "Cola de langosta en salsa enchilada",
    },
    {
        "categoria": "Mariscos",
        "nombre": "Ceviche de Camarón",
        "precio": 13.00,
        "descripcion": "Camarones marinados en cítricos",
    },
    # Carnes
    {
        "categoria": "Carnes",
        "nombre": "Bistec de Palomilla",
        "precio": 13.50,
        "descripcion": "Bistec encebollado",
    },
    {
        "categoria": "Carnes",
        "nombre": "Churrasco",
        "precio": 17.00,
        "descripcion": "Churrasco argentino con chimichurri",
    },
    {
        "categoria": "Carnes",
        "nombre": "Filete Mignon",
        "precio": 19.00,
        "descripcion": "Filete de res envuelto en tocino",
    },
    {
        "categoria": "Carnes",
        "nombre": "Costillas BBQ",
        "precio": 16.50,
        "descripcion": "Costillas de cerdo con salsa barbacoa",
    },
    # Pastas
    {
        "categoria": "Pastas",
        "nombre": "Spaghetti Bolognesa",
        "precio": 12.00,
        "descripcion": "Spaghetti con salsa bolognesa",
    },
    {
        "categoria": "Pastas",
        "nombre": "Lasaña de Carne",
        "precio": 13.50,
        "descripcion": "Lasaña de carne con queso gratinado",
    },
    {
        "categoria": "Pastas",
        "nombre": "Fettuccine Alfredo",
        "precio": 12.50,
        "descripcion": "Fettuccine con salsa Alfredo",
    },
    # Postres
    {
        "categoria": "Postres",
        "nombre": "Flan de Queso",
        "precio": 4.50,
        "descripcion": "Flan cremoso de queso",
    },
    {
        "categoria": "Postres",
        "nombre": "Arroz con Leche",
        "precio": 4.00,
        "descripcion": "Arroz con leche espolvoreado con canela",
    },
    {
        "categoria": "Postres",
        "nombre": "Tres Leches",
        "precio": 5.00,
        "descripcion": "Pastel bañado en tres leches",
    },
    {
        "categoria": "Postres",
        "nombre": "Helado de Mango",
        "precio": 3.50,
        "descripcion": "Helado artesanal de mango",
    },
    # Bebidas
    {
        "categoria": "Bebidas",
        "nombre": "Refresco de Cola",
        "precio": 2.00,
        "descripcion": "Refresco nacional",
    },
    {
        "categoria": "Bebidas",
        "nombre": "Agua Mineral",
        "precio": 1.50,
        "descripcion": "Agua mineral con/sin gas",
    },
    {
        "categoria": "Bebidas",
        "nombre": "Jugo de Mango",
        "precio": 3.00,
        "descripcion": "Jugo natural de mango",
    },
    {
        "categoria": "Bebidas",
        "nombre": "Jugo de Guayaba",
        "precio": 3.00,
        "descripcion": "Jugo natural de guayaba",
    },
    # Cócteles
    {
        "categoria": "Cócteles",
        "nombre": "Mojito Cubano",
        "precio": 6.00,
        "descripcion": "Ron, hierbabuena, limón, azúcar y soda",
    },
    {
        "categoria": "Cócteles",
        "nombre": "Cuba Libre",
        "precio": 5.50,
        "descripcion": "Ron con cola",
    },
    {
        "categoria": "Cócteles",
        "nombre": "Daiquiri",
        "precio": 6.00,
        "descripcion": "Ron, limón y azúcar",
    },
    {
        "categoria": "Cócteles",
        "nombre": "Piña Colada",
        "precio": 7.00,
        "descripcion": "Ron, crema de coco y piña",
    },
]

print(f"\n{YELLOW}📌 Creando platos...{NC}")
platos_creados = []
for plato_data in platos_data:
    categoria = Categoria.objects.get(
        restaurante=restaurante, nombre=plato_data["categoria"]
    )
    plato, created = Plato.objects.get_or_create(
        categoria=categoria,
        nombre=plato_data["nombre"],
        defaults={
            "descripcion": plato_data["descripcion"],
            "precio": plato_data["precio"],
            "disponible": True,
            "destacado": random.choice([True, False]),
            "es_vegetariano": random.choice([True, False]),
            "es_picante": random.choice([True, False]),
            "tiempo_preparacion": random.randint(10, 30),
        },
    )
    platos_creados.append(plato)
    status = "✅ Creado" if created else "🔄 Ya existe"
    print(f"  {status}: {plato.nombre} - ${plato.precio}")

print(f"\n{YELLOW}📌 Creando pedidos de prueba (últimos 30 días)...{NC}")

estados = ["pendiente", "confirmado", "preparando", "listo", "entregado", "cancelado"]
metodos_pago = ["efectivo", "transferencia", "tarjeta"]
nombres_clientes = [
    "Juan Pérez",
    "María García",
    "Carlos Rodríguez",
    "Ana Martínez",
    "José López",
    "Laura Sánchez",
    "Pedro Díaz",
    "Carmen Ruiz",
    "Roberto Gómez",
    "Isabel Torres",
    "Miguel Castro",
    "Díaz",
]

for i in range(50):  # Crear 50 pedidos
    fecha = datetime.now() - timedelta(days=random.randint(0, 30))

    pedido = Pedido.objects.create(
        restaurante=restaurante,
        estado=random.choice(estados),
        nombre_cliente=random.choice(nombres_clientes),
        telefono_cliente=f"+53 {random.randint(50000000, 59999999)}",
        mesa=str(random.randint(1, 10)) if random.choice([True, False]) else "",
        notas=random.choice(["", "Sin cebolla", "Bien cocido", "Sin sal"]),
        metodo_pago=random.choice(metodos_pago),
        pagado=random.choice([True, False]),
        fecha_creacion=fecha,
    )

    # Agregar items al pedido
    total = 0
    for _ in range(random.randint(1, 5)):
        plato = random.choice(platos_creados)
        cantidad = random.randint(1, 3)
        precio = plato.precio
        subtotal = precio * cantidad
        total += subtotal

        ItemPedido.objects.create(
            pedido=pedido,
            plato=plato,
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=subtotal,
            notas=random.choice(["", "Sin sal", "Bien cocido", "Extra salsa"]),
        )

    pedido.total = total
    pedido.save()

print(f"{GREEN}  ✅ 50 pedidos creados{NC}")

print(f"\n{BLUE}{'='*60}{NC}")
print(f"{GREEN}✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE{NC}")
print(f"{BLUE}{'='*60}{NC}")
print(f"\n📊 Resumen:")
print(f"  • Categorías: {Categoria.objects.filter(restaurante=restaurante).count()}")
print(f"  • Platos: {Plato.objects.filter(categoria__restaurante=restaurante).count()}")
print(f"  • Pedidos: {Pedido.objects.filter(restaurante=restaurante).count()}")
print(f"\n{YELLOW}🔐 Acceso:{NC}")
print(f"  Usuario: testuser")
print(f"  Password: testpass123")
