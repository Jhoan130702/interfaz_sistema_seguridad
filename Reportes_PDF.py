import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import DataBase
from datetime import datetime, timedelta

class ReportePDF:
    def __init__(self, filename, generador, cargo):
        self.filename = filename
        self.conexion = DataBase.ConexionBaseDatos()
        self.generador = generador
        self.cargo = cargo

    def generar_reporte(self, cedula, periodo):
        # Determinar la ruta de guardado
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", self.filename)
        documents_path = os.path.join(os.path.expanduser("~"), "Documents", self.filename)
        self.filename = desktop_path if os.path.exists(desktop_path) else documents_path

        document = SimpleDocTemplate(self.filename, pagesize=landscape(letter))
        content = []

        # Definir las fechas para los filtros
        fecha_hasta = datetime.now()
        if periodo == 'ultimo_mes':
            fecha_desde = fecha_hasta - timedelta(days=30)
        elif periodo == 'ultimos_3_meses':
            fecha_desde = fecha_hasta - timedelta(days=90)
        elif periodo == 'ultimo_año':
            fecha_desde = fecha_hasta - timedelta(days=365)
        else:  # 'todos'
            fecha_desde = datetime(2000, 1, 1)  # Fecha muy antigua para incluir todo

        # Consultas a realizar
        consultas = [
            f"""
            SELECT usuario.id, usuario.cedula, usuario.nombres, usuario.apellidos, 
            permisos.Nombre_C AS Cargo, usuario.correo, usuario.Estado 
            FROM usuario 
            INNER JOIN permisos ON usuario.cargo = permisos.ID 
            {"WHERE usuario.cedula = %s" if cedula else ""}
            ORDER BY usuario.id ASC 
            """,
            f"""
            SELECT huella.ID, usuario.Nombres, huella.Huella_1_P_D, huella.Huella_2_P_I, 
            huella.Huella_3_I_D, huella.Huella_4_I_I 
            FROM huella 
            INNER JOIN usuario ON huella.ID_Usuarios = usuario.ID
            """,
            f"""
            SELECT ingresos_sistema.id_ingreso, usuario.Nombres, ingresos_sistema.fecha, 
            ingresos_sistema.hora 
            FROM ingresos_sistema 
            INNER JOIN usuario ON ingresos_sistema.id_usuario2 = usuario.ID 
            {"WHERE ingresos_sistema.fecha >= %s" if periodo != 'todos' else ""}
            {"AND usuario.cedula = %s" if cedula else ""}
            ORDER BY fecha DESC, hora DESC 
            """,
            f"""
            SELECT iz.Id_ingreso, usuario.Nombres, iz.Puerta, iz.fecha, iz.hora 
            FROM ingresos_zona AS iz 
            INNER JOIN usuario ON iz.Id_usuario = usuario.ID 
            {"WHERE iz.fecha >= %s" if periodo != 'todos' else ""}
            {"AND usuario.cedula = %s" if cedula else ""}
            ORDER BY fecha DESC, hora DESC 
            """,
            f"""
            SELECT historial_alerta.Id, alerta.nombre, historial_alerta.Fecha_Alerta, 
            historial_alerta.hora_alerta 
            FROM historial_alerta 
            INNER JOIN alerta ON historial_alerta.Detalles = alerta.id_alerta 
            {"WHERE historial_alerta.Fecha_Alerta >= %s" if periodo != 'todos' else ""}
            ORDER BY historial_alerta.hora_alerta DESC, historial_alerta.Fecha_Alerta ASC 
            """,
            f"""
            SELECT usos_sistema.id_historial, usuario.Nombres, usos_sistema.Tabla_Editada, 
            usos_sistema.Accion, usos_sistema.Fecha, usos_sistema.hora 
            FROM usos_sistema 
            INNER JOIN ingresos_sistema ON usos_sistema.Id_ingreso = ingresos_sistema.id_ingreso 
            INNER JOIN usuario ON ingresos_sistema.id_usuario2 = usuario.ID 
            {"WHERE usos_sistema.Fecha >= %s" if periodo != 'todos' else ""}
            {"AND usuario.cedula = %s" if cedula else ""}
            ORDER BY usos_sistema.Fecha ASC, usos_sistema.Hora DESC 
            """
        ]

        # Nombres de las tablas para el reporte
        nombres_tablas = [
            "Usuarios Registrados",
            "Huellas Registradas",
            "Registro de Ingresos al Sistema",
            "Registro de Ingresos a Zonas",
            "Historial de Alertas",
            "Registros de Usos de Sistema"
        ]

        # Procesar cada consulta
        for index, consulta in enumerate(consultas):
            params = []
            if cedula:
                params.append(cedula)
            if periodo != 'todos':
                params.append(fecha_desde)

            print("esta es la cedula: ", cedula, "estos son los params: ", params)

            # Solo ejecutar la consulta si hay parámetros
            if ('%s' in consulta and params):
                # Verificar que el número de parámetros coincida con los marcadores de posición
                num_placeholders = consulta.count('%s')
                if num_placeholders == len(params):
                    data = self.conexion.ejecutar_consulta(consulta, params)

                    if data:
                        # Convertir los datos a una tabla
                        table_data = [list(row) for row in data]

                        # Agregar encabezados
                        headers = [desc[0] for desc in self.conexion.ejecutar_consulta(f"DESCRIBE {consulta.split('FROM')[1].split()[0]}")]
                        # Eliminar campos no deseados de la tabla de usuarios
                        if index == 0:  # Solo para la primera tabla
                            headers = [h for h in headers if h not in ['contrasena', 'sal']]
                        
                        table_data.insert(0, headers)

                        # Crear el título y subtítulo
                        styles = getSampleStyleSheet()
                        title = Paragraph(f'Tabla: {nombres_tablas[index]}', styles['Title'])
                        subtitle_style = ParagraphStyle(name='SubtitleStyle', fontSize=12, alignment=1)  # 1 para centrado
                        subtitle = Paragraph('Sistema nacional de Orquestas y Coros Juveniles e Infantiles de Venezuela Núcleo Rubio', subtitle_style)
                        date_info = Paragraph(f'Fecha de generación: {fecha_hasta.strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal'])

                        content.append(title)
                        content.append(subtitle)
                        content.append(date_info)
                        content.append(Spacer(1, 12))

                        # Crear la tabla
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        content.append(table)

                        # Pie de página
                        footer = Paragraph(f'Generado por: {self.generador}, Cargo: {self.cargo}', styles['Normal'])
                        content.append(Spacer(1, 12))
                        content.append(footer)
                        content.append(PageBreak())  # Salto de página para la siguiente tabla
            elif '%s' not in consulta:
                data = self.conexion.ejecutar_consulta(consulta)

                if data:
                    # Convertir los datos a una tabla
                    table_data = [list(row) for row in data]

                    # Agregar encabezados
                    headers = [desc[0] for desc in self.conexion.ejecutar_consulta(f"DESCRIBE {consulta.split('FROM')[1].split()[0]}")]
                    # Eliminar campos no deseados de la tabla de usuarios
                    if index == 0:  # Solo para la primera tabla
                        headers = [h for h in headers if h not in ['contrasena', 'sal']]
                    
                    table_data.insert(0, headers)

                    # Crear el título y subtítulo
                    styles = getSampleStyleSheet()
                    title = Paragraph(f'Tabla: {nombres_tablas[index]}', styles['Title'])
                    subtitle_style = ParagraphStyle(name='SubtitleStyle', fontSize=12, alignment=1)  # 1 para centrado
                    subtitle = Paragraph('Sistema nacional de Orquestas y Coros Juveniles e Infantiles de Venezuela Núcleo Rubio', subtitle_style)
                    date_info = Paragraph(f'Fecha de generación: {fecha_hasta.strftime("%Y-%m-%d %H:%M:%S")}', styles['Normal'])

                    content.append(title)
                    content.append(subtitle)
                    content.append(date_info)
                    content.append(Spacer(1, 12))

                    # Crear la tabla
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ]))
                    content.append(table)

                    # Pie de página
                    footer = Paragraph(f'Generado por: {self.generador}, Cargo: {self.cargo}', styles['Normal'])
                    content.append(Spacer(1, 12))
                    content.append(footer)
                    content.append(PageBreak()) 
        # Solo construir el documento si hay contenido
        if content:
            document.build(content)
            consulta = "insert into historial_alerta values(null, 9, CURRENT_DATE(), CURRENT_TIME())"
            self.conexion.ejecutar_actualizacion(consulta, valores = None)
            consulta = "insert into usos_sistema values(null,(select id_ingreso from ingresos_sistema order by id_ingreso desc limit 1), 'PDF-Reportes', 'Generacion de reporte', CURRENT_DATE(), CURRENT_TIME())"
            self.conexion.ejecutar_actualizacion(consulta, valores = None)
        else:
            print("No se generó contenido para el reporte.")

# Ejemplo de uso
# reporte = ReportePDF("reporte.pdf", "Nombre Generador", "Cargo")
# reporte.generar_reporte("123456789", "ultimo_mes")
