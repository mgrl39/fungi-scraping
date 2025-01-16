import requests
from bs4 import BeautifulSoup
import json
import os
import re

# Colores para depuración
class bcolors:
    OKCYAN = '\033[96m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    FAIL = '\033[91m'

def print_text(name, text):
    print(f"{bcolors.OKCYAN}{bcolors.BOLD}{name}:{bcolors.ENDC} {text if text else f'{bcolors.FAIL}NULL{bcolors.ENDC}'}")

def format_name(name):
    return name.strip().lower().replace(' ', '-')

def get_text_or_none(soup_element):
    return soup_element.text.strip() if soup_element else None

def scrape_fungi_details(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"{bcolors.FAIL}Error al acceder a {url}{bcolors.ENDC}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Título y Autor
        title = get_text_or_none(soup.select_one('h1.itemTitle'))
        author = get_text_or_none(soup.select_one('span.itemAuthor'))

        # Imagen principal
        imagen_principal = soup.select_one('img.sigProImg')
        imagen_principal_url = imagen_principal['src'] if imagen_principal else None

        # Imágenes adicionales
        imagenes_adicionales = [img['href'] for img in soup.select('a.fancybox-image')]

        # Información adicional (como Nombre común y Sinónimo)
        info_adicional = {}
        for field in soup.select('div.itemExtraFieldsFungi span'):
            label = field.find_previous('span', class_='itemExtraFieldsLabel')
            value = field.find_next('span', class_='itemExtraFieldsValue')
            if label and value:
                info_adicional[label.text.strip()] = value.text.strip()

        nombre_comun = info_adicional.get("Nombre común:")
        sinonimo = info_adicional.get("Sinónimo:")

        # Taxonomía
        taxonomia = {key.strip(':'): info_adicional.get(key) for key in [
            "División:", "Subdivisión:", "Clase:", "Subclase:", "Orden:", "Familia:"
        ]}

        # Comestibilidad
        comestibilidad = None
        comest_img = soup.select_one('div.itemToolbarFungi img')
        if comest_img:
            match = re.search(r'/images/comestibilidad/(.*?).png', comest_img['src'])
            if match:
                comestibilidad = match.group(1)

        # Características, Hábitat y Observaciones
        caracteristicas = {"sombrero": None, "láminas": None, "pie": None, "carne": None}
        habitat, observaciones = None, None

        full_text = soup.select_one('div.itemFullText')
        if full_text:
            paragraphs = full_text.find_all(['p', 'h3'])
            current_section = None
            for para in paragraphs:
                text = para.text.strip()
                if "Características" in text:
                    current_section = "características"
                elif "Hábitat" in text:
                    current_section = "hábitat"
                elif "Observaciones" in text:
                    current_section = "observaciones"
                elif current_section == "características" and para.name == 'p':
                    keys = list(caracteristicas.keys())
                    for i, key in enumerate(keys):
                        if not caracteristicas[key]:
                            caracteristicas[key] = text
                            break
                elif current_section == "hábitat" and para.name == 'p':
                    habitat = text
                elif current_section == "observaciones" and para.name == 'p':
                    observaciones = text

        # Datos estructurados
        data = {
            "nombre": url.split('/')[-1].replace('.html', ''),
            "title": title,
            "author": author,
            "imagen_principal": imagen_principal_url,
            "imagenes_adicionales": imagenes_adicionales,
            "nombre_comun": nombre_comun,
            "sinonimo": sinonimo,
            "taxonomia": taxonomia,
            "comestibilidad": comestibilidad,
            "caracteristicas": caracteristicas,
            "habitat": habitat,
            "observaciones": observaciones
        }

        return data
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return None

def main():
    with open('names.txt', 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file.readlines()]

    base_url = "https://www.fungipedia.org/hongos/"
    os.makedirs('output_jsons', exist_ok=True)

    for name in names:
        print(f"{bcolors.OKCYAN}<===================================================>{bcolors.ENDC}")
        formatted_name = format_name(name)
        url = f"{base_url}{formatted_name}.html"
        print_text("URL", url)

        fungi_details = scrape_fungi_details(url)
        if fungi_details:
            json_filename = f'output_jsons/{formatted_name}.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(fungi_details, json_file, ensure_ascii=False, indent=4)
            print(f"Guardado en {json_filename}")

    print(f"{bcolors.OKCYAN}{bcolors.BOLD}Scraping completado. Todos los archivos JSON generados por seta individual.{bcolors.ENDC}")

if __name__ == "__main__":
    main()

