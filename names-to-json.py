import requests
from bs4 import BeautifulSoup
import json
import re
import os

def format_name(name):
    """Convierte el nombre en URL-friendly."""
    return name.strip().lower().replace(' ', '-')

def get_text_or_none(soup_element):
    """Devuelve el texto del elemento si existe."""
    return soup_element.text.strip() if soup_element else None

def scrape_fungi_details(url):
    """Scrapea la página de detalles de una seta."""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error al acceder a {url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Título y Autor
        titulo = get_text_or_none(soup.select_one('h1.itemTitle'))
        autor = get_text_or_none(soup.select_one('span.itemAuthor'))
        print(titulo);
        print(autor);

        # Imagen principal
        imagen_principal = soup.select_one('img.sigProImg')
        imagen_principal_url = imagen_principal['src'] if imagen_principal else None

        # Imágenes adicionales
        imagenes_adicionales = [img['href'] for img in soup.select('a.fancybox-image')]

        # Información adicional (Nombre común y Sinónimo)
        info_adicional = {}
        extra_fields = soup.select('div.itemExtraFieldsFungi')
        for field in extra_fields:
            label = field.select_one('span.itemExtraFieldsLabel')
            value = field.select_one('span.itemExtraFieldsValue')
            if label and value:
                info_adicional[label.text.strip()] = value.text.strip()
        
        nombre_comun = info_adicional.get("Nombre común")
        sinonimo = info_adicional.get("Sinónimo")

        # Taxonomía
        taxonomia = {
            "division": info_adicional.get("División"),
            "subdivision": info_adicional.get("Subdivisión"),
            "clase": info_adicional.get("Clase"),
            "subclase": info_adicional.get("Subclase"),
            "orden": info_adicional.get("Orden"),
            "familia": info_adicional.get("Familia")
        }

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
            "titulo": titulo,
            "autor": autor,
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
    # Leer los nombres desde el archivo 'names.txt'
    with open('names.txt', 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file.readlines()]

    base_url = "https://www.fungipedia.org/hongos/"
    
    # Crear carpeta para los archivos JSON si no existe
    os.makedirs('output_jsons', exist_ok=True)

    for name in names:
        formatted_name = format_name(name)
        url = f"{base_url}{formatted_name}.html"
        print(f"Scrapeando: {url}")
        
        fungi_details = scrape_fungi_details(url)
        if fungi_details:
            # Guardar cada seta en un archivo JSON individual
            json_filename = f'output_jsons/{formatted_name}.json'
            with open(json_filename, 'w', encoding='utf-8') as json_file:
                json.dump(fungi_details, json_file, ensure_ascii=False, indent=4)
            print(f"Guardado en {json_filename}")

    print("Scraping completado. Todos los archivos JSON generados por seta individual.")

if __name__ == "__main__":
    main()

