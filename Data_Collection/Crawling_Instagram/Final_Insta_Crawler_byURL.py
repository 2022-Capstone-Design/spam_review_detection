'''
    [file]
    Final_Insta_Crawler_byURL.py :: project에 필요한 데이터만을 추출(최종본)
                                url 받아와서 게시글 33개 추출
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
    Crawl_Insta :: Instagram API를 활용해 해시태그 별 게시물 33개씩 crawling
            crawling data  - 게시글 url, 작성자, 위치, 게시글(텍스트), 태그
'''


class Crawl_Insta:

    def __init__(self): 
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 Instagram login url 열기
        
        [data column 정보]
            post_url : 게시글 url
            writer_id : 작성자 id
            main_text : 게시물 본문(text)
            tag : 해시태그
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
        self.update_num = 33                                 # 중간 저장 게시글 개수
        self.update_fix_num = self.update_num                # 중간 저장 고정 게시물 개수 (몇 개씩 끊어서 저장할 것인지)
        self.wish_num = 33                                   # 최종적으로 crawling할 게시물 개수
        self.check_next = True                               # 다음 버튼이 있는지 확인
        self.save_cnt = 0                                    # 저장 version
        self.print_flag = True                               # True면 추출한 데이터 출력
        self.url_dict = {}                                   # crawling할 가게 이름(Key), url(value) 딕셔너리
        ## 저장할 데이터 list
        self.post_urls = []                                  # 게시글 url
        self.upload_ids = []                                 # 작성자 id
        self.main_texts = []                                 # 게시글 텍스트
        self.instagram_tags = []                             # 게시글 tag


        print("\n------- data extraction info -------")
        print("추출할 데이터 개수 :", self.wish_num)
        print("중간 저장 데이터 개수 :", self.update_fix_num)
        print("-----------------------------------\n")


        # instagram site login url 열기
        url = "https://www.instagram.com/accounts/login"    # url 이동
        self.driver.get(url)
        self.driver.implicitly_wait(3)

        # [NEXT STEP _ 1] 음식점 List를 dicinary로 저장
        self.list_url()
        print("\n음식점 개수 : %d개\n"%(len(self.url_dict)))

        # [NEXT STEP _2] login 함수 호출
        self.login()                                        # 로그인 시도
        self.driver.implicitly_wait(3)

        
    def __del__(self):   
        '''
        __del__() : 소멸자 함수
                    crawling 작업이 끝난 후 chrome webdriver 닫기
        '''
        
        self.driver.close()
        self.driver.quit()


    '''
    다음 action 전 random으로 time sleep 주기
        delay_until_next_step() 
        make_random_sleep_time()
    '''
    def delay_until_next_step(self, start,end):
        time.sleep(self.make_random_sleep_time(start=start, end=end+1))
    
    def make_random_sleep_time(self, start, end):
        return random.randrange(start=start, stop=end+1)
    

    def list_url(self):
        '''
        list_url() : 크롤링할 음식점 List가 담긴 csv 열고, 음식점이름(key)과 url(value)로 dictionary 생성
            input parameter : None
            output : None
        '''
        restaurant = pd.read_csv('Data_Collection/Crawling_Instagram/Data/가게조사_testt.csv')
        restaurant = restaurant.loc[:, ['id', 'url']]
        self.url_dict =restaurant.set_index('id').T.to_dict('list')
           
    
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
        
         # [NEXT STEP _ 3] url page 이동
        if self.is_login_success:
            self.go_to_url() 
            self.driver.implicitly_wait(3)


    def go_to_url(self):
        '''
        go_to_url() : Url 이동
            input parameter : url
            output : None
        '''

        for key, value in self.url_dict.items():
            # 해당하는 url로 이동
            rest_url = value[0]
            self.driver.get(rest_url)
            self.delay_until_next_step(start = 3, end = 5)

            # [NEXT STEP _ 4] 데이터 추출
            self.data_extraction(key)


    def data_extraction(self, keyword):  
        '''
        data_extraction() : keyword 관련 instagram data crawling
                            첫번째 게시글 클릭 후 다음 버튼 누르면 됨
            input parameter : (int)keyword - 가게id
            output : (csv)keyword_instagram_data
        '''

        '''
        [data column 정보]
            post url : 게시글 url
            writer_id : 작성자 id
            main_text : 게시물 본문(text)
            tag : 본문 속 tag 및 comment tag -> 둘 다 OK
        '''

        try:
            # 첫번째 게시물 클릭
            first_img_css = '#react-root > section > main > article > div.EZdmt > div > div > div:nth-child(1) > div:nth-child(1) > a > div.eLAPa'
            self.driver.find_element_by_css_selector(first_img_css).click()

            self.delay_until_next_step(start=5,end=7)
        except:
            print("--------- 게시물이 없습니다! ---------")
            pass

        # data crawling
        ## crawling object css
        upload_id_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.UE9AK > div > header > div.o-MQd.z8cbW > div.PQo_0.RqtMr > div.e1e1d > div > span > a"
        main_text_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > div > li > div > div > div.C4VMK > div.MOdxS > span"
        tag_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > div > li > div > div"
        # comment_more_btn = "button.dCJp8.afkep"
        comment_more_btn = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > li > div > button > div"
        comment_ids_object_css = "ul.Mr508 > div.ZyFrc > li.gElp9.rUo9f > div.P9YgZ > div.C7I1f > div.C4VMK > h3"
        '''
        # [ comment_texts_object_css 패턴 ]
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(2) > div > li > div > div > div.C4VMK > div.MOdxS # 첫번째 댓글 text
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(3) > div > li > div > div > div.C4VMK > div.MOdxS
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(4) > div > li > div > div > div.C4VMK > div.MOdxS
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(112) > div > li > div > div > div.C4VMK > div.MOdxS # 마지막 댓글 text(총 111개)
        '''
        next_btn_css1 = 'body > div.RnEpo._Yhr4 > div.Z2Inc._7c9RR > div > div.l8mY4.feth3 > button'


        # data extraction
        while True:
            # if self.count_extract > self.wish_num:
            #     # self.save_data(keyword)
            #     print("\n최종 저장 게시물 개수 :", self.count_extract-1)
            #     break

            self.delay_until_next_step(start=4, end=7)

            if self.check_next == False:
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                self.save_data(keyword)
                break

            # 게시글 url extraction
            try:
                post_url = self.driver.current_url
            except:
                post_url = None

            # 작성자ID extraction
            try:
                upload_id_object = self.driver.find_element_by_css_selector(upload_id_object_css)
                upload_id = upload_id_object.text
            except:
                upload_id = None
            self.delay_until_next_step(start=2,end=4)

            # 본론 text extraction
            try:
                main_text_object = self.driver.find_element_by_css_selector(main_text_object_css)
                main_text = main_text_object.text
            except:
                main_text = None

            # 본문 속 태그 extraction
            tag_list = []
            try:
                tag_object = self.driver.find_element_by_css_selector(tag_css)
                tag_raw = tag_object.text
                tags = re.findall('#[A-Za-z0-9가-힣]+', tag_raw)
                tag = ''.join(tags).replace("#", " ")
                tag_data = tag.split()
                for tag_one in tag_data:
                    tag_list.append(tag_one)
            except:
                pass

            # 댓글 extraction
            ## 더보기 버튼
            try:
                while True:
                    try:
                        more_btn = self.driver.find_element_by_css_selector(comment_more_btn)
                        more_btn.click()
                    except:
                        break
            except:
                print("\n------------ fail to click more btn ------------\n")
                pass
            self.delay_until_next_step(start=3,end=5)
            ## 댓글 데이터
            try:
                comment_data = {}
                comment_ids_objects = self.driver.find_elements_by_css_selector(comment_ids_object_css)
                self.delay_until_next_step(start=2,end=5)
                try:
                    for idx in range(len(comment_ids_objects)):
                        # 댓글
                        comment_text_cnt = idx + 2
                        comment_texts_object_css =  "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child({}) > div > li > div > div > div.C4VMK > div.MOdxS".format(comment_text_cnt)
                        comment_texts_object = self.driver.find_element_by_css_selector(comment_texts_object_css)
                        # 대댓글 - 작성자 댓글일 때만
                        comment_text2 = None # 초기화
                        comment_id = comment_ids_objects[idx].text
                        if comment_id == upload_id:
                            try:
                                comment_more_btn2 = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child({}) > li > ul > li".format(comment_text_cnt)
                                more_btn2 = self.driver.find_element_by_css_selector(comment_more_btn2)
                                more_btn2.click()
                                self.delay_until_next_step(start=2,end=3)
                                comment_tag_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child({}) > li > ul > div > li > div > div > div.C4VMK > div.MOdxS".format(comment_text_cnt)
                                comment_tag_object = self.driver.find_element_by_css_selector(comment_tag_css)
                                comment_text2 = comment_tag_object.text
                                print("\n대댓글 :", comment_text2)
                            except:
                                comment_text2 = None
                                print("\n대댓글 없음\n")

                        comment_data[str((idx+1))] = {'comment_id':comment_id, 
                                                    'comment_text':comment_texts_object.text,
                                                    'comment_text2':comment_text2}
                except:
                    print("\nXXXXXXX\n")
            except:
                comment_id = None
                comment_text = None
                comment_text2 = None
                comment_data = {}
            
            try:
                if comment_data != {}:
                    keys = list(comment_data.keys())

                    for key in keys:
                        if comment_data[key]['comment_id'] == upload_id:
                            # 댓글의 tag data 저장
                            tags = re.findall('#[A-Za-z0-9가-힣]+', comment_data[key]['comment_text'])
                            tag = ''.join(tags).replace("#", " ")
                            tag_data = tag.split()
                            for tag_one in tag_data:
                                tag_list.append(tag_one)
                            
                            # 대댓글의 tag data 저장
                            tags = re.findall('#[A-Za-z0-9가-힣]+', comment_data[key]['comment_text2'])
                            tag = ''.join(tags).replace("#", " ")
                            tag_data = tag.split()
                            for tag_one in tag_data:
                                tag_list.append(tag_one)
                else:
                    print("\n댓글 없음\n")
            except:
                print("\nfail\n")
                pass


            # 추출한 데이터를 dataframe에 추가
            self.post_urls.append(post_url)
            self.upload_ids.append(upload_id)
            self.main_texts.append(main_text)
            self.instagram_tags.append(tag_list)

            # 추출한 데이터 출력
            if self.print_flag:
                print("\n---------- INFO ----------")
                print("post_url :", post_url)
                print("upload_id :", upload_id)
                print("main :", main_text)
                print("insta tags :", tag_list)
                print("--------------------------\n")

            # 지정된 개수씩 csv로 저장
            self.count_extract += 1
            if self.wish_num == self.count_extract:
                # self.update_num += self.update_fix_num
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                self.save_data(keyword)
                break

            
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
            input parameter : (int)keyword - 가게 아이디

        '''

        # self.save_cnt += 1
        # save_file_name = str(keyword)+ "_instagram_data_"+str(self.save_cnt)
        save_file_name = str(keyword)+ "_instagram_data"
        
        try:
            # data list를 dataframe으로 변환 후 csv로 저장
            instagram_data_df = pd.DataFrame({"post_url":self.post_urls, "writer_id":self.upload_ids, 
                                            "main_text":self.main_texts, "tag":self.instagram_tags})
            instagram_data_df.to_csv("{}.csv".format(save_file_name), index=False)

            # data list 초기화 및 변수 초기화
            self.post_urls = []
            self.upload_ids = []
            self.main_texts = []
            self.instagram_tags = []
            self.count_extract = 0
            self.check_next = True

            
        except:
            print("\nfail total save data\n")

        

if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    insta_data = Crawl_Insta()