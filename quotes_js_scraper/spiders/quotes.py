from typing import Iterable
import scrapy
from quotes_js_scraper.items import QuoteItem
from scrapy_playwright.page import PageMethod

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        url = "https://quotes.toscrape.com/scroll"
        yield scrapy.Request(url, meta={
            "playwright": True,
            "playwright_include_page" : True,
            "playwright_page_methods" : [
                PageMethod("wait_for_selector", "div.quote"),
            ],
            "errback" : self.errback
        })

    async def parse(self, response):
        # now that we'll be scrapingg multiple pages we should also close pages to conserve memory
        page = response.meta["playwright_page"]
        screenshot = await page.screenshot(path = "example.png", full_page = True)
        await page.close()

    
    async def errback (self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()