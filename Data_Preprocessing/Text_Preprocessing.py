'''
    [file]
    Text_Preprocessing.py :: text similarity를 위한 text preprocessing 과정
'''

import re
import pandas as pd
# import numpy as np
from konlpy.tag import Okt, Mecab


class Preprocessing:
    '''
    [class]
    Preprocessing :: Instagram 본문 데이터를 통한 
    '''
    def __init__(self):
        self.id_list = self.Load_ID()                         # 가게 Id list
        self.stop_words = ['은','는','이','가','하','아',
                            '것','들','의','있','되','수',
                            '보','주','등','한']                # 불용어 - 한국어 100 사전 찾아보기
        self.tag_flag = False                                 # [option] tag tokenizer - True면 Okt, False면 Mecab
        self.file_dir = 'Data_Preprocessing/Cleaned_Data'     # cleaned data를 저장할 경로

        self.text_preprocessing()


    def DataLoad(self, id_info):
        '''
        DataLoad() : Insta 게시글 데이터 불러오기
            input parameter : (int)id_info
            ouput : (df)total_data, (list)text_data
        '''
    
        csv_name = "Data_Collection/Crawling_Instagram/Insta Post Data/{}_instagram_data.csv".format(id_info)
        total_data = pd.read_csv(csv_name)
        text_data = total_data.loc[:, ['main_text']]
        

        return total_data, text_data
    
    def Load_ID(self):
        file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
        csv_file = pd.read_csv(file_name)
        return csv_file['id'].tolist()

    def cleaning(self, review):
        '''
        cleaning() : 데이터 정제
                    토큰화(Tokenization)
                    불용어(Stopword)
                    정규 표현식 (Regular Expression)
                    정수 인코딩(Integer Encoding)
            input parameter : (str)review
            output : (str)정제된 정보
        '''
        
        if type(review) == str:                 # main_text가 빈 리스트가 아닌 경우
            # 영어 및 한글을 제외한 문자 모두 제거
            review_text = re.sub('[^A-Za-z가-힣]',' ',review)
            # 영어는 소문자로 convert
            cleaned_lowercase = review_text.lower()
            # 형태소 토큰화
            review_words = self.tag.morphs(cleaned_lowercase)
            # 불용어 제거 - 추 후에 불용어 사전 다운 + 음식점 이름도 불용어로 추가
            cleaned_words = [token for token in review_words if not token in self.stop_words]
        else:
            cleaned_words = 'None'
        return " ".join(cleaned_words)

    def text_preprocessing(self):
        '''
        text_preprocessing() : file 전체 text 전처리
            input parameter
            output
        '''
        # tag 선정
        if self.tag_flag:
            self.tag = Okt()
        else:
            self.tag = Mecab()

        test_list = [101]           # test로 id 101 Post data에 대해 수행
        # for id in self.id_list:
        for id in test_list:
            # id에 해당하는 post data 가져오기
            total_data, text_data = self.DataLoad(id)
            # cleaning
            total_data['cleaned_main_text'] = text_data['main_text'].apply(self.cleaning)
        print(total_data)
            


if __name__ == "__main__":
    '''
    Preprocessing class 실행
    '''

    # text 전처리
    cleaned_text_data = Preprocessing()