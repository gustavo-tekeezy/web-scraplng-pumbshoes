import scrapy
from scrapy_playwright.page import PageMethod

class PumbSpider(scrapy.Spider):
    name = "pumb"

    def __init__(self, query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not query:
            raise ValueError("Use: scrapy crawl pumb -a query='sandalia'")
        self.query = query

    def start_requests(self):
        url = f"https://www.pumbshoes.com.br/buscar?q={self.query}"

        yield scrapy.Request(
            url=url,
            callback=self.parse_results,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "div.listagem-item")
                ],
                "playwright_include_page": True,
            }
        )

    async def parse_results(self, response):
        products = response.css("div.listagem-item")

        for p in products:
            yield {
                "name": p.css(".nome-produto::text").get(default="").strip(),
                "price": p.css(".preco-promocional::text, .preco-venda::text").get(default="").strip(),
                "url": response.urljoin(p.css("a::attr(href)").get()),
                "image": response.urljoin(p.css("img::attr(src)").get()),
            }

        page = response.meta.get("playwright_page")
        if page:
            await page.close()
