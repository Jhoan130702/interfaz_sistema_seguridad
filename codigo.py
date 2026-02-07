import tkinter as tk
from tkinter import ttk
import mysql.connector
from tkinter import messagebox
import requests
import threading
import time
import json
import screeninfo 

###################################################################################################### ACTIVACION DEL PIR
class pir():
    def __init__(self):
        self.url = "http://192.168.4.1/"
        

    def activar_pir(self):
        self.url = "http://192.168.4.1/"
        self.command = "PIR"  # Comando para activar la suma
        data = {"command": self.command}
        response = requests.post(self.url, data=data)

        if response.status_code == 200:
            print(response.text)
        else:
            print("Error al enviar el comando al NodeMCU")
activar_pir = pir()


##################################################################################################### EJECUCION 2 EN SEGUNDO PLANO 
class MiHilo2(threading.Thread):
    
    def __init__(self):
        super().__init__()
        activar_pir = pir()
        self.tiempo = 5  
        self.paused = False  # Variable para controlar la pausa del hilo
        self.pause_cond = threading.Condition(threading.Lock())  # Condición para pausar el hilo
        
        # Configuración de la conexión a la base de datos
        
    # Función para realizar la consulta a la base de datos
    def hacer_consulta(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )

        self.cursor = self.conn.cursor()

############################################################# consulta de pir

        url_d = "http://192.168.4.1/handlepir"
        params_d = {'box_d': 'valor_de_box_d'}  # Aquí, '5' es un ejemplo de valor que deseas enviar

        try:
            # Realizar una solicitud GET al ESP8266 para box_d
            response_d = requests.get(url_d, params=params_d)
            response_d.raise_for_status()  # Generar una excepción para códigos de error HTTP

            # Analizar la respuesta JSON para box_d
            data_d = response_d.text

            if "Operación no válida" in data_d:
                result_box_d = None  # Puedes asignar cualquier valor predeterminado
                print("Operación no válida para box_d")
            elif " " in data_d:
                result_box_d = None  # Puedes asignar cualquier valor predeterminado
                print(f"solicitud {data_d}") 
            else:
                result_box_d = int(data_d.strip('"'))
                print(result_box_d)
                if result_box_d == 1:
                    self.cursor.execute(f"insert into alerta_usuario values (4, 1, 1, 1, CURRENT_DATE(), current_time())")
                    self.conn.commit()
                    self.cursor.fetchall()
                print(f"Variable box_d recibida desde ESP8266: {result_box_d}")
                # Operación para handleacces si es necesario

        except requests.exceptions.RequestException as e:
            result_box_d = None  # Puedes asignar cualquier valor predeterminado
            print("Error en la solicitud de box_d")

############################################################ consulta de lector de huellas

        url_c = "http://192.168.4.1/handleRequest"
        params_c = {'box_c': 'valor_de_box_c'}

        try:
            # Espera 2 segundos antes de realizar la solicitud para box_d

            # Realiza una solicitud GET al ESP8266 para box_c
            response_c = requests.get(url_c, params=params_c)
            response_c.raise_for_status()  # Genera una excepción para códigos de error HTTP

            # Analiza la respuesta JSON para box_c
            data_c = response_c.text

            if "Operación no válida" in data_c:
                result_box_c = None  # Puedes asignar cualquier valor predeterminado
                print("Operación no válida para box_c")
            elif " " in data_c:
                result_box_c = None  # Puedes asignar cualquier valor predeterminado
                print(f"solicitud {data_c}")            
            else:
                result_box_c = int(data_c.strip('"'))
                print(result_box_c)
                if result_box_c:
                    print(result_box_c)
                    if result_box_c >= 1:
                        self.cursor.execute(f"insert into alerta_usuario values (3, (select usuario.ID from usuario inner join huella on usuario.id = huella.ID_Usuarios where huella.Huella_1_P_D = {result_box_c} or huella.Huella_2_P_I = {result_box_c} or huella.Huella_3_I_D = {result_box_c} or huella.Huella_4_I_I = {result_box_c} or huella.Huella_5_M_D = {result_box_c} or huella.Huella_6_M_I = {result_box_c}), 1, 1, CURRENT_DATE(), current_time())")
                        self.conn.commit()
                        self.cursor.fetchall()
                    elif result_box_c < 1:
                        self.cursor.execute(f"insert into alerta_usuario values (1, 1, 1, 1, CURRENT_DATE(), CURRENT_TIME())")
                        self.conn.commit()
                        self.cursor.fetchall()

                else:
                    result_box_c = data_c
                    print(f"Variable box_c recibida desde ESP8266: {result_box_c}")
                    if len(result_box_c) > 1:
                        self.cursor.execute(f"insert into alerta_usuario values (1, 1, 1, 1, CURRENT_DATE(), CURRENT_TIME())")
                        self.conn.commit()
                    self.cursor.fetchall()
                    # Operación para handlepir
                    

        except requests.exceptions.RequestException as e:
            result_box_c = None  # Puedes asignar cualquier valor predeterminado
            print(f"Error en la solicitud de box_c: {e}")

            
        self.cursor.close()
        self.conn.close()

######################################################## resto de funcionalidades del hilo

    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
            # Aquí va el código de tu hilo
            print("Ejecutando consulta...")
            self.hacer_consulta()
            time.sleep(self.tiempo)  # Hacer una pausa de 2 segundos entre consultas
    
    def pause(self):
        with self.pause_cond:
            self.paused = True
            print("Hilo en pausa")

    def resume(self):
        with self.pause_cond:
            self.paused = False
            self.pause_cond.notify()
            print("Hilo reanudado")

# Crear una instancia del hilo
mi_hilo2 = MiHilo2()

# Iniciar el hilo
mi_hilo2.start()



##################################################################################################### EJECUCION 1 EN SEGUNDO PLANO 

class MiHilo(threading.Thread):
    
    def __init__(self):
        super().__init__()
        mi_hilo2 = MiHilo2()

        self.tiempo = 130.7  
        self.paused = False  # Variable para controlar la pausa del hilo
        self.pause_cond = threading.Condition(threading.Lock())  # Condición para pausar el hilo
        
        # Configuración de la conexión a la base de datos
        
    # Función para realizar la consulta a la base de datos
    def hacer_consulta(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )

        self.cursor = self.conn.cursor()
        
        

        self.datos = []
        self.mensaje = []
        fila = []
        letra = []
        i = []
        # Realizar aquí la consulta a la base de datos
        self.cursor.execute("SELECT Huella_1_P_D, Huella_2_P_I, Huella_3_I_D, Huella_4_I_I, Huella_5_M_D, Huella_6_M_I from huella")

        #se asignan los resultados de la consulta a base de datos a un array
        for fila in self.cursor:
            self.datos.append(fila[0:])
        self.cursor.fetchall()
        
        temporal = []

        for tupla in self.datos:
            temporal.extend(tupla)
        
        self.datos = temporal
        # Liberar los resultados pendientes
        self.cursor.nextset()
        
        #se realiza la conexion y consulta al esp
        url = "http://192.168.4.1/"
        command = "Consultar"  # Comando para consultar

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
            self.cursor.execute("Delete from huella where id > 0;")
            self.conn.commit()
            self.cursor.fetchall()
            print ("no habian datos en el esp")

        elif self.mensaje and not self.datos:
            url = "http://192.168.4.1/"
            command = "Eliminar"  # Comando para activar la suma

            for i in range(len(self.mensaje)):
                box_a = self.mensaje[i]

                data = {"command": command, "box_a": str(box_a)}
                response = requests.post(url, data=data)

                if response.status_code == 200:
                    # Recibe el ID como un entero
                    id_response = response.text
                    print("Huella eliminada con ID:", id_response)
                else:
                    print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
        else:
            eliminar_db = []
            eliminar_esp = []
            arreglo = []
            for i in range(len(self.datos)):
                if self.datos[i] not in self.mensaje:
                    eliminar_db.append(self.datos[i])
            
            for i in range(len(self.mensaje)):
                if self.mensaje[i] not in self.datos:
                    eliminar_esp.append(self.mensaje[i])
                    
            if eliminar_db:
                
                for huella in eliminar_db:
                    self.cursor.execute(f"select id FROM huella WHERE Huella_1_P_D = {huella} or Huella_2_P_I = {huella} or Huella_3_I_D = {huella} or Huella_4_I_I = {huella} or Huella_5_M_D = {huella} or Huella_6_M_I = {huella}")
                    for i in self.cursor:
                        arreglo.append(i[0])
                    self.cursor.fetchall()
                for i in arreglo:
                    self.cursor.execute(f"delete from huella where id = {i}")
                    self.conn.commit()
                    self.cursor.fetchall

                print("Huellas eliminadas de la base de datos:", eliminar_db)
                
            elif eliminar_esp:
                url = "http://192.168.4.1/"
                command = "Eliminar"  # Comando para activar la suma

                for huella in eliminar_esp:
                    box_a = huella

                    data = {"command": command, "box_a": str(box_a)}
                    response = requests.post(url, data=data)

                    if response.status_code == 200:
                        # Recibe el ID como un entero
                        id_response = response.text
                        print("Huella eliminada del dispositivo NodeMCU con ID:", id_response)
                    else:
                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
        
        self.cursor.execute("select cargo.Id, huella.Huella_1_P_D, huella.Huella_2_P_I, huella.Huella_3_I_D, huella.Huella_4_I_I, huella.Huella_5_M_D, huella.Huella_6_M_I from cargo inner join usuario on cargo.ID = usuario.Cargo inner join huella on usuario.ID = huella.ID_Usuarios where huella.Huella_1_P_D > 0")
        datos = []
        # se asignan los resultados de la consulta a base de datos a un array
        for fila in self.cursor:
            datos.append(list(fila[0:]))
        self.cursor.fetchall()

        # Realizar la comparación y asignación en la primera columna de cada fila
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

        # Crear una matriz para almacenar los datos volteados
        matriz_volteada = []

        # Recorrer el array y guardar cada fila volteada en la matriz
        for fila in datos:
            for i in range(1, len(fila)):
                fila_matriz = []  # Crear una nueva fila vacía
                fila_matriz.append(fila[i])  # Agregar el elemento actual a la fila de la matriz
                fila_matriz.append(fila[0])  # Agregar el primer elemento a la fila de la matriz (columna 1 convertida en columna 2)
                matriz_volteada.append(fila_matriz)  # Agregar la fila completa volteada a la matriz

        print(matriz_volteada)

        url = "http://192.168.4.1/"
        command = "sql"  # Cambiado a "sql" en lugar de "Consultar"

        # Convertir la variable matriz en una cadena JSON
        array_data = json.dumps(matriz_volteada)

        # Agregar el comando y el array al diccionario de datos
        data = {"command": command, "array": array_data}
        response = requests.post(url, data=data)

        if response.status_code == 200:
            print("Respuesta del NodeMCU:", response.text)
        else:
            print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

        self.cursor.close()
        self.conn.close()

        

    def run(self):
        while True:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()
            # Aquí va el código de tu hilo
            mi_hilo2.pause()
            print("Ejecutando consulta...")
            self.hacer_consulta()
            mi_hilo2.resume()
            
            time.sleep(self.tiempo)  # Hacer una pausa de 2 segundos entre consultas
    
    def pause(self):
        with self.pause_cond:
            self.paused = True
            print("Hilo en pausa")

    def resume(self):
        with self.pause_cond:
            self.paused = False
            self.pause_cond.notify()
            print("Hilo reanudado")

