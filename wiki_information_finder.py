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

def get_caption(table):
    return table.caption.text;

def get_personal_info_json(table):
    personal_info_json = {}
    personal_info_str = ''
    
    rows = table.find_all('tr')
    
    for row in rows:
        if len(row.find_all('th')) != 0:
            attrs = row.th.attrs
            
            flag = False
            for attr in attrs:
                if attr == 'scope':
                    flag = True
                    break
            
            if flag == True:
                if row.th['scope'] == 'row':
                    key = row.th.text.replace('\n', ' ').replace('  ', ' ').replace('|', ' ').replace('=', '')
                    value = row.td.text.replace('\n', ' ').replace('  ', ' ').replace('|', ' ').replace('=', '')
                    personal_info_str = personal_info_str + key
    return personal_info_json

def get_info(url):
    info = ''
    wiki_page = requests.get(url)
    
    if wiki_page.status_code == 200:
        wiki_soup = BeautifulSoup(wiki_page.content, 'html.parser')
        info_tables = wiki_soup.find_all('table', { 'class': 'infobox vcard' })
        if len(info_tables) == 0:
            info = 'infobox vcard not found'
        else:
            for info_table in info_tables:
                info = info + str(info_table)
                '''
                with codecs.open('data.html', 'a', 'utf-8-sig') as f:
                    f.write(str(info_table))
                f.closed
                '''
    else:
        info = 'error connecting'
    
    return info

def find_related_links(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    related_links = soup.find_all('a')
    urls = []
    
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
wiki_url = 'https://en.wikipedia.org'
url_part = '/wiki/Main_Page'
depth = 1000

full_url = wiki_url + url_part

page = requests.get(full_url)
soup = BeautifulSoup(page.content, 'html.parser')
links = soup.find_all('a')
urls = []
data = {}

while len(urls) < depth:
    related_links = find_related_links(full_url)
    for related_link in related_links:
        if related_link not in urls:
            urls.append(related_link)

with codecs.open('data.json', 'a', 'utf-8-sig') as f:
    for url in urls:
        data['url'] = url
        data['info'] = get_info(wiki_url + url)
        json.dump(data, f)
f.closed        
