import pandas as pd
import numpy as np
from bs4 import BeautifulSoup              
from selenium import webdriver             # selenium module import
from selenium.webdriver.common.keys import Keys
import requests
import time
import re

'''
    [class]
    Crawl_Insta :: Instagram API를 활용해 해시태그 별 게시물 1000개씩 crawling
            crawling data  - 작성자, 위치, 게시글(사진, 텍스트), 작성 날짜, 댓글
'''


class Crawl_Insta:

    def __init__(self): 
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 네이버 금융 사이트 열기
        '''

        
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--diable-dev-shm-usage")
        self.options.add_argument("user-agent={Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36}")

        # chrome 가상 driver 열기
        self.driver = webdriver.Chrome('/Users/eesun/Downloads/chromedriver', options = self.options)
        self.driver.implicitly_wait(1)
        self.driver.maximize_window()

        # instagram site url 열기
        self.driver.get("")
        self.driver.implicitly_wait(1)

        # data를 저장할 csv - 작성자 Id, 위치, 작성 날짜, 이미지 게시글, 텍스트 게시글, 댓글
        self.insta_data = pd.DataFrame(columns={"writer_id", "location", "date", "image", "text", "comment"})


    def __del__(self):   
        '''
        __del__() : 소멸자 함수
                    crawling 작업이 끝난 후 chrome webdriver 닫기
        '''
        
        self.driver.close()       


    def enter_keyword(self, keyword):
        '''
        enter_keyword() : 크롤링 할 hashtag 입력
            input parameter : (str)keyword
            output : None
        '''

        # 검색창 찾기
        search_btn = self.driver.find_element_by_xpath('//*[@id="stock_items"]')

        # keyword 검색
        search_btn.send_keys(keyword)
        self.driver.implicitly_wait(3)

        # Enter
        search_btn.send_keys(Keys.ENTER)    
    

    def data_extraction(self, keyword):  
        '''
        data_extraction() : keyword 관련 instagram data crawling
            input parameter : (str)keyword
            output : (csv)[keyword]instagram_data
        '''

                                     
        # data를 csv 파일로 저장  
        insta_df = pd.DataFrame(self.insta_data)
        insta_df.to_csv('['+keyword+ "]instagram_data.csv", index = False, header = True)


if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    insta_data = Crawl_Insta()
    
    # keyword 입력
    print("크롤링할 해시태그를 입력해주세요")
    print("ex) '#맛집' 해시태그를 검색하려면 '맛집'이라고 입력")
    keyword = input("Input HashTag : ")
    keyword = '#'+keyword
    insta_data.enter_keyword(keyword)

    # keyword 관련 instagram 데이터 crawling
    insta_data.data_extraction(keyword)