# Crear una instancia del hilo
mi_hilo = MiHilo()

# Iniciar el hilo
mi_hilo.start()

##################################################################################################### CONEXION A LA BASE DE DATOS PARA LA CLASE PRINCIPAL
   

class ConexionBaseDatos:
    def __init__(self):
        self.conexion = None
        self.cursor = None


    def conectar(self):
            
        self.conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sistema_seguridad",
        port='3307'
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
        return self.cursor.fetchall()
        self.desconectar()
       

    def ejecutar_actualizacion(self, consulta, valores):
        self.conectar()
        self.cursor.execute(consulta, valores)
        self.conexion.commit()
        self.desconectar()

    def cerrar_conexion(self):
        self.cursor.close()
        self.conexion.close()

################################################################################### CLASE LISTA USUARIO ####################################################################################################


class Lista_Usuarios:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()

        self.frame_actual = None
        
        self.ventana = None
        
        self.tabla_resultados = ttk.Treeview(self.frame_actual, show="headings", selectmode="browse")
        self.tabla_resultados.pack()
        
        self.columnas = []
        self.resultados = []
        
        self.crear_tabla_usuario()
        self.cargar_datos_usuario()

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))
        
    def crear_tabla_usuario(self):
        self.cursor.execute("SELECT usuario.id as Id, usuario.cedula as Cedula, usuario.Nombres, usuario.Apellidos, cargo.Nombre_C as Cargo, usuario.contrasena as Contraseña FROM usuario inner join cargo on usuario.Cargo = cargo.ID")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()
        
    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None
        
    def cargar_datos_usuario(self):
        self.cursor.execute("SELECT usuario.id as Id, usuario.cedula as Cedula, usuario.Nombres, usuario.Apellidos, cargo.Nombre_C as Cargo, usuario.contrasena as Contraseña FROM usuario inner join cargo on usuario.Cargo = cargo.ID and usuario.estado > 0 order by usuario.id asc")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            self.tabla_resultados.insert('', tk.END, values=[resultado[i] if i < len(resultado) - 1 else '*' * len(str(resultado[i])) for i in range(len(resultado))])
            
        self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:]) - 1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]

        if columna > 0:
            if self.columnas[columna] == "Cargo":
                ventana_edicion = tk.Toplevel()
                ventana_edicion.title("Editar Campo")
                ventana_edicion.geometry("200x100")


                self.cursor.execute("Select Nombre_C from cargo")
                resultados = self.cursor.fetchall()

                # Obtener opciones
                opciones = [resultado[0] for resultado in resultados]

                etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
                etiqueta_valor_actual.pack()

                # Crear el combobox_cargo después de la etiqueta
                combobox_cargo = ttk.Combobox(ventana_edicion)
                combobox_cargo.pack()
                combobox_cargo.config(values=opciones)  # Mover esta línea después de crear el combobox

                entrada_valor_nuevo = combobox_cargo.get()

                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_usuario(valor_id, columna, entrada_valor_nuevo, combobox_cargo.get(), ventana_edicion))
                boton_guardar.pack()

            else:
                ventana_edicion = tk.Toplevel()
                ventana_edicion.title("Editar Campo")
                ventana_edicion.geometry("200x100")

                etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
                etiqueta_valor_actual.pack()

                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valor_actual)
                entrada_valor_nuevo.pack()
                combobox_cargo = entrada_valor_nuevo.get()
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_usuario(valor_id, columna, entrada_valor_nuevo.get(), combobox_cargo, ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def guardar_cambios_usuario(self, valor_id, columna, valor_nuevo, combobox_cargo , ventana_edicion):
        item = self.columnas[columna]
        registro = valor_id
        print(item)
        if item == "Cargo":
            print(combobox_cargo, valor_nuevo)
            if combobox_cargo:
                if combobox_cargo == "Gerente":
                    valor_nuevo = 2
                elif combobox_cargo == "Seguridad":
                    valor_nuevo = 6
                elif combobox_cargo == "Administrativo":
                    valor_nuevo = 3
                elif combobox_cargo == "Pasantes":
                    valor_nuevo = 7
                elif combobox_cargo == "Visita":
                    valor_nuevo = 8
                else:
                    valor_nuevo = 1
            else: 
                if valor_nuevo == "Gerente":
                    valor_nuevo = 2
                elif valor_nuevo == "Seguridad":
                    valor_nuevo = 6
                elif valor_nuevo == "Administrativo":
                    valor_nuevo = 3
                elif valor_nuevo == "Pasantes":
                    valor_nuevo = 7
                elif valor_nuevo == "Visita":
                    valor_nuevo = 8
                else:
                    valor_nuevo = 1
            print(valor_nuevo)
        if item == "Contraseña":
            item = "contrasena"
        consulta = f"UPDATE usuario SET {item} = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_usuario()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_usuario(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_usuario()
        self.cursor.fetchall()

    def editar_registro_usuario(self):
        item = self.tabla_resultados.focus()
        
        if item:
            ventana_edicion = ttk.Toplevel()
            
            valores_actuales = self.tabla_resultados.item(item)['values']
            
            for i in range(len(valores_actuales)):
                etiqueta_valor_actual = tk.Label(ventana_edicion, text=f"{self.columnas[i]}:")
                etiqueta_valor_actual.pack()
                
                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valores_actuales[i+1])
                entrada_valor_nuevo.pack()
                
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda i=i: self.guardar_cambios_usuario(valores_actuales[0], i, entrada_valor_nuevo.get(), ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def eliminar_registro_usuario(self):
        item = self.tabla_resultados.focus()
        
        if item:
            
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    self.cursor.execute(f"UPDATE usuario SET estado = 0 WHERE id = {registro_id}")
                    self.conn.commit()
                    self.tabla_resultados.delete(item)
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()
 
################################################################################# CLASE LISTA HUELLAS #####################################################################################################

class Lista_huella:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_huella()
        self.cargar_datos_huella()

        #No tocar
        mi_hilo2 = MiHilo2()
        mi_hilo = MiHilo()

        # Iniciar el hilo     

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))

    def crear_tabla_huella(self):
        self.cursor.execute("SELECT huella.ID, usuario.Nombres as Nombre, huella.Huella_1_P_D as 'huella 1', huella.Huella_2_P_I as 'huella 2', huella.Huella_3_I_D as 'huella 3', huella.Huella_4_I_I as 'huella 4', huella.Huella_5_M_D as 'huella 5', huella.Huella_6_M_I as 'huella 6' FROM huella inner join usuario on huella.ID_Usuarios = usuario.ID where usuario.Estado > 0")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)
        for col in self.tabla_resultados['columns']:

            self.tabla_resultados.column(col, width=100)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def cargar_datos_huella(self):
        self.cursor.execute("SELECT huella.ID, usuario.Nombres as Nombre, huella.Huella_1_P_D as 'huella 1', huella.Huella_2_P_I as 'huella 2', huella.Huella_3_I_D as 'huella 3', huella.Huella_4_I_I as 'huella 4', huella.Huella_5_M_D as 'huella 5', huella.Huella_6_M_I as 'huella 6' FROM huella inner join usuario on huella.ID_Usuarios = usuario.ID where usuario.Estado > 0")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:])-1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]
        if columna > 1:
            ventana_edicion = tk.Toplevel()
            ventana_edicion.title("Editar Campo")
            ventana_edicion.geometry("200x100")

            etiqueta_valor_actual = tk.Label(ventana_edicion, text="Huella actual:")
            etiqueta_valor_actual.pack()

            etiqueta_valor = tk.Label(ventana_edicion, text="huella :" + str(valor_actual))
            etiqueta_valor.pack()
            
            boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_huella(valor_id, columna, valor_nuevo, ventana_edicion))
            boton_guardar.pack()

            mi_hilo2.pause()
            mi_hilo.pause()

            url = "http://192.168.4.1/"
            command = "Eliminar"  #comando eliminar
            box_a = valor_actual

            data = {"command": command, "box_a": str(box_a)}
            response = requests.post(url, data=data)

            if response.status_code == 200:

                print("Huella eliminada con ID:", response)
                
                command = "Registrar"  # Comando para activar el registro de huellas
                data = {"command": command}

                response = requests.post(url, data=data)

                # Verifica si la solicitud fue exitosa (código de estado 200)
                if response.status_code == 200:
                    # Recibe el ID como un entero
                    id_response = response.text
                    print("Regisro", id_response)
                    valor_nuevo = id_response
                else:
                    print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                    
            else:

                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

            mi_hilo2.resume()
            mi_hilo.resume()
            
        self.cursor.fetchall()

    def guardar_cambios_huella(self, valor_id, columna, valor_nuevo, ventana_edicion):
            
        item = self.columnas[columna]
        
        if item == "huella 1":
            item = "Huella_1_P_D"
        elif item == "huella 2":
            item = "Huella_2_P_I"
        elif item == "huella 3":
            item = "Huella_3_I_D"
        elif item == "huella 4":
            item = "Huella_4_I_I"
        elif item == "Huella 5":
            item = "Huella_5_M_D"
        elif item == "Huella 6":
            item = "Huella_6_M_I"

        registro = valor_id

        consulta = f"UPDATE huella SET {item} = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_huella()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_huella(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_huella()
        self.cursor.fetchall()


    def eliminar_registro_huella(self):
        item = self.tabla_resultados.focus()
        
        if item:
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    mi_hilo2.pause()
                    mi_hilo.pause()
                    url = "http://192.168.4.1/"
                    command = "Eliminar"  # Comando para activar la suma

                    
                    for i in range(6):
                        i+1
                        registro = self.tabla_resultados.item(item)['values'][2+i]
                        box_a = registro

                        data = {"command": command, "box_a": str(box_a)}
                        response = requests.post(url, data=data)

                        if response.status_code == 200:
                            # Recibe el ID como un entero
                            id_response = response.text
                            print("Huella eliminada con ID:", id_response)
                        else:
                            print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                    
                    self.cursor.execute(f"delete from huella WHERE id = {registro_id}")
                    self.conn.commit()
                    self.tabla_resultados.delete(item)

                    messagebox.showinfo("Huellas Eliminadas", "Ya todas las huellas fueron eliminadas")
                    mi_hilo2.resume()
                    mi_hilo.resume()
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:       
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()

