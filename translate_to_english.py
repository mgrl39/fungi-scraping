import os
import json
import time
from googletrans import Translator

# Inicializar el traductor
translator = Translator()

# Función para traducir el contenido de un JSON
def translate_json(json_data):
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if isinstance(value, str):
                # Traducir el texto
                json_data[key] = translator.translate(value, src='es', dest='en').text
            elif isinstance(value, dict) or isinstance(value, list):
                # Llamada recursiva si el valor es un diccionario o lista
                translate_json(value)
    elif isinstance(json_data, list):
        for i in range(len(json_data)):
            if isinstance(json_data[i], str):
                json_data[i] = translator.translate(json_data[i], src='es', dest='en').text
            elif isinstance(json_data[i], dict) or isinstance(json_data[i], list):
                translate_json(json_data[i])

# Función para procesar todos los archivos en un directorio
def translate_json_files(input_directory, output_directory):
    file_count = 0
    for filename in os.listdir(input_directory):
        if filename.endswith('.json'):
            file_count += 1
            file_path = os.path.join(input_directory, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            # Traducir el contenido del JSON
            translate_json(json_data)

            # Guardar el JSON traducido en la carpeta de salida
            translated_file_path = os.path.join(output_directory, f"translated_{filename}")
            with open(translated_file_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)

            print(f"Archivo traducido guardado en: {translated_file_path}")

            # Agregar un sleep de 2 segundos entre archivos para evitar bloqueos
            time.sleep(2)

            # Para evitar problemas por demasiados archivos seguidos, podrías agregar una pausa más larga después de cada bloque de 100 archivos.
            if file_count % 100 == 0:
                print("Pausa de 30 segundos para evitar bloqueos...")
                time.sleep(30)

# Directorios de entrada y salida
input_directory = 'output_jsons'
output_directory = 'output_jsons_eng'

# Crear el directorio de salida si no existe
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Ejecutar la traducción
translate_json_files(input_directory, output_directory)

