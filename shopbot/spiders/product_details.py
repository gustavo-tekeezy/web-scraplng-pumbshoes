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
                    PageMethod("wait_for_selector", "h1.nome-produto"),
                    PageMethod(
                        "wait_for_function",
                        "document.querySelector('#descricao') && document.querySelector('#descricao').innerText.length > 20"
                    ),
                ],
                "playwright_include_page": True
            }
        )

    async def parse(self, response):
        page = response.meta.get("playwright_page")

        if page:
            try:
                await page.wait_for_selector("#descricao", timeout=3000)
            except:
                pass
            html = await page.content()
            await page.close()
            response = scrapy.Selector(text=html)

        title = response.css("h1.nome-produto::text").get()
        description_html = response.css("#descricao").get()

        # DESCRIÇÃO TEXTUAL
        paragraphs = []
        for p in response.css("#descricao p"):
            txt = p.xpath("string(.)").get()
            if txt:
                txt = " ".join(txt.split())
                paragraphs.append(txt)

        description_text = "\n\n".join(paragraphs) if paragraphs else ""

        # ============================================================
        # AGORA O SEGREDO:
        # PEGAR APENAS AS ÚLTIMAS 2 UL (que são a tabela correta)
        # ============================================================

        all_uls = response.css(".accordion-inner > ul")

        # se não tiver pelo menos 2 listas, não tem como montar 12x
        if len(all_uls) >= 2:
            ul1 = all_uls[-2]  # tabela correta (1–6)
            ul2 = all_uls[-1]  # tabela correta (7–12)
        else:
            ul1 = all_uls[0] if len(all_uls) >= 1 else []
            ul2 = []

        # Coleta apenas das duas UL certas
        parcelas_raw = []
        parcelas_raw.extend(self.parse_parcelas(ul1))
        parcelas_raw.extend(self.parse_parcelas(ul2))

        # Remove duplicações internas
        final = []
        seen = set()
        for p in parcelas_raw:
            key = (p["parcela"], p["texto"])
            if key not in seen:
                seen.add(key)
                final.append(p)

        # Ordenar corretamente
        def num(x):
            try:
                return int(x["parcela"].replace("x", ""))
            except:
                return 999

        parcelas = sorted(final, key=num)

        # ============================================================

        images = response.css(".miniaturas img::attr(src)").getall()
        images_big = response.css(".miniaturas a::attr(data-imagem-grande)").getall()

        tamanhos = [
            t.strip()
            for t in response.css(".atributo-comum ul li a span::text").getall()
            if t.strip()
        ]

        yield {
            "title": title,
            "description_html": description_html,
            "description_text": description_text,
            "parcelas": parcelas,  # <<== AGORA SOMENTE AS 12 CERTAS
            "images": images,
            "images_big": images_big,
            "tamanhos": tamanhos,
        }

    def parse_parcelas(self, ul):
        parcelas = []

        for li in ul.css("li"):
            parcela_num = li.css("b.cor-principal::text").get()

            span = li.css("span.cor-secundaria")
            textos = [t.strip() for t in span.xpath("text()").getall() if t.strip()] if span else []

            texto = " ".join(textos)
            texto = " ".join(texto.split())

            if parcela_num and texto:
                parcelas.append({
                    "parcela": parcela_num,
                    "texto": texto
                })

        return parcelas