################################################################################### CLASE LISTA ZONA #######################################################################################################

class Lista_Zona:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_zona()
        self.cargar_datos_zona()

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))

        

    def crear_tabla_zona(self):
        self.cursor.execute("SELECT ID, NOMBRE FROM zona")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")
        

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def cargar_datos_zona(self):
        self.cursor.execute("SELECT id, nombre FROM zona WHERE ESTADO > 0")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:])-1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]
        if columna > 0:
            ventana_edicion = tk.Toplevel()
            ventana_edicion.title("Editar Campo")
            ventana_edicion.geometry("200x100")

            etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
            etiqueta_valor_actual.pack()

            entrada_valor_nuevo = tk.Entry(ventana_edicion)
            entrada_valor_nuevo.insert(0, valor_actual)
            entrada_valor_nuevo.pack()

            boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_zona(valor_id, columna, entrada_valor_nuevo.get(), ventana_edicion))
            boton_guardar.pack()
        self.cursor.fetchall()

    def guardar_cambios_zona(self, valor_id, columna, valor_nuevo, ventana_edicion):
        item = self.columnas[columna]
        registro = valor_id

        consulta = f"UPDATE zona SET {item} = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_zona()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_zona(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_zona()
        self.cursor.fetchall()

    def editar_registro_zona(self):
        item = self.tabla_resultados.focus()
        
        if item:
            ventana_edicion = tk.Toplevel()
            
            valores_actuales = self.tabla_resultados.item(item)['values']
            
            for i in range(len(valores_actuales)):
                etiqueta_valor_actual = tk.Label(ventana_edicion, text=f"{self.columnas[i]}:")
                etiqueta_valor_actual.pack()
                
                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valores_actuales[i+1])
                entrada_valor_nuevo.pack()
                
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda i=i: self.guardar_cambios_zona(valores_actuales[0], i, entrada_valor_nuevo.get(), ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def eliminar_registro_zona(self):
        item = self.tabla_resultados.focus()
        
        if item:
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    self.cursor.execute(f"UPDATE zona SET estado = 0 WHERE id = %s", (registro_id,))
                    self.conn.commit()
                    self.tabla_resultados.delete(item)
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()

################################################################################# CLASE LISTA SENSORES ###################################################################################################

class Lista_sensores:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_sensores()
        self.cargar_datos_sensores()

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))

    def crear_tabla_sensores(self):
        self.cursor.execute("select SENSOR.ID,	zona.Nombre as 'Nombre de la zona', sensor.Especificacion as Detalles from sensor inner join zona on sensor.Id_Zona = zona.ID")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def cargar_datos_sensores(self):
        self.cursor.execute("select SENSOR.ID,	zona.Nombre as 'Nombre de la zona', sensor.Especificacion as Detalles from sensor inner join zona on sensor.Id_Zona = zona.ID where sensor.estado > 0")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:])-1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]
        if columna > 1:
            ventana_edicion = tk.Toplevel()
            ventana_edicion.title("Editar Campo")
            ventana_edicion.geometry("200x100")

            etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
            etiqueta_valor_actual.pack()

            entrada_valor_nuevo = tk.Entry(ventana_edicion)
            entrada_valor_nuevo.insert(0, valor_actual)
            entrada_valor_nuevo.pack()

            boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_sensores(valor_id, columna, entrada_valor_nuevo.get(), ventana_edicion))
            boton_guardar.pack()
        self.cursor.fetchall()

    def guardar_cambios_sensores(self, valor_id, columna, valor_nuevo, ventana_edicion):
        item = self.columnas[columna]
        registro = valor_id
        
        consulta = f"UPDATE sensor SET Especificacion = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_sensores()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_sensores(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_sensores()
        self.cursor.fetchall()

    def editar_registro_sensores(self):
        item = self.tabla_resultados.focus()
        
        if item:
            ventana_edicion = tk.Toplevel()
            
            valores_actuales = self.tabla_resultados.item(item)['values']
            
            for i in range(len(valores_actuales)):
                etiqueta_valor_actual = tk.Label(ventana_edicion, text=f"{self.columnas[i]}:")
                etiqueta_valor_actual.pack()
                
                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valores_actuales[i+1])
                entrada_valor_nuevo.pack()
                
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda i=i: self.guardar_cambios_sensores(valores_actuales[0], i, entrada_valor_nuevo.get(), ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def eliminar_registro_sensores(self):
        item = self.tabla_resultados.focus()
        
        if item:
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    self.cursor.execute(f"update sensor set estado = 0 WHERE id = '{registro_id}'")
                    self.conn.commit()
                    self.tabla_resultados.delete(item)
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()

################################################################################# CLASE LISTA LECTORES ###################################################################################################

class Lista_lectores:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_lectores()
        self.cargar_datos_lectores()

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))

    def crear_tabla_lectores(self):
        self.cursor.execute("select puerta.ID, zona.Nombre as 'Nombre de la Zona', puerta.Nombre as 'Descripción de la puerta' from puerta inner join zona on puerta.ID_Zona = zona.ID")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def cargar_datos_lectores(self):
        self.cursor.execute("select puerta.ID, zona.Nombre as 'Nommbre de la Zona', puerta.Nombre as 'Descripción de la puerta' from puerta inner join zona on puerta.ID_Zona = zona.ID where puerta.estado > 0 and zona.Estado > 0")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:])-1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]
        if columna > 1:
            ventana_edicion = tk.Toplevel()
            ventana_edicion.title("Editar Campo")
            ventana_edicion.geometry("200x100")

            etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
            etiqueta_valor_actual.pack()

            entrada_valor_nuevo = tk.Entry(ventana_edicion)
            entrada_valor_nuevo.insert(0, valor_actual)
            entrada_valor_nuevo.pack()

            boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_lectores(valor_id, columna, entrada_valor_nuevo.get(), ventana_edicion))
            boton_guardar.pack()
        self.cursor.fetchall()

    def guardar_cambios_lectores(self, valor_id, columna, valor_nuevo, ventana_edicion):
        item = self.columnas[columna]
        registro = valor_id
        if item == "Descripción de la puerta":
            item = "Nombre"
        consulta = f"UPDATE puerta SET {item} = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_lectores()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_lectores(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_lectores()
        self.cursor.fetchall()

    def editar_registro_lectores(self):
        item = self.tabla_resultados.focus()
        
        if item:
            ventana_edicion = tk.Toplevel()
            
            valores_actuales = self.tabla_resultados.item(item)['values']
            
            for i in range(len(valores_actuales)):
                etiqueta_valor_actual = tk.Label(ventana_edicion, text=f"{self.columnas[i]}:")
                etiqueta_valor_actual.pack()
                
                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valores_actuales[i+1])
                entrada_valor_nuevo.pack()
                
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda i=i: self.guardar_cambios_lectores(valores_actuales[0], i, entrada_valor_nuevo.get(), ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def eliminar_registro_lectores(self):
        item = self.tabla_resultados.focus()
        
        if item:
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    self.cursor.execute(f"update puerta set estado = 0 WHERE id = '{registro_id}'")
                    self.conn.commit()
                    self.tabla_resultados.delete(item)
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()

################################################################################## CLASE LISTA ALERTAS ###################################################################################################

class Lista_alertas:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_alerta()
        self.cargar_datos_alerta()

    def crear_tabla_alerta(self):
        self.cursor.execute("select alerta.Tipo as 'Tipo de alerta', usuario.Nombres as 'Usuario', puerta.Nombre as 'Identificacion de Puerta', sensor.Especificacion as 'Identificación de Sensor', alerta_usuario.fecha as 'fecha', alerta_usuario.hora as 'Hora' from alerta_usuario left join alerta on alerta_usuario.id_alerta = alerta.Id left join usuario on alerta_usuario.id_usuario = usuario.ID left join puerta on alerta_usuario.id_puerta = puerta.ID left join sensor on alerta_usuario.id_sensor = sensor.Id")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def actualizar_tabla_alerta(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_alerta()
        self.cursor.fetchall()

    def cargar_datos_alerta(self):
        self.cursor.execute("select alerta.Tipo as 'Tipo de alerta', usuario.Nombres as 'Usuario', puerta.Nombre as 'Identificacion de Puerta', sensor.Especificacion as 'Identificación de Sensor', alerta_usuario.fecha as 'Fecha', alerta_usuario.hora as 'Hora' from alerta_usuario left join alerta on alerta_usuario.id_alerta = alerta.Id left join usuario on alerta_usuario.id_usuario = usuario.ID left join puerta on alerta_usuario.id_puerta = puerta.ID left join sensor on alerta_usuario.id_sensor = sensor.Id order by hora desc")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()
            
################################################################################### CLASE LISTA CARGOS ###################################################################################################

class Lista_permisos:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_permisos()
        self.cargar_datos_permisos()

        self.tabla_resultados.bind("<Double-1>", lambda event: self.cell_editing(event))

    def crear_tabla_permisos(self):
        self.cursor.execute("SELECT ID, nombre_c as 'Cargo', Descripcion from cargo")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def cargar_datos_permisos(self):
        self.cursor.execute("SELECT ID, nombre_c as 'Cargo', Descripcion from cargo")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

    def cell_editing(self, event):
        item = self.tabla_resultados.selection()[0]
        columna = int(self.tabla_resultados.identify_column(event.x)[1:])-1
        valor_actual = self.tabla_resultados.item(item)['values'][columna]
        valor_id = self.tabla_resultados.item(item)['values'][0]
        if columna > 0:
            ventana_edicion = tk.Toplevel()
            ventana_edicion.title("Editar Campo")
            ventana_edicion.geometry("200x100")

            etiqueta_valor_actual = tk.Label(ventana_edicion, text="Valor actual:")
            etiqueta_valor_actual.pack()

            entrada_valor_nuevo = tk.Entry(ventana_edicion)
            entrada_valor_nuevo.insert(0, valor_actual)
            entrada_valor_nuevo.pack()

            boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda: self.guardar_cambios_permisos(valor_id, columna, entrada_valor_nuevo.get(), ventana_edicion))
            boton_guardar.pack()
        self.cursor.fetchall()

    def guardar_cambios_permisos(self, valor_id, columna, valor_nuevo, ventana_edicion):
        item = self.columnas[columna]
        registro = valor_id

        consulta = f"UPDATE cargo SET {item} = %s WHERE id = %s"
        valores = (valor_nuevo, registro)
        
        try:
            self.cursor.execute(consulta, valores)
            self.conn.commit()
            self.actualizar_tabla_permisos()
            ventana_edicion.destroy()
        except mysql.connector.Error as error:
            print("Error al actualizar la base de datos:", error)
        self.cursor.fetchall()

    def actualizar_tabla_huella(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_permisos()
        self.cursor.fetchall()

    def editar_registro_permisos(self):
        item = self.tabla_resultados.focus()
        
        if item:
            ventana_edicion = tk.Toplevel()
            
            valores_actuales = self.tabla_resultados.item(item)['values']
            
            for i in range(len(valores_actuales)):
                etiqueta_valor_actual = tk.Label(ventana_edicion, text=f"{self.columnas[i]}:")
                etiqueta_valor_actual.pack()
                
                entrada_valor_nuevo = tk.Entry(ventana_edicion)
                entrada_valor_nuevo.insert(0, valores_actuales[i+1])
                entrada_valor_nuevo.pack()
                
                boton_guardar = tk.Button(ventana_edicion, text="Guardar", command=lambda i=i: self.guardar_cambios_permisos(valores_actuales[0], i, entrada_valor_nuevo.get(), ventana_edicion))
                boton_guardar.pack()
        self.cursor.fetchall()

    def eliminar_registro_permisos(self):
        item = self.tabla_resultados.focus()
        
        if item:
            registro = self.tabla_resultados.item(item)['values'][0]
            respuesta = messagebox.askquestion("Eliminar registro", "¿Estás seguro de que deseas eliminar este registro?")
            
            if respuesta == 'yes':
                registro_id = self.tabla_resultados.item(item)['values'][0]
                try:
                    self.cursor.execute(f"CALL eliminar_cargo(%s,%s)", (registro_id, registro_id))
                    self.conn.commit()
                    self.tabla_resultados.delete(item)
                except mysql.connector.Error as error:
                    print("Error al eliminar el registro:", error)
        else:
            messagebox.showinfo("Selección", "Seleccione un registro para eliminar")
        self.cursor.fetchall()

############################################################################### CLASE LISTA MODIFICACIONES ###############################################################################################

class Lista_modificaciones:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_modificaciones()
        self.cargar_datos_modificaciones()

    def crear_tabla_modificaciones(self):
        self.cursor.execute("select historial_ingresos.id_historial as ID, historial_ingresos.Fecha, historial_ingresos.hora as Hora, historial_ingresos.Tabla_Editada, historial_ingresos.Accion, usuario.Nombres as 'Usuario' from historial_ingresos left join ingresos_sistema on historial_ingresos.Id_ingreso = ingresos_sistema.Id_ingreso left join usuario on ingresos_sistema.Id_usuario = usuario.ID order by ID desc")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def actualizar_tabla_modificaciones(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_modificaciones()
        self.cursor.fetchall()

    def cargar_datos_modificaciones(self):
        self.cursor.execute("select historial_ingresos.id_historial as ID, historial_ingresos.Fecha, historial_ingresos.hora as Hora, historial_ingresos.Tabla_Editada, historial_ingresos.Accion, usuario.Nombres as 'Usuario' from historial_ingresos left join ingresos_sistema on historial_ingresos.Id_ingreso = ingresos_sistema.Id_ingreso left join usuario on ingresos_sistema.Id_usuario = usuario.ID order by ID desc")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()

################################################################################## CLASE LISTA ENTRADAS ##################################################################################################

class Lista_entradas:
    def __init__(self):
        self.conn = mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            database='sistema_seguridad',
            port='3307'
        )
        self.cursor = self.conn.cursor()
        item = 0
    
        self.frame_actual = None
        
        self.ventana = None

        self.tabla_resultados = ttk.Treeview(self.ventana, show="headings", selectmode="browse")
        self.tabla_resultados.pack()

        self.columnas = []
        self.resultados = []

        self.crear_tabla_entradas()
        self.cargar_datos_entradas()

    def crear_tabla_entradas(self):
        self.cursor.execute("select ingresos_sistema.Id_ingreso, usuario.Nombres as 'Usuario', ingresos_sistema.fecha as Fecha, ingresos_sistema.hora as Hora from ingresos_sistema inner join usuario on ingresos_sistema.Id_usuario = usuario.ID order by ingresos_sistema.Id_ingreso desc")
        self.columnas = [desc[0] for desc in self.cursor.description]
        self.tabla_resultados['columns'] = self.columnas
        self.tabla_resultados.column("#0", width=0, stretch=tk.NO)

        style = ttk.Style()
        style.configure("Treeview.Heading", anchor="w")

        for columna in self.columnas:
            self.tabla_resultados.heading(columna, text=columna)
        self.cursor.fetchall()

    def limpiar_instancia(self):
        if self.tabla_resultados:
            self.tabla_resultados.destroy()
            self.tabla_resultados = None
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        if self.frame_actual:
            self.frame_actual.destroy()
            self.frame_actual = None
        if self.ventana:
            self.ventana.destroy()
            self.ventana = None

    def actualizar_tabla_entradas(self):
        for fila in self.tabla_resultados.get_children():
            self.tabla_resultados.delete(fila)

        self.cargar_datos_entradas()
        self.cursor.fetchall()

    def cargar_datos_entradas(self):
        self.cursor.execute("select ingresos_sistema.Id_ingreso, usuario.Nombres as 'Usuario', ingresos_sistema.fecha as Fecha, ingresos_sistema.hora as Hora from ingresos_sistema inner join usuario on ingresos_sistema.Id_usuario = usuario.ID order by ingresos_sistema.Id_ingreso desc")
        self.resultados = self.cursor.fetchall()
        for resultado in self.resultados:
            values = resultado[0:]
            self.tabla_resultados.insert('', tk.END, values=values)

            self.cursor.fetchall()
        
################################################################################ CLASE VENTANA PRINCIPAL ###################################################################################################

class VentanaPrincipal:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Sistema de Seguridad")
        screen = screeninfo.get_monitors()[0]
        width, height = screen.width, screen.height
        self.ventana.geometry("%dx%d+0+0"%(width, height))
        self.ventana.configure(bg="#000000")
    
        self.lista = None
        self.formulario = None

        mi_hilo = MiHilo()
        mi_hilo2 = MiHilo2()
        activar_pir = pir()
        

        # Crear un estilo personalizado para ttk
        estilo = ttk.Style()
        estilo.theme_use("clam") 

        # Cambiar la paleta de colores a azul
        estilo.configure("TFrame", background="#000000")
        estilo.configure("TButton", relief="flat", background="#1D6B70", foreground="7B68EE")
        estilo.configure("TLabel", background="#000000", foreground="#FFFFFF")
        # Configurar estilo para TCombobox
        estilo.configure("TCombobox", fieldbackground="#303232", background="#303232")

        # Configurar estilo para TCombobox.TEntry
        estilo.configure("TCombobox.TEntry", borderwidth=2, relief="solid", highlightthickness=1)                                                           #background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=3
        self.frame_actual = None

        # Crear la conexión a la base de datos
        self.conexion_bd = ConexionBaseDatos()

        # Crear el frame inicial
        self.mostrar_frame_login()

###################################### FRAME LOGIN
        
    def mostrar_frame_login(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
        
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de inicio de sesión...

        etiqueta_titulo = tk.Label(self.frame_actual, text="INICIAR SESION", background="#000000", fg="#FFFFFF", font=("impact", 40))
        etiqueta_titulo.pack(pady=80)
        
        
        etiqueta_usuario = ttk.Label(self.frame_actual, text="Usuario:", font=("impact", 12))
        etiqueta_usuario.pack(pady=10)
        
        self.entrada_usuario = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entrada_usuario.pack()
        
        etiqueta_contrasena = ttk.Label(self.frame_actual, text="Contraseña:", font=("impact", 12))
        etiqueta_contrasena.pack(pady=10)
        
        self.entrada_contrasena = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2 , show="*")
        self.entrada_contrasena.pack() 
        
        boton_iniciar_sesion = tk.Button(self.frame_actual,text="Acceder",relief="flat", background="#1D6B70", fg="#FFFFFF", width=15, height=1, highlightbackground="red", command=self.iniciar_sesion) #self.iniciar_sesion ese es el comand que deberia ir OJO self.mostrar_frame_gestion_usuarios
        boton_iniciar_sesion.pack(pady=15) 

        boton_activar_pir = tk.Button(self.frame_actual,text="Encender PIR",relief="flat", background="#1D6B70", fg="#FFFFFF", width=15, height=1, highlightbackground="red", command=activar_pir.activar_pir) #self.iniciar_sesion ese es el comand que deberia ir OJO self.mostrar_frame_gestion_usuarios
        boton_activar_pir.pack(pady=15)

        self.frame_actual.pack(padx=70, pady=20)
        
    def iniciar_sesion(self):
        usuario = self.entrada_usuario.get()
        contrasena = self.entrada_contrasena.get()
        
        # Verificar el usuario y contraseña en la base de datos
        consulta = "CALL login(%s, %s); COMMIT;"
        valores = (usuario, contrasena)
        resultado = self.conexion_bd.ejecutar_consulta(consulta, valores)
            
        if resultado:
            # Si el usuario y contraseña son correctos, mostrar el menú principal
            self.mostrar_frame_menu_principal()
        else:
            # Si el usuario y contraseña son incorrectos, mostrar un mensaje de error
            usuario = ""
            contrasena = ""
            mensaje_error = "Usuario o contraseña incorrectos"
            etiqueta_error = ttk.Label(self.frame_actual, text=mensaje_error,background="#000000", foreground="red")
            etiqueta_error.pack()

############################################ FRAME MENU PRINCIPAL

    def mostrar_frame_menu_principal(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()

        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame del menú principal...
        
        etiqueta_titulo = ttk.Label(self.frame_actual, text="Menú principal", font=("impact", 20))
        etiqueta_titulo.pack(pady=50)

        #boton ver usuarios
        boton_usuarios = tk.Button(self.frame_actual, text="Usuarios", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_gestion_usuarios)
        boton_usuarios.pack(pady=10)

        #boton ver zonas
        boton_zonas = tk.Button(self.frame_actual, text="Zonas",  font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_gestion_zonas)
        boton_zonas.pack(pady=10)

        #boton ver permisos
        boton_permisos = tk.Button(self.frame_actual, text="Permisos", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_gestion_permisos)
        boton_permisos.pack(pady=10)

        #boton ver alertas
        boton_alertas = tk.Button(self.frame_actual, text="Alertas", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_gestion_alertas)
        boton_alertas.pack(pady=10)

        #boton ver modificaciones al sistema
        boton_modificaciones = tk.Button(self.frame_actual, text="Modificaciones", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_modificaciones)
        boton_modificaciones.pack(pady=10)

        #boton ver entradas
        boton_entradas = tk.Button(self.frame_actual, text="Entradas", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_entradas)
        boton_entradas.pack(pady=10)

        #boton de cerrar sesion
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(pady=10)
        
        self.frame_actual.pack(padx=100, pady=30)
        
############################################# FRAME GESTION DE USUARIO
        
    def mostrar_frame_gestion_usuarios(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Código para mostrar la gestión de usuarios...
        self.frame_actual.pack(padx=20, pady=20)

        #Se crea la instancia de la clase lista usuarios
        self.lista = Lista_Usuarios()
        
        etiqueta_titulo =ttk.Label(self.frame_actual, text="Gestión de usuarios", font=("impact", 15))
        etiqueta_titulo.pack()

        #boton agregar usuario
        boton_agregar_usuario = tk.Button(self.frame_actual, text="Registrar Usuario", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1,  command=self.mostrar_frame_agregar_usuario)
        boton_agregar_usuario.pack(side="left",fill="none", padx=10, pady=50)

        #boton eliminar usuario
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Usuario", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF",width=20, height=1, command=self.lista.eliminar_registro_usuario)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=80)

        #boton ver huellas
        boton_ver_huellas = tk.Button(self.frame_actual, text="Ver Huellas", font=("impact", 10),relief="flat", background="#1D6B70", fg="#FFFFFF", width=20, height=1, command=self.mostrar_frame_gestion_huellas)
        boton_ver_huellas.pack(side="left",fill="none", padx=80, pady=50)
        
        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10),relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF",command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=10, pady=50)

        #Código boton de cerrar sesion
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)


