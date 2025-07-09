import requests
import cloudscraper
import random
import time
from fake_useragent import UserAgent
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RequestHandler:
    def __init__(
        self,
        headers=None,
        use_proxy=False,
        max_retries=5,
        backoff_factor=1.0,
        timeout=10,
        enable_cloudscraper=True
    ):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self.enable_cloudscraper = enable_cloudscraper
        self.use_proxy = use_proxy
        self.default_headers = headers if headers else {
            "Accept-Language": "es-AR,es;q=0.9",
            "Connection": "keep-alive",
        }

        self.proxy_list = [
            "http://user:pass@proxy1.com:8080",
            "http://user:pass@proxy2.com:8080",
            "http://user:pass@proxy3.com:8080",
        ]

        self.scraper = cloudscraper.create_scraper() if enable_cloudscraper else None

    def _get_random_user_agent(self) -> str:
        return self.ua.random

    def _get_random_proxy(self):
        logger.info("Obteniendo proxy")
        if not self.proxy_list:
            return None
        proxy = random.choice(self.proxy_list)
        return {"http": proxy, "https": proxy}

    def _make_request(self, method: str, url: str, headers, params, data, proxies, use_cloudscraper=False, **kwargs):
        requester = self.scraper if use_cloudscraper and self.scraper else self.session
        try:
            logger.info(f"Request a {url} con proxy: {proxies['http'] if proxies else 'sin proxy'}")
            response = requester.request(
                method=method,
                url=url,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout,
                params=params,
                data=data,
                **kwargs
            )

            return response
        except requests.RequestException as e:
            logger.error(f"ERROR - {'cloudscraper' if use_cloudscraper else 'requests'} {e}")
            return None

    def _request_with_retries(self, method: str, url: str, headers, params, data, **kwargs):
        retries = 0
        proxy_pool = self.proxy_list.copy() if self.use_proxy else [None]

        while retries < self.max_retries:
            merged_headers = self.default_headers.copy()
            merged_headers["User-Agent"] = self._get_random_user_agent()
            if headers:
                merged_headers.update(headers)

            if self.use_proxy:
                if not proxy_pool:
                    logger.warning("Se agotaron los proxies disponibles. Intentando sin proxy...")
                    proxies = None
                    self.use_proxy = False
                else:
                    proxy = random.choice(proxy_pool)
                    proxies = {"http": proxy, "https": proxy}
            else:
                proxies = None

            response = self._make_request(method, url, merged_headers, params, data, proxies, use_cloudscraper=False, **kwargs)

            if response and response.status_code == 200:
                return response

            if response and response.status_code in [403, 429, 503] and self.enable_cloudscraper:
                logger.warning(f"[{response.status_code}] Bloqueo detectado. Probando con Cloudscraper...")
                response = self._make_request(method, url, merged_headers, params, data, proxies, use_cloudscraper=True, **kwargs)
                if response and response.status_code == 200:
                    logger.info("[OK] Cloudscraper funcionó correctamente.")
                    return response

            # Si se usó proxy y hubo error, lo removemos para no reusar
            if proxies:
                proxy_pool = [p for p in proxy_pool if p != proxy]
                logger.info(f"Proxy {proxy} eliminado de la lista por fallo. Quedan {len(proxy_pool)} proxies.")

            wait = self.backoff_factor * (2 ** retries)
            logger.warning(f"Intento {retries+1}/{self.max_retries} fallido. Reintentando en {wait:.1f}s...")
            time.sleep(wait)
            retries += 1

        logger.error(f"Falló al acceder a {url} tras {self.max_retries} intentos.")
        return None

    def get(self, url: str, headers = None, params=None, data=None, **kwargs):
        return self._request_with_retries("GET", url, headers, params, data, **kwargs)

    def post(self, url: str, headers = None, params=None, data=None, **kwargs):
        return self._request_with_retries("POST", url, headers, params, data, **kwargs)
