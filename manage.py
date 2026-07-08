#!/usr/bin/env python
"""
Punto de entrada de línea de comandos para tareas administrativas de Django.
"""
import os
import sys


def main():
    """Ejecuta tareas administrativas."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar Django. ¿Está instalado y activado en el "
            "entorno virtual? Verifique con: 'pip install django'"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
