def scrape_fungi_details(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error al acceder a {url}")
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
        additional_info_section = soup.find('div', class_='itemExtraFieldsFungi')
        if additional_info_section:
            for item in additional_info_section.find_all('li', class_='caracteristica'):
                label = item.find('span', class_='itemExtraFieldsLabel')
                value = item.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    info_adicional[label.text.strip()] = value.text.strip()

        nombre_comun = info_adicional.get("Nombre común:")
        sinonimo = info_adicional.get("Sinónimo:")

        # Taxonomía
        taxonomia_section = soup.find_all('div', class_='itemExtraFieldsFungi')
        taxonomia = {}
        if len(taxonomia_section) > 1:
            for item in taxonomia_section[1].find_all('li', class_='caracteristica'):
                label = item.find('span', class_='itemExtraFieldsLabel')
                value = item.find('span', class_='itemExtraFieldsValue')
                if label and value:
                    taxonomia[label.text.strip().replace(':', '')] = value.text.strip()

        # Comestibilidad
        comestibilidad = None
        comest_img = soup.select_one('div.itemToolbarFungi img')
        if comest_img:
            match = re.search(r'/images/comestibilidad/(.*?).png', comest_img['src'])
            if match:
                comestibilidad = match.group(1)

        # Características, Hábitat y Observaciones
        caracteristicas = {}
        habitat = observaciones = None

        full_text = soup.select_one('div.itemFullText')
        if full_text:
            h3_headers = full_text.find_all('h3')
            paragraphs = full_text.find_all('p')

            current_section = None
            for header in h3_headers:
                header_text = header.text.strip()
                if "Características" in header_text:
                    current_section = "características"
                elif "Hábitat" in header_text:
                    current_section = "hábitat"
                elif "Observaciones" in header_text:
                    current_section = "observaciones"

                if current_section == "características":
                    for i, key in enumerate(["sombrero", "láminas", "pie", "carne"]):
                        caracteristicas[key] = paragraphs[i].text.strip()
                elif current_section == "hábitat":
                    habitat = paragraphs[len(caracteristicas)].text.strip()
                elif current_section == "observaciones":
                    observaciones = paragraphs[len(caracteristicas) + 1].text.strip()

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
            "observaciones": observaciones,
        }

        return data
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return None

