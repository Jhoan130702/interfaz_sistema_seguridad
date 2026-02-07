import requests

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
    
EnviarNotificaciones()