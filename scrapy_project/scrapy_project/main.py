from spiders.quotes import QuotesSpider
from spiders.authors import AuthorsSpider

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

process = CrawlerProcess(settings)
process.crawl(QuotesSpider)
process.crawl(AuthorsSpider)
process.start()