#################################################### FRAME AGREGAR USUARIO

    def mostrar_frame_agregar_usuario(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
        
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...

        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Usuario", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)
        
        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)
        
        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre = ttk.Label(self.frame_actual, text="Nombres:")
        self.etiqueta_nombre.pack()
        self.entry_nombre = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_nombre.pack()

        self.etiqueta_apellido = ttk.Label(self.frame_actual, text="Apellidos:")
        self.etiqueta_apellido.pack()
        self.entry_apellido = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_apellido.pack()

        self.etiqueta_cedula = ttk.Label(self.frame_actual, text="Cedula:")
        self.etiqueta_cedula.pack()
        self.entry_cedula = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_cedula.pack()

        self.etiqueta_cargo = ttk.Label(self.frame_actual, text="Cargo:")
        self.etiqueta_cargo.pack()
        self.combobox_cargo = ttk.Combobox(self.frame_actual, style="TCombobox")
        self.combobox_cargo.pack()

        self.etiqueta_contrasena = ttk.Label(self.frame_actual, text="Contraseña:")
        self.etiqueta_contrasena.pack()
        self.entry_contrasena = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_contrasena.pack()

        self.etiqueta_confirmar_contrasena = ttk.Label(self.frame_actual, text="Confirmar Contraseña")
        self.etiqueta_confirmar_contrasena.pack()
        self.entry_confirmar_contrasena = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_confirmar_contrasena.pack()


        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port="3307"
        )
        self.cursor = self.conn.cursor()
        self.obtener_opciones()

        # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_usuario)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)

         #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), width=20,relief="flat", height=1, background="#1D6B70", fg="#FFFFFF",command=self.mostrar_frame_gestion_usuarios)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF",command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)
        
    def obtener_opciones(self):
        self.cursor.execute("Select Nombre_C from cargo")
        resultados = self.cursor.fetchall()

        #obtener opciones
        opciones = [resultado[0] for resultado in resultados]
        self.combobox_cargo.config(values=opciones)

    def registrar_usuario(self):
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        cedula = self.entry_cedula.get()
        cargo = self.combobox_cargo.get()
        contrasena = self.entry_contrasena.get()
        confirmar_contrasena = self.entry_confirmar_contrasena.get()

        # Verificar que los campos no estén vacíos
        if nombre and apellido and cedula and cargo and contrasena and confirmar_contrasena:
            if contrasena == confirmar_contrasena:
                usuario_existe=[]
                activar_usuario = []

                self.cursor.execute(f"SELECT cedula FROM usuario where estado > 0")
                for fila in self.cursor:
                    usuario_existe.append(fila[0])
                self.cursor.fetchall()

                self.cursor.execute(f"SELECT cedula FROM usuario where estado = 0")
                for fila in self.cursor:
                    activar_usuario.append(fila[0])
                self.cursor.fetchall()

                print(usuario_existe)

                if not cedula in usuario_existe and cedula not in activar_usuario:

                    try:
                        self.cursor.execute(f"SELECT ID FROM CARGO WHERE Nombre_C = '{cargo}'")
                        cargo = self.cursor.fetchall()
                        cargo = cargo[0][0]
                    except:
                        messagebox.showerror("Error entrada invalida", "Seleccione un cargo de la lista")
                    try:
                        # Insertar el nuevo usuario en la tabla usuarios
                        self.cursor.execute("INSERT INTO usuario VALUES (null, %s, %s, %s, %s, %s, 1)", (cedula, nombre, apellido, cargo, contrasena))
                        self.conn.commit()
                        self.cursor.fetchall()
                        messagebox.showinfo("Registro exitoso", "El usuario ha sido registrado correctamente")
                        self.limpiar_campos_usuario()
                    except mysql.connector.Error as error:
                        print("Error al registrar el usuario:", error)
                        messagebox.showerror("Error", "No se pudo registrar el usuario")
                        
                elif cedula in activar_usuario:
                    self.cursor.execute(f"UPDATE usuario SET estado = 1, contrasena = %s where cedula = %s ", (contrasena, cedula))
                    self.conn.commit()
                    messagebox.showinfo("Registro exitoso", "El usuario ha sido registrado Nuevamente")
                    self.limpiar_campos_usuario()
                else:
                    messagebox.showwarning("Usuario Existente", "El usuario ya esta registrado en la base de datos")
            else:
                messagebox.showwarning("Contraseña no coincide", "Por favor, complete asegurece de ingresar conrrectamente la contrasena")
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos")
    def limpiar_campos_usuario(self):
        self.entry_nombre.delete(0, tk.END)
        self.entry_apellido.delete(0, tk.END)
        self.entry_cedula.delete(0, tk.END)
        self.combobox_cargo.delete(0, tk.END)
        self.entry_contrasena.delete(0, tk.END)
        self.entry_confirmar_contrasena.delete(0, tk.END)
        
