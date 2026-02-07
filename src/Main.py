import flet as ft
from src.ui import Login
from src.services import FuncionesEsp

FuncionesEsp.iniciar_hilos()

def main(page: ft.Page, title="Sistema de Seguridad"):
    page.title = title
    # Configuración de la ventana
    page.window.width = 1100
    page.window.height = 850
    # page.padding = 0
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.window.bgcolor = ft.colors.TRANSPARENT
    page.window.title_bar_buttons_hidden = True
    page.window.frameless = True
    page.window.title_bar_hidden = True
    page.bgcolor = ft.colors.TRANSPARENT
    page.on_close = lambda e: None 
    
    Login.main(page)
    
ft.app(main)

