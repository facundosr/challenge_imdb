import psycopg2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="imdb",
            user="postgres",
            password="admin",
            host="localhost",
            port=5432
        )
        return conn
    except Exception as e:
        logger.error(f"No se pudo conectar a la base de datos: {e}")
        raise
