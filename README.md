## 🍄 **Fungi Scraper**  

Este proyecto incluye un conjunto de **scripts de scraping** para extraer datos y gestionar imágenes de hongos desde una fuente externa, e insertarlos en una base de datos MySQL.  

---

## 🚀 **Componentes Principales**  

### 1️⃣ **Scraper de datos** (`scraper.py`)  
- Extrae datos desde la página de origen (`fungipedia.org`)  
- Guarda los datos en formato JSON en la carpeta `/output_jsons`  

---

### 2️⃣ **Inserción de imágenes** (`insert_images_to_db.py`)  
- Descarga las imágenes desde las rutas proporcionadas por el scraper  
- Guarda las imágenes en la carpeta `/images`  
- **Inserta las imágenes** en la base de datos y las relaciona con los datos  

---

### 3️⃣ **Inserción de datos** (`insert-jsons-to-db.py`)  
- Lee los JSON generados por el scraper  
- **Inserta los datos** en las tablas `fungi`, `taxonomy` y `characteristics`  
- Relaciona las imágenes con los datos en la base de datos  

---

## ✅ **Estado:**  
✔️ Scraping y descarga de imágenes funcional  
✔️ Inserción en base de datos optimizada  
✔️ Manejo de errores y conflictos de datos  

---

👉 **Directorio de trabajo:**  
- `/output_jsons` → Datos extraídos  
- `/images` → Imágenes descargadas  
- `/names.txt` → Lista de nombres escrapeados  
