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

        # Imagen principal (URL completa)
        imagen_principal = soup.select_one('img.sigProImg')
        imagen_principal_url = imagen_principal['src'] if imagen_principal else None
        if imagen_principal_url and not imagen_principal_url.startswith('http'):
            imagen_principal_url = f"https://www.fungipedia.org{imagen_principal_url}"

        # Imágenes adicionales
        imagenes_adicionales = [
            f"https://www.fungipedia.org{img['href']}" for img in soup.select('a.fancybox-image')
        ]

        # Información adicional (como Nombre común y Sinónimo)
        info_adicional = {}
        for field in soup.select('div.itemExtraFieldsFungi span'):
            label = field.find_previous('span', class_='itemExtraFieldsLabel')
            value = field.find_next('span', class_='itemExtraFieldsValue')
            if label and value:
                info_adicional[label.text.strip()] = value.text.strip()

        nombre_comun = info_adicional.get("Nombre común:", None)
        sinonimo = info_adicional.get("Sinónimo:", None)

        # Taxonomía
        taxonomia = {key.strip(':'): info_adicional.get(key, None) for key in [
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
        caracteristicas = {}
        habitat, observaciones = None, None

        full_text = soup.select_one('div.itemFullText')
        if full_text:
            h3_headers = full_text.find_all('h3')
            paragraphs = full_text.find_all('p')
            current_section = None

            for header in h3_headers:
                if "Características" in header.text:
                    current_section = "características"
                elif "Hábitat" in header.text:
                    current_section = "hábitat"
                elif "Observaciones" in header.text:
                    current_section = "observaciones"

                if current_section == "características":
                    caracteristicas["sombrero"] = paragraphs[0].text.strip()
                    caracteristicas["láminas"] = paragraphs[1].text.strip()
                    caracteristicas["pie"] = paragraphs[2].text.strip()
                    caracteristicas["carne"] = paragraphs[3].text.strip()
                elif current_section == "hábitat":
                    habitat = paragraphs[4].text.strip()
                elif current_section == "observaciones":
                    observaciones = paragraphs[5].text.strip()

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

