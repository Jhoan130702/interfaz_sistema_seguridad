import threading
import time
from plyer import notification
import DataBase  # Cambia esto según tu base de datos

class Notificador(threading.Thread):
    def __init__(self):
        self.conexion = DataBase.ConexionBaseDatos()  # Asegúrate de que esta clase esté bien definida
        self.hilo = None
        self.ejecutando = True  # Controla el bucle del hilo

    def mostrar_notificacion(self, mensaje):
        icon_path = r"Icono_notificacion.ico"
        
        notification.notify(
            title="Nueva Notificación",
            message=mensaje,
            app_name='Sistema Seguridad',
            timeout=10,  # Duración de la notificación en segundos
            app_icon=icon_path
        )

    def consultar_soporte(self):
        while self.ejecutando:
            try:
                resultados = self.conexion.ejecutar_consulta("SELECT * FROM soporte WHERE estatus > 0 limit 1")
                if resultados:
                    mensaje = f"Nueva Solicitud: {resultados[0][0]}, El Usuario: {resultados[0][1]} tuvo problemas para ingresar al sistema el día: {resultados[0][2]}, a las {resultados[0][3]}"
                    self.mostrar_notificacion(mensaje)
                    consulta = f"UPDATE soporte set estatus = 0 where id = {resultados[0][0]}"
                    self.conexion.ejecutar_actualizacion(consulta, valores=None)

            except Exception as e:
                print(f"Error al realizar la consulta: {e}")

            time.sleep(20)  # Espera 10 segundos antes de volver a consultar

    def iniciar_notificacion(self):
        self.hilo = threading.Thread(target=self.consultar_soporte)
        self.hilo.start()

    def detener_notificacion(self):
        self.ejecutando = False
        if self.hilo:
            self.hilo.join()

# Ejemplo de uso
def iniciar():
    notificador = Notificador()  # No se necesita pasar la ruta aquí
    notificador.iniciar_notificacion()

    try:
        while True:
            time.sleep(1)  # Mantiene el programa en ejecución
    except KeyboardInterrupt:
        notificador.detener_notificacion()
        print("Notificador detenido.")
