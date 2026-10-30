#!/usr/bin/env python3
"""
Script para mostrar la estructura completa del proyecto Carta Virtual Cuba.
Ejecutar: python tree_project.py
"""

import os
import sys
from pathlib import Path


# Colores para la terminal
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


# Iconos para tipos de archivo
ICON_DIR = "📁"
ICON_PY = "🐍"
ICON_HTML = "🌐"
ICON_CSS = "🎨"
ICON_JS = "⚡"
ICON_TXT = "📄"
ICON_IMG = "🖼️"
ICON_MD = "📝"
ICON_DB = "🗄️"


def get_icon(filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".py":
        return ICON_PY
    elif ext == ".html":
        return ICON_HTML
    elif ext == ".css":
        return ICON_CSS
    elif ext == ".js":
        return ICON_JS
    elif ext in [".txt", ".md"]:
        return ICON_TXT if ext == ".txt" else ICON_MD
    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".ico"]:
        return ICON_IMG
    elif ext == ".sqlite3":
        return ICON_DB
    else:
        return "📄"


def print_tree(startpath, indent="", max_depth=None, current_depth=0):
    if max_depth is not None and current_depth > max_depth:
        return
    try:
        items = sorted(os.listdir(startpath))
    except PermissionError:
        return
    dirs = []
    files = []
    for item in items:
        full = os.path.join(startpath, item)
        if os.path.isdir(full):
            # Ignorar __pycache__, .git, venv, etc.
            if item in ["__pycache__", ".git", ".idea", "venv", "env", "__pycache__"]:
                continue
            dirs.append(item)
        else:
            files.append(item)
    # Imprimir directorios
    for i, d in enumerate(dirs):
        is_last = (i == len(dirs) - 1) and len(files) == 0
        connector = "└── " if is_last else "├── "
        print(f"{indent}{connector}{ICON_DIR} {Colors.BLUE}{d}{Colors.ENDC}/")
        extension = "    " if is_last else "│   "
        print_tree(
            os.path.join(startpath, d), indent + extension, max_depth, current_depth + 1
        )
    # Imprimir archivos
    for i, f in enumerate(files):
        is_last = i == len(files) - 1
        connector = "└── " if is_last else "├── "
        icon = get_icon(f)
        print(f"{indent}{connector}{icon} {Colors.GREEN}{f}{Colors.ENDC}")


def print_summary():
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}   📊 RESUMEN DEL PROYECTO{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

    # Contar archivos por tipo
    py_count = 0
    html_count = 0
    css_count = 0
    js_count = 0
    total_files = 0
    for root, dirs, files in os.walk("."):
        if "venv" in root or "__pycache__" in root or ".git" in root:
            continue
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            if ext == ".py":
                py_count += 1
            elif ext == ".html":
                html_count += 1
            elif ext == ".css":
                css_count += 1
            elif ext == ".js":
                js_count += 1

    print(f"\n{Colors.CYAN}📈 Archivos totales: {total_files}{Colors.ENDC}")
    print(f"  • Python: {py_count}")
    print(f"  • HTML: {html_count}")
    print(f"  • CSS: {css_count}")
    print(f"  • JavaScript: {js_count}")

    # Aplicaciones principales
    apps = [
        "core",
        "restaurantes",
        "menu",
        "pedidos",
        "clientes",
        "dashboard",
        "reservas",
    ]
    print(f"\n{Colors.CYAN}🏗️ Aplicaciones:{Colors.ENDC}")
    for app in apps:
        if os.path.isdir(app):
            print(f"  • {app}/")

    # Modelos importantes
    print(f"\n{Colors.CYAN}🗄️ Modelos principales:{Colors.ENDC}")
    models_info = {
        "restaurantes": "Restaurante",
        "menu": "Categoria, Plato",
        "pedidos": "Pedido, ItemPedido",
        "reservas": "Reserva",
        "core": "ConfiguracionSistema, Auditoria, etc.",
    }
    for app, models in models_info.items():
        if os.path.isdir(app):
            print(f"  • {app}: {models}")

    # Funcionalidades implementadas
    print(f"\n{Colors.CYAN}✅ Funcionalidades completadas:{Colors.ENDC}")
    print("  • Autenticación (login/registro)")
    print("  • Gestión de restaurantes (perfil, QR)")
    print("  • Gestión de menú (categorías, platos)")
    print("  • Sistema de pedidos (carrito, checkout)")
    print("  • Dashboard administrativo completo")
    print("  • Reservas (gestión desde dashboard)")
    print("  • Vista pública de carta con carrito")
    print("  • Reservas públicas (desde la carta)")
    print("  • Código QR funcional para acceso móvil")


def main():
    project_root = os.getcwd()
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(
        f"{Colors.HEADER}{Colors.BOLD}   📁 ESTRUCTURA COMPLETA - CARTA VIRTUAL CUBA{Colors.ENDC}"
    )
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"\n📂 Proyecto raíz: {Colors.CYAN}{project_root}{Colors.ENDC}\n")

    print_tree(project_root, max_depth=3)  # Mostrar hasta profundidad 3 para no saturar
    print_summary()


if __name__ == "__main__":
    main()
