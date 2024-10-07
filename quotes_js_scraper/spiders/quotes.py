from typing import Iterable
import scrapy
from quotes_js_scraper.items import QuoteItem
from scrapy_playwright.page import PageMethod

class QuotesSpider(scrapy.Spider):
    name = 'quotes'

    def start_requests(self):
        url = "https://quotes.toscrape.com/js/"
        yield scrapy.Request(url, meta={
            "playwright": True,
            "playwright_include_page" : True,
            "playwright_Page_methods" : [
                PageMethod("wait_for_selector", "div.quote")
            ],
            "errback" : self.errback
        })

    async def parse(self, response):
        # now that we'll be scrapingg multiple pages we should also close pages to conserve memory
        page = response.meta["playwright_page"]
        await page.close()

        for quote in response.css("div.quote"):
            quote_item = QuoteItem()
            quote_item["text"] = quote.css("span.text::text").get()
            quote_item["author"] = quote.css("small.author::text").get()
            quote_item["tags"] = quote.css("div.tags a.tag::text").get()
            yield quote_item
        
        # getting the next page
        next_page = response.css(".next>a::attr(href)").get()
        if next_page is not None:
            next_page_url = "https://quotes.toscrape.com" + next_page
            yield scrapy.Request(next_page_url,meta={
                "playwright": True,
                "playwright_include_page" : True,
                "playwright_Page_methods" : [
                    PageMethod("wait_for_selector", "div.quote")
                ],
                "errback" : self.errback
            })
    
    async def errback (self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()