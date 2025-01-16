# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# NO BORRAR
# Librerias 
import requests
from bs4 import BeautifulSoup
import json
import re
import os

# Colors
from defs import *

def print_text(name, text):
    print(f"{bcolors.OKCYAN}{bcolors.BOLD}" + name + ":", end="");
    if text is None:
        print(f"{bcolors.FAIL}{bcolors.BOLD} NULL{bcolors.ENDC}")
        return ;
    print(f"{bcolors.ENDC}", end=" ");
    print(text);

# Convierte el nombre en URL-friendly.
def format_name(name):
    print_text("FORMAT_NAME", name.strip().lower().replace(' ', '-'));
    return name.strip().lower().replace(' ', '-')

# Devuelve el texto del elemento si existe.
# Si no existe devuelve None
def get_text_or_none(soup_element):
    return soup_element.text.strip() if soup_element else None

# Scrapea la página de detalles de una seta.
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
            # print_text("TITULO", title);
            # print_text("AUTOR", author);

        # Imagen principal
        imagen_principal = soup.select_one('img.sigProImg')
        imagen_principal_url = imagen_principal['src'] if imagen_principal else None
            # print_text("IMAGEN PRINCIPAL", imagen_principal);
            # print_text("URL IMAGEN PRINCIPAL", imagen_principal_url);

        # Imágenes adicionales
        imagenes_adicionales = [img['href'] for img in soup.select('a.fancybox-image')]
            # print_text("IMAGENES ADICIONALES", imagenes_adicionales);

        # Información adicional (Nombre común y Sinónimo)
        info_adicional = {}
        extra_fields = soup.select('div.itemExtraFieldsFungi')
        for field in extra_fields:
            label = field.select_one('span.itemExtraFieldsLabel')
            value = field.select_one('span.itemExtraFieldsValue')
            if label and value:
                info_adicional[label.text.strip()] = value.text.strip()
        
        print("BUENOS DIAS")
        print(info_adicional);
        # TODO AQUI EL GET ESTE LO HACE MAL 
        # print(info_adicional[label.text.strip]);
        print(type(info_adicional));
        for info in info_adicional:
            print("HOLA MUNDO " + info);
        print(info_adicional.keys);
        print(label.text.strip());
        print(info_adicional[label.text.strip()])
        nombre_comun = info_adicional.get("Nombre común")
        sinonimo = info_adicional.get("Sinónimo")
        print_text("NOMBRE COMUN", nombre_comun);
        # return ;
        print_text("SINONIMO", sinonimo);

        # Taxonomía
        taxonomia = {
            "division": info_adicional.get("División"),
            "subdivision": info_adicional.get("Subdivisión"),
            "clase": info_adicional.get("Clase"),
            "subclase": info_adicional.get("Subclase"),
            "orden": info_adicional.get("Orden"),
            "familia": info_adicional.get("Familia")
        }
        print_text("TAXONOMIA", taxonomia);
        # print(taxonomia);

        # Comestibilidad
        comestibilidad = None
        comest_img = soup.select_one('div.itemToolbarFungi img')
        if comest_img:
            match = re.search(r'/images/comestibilidad/(.*?).png', comest_img['src'])
            if match:
                comestibilidad = match.group(1)
        print_text("COMESTABILIDAD", comestibilidad);
        #print(comestibilidad);
        #print(comest_img);

        # Características, Hábitat y Observaciones
        caracteristicas = {}
        habitat, observaciones = None, None
        full_text = soup.select_one('div.itemFullText')

        if full_text:
            h3_headers = full_text.select('h3[style*="border-bottom: 1px solid #2e2415;"]')
            paragraphs = full_text.select('p')

            for header, paragraph in zip(h3_headers, paragraphs):
                header_text = header.text.strip()
                if "Características" in header_text:
                    caracteristicas["sombrero"] = paragraphs[0].text.strip()
                    caracteristicas["laminas"] = paragraphs[1].text.strip()
                    caracteristicas["pie"] = paragraphs[2].text.strip()
                    caracteristicas["carne"] = paragraphs[3].text.strip()
                elif "Hábitat" in header_text:
                    habitat = paragraph.text.strip()
                elif "Observaciones" in header_text:
                    observaciones = paragraph.text.strip()

        # Estructurar los datos extraídos
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

# Leer los nombres desde el archivo 'names.txt'
def main():
    with open('names.txt', 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file.readlines()]

    base_url = "https://www.fungipedia.org/hongos/"
    
    # Crear carpeta para los archivos JSON si no existe
    os.makedirs('output_jsons', exist_ok=True)

    for name in names:
        print(f"{bcolors.OKBLUE}<===================================================>{bcolors.ENDC}")
        formatted_name = format_name(name)
        url = f"{base_url}{formatted_name}.html"
        print_text("URL", url)
        # print(f"Scrapeando: {url}")
        
        fungi_details = scrape_fungi_details(url)
        if fungi_details:
            # Guardar cada seta en un archivo JSON individual
            json_filename = f'output_jsons/{formatted_name}.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(fungi_details, json_file, ensure_ascii=False, indent=4)
            print(f"Guardado en {json_filename}")

    print(f"{bcolors.OKBLUE}{bcolors.BOLD}Scraping completado. Todos los archivos JSON generados por seta individual.{bcolors.ENDC}")

if __name__ == "__main__":
    main()
