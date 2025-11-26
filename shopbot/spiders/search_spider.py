import scrapy

class SearchSpider(scrapy.Spider):
    name = "search"

    def __init__(self, query=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not query:
            raise ValueError("Use: scrapy crawl search -a query='sandalia'")
        self.query = query

    def start_requests(self):
        url = f"https://example.com/search?q={self.query}"  # Trocar depois para o site real
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        # Seletores de exemplo — trocaremos depois para o site real
        for product in response.css(".product"):
            yield {
                "name": product.css(".title::text").get(),
                "price": product.css(".price::text").get(),
                "url": response.urljoin(product.css("a::attr(href)").get()),
            }
