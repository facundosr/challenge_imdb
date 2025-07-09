import os
import csv
import json
import logging
from bs4 import BeautifulSoup as BS
from utils.request_handler import RequestHandler
from utils.db_handler import get_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IMDbScraper():
    _HEADERS = {'Content-Type': 'application/json'}
    _OPERATION_HASHES = {
        "credits": "7f5916c2ad82a9c4178d8795981f97370cb2f703614edcd05a9316f1d3717a24"
    }

    def __init__(self):
        self.rh = RequestHandler(self._HEADERS, use_proxy=False)
        self.url_base = "https://www.imdb.com"
        self.chart_endpoint = "/es/chart/top/"
        self.imdb_api = "https://caching.graphql.imdb.com"
        self.chart_movie_list = list()

    def run(self):
        logger.info("Iniciando scraping...")
        self._get_movies()
        self._export_csv()
        self._export_postgres()
    
    def _get_movies(self):
        soup = self._get_soup()
        chart_movies = self._get_chart_list(soup)

        logger.info(f"{len(chart_movies)} movies encontrados")
        
        all_chart_cast = self._get_all_chart_cast()
        for item in chart_movies:
            dict_movie = None
            movie = item.get("node")
            if not movie: continue
            id_ = movie.get("id")
            try:
                dict_movie = {
                    # "id": id_,
                    "title": self._get_title(movie),
                    "release_year": self._get_release_year(movie),
                    "duration": self._get_duration(movie),
                    "calification": self._get_calification(movie),
                    "cast": self._get_movie_cast(id_, all_chart_cast)
                }
            except Exception as e:
                logger.error(f"Error al obtener el contenido {id_}: {e}")

            logger.info(dict_movie)
            self.chart_movie_list.append(dict_movie) if dict_movie else None
            logger.info("________________________")
        
    
    def _get_soup(self):
        try:
            response = self.rh.get(f"{self.url_base}{self.chart_endpoint}")
            return BS(response.text, 'lxml')
        except Exception as e:
            raise Exception("No se pudo obtener el soup del html")

    def _get_chart_list(self, soup):
        """
            Busca en el html el elemento script y devuelve una lista con los contenidos.
            Comment: Haciendo soup y buscando los elementos del html solo trae los primeros 25 ya que la web carga con JS
            Por eso, se hace soup y se extrae el diccionario con todos los contenidos desde el elemento script
            - Args:
                - soup: soup
            - Returns: 
                - chart_list: lista con los contenidos del top
        """
        # soup_movies = soup.select(".cli-parent")
        try:
            script = soup.find('script', {'id': '__NEXT_DATA__'})
            json_ = json.loads(script.string)
            page_data = json_['props']['pageProps']['pageData']
            chart_list = page_data['chartTitles']['edges']
            return chart_list
        except Exception as e:
            raise Exception("No se pudo obtener el top de contenidos")

    def _get_title(self, movie):
        try:
            return movie['titleText']['text']
        except KeyError:
            raise Exception("No se pudo obtener el título")

    def _get_release_year(self, movie):
        try:
            return movie['releaseYear']['year']
        except KeyError:
            logger.warning("No se pudo obtener el release year")

    def _get_calification(self, movie):
        try:
            return movie['ratingsSummary']['aggregateRating']
        except KeyError:
            logger.warning("No se pudo obtener la calificación")

    def _get_duration(self, movie):
        duration = None
        try:
            seconds = movie['runtime']['seconds']
            duration = int(int(seconds) / 60)
        except KeyError as e:
            logger.warning(f"Error: {e} - No se pudo obtener la duración")
        return duration

    
    def _get_all_chart_cast(self):
        try:
            variables = {
                "first": 250,
                "isInPace": False,
                "locale": "en-US"
            }

            extensions = {
                "persistedQuery": {
                    "sha256Hash": self._OPERATION_HASHES['credits'],
                    "version": 1
                }
            }

            querystring = {
                "variables": json.dumps(variables, separators=(",", ":")),
                "extensions": json.dumps(extensions, separators=(",", ":"))
            }
            response = self.rh.get(
                self.imdb_api, headers=self._HEADERS, params=querystring)
            json_ = response.json()
            return json_['data']['chartTitles']['edges']
        except Exception as e:
            raise Exception(f"Error: {e} - No se pudo obtener el diccionario de Cast")

    def _get_movie_cast(self, movie_id, all_cast):
        cast = []
        if not movie_id:
            return cast
        
        for node in all_cast:
            cast_node = node.get("node", {})
            if cast_node.get("id") != movie_id:
                continue
            principal_credits = cast_node.get("principalCredits", [])
            cast_credits = next(
                (c for c in principal_credits if c.get(
                    "category", {}).get("id") == "cast"), {}
            )
            raw_cast = cast_credits.get("credits", [])
            cast = [actor.get("name", {}).get("nameText", {}).get(
                "text", "") for actor in raw_cast]
            break
        return cast
    
    def _export_csv(self, filename="output/imdb_chart.csv"):
        if not self.chart_movie_list:
            logger.warning("No se encontraron datos para exportar.")
            return
        os.makedirs("output", exist_ok=True)
        with open(filename, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.chart_movie_list[0].keys())
            writer.writeheader()
            writer.writerows(self.chart_movie_list)
        logger.info(f"[OK] CSV guardado en {filename}")


    def _create_tables(self, cur):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS peliculas (
                id SERIAL PRIMARY KEY,
                titulo TEXT NOT NULL,
                anio INT,
                calificacion FLOAT,
                duracion INT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS actores (
                id SERIAL PRIMARY KEY,
                pelicula_id INT REFERENCES peliculas(id),
                nombre TEXT NOT NULL,
                UNIQUE (pelicula_id, nombre)
            );
        """)
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes WHERE tablename = 'peliculas' AND indexname = 'unique_titulo_anio'
                ) THEN
                    ALTER TABLE peliculas ADD CONSTRAINT unique_titulo_anio UNIQUE (titulo, anio);
                END IF;
            END
            $$;
        """)

        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_indexes WHERE tablename = 'actores' AND indexname = 'unique_actor_por_pelicula'
                ) THEN
                    ALTER TABLE actores ADD CONSTRAINT unique_actor_por_pelicula UNIQUE (pelicula_id, nombre);
                END IF;
            END
            $$;
        """)

    def _export_postgres(self):
        if not self.chart_movie_list:
            logger.warning("No hay datos para exportar a PostgreSQL.")
            return

        conn = get_connection()
        cur = conn.cursor()
        self._create_tables(cur)

        for row in self.chart_movie_list:
            cur.execute("""
                    INSERT INTO peliculas (titulo, anio, calificacion, duracion)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (titulo, anio) DO UPDATE
                    SET calificacion = EXCLUDED.calificacion,
                        duracion = EXCLUDED.duracion
                    RETURNING id;
                """, (
                row["title"],
                row.get("release_year"),
                row.get("calification"),
                row.get("duration"),
            ))
            pelicula_id = cur.fetchone()[0]

            cast = row.get("cast", [])
            for actor in cast:
                cur.execute("""
                    INSERT INTO actores (pelicula_id, nombre)
                    VALUES (%s, %s)
                    ON CONFLICT (pelicula_id, nombre) DO NOTHING;
                """, (pelicula_id, actor))

        conn.commit()
        conn.close()
        logger.info("[OK] Datos guardados en PostgreSQL")
