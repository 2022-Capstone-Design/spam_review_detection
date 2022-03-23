# 이미지가 저장될 img 폴더가 존재해야함
# 우선은 이미지 추가하는 스크롤 기능 미사용
# 일부러 URL 출력되도록 만들어놓았음 --> 출력 부분 삭제해야함

from urllib.request import urlopen
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
import time
import requests
import shutil

driver = webdriver.Chrome()
driver.get('https://www.instagram.com/')
time.sleep(2)

#로그인
id_box = driver.find_element_by_css_selector\
    ('#loginForm > div > div:nth-child(1) > div > label > input')
password_box = driver.find_element_by_css_selector\
    ('#loginForm > div > div:nth-child(2) > div > label > input')
login_button = driver.find_element_by_css_selector\
    ('#loginForm > div > div:nth-child(3) > button')

act = ActionChains(driver)

act.send_keys_to_element(id_box, 'suthink__')\
    .send_keys_to_element(password_box, 'wkd!!tnaud11')\
    .click(login_button).perform()
time.sleep(3)

#로그인 정보 저장 나중에 하기
driver.find_element_by_css_selector('.sqdOP.yWX7d.y3zKF').click()
time.sleep(3)
#알림설정 나중에 하기
driver.find_element_by_css_selector('.aOOlW.HoLwm').click()
time.sleep(2)

#로그인 완료
#tag 입력받기
baseUrl = "https://www.instagram.com/explore/tags/"
plusUrl = input("검색어를 입력하세요")
url = baseUrl + quote_plus(plusUrl)

driver.get(url)
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

insta = soup.select('.v1Nh3.kIKUG._bz0w')
#print(insta[0])

n = 1
for i in insta:
    print('https://www.instagram.com' + i.a['href'])

    imgUrl = i.img['src']
    # 예외처리?
    """
    try:
        imgUrl = i.select_one('KL4Bh').img['src']
    except AttributeError as e:
        continue
    """
    #이미지 저-장
    with urlopen(imgUrl) as f:
        with open('./img/' + plusUrl + str(n) + '.jpg', 'wb') as h:
            img = f.read()
            h.write(img)
    n += 1
    print(imgUrl)
    print()

driver.close()