🔧 Implementación del scraper con Playwright
1. Configuración avanzada del navegador

Modo headless opcional:
```
context = await browser.new_context(
    user_agent="Mozilla/5.0 ...",
    extra_http_headers={"Referer": "...", "Accept-Language": "en-US"},
    storage_state="cookies.json"
)
```


2. Selectores dinámicos con espera explícita

```
await page.goto("https://www.imdb.com/chart/top/")
await page.wait_for_selector("script#__NEXT_DATA__")
```
O también con PW podríamos hacer scrolling e ir bajando hasta el footer, para que carguen todos los contenidos del TOP y ahí recién hacer el soup sobre el html completo.

3. Evasión de WebDriver: Playwright no expone navigator.webdriver por defecto, lo cual reduce su detección. Se puede usar playwright-stealth para reforzar aún más.

Manejo de CAPTCHA o JavaScript Rendering

Playwright permite:

Detectar elementos de CAPTCHA.

Simular interacción humana (mouse/teclado).

Tomar capturas de pantalla para debugging.

Por ejemplo si detectamos un captcha con audio, mediante un script se puede obtener el audio, transcribirlo y pasar el captcha (solo en linux)

Conclusión: Playwright (o seleniu,) es ideal para scrapear sitios con mucho JavaScript y comportamiento dinámico.
Scrapy, en cambio, es un framework rápido y eficiente para scrapear sitios estáticos, por eso en este caso no sería tan útil.