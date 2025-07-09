# 🎬 IMDb Top Movies Scraper

Este proyecto implementa un scraper en Python que extrae información de las 250 películas mejor calificadas en IMDb, junto con su reparto principal, y las almacena en un archivo CSV y en una base de datos PostgreSQL relacional.

---

## 📌 Funcionalidades

- Extracción de películas del ranking IMDb Top Chart (`https://www.imdb.com/chart/top/`).
- Obtención de:
  - Título
  - Año de estreno
  - Calificación (IMDb)
  - Duración en minutos
  - Cast principal (al menos 3 actores)
- Exportación a:
  - Archivo CSV
  - Base de datos PostgreSQL normalizada (tablas `peliculas` y `actores`)
- Reintentos con backoff, logs y manejo de errores.
- Estructura modular y orientada a objetos.
- Patrón de diseño aplicado: **Factory** (RequestHandler y DBHandler abstraídos como servicios).

---

## 🗂️ Estructura del Proyecto

.
├── main.py
├── extract/
│ └── scraper.py
├── utils/
│ ├── request_handler.py
│ └── db_handler.py
├── output/
│ └── imdb_chart.csv
├── requeriments.txt

---

## ⚙️ Requisitos

- Python 3.8+
- PostgreSQL (corriendo en local o remoto)
- Librerías Python:
  - `requests`
  - `beautifulsoup4`
  - `psycopg2`
  - `lxml`

Instalá los paquetes necesarios con:

```bash
pip install -r requirements.txt

---

## 🛠️ Configuración

1. **Base de datos PostgreSQL**: asegurate de tener una instancia corriendo. El handler espera una función `get_connection()` que devuelva una conexión válida. Se puede configurar desde `utils/db_handler.py`.

2. **Tabla y modelo**:

```sql
CREATE TABLE peliculas (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    anio INT,
    calificacion FLOAT,
    duracion INT,
    UNIQUE (titulo, anio)
);

CREATE TABLE actores (
    id SERIAL PRIMARY KEY,
    pelicula_id INT REFERENCES peliculas(id),
    nombre TEXT NOT NULL,
    UNIQUE (pelicula_id, nombre)
);
```

Estas tablas son creadas automáticamente si no existen.

---

## 🚀 Ejecución

```bash
python main.py
```

Esto ejecutará:

1. El scraping de películas y actores.
2. La exportación a un archivo CSV en `/output/imdb_chart.csv`.
3. La carga de datos en la base de datos PostgreSQL NOTA: (se carga el top completo con la ejecución del script, si en cambio se quieren agregar contenidos mediante script sql dentro de sql_files se puede ejecutar el script 'create_and_insert_script.sql' que agregará los primeros 50 films y sus respectivos actores)

---

## 📊 Consultas Analíticas Sugeridas

```sql
-- 1. Top 5 películas con mayor promedio de duración por década
SELECT
  (anio / 10) * 10 AS decada,
  AVG(duracion) AS promedio_duracion
FROM peliculas
GROUP BY decada
ORDER BY promedio_duracion DESC
LIMIT 5;

-- 2. Desviación estándar de calificación por año
SELECT
  anio,
  STDDEV(calificacion) AS desviacion_calificacion
FROM peliculas
GROUP BY anio;

-- 3. Películas con diferencia > 20% entre calificación y metascore (si existiera)
-- No se incluye metascore en esta versión por no estar en los datos finales.

-- 4. Vista para filtrar películas por actor
CREATE VIEW vista_peliculas_actores AS
SELECT
  p.titulo,
  p.anio,
  a.nombre AS actor
FROM peliculas p
JOIN actores a ON p.id = a.pelicula_id;

-- 5. Índice sugerido para consultas por actor
CREATE INDEX idx_nombre_actor ON actores(nombre);
```

---

## 📞 Contacto

Desarrollado por **Facundo Sosa**.  
Proyecto técnico para desafío de scraping y modelado relacional.

---


