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
        page = response.meta["playwright_page"]

        try:
            await page.wait_for_selector("#descricao", timeout=5000)
        except:
            pass

        html = await page.content()
        response = scrapy.Selector(text=html)
        page.close()

        title = response.css("h1.nome-produto::text").get()

        description_html = response.css("#descricao").get()

        parcelas_list = []
        for li in response.css(".accordion-inner ul li"):
            parcela = li.css("b.cor-principal::text").get()
            valor = li.css("span::text").getall()
            valor = " ".join(v.strip() for v in valor if v.strip())
            parcelas_list.append({
                "parcela": parcela,
                "texto": valor
            })

        images = response.css(".miniaturas img::attr(src)").getall()
        images_big = response.css(".miniaturas a::attr(data-imagem-grande)").getall()

        tamanhos = response.css(".atributo-comum ul li a span::text").getall()
        tamanhos = [t.strip() for t in tamanhos]

        yield {
            "title": title,
            "description_html": description_html,
            "parcelas": parcelas_list,
            "images": images,
            "images_big": images_big,
            "tamanhos": tamanhos
        }
