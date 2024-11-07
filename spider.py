import os
import pandas as pd
import re
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

try:
    from googlesearch import search
except ImportError:
    print("O módulo 'googlesearch' não está instalado. Instale com 'pip install googlesearch-python'.")

def get_urls(tag, n, n_skip, language):
    all_urls = list(search(tag, num_results=n + n_skip, lang=language))
    urls = all_urls[n_skip:]
    return urls

class LeadSpider(scrapy.Spider):
    name = 'lead-spider'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0',
        'ROBOTSTXT_OBEY': False,
    }

    def __init__(self, start_urls, output_path, reject, emails, phones, *args, **kwargs):
        super(LeadSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.output_path = output_path
        self.reject = reject
        self.collect_emails = emails
        self.collect_phones = phones
        self.emails = set()
        self.phones = set()

    def parse(self, response):
        links = LxmlLinkExtractor(allow=(), deny=self.reject).extract_links(response)
        links = [str(link.url) for link in links]
        links.append(str(response.url))

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_link)

    def parse_link(self, response):
        try:
            html_text = response.text

            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            mail_list = re.findall(email_pattern, html_text)

            phone_pattern = r'(?:\+?(\d{1,3})[-.\s]?)?(?:\(?(\d{2,4})\)?[-.\s]?)?(\d{4,5}[-.\s]?\d{4})'
            phone_list_matches = re.findall(phone_pattern, html_text)
            phone_list = [''.join(match) for match in phone_list_matches]

            if self.collect_emails:
                self.emails.update(mail_list)

            if self.collect_phones:
                self.phones.update(phone_list)

        except Exception as e:
            self.logger.error(f"Erro ao processar {response.url}: {e}")

    def closed(self, reason):
        if self.collect_emails and self.emails:
            emails_list = list(self.emails)
            df_emails = pd.DataFrame({'Emails': emails_list})
            df_emails.to_csv(os.path.join(self.output_path, 'emails.csv'), index=False, header=False)

        if self.collect_phones and self.phones:
            phones_list = list(self.phones)
            df_phones = pd.DataFrame({'Phones': phones_list})
            df_phones.to_csv(os.path.join(self.output_path, 'phones.csv'), index=False, header=False)
