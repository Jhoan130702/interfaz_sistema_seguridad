import flet as ft
from src.ui import Aplicacion
from src.database import DataBase
from plyer import notification
from src.services import FuncionesEsp

def mostrar_dialogo(page, mensaje, titulo):
    dialogo = ft.AlertDialog(
        title=ft.Text(titulo),
        content=ft.Text(mensaje),
        actions=[
            ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(page, dialogo))
        ],
    )
    dialog = dialogo
    page.overlay.append(dialog)
    dialogo.open = True
    page.update()  # Muestra el diálogo

def cerrar_dialogo(page, dialogo):
    dialogo.open = False
    page.update()  # Actualiza la página

def avisar_admin(page, cedula, password):
    # Verificación de campos vacíos
    if not cedula:
        print("Campo cédula vacío")
        mostrar_dialogo(page, "Por favor ingrese su Usuario para poder ayudarlo", "Alerta")
        return  # Salimos de la función si el campo está vacío 

    db = DataBase.ConexionBaseDatos()
    resultado = db.ejecutar_consulta(f"Select Nombres from usuario where cedula = {cedula}")
    if not resultado:
        mostrar_dialogo(page, f"Usted no esta registrado en el sistema, contacte directamente al administrador", "Notificación")
        return # Salimos de la función si el campo está vacío
    db.ejecutar_actualizacion("insert into historial_alerta values(null, 7, CURRENT_DATE(), CURRENT_TIME())", valores=None)
    mostrar_dialogo(page, f"Avisaste al administrador. ¡Gracias {resultado[0][0]}!", "Notificación")
    valores= resultado[0][0]
    db.ejecutar_actualizacion(f"insert into soporte (id, nombre, fecha, hora, estatus) values(null, '{valores}', CURRENT_DATE(), CURRENT_TIME(), 1)", valores=None)
    slack = FuncionesEsp
    slack.NotificacionesESP.ProblemaInicio()
    
    
def consulta(page):
    cedula = Cedula_field.value
    password = password_field.value
    db = DataBase.ConexionBaseDatos()

    # Verificación de campos vacíos
    if not cedula:
        print("Campo cédula vacío")
        mostrar_dialogo(page, "Por favor ingrese su cédula.", "Alerta")
        return  # Salimos de la función si el campo está vacío

    if not password:
        print("Campo contraseña vacío")
        mostrar_dialogo(page, "Por favor ingrese su contraseña.", "Alerta")
        return  # Salimos de la función si el campo está vacío

    try:
        valores = cedula, password
        Consulta = "CALL Login(%s, %s, @cedulaUsuario);"
        resultados = db.ejecutar_actualizacion(Consulta, valores)

        if resultados == int(cedula):  # Convertimos cédula a entero para comparar
            print("acceso concedido")
            mostrar_dialogo(page, "Acceso Concedido.", "Bienvenido")
            Aplicacion.iniciar_aplicacion(page, cedula)
        else:
            print("acceso denegado")
            mostrar_dialogo(page, "Acceso denegado. Verifica tus credenciales.", "Error")
    except Exception as e:
        print(f"Error en la consulta: {e}")
        mostrar_dialogo(page, "Error al realizar la consulta.", "Error")
    finally:
        db.desconectar()  # Siempre desconecta la base de datos

def iniciar_consulta(page):
    consulta(page)

def main(page: ft.Page, title="Sistema de Seguridad"):
    page.title = title
    page.clean()
    global password_field 
    global Cedula_field  # Referencia al campo de contraseña
    page.window.bgcolor = ft.colors.TRANSPARENT
    page.bgcolor = ft.colors.TRANSPARENT
    # Configuración de la ventana
    page.window.width = 1400
    page.window.height = 900
    page.padding = 0
    page.on_close = lambda e: None 

    Cedula_field = ft.TextField(
        label="Usuario",
        width=350,
        height=80,
        hint_text='Ingrese su Cédula',
        border='underline',
        color='black',
        prefix_icon=ft.icons.PERSON,
        input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=" "),
        max_length=9
    )

    password_field = ft.TextField(
        label="Contraseña", 
        width=350, 
        height= 80,
        password=True, 
        can_reveal_password=True,
        border='underline',
        color='black',
        prefix_icon=ft.icons.LOCK
    )

    body = ft.Container(
        ft.Row([
            ft.Container(
                ft.Column(controls=[ft.Container(ft.Row(
                    [
                        ft.WindowDragArea(ft.Container(ft.Text(
                            'Iniciar Sesión',
                            width=340,
                            size=34,
                            weight='w900',
                            text_align='center',
                        ),), expand=True),
                        ft.IconButton(ft.icons.CLOSE, on_click=lambda _: page.window.close())
                    ]                    
                    ),
                    gradient=ft.LinearGradient(colors=[ft.colors.BLUE_500, ft.colors.GREY_300])
                    ),
                    ft.Container(
                        Cedula_field,
                        padding=ft.padding.only(40, 10, 10, 10)
                    ),
                    ft.Container(
                        ft.Row([
                            password_field
                        ], spacing=0),
                        padding=ft.padding.only(40, 10, 10, 10)
                    ),
                    ft.Container(
                        ft.ElevatedButton(
                            content=ft.Text(
                                'INICIAR',
                                color='white',
                                weight='w500',
                            ),
                            width=350,
                            bgcolor='black',
                            on_click=lambda e: iniciar_consulta(page)  # Llama a iniciar_consulta
                        ),
                        padding=ft.padding.only(40, 10, 10, 10)
                    ),
                    ft.Container(
                        ft.Row([
                            ft.Text('¿No Puede Acceder?'),
                            ft.TextButton('Avisar al Administrador', on_click=lambda e: avisar_admin(page, Cedula_field.value, password_field.value)),
                        ], spacing=5),
                        padding=ft.padding.only(60)
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY),  # Controladores para el contenedor del login
                gradient=ft.LinearGradient(colors=[ft.colors.BLUE_500, ft.colors.GREY_300]),
                width=430,
                height=510,
                border_radius=20
            ),
        ],
        alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        padding=10,
    )

    # Agrega el cuerpo a la página
        
    page.add(body)
    
