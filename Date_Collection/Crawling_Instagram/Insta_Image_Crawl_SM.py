from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import requests
import shutil

from selenium.webdriver import ActionChains

driver = webdriver.Chrome()
driver.get('https://www.instagram.com/')
time.sleep(2)

id_box = driver.find_element_by_css_selector('#loginForm > div > div:nth-child(1) > div > label > input')
password_box = driver.find_element_by_css_selector('#loginForm > div > div:nth-child(2) > div > label > input')
login_button = driver.find_element_by_css_selector('#loginForm > div > div:nth-child(3) > button')

act = ActionChains(driver)

act.send_keys_to_element(id_box, 'suthink__').send_keys_to_element(password_box, 'wkd!!tnaud11').click(login_button).perform()
time.sleep(3)

driver.find_element_by_css_selector('.sqdOP.yWX7d.y3zKF').click()
time.sleep(3)

driver.find_element_by_css_selector('.aOOlW.HoLwm').click()
time.sleep(3)




baseUrl = "https://www.instagram.com/explore/tags/"
plusUrl = input("검색어를 입력하세요")
url = baseUrl + quote_plus(plusUrl)

#driver = webdriver.Chrome()
driver.get(url)
time.sleep(6)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

insta = soup.select('.v1Nh3.kIKUG._bz0w')
print(insta[0])
#driver.close()

n = 1
for i in insta:
    print('https://www.instagram.com' + i.a['href'])
    try:
        imgUrl = i.select_one('_9AhH0').img['src']
    except Exception as e:
        continue

    with urlopen(imgUrl) as f:
        with open('./img/' + plusUrl + str(n) + '.jpg', 'wb') as h:
            img = f.read()
            h.write(img)
    n += 1
    print(imgUrl)
    print()

driver.close()