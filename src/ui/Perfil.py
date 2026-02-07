import flet as ft
from datetime import datetime, timedelta
from src.database import DataBase
import shutil
import os
import threading
import time
from src.services.Reportes_PDF import ReportePDF  # Asegúrate de importar tu clase ReportePDF

class UserProfile:
    def __init__(self, page: ft.Page, cedula: int):
        self.page = page
        self.cedula = cedula
        self.time_label = ft.Text("", size=16)
        self.conexion = DataBase.ConexionBaseDatos()
        
        # Crear el contenedor del perfil
        self.profile_container = self.create_profile_container()
        
        # Iniciar el hilo para actualizar la hora
        threading.Thread(target=self.update_time, daemon=True).start()

        # Cargar datos del usuario
        self.load_user_data()

        # Inicializar el FilePicker
        self.file_picker = ft.FilePicker(on_result=self.update_profile_picture)
        self.page.overlay.append(self.file_picker)  # Agregar solo una vez

    def create_profile_container(self):
        # Contenedor para el perfil
        profile_content = ft.Column(
            spacing=10,
        )

        profile_container = ft.Container(
            content=profile_content,
            padding=20,
            border_radius=ft.border_radius.all(10),
            bgcolor=ft.colors.BLUE_50,
            height=600,
            width=350,
            margin=ft.margin.only(left=990, bottom=10, right=5),
            shadow=ft.BoxShadow(
                color=ft.colors.BLACK45,
                blur_radius=10,
                spread_radius=5,
                offset=ft.Offset(5, 5)
            )
        )

        return profile_container

    def load_user_data(self):
        global nombre, cargo
        # Obtener datos del usuario
        datos_usuario = self.conexion.ejecutar_consulta(
            """
            SELECT usuario.ID, usuario.Nombres, usuario.Apellidos, permisos.Nombre_C 
            FROM usuario 
            LEFT JOIN permisos ON usuario.Cargo = permisos.ID 
            WHERE cedula = %s
            """, 
            (self.cedula,)
        )

        if datos_usuario:
            self.id, nombre, apellidos, cargo = datos_usuario[0]
            self.url_foto = self.get_profile_picture_url()  # Obtener URL de la foto
            self.setup_profile_view(nombre, apellidos, cargo)
        else:
            self.setup_profile_view("No encontrado", "No encontrado", "No disponible")
            self.url_foto = f"Perfiles/150.png"  # Foto por defecto

    def get_profile_picture_url(self):
        foto = self.conexion.ejecutar_consulta(
            "SELECT url FROM fotos WHERE id_usuario3 = %s", 
            (self.id,)
        )
        if not foto:
            return f"assets/profiles/150.png"  # URL por defecto si no hay foto
        else:
            return foto[0][0]

    def setup_profile_view(self, nombre, apellidos, cargo):
        # Limpiar el contenedor antes de agregar nuevos controles
        self.profile_container.content.controls.clear()

        # Configurar la vista del perfil
        self.profile_picture = ft.Image(
            src=self.url_foto,
            width=150,
            height=150,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(75),
        )
        
        self.name_label = ft.Text(f"Nombre: {nombre} {apellidos}", size=20)
        self.position_label = ft.Text(f"Cargo: {cargo}", size=16)
        self.connection_label = ft.Text("Conexión Activa", size=16)

        # Agregar los elementos al contenedor
        self.profile_container.content.controls.append(self.profile_picture)
        self.profile_container.content.controls.append(self.name_label)
        self.profile_container.content.controls.append(self.position_label)
        self.profile_container.content.controls.append(self.time_label)
        self.profile_container.content.controls.append(self.connection_label)

        # Agregar formulario de reporte
        self.add_report_form()

        self.page.add(self.profile_container)  # Agregar el contenedor a la página

    def add_report_form(self):
        # Campos del formulario
        self.periodo_dropdown = ft.Dropdown(
            label="Selecciona el periodo",
            options=[
                ft.dropdown.Option("todos"),
                ft.dropdown.Option("ultimo_mes"),
                ft.dropdown.Option("ultimos_3_meses"),
                ft.dropdown.Option("ultimo_año"),
            ],
            width=300
        )

        # Botón para generar el reporte
        self.generar_button = ft.ElevatedButton(
            text="Generar Reporte",
            on_click=self.generar_reporte
        )

        # Agregar formulario al contenedor de perfil
        report_form = ft.Column(
            controls=[
                self.periodo_dropdown,
                self.generar_button
            ],
            spacing=10
        )

        self.profile_container.content.controls.append(report_form)

    def generar_reporte(self, e):
        cedula = None
        periodo = self.periodo_dropdown.value

        if not periodo:
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text(f"Selecciona un Periodo {nombre}...")
                        ]
                    )
                )
            )
            self.page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            self.page.update()
        else:
            # Crear el reporte PDF
            reporte = ReportePDF(f"Reporte_{periodo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf", nombre, cargo )
            reporte.generar_reporte(cedula=cedula, periodo=periodo)

            # Mensaje de éxito
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text(f"Reporte Generado con Exito {nombre}!")
                        ]
                    )
                )
            )
            self.page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            self.page.update()

    def open_file_picker(self):
        # Abre el FilePicker para seleccionar un archivo
        self.file_picker.pick_files(allow_multiple=False)

    def update_profile_picture(self, e):
        if e.files and len(e.files) > 0:
            new_url = e.files[0].path  # Obtener la ruta del archivo seleccionado

            # Obtener la ruta de la foto anterior
            foto_anterior = self.get_profile_picture_url()

            # Registrar la nueva foto en la base de datos primero
            ruta_absoluta = os.path.abspath(f"assets/profiles/{self.cedula}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            if self.guardar_en_base_datos(ruta_absoluta):
                # Eliminar la foto anterior si no es la foto por defecto

                # Ahora guardar la nueva foto en el sistema
                self.guardar_foto(new_url, ruta_absoluta)
                
                if foto_anterior != f"assets/profiles/150.png":
                    self.eliminar_foto(foto_anterior)

                # Volver a cargar los datos del usuario para refrescar la vista
                self.load_user_data()
                self.page.update()
            else:
                print("Error al guardar en la base de datos.")
        else:
            print("No se seleccionó ningún archivo.")

    def update_time(self):
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.time_label.value = f"Hora actual: {current_time}"
            self.page.update()
            time.sleep(1)  # Esperar 1 segundo

    def guardar_foto(self, ruta_foto_origen, ruta_foto_destino):
        os.makedirs(os.path.dirname(ruta_foto_destino), exist_ok=True)
        shutil.copy2(ruta_foto_origen, ruta_foto_destino)

    def guardar_en_base_datos(self, ruta_absoluta):
        # Eliminar fotos anteriores del usuario
        consulta = "DELETE FROM fotos WHERE id_usuario3 = %s"
        self.conexion.ejecutar_actualizacion(consulta, (self.id,))

        # Insertar nueva foto
        consulta = "INSERT INTO fotos (id_foto, id_usuario3, url, fecha) VALUES (NULL, %s, %s, CURRENT_DATE())"
        valores = (self.id, ruta_absoluta)  # Aquí se guarda la ruta absoluta
        self.conexion.ejecutar_actualizacion(consulta, valores)
        return True  # Asegúrate de que esto se ejecute correctamente

    def eliminar_foto(self, ruta_foto):
        try:
            if os.path.exists(ruta_foto):
                os.remove(ruta_foto)
                print(f"Foto eliminada: {ruta_foto}")
            else:
                print(f"La foto no existe: {ruta_foto}")
        except Exception as e:
            print(f"Error al eliminar la foto: {e}")
