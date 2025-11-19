# Importamos las librerías que acabamos de instalar
import requests
from bs4 import BeautifulSoup

# La URL de una página simple para probar
url = 'http://example.com'

print(f"Haciendo petición a: {url}")

# Hacemos la petición a la página
response = requests.get(url)

# Verificamos que la petición fue exitosa (código 200)
if response.status_code == 200:
    print("¡Petición exitosa!")

    # Creamos un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Buscamos la etiqueta <title> y extraemos su texto
    titulo_pagina = soup.find('title').text

    print(f"El título de la página es: '{titulo_pagina}'")
else:
    print(f"Error al hacer la petición. Código: {response.status_code}")
