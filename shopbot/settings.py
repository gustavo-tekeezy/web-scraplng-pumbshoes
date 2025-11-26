TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
REACTOR_THREADPOOL_MAXSIZE = 20

BOT_NAME = "shopbot"

SPIDER_MODULES = ["shopbot.spiders"]
NEWSPIDER_MODULE = "shopbot.spiders"

ROBOTSTXT_OBEY = False

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

FEED_EXPORT_ENCODING = "utf-8"
