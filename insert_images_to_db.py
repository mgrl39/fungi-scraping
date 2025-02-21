import os
import argparse
import mysql.connector
from mysql.connector import Error
import re

def normalize_fungi_name(filename):
    # Eliminar número y extensión
    base = re.sub(r'[-_]\d+\.jpg$', '', filename)
    
    # Convertir a formato de la base de datos (lowercase con guiones)
    name = base.lower()
    # Reemplazar espacios y underscores con guiones
    name = re.sub(r'[_ ]', '-', name)
    # Eliminar caracteres no permitidos
    name = re.sub(r'[^a-z0-9-]', '', name)
    
    return name

def get_exact_fungi_match(cursor, normalized_name):
    # Primero intentar una coincidencia exacta
    cursor.execute("SELECT id, name FROM fungi WHERE name = %s", (normalized_name,))
    result = cursor.fetchone()
    if result:
        return result

    # Si no hay coincidencia exacta, buscar coincidencias parciales
    cursor.execute("""
        SELECT id, name 
        FROM fungi 
        WHERE name LIKE %s 
        OR name LIKE %s 
        OR name LIKE %s
    """, (
        f'{normalized_name}%',
        f'%{normalized_name}%',
        f'%{normalized_name}'
    ))
    results = cursor.fetchall()
    
    if len(results) == 1:
        return results[0]
    elif len(results) > 1:
        print(f"Múltiples coincidencias para {normalized_name}:")
        for id, name in results:
            print(f"  - ID: {id}, Nombre: {name}")
        return None
    return None

def get_or_create_config(cursor, config_key, base_path):
    cursor.execute("SELECT config_key FROM image_config WHERE config_key = %s", (config_key,))
    if not cursor.fetchone():
        insert_query = """
        INSERT INTO image_config (config_key, path)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (config_key, base_path))
    return config_key

def process_images(cursor, config_key, image_dir):
    successful_imports = 0
    failed_imports = 0
    
    for filename in os.listdir(image_dir):
        if not filename.lower().endswith('.jpg'):
            continue
            
        normalized_name = normalize_fungi_name(filename)
        result = get_exact_fungi_match(cursor, normalized_name)
        
        if not result:
            print(f"❌ No se encontró coincidencia para {filename}")
            print(f"   Nombre normalizado: {normalized_name}")
            failed_imports += 1
            continue
            
        fungi_id, db_fungi_name = result
        
        # Verificar si esta imagen específica ya existe
        cursor.execute("SELECT id FROM images WHERE filename = %s", (filename,))
        if cursor.fetchone():
            print(f"⚠️  La imagen {filename} ya existe en la base de datos")
            failed_imports += 1
            continue
        
        try:
            # Insertar imagen
            insert_image_query = """
            INSERT INTO images (filename, config_key, description)
            VALUES (%s, %s, %s)
            """
            image_values = (filename, config_key, f"Imagen de {db_fungi_name}")
            cursor.execute(insert_image_query, image_values)
            image_id = cursor.lastrowid
            
            # Insertar relación
            insert_relation_query = """
            INSERT INTO fungi_images (fungi_id, image_id)
            VALUES (%s, %s)
            """
            cursor.execute(insert_relation_query, (fungi_id, image_id))
            
            successful_imports += 1
            print(f"✓ Insertada imagen {filename} para {db_fungi_name} (ID: {fungi_id})")
            
        except Error as e:
            print(f"❌ Error al procesar {filename}: {e}")
            failed_imports += 1
            raise

    # Resumen final
    print("\n=== Resumen de importación ===")
    print(f"✓ Imágenes importadas exitosamente: {successful_imports}")
    print(f"❌ Imágenes fallidas: {failed_imports}")
    print(f"📊 Total procesadas: {successful_imports + failed_imports}")

def main():
    parser = argparse.ArgumentParser(description='Insertar imágenes de hongos en la base de datos')
    parser.add_argument('--image-dir', required=True, help='Directorio con las imágenes')
    parser.add_argument('--base-path', required=True, help='Ruta base ej: "/uploads/fungi/"')
    parser.add_argument('--dry-run', action='store_true', help='Ejecutar sin hacer cambios')
    args = parser.parse_args()

    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Root@1234',
        'database': 'fungidb'
    }

    try:
        connection = mysql.connector.connect(**db_config)
        connection.autocommit = False
        cursor = connection.cursor()

        print("Iniciando proceso...")
        print(f"Directorio de imágenes: {args.image_dir}")
        print(f"Ruta base: {args.base_path}")
        print(f"Modo prueba: {'Sí' if args.dry_run else 'No'}")
        
        config_key = 'fungi_upload_path'
        get_or_create_config(cursor, config_key, args.base_path)
        
        process_images(cursor, config_key, args.image_dir)
        
        if args.dry_run:
            print("Modo prueba - haciendo rollback")
            connection.rollback()
        else:
            print("Confirmando cambios...")
            connection.commit()
            print("Proceso completado con éxito")

    except Error as e:
        print(f"Error de base de datos: {e}")
        connection.rollback()
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    main()
