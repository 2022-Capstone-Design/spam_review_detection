'''
    [file]
    Naver_Crawler.py :: RS에 필요한 가게 정보 크롤링
        Extraction DATA :: 리뷰 카테고리 데이터(몇 명 참여, 해당 카테고리 투표결과)
                            영업 시간
                            주소
                            기재된 가게 종류
                            리뷰 상위 10개

'''

from selenium import webdriver
from selenium.webdriver.common.keys import Keys  # 스크롤을 내리기 위해 Import
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import requests

'''
    [class]
    Crawl_Naver :: Naver 가게 정보 데이터 crawling
'''


class Crawl_Naver:
    def __init__(self):
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 naver map 이동
        '''

        # 관련 list 초기화
        self.Load_info()
        self.store_names = []                       # 가게 이름
        self.locations = []                         # 가게 위치
        self.open_times = []                        # 영업 시간
        self.food_infos = []                        # 기재된 가게 종류
        self.review_category_datas = []             # 리뷰 카테고리 데이터
        self.participants = []                      # 리뷰 카테고리 참여자
        self.reviews_TOP10 = []                     # 리뷰 상위 10개
        
        # chrome 가상 driver 열기
        self.driver = webdriver.Chrome('/Users/eesun/Downloads/chromedriver')     

        # 네이버 지도 사이트 이동
        self.driver.get("https://map.naver.com/v5/?c=14145551.7062195,4516768.6599434,15,0,0,0,dh")
        self.driver.implicitly_wait(5)


        print("\n------- crawling할 가게 info -------")
        print("추출할 가게 데이터 개수 :", len(self.name_list))
        print(self.name_list)
        print("-----------------------------------\n")

        self.go_to_page('뱃놈')
        # self.crawling()


    # def __del__(self):
    #     '''
    #     __del__() : 소멸자 함수
    #                 프로젝트 실행 후 chrome webdriver close
    #     '''

    #     self.driver.close()


    def Load_info(self):
        '''
        Load_info() : 가게 이름과 ID를 list 형태로 반환
            input parameter : None
            output : (list)Name, (list)ID
        '''

        file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
        csv_file = pd.read_csv(file_name)

        self.id_infos = csv_file['id'].tolist()             # 가게 아이디 List
        self.name_list = csv_file['name'].tolist()               # 가게 이름 List        
        

    def crawling(self):
        '''
        crawling() : naver data crawling 전체 코드
                    가게 개수만큼 페이지 이동 -> 데이터 추출 진행 -> 저장
                input parameter : None
                output : 가게 개수 데이터 추출한 list 반환
        '''
        for keyword in self.name_list:
            self.go_to_page(keyword)
        
        self.save_data()


    def go_to_page(self, keyword):
        '''
        go_to_page() : keyword 관련 페이지 이동 -> 데이터 추출
            input parameter : (str)keyword
            output : None
        '''

        store_btn_css = '#baseMap > div:nth-child(1) > div > div.mapboxgl-canvas-container.mapboxgl-interactive > div > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > salt-marker > div > button'

        search_contents = self.driver.find_element(by=By.XPATH, value="""/html/body/app/layout/div[3]/div[2]/shrinkable-layout/div/app-base/search-input-box/div/div[1]/div/input""")
        search_contents.send_keys(keyword)
        search_contents.send_keys(Keys.ENTER)
        time.sleep(2)

        # 해당 가게 클릭
        # store_btn = self.driver.find_element(by=By.XPATH, value="""/html/body/div[1]/div[1]/div/div[1]/div[3]/div[2]/div[1]/salt-marker/div/button""")
        store_btn = self.driver.find_element_by_css_selector(store_btn_css)
        store_btn.click()
        time.sleep(2)

        # 정보 페이지로 이동 (크롤링을 위한 frame 이동)
        # self.driver.switch_to.frame("entryIframe")
        # req = self.driver.page_source
        # self.soup = BeautifulSoup(req, 'html.parser')

        ## 데이터 추출 함수 선언
        self.data_extraction()


    def data_extraction(self):
        '''
        data_extraction() : 가게 정보 crawling
                    [Extraction DATA]
                            리뷰 카테고리 데이터(몇 명 참여, 해당 카테고리 투표결과)
                            영업 시간
                            주소
                            기재된 가게 종류
                            리뷰 상위 10개
            input parameter : None
            output : None
        '''

        location_object_css = '#app-root > div > div > div > div:nth-child(5) > div > div.place_section.no_margin._18vYz > div > ul > li._1M_Iz._1aj6- > div'
        open_time_btn_css = '#app-root > div > div > div > div:nth-child(5) > div > div.place_section.no_margin._18vYz > div > ul > li._1M_Iz._2KHqk > div > a > div > div > span'
        open_time_object_css = '#app-root > div > div > div > div:nth-child(5) > div > div.place_section.no_margin._18vYz > div > ul > li._1M_Iz._2KHqk'
        food_info_object_css = '#_title > span._3ocDE'
        # food_info_object_class = '_3ocDE'
        review_page_href_css = '#app-root > div > div > div > div:nth-child(6) > div > div.place_section.nQcjn > div'
        # review_page_href_css = '#app-root > div > div > div > div:nth-child(6) > div > div.place_section.nQcjn > div > div._2ItDC > a'
        participant_obejct_css = '#app-root > div > div > div > div:nth-child(5) > div:nth-child(3) > div.place_section._11ptV > div > div > div._3zxNp > span'
        review_category_ul_css = '#app-root > div > div > div > div:nth-child(6) > div:nth-child(4) > div.place_section._11ptV > div > div > div._10UcK > ul'
        review_data_ul_css = '#app-root > div > div > div > div:nth-child(6) > div:nth-child(4) > div.place_section.cXO6M > div.place_section_content > div > ul'

        # [data extraction]
        # 위치 정보
        try:
            location_object = self.driver.find_element_by_css_selector(location_object_css)
            location = location_object.text
        except:
            location = None
        
        print("location :",location)
        
        
        # 가게 대표 메뉴
        try:
            food_info_object = self.driver.find_element_by_css_selector(food_info_object_css)
            food_info = food_info_object.text
        except:
            food_info = None
        print("food_info :",food_info)

        # 영업시간
        try:
            open_time_btn = self.driver.find_element_by_css_selector(open_time_btn_css)
            open_time_btn.click()
            try:
                open_time_object = self.driver.find_element_by_css_selector(open_time_object_css)
                open_time = open_time_object.text
            except:
                open_time = None
        except:
            open_time = 'No BTN'
        print("open_time :", open_time)
        

        # 리뷰 href html parser
        review_page_obejct = self.driver.find_element_by_css_selector(review_page_href_css)
        review_page_href = review_page_obejct.get_attribute('href')
        print(review_page_href)
        self.driver.get(review_page_href)
        self.driver.implicitly_wait(5)
        # response = requests.get(review_page_href)
        # html = response.text
        # self.soup = BeautifulSoup(html, 'html.parser')

        # 리뷰 카테고리
        review_category = []
        try:
            participant_object = self.driver.find_element_by_css_selector(participant_obejct_css)
            participant = participant_object.text
            # 리뷰 카테고리 투표 결과
            #app-root > div > div > div > div:nth-child(5) > div:nth-child(3) > div.place_section._11ptV > div > div > div._10UcK > ul > li:nth-child(1)
            #app-root > div > div > div > div:nth-child(5) > div:nth-child(3) > div.place_section._11ptV > div > div > div._10UcK > ul > li:nth-child(2)
            #app-root > div > div > div > div:nth-child(6) > div:nth-child(4) > div.place_section._11ptV > div > div > div._10UcK > ul > li:nth-child(12)
            review_category_ul = self.driver.find_element_by_css_selector(review_category_ul_css)
            review_categories = review_category_ul.find_elements_by_css_selector('li')
            print(review_categories)
            # for review in review_categories:
            #     review_category.append(review.text))
            '''
            # 참가자
            participant_object = self.soup.select_one(participant_obejct_css)
            participant = participant_object.get_text()
            # 리뷰 카테고리 투표 결과
            review_category_ul = self.soup.select_one(review_category_ul_css)
            review_categories = review_category_ul.select('li > div')
            for review in review_categories:
                review_category.append(review.get_text())
            '''
        except:
            participant = None
            review_category = None
        print("participant :", participant)
        print("review_category :", review_category)

        # 리뷰 상위 10개
        review_list = []
        try:
            review_data_ul = self.driver.find_element_by_css_selector(review_data_ul_css)
            review_datas = review_data_ul.find_elements_by_css_selector('li > div._3vfQ6')
            print(review_datas)
            # for review in review_datas:
            #     review_list.append(review.get_text())   
            '''
            review_data_ul = self.soup.select_one(review_data_ul_css)
            review_datas = review_data_ul.select('li > div._3vfQ6')
            for review in review_datas:
                review_list.append(review.get_text())    
            '''        
        except:
            review_list = None
        print('review_TOP10 :', review_list)


        print("\n---------- INFO ----------")
        print("location :",location)
        print("food_info :",food_info)
        print("open_time :", open_time)
        print("participant :", participant)
        print("review_category :", review_category)
        print('review_TOP10 :', review_list)
        print("--------------------------\n")


        self.locations.append(location)                          # 가게 위치
        self.food_infos.append(food_info)                        # 기재된 가게 종류
        self.open_times.append(open_time)                        # 영업 시간
        self.participants.append(participant)                    # 리뷰 카테고리 참여자
        self.review_category_datas.append(review_category)       # 리뷰 카테고리 데이터
        self.reviews_TOP10.append(review_list)                   # 리뷰 상위 10개



        '''
        
        
        ## 가게 대표 메뉴
        food_info_object = self.soup.find("span",{"class":"_3ocDE"})
        food_info = food_info_object.text

        ## 가게 위치
        location_object = self.soup.find("span", {"class": "_2yqUQ"})
        location = location_object.text

        ## 영업 시간
        # 펼쳐보기 클릭
        hour_button = self.driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper > div:nth-child(4) > div > div.place_section.no_margin > div > ul > li._1M_Iz._2KHqk > div > a')
        hour_button.click()
        time.sleep(2)
        # 영업 시간 정보 (* 해결점(펼쳐보기를 눌렀음에도 불구하고 전체 시간 크롤링 실패))
        open_time_object = self.soup.find("a", {"class": "_2BDci _1OkoP"})
        open_time = open_time_object.text



        print("영업시간 :", open_time)
        print("가게위치 :", location)
        print("대표메뉴 :", food_info)

        ## review
        # review tab 열기
        review_tab = self.driver.find_element(by=By.XPATH, value="""/html/body/div[3]/div/div/div[2]/div[3]/div/div/div/div/a[4]""")
        review_tab.click()
        time.sleep(3)

        # review keyword 크롤링
        review_keyword = self.driver.find_element_by_css_selector('#app-root > div > div > div.place_detail_wrapper > div:nth-child(5) > div:nth-child(4) > div.place_section._11ptV > div > div > div._10UcK > ul > li:nth-child(1) > div._3ZEZK > span._1lntw')
        print(review_keyword.text)
        time.sleep(3)

        # 각 keyword에 대한 사람들 선택 숫자 크롤링 (*같은 태그로 되어 있어서 대표 숫자만 불러와짐)
        review_keyword_count = self.driver.find_element_by_css_selector("span.Nqp-s")
        print(review_keyword_count.get_attribute('innerText'))
        '''

            


    def save_data(self):
            '''
            save_data() : 추출한 데이터 csv 파일로 저장
                input parameter : None
                output : (DF)save
            '''

            save_file_name = "Naver_data"
            
            try:
                # data list를 dataframe으로 변환 후 csv로 저장
                naver_data_df = pd.DataFrame({"ID":self.id_infos, "store_name":self.name_list, "food_info":self.food_infos,
                                            "location":self.locations, "open_time":self.open_times, 
                                            "review_category_datas":self.review_category_datas, "participants":self.participants,
                                            "reviews_top10":self.reviews_TOP10})
                naver_data_df.to_csv("Data_Collection/Crawling_Naver/{}.csv".format(save_file_name), 
                                        index=False, encoding='utf-8')

                print("\nNaver 가게 데이터 저장 완료!")
                
            except:
                print("\nfail total save data\n")




if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    naver_data = Crawl_Naver()