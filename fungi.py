import requests
from bs4 import BeautifulSoup

# Función para obtener los h3 con la clase específica y guardarlos en un archivo
def scrape_and_save(url, file):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Seleccionar solo los h3 con clase "catItemTitle"
    headlines = soup.select('h3.catItemTitle')

    for headline in headlines:
        nombre = headline.text.strip()
        file.write(nombre + '\n')
        print(f'Guardado: {nombre}')

# Función para paginar y recorrer todas las páginas
def scrape_all_pages(base_url, max_pages, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for offset in range(0, max_pages + 1, 20):
            print(f'Scrapeando página con offset {offset}')
            page_url = f"{base_url}?start={offset}"
            scrape_and_save(page_url, file)

# Parámetros de la página base y el número máximo de páginas
base_url = "https://www.fungipedia.org/hongos.html"
max_offset = 560  # Cambia esto si hay más páginas en el futuro

# Ejecutar el scraping y guardar en names.txt
scrape_all_pages(base_url, max_offset, 'names.txt')

print("Scraping completado y guardado en 'names.txt'")

