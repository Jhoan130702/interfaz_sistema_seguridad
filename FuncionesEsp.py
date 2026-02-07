import requests
import time
from datetime import datetime
import json
import flet as ft
import threading
import DataBase
import NotificacionesBarra
notificacion =  NotificacionesBarra.Notificador()
hora_actual = datetime.now().strftime("%H:%M")
###################################################################################################### ACTIVACION DEL PIR tercer hilo
class Pir(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True 
        self.url = "http://192.168.4.1/"
    
    def run(self):
        while True:
            # Obtener la hora actual
            hora_actual = datetime.now().strftime("%H:%M")
            print(f"La hora actual: {hora_actual}")
        
            # Verificar si son las 6:00 PM ("18:00")
            if hora_actual == "18:00":
                self.activar_pir(hora_actual)
                # Esperar 59 min para evitar múltiples activaciones la misma hora
                time.sleep(120)
            elif hora_actual == "19:00":
                self.activar_pir(hora_actual)
                # Esperar 29 min para evitar múltiples activaciones la misma hora
                time.sleep(1740)
            elif hora_actual == "19:30":
                self.activar_pir(hora_actual)
                # Esperar 22 horas para evitar múltiples activaciones en el mismo día
                time.sleep(79200)
            else:
                # Esperar un minuto antes de volver a verificar
                time.sleep(60)
    
    def activar_pir(self, hora_actual):
        command = "PIR"  # Comando para activar el pir
        data = {"command": command}
        response = requests.post(self.url, data=data)

        if response.status_code == 200:
            mensaje = f"Comando enviado exitosamente: {response.text}, a las {hora_actual}"
            notificacion.mostrar_notificacion(mensaje)
            print(f"Comando enviado exitosamente: {response.text}")
            print(f"Hora de activación: {hora_actual}")
        else:
            mensaje = f"Error al enviar el comando: {response.text} a las {hora_actual}"
            notificacion.mostrar_notificacion(mensaje)
            print("Error al enviar el comando al NodeMCU")
def iniciar_pir():
    # Crear una instancia de la clase Pir
    print("PIR Activado")
    activar_pir = Pir()

    # Iniciar el hilo
    activar_pir.activar_pir(hora_actual)
########################################################################################## Ejecucion 2 en Segundo Plano
class MiHilo2(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.daemon = True 
        self.tiempo = 5
        self.paused = threading.Event()  # Usar Event para controlar la pausa
        self.paused.set()  # Comenzar en estado de ejecución

    def hacer_consulta(self):
        self.db = DataBase.ConexionBaseDatos()

        # Consulta de PIR
        url_d = "http://192.168.4.1/handlepir"
        params_d = {'box_d': 'valor_de_box_d'}

        try:
            response_d = requests.get(url_d, params=params_d)
            response_d.raise_for_status()
            data_d = response_d.text

            if "Operación no válida" in data_d:
                result_box_d = None
            elif " " in data_d:
                result_box_d = None
            else:
                result_box_d = int(data_d.strip('"'))
                if result_box_d == 1:
                    mensaje = f"Hay Movimiento en el area a las {hora_actual}"
                    notificacion.mostrar_notificacion(mensaje)
                    self.db.ejecutar_actualizacion(f"insert into historial_alerta values (Null, 1, CURRENT_DATE(), current_time())", valores=None)
                print(f"Variable box_d recibida desde ESP8266: {result_box_d}")

        except requests.exceptions.RequestException:
            print("Error en la solicitud de box_d")

        # Consulta de lector de huellas
        url_c = "http://192.168.4.1/handleRequest"
        params_c = {'box_c': 'valor_de_box_c'}

        try:
            response_c = requests.get(url_c, params=params_c)
            response_c.raise_for_status()
            data_c = response_c.text
            print(data_c)
            if "Operación no válida" in data_c:
                print("Operación no válida para box_c")
            elif " " in data_c:
                if "Acceso denegado" in data_c:
                    print(data_c)
                    mensaje = f"Acceso Denegado a las: {hora_actual}"
                    notificacion.mostrar_notificacion(mensaje)
                    self.db.ejecutar_actualizacion(f"insert into historial_alerta values (null, 2, CURRENT_DATE(), CURRENT_TIME())", valores=None)
            else:
                result_box_c = int(data_c.strip('"'))
                if result_box_c:
                    if result_box_c >= 1:
                        valores = (result_box_c,) * 4
                        mensaje = f"Acceso Concedido a las {hora_actual}"
                        notificacion.mostrar_notificacion(mensaje)
                        consulta = "insert into ingresos_zona values (null, (select usuario.ID from usuario inner join huella on usuario.id = huella.ID_Usuarios where huella.Huella_1_P_D = %s or huella.Huella_2_P_I = %s or huella.Huella_3_I_D = %s or huella.Huella_4_I_I = %s limit 1), 'Deposito', CURRENT_DATE(), current_time())"
                        self.db.ejecutar_actualizacion(consulta, valores)
                    elif result_box_c < 1:
                        self.db.ejecutar_actualizacion(f"insert into historial_alerta values (null, 2, CURRENT_DATE(), CURRENT_TIME())", valores=None)

                print(f"Variable box_c recibida desde ESP8266: {result_box_c}")

        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud de box_c: {e}")

    def run(self):
        while True:
            self.paused.wait()  # Esperar hasta que se reanude
            print("Ejecutando consulta hilo 2...")
            self.hacer_consulta()
            time.sleep(self.tiempo)

    def pause(self):
        self.paused.clear()  # Pausar el hilo
        print("Hilo 2 en pausa")

    def resume(self):
        self.paused.set()  # Reanudar el hilo
        print("Hilo 2 reanudado")

###################################################### Hilo 1
class MiHilo(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.daemon = True 
        self.tiempo = 180.1  
        self.paused = threading.Event()  # Usar Event para controlar la pausa
        self.paused.set()  # Comenzar en estado de ejecución
        self.hilo2 = MiHilo2()  # Crear instancia del segundo hilo

    def hacer_consulta(self):
        self.db = DataBase.ConexionBaseDatos()

        self.datos = []
        self.mensaje = []
        # Realizar aquí la consulta a la base de datos
        resultados = self.db.ejecutar_consulta("SELECT Huella_1_P_D, Huella_2_P_I, Huella_3_I_D, Huella_4_I_I from huella")

        for fila in resultados:
            self.datos.append(fila[0:])
        
        temporal = []
        for tupla in self.datos:
            temporal.extend(tupla)
        
        self.datos = temporal
        
        # Conexión y consulta al ESP
        url = "http://192.168.4.1/"
        command = "Consultar"

        data = {"command": command}
        response = requests.post(url, data=data)
        temporal = ""
        if response.status_code == 200:
            for letra in response.text:
                if letra.isdigit():
                    temporal += letra
                elif temporal:
                    self.mensaje.append(int(temporal))
                    temporal = ""
            if temporal:
                self.mensaje.append(int(temporal))
        else:
            print("Error al enviar el comando al NodeMCU")
        
        print(self.mensaje, self.datos)
        
        if not self.mensaje and not self.datos:
            print("No hay ninguna huella registrada")
        elif self.datos and not self.mensaje:
            self.db.ejecutar_actualizacion("Delete from huella where id > 0;")
            print("No había datos en el esp")
        elif self.mensaje and not self.datos:
            url = "http://192.168.4.1/"
            command = "Eliminar"

            for box_a in self.mensaje:
                data = {"command": command, "box_a": str(box_a)}
                response = requests.post(url, data=data)

                if response.status_code == 200:
                    id_response = response.text
                    print("Huella eliminada con ID:", id_response)
                else:
                    print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
        else:
            eliminar_db = []
            eliminar_esp = []
            
            for dato in self.datos:
                if dato not in self.mensaje:
                    eliminar_db.append(dato)
            
            for huella in self.mensaje:
                if huella not in self.datos:
                    eliminar_esp.append(huella)

            if eliminar_esp:
                url = "http://192.168.4.1/"
                command = "Eliminar"

                for huella in eliminar_esp:
                    data = {"command": command, "box_a": str(huella)}
                    response = requests.post(url, data=data)

                    if response.status_code == 200:
                        id_response = response.text
                        print("Huella eliminada del dispositivo NodeMCU con ID:", id_response)
                    else:
                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

        resultados = self.db.ejecutar_consulta("select permisos.Id, huella.Huella_1_P_D, huella.Huella_2_P_I, huella.Huella_3_I_D, huella.Huella_4_I_I from permisos inner join usuario on permisos.ID = usuario.Cargo inner join huella on usuario.ID = huella.ID_Usuarios where huella.Huella_1_P_D > 0")
        datos = []
        for fila in resultados:
            datos.append(list(fila[0:]))

        for fila in datos:
            valor = fila[0]
            if valor == 1:
                fila[0] = 000
            elif valor >= 2 and valor <= 5:
                fila[0] = 333
            elif valor == 6:
                fila[0] = 222
            elif valor > 6:
                fila[0] = 111

        matriz_volteada = []

        for fila in datos:
            for i in range(1, len(fila)):
                fila_matriz = []
                fila_matriz.append(fila[i])
                fila_matriz.append(fila[0])
                matriz_volteada.append(fila_matriz)

        print(matriz_volteada)

        url = "http://192.168.4.1/"
        command = "sql"

        array_data = json.dumps(matriz_volteada)
        data = {"command": command, "array": array_data}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            print("Respuesta del NodeMCU:", response.text)
        else:
            print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

        self.db.cerrar_conexion()

    def run(self):
        self.hilo2.start()  # Iniciar el hilo 2
        while True:
            self.paused.wait()  # Esperar hasta que se reanude
            self.hilo2.pause()  # Pausar el hilo 2
            print("Ejecutando consulta hilo 1...")
            self.hacer_consulta()
            self.hilo2.resume()  # Reanudar el hilo 2
            
            time.sleep(self.tiempo)

    def pause(self):
        self.paused.clear()  # Pausar el hilo
        print("Hilo 1 en pausa")

    def resume(self):
        self.paused.set()  # Reanudar el hilo
        print("Hilo 1 reanudado")

def iniciar_hilos():
    mi_hilo = MiHilo()

    mi_hilo.start()  # Iniciar el hilo 1
    # El hilo 2 se inicia dentro de MiHilo

################################################################################################# Codigo para registro de huellas
class RegistroHuellas:
    def __init__(self, page):
        self.page = page
        self.conn = DataBase.ConexionBaseDatos()
        self.hilo = MiHilo()
        self.hilo2 = MiHilo2()
        self.continuar_registro = True
        
    def registrar_huellas(self, nombre, page):
        self.page = page
        result = self.conn.ejecutar_consulta("SELECT Nombres FROM usuario where estado > 0")
        validar = [fila[0] for fila in result]

        if nombre:
            if nombre in validar:
                try:
                    # Detener temporalmente los hilos
                    self.hilo.pause()
                    self.hilo2.pause()
                    id_var = None
                    huellas = []
                    id_response = []
                    url = "http://192.168.4.1/"
                    command = "Registrar"
                    bottom_sheet = ft.BottomSheet(
                        content=ft.Container(
                            padding=50, 
                            content=ft.Column(
                                tight=True, 
                                controls=[
                                    ft.Text("Escaneando"),
                                    ft.Text("Por Favor Atento!, se va a Activar el Lector de Huellas")
                                ]
                            )
                        )
                    )
                    self.page.overlay.append(bottom_sheet)
                    bottom_sheet.open = True
                    self.page.update()

                    for i in range(4):
                        
                        if not self.continuar_registro:  # Verificar si debe continuar
                            print("Registro de huellas detenido.")
                            command = "Eliminar"
                            for box_a in huellas:
                                data = {"command": command, "box_a": str(box_a)}
                                response = requests.post(url, data=data)
                                if response.status_code == 200:
                                    id_response = response.text
                                    print("Huella eliminada con ID:", id_response)
                                else:
                                    print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            break
                        
                        data = {"command": command}
                        response = requests.post(url, data=data)

                        if response.status_code == 200:
                            huellas_db = self.conn.ejecutar_consulta("SELECT Huella_1_P_D, Huella_2_P_I, Huella_3_I_D, Huella_4_I_I FROM Huella")
                            id_response = response.text
                            print("huella", i + 1, "registrada con ID:", id_response)

                            if len(id_response) < 4:
                                if  int(id_response) not in huellas_db:
                                    id_var = f"id_{i + 1}"
                                    huellas.append(id_response)
                                    bottom_sheet = ft.BottomSheet(
                                        content=ft.Container(
                                            padding=50, 
                                            content=ft.Column(
                                                tight=True, 
                                                controls=[
                                                    ft.Text("Escaneado"),
                                                    ft.Text(f"{i+1} Huella escaneada correctamente")
                                                ]
                                            )
                                        )
                                    )
                                    self.page.overlay.append(bottom_sheet)
                                    bottom_sheet.open = True
                                    self.page.update()
                                else:
                                    while int(id_response) in huellas_db:
                                        print(id_response)
                                        
                                        bottom_sheet = ft.BottomSheet(
                                            content=ft.Container(
                                                padding=50, 
                                                content=ft.Column(
                                                    tight=True, 
                                                    controls=[
                                                        ft.Text(f"Error {i+1}"),
                                                        ft.Text(id_response, "Ya está en la base de")
                                                    ]
                                                )
                                            )
                                        )
                                        self.page.overlay.append(bottom_sheet)
                                        bottom_sheet.open = True
                                        self.page.update()
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                    
                                    bottom_sheet = ft.BottomSheet(
                                        content=ft.Container(
                                            padding=50, 
                                            content=ft.Column(
                                                tight=True, 
                                                controls=[
                                                    ft.Text("Escaneado"),
                                                    ft.Text(f"{i+1} Huella escaneada correctamente")
                                                ]
                                            )
                                        )
                                    )
                                    self.page.overlay.append(bottom_sheet)
                                    bottom_sheet.open = True
                                    self.page.update()
                                setattr(self, id_var, id_response)
                            elif len(id_response) >= 4:
                                while len(id_response) >= 4:
                                    print(id_response)
                                    
                                    bottom_sheet = ft.BottomSheet(
                                        content=ft.Container(
                                            padding=50, 
                                            content=ft.Column(
                                                tight=True, 
                                                controls=[
                                                    ft.Text(f"Error {i+1}"),
                                                    ft.Text(id_response)
                                                ]
                                            )
                                        )
                                    )
                                    self.page.overlay.append(bottom_sheet)
                                    bottom_sheet.open = True
                                    self.page.update()
                                    data = {"command": command}
                                    response = requests.post(url, data=data)
                                    id_response = response.text
                                
                                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Escaneado"),
                                                ft.Text(f"{i+1} Huella escaneada correctamente")
                                            ]
                                        )
                                    )
                                )
                                self.page.overlay.append(bottom_sheet)
                                bottom_sheet.open = True
                                self.page.update()
                            else:
                                while int(id_response) in huellas_db:
                                    print(id_response)
                                    
                                    bottom_sheet = ft.BottomSheet(
                                        content=ft.Container(
                                            padding=50, 
                                            content=ft.Column(
                                                tight=True, 
                                                controls=[
                                                    ft.Text(f"Error {i+1}"),
                                                    ft.Text(id_response)
                                                ]
                                            )
                                        )
                                    )
                                    self.page.overlay.append(bottom_sheet)
                                    bottom_sheet.open = True
                                    self.page.update()
                                    data = {"command": command}
                                    response = requests.post(url, data=data)
                                    id_response = response.text
                                
                                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Escaneado"),
                                                ft.Text(f"{i+1} Huella escaneada correctamente")
                                            ]
                                        )
                                    )
                                )
                                self.page.overlay.append(bottom_sheet)
                                bottom_sheet.open = True
                                self.page.update()
                            setattr(self, id_var, id_response)

                        else:
                            print("error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                            bottom_sheet = ft.BottomSheet(
                                content=ft.Container(
                                    padding=50, 
                                    content=ft.Column(
                                        tight=True, 
                                        controls=[
                                            ft.Text("Error"),
                                            ft.Text("Error al enviar el comando al modulo NodeMCU")
                                        ]
                                    )
                                )
                            )
                            self.page.overlay.append(bottom_sheet)
                            bottom_sheet.open = True
                            self.page.update()
                            self.hilo.resume()
                            self.hilo2.resume()
                            return

                    if hasattr(self, 'id_4'):
                        try:
                            nombre = self.conn.ejecutar_consulta(f"SELECT ID FROM usuario WHERE Nombres = '{nombre}'")
                            try:
                                valores=[]
                                valores = (int(nombre[0][0]), int(huellas[0]), int(huellas[1]), int(huellas[2]), int(huellas[3]))
                                print(valores)
                                Consulta = "INSERT INTO huella VALUES (null, %s, %s, %s, %s, %s)"
                                self.conn.ejecutar_actualizacion(Consulta, valores)
                                
                                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("¡Registro Exitoso!"),
                                                ft.Text("Todas las Huellas han sido registradas exitosamente")
                                            ]
                                        )
                                    )
                                )
                                self.page.overlay.append(bottom_sheet)
                                bottom_sheet.open = True
                                self.page.update()
                                self.hilo.resume()
                                self.hilo2.resume()

                            except Exception as e:
                                print("Error al registrar las Huellas:", e)
                                bottom_sheet = ft.BottomSheet(
                                    content=ft.Container(
                                        padding=50, 
                                        content=ft.Column(
                                            tight=True, 
                                            controls=[
                                                ft.Text("Error"),
                                                ft.Text("No se pudo registrar las Huellas")
                                            ]
                                        )
                                    )
                                )
                                self.page.overlay.append(bottom_sheet)
                                bottom_sheet.open = True
                                self.page.update()
                                self.eliminar_huellas(huellas)
                                self.hilo.resume()
                                self.hilo2.resume()
                                id_var = []
                                
                        except Exception as e:
                            print(e)
                            bottom_sheet = ft.BottomSheet(
                                content=ft.Container(
                                    padding=50, 
                                    content=ft.Column(
                                        tight=True, 
                                        controls=[
                                            ft.Text("Error"),
                                            ft.Text("Entrada Invalida, el Usuario no está en la base de datos")
                                        ]
                                    )
                                )
                            )
                            self.page.overlay.append(bottom_sheet)
                            bottom_sheet.open = True
                            self.page.update()
                            self.eliminar_huellas(huellas)
                            self.hilo.resume()
                            self.hilo2.resume()
                            id_var = []

                except Exception as e:
                    print(e)
                    bottom_sheet = ft.BottomSheet(
                        content=ft.Container(
                            padding=50, 
                            content=ft.Column(
                                tight=True, 
                                controls=[
                                    ft.Text("Error"),
                                    ft.Text("No se puede conectar con el modulo NodeMCU")
                                ]
                            )
                        )
                    )
                    self.page.overlay.append(bottom_sheet)
                    bottom_sheet.open = True
                    self.page.update()
                    self.eliminar_huellas(huellas)
                    self.hilo.resume()
                    self.hilo2.resume()
            else:
                bottom_sheet = ft.BottomSheet(
                    content=ft.Container(
                        padding=50, 
                        content=ft.Column(
                            tight=True, 
                            controls=[
                                ft.Text("Usuario no existe"),
                                ft.Text("El usuario no está en la base de datos")
                            ]
                        )
                    )
                )
                self.page.overlay.append(bottom_sheet)
                bottom_sheet.open = True
                self.page.update()
                
        else:
            bottom_sheet = ft.BottomSheet(
                content=ft.Container(
                    padding=50, 
                    content=ft.Column(
                        tight=True, 
                        controls=[
                            ft.Text("Campos Vacios"),
                            ft.Text("Por Favor Indique el Usuario")
                        ]
                    )
                )
            )
            self.page.overlay.append(bottom_sheet)
            bottom_sheet.open = True
            self.page.update()

    def eliminar_huellas(self, ids):
        url = "http://192.168.4.1/"
        command = "Eliminar"
        for box_a in ids:
            if box_a:
                data = {"command": command, "box_a": str(box_a)}
                response = requests.post(url, data=data)
                if response.status_code == 200:
                    id_response = response.text
                    print("Huella eliminada con ID:", id_response)
                else:
                    print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
    def detener_registro(self):
        print("rompe el bucle")
        self.continuar_registro = False  # Método para detener el registro