############################################### FRAME GESTION HUELLAS
        
    def mostrar_frame_gestion_huellas(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
        # Reanudar el hilo 
        mi_hilo.resume()
        mi_hilo2.resume()

        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión Huellas", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)

        #Se crea la instancia de la clase lista huellas
        self.lista = Lista_huella()

        #Código de Boton agregar huellas
        boton_agregar_huellas = tk.Button(self.frame_actual, text="Agregar Huellas", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_agregar_huellas)
        boton_agregar_huellas.pack(side="left",fill="none", padx=10, pady=50)

        #Boton eliminar huella
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Huella", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.eliminar_registro_huella)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_usuarios)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)

        #Código de Boton de volver a menú
        boton_volver_menu = tk.Button(self.frame_actual, text="Volver a Menú", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF",  command=self.mostrar_frame_menu_principal)
        boton_volver_menu.pack(side="left",fill="none", padx=10, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

############################################## FRAME AGREGAR HUELLAS
        
    def mostrar_frame_agregar_huellas(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
          
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Huellas", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...
        
        self.frame_actual.pack(padx=20, pady=80)

        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre = ttk.Label(self.frame_actual, text="Nombre :")
        self.etiqueta_nombre.pack()
        self.entry_nombre = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_nombre.pack()
        

        # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_huella)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)

         #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10),  width=20,relief="flat", height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_huellas)
        boton_volver.pack(side="left",fill="none", padx=10, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)


        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port='3307'
        )
        self.cursor = self.conn.cursor()

    def registrar_huella(self):
        
        nombre = self.entry_nombre.get()
        self.cursor.execute("SELECT Nombres FROM usuario where estado > 0")
        validar = [] 
        for fila in self.cursor:
            validar.append(fila[0])
        print(validar)

        if nombre: 
            if nombre in validar:
                try:
                    # Detener temporalmente el hilo durante 5 segundos
                    mi_hilo.pause()
                    mi_hilo2.pause()
        
                    url = "http://192.168.4.1/"
                    command = "Registrar"
                    messagebox.showinfo("Escaneando", "Por favor atento, se va a activar el lector de huellas")
        
                    for i in range(6):
                        data = {"command": command}
                        response = requests.post(url, data=data)
                    
                        if response.status_code == 200:
                            id_response = response.text
                            print("huella", i + 1, "registrada con ID:", id_response)

                            if i == 0:

                                id_1 = id_response
                            
                                if len(id_1) < 4:
                                    messagebox.showinfo("Escaneado", "Primera Huella escaneada correctamente")
                                else:
                                    while len(id_1) >=4:
                                        print(id_1)
                                        messagebox.showerror("Error 1", id_1)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_1 = id_response
                                    messagebox.showinfo("Escaneado", "Primera Huella escaneada correctamente")
                                    

                            elif i == 1:
                                id_2 = id_response
                                if len(id_2) < 4:
                                    messagebox.showinfo("Escaneado", "Segunda Huella escaneada correctamente")
                                else:
                                    while len(id_2) > 4:
                                        messagebox.showerror("Error 2", id_2)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_2 = id_response
                                    messagebox.showinfo("Escaneado", "Segunda Huella escaneada correctamente")
                                
                            elif i == 2:
                                id_3 = id_response
                                if len(id_3) < 4:
                                    messagebox.showinfo("Escaneado", "Tercera Huella escaneada correctamente")
                                else:
                                    while len(id_3) > 4:
                                        messagebox.showerror("Error 3", id_3)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_3 = id_response
                                    messagebox.showinfo("Escaneado", "Tercera Huella escaneada correctamente")

                            elif i == 3:
                                id_4 = id_response
                                if len(id_4) < 4:
                                    messagebox.showinfo("Escaneado", "Cuarta Huella escaneada correctamente")
                                else:
                                    while len(id_4) > 4:
                                        messagebox.showerror("Error 4", id_4)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_4 = id_response
                                    messagebox.showinfo("Escaneado", "Cuarta Huella escaneada correctamente")

                            elif i == 4:
                                id_5 = id_response
                                if len(id_5) < 4:
                                    messagebox.showinfo("Escaneado", "Quinta Huella escaneada correctamente")
                                else:
                                    while len(id_5) > 4:
                                        messagebox.showerror("Error 5", id_5)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_5 = id_response
                                    messagebox.showinfo("Escaneado", "Quinta Huella escaneada correctamente")

                            elif i == 5:
                                id_6 = id_response
                                if len(id_6) < 4:
                                    messagebox.showinfo("Escaneado", "Sexta Huella escaneada correctamente")
                                else:
                                    while len(id_6) > 4:
                                        messagebox.showerror("Error 6", id_6)
                                        data = {"command": command}
                                        response = requests.post(url, data=data)
                                        id_response = response.text
                                        id_6 = id_response
                                    messagebox.showinfo("Escaneado", "Sexta Huella escaneada correctamente")
        
                        else:
                            print("error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            messagebox.showerror("Error", id_response)
                            mi_hilo.resume()
                            mi_hilo2.resume()

                        # Verificar que los campos no estén vacíos
            
                    if id_6:
                        try:
                            self.cursor.execute(f"SELECT ID FROM usuario WHERE Nombres = '{nombre}'")
                            nombre = self.cursor.fetchall()
                            nombre = nombre[0][0]
                            try:
                                # Insertar el nuevo usuario en la tabla usuarios
                                self.cursor.execute("INSERT INTO huella VALUES (null, %s, %s, %s, %s, %s, %s, %s)", (nombre, id_1, id_2, id_3, id_4, id_5, id_6))
                                self.conn.commit()
                                messagebox.showinfo("Registro exitoso", "Las huellas han sido registradas correctamente")
                                self.limpiar_campos_huella()
                                # Reanudar el hilo 
                                mi_hilo.resume()
                                mi_hilo2.resume()

                            except mysql.connector.Error as error:
                                print("Error al registrar las Huellas:", error)

                                command = "Eliminar"  # Comando para activar la suma

                                if id_1:
                                    box_a = id_1

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                                if id_2:
                                    box_a = id_2

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                                if id_3:
                                    box_a = id_3

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                                if id_4:
                                    box_a = id_4

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

                                if id_5:
                                    box_a = id_5

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

                                if id_6:
                                    box_a = id_6

                                    data = {"command": command, "box_a": str(box_a)}
                                    response = requests.post(url, data=data)

                                    if response.status_code == 200:
                                        # Recibe el ID como un entero
                                        id_response = response.text
                                        print("Huella eliminada con ID:", id_response)
                                    else:
                                        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)


                                messagebox.showerror("Error", "No se pudo registrar las huellas")
                                # Reanudar el hilo 
                                mi_hilo.resume()
                                mi_hilo2.resume()
                            
                        except:
                            messagebox.showerror("Error entrada invalida", "El usuario no esta en la base de datos") 
                            mi_hilo.resume()
                            mi_hilo2.resume()   

                except:
                    messagebox.showerror("Error", "No se pudo conectar al NodeMCU")
                    command = "Eliminar"  # Comando para activar la suma

                    if id_1:
                        box_a = id_1

                        data = {"command": command, "box_a": str(box_a)}
                        response = requests.post(url, data=data)

                        if response.status_code == 200:
                            # Recibe el ID como un entero
                            id_response = response.text
                            print("Huella eliminada con ID:", id_response)
                        else:
                            print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                        if id_2:
                            box_a = id_2

                            data = {"command": command, "box_a": str(box_a)}
                            response = requests.post(url, data=data)

                            if response.status_code == 200:
                                # Recibe el ID como un entero
                                id_response = response.text
                                print("Huella eliminada con ID:", id_response)
                            else:
                                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                            if id_3:
                                box_a = id_3

                                data = {"command": command, "box_a": str(box_a)}
                                response = requests.post(url, data=data)

                            if response.status_code == 200:
                                # Recibe el ID como un entero
                                id_response = response.text
                                print("Huella eliminada con ID:", id_response)
                            else:
                                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)
                            
                        if id_4:
                            box_a = id_4

                            data = {"command": command, "box_a": str(box_a)}
                            response = requests.post(url, data=data)

                            if response.status_code == 200:
                                # Recibe el ID como un entero
                                id_response = response.text
                                print("Huella eliminada con ID:", id_response)
                            else:
                                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

                        if id_5:
                            box_a = id_5

                            data = {"command": command, "box_a": str(box_a)}
                            response = requests.post(url, data=data)

                            if response.status_code == 200:
                                # Recibe el ID como un entero
                                id_response = response.text
                                print("Huella eliminada con ID:", id_response)
                            else:
                                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)

                        if id_6:
                            box_a = id_6

                            data = {"command": command, "box_a": str(box_a)}
                            response = requests.post(url, data=data)

                            if response.status_code == 200:
                                # Recibe el ID como un entero
                                id_response = response.text
                                print("Huella eliminada con ID:", id_response)
                            else:
                                print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)


                        messagebox.showerror("Error", "No se pudo registrar las huellas")
                        # Reanudar el hilo 
                        mi_hilo.resume()
                        mi_hilo2.resume()
            else:
                messagebox.showwarning("Usuario no existe", "El usuario no esta en la base de datos")
                mi_hilo.resume()
                mi_hilo2.resume()
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, indique el usuario")
            mi_hilo.resume()
            mi_hilo2.resume()     
        
            
    def limpiar_campos_huella(self):
        self.entry_nombre.delete(0, tk.END)
        
