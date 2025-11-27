import scrapy
from scrapy_playwright.page import PageMethod


class ProductDetailsSpider(scrapy.Spider):
    name = "product_details"

    def __init__(self, url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not url:
            raise ValueError("Use: scrapy crawl product_details -a url=https://...")
        self.start_url = url

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url,
            callback=self.parse_product,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", ".nome-produto"),
                    PageMethod("wait_for_selector", ".accordion-inner"),
                    PageMethod("wait_for_selector", "#descricao"),
                    PageMethod("wait_for_selector", ".atributo-item"),
                ],
            }
        )

    async def parse_product(self, response):

        name = response.css(".nome-produto::text").get("")
        name = name.strip()

        sku = response.css(".produto-sku::text").get()
        sku = sku.strip() if sku else ""

        base_price = response.css(
            ".preco-promocional::text, .preco-venda::text, .preco-a-partir strong::text"
        ).get()
        if base_price:
            base_price = base_price.strip()

        pix_price = response.css(".desconto-a-vista strong::text").get()
        pix_price = pix_price.strip() if pix_price else ""

        installments = []
        for li in response.css(".accordion-inner li.parcela"):
            times = li.css("b.cor-principal::text").get()
            value = li.css("::text").re_first(r"R\$ ?\d+,\d+")
            no_interest = "sem juros" in li.get().lower()

            if times and value:
                installments.append({
                    "times": times.strip(),
                    "value": value.strip(),
                    "no_interest": no_interest
                })

        sizes = []
        for s in response.css(".atributo-item span::text").getall():
            s = s.strip()
            if s:
                sizes.append(s)
        sizes = list(dict.fromkeys(sizes))

        description = " ".join(
            response.css("#descricao *::text").getall()
        ).strip()

        images = response.css(
            "ul.miniaturas.slides li a::attr(data-imagem-grande)"
        ).getall()

        if not images:
            img = response.css(".imagem-principal::attr(src)").get()
            if img:
                images.append(img)

        page = response.meta.get("playwright_page")
        if page:
            await page.close()

        yield {
            "name": name,
            "sku": sku,
            "url": response.url,
            "images": images,
            "price": {
                "base_price": base_price,
                "pix_price": pix_price,
                "installments": installments
            },
            "sizes": sizes,
            "description": description
        }
