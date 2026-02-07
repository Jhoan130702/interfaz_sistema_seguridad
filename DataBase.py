import flet as ft
import mysql.connector 

class ConexionBaseDatos:
    def __init__(self):
        self.conexion = None
        self.cursor = None


    def conectar(self):
            
        self.conexion = mysql.connector.connect(
        host="localhost",
        user="root_remoto",
        password="Jhoan",
        database="sistema_seguridad",
        port='3306'
        )
        self.cursor = self.conexion.cursor()

    def desconectar(self):
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()

    def ejecutar_consulta(self, consulta, valores=None):
        self.conectar()
        self.cursor.execute(consulta, valores)
        resultados = self.cursor.fetchall()
        self.desconectar()
        return resultados
    
    def ejecutar_consulta2(self, consulta, valores):
        self.conectar()
        self.cursor.execute(consulta, valores)
        resultados = self.cursor.fetchall()
        self.desconectar()
        return resultados

    def ejecutar_actualizacion(self, consulta, valores):
        self.conectar()
        self.cursor.execute(consulta, valores)
        self.conexion.commit()

        if "CALL Login" in consulta:
            # Ejecutar la consulta para obtener el valor de la variable de salida
            self.cursor.execute("SELECT @cedulaUsuario;")
            resultado = self.cursor.fetchone()
            self.desconectar()  # Desconectar aquí para evitar problemas de conexión
            if resultado:
                return resultado[0]
            else:
                print("No se encontró el resultado.")
                return None  # Retornar None si no hay resultado
        
        if "CALL CreateUsuario" in consulta:
            print("si cumple")
            # Ejecutar la consulta para obtener el valor de la variable de salida
            self.cursor.execute("SELECT @resultado;")
            resultado = self.cursor.fetchone()
            self.desconectar()  # Desconectar aquí para evitar problemas de conexión
            if resultado:
                print(resultado[0:1][0])
                return resultado[0:1][0]
            else:
                print("No se encontró el resultado.")
                return None  # Retornar None si no hay resultado
        
        self.desconectar()

    def cerrar_conexion(self):
        self.desconectar()