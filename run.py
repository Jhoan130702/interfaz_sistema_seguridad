"""
Punto de entrada principal del Sistema de Seguridad
Este archivo debe ejecutarse desde la raíz del proyecto
"""
import sys
import os

# Agregar el directorio raíz al path para que Python encuentre el paquete src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar el main
from src.Main import main
import flet as ft

if __name__ == "__main__":
    ft.app(main)
