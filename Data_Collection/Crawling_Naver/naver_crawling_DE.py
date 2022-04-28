from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # 스크롤을 내리기 위해 Import
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

driver = webdriver.Chrome('/Users/82104/Downloads/chromedriver_win32/chromedriver')
driver.implicitly_wait(1)
driver.maximize_window()

# 네이버 지도 사이트
driver.get("https://map.naver.com/v5/?c=14145551.7062195,4516768.6599434,15,0,0,0,dh")

search_contents = driver.find_element(by=By.XPATH, value="""/html/body/app/layout/div[3]/div[2]/shrinkable-layout/div/app-base/search-input-box/div/div[1]/div/input""")

# 가게 이름 list 만들어서 반복문 사용하면 될 듯!
search_contents.send_keys("뱃놈")
search_contents.send_keys(Keys.RETURN)
time.sleep(5)

# 해당 가게 클릭
store_button = driver.find_element(by=By.XPATH, value="""/html/body/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/salt-marker/div/button""").click()
time.sleep(5)

# 정보 페이지로 이동 (크롤링을 위한 frame 이동)
driver.switch_to.frame("entryIframe")

req = driver.page_source
soup = BeautifulSoup(req, 'html.parser')

### 가게 정보 crawling ###

# 가게 이름
store_name = soup.find("span",{"class":"_3ocDE"})
print(store_name.text)

# 가게 주소
address_information = soup.find("span", {"class": "_2yqUQ"})
address_text = address_information.text
print(address_text)

# 영업 시간 펼쳐보기 클릿
hour_button = driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper > div:nth-child(4) > div > div.place_section.no_margin > div > ul > li._1M_Iz._2KHqk > div > a')
hour_button.click()
time.sleep(10)

# 영업 시간 정보 (* 해결점(펼쳐보기를 눌렀음에도 불구하고 전체 시간 크롤링 실패))
store_running = soup.find("a", {"class": "_2BDci _1OkoP"})
print(store_running.text)

# menu tab 열기
menu_tab = driver.find_element(by=By.XPATH, value="""/html/body/div[3]/div/div/div[2]/div[3]/div/div/div/div/a[3]""")
menu_tab.click()
time.sleep(10)

# menu list (*첫번째 메뉴만 불러와짐)
menu = driver.find_element_by_css_selector(
        '#app-root > div > div > div.place_detail_wrapper > div:nth-child(5) > div > div.place_section.no_margin > div.place_section_content > ul > li:nth-child(2)').text
print(menu)

# review tab 열기
review_tab = driver.find_element(by=By.XPATH, value="""/html/body/div[3]/div/div/div[2]/div[3]/div/div/div/div/a[4]""")
review_tab.click()
time.sleep(10)

# review keyword 크롤링
review_keyword = driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper > div:nth-child(5) > div:nth-child(4) > div.place_section._11ptV > div > div > div._10UcK > ul > li:nth-child(1) > div._3ZEZK > span._1lntw')
print(review_keyword.text)
time.sleep(10)

# 각 keyword에 대한 사람들 선택 숫자 크롤링 (*같은 태그로 되어 있어서 대표 숫자만 불러와짐)
review_keyword_count = driver.find_element_by_css_selector("span.Nqp-s")
print(review_keyword_count.get_attribute('innerText'))

driver.close()
