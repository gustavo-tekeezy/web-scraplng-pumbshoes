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
                    PageMethod("wait_for_selector", ".listagem-item")
                ],
                "playwright_include_page": True,
            }
        )

    async def parse_results(self, response):
        products = response.css("div.listagem-item")

        for p in products:

            # --- URL do produto (correta) ---
            url_produto = p.css("a.produto-sobrepor::attr(href)").get()
            if url_produto:
                url_produto = response.urljoin(url_produto)

            # --- Nome ---
            nome = p.css(".nome-produto::text").get(default="").strip()

            # --- SKU ---
            sku = p.css(".produto-sku::text").get(default="").strip()

            # --- Preço promocional ---
            preco_promocional = p.css(".preco-promocional::text").get()
            if preco_promocional:
                preco_promocional = preco_promocional.strip()

            # --- Preço original / a partir ---
            preco_original = p.css(".preco-venda::text").get()
            if preco_original:
                preco_original = preco_original.strip()

            # --- Preço no Pix ---
            preco_pix = p.css(".desconto-a-vista strong::text").get()
            if preco_pix:
                preco_pix = preco_pix.strip()

            # --- Parcelamento ---
            parcelamento = p.css(".preco-parcela strong.titulo::text").get()
            if parcelamento:
                parcelamento = parcelamento.strip()

            parcelas_qtd = p.css(".preco-parcela strong::text").get()
            if parcelas_qtd:
                parcelas_qtd = parcelas_qtd.replace("x", "").strip()

            # Montagem final do texto de parcelamento
            if parcelas_qtd and parcelamento:
                parcelado = f"{parcelas_qtd}x de {parcelamento}"
            else:
                parcelado = None

            # --- Desconto (%) ---
            desconto = p.css(".bandeira-promocao::text").get()
            if desconto:
                desconto = desconto.strip()

            # --- Imagem ---
            imagem = p.css("img.imagem-principal::attr(src)").get()
            if imagem:
                imagem = response.urljoin(imagem)

            yield {
                "name": nome,
                "sku": sku,
                "url": url_produto,
                "parcelado": parcelado,
                "preco_original": preco_original,
                "preco_promocional": preco_promocional,
                "preco_pix": preco_pix,
                "desconto": desconto,
                "image": imagem
            }

        page = response.meta.get("playwright_page")
        if page:
            await page.close()
