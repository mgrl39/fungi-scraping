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
        imagen_principal_url = (
            f"https://www.fungipedia.org{imagen_principal['src']}" if imagen_principal else None
        )

        # Imágenes adicionales
        imagenes_adicionales = [
            f"https://www.fungipedia.org{img['href']}" for img in soup.select('a.fancybox-image')
        ]

        # Información adicional
        info_adicional = {}
        info_adicional_section = soup.find('div', class_='itemExtraFieldsFungi')
        if info_adicional_section:
            for li in info_adicional_section.find_all('li', class_='caracteristica'):
                label = li.find('span', class_='itemExtraFieldsLabel')
                value = li.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    key = label.text.strip().strip(':')
                    val = value.text.strip()
                    info_adicional[key] = val

        nombre_comun = info_adicional.get("Nombre común")
        sinonimo = info_adicional.get("Sinónimo")

        # Taxonomía
        taxonomia_section = soup.find('div', class_='taxonomia')
        taxonomia = {}
        if taxonomia_section:
            for li in taxonomia_section.find_all('li', class_='caracteristica'):
                label = li.find('span', class_='itemExtraFieldsLabel')
                value = li.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    key = label.text.strip().strip(':')
                    val = value.text.strip()
                    taxonomia[key] = val

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

