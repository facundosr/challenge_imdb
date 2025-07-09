import requests
import cloudscraper
import random
import time
from fake_useragent import UserAgent

class RequestHandler:
    def __init__(
        self,
        headers=None,
        proxies=None,
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

        self.default_headers = headers if headers else {
            "Accept-Language": "es-AR,es;q=0.9",
            "Connection": "keep-alive",
        }

        self.proxy_list = proxies if isinstance(proxies, list) else [proxies] if proxies else []
        self.scraper = cloudscraper.create_scraper() if enable_cloudscraper else None

    def _get_random_user_agent(self) -> str:
        return self.ua.random

    def _get_random_proxy(self):
        if not self.proxy_list:
            return None
        proxy = random.choice(self.proxy_list)
        return {"http": proxy, "https": proxy}

    def _make_request(self, method: str, url: str, headers, params, data, use_cloudscraper=False, **kwargs):
        requester = self.scraper if use_cloudscraper and self.scraper else self.session
        proxies = self._get_random_proxy()
        try:
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
            print(f"ERROR - {'cloudscraper' if use_cloudscraper else 'requests'} {e}")
            return None

    def _request_with_retries(self, method: str, url: str, headers, params, data, **kwargs):
        retries = 0
        while retries < self.max_retries:
            merged_headers = self.default_headers.copy()
            merged_headers["User-Agent"] = self._get_random_user_agent()
            if headers:
                merged_headers.update(headers)

            response = self._make_request(method, url, merged_headers, params, data, use_cloudscraper=False, **kwargs)

            if response and response.status_code == 200:
                return response
            elif response and response.status_code in [403, 429, 503] and self.enable_cloudscraper:
                print(f"[{response.status_code}] Bloqueo detectado. Probando con Cloudscraper...")
                response = self._make_request(method, url, merged_headers, params, data, use_cloudscraper=True, **kwargs)
                if response and response.status_code == 200:
                    print("[OK] Cloudscraper funcionó correctamente.")
                    return response

            wait = self.backoff_factor * (2 ** retries)
            print(f"Intento {retries+1}/{self.max_retries} fallido. Reintentando en {wait:.1f}s...")
            time.sleep(wait)
            retries += 1

        print(f"Falló al acceder a {url} tras {self.max_retries} intentos.")
        return None

    def get(self, url: str, headers = None, params=None, data=None, **kwargs):
        return self._request_with_retries("GET", url, headers, params, data, **kwargs)

    def post(self, url: str, headers = None, params=None, data=None, **kwargs):
        return self._request_with_retries("POST", url, headers, params, data, **kwargs)
