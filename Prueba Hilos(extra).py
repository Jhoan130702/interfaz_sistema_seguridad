import time
import threading
import requests
import json

class MiHilo2(threading.Thread):
    
    def __init__(self):
        super().__init__()
        self.daemon = True 
        self.tiempo = 7  
        self.paused = threading.Event()  # Usar Event para controlar la pausa
        self.paused.set()  # Comenzar en estado de ejecución

    def hacer_consulta(self):
        print("siiiiiiiii")
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
        self.tiempo = 120.1  
        self.paused = threading.Event()  # Usar Event para controlar la pausa
        self.paused.set()  # Comenzar en estado de ejecución
        self.hilo2 = MiHilo2()  # Crear instancia del segundo hilo

    def hacer_consulta(self):
        print("si x")
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
    mi_hilo2 = MiHilo2()
    mi_hilo = MiHilo()

    mi_hilo.start()  # Iniciar el hilo 1
    # El hilo 2 se inicia dentro de MiHilo

iniciar_hilos()

# Mantener el programa en ejecución indefinidamente
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Programa terminado.")
