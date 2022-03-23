import time
from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.request import urlopen
from urllib.parse import quote_plus

testUrl1 = "https://www.instagram.com/explore/tags"
testUrl2 = input("검색어를 입력하세요")
testUrl3 = testUrl1 + quote_plus(testUrl2)

driver01 = webdriver.Chrome()
driver01.get(testUrl3)

himl01 = driver01.page_source
Source01 = BeautifulSoup(himl01)

time.sleep(3)

Dem_insta = Source01.select('_9AhH0')

x = 1

for i in insta:
    print("https://www.instagram.com/" + i.a['href'])
    img01 = i.select_one()