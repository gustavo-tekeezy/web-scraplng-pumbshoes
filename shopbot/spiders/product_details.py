import scrapy
from scrapy_playwright.page import PageMethod


class ProductDetailsSpider(scrapy.Spider):
    name = "product_details"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [url]

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "h1.nome-produto")
                ],
                "playwright_include_page": True
            }
        )

    async def parse(self, response):
        page = response.meta.get("playwright_page")

        try:
            # espera o conteúdo principal da página
            if page:
                await page.wait_for_selector("#descricao", timeout=5000)
        except Exception:
            pass

        # pega HTML renderizado pelo Playwright
        if page:
            html = await page.content()
            await page.close()
            response = scrapy.Selector(text=html)

        title = response.css("h1.nome-produto::text").get()
        description_html = response.css("#descricao").get()

        # PARCELAS: iterar UL por UL para preservar a ordem (1-6, depois 7-12)
        parcelas_list = []
        seen = set()  # para evitar duplicações acidentais

        for ul in response.css(".accordion-inner > ul"):
            for li in ul.css("li"):
                # só processa se for item de parcela ou contiver <b class="cor-principal">
                parcela_num = li.css("b.cor-principal::text").get()
                # extrai o span com a classe específica se existir, senão pega os text nodes do li
                span = li.css("span.cor-secundaria")
                if span:
                    textos = [t.strip() for t in span.xpath("text()").getall() if t.strip()]
                else:
                    textos = [t.strip() for t in li.xpath(".//text()").getall() if t.strip()]

                # junta e limpa espaços extras
                texto_completo = " ".join(textos)
                texto_completo = " ".join(texto_completo.split())

                # se não houver parcela_num, tenta extrair diretamente do texto (fallback)
                if not parcela_num:
                    # tenta pegar algo parecido com "1x" no começo do texto
                    # isolamos o primeiro token que contenha 'x' (ex: "1x", "10x")
                    tokens = texto_completo.split()
                    parcela_candidate = next((t for t in tokens if "x" in t and any(ch.isdigit() for ch in t)), None)
                    parcela_num = parcela_candidate or parcela_num

                # evita entradas vazias
                if not parcela_num and not texto_completo:
                    continue

                key = (parcela_num or "", texto_completo or "")
                if key in seen:
                    continue
                seen.add(key)

                parcelas_list.append({
                    "parcela": parcela_num,
                    "texto": texto_completo
                })

        images = response.css(".miniaturas img::attr(src)").getall()
        images_big = response.css(".miniaturas a::attr(data-imagem-grande)").getall()

        tamanhos = response.css(".atributo-comum ul li a span::text").getall()
        tamanhos = [t.strip() for t in tamanhos if t.strip()]

        yield {
            "title": title,
            "description_html": description_html,
            "parcelas": parcelas_list,
            "images": images,
            "images_big": images_big,
            "tamanhos": tamanhos
        }
