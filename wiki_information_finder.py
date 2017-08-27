# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 19:24:56 2017

@author: abhil
"""

import requests
import json
import codecs
from bs4 import BeautifulSoup
from datetime import datetime
import os.path
import hashlib

def cache_page(url, page):
    hash_object = hashlib.md5(url.encode())
    filename = 'cache_' + hash_object.hexdigest() + '.json'
    
    with codecs.open(filename, 'w', 'utf-8-sig') as f:
        f.write(str(page.content))
    f.closed
    
def get_page(url):
    status = False
    hash_object = hashlib.md5(url.encode())
    filename = 'cache_' + hash_object.hexdigest() + '.json'
    
    if os.path.exists(filename):
        with codecs.open(filename, 'r', 'utf-8-sig') as f:
            page = f.read()
        f.closed
        status = True
    else:
        page = requests.get(url)
        if page.status_code == 200:
            cache_page(url, page)
            page = page.content
            status = True
        
    return status, page
    
def get_info(url):
    info = ''
    status, wiki_page = get_page(url)
    
    if status:
        wiki_soup = BeautifulSoup(wiki_page, 'html.parser')
        info_tables = wiki_soup.find_all('table', { 'class': 'infobox vcard' })
        if len(info_tables) == 0:
            info = 'infobox vcard not found'
        else:
            for info_table in info_tables:
                info = info + '\n' + str(info_table)
    else:
        info = 'error connecting'
    
    return info
    
def find_related_links(link):
    urls = []
    
    status, page = get_page(link)
    
    if status:
        soup = BeautifulSoup(page, 'html.parser')
        related_links = soup.find_all('a')
        
        for related_link in related_links:
            flag = False
            for attr in related_link.attrs:
                if attr == 'href':
                    flag = True
                    break
            if flag == True:
                if related_link['href'].startswith('/wiki/'):
                    urls.append(related_link['href'])
                
    return urls

# Starting Point
start = datetime.now()
print('Started app: ' + str(start))

wiki_url = 'https://en.wikipedia.org'
url_part = '/wiki/Main_Page'
depth = 10000

full_url = wiki_url + url_part

page = requests.get(full_url)
soup = BeautifulSoup(page.content, 'html.parser')
links = soup.find_all('a')
urls = []
data = {}
url_index = 0
urls.append(full_url)

while len(urls) < depth:
    print('Current depth: ' + str(len(urls)))
    
    related_links = find_related_links(urls[url_index])
    url_index = url_index + 1
    
    print('Related urls found: ' + str(len(related_links)))
    for related_link in related_links:
        if related_link not in urls:
            urls.append(wiki_url + related_link)

with codecs.open('data.json', 'w', 'utf-8-sig') as f:
    for url in urls:
        data['url'] = url
        data['info'] = get_info(url)
        json.dump(data, f)
f.closed

end = datetime.now()
print('Ended app: ' + str(end))

