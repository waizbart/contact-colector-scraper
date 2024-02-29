import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from googlesearch import search

N_URL = 20  # Número de URLs inicialmente coletadas
N_URL_SKIP = 0  # Número de URLs a serem ignoradas no início da busca
EMAILS = True # Coletar emails?
PHONE_NUMBERS = True # Coletar números de telefone?
TERMO_BUSCA = 'sympla' # Termo a ser buscado
DEPTH_LIMIT = 1  # Profundidade máxima de busca, 0 para ilimitado

def get_urls(tag, n, language):
    all_urls = list(search(tag, num_results=n+N_URL_SKIP, lang=language)) 
    urls = all_urls[N_URL_SKIP:n+N_URL_SKIP]  
    return urls
class MailSpider(scrapy.Spider):
    name = 'email'
    
    def __init__(self, start_urls, output_path, reject):
        self.start_urls = start_urls
        self.output_path = output_path
        self.reject = reject
        self.emails = set() 
        self.phones = set()
    
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
        phone_list = re.findall(r'\(?\d{2}\)?\s\d{4,5}[- ]?\d{4}', html_text)

        if EMAILS:
            self.emails.update(mail_list)
            
        if PHONE_NUMBERS:
            self.phones.update(phone_list)

    def closed(self, _):
        emails_list = list(self.emails)
        phones_list = list(self.phones)
        
        if EMAILS:
            df = pd.DataFrame({ 'Emails': emails_list })
            df.to_csv(self.output_path + r'\emails.csv', index=False, header=False)
        if PHONE_NUMBERS:
            df = pd.DataFrame({ 'Phones': phones_list })
            df.to_csv(self.output_path + r'\phones.csv', index=False, header=False)

if __name__ == "__main__":
    google_urls = get_urls(TERMO_BUSCA, N_URL, 'pt-BR')
    
    output_file_path = r'C:\Users\guilh\Documents\contact-colector-scraper'
    
    settings = {
        'USER_AGENT': 'Mozilla/5.0', 
        }
    
    if DEPTH_LIMIT > 0:
        settings['DEPTH_LIMIT'] = DEPTH_LIMIT
    
    process = CrawlerProcess()
    process.crawl(MailSpider, start_urls=google_urls, output_path=output_file_path, reject=['whatsapp ', 'facebook', 'instagram', 'twitter'])
    process.start()
