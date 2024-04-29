import scrapy


class AuthorsSpider(scrapy.Spider):
    name = "authors"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "authors.json"}
    visited_links = set()


    def parse(self, response):
        content = response.xpath("/html/body/div/div[2]/div[1]/div/span[2]/a")
        for link in content:
            full_link = self.start_urls[0] + link.xpath('@href').get()
            if full_link not in self.visited_links:
                yield response.follow(full_link, self.parse_author)
                self.visited_links.add(full_link)

        next_link = response.xpath("//li[@class='next']/a/@href").get()
        if next_link:
            yield scrapy.Request(url=self.start_urls[0] + next_link)


    def parse_author(self, response):
        yield {
            "fullname": response.xpath("/html//h3[@class='author-title']/text()").extract(),
            "born_date": response.xpath("/html//span[@class='author-born-date']/text()").extract(),
            "born_location": response.xpath("/html//span[@class='author-born-location']/text()").extract(),
            "description": response.xpath("/html//div[@class='author-description']/text()").extract()
        }