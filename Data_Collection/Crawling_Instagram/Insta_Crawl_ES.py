'''
    [file]
    Insta_Crawl_ES.py :: 가져올 수 있는 데이터 모두 추출한 crawler (초기 ver.)
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
    Crawl_Insta :: Instagram API를 활용해 해시태그 별 게시물 1000개씩 crawling
            crawling data  - 작성자, 위치, 게시글(사진, 텍스트), 작성 날짜, 댓글
'''


class Crawl_Insta:

    def __init__(self): 
        '''
        __init__() : 초기화 함수
                    chrome webdriver open 및 Instagram login url 열기
        
        [data column 정보]
            post_url : 게시글 url
            writer_id : 작성자 id
            location_info : 게시물 위치정보 이름
            location_href : 게시물 위치정보 url
            date_text : 게시물 게시 날짜 (월 일)
            date_time : 게시물 게시 날짜 (datetime 형식)
            date_title : 게시물 게시 날짜 (년 월 일)
            main_image_url : 게시물 본문(image)
            main_text : 게시물 본문(text)
            tag : 본문 속 tag
            comment : 게시물 댓글
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
        self.keyword = ''                                    # hashtag keyword
        self.count_extract = 0                               # 현재 crawlng한 게시물 개수 count
        self.update_num = 100                                # 중간 저장 게시글 개수
        self.update_fix_num = self.update_num                # 중간 저장 고정 게시물 개수 (몇 개씩 끊어서 저장할 것인지)
        self.wish_num = 300                                  # 최종적으로 crawling할 게시물 개수
        self.check_next = True                               # 다음 버튼이 있는지 확인
        self.save_cnt = 0                                    # 저장 version
        self.print_flag = False                              # True면 추출한 데이터 출력
        ## 저장할 데이터 list
        self.post_urls = []                                  # 게시글 url
        self.location_infos = []                             # 위치 정보
        self.location_hrefs = []                             # 위치 하이퍼링크(url)
        self.upload_ids = []                                 # 작성자 id
        self.date_texts = []                                 # 작성 날짜 (text)
        self.date_times = []                                 # 작성 날짜 (datetime)
        self.date_titles = []                                # 작성 날짜 (title)
        self.main_texts = []                                 # 게시글 텍스트
        self.main_images_url = []                            # 게시글 이미지 url
        self.instagram_tags = []                             # 게시글 tag
        self.comments = []                                   # 게시글 댓글


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
        
        # [NEXT STEP _2] hashtag keyword 입력 함수 호출
        if self.is_login_success:
            self.set_keyword()      # hashtag 입력
            self.driver.implicitly_wait(3)


    def set_keyword(self):
        '''
        set_keyword() : 크롤링 할 hashtag keyword 입력 및 Url 이동
            input parameter : None
            output : None
        '''

        # keyword 저장
        print("\n크롤링할 해시태그를 입력해주세요")
        print("ex) '#건대맛집' 해시태그를 검색하려면 '건대맛집'이라고 입력")
        self.keyword = input("Input HashTag : ")
        # self.keyword = '#' + self.keyword
        print()

        # 해당하는 hashtag url로 이동
        hash_tag_url = 'https://www.instagram.com/explore/tags/{}/'.format(self.keyword)
        self.driver.get(hash_tag_url)
        time.sleep(5)   

        # [NEXT STEP _3] data 추출 함수로 이동
        self.data_extraction() 
    

    def data_extraction(self):  
        '''
        data_extraction() : keyword 관련 instagram data crawling
                            첫번째 게시글 클릭 후 다음 버튼 누르면 됨
            input parameter : None
            output : (csv)[keyword]instagram_data
        '''

        '''
        [data column 정보]
            post url : 게시글 url
            writer_id : 작성자 id -> OK
            location_info : 게시물 위치정보 이름 -> OK
            location_href : 게시물 위치정보 url -> OK
            date_text : 게시물 게시 날짜 (월 일) 
            date_time : 게시물 게시 날짜 (datetime 형식)
            date_title : 게시물 게시 날짜 (년 월 일)
            main_image_url : 게시물 본문(image)
            main_text : 게시물 본문(text) -> OK
            tag : 본문 속 tag 및 comment tag -> 둘 다 OK
            comment : 게시물 댓글 -> OK
        '''

        try:
            # 첫번째 게시물 클릭 :: 최근게시물
            first_img_css = '#react-root > section > main > article > div:nth-child(4) > div > div:nth-child(1) > div:nth-child(1) > a > div.eLAPa'
            self.driver.find_element_by_css_selector(first_img_css).click()

            self.delay_until_next_step(start=5,end=7)
        except:
            print("--------- 게시물이 없습니다! ---------")
            pass

        # data crawling
        ## crawling object css
        post_url_object_css = ''
        location_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.UE9AK > div > header > div.o-MQd.z8cbW > div.M30cS > div > div.JF9hh > div > a"
        upload_id_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.UE9AK > div > header > div.o-MQd.z8cbW > div.PQo_0.RqtMr > div.e1e1d > div > span > a"
        date_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.qF0y9.Igw0E.IwRSH.eGOV_._4EzTm > div > div > div.NnvRN > div"
        main_text_object_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > div > li > div > div > div.C4VMK > div.MOdxS > span"
        main_image_object_css1 = 'body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div._97aPb.C2dOX.HCDIA > div > div'
        main_image_object_css2 = 'body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div._97aPb.C2dOX.HCDIA > div > div.pR7Pc > div.qF0y9.Igw0E.IwRSH.eGOV_._4EzTm.O1flK.D8xaz.fm1AK.TxciK.yiMZG > div > div > div > ul > li:nth-child(2) > div > div > div'
        tag_css = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > div > li > div > div"
        # comment_more_btn = "button.dCJp8.afkep"
        comment_more_btn = "body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > li > div > button > div"
        comment_ids_object_css = "ul.Mr508 > div.ZyFrc > li.gElp9.rUo9f > div.P9YgZ > div.C7I1f > div.C4VMK > h3"
        # comment_texts_object_css = "ul.Mr508 > div.ZyFrc > li.gElp9.rUo9f > div.P9YgZ > div.C7I1f > div.C4VMK > span"
        '''
        # [ comment_texts_object_css 패턴 ]
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(2) > div > li > div > div > div.C4VMK > div.MOdxS # 첫번째 댓글 text
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(3) > div > li > div > div > div.C4VMK > div.MOdxS
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(4) > div > li > div > div > div.C4VMK > div.MOdxS
        body > div.RnEpo._Yhr4 > div.pbNvD.QZZGH.bW6vo > div > article > div > div.HP0qD > div > div > div.eo2As > div.EtaWk > ul > ul:nth-child(112) > div > li > div > div > div.C4VMK > div.MOdxS # 마지막 댓글 text(총 111개)
        '''
        # next_btn_css1 = "div.l8mY4.feth3 > .wpO6b "
        # next_btn_css1 = "body > div.RnEpo._Yhr4 > div.Z2Inc._7c9RR > div > div > button"
        next_btn_css1 = 'body > div.RnEpo._Yhr4 > div.Z2Inc._7c9RR > div > div.l8mY4.feth3 > button'
        
        
        # data extraction
        while True:
            if self.count_extract > self.wish_num:
                self.save_data()
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                break

            self.delay_until_next_step(start=4, end=7)

            if self.check_next == False:
                self.save_data()
                print("\n최종 저장 게시물 개수 :", self.count_extract)
                break

            # 게시글 url extraction
            try:
                post_url = self.driver.current_url
            except:
                post_url = None

            # 위치 정보 extraction
            try:
                location_object = self.driver.find_element_by_css_selector(location_object_css)
                location_info = location_object.text
                location_href = location_object.get_attribute("href")
            except:
                location_info = None
                location_href = None
            self.delay_until_next_step(start=2,end=4)

            # 작성자ID extraction
            try:
                upload_id_object = self.driver.find_element_by_css_selector(upload_id_object_css)
                upload_id = upload_id_object.text
            except:
                upload_id = None
            self.delay_until_next_step(start=2,end=4)

            # 게시 날짜 extraction
            '''
                [comment] 아니 이거 왜 안받아와지지?!?!?!?! 왜?!?!?!?
            '''
            try:
                date_object = self.driver.find_element_by_css_selector(date_object_css)
                date_text = date_object.text
                date_time = date_object.get_attribute("datetime")
                date_title = date_object.get_attribute("title")
            except:
                date_text = None
                date_time = None
                date_title = None
            self.delay_until_next_step(start=2,end=4)

            # 본론 extraction
            # [수정] image url 저장하는 부분
            '''
                [comment] text 받아오는 것은 된다. 하지만 image url 받아오는 건 왜 안되는 거지?!
            '''
            try:
                # text
                main_text_object = self.driver.find_element_by_css_selector(main_text_object_css)
                main_text = main_text_object.text
                # img - [수정!!]
                # main_image_object = self.driver.find_element_by_css_selector(main_image_object_css)
                # main_image_url = main_image_object 
                main_image_url = "아직 해결 못했음"
            except:
                main_text = None
                main_image_url = None

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
                # comment_texts_objects = self.driver.find_elements_by_css_selector(comment_texts_object_css)
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
            self.location_infos.append(location_info)
            self.location_hrefs.append(location_href)
            self.upload_ids.append(upload_id)
            self.date_texts.append(date_text)
            self.date_times.append(date_time)
            self.date_titles.append(date_title)
            self.main_texts.append(main_text)
            self.main_images_url.append(main_image_url)
            self.instagram_tags.append(tag_list)
            comment_json = json.dumps(comment_data)
            self.comments.append(comment_json)

            # 추출한 데이터 출력
            if self.print_flag:
                print("\n---------- INFO ----------")
                print("post_url :", post_url)
                print("location_info :", location_info)
                print("location_href :", location_href)
                print("upload_id :", upload_id)
                print("date : {} {} {}".format(date_text, date_time, date_title))
                print("main :", main_text)
                print("comment :", comment_data)
                print("insta tags :", tag_list)
                print("--------------------------\n")

            # 지정된 개수씩 csv로 저장
            self.count_extract += 1
            if self.update_num == self.count_extract:
                self.update_num += self.update_fix_num
                self.save_data()
            
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


    def save_data(self):
        '''
        save_data() : 추출한 데이터 csv 파일로 저장
        '''
        self.save_cnt += 1
        save_file_name = '['+self.keyword+ "]instagram_data_"+str(self.save_cnt)
        
        try:
            # data list를 dataframe으로 변환 후 csv로 저장
            instagram_data_df = pd.DataFrame({"post_url":self.post_urls, "writer_id":self.upload_ids, 
                                            "location_info":self.location_infos, "location_href":self.location_hrefs, 
                                            "date_text":self.date_texts, "date_time":self.date_times, "date_title":self.date_titles,
                                            "main_image_url":self.main_images_url, "main_text":self.main_texts, 
                                            "tag":self.instagram_tags, "comment":self.comments})
            instagram_data_df.to_csv("{}.csv".format(save_file_name), index=False)

            # data list 초기화
            self.post_urls = []
            self.location_infos = []
            self.location_hrefs = []
            self.upload_ids = []
            self.date_texts = []
            self.date_times = []
            self.date_titles = []
            self.main_texts = []
            self.main_images_url = []
            self.instagram_tags = []
            self.comments = []
        except:
            print("\nfail total save data\n")

        

if __name__ == "__main__":
    '''
    Crawling class 실행
    '''

    # crawling class 선언
    insta_data = Crawl_Insta()