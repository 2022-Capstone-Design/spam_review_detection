from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests
import shutil

baseUrl = "https://www.instagram.com/explore/tags/"
plusUrl = input("검색어를 입력하세요")
url = baseUrl + quote_plus(plusUrl)

driver = webdriver.Chrome()
driver.get(url)
time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

insta = soup.select('v1Nh3.kIKUG._bz0w')

n = 1
for i in insta:
    print('https://www.instagram.com' + i.a['href'])
    imgUrl = i.select_one('_9AhH0').img['src']

    with urlopen(imgUrl) as f:
        with open('./img/' + plusUrl + str(n) + '.jpg', 'wb') as h:
            img = f.read()
            h.write(img)
        n += 1

driver.close()