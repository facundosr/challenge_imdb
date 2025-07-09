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

```
.
├── main.py
├── extract/
│   └── scraper.py
├── utils/
│   ├── request_handler.py
│   └── db_handler.py
├── output/
│   └── imdb_chart.csv
├── requeriments.txt
```

---

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

```

---
3️⃣ Proxies &amp; Control de Red 
Implementar una estrategia robusta para evitar bloqueos:
A. Uso de proxies rotativos (mínimo 3 IPs), configurados con retry/fallback automático.
LOG:
```
2025-07-09 17:36:43,518 - INFO - Iniciando scraping...
2025-07-09 17:36:47,633 - INFO - Request a https://www.imdb.com/es/chart/top/ con proxy: http://user:pass@proxy3.com:8080
2025-07-09 17:36:57,668 - ERROR - ERROR - requests HTTPSConnectionPool(host='www.imdb.com', port=443): Max retries exceeded with url: /es/chart/top/ (Caused by ProxyError('Unable to connect to proxy', ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x000002831C283650>, 'Connection to proxy3.com timed out. (connect timeout=10)')))
2025-07-09 17:37:11,834 - INFO - Proxy http://user:pass@proxy3.com:8080 eliminado de la lista por fallo. Quedan 2 proxies.
2025-07-09 17:37:11,835 - WARNING - Intento 1/5 fallido. Reintentando en 1.0s...
2025-07-09 17:37:16,603 - INFO - Request a https://www.imdb.com/es/chart/top/ con proxy: http://user:pass@proxy1.com:8080
2025-07-09 17:37:36,779 - ERROR - ERROR - requests HTTPSConnectionPool(host='www.imdb.com', port=443): Max retries exceeded with url: /es/chart/top/ (Caused by ProxyError('Unable to connect to proxy', ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x000002831C25EA50>, 'Connection to proxy1.com timed out. (connect timeout=10)')))
2025-07-09 17:37:36,779 - INFO - Proxy http://user:pass@proxy1.com:8080 eliminado de la lista por fallo. Quedan 1 proxies.
2025-07-09 17:37:36,780 - WARNING - Intento 2/5 fallido. Reintentando en 2.0s...
2025-07-09 17:37:38,790 - INFO - Request a https://www.imdb.com/es/chart/top/ con proxy: http://user:pass@proxy2.com:8080
2025-07-09 17:37:58,828 - ERROR - ERROR - requests HTTPSConnectionPool(host='www.imdb.com', port=443): Max retries exceeded with url: /es/chart/top/ (Caused by ProxyError('Unable to connect to proxy', ConnectTimeoutError(<urllib3.connection.HTTPSConnection object at 0x000002831C298FD0>, 'Connection to proxy2.com timed out. (connect timeout=10)')))
2025-07-09 17:37:58,828 - INFO - Proxy http://user:pass@proxy2.com:8080 eliminado de la lista por fallo. Quedan 0 proxies.
2025-07-09 17:37:58,829 - WARNING - Intento 3/5 fallido. Reintentando en 4.0s...
2025-07-09 17:38:02,838 - WARNING - Se agotaron los proxies disponibles. Intentando sin proxy...
```

---

## 📞 Contacto

Desarrollado por **Facundo Sosa**.  

---


