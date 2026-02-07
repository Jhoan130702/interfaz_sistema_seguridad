import flet as ft
import DataBase
import FuncionesEsp
import Login
import NotificacionesBarra
from Perfil import UserProfile

conexion = DataBase.ConexionBaseDatos()
edit_fields = ft.Column(visible=False)  # Campos de edición inicialmente ocultos
def permisos(cedula):
    global user_permissions
    global current_user
    
    user_permissions = {
        "Admin": ["ver", "agregar", "editar", "eliminar"],
        "Secretaria/o": ["ver", "agregar", "editar"],
        "Seguridad": ["ver"],
        "visitante": ["ver"],
    }
    Consulta = f"SELECT permisos.Nombre_C FROM permisos inner join usuario ON permisos.ID = usuario.Cargo WHERE usuario.Cedula = {cedula}"
    permiso_usuario = conexion.ejecutar_consulta(Consulta)
    print(permiso_usuario[0][0])
    current_user = permiso_usuario[0][0]  # simular diferentes usuarios (admin, editor, viewer)

def toggle_menu(page, menu_container):
    menu_container.visible = not menu_container.visible
    page.update()

def main(page: ft.Page, title="Sistema de Seguridad"):
    page.clean()
    page.window.bgcolor = ft.colors.WHITE10
    page.bgcolor = ft.colors.WHITE10
    page.on_close = lambda e: None 
    page.add(
        ft.Container(
            ft.Row(
                [ft.WindowDragArea(
                    ft.Container(
                        ft.Text(
                            'SISTEMA',
                            width=340,
                            size=20,
                            weight='w900',
                            text_align='center',
                        )
                    ), 
                    expand=True),
                    ft.IconButton(
                        ft.icons.CLOSE, on_click=lambda _: page.window.close()
                    )
                ]                    
            ), 
            bgcolor=ft.colors.WHITE,
        )
    )
    page.title = title
    Registro_Huellas = FuncionesEsp.RegistroHuellas(page)
    title_text = ft.Text(value="Usuarios", size=30, weight=ft.FontWeight.BOLD)
    if "agregar" in user_permissions[current_user]:
        title_add = ft.IconButton(ft.icons.ADD, tooltip="Agregar Registro", on_click=lambda e: mostrar_formulario()) 
    else:
        title_add = ft.IconButton(ft.icons.ADD, tooltip="Permisos Requeridos")
    title_menu = ft.IconButton(ft.icons.MENU, tooltip="Menú", on_click=lambda e: toggle_menu(page, menu_container))
    
    title_bar = ft.Container(
        content=ft.Row(
            controls=[
                title_menu,
                title_text,
                title_add,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        bgcolor=ft.colors.BLUE_500,
        height=60,
        padding=ft.padding.all(10),
        margin=ft.margin.only(left= 5, bottom=10, right= 5),
        shadow=ft.BoxShadow(
            color=ft.colors.BLACK45,
            blur_radius=10,
            spread_radius=5,
            offset=ft.Offset(5, 5)
        ),
        border_radius=ft.BorderRadius(5, 5, 5, 5)
    )

    content = ft.Column(scroll=True, expand=True, alignment=ft.MainAxisAlignment.START)
    form_container = ft.Column(visible=False)  # Definición del contenedor del formulario

    titles = ["Usuarios", "Huella", "Ingresos a Sistema", "Ingresos a Areas", "Registro de alertas", "Registro de Usos"]
    queries = [
        "usuario",
        "huella",
        "ingresos_sistema",
        "ingresos_zona",
        "historial_alerta",
        "usos_sistema"
    ]
    def mostrar_formulario():
        dialog_content = ft.Column()
        form_fields = get_form_fields(current_index)  # Obtener campos según el índice actual
        if current_index > 1:
            dialog_content = ft.Text("No se pueden agregar registros en esta sección, Por favor no insista")
            dialog = ft.AlertDialog(
                title=ft.Text("Alerta"),
                content=dialog_content,
                actions=[]
            )
            page.open(dialog)
            page.update()
            return
        for field in form_fields:
            dialog_content.controls.append(field)
        if current_index == 1:
            dialog = ft.AlertDialog(
                title=ft.Text("Agregar Registro"),
                content=dialog_content,
                actions=[
                    ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo_registro_huellas(dialog))
                ],
            )
        else:
            dialog = ft.AlertDialog(
                title=ft.Text("Agregar Registro"),
                content=dialog_content,
                actions=[
                    ft.TextButton("Guardar", on_click=lambda e: guardar_registro(dialog, form_fields)),
                    ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog)),
                ],
            )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def guardar_registro(dialog, form_fields):
        values = [field.value for field in form_fields]
        if not values[0]:
            print("Campo cédula vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Campo cedula vacio")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío

        if not values[1]:
            print("Campo Nombres vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Campo Nombres vacio")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        if not values[2]:
            print("Campo Apellidos vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Campo Apellidos vacio")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        if not values[3]:
            print("Campo Correo vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Campo Correo vacio")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        if not values[4]:
            print("Campo Cargo vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Por favor Seleccione un Cargo")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        if not values[5]:
            print("Campo Contraseña vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Campo Contraseña vacio")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        if not values[6]:
            print("Campo Confirmacion de contraseña vacío")
            bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("¡Alerta!", size=20, weight=ft.FontWeight.BOLD),ft.Text("Por favor confirme la contraseña")])))
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return  # Salimos de la función si el campo está vacío
        
        print(f"Guardando registro: {values}")
        
        if values[5] == values[6]:
            if values[4]== "Admin":
                values[4] = 2
            elif values[4]== "Secretaria/o":
                values[4] = 3
            elif values[4]== "Seguridad":
                values[4] = 5
            elif values[4]== "Pasante":
                values[4] = 7
            elif values[4]== "Visitante":
                values[4] = 4
            else:
                values[4] = 8
            valores = values[0], values[1], values[2], values[4], values[3], values[5]
            consulta = "CALL CreateUsuario(%s, %s, %s, %s, %s, %s, 1, @resultado)"
            retorno = conexion.ejecutar_actualizacion(consulta, valores)
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text("Mensaje"),
                            ft.Text(retorno)
                        ]
                    )
                )
            )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            cerrar_dialogo(dialog)
            update_content(current_index)  # Actualizar el contenido de la tabla
        else:
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text("Error"),
                            ft.Text("No se pudo registrar el Usuario, las contraseñas no coinciden")
                        ]
                    )
                )
            )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return
    def cerrar_dialogo_registro_huellas(dialog):
        page.close(dialog)
        Registro_Huellas.continuar_registro = False
        page.update()
    def cerrar_dialogo(dialog):
        page.close(dialog)
        update_content(current_index)
    def crear_tabla(data, columnas):
        rows = []
        for row in data:
            row_id = row[0]  # Guarda el ID actual
            cells = [ft.DataCell(ft.Text(str(cell))) for cell in row]
            actions = []
            if current_index <= 1:
                if "editar" in user_permissions[current_user]:
                    actions.append(ft.IconButton(ft.icons.EDIT, tooltip="Editar", on_click=lambda e, id=row_id, r=row: editar_registro(id, r, columnas, menu_container)))
                if "eliminar" in user_permissions[current_user]:
                    actions.append(ft.IconButton(ft.icons.DELETE, tooltip="Eliminar", on_click=lambda e, id=row_id: confirmar_eliminacion(id, menu_container)))
                cells.append(ft.DataCell(ft.Row(actions)))
            rows.append(ft.DataRow(cells=cells))
        if current_index > 1: 
            columns = [ft.DataColumn(ft.Text(col, style=ft.TextStyle(color=ft.colors.BLACK))) for col in columnas]
        else:    
            columns = [ft.DataColumn(ft.Text(col, style=ft.TextStyle(color=ft.colors.BLACK))) for col in columnas] + [ft.DataColumn(ft.Text("Acciones", style=ft.TextStyle(color=ft.colors.BLACK)))]

        table = ft.DataTable(column_spacing=20, columns=columns, rows=rows, bgcolor="white", border=ft.border.all(2, "blue"), heading_row_color=ft.colors.BLACK12, heading_row_height=50, )
        
        return table
    def obtener_datos_y_columnas(query):
        if query == "usuario":
            Consulta = "SELECT usuario.id, usuario.cedula, usuario.nombres, usuario.apellidos, REPEAT('*', 4) AS contrasena, usuario.correo, permisos.Nombre_C AS Cargo FROM usuario INNER JOIN permisos ON usuario.cargo = permisos.ID where usuario.Estado > 0 ORDER BY usuario.id ASC limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID','Cedula', 'Nombre', 'Apellido', 'Contraseña', 'Correo',  'Cargo']
        elif query == "huella":
            Consulta = "SELECT huella.ID, usuario.Nombres, huella.Huella_1_P_D, huella.Huella_2_P_I, huella.Huella_3_I_D, huella.Huella_4_I_I FROM huella INNER JOIN usuario ON huella.ID_Usuarios = usuario.ID limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID', 'Usuario', 'Huella 1', 'Huella 2', 'Huella 3', 'Huella 4']
        elif query == "ingresos_sistema":
            Consulta = f"SELECT ingresos_sistema.id_ingreso, usuario.Nombres, ingresos_sistema.fecha, ingresos_sistema.hora FROM ingresos_sistema inner join usuario on ingresos_sistema.id_usuario2 = usuario.ID order by fecha Desc, hora Desc limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID', 'Usuario', 'Fecha', 'Hora']
        elif query == "ingresos_zona":
            Consulta = "SELECT iz.Id_ingreso, usuario.Nombres, iz.Puerta, iz.fecha, iz.hora FROM ingresos_zona AS iz inner join usuario on iz.Id_usuario = usuario.ID order by fecha Desc, hora Desc limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID', 'Usuario', 'Zona', 'Fecha', 'Hora']
        elif query == "historial_alerta":
            Consulta = "SELECT historial_alerta.Id, alerta.nombre, historial_alerta.Fecha_Alerta, historial_alerta.hora_alerta FROM historial_alerta INNER JOIN alerta ON historial_alerta.Detalles = alerta.id_alerta ORDER BY historial_alerta.Fecha_Alerta Desc, historial_alerta.hora_alerta DESC limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID', 'Detalles', 'Fecha', 'Hora']
        elif query == "usos_sistema":
            Consulta = "SELECT usos_sistema.id_historial, usuario.Nombres, usos_sistema.Tabla_Editada, usos_sistema.Accion, usos_sistema.Fecha, usos_sistema.hora FROM usos_sistema INNER JOIN ingresos_sistema ON usos_sistema.Id_ingreso = ingresos_sistema.id_ingreso INNER JOIN usuario ON ingresos_sistema.id_usuario2 = usuario.ID ORDER BY usos_sistema.Fecha Desc, usos_sistema.Hora Desc limit 50"
            resultados = conexion.ejecutar_consulta(Consulta)
            return resultados, ['ID', 'Nombre', 'Tabla Editada', 'Cambio', 'Fecha', 'Hora']
        return [], []
    def update_content(selected_index):
        global current_index
        
        current_index = selected_index  # Actualizar el índice actual
        content.controls.clear()
        edit_fields.controls.clear()  # Limpiar campos de edición
        form_container.controls.clear()  # Limpiar campos del formulario

        query = queries[selected_index]
        data, columnas = obtener_datos_y_columnas(query)
        title_text.value = titles[selected_index]  # Actualizar el título en el banner

        # Obtener y agregar campos del formulario según el índice
        form_fields = get_form_fields(selected_index)  # Cambiar aquí para usar el índice
        form_container.controls.extend(form_fields)
        if selected_index >=2 and selected_index <=4: 
            margen = 200 
        else: 
            margen = 50 
        # Agregar contenedor con desplazamiento horizontal
        content.controls.append(
            ft.Container(
                content=ft.Row(
                    controls=[crear_tabla(data, columnas)],
                    scroll=True  # Permitir desplazamiento horizontal
                ),
                margin=ft.margin.only(top=0, left= margen, bottom=20),  # Sin margen superior para acercar al banner
                border_radius=ft.BorderRadius(5, 5, 5, 5)
            )
        )
        page.update()
    def get_form_fields(selected_index):
        if selected_index == 0:  # Usuarios
            return [
                ft.TextField(label="Cedula", width=300, height=65, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),max_length=9),
                ft.TextField(label="Nombre", width=300, height=65, input_filter=ft.TextOnlyInputFilter(),max_length=30),
                ft.TextField(label="Apellido", width=300, height=65,input_filter=ft.TextOnlyInputFilter(),max_length=30),
                ft.TextField(label="Correo", width=300, height=65, max_length=30),
                ft.Dropdown(label="Cargo", width=300, height=65, dense=True,options=[
                                            ft.dropdown.Option("Nulo"),
                                            ft.dropdown.Option("Admin"),
                                            ft.dropdown.Option("Secretaria/o"),
                                            ft.dropdown.Option("Seguridad"),
                                            ft.dropdown.Option("Pasante"),
                                            ft.dropdown.Option("Visitante")
                                        ],
                ),
                ft.TextField(label="Contraseña", width=300, height=65, password=True, can_reveal_password=True),
                ft.TextField(label="Confirmar Contraseña", height=65, width=300, password=True, can_reveal_password=True)
            ]
        elif selected_index == 1:  # Huella
            Nombre = ft.TextField(label="Nombre",input_filter=ft.TextOnlyInputFilter(), width=300)
            btn = ft.TextButton("Comprobar", on_click=lambda e: Registro_Huellas.registrar_huellas(Nombre.value, page))
            return [Nombre, btn] 
        
        elif selected_index == 2:  # Ingresos a Sistema
            return [
                ft.TextField(label="ID", width=300),
                ft.TextField(label="Usuario", width=300),
                ft.TextField(label="Fecha", width=300),
                ft.TextField(label="Hora", width=300)
            ]
        elif selected_index == 3:  # Ingresos a Áreas
            return [
                ft.TextField(label="ID", width=300),
                ft.TextField(label="Usuario", width=300),
                ft.TextField(label="Zona", width=300),
                ft.TextField(label="Fecha", width=300),
                ft.TextField(label="Hora", width=300)
            ]
        elif selected_index == 4:  # Historial de Alertas
            return [
                ft.TextField(label="ID", width=300),
                ft.TextField(label="Detalles", width=300),
                ft.TextField(label="Fecha", width=300),
                ft.TextField(label="Hora", width=300)
            ]
        elif selected_index == 5:  # Registro de Usos
            return [
                ft.TextField(label="ID", width=300),
                ft.TextField(label="Ingreso", width=300),
                ft.TextField(label="Tabla Editada", width=300),
                ft.TextField(label="Acción", width=300),
                ft.TextField(label="Fecha", width=300),
                ft.TextField(label="Hora", width=300)
            ]
        return []
    def editar_registro(id, row, columnas, menu_container):
        Registro_Huellas = FuncionesEsp.RegistroHuellas(page)
        #Crear contenido para el dialog
        dialog_content = ft.Column()
        text_fields = []  # Lista para almacenar los campos de texto
        if current_index == 1:
            for i, value in enumerate(row[1:], start=1):  # Ignorar el primer campo (ID)
                text_field = ft.TextField(label=columnas[i], value=str(value), width=300)
                text_fields.append(text_field)
            
            def editar_huellas(id):
                values = id
                Nombre = text_fields[0].value
                Huellas = text_fields[1].value, text_fields[2].value, text_fields[3].value, text_fields[4].value
                bottom_sheet = ft.BottomSheet(
                    content=ft.Container(
                        padding=50, 
                        content=ft.Column(
                            tight=True, 
                            controls=[
                                ft.Text("Por favor espere un momento"),
                                ft.Text("Preparando los dispositivos y borrando los datos")
                            ]
                        )
                    )
                )
                page.overlay.append(bottom_sheet)
                bottom_sheet.open = True
                page.update()
                consulta = f"Delete from huella where id = {values}" 
                # Registro_Huellas.eliminar_huellas(Huellas)
                conexion.ejecutar_actualizacion(consulta, valores=None)
                # Registro_Huellas.registrar_huellas(Nombre, page)
                
            
            dialog_content.controls.append(ft.Row(controls=[
                ft.Text("¿Seguro quiere cambiar las huellas?"),
                ft.ElevatedButton("Cambiar", on_click=lambda e: editar_huellas(id))
            ]))

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar Registro"),
                content=dialog_content,
                actions=[
                    ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo_registro_huellas(dialog)),
                ],
            )
        else:
            for i, value in enumerate(row[1:], start=1):  # Ignorar el primer campo (ID)
                text_field = ft.TextField(label=columnas[i], value=str(value), width=300)
                dialog_content.controls.append(text_field)
                text_fields.append(text_field)  # Agregar a la lista

            dialog_content.controls.append(ft.Row(controls=[
                ft.ElevatedButton("Guardar Cambios", on_click=lambda e: guardar_cambios(id, text_fields, dialog)),
                ft.ElevatedButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog))
            ]))

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Editar Registro"),
                content=dialog_content
            )
        
        page.open(dialog)
        page.update()
    def guardar_cambios(id, text_fields, dialog):
        # Obtener los valores de los campos de texto
        valores = [text_field.value for text_field in text_fields]

        # Aquí puedes usar current_index para manejar los valores
        if current_index == 0:
            if valores[5]== "Admin":
                valores[5] = 2
            elif valores[5]== "Secretaria/o":
                valores[5] = 3
            elif valores[5]== "Seguridad":
                valores[5] = 6
            elif valores[5]== "Pasantes":
                valores[5] = 7
            elif valores[5]== "Visita":
                valores[5] = 8
            elif valores[5] == "Nulo":
                valores[5] = 1
            
            # Verifica si la contraseña actual es un marcador de posición
            if valores[3] == "****":
                # Actualiza los datos sin cambiar la contraseña
                valores[0] = int(valores[0])
                values = valores[0], valores[1], valores[2], valores[5], valores[4], id
                consulta = "Update usuario set Cedula = %s, Nombres = %s, Apellidos = %s, Cargo = %s, Correo = %s where ID = %s"
                conexion.ejecutar_actualizacion(consulta, values)
                bottom_sheet = ft.BottomSheet(
                    content=ft.Container(
                        padding=50, 
                        content=ft.Column(
                            tight=True, 
                            controls=[
                                ft.Text("Exito"),
                                ft.Text("Datos Actualizados Correctamente")
                            ]
                        )
                    )
                )
                page.overlay.append(bottom_sheet)
                bottom_sheet.open = True
                page.update()
                cerrar_dialogo(dialog)
                
            else:
                # Si la contraseña actual no es un marcador de posición, solicita confirmación
                confirmar = ft.TextField(label="Confirmar Contraseña", height=65, width=300, password=True, can_reveal_password=True, max_length=8)

                def llamada(confirmar_value):
                    if confirmar_value == valores[3]:
                        # Solo se ejecuta si las contraseñas coinciden
                        valores[0] = int(valores[0])
                        values = valores[0], valores[1], valores[2], valores[3], valores[5], valores[4], id
                        consulta = "CALL ActualizarUsuario (%s, %s, %s, %s, %s, %s, %s)"
                        conexion.ejecutar_actualizacion(consulta, values)
                        # Mostrar mensaje de éxito
                        print("se pudo")
                        bottom_sheet_success = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("Éxito"), ft.Text("Los datos han sido actualizados correctamente.")])))
                        page.overlay.append(bottom_sheet_success)
                        bottom_sheet_success.open = True
                        page.update()
                    else:
                        # Mostrar mensaje de error si las contraseñas no coinciden
                        bottom_sheet_error = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[ft.Text("Error"), ft.Text("No se pudo registrar el Usuario, las contraseñas no coinciden")])))
                        page.overlay.append(bottom_sheet_error)
                        bottom_sheet_error.open = True
                        page.update()

                btn = ft.ElevatedButton("Guardar Cambios", on_click=lambda e: llamada(confirmar.value))
                bottom_sheet = ft.BottomSheet(content=ft.Container(padding=50, content=ft.Column(tight=True, controls=[confirmar, btn])))
                page.overlay.append(bottom_sheet)
                bottom_sheet.open = True
                page.update()
        
            print(f"Valores para index 0: {valores}")
            page.update()
        else:
            bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Error"),
                                                ft.Text("No se pudo Actualizar la información")
                                            ]
                                        )
                                    )
                                )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            page.update()
            return
        print(f"Guardar cambios para el registro con ID: {id} con valores: {valores}")
        page.update()
    def confirmar_eliminacion(id, menu_container):
        if menu_container.visible:
            menu_container.visible = not menu_container.visible
        if form_container.visible: 
            form_container.visible = not form_container.visible  # Cerrar el formulario si está abierto
        if edit_fields.visible:
            edit_fields.visible = False  # Ocultar campos de edición 
        dialog = ft.AlertDialog(
            title=ft.Text("Advertencia"),
            content=ft.Text(f"¿Está seguro de que desea eliminar el registro con ID: {id}?"),
            actions=[
                ft.TextButton("Eliminar", on_click=lambda e: eliminar_registro(id, dialog)),
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_dialogo(dialog))
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()
    def eliminar_registro(id, dialog):
        values = id
        if current_index == 0:
            consulta = f"Update usuario set Estado = 0 where id = {id}"
            conexion.ejecutar_actualizacion(consulta, valores = None)
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text("Exito"),
                            ft.Text("Se Eliminó el registro")
                        ]
                    )
                )
            )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            cerrar_dialogo(dialog)
            page.update()
            update_content(current_index)
            return
        elif current_index == 1:
            
            try: 
                ids = conexion.ejecutar_consulta(f"SELECT Huella_1_P_D, Huella_2_P_I, Huella_3_I_D, Huella_4_I_I FROM huella WHERE id = {values}")
                huellas = ids[0], ids[1], ids[2], ids[3]
                Registro_Huellas.eliminar_huellas(huellas)
                consulta = f"Delete From huella where id = {id}"
                conexion.ejecutar_actualizacion(consulta, valores=None)
                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Exito"),
                                                ft.Text("Se Eliminaron las huellas")
                                            ]
                                        )
                                    )
                                )
                page.overlay.append(bottom_sheet)
                bottom_sheet.open = True
                cerrar_dialogo(dialog)
                page.update()
                update_content(current_index)
                return
            except:
                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Error"),
                                                ft.Text("No se pudo Conectar con el Esp, ni borrar las huellas")
                                            ]
                                        )
                                    )
                                )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            cerrar_dialogo(dialog)
            page.update()
            return
        else:
            values = None
            consulta ="insert into historial_alerta values(null, 8, CURRENT_DATE(), CURRENT_TIME())"
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text("Error"),
                            ft.Text("No se pueden borrar registros de esta sección")
                        ]
                    )
                )
            )
            page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            cerrar_dialogo(dialog)
            page.update()
            update_content(current_index)
            return       
    def cerrar_session():
        print("cerrar Sesion")
        Login.main(page)
    menu_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[
                    ft.IconButton(ft.icons.PERSON, on_click=lambda e: update_content(0)),
                    ft.TextButton("Usuarios", on_click=lambda e: update_content(0))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.FINGERPRINT, on_click=lambda e: update_content(1)),
                    ft.TextButton("Huella", on_click=lambda e: update_content(1))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.LOGIN, on_click=lambda e: update_content(2)),
                    ft.TextButton("Ingresos a Sistema", on_click=lambda e: update_content(2))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.LOCATION_ON, on_click=lambda e: update_content(3)),
                    ft.TextButton("Ingresos a Areas", on_click=lambda e: update_content(3))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.WARNING, on_click=lambda e: update_content(4)),
                    ft.TextButton("Registro de Alertas", on_click=lambda e: update_content(4))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.NOTE_ALT, on_click=lambda e: update_content(5)),
                    ft.TextButton("Registro de Usos", on_click=lambda e: update_content(5))
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.FLASHLIGHT_ON, on_click=lambda e: FuncionesEsp.iniciar_pir()),
                    ft.TextButton("Activar Pir", on_click=lambda e: FuncionesEsp.iniciar_pir())
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.DOOR_SLIDING, on_click=lambda e: FuncionesEsp.NotificacionesESP.AbrirPuerta()),
                    ft.TextButton("Abrir Puerta", on_click=lambda e: FuncionesEsp.NotificacionesESP.AbrirPuerta())
                ]),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.EDIT, on_click=lambda e: info.open_file_picker()),
                    ft.TextButton("Editar foto de Perfil", on_click=lambda e: info.open_file_picker())
                ]),
                ft.Row(expand=True),
                ft.Row(controls=[
                    ft.IconButton(ft.icons.LOGOUT, on_click=lambda e: cerrar_session()),
                    ft.TextButton("Cerrar Sesión", on_click=lambda e: cerrar_session())
                ], alignment=ft.MainAxisAlignment.START)
            ],
            width=220,
        ),
        bgcolor=ft.colors.WHITE,
        padding=ft.padding.all(10),
        shadow=ft.BoxShadow(
            color=ft.colors.BLACK45,
            blur_radius=20,
            spread_radius=5,
            offset=ft.Offset(10, 10)
        ),
        border_radius=ft.BorderRadius(5, 5, 5, 5),
        visible=True,
        height=630,
        margin=ft.margin.only(top=-20)
    )
    main_container = ft.Stack(
        controls=[
            ft.Column(controls=[content, form_container, edit_fields], expand=True),  # Contenido principal
            menu_container, # Menú superpuesto
            ft.Column(controls=[info.profile_container], expand=True, alignment=ft.alignment.center_right),
        ],
        expand=True,
    )

    page.add(title_bar, main_container)
    update_content(0)

    # Ajustar la visibilidad del menú según el tamaño de la pantalla
    def on_resize(e):
        if page.window.width < 900:
            menu_container.width = 60
            
            for row in menu_container.content.controls:
                if len(row.controls) > 1:  # Verificar que haya al menos dos controles
                    row.controls[1].visible = False  # Ocultar el texto del botón
                    row.controls[0].tooltip = row.controls[1].text  # Asignar tooltip al icono
        else:
            menu_container.width = 250
            for row in menu_container.content.controls:
                if len(row.controls) > 1:  # Verificar que haya al menos dos controles
                    row.controls[1].visible = True  # Mostrar el texto del botón

    page.on_resized = on_resize
    page.update()

def iniciar_aplicacion(page, cedula):
    global usuario 
    global info
    permisos(cedula)
    notificar = conexion.ejecutar_consulta(f"Select Cargo, Nombres from usuario where Cedula = {cedula}")
    slack = FuncionesEsp
    usuario = notificar[0][1]
    info = UserProfile(page, cedula)
    page.update()
    def mostrar_dialogo(page, mensaje, titulo):
        dialog = ft.AlertDialog(
            modal = True,
            title=ft.Text(titulo),
            content=ft.Text(mensaje),
            actions=[
                ft.TextButton("Cerrar", on_click=lambda e: cerrar_dialogo(page, dialog))
            ],
        )
        slack.NotificacionesESP.acceso()
        page.overlay.append(dialog)
        dialog.open = True
        page.update()  # Muestra el diálogo
        if notificar[0][0] == 2:
            NotificacionesBarra.iniciar()
        
        
    def cerrar_dialogo(page, dialogo):
        page.close(dialogo)
        page.update()  # Actualiza la página
                
    main(page)
    mostrar_dialogo(page, "Acceso Concedido.", f"Bienvenido: {usuario}")
    