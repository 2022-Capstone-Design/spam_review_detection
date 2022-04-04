'''
    [file]
    Final_Insta_Crawler_byID.py :: project에 필요한 데이터만을 추출(최종본)
                                광고데이터 수집 - 광고 계정으로 이동
'''

from bs4 import BeautifulSoup              
from selenium import webdriver             # selenium module import
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import time
import re
import json
import pandas as pd
import numpy as np
import random
from config_ES import user_id, user_pw




'''
    [class]
    Crawl_Insta :: Instagram API를 활용해 해시태그 별 게시물 지정 개수씩 crawling
            crawling data  - 게시글(텍스트)
'''


class Crawl_Insta:

    def __init__(self): 
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 Instagram login url 열기
        
        [data column 정보]
            main_text : 게시물 본문(text)
        '''

        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--diable-dev-shm-usage")
        self.options.add_argument("user-agent={Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36}")

        # chrome 가상 driver 열기
        self.driver = webdriver.Chrome('/Users/eesun/Downloads/chromedriver', options = self.options)
        self.driver.implicitly_wait(1)
        # self.driver.maximize_window()

        # [사용 변수 및 file]
        self.is_login_success = False                        # login 성공 여부
        self.count_extract = 0                               # 현재 crawlng한 게시물 개수 count
        self.update_num = 50                                 # 중간 저장 게시글 개수
        self.update_fix_num = self.update_num                # 중간 저장 고정 게시물 개수 (몇 개씩 끊어서 저장할 것인지)
        self.wish_num = 100                                  # 최종적으로 crawling할 게시물 개수
        self.check_next = True                               # 다음 버튼이 있는지 확인
        self.save_cnt = 0                                    # 저장 version
        self.print_flag = True                               # True면 추출한 데이터 출력
        self.ad_id = 'seoul__foodie'                         # crawling할 광고 계정 아이디 이름
        ## 저장할 데이터 list
        self.upload_ids = []                                 # 작성자 id
        self.main_texts = []                                 # 게시글 텍스트


        print("\n------- data extraction info -------")
        print("추출할 데이터 개수 :", self.wish_num)
        print("중간 저장 데이터 개수 :", self.update_fix_num)
        print("-----------------------------------\n")


        # instagram site login url 열기
        url = "https://www.instagram.com/accounts/login"    # url 이동
        self.driver.get(url)
        self.driver.implicitly_wait(3)

        # [NEXT STEP _1] login 함수 호출
        self.login()                                        # 로그인 시도
        self.driver.implicitly_wait(3)

        
    def __del__(self):   
        '''
        __del__() : 소멸자 함수
                    crawling 작업이 끝난 후 chrome webdriver 닫기
        '''
        
        self.driver.close()


    '''
    다음 action 전 random으로 time sleep 주기
        delay_until_next_step() 
        make_random_sleep_time()
    '''
    def delay_until_next_step(self, start,end):
        time.sleep(self.make_random_sleep_time(start=start, end=end+1))
    
    def make_random_sleep_time(self, start, end):
        return random.randrange(start=start, stop=end+1)
           
    
    def login(self):
        '''
        login() : instagram login 함수
            input parameter : None
            output : None
        '''

        # login하기 위한 id명 및 Xpath명
        instagram_id_name = "username"                                      # login 아이디 id명
        instagram_pw_name = "password"                                      # login 비밀번호 id명
        instagram_login_btn_path = '//*[@id="loginForm"]/div/div[3]/button' # login 버튼 Xpath명

        # login 정보 입력
        try:
            # id 입력
            instagram_id_form = self.driver.find_element_by_name(instagram_id_name)
            instagram_id_form.send_keys(user_id)
            time.sleep(2)

            # pw 입력
            instagram_pw_form = self.driver.find_element_by_name(instagram_pw_name)
            instagram_pw_form.send_keys(user_pw)
            time.sleep(2)

            # 로그인 버튼 클릭
            login_button = self.driver.find_element_by_xpath(instagram_login_btn_path)
            login_button.click()
            time.sleep(5)
            self.is_login_success = True
        except:
            print("Instagram login fail")
            self.is_login_success = False
        
         # [NEXT STEP _ 2] url page 이동
        if self.is_login_success:
            self.go_to_url() 
            self.driver.implicitly_wait(3)


    def go_to_url(self):
        '''
        go_to_url() : Url 이동
            input parameter : url
            output : None
        '''

        # 해당하는 url로 이동
        ad_url = 'https://www.instagram.com/{}/'.format(self.ad_id)
        self.driver.get(ad_url)
        self.delay_until_next_step(start = 3, end = 5)

        # [NEXT STEP _ 3] 데이터 추출
        self.data_extraction(keyword ='AD')


    def data_extraction(self, keyword):  
        '''
        data_extraction() : keyword 관련 instagram data crawling
                            첫번째 게시글 클릭 후 다음 버튼 누르면 됨
            input parameter : (str)keyword - AD
            output : (csv)keyword_instagram_data
        '''

        '''
        [data column 정보]
            main_text : 게시물 본문(text)
        '''

        try:
            # 첫번째 게시물 클릭
            first_img_css = '#react-root > section > main > div > div._2z6nI > article > div:nth-child(1) > div > div:nth-child(1) > div:nth-child(1) > a > div.eLAPa'
            self.driver.find_element_by_css_selector(first_img_css).click()

            self.delay_until_next_step(start=5,end=7)
        except:
            print("--------- 게시물이 없습니다! ---------")
            pass

        # data crawling
        ## crawling object css
        main_text_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > div > li > div > div > div.C4VMK > div.MOdxS > span"
        next_btn_css1 = 'body > div.RnEpo._Yhr4 > div.Z2Inc._7c9RR > div > div.l8mY4.feth3 > button'


        # data extraction
        while True:
            if self.count_extract > self.wish_num:
                # self.save_data(keyword)
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                break

            self.delay_until_next_step(start=4, end=7)

            if self.check_next == False:
                self.save_data(keyword)
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                break

            # 본론 text extraction
            try:
                main_text_object = self.driver.find_element_by_css_selector(main_text_object_css)
                main_text = main_text_object.text
            except:
                main_text = None

            # 추출한 데이터를 dataframe에 추가
            self.main_texts.append(main_text)

            # 추출한 데이터 출력
            if self.print_flag:
                print("\n---------- INFO ----------")
                print("main :", main_text)
                print("--------------------------\n")

            # 지정된 개수씩 csv로 저장
            self.count_extract += 1
            if self.update_num == self.count_extract:
                self.update_num += self.update_fix_num
                self.save_data(keyword)
            
            # 다음 게시물로 넘어가기
            try:
                WebDriverWait(self.driver, 100).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, next_btn_css1)))
                time.sleep(5)
                print("\n잘 기다렸다 !\n")
                next_btn = self.driver.find_element_by_css_selector(next_btn_css1)
                next_btn.send_keys(Keys.ENTER)
                self.check_next = True
            except:
                self.check_next = False
                print("\n버튼 작동 X\n")


    def save_data(self,keyword):
        '''
        save_data() : 추출한 데이터 csv 파일로 저장
            input parameter : (str)keyword - AD
            
        '''
        self.save_cnt += 1
        save_file_name = 'Data_Collection/Crawling_Instagram/Data/{}({})_instagram_data_{}'.format(keyword, self.ad_id, str(self.save_cnt))
        
        try:
            # data list를 dataframe으로 변환 후 csv로 저장
            instagram_data_df = pd.DataFrame({"writer_id":self.ad_id, "main_text":self.main_texts})
            instagram_data_df.to_csv("{}.csv".format(save_file_name), index=False)

            # data list 초기화
            self.main_texts = []
            
        except:
            print("\nfail total save data\n")

        

if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    insta_data = Crawl_Insta()