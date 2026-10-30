"""
Sistema de control de versiones para templates
"""

import os
import hashlib
import json
from pathlib import Path
from django.conf import settings


class TemplateVersionControl:
    """Control de versiones para templates"""

    VERSION_FILE = "template_versions.json"

    @classmethod
    def get_template_hash(cls, template_path):
        """Calcula hash de un template"""
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
                return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            return None

    @classmethod
    def scan_templates(cls):
        """Escanea todos los templates y genera versión"""
        templates_dir = settings.BASE_DIR / "templates"

        if not templates_dir.exists():
            return {}

        template_versions = {}

        for root, dirs, files in os.walk(templates_dir):
            for file in files:
                if file.endswith(".html"):
                    template_path = Path(root) / file
                    relative_path = template_path.relative_to(templates_dir)

                    # Calcular hash
                    file_hash = cls.get_template_hash(template_path)

                    if file_hash:
                        template_versions[str(relative_path)] = {
                            "hash": file_hash,
                            "path": str(template_path),
                            "size": os.path.getsize(template_path),
                            "last_modified": os.path.getmtime(template_path),
                        }

        return template_versions

    @classmethod
    def save_versions(cls):
        """Guarda las versiones actuales"""
        versions = cls.scan_templates()
        version_file = settings.BASE_DIR / cls.VERSION_FILE

        with open(version_file, "w", encoding="utf-8") as f:
            json.dump(versions, f, indent=2)

        return versions

    @classmethod
    def load_versions(cls):
        """Carga las versiones guardadas"""
        version_file = settings.BASE_DIR / cls.VERSION_FILE

        if not version_file.exists():
            return {}

        with open(version_file, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def check_for_changes(cls):
        """Verifica cambios en los templates"""
        saved_versions = cls.load_versions()
        current_versions = cls.scan_templates()

        changes = {"added": [], "modified": [], "deleted": [], "unchanged": []}

        # Verificar templates nuevos y modificados
        for template, current_data in current_versions.items():
            if template not in saved_versions:
                changes["added"].append(template)
            elif current_data["hash"] != saved_versions[template]["hash"]:
                changes["modified"].append(template)
            else:
                changes["unchanged"].append(template)

        # Verificar templates eliminados
        for template in saved_versions:
            if template not in current_versions:
                changes["deleted"].append(template)

        return changes

    @classmethod
    def validate_template_structure(cls):
        """Valida la estructura de templates"""
        required_dirs = [
            "templates/base",
            "templates/auth",
            "templates/core",
            "templates/dashboard",
            "templates/clientes",
            "templates/includes",
        ]

        required_files = [
            "templates/base/base.html",
            "templates/base/base_dashboard.html",
            "templates/auth/login.html",
            "templates/auth/register.html",
            "templates/core/home.html",
            "templates/dashboard/index.html",
        ]

        errors = []
        warnings = []

        base_dir = settings.BASE_DIR

        # Verificar directorios
        for dir_path in required_dirs:
            full_path = base_dir / dir_path
            if not full_path.exists():
                errors.append(f"Directorio faltante: {dir_path}")
            elif not list(full_path.iterdir()):
                warnings.append(f"Directorio vacío: {dir_path}")

        # Verificar archivos
        for file_path in required_files:
            full_path = base_dir / file_path
            if not full_path.exists():
                errors.append(f"Archivo faltante: {file_path}")
            elif full_path.stat().st_size == 0:
                warnings.append(f"Archivo vacío: {file_path}")

        return {"errors": errors, "warnings": warnings, "passed": len(errors) == 0}