####################################### FRAME GESTION DE ZONAS
        
    def mostrar_frame_gestion_zonas(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de zonas...
        self.frame_actual.pack(padx=20, pady=50)
          
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión de zonas", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar la gestión de zonas...
        self.lista = Lista_Zona()

        #boton frame lectores
        boton_ver_puertas = tk.Button(self.frame_actual, text="Ver Puertas", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_puerta)
        boton_ver_puertas.pack(side="left",fill="none", padx=10, pady=50)

        #boton frame sensores
        boton_ver_sensores = tk.Button(self.frame_actual, text="Ver sensores", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_sensores)
        boton_ver_sensores.pack(side="left",fill="none", padx=10, pady=50)

        #boton agregar usuario
        boton_agregar_zona = tk.Button(self.frame_actual, text="Agregar Zona", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_agregar_zona)
        boton_agregar_zona.pack(side="left",fill="none", padx=15, pady=50)

        #Boton eliminar zona
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Zona", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.eliminar_registro_zona)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=60, pady=50)
        
        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

############################################## GESTION DE PUERTAS (LECTORES)

    def mostrar_frame_gestion_puerta(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión de puertas",  background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)
        
        self.frame_actual.pack(padx=20, pady=20)
        
        # Código para mostrar la gestión de alertas...

        self.lista = Lista_lectores()
        
        #Código de Boton agregar puertas
        boton_agregar_puertas = tk.Button(self.frame_actual, text="Agregar Puerta",  font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_agregar_puerta)
        boton_agregar_puertas.pack(side="left",fill="none", padx=10, pady=50)

        #Boton eliminar puerta
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Puerta", font=("impact", 10),  relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.eliminar_registro_lectores)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=50)
        
        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_zonas)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)
        
        #Código de Boton de volver a menú
        boton_volver_menu =tk.Button(self.frame_actual, text="Volver a Menú", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver_menu.pack(side="left",fill="none", padx=10, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

################################################ FRAME AGREGAR PUERTA
        
    def mostrar_frame_agregar_puerta(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Puerta", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)

    

        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre_lector = ttk.Label(self.frame_actual, text="Descripcion del Lector:")
        self.etiqueta_nombre_lector.pack()
        self.entry_nombre_lector = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_nombre_lector.pack()

        self.etiqueta_zona = ttk.Label(self.frame_actual, text="Zona:")
        self.etiqueta_zona.pack()
        self.combobox_zona = ttk.Combobox(self.frame_actual)
        self.combobox_zona.pack()
        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port="3307"
        )
        self.cursor = self.conn.cursor()
        self.obtener_opciones_zona()

        # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_usuario)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)

         #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_puerta)
        boton_volver.pack(side="left",fill="none", padx=10, pady=50)
        
        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)
        
    def obtener_opciones_zona(self):
        self.cursor.execute("Select Nombre from Zona")
        resultados = self.cursor.fetchall()

        #obtener opciones
        opciones = [resultado[0] for resultado in resultados]
        self.combobox_zona.config(values=opciones)

    def registrar_lector(self):
        nombre = self.entry_nombre_lector.get()
        zona = self.combobox_zona.get()

        # Verificar que los campos no estén vacíos
        if nombre and zona:
            try:
                self.cursor.execute(f"SELECT ID FROM zona WHERE Nombre = '{zona}'")
                zona = self.cursor.fetchall()
                zona = zona[0][0]
            except:
                messagebox.showerror("Error entrada invalida", "Seleccione una zona de la lista")
            try:
                # Insertar el nuevo usuario en la tabla usuarios
                self.cursor.execute("INSERT INTO puerta VALUES (null, %s, %s)", (zona, nombre))
                self.conn.commit()
                messagebox.showinfo("Registro exitoso", "El Lector ha sido registrado correctamente")
                self.limpiar_campos_lector()
            except mysql.connector.Error as error:
                print("Error al registrar el Lector:", error)
                messagebox.showerror("Error", "No se pudo registrar el Lector")
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos")
    def limpiar_campos_lector(self):
        self.entry_nombre_lector.delete(0, tk.END)
        self.combobox_zona.delete(0, tk.END)

########################################## FRAME GESTION SENSORES

    def mostrar_frame_gestion_sensores(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión de Sensores", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar la gestión de alertas...

        self.frame_actual.pack(padx=20, pady=20)

        self.lista = Lista_sensores()

        #Código de Boton agregar sensor
        boton_agregar_sensor = tk.Button(self.frame_actual, text="Agregar Sensores", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_agregar_sensor)
        boton_agregar_sensor.pack(side="left",fill="none", padx=10, pady=20)

        #Boton eliminar zona
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Sensor", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.eliminar_registro_sensores)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=20)
        
        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_zonas)
        boton_volver.pack(side="left",fill="none", padx=80, pady=20)
        
        #Código de Boton de volver a menú
        boton_volver_menu = tk.Button(self.frame_actual, text="Volver a Menú", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver_menu.pack(side="left",fill="none", padx=10, pady=20)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=20)

####################################################### FRAME AGREGAR SENSORES
    def mostrar_frame_agregar_sensor(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Sensor", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)
        
    
        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre_sensor = ttk.Label(self.frame_actual, text="Descripcion del Sensor:")
        self.etiqueta_nombre_sensor.pack()
        self.entry_nombre_sensor = ttk.Entry(self.frame_actual)
        self.entry_nombre_sensor.pack()

        self.etiqueta_zona = ttk.Label(self.frame_actual, text="Zona:")
        self.etiqueta_zona.pack()
        self.combobox_zona = ttk.Combobox(self.frame_actual)
        self.combobox_zona.pack()

        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port="3307"
        )
        self.cursor = self.conn.cursor()
        self.obtener_opciones_zona()

        # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar", font=("impact", 10),relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_sensor)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_sensores)
        boton_volver.pack(side="left",fill="none", padx=10, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)
        
    def obtener_opciones_zona(self):
        self.cursor.execute("Select Nombre from Zona")
        resultados = self.cursor.fetchall()

        #obtener opciones
        opciones = [resultado[0] for resultado in resultados]
        self.combobox_zona.config(values=opciones)

    def registrar_sensor(self):
        nombre = self.entry_nombre_sensor.get()
        zona = self.combobox_zona.get()

        # Verificar que los campos no estén vacíos
        if nombre and zona:
            try:
                self.cursor.execute(f"SELECT ID FROM zona WHERE Nombre = '{zona}'")
                zona = self.cursor.fetchall()
                zona = zona[0][0]
            except:
                messagebox.showerror("Error entrada invalida", "Seleccione una zona de la lista")
            try:
                # Insertar el nuevo usuario en la tabla usuarios
                self.cursor.execute("INSERT INTO sensor VALUES (null, %s, %s)", (zona, nombre))
                self.conn.commit()
                messagebox.showinfo("Registro exitoso", "El Sensor ha sido registrado correctamente")
                self.limpiar_campos_sensor()
            except mysql.connector.Error as error:
                print("Error al registrar el Sensor:", error)
                messagebox.showerror("Error", "No se pudo registrar el Sensor")
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos")
    def limpiar_campos_sensor(self):
        self.entry_nombre_sensor.delete(0, tk.END)
        self.combobox_zona.delete(0, tk.END)

######################################### FRAME AGREGAR ZONAS

    def mostrar_frame_agregar_zona(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Zona",  background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)

        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre_zona = ttk.Label(self.frame_actual, text="Nombre de la Zona:")
        self.etiqueta_nombre_zona.pack()
        self.entry_nombre_zona = ttk.Entry(self.frame_actual)
        self.entry_nombre_zona.pack()

        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port="3307"
        )

        self.cursor = self.conn.cursor()

        # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_zona)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_zonas)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)
        
        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)


    def registrar_zona(self):
        nombre = self.entry_nombre_zona.get()
        print(nombre)
        # Verificar que los campos no estén vacíos
        if nombre:
            
            try:
                # Insertar el nuevo usuario en la tabla usuarios
                self.cursor.execute(f"INSERT INTO zona VALUES (null, '{nombre}', 1)")
                self.conn.commit()
                messagebox.showinfo("Registro exitoso", "La Zona ha sido registrado correctamente")
                self.limpiar_campos_zona()
            except mysql.connector.Error as error:
                print("Error al registrar la zona:", error)
                messagebox.showerror("Error", "No se pudo registrar la zona")
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos")
    def limpiar_campos_zona(self):
        self.entry_nombre_zona.delete(0, tk.END)

