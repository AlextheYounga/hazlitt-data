from app.lab.scrape.scraper import Scraper
from app.lab.core.functions import readTxtFile, is_date
import datetime
from dateutil.parser import parse
import colored
from colored import stylize
import time
import sys
import json
import django
from django.apps import apps


BLACKLISTWORDS = 'app/lab/news/data/blacklist_words.txt'
BLACKLISTPAGES = 'app/lab/news/data/blacklist_pages.txt'
CURATED = 'app/lab/news/data/curated.txt'
PAYWALLED = 'app/lab/news/data/paywalled.txt'
URL = 'https://news.google.com/'

class GoogleNews():
    def __init__(self, url=URL):
        self.url = url

    def collectNewsCards(self, searchq):
        scrape = Scraper()                              
        response = scrape.search(searchq)        
        print(stylize(f"Grabbing links {searchq}", colored.fg("yellow")))
        time.sleep(1)
        if (response.ok):
            soup = scrape.parseHTML(response)
            card_soup = soup.find_all('article')
            print(stylize(f"{len(card_soup)} articles found.", colored.fg("yellow")))
            return card_soup

    def scanLinks(self, card_soup):
        heap = []
        scrape = Scraper()
        for card in card_soup:
            link = card.find('a').attrs.get('href', False)
            if (link):
                headline = card.find('h3').text
                source = card.find_all('a')[2].text if (card.find_all('a')) else None
                pubDate = self.findPubDate(card)                    
                google_url = f"{self.url}{link.split('./')[1]}"
                
                page = scrape.search(google_url, useHeaders=False)
                if (page and (page.ok) and (self.checkLink(page.url))):
                    print(stylize(f"Searching {google_url}", colored.fg("yellow")))
                    page_soup = scrape.parseHTML(page)

                    newsitem = {
                        'url': page.url,
                        'headline': headline,
                        'pubDate': pubDate,
                        'source': source,
                        'author': self.findAuthor(page_soup),
                        'soup': page_soup
                    }
                    self.save(newsitem)
                    heap.append(newsitem)
                    time.sleep(1)
        return heap

    
    def checkLink(self, link):        
        blacklist_pgs = readTxtFile(BLACKLISTPAGES)
        for pg in blacklist_pgs:
            if (pg in link):
                return False
        return True
     

    def findAuthor(self, soup):
        
        def checkAuthor(author):
            badCharacters = ['facebook', '.']
            for bc in badCharacters:
                if (bc in author):
                    return None
            return author

        for meta in soup.head.find_all('meta'):
            for prop in ['property', 'name']:
                if ('author' in str(meta.attrs.get(prop))):
                    author = meta.attrs.get('content')
                    return checkAuthor(author)
        for tag in soup.body.find_all(['span', 'div', 'a', 'p']):
            classes = tag.attrs.get('class')
            if (classes):  
                for clas in list(classes):
                    if ('author' in clas):      
                        return checkAuthor(tag.text)
        return None

    
    def findPubDate(self, card):
        if (card):
            tag = card.find('time')
            if (tag and tag.attrs.get('datetime', False)):
                return tag.attrs.get('datetime', None)

    def save(self, newsitem):
        News = apps.get_model('database', 'News')
        News.objects.update_or_create(
            url=newsitem['url'],
            defaults = {
            'headline': newsitem.get('headline', None),
            'author': newsitem.get('author', None),
            'source': newsitem.get('source', None),
            'description': newsitem.get('description', None),
            'pubDate': newsitem.get('pubDate', None)}
        )
        print(stylize(f"Saved {(newsitem.get('source', False) or 'unsourced')} article", colored.fg("green")))