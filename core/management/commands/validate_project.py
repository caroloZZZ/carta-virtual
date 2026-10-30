"""
Comando para validar todo el proyecto
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import sys
import os


class Command(BaseCommand):
    help = "Valida todo el proyecto Django (URLs, templates, settings)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--fix",
            action="store_true",
            help="Intentar corregir errores automáticamente",
        )
        parser.add_argument(
            "--strict", action="store_true", help="Modo estricto (falla con warnings)"
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("=" * 80))
        self.stdout.write(self.style.SUCCESS("🚀 VALIDACIÓN COMPLETA DEL PROYECTO"))
        self.stdout.write(self.style.SUCCESS("=" * 80))

        results = {"checks": [], "errors": 0, "warnings": 0, "successes": 0}

        # 1. Validar settings
        self.stdout.write("\n1. 📋 Validando configuración...")
        settings_result = self.validate_settings()
        results["checks"].append(settings_result)

        # 2. Validar URLs
        self.stdout.write("\n2. 🔗 Validando URLs...")
        urls_result = self.validate_urls()
        results["checks"].append(urls_result)

        # 3. Validar templates
        self.stdout.write("\n3. 🎨 Validando templates...")
        templates_result = self.validate_templates()
        results["checks"].append(templates_result)

        # 4. Validar modelos
        self.stdout.write("\n4. 🗄️  Validando modelos...")
        models_result = self.validate_models()
        results["checks"].append(models_result)

        # 5. Validar migraciones
        self.stdout.write("\n5. 📦 Validando migraciones...")
        migrations_result = self.validate_migrations()
        results["checks"].append(migrations_result)

        # 6. Validar static files
        self.stdout.write("\n6. 🎯 Validando archivos estáticos...")
        static_result = self.validate_static_files()
        results["checks"].append(static_result)

        # Resumen
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS("📊 RESUMEN DE VALIDACIÓN"))
        self.stdout.write("=" * 80)

        for check in results["checks"]:
            if check["type"] == "error":
                results["errors"] += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ {check['name']}: {check['message']}")
                )
            elif check["type"] == "warning":
                results["warnings"] += 1
                self.stdout.write(
                    self.style.WARNING(f"⚠️  {check['name']}: {check['message']}")
                )
            else:
                results["successes"] += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ {check['name']}: {check['message']}")
                )

        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.SUCCESS(f"✅ Exitosos: {results['successes']}"))
        self.stdout.write(
            self.style.WARNING(f"⚠️  Advertencias: {results['warnings']}")
        )
        self.stdout.write(self.style.ERROR(f"❌ Errores: {results['errors']}"))
        self.stdout.write("=" * 80)

        # Si hay errores y estamos en modo estricto, salir con error
        if results["errors"] > 0 and options["strict"]:
            self.stdout.write(
                self.style.ERROR("\n❌ Validación fallida en modo estricto")
            )
            sys.exit(1)

        if results["errors"] == 0:
            self.stdout.write(
                self.style.SUCCESS("\n🎉 ¡Proyecto validado exitosamente!")
            )
        else:
            self.stdout.write(
                self.style.ERROR("\n⚠️  Proyecto con errores que requieren atención")
            )

    def validate_settings(self):
        """Valida la configuración de Django"""
        try:
            # Verificar DEBUG mode
            if settings.DEBUG:
                return {
                    "name": "Settings",
                    "type": "warning",
                    "message": "DEBUG=True (cambiar a False en producción)",
                }

            # Verificar SECRET_KEY
            if "django-insecure" in settings.SECRET_KEY:
                return {
                    "name": "Settings",
                    "type": "error",
                    "message": "SECRET_KEY insegura (usar variable de entorno)",
                }

            # Verificar ALLOWED_HOSTS
            if not settings.ALLOWED_HOSTS:
                return {
                    "name": "Settings",
                    "type": "error",
                    "message": "ALLOWED_HOSTS vacío",
                }

            return {
                "name": "Settings",
                "type": "success",
                "message": "Configuración válida",
            }

        except Exception as e:
            return {"name": "Settings", "type": "error", "message": f"Error: {str(e)}"}

    def validate_urls(self):
        """Valida las URLs del proyecto"""
        try:
            from core.validators import URLValidator

            result = URLValidator.validate_all_urls()

            if result["errors"]:
                error_messages = [e["message"] for e in result["errors"][:3]]
                return {
                    "name": "URLs",
                    "type": "error",
                    "message": f'{len(result["errors"])} errores. Ej: {", ".join(error_messages)}',
                }
            elif result["warnings"]:
                return {
                    "name": "URLs",
                    "type": "warning",
                    "message": f'{len(result["warnings"])} advertencias en URLs',
                }
            else:
                return {
                    "name": "URLs",
                    "type": "success",
                    "message": f'{result["total"]} URLs válidas',
                }

        except Exception as e:
            return {
                "name": "URLs",
                "type": "error",
                "message": f"Error validando URLs: {str(e)}",
            }

    def validate_templates(self):
        """Valida los templates del proyecto"""
        try:
            from core.template_versioning import TemplateVersionControl

            structure_result = TemplateVersionControl.validate_template_structure()

            if structure_result["errors"]:
                error_messages = structure_result["errors"][:3]
                return {
                    "name": "Templates",
                    "type": "error",
                    "message": f'{len(structure_result["errors"])} errores. Ej: {", ".join(error_messages)}',
                }
            elif structure_result["warnings"]:
                return {
                    "name": "Templates",
                    "type": "warning",
                    "message": f'{len(structure_result["warnings"])} advertencias en templates',
                }
            else:
                changes = TemplateVersionControl.check_for_changes()
                if changes["modified"]:
                    return {
                        "name": "Templates",
                        "type": "warning",
                        "message": f'{len(changes["modified"])} templates modificados desde última validación',
                    }
                else:
                    return {
                        "name": "Templates",
                        "type": "success",
                        "message": f'Templates válidos ({len(changes["unchanged"])} sin cambios)',
                    }

        except Exception as e:
            return {
                "name": "Templates",
                "type": "error",
                "message": f"Error validando templates: {str(e)}",
            }

    def validate_models(self):
        """Valida los modelos de la base de datos"""
        try:
            call_command("check")
            return {"name": "Models", "type": "success", "message": "Modelos válidos"}
        except Exception as e:
            return {
                "name": "Models",
                "type": "error",
                "message": f"Error en modelos: {str(e)}",
            }

    def validate_migrations(self):
        """Valida las migraciones"""
        try:
            from django.db import connection
            from django.db.migrations.executor import MigrationExecutor

            executor = MigrationExecutor(connection)
            plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

            if plan:
                return {
                    "name": "Migrations",
                    "type": "warning",
                    "message": f"{len(plan)} migraciones pendientes",
                }
            else:
                return {
                    "name": "Migrations",
                    "type": "success",
                    "message": "Todas las migraciones aplicadas",
                }

        except Exception as e:
            return {
                "name": "Migrations",
                "type": "error",
                "message": f"Error en migraciones: {str(e)}",
            }

    def validate_static_files(self):
        """Valida archivos estáticos"""
        try:
            static_dir = (
                settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None
            )

            if not static_dir or not os.path.exists(static_dir):
                return {
                    "name": "Static Files",
                    "type": "error",
                    "message": "Directorio static no encontrado",
                }

            # Verificar estructura básica
            required_dirs = ["css", "js", "images"]
            missing_dirs = []

            for dir_name in required_dirs:
                dir_path = os.path.join(static_dir, dir_name)
                if not os.path.exists(dir_path):
                    missing_dirs.append(dir_name)

            if missing_dirs:
                return {
                    "name": "Static Files",
                    "type": "warning",
                    "message": f'Directorios faltantes: {", ".join(missing_dirs)}',
                }

            return {
                "name": "Static Files",
                "type": "success",
                "message": "Archivos estáticos válidos",
            }

        except Exception as e:
            return {
                "name": "Static Files",
                "type": "error",
                "message": f"Error validando static files: {str(e)}",
            }
