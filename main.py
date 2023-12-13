import os
import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from googlesearch import search

def get_urls(tag, n, language):
    urls = [url for url in search(tag, num_results=n, lang=language)][:n]
    return urls

class MailSpider(scrapy.Spider):
    name = 'email'
    
    def __init__(self, start_urls, output_path, reject):
        self.start_urls = start_urls
        self.output_path = output_path
        self.reject = reject
        self.emails = set() 
    
    def parse(self, response):
        links = LxmlLinkExtractor(allow=()).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))
        
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_link) 
            
    def parse_link(self, response):
        for word in self.reject:
            if word in str(response.url):
                return
            
        html_text = str(response.text)
        mail_list = re.findall(r'\w+@(?:[a-zA-Z]{2,}\.)+[a-zA-Z]{2,}', html_text)

        self.emails.update(mail_list)

    def closed(self, reason):
        emails_list = list(self.emails)
        df = pd.DataFrame({'Emails': emails_list})
        df.to_csv(self.output_path, index=False)
        self.log(f"Salvo em {self.output_path}")

if __name__ == "__main__":
    google_urls = get_urls('advocacia', 100, 'pt-BR')
    output_file_path = r'C:\Users\guilh\Documents\contact-colector-scraper\emails.csv'
    
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MailSpider, start_urls=google_urls, output_path=output_file_path, reject=['oab', 'facebook', 'instagram', 'twitter'])
    process.start()
