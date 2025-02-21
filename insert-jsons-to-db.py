import os
import json
import mysql.connector
from mysql.connector import Error

# Configuración de la base de datos
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Root@1234',
    'database': 'fungidb'
}

def insert_fungi_data(cursor, fungi_data):
    # Insertar en la tabla fungi
    insert_fungi_query = """
    INSERT INTO fungi (name, author, edibility, habitat, observations, common_name, synonym, title)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    fungi_values = (
        fungi_data['name'],
        fungi_data['author'],
        fungi_data['edibility'],
        fungi_data['habitat'],
        fungi_data['observations'],
        fungi_data['additional_info']['common_name'],
        fungi_data['additional_info']['synonym'],
        fungi_data['title']
    )
    cursor.execute(insert_fungi_query, fungi_values)
    fungi_id = cursor.lastrowid

    # Insertar en la tabla taxonomy
    insert_taxonomy_query = """
    INSERT INTO taxonomy (fungi_id, division, subdivision, class, subclass, ordo, family)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    taxonomy_values = (
        fungi_id,
        fungi_data['taxonomy']['División'],
        fungi_data['taxonomy']['Subdivisión'],
        fungi_data['taxonomy']['Clase'],
        fungi_data['taxonomy']['Subclase'],
        fungi_data['taxonomy']['Orden'],
        fungi_data['taxonomy']['Familia']
    )
    cursor.execute(insert_taxonomy_query, taxonomy_values)

    # Insertar en la tabla characteristics
    insert_characteristics_query = """
    INSERT INTO characteristics (fungi_id, cap, hymenium, stipe, flesh)
    VALUES (%s, %s, %s, %s, %s)
    """
    characteristics_values = (
        fungi_id,
        fungi_data['characteristics']['cap'],
        fungi_data['characteristics']['hymenium'],
        fungi_data['characteristics']['stipe'],
        fungi_data['characteristics']['flesh']
    )
    cursor.execute(insert_characteristics_query, characteristics_values)

def main():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            print("Conectado a la base de datos MySQL")

            # Leer todos los archivos JSON en el directorio actual
            for filename in os.listdir('.'):
                if filename.endswith('.json'):
                    with open(filename, 'r', encoding='utf-8') as file:
                        fungi_data = json.load(file)
                        insert_fungi_data(cursor, fungi_data)
                        print(f"Datos insertados de {filename}")

            connection.commit()
            print("Todos los datos han sido insertados correctamente")

    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    main()