########################################### FRAME ALERTAS

    def mostrar_frame_gestion_alertas(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión de alertas", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        self.frame_actual.pack(padx=20, pady=20)

        # Código para mostrar la gestión de alertas...

        self.lista = Lista_alertas()
        
        #Código de Boton actualizar tabla
        boton_refrescar = tk.Button(self.frame_actual, text="Actualizar", font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_alertas)
        boton_refrescar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

################################################ FRAME GESTION PERMISOS

    def mostrar_frame_gestion_permisos(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Gestión de Permisos", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar la gestión de alertas...

        self.frame_actual.pack(padx=20, pady=20)

        self.lista = Lista_permisos()

        #Código de Boton agregar sensor
        boton_agregar_sensor = tk.Button(self.frame_actual, text="Agregar permisos", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_agregar_permisos)
        boton_agregar_sensor.pack(side="left",fill="none", padx=10, pady=50)
        
        #boton eliminar permiso
        boton_eliminar = tk.Button(self.frame_actual, text="Eliminar Permiso", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.eliminar_registro_permisos)
        boton_eliminar.pack(side="left",fill="none", padx=10, pady=50)
        
        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=20, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

############################################# FRAME AGREGAR PERMISOS
        
    def mostrar_frame_agregar_permisos(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)
        
        # Agregar elementos al frame de agregar usuario...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Agregar Permisos", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        # Código para mostrar formulario...

        self.frame_actual.pack(padx=20, pady=80)

      
        # Crear etiquetas y campos de entrada
        self.etiqueta_nombre_cargo = ttk.Label(self.frame_actual, text="Nombre del Cargo:")
        self.etiqueta_nombre_cargo.pack()
        self.entry_nombre_cargo = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_nombre_cargo.pack()

        # Crear etiquetas y campos de entrada
        self.etiqueta_descripcion_cargo = ttk.Label(self.frame_actual, text="Descripcion del Cargo:")
        self.etiqueta_descripcion_cargo.pack()
        self.entry_descripcion_cargo = tk.Entry(self.frame_actual,background="#303232",fg="#FFFFFF", highlightthickness=1, bd=2, relief="solid", borderwidth=2)
        self.entry_descripcion_cargo.pack()
        
        # Conectar a la base de datos
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_seguridad",
            port="3307"
        )
        self.cursor = self.conn.cursor()

         # Crear botón de registro
        self.boton_registrar = tk.Button(self.frame_actual, text="Registrar",font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command= self.registrar_cargo)
        self.boton_registrar.pack(side="left",fill="none", padx=10, pady=50)
        

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver",font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_gestion_permisos)
        boton_volver.pack(side="left",fill="none", padx=10, pady=50)
        
        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión",font=("impact", 10),relief="flat",  width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)


    def registrar_cargo(self):
        nombre = self.entry_nombre_cargo.get()
        descripcion = self.entry_descripcion_cargo.get()

        # Verificar que los campos no estén vacíos
        if nombre and descripcion:

            try:
                # Insertar el nuevo usuario en la tabla usuarios
                self.cursor.execute("INSERT INTO cargo VALUES (null, %s, %s)", (nombre, descripcion))
                self.conn.commit()
                messagebox.showinfo("Registro exitoso", "El cargo ha sido registrado correctamente")
                self.limpiar_campos_cargo()
            except mysql.connector.Error as error:
                print("Error al registrar el Cargo:", error)
                messagebox.showerror("Error", "No se pudo registrar el Cargo")
        else:
            messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos")
    def limpiar_campos_cargo(self):
        self.entry_nombre_cargo.delete(0, tk.END)
        self.entry_descripcion_cargo.delete(0, tk.END)

####################################### FRAME MODIFICACIONES AL SISTEMA

    def mostrar_frame_modificaciones(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Historial de Modificaciones", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        self.frame_actual.pack(padx=20, pady=20)

        # Código para mostrar la gestión de alertas...

        self.lista = Lista_modificaciones()

        #Código de Boton actualizar tabla
        boton_refrescar = tk.Button(self.frame_actual, text="Actualizar", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.actualizar_tabla_modificaciones)
        boton_refrescar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver",font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión",font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)

########################################### FRAME ENTRADAS AL SISTEMA

    def mostrar_frame_entradas(self):
        # Limpiar el frame actual si existe
        if self.frame_actual:
            self.frame_actual.destroy()
        if self.formulario:
            self.formulario.limpiar_instancia()
        if self.lista:
            self.lista.limpiar_instancia()
            
        # Crear el nuevo frame
        self.frame_actual = ttk.Frame(self.ventana)

        # Agregar elementos al frame de gestión de alertas...
        
        etiqueta_titulo = tk.Label(self.frame_actual, text="Historial de Entradas", background="#000000", fg="#FFFFFF", font=("impact", 15))
        etiqueta_titulo.pack(pady=10)

        self.frame_actual.pack(padx=20, pady=20)

        # Código para mostrar la gestión de alertas...

        self.lista = Lista_entradas()
        
        #Código de Boton actualizar tabla
        boton_refrescar = tk.Button(self.frame_actual, text="Actualizar", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.lista.actualizar_tabla_entradas)
        boton_refrescar.pack(side="left",fill="none", padx=10, pady=50)

        #Código de Boton de volver
        boton_volver = tk.Button(self.frame_actual, text="Volver", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_menu_principal)
        boton_volver.pack(side="left",fill="none", padx=80, pady=50)

        #Código para Cerrar Sesión
        boton_cerrar_sesion = tk.Button(self.frame_actual, text="Cerrar Sesión", font=("impact", 10), relief="flat", width=20, height=1, background="#1D6B70", fg="#FFFFFF", command=self.mostrar_frame_login)
        boton_cerrar_sesion.pack(side="left",fill="none", padx=10, pady=50)
    
    
    def iniciar_aplicacion(self):
        self.ventana.mainloop()

if __name__ == "__main__":
    aplicacion = VentanaPrincipal()
    aplicacion.iniciar_aplicacion()
