import requests
import json

url = "http://192.168.4.1/"
command = "Eliminar"
box_a = 5
if box_a:
    data = {"command": command, "box_a": str(box_a)}
    response = requests.post(url, data=data)
    if response.status_code == 200:
        id_response = response.text
        print("Huella eliminada con ID:", id_response)
    else:
        print("Error al enviar el comando al NodeMCU. Código de estado:", response.status_code)