################################################################################################# Manejo de Notificaciones a Slack
class NotificacionesESP():
    def acceso():
        print("acceso")
        url = "http://192.168.4.1/"
        print(url)
        command = "notificacion"
        print(command)

        data = {"command": command}
        print(data)
        try:
            response = requests.post(url, data=data, timeout=15)
            response.raise_for_status()  # Lanza un error si la respuesta fue un error HTTP
            print(response.text)  # Imprime la respuesta del servidor
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
            
    def AbrirPuerta():
        print("Abrir Puerta")
        url = "http://192.168.4.1/"
        print(url)
        command = "puerta"
        print(command)

        data = {"command": command}
        print(data)
        try:
            response = requests.post(url, data=data, timeout=15)
            response.raise_for_status()  # Lanza un error si la respuesta fue un error HTTP
            print(response.text)  # Imprime la respuesta del servidor
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
    
    def ProblemaInicio():
        print("Problema de Inicio")
        url = "http://192.168.4.1/"
        print(url)
        command = "notificacioninicio"
        print(command)

        data = {"command": command}
        print(data)
        try:
            response = requests.post(url, data=data, timeout=15)
            response.raise_for_status()  # Lanza un error si la respuesta fue un error HTTP
            print(response.text)  # Imprime la respuesta del servidor
        except requests.exceptions.RequestException as e:
            print(f"Error al enviar la solicitud: {e}")
            

def EnviarNotificaciones():
    print("Enviar")
    Enviar = NotificacionesESP
    Enviar.ProblemaInicio()
    
# EnviarNotificaciones()