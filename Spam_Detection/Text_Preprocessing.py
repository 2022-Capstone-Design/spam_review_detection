'''
    [file]
    Text_Preprocessing.py :: text preprocessing -> embedding -> text similarity
        1) text preprocessing : 한글 제외 문자 제거 -> 토큰화 -> 불용어 제거
        2) embedding : TFIDF , FastText, pre-trained FastText
        3) cosine similarity
'''

'''
    [전체 spam detection 과정] text preprocessing -> embedding -> text similarity -> sorting
        data :: len 긴 것(정성 review data)
        그 중 1으로 이미 labeling된 것도 아닌 것끼리 비교
        (하나의 텍스트 데이터에 대한 최종 유사도는 비교한 것의 평균)
'''

import re
import pandas as pd
import numpy as np
from konlpy.tag import Okt, Mecab, Hannanum, Kkma, Komoran
from setuptools import sic           # tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer         # embedding
from sklearn.metrics.pairwise import euclidean_distances            # 유클리디언 거리
from sklearn.metrics.pairwise import cosine_similarity              # 코사인 유사도
from gensim.models import FastText                                  # FastText
from gensim.models import fasttext                                  # FastText pre-trained model
# from gensim.models import fasttext.util
# from gensim.models import Word2Vec
# from glove import Corpus, Glove
# import pickle


class Preprocessing:
    '''
    [class]
    Preprocessing :: Instagram 본문 데이터를 통한 
    '''
    def __init__(self):
        self.id_list = self.Load_ID()                                                                       # 가게 Id list
        self.name_list = self.Load_Name()                                                                   # 가게 이름 list
        self.one_stop_words = ['은','는','이','가','하','아','것','들','의','있','되','수', '고', '에서',
                            '보','주','등','한','과','랑', '을', '를', '와', '도', '어요', '다']                   # 지정 불용어
        self.candidate_stop_words = self.Candidate_Stopwords_list_Load()                                    # 한국어불용어100사전
        self.stop_words = self.name_list + list(set(self.one_stop_words + self.candidate_stop_words))       # 가게 이름까지 합친 불용어
        self.tag_flag = 1                                            # [option] tag tokenizer
        self.file_dir = 'Spam_Detection/Cleaned_Data/'               # cleaned data를 저장할 경로


        # self.text_preprocessing()
        self.Embedding_Process()
        # self.check_Similarity()


    def Load_ID(self):
        '''
        Load_ID() : 가게 ID를 list형태로 반환
            input parameter : None
            output : (list)ID
        '''
        file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
        csv_file = pd.read_csv(file_name)
        return csv_file['id'].tolist()


    def Load_Name(self):
        '''
        Load_Name() : 가게 이름을 중복 제거 하여 list형태로 반환
            input parameter : None
            output : (list)Name
        '''
        file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
        csv_file = pd.read_csv(file_name)
        name_list = list(csv_file['name'][idx].split() for idx in range(len(csv_file['name'])))
        return list(set(sum(name_list, [])))


    def Candidate_Stopwords_list_Load(self):
        '''
        Candidate_Stopwords_list_Load() : 한국어불용어100.text 파일을 열어서 불용어 단어 반환
            input parameter : None
            output : (list)불용어
        '''
        file_name = 'Spam_Detection/한국어불용어100.txt'
        korean_stopwords100 = pd.read_csv(file_name, sep = '\t', header = None, names=['word', 'morph', 'rate'])
        return korean_stopwords100['word'].tolist()


    def DataLoad(self):
        '''
        DataLoad() : Insta 게시글 데이터 불러오기(Len 100이상 정성 데이터)
            input parameter : None
            ouput : (df)total_data
        '''
    
        # csv_name = "Data_Collection/Crawling_Instagram/Data/instagram_data_AD_label.csv"
        csv_name = "Data_Collection/Crawling_Instagram/Data/removed_instagram_data_AD_label.csv"
        total_data = pd.read_csv(csv_name)
        total_data = total_data.drop(['idx'], axis = 1)     # 전체 데이터
        # text_data = total_data.loc[:, ['main_text']]
        
        return total_data
    

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
            # review_text = re.sub('[^A-Za-z가-힣]','',review)
            review_text = re.sub('[^가-힣]','',review)

            # 영어는 소문자로 convert
            # cleaned_lowercase = review_text.lower()
            
            # 형태소 토큰화
            # review_words = self.tag.morphs(cleaned_lowercase)
            review_words = self.tag.morphs(review_text)

            # 불용어 제거 - 추 후에 불용어 사전 다운 + 음식점 이름도 불용어로 추가
            cleaned_words = [token for token in review_words if not token in self.stop_words]
        else:
            cleaned_words = []
        return " ".join(cleaned_words)    # 하나의 문장으로
        # return cleaned_words                # list로


    def text_preprocessing(self):
        '''
        text_preprocessing() : file 전체 text 전처리
            input parameter : None
            output : (df)total_data with cleaned data
        '''
        # tag 선정
        if self.tag_flag == 0:
            self.tag = Okt()
        elif self.tag_flag == 1:
            self.tag = Mecab()
        elif self.tag_flag == 2:
            self.tag = Hannanum()
        elif self.tag_flag == 3:
            self.tag = Kkma()
        else:
            self.tag = Komoran()

        # post data 가져오기
        total_data = self.DataLoad()
            
        # cleaning
        total_data['cleaned_main_text'] = total_data['main_text'].apply(self.cleaning)
        print(total_data)
        print(total_data.info())
        # print(total_data['cleaned_main_text'][0])

        return total_data
    

    def Embedding_Process(self):
        '''
        Embedding_Process() : 전처리가 진행된 데이터를 벡터화 (embedding)
            input parameter : None
            output : (df)total_data with embedded data
        '''

        # cleaned main text가 포함된 total data load
        total_data = self.text_preprocessing()
        AD_data = total_data.loc[total_data['AD']==1, :]    # AD data - 협찬 문구 들어간 것
        target_data = total_data.loc[total_data['AD']==2, :]    # 유사도 비교 데이터

        print("\n---------- data info ----------")
        print("TOTAL DATA")
        print(total_data.info())
        print("AD DATA")
        print(AD_data.info())
        print("TARGET DATA")
        print(target_data.info())
        print("-----------------------------\n")
        cleaned_main_text = total_data.loc[:, ['cleaned_main_text']]
        # print(AD_data)
        # print(target_data)
        
        ### embedding & similarity
        #-- tfidf --#
        '''
        [ver 1]
        vec_1 = TfidfVectorizer()
        tfidf_metrics = vec_1.fit_transform(cleaned_main_text['cleaned_main_text'])

        print("\n---------- Tfid-f ----------")
        print('광고O, 광고X 사이의 유클리디언 거리 :', euclidean_distances(tfidf_metrics[1], tfidf_metrics[3207]))
        print('광고O, 광고O 사이의 유클리디언 거리 :',euclidean_distances(tfidf_metrics[1], tfidf_metrics[4]))
        print('광고O, 광고X 사이의 코사인유사도 :',cosine_similarity(tfidf_metrics[1], tfidf_metrics[3207]))
        print('광고O, 광고O 사이의 코사인유사도 :',cosine_similarity(tfidf_metrics[1], tfidf_metrics[4]))
        print("-----------------------------\n")
        '''

        '''
        [ver 2]
        vec_1 = TfidfVectorizer()
        AD_vec = vec_1.fit_transform(AD_data['cleaned_main_text'])
        target_vec = vec_1.transform(target_data['cleaned_main_text'])
        print(cosine_similarity(AD_vec[1], target_vec[0]))
        print(type(cosine_similarity(AD_vec[1], target_vec[0])))
        print(cosine_similarity(AD_vec[1], target_vec[0])[0,0])
        
        similar_tfidf = []
        for target in range(len(target_data)):
            similar_sum=0
            for ad in range(len(AD_data)):
                similar_sum += (cosine_similarity(AD_vec[ad], target_vec[target])[0,0])
            print("\n---------- %d ----------"%target)
            print(similar_sum)
            similar_avg = similar_sum / len(AD_data)
            print(similar_avg)
            similar_tfidf.append(similar_avg)
            print("-----------------------------\n")

        print("\n---------- Tfid-f ----------")
        print(similar_tfidf)
        print("-----------------------------\n")
        '''

        # [ver 3]
        vec_1 = TfidfVectorizer()
        tfidf_metrics = vec_1.fit_transform(cleaned_main_text['cleaned_main_text'])
        
        similar_tfidf = []
        for idx in range(len(cleaned_main_text)):
            similar_sum=0
            cnt = 0
            if total_data['AD'][idx] == 1:
                similar_tfidf.append('AD')
                continue
            for idxx in range(len(cleaned_main_text)):
                if total_data['AD'][idxx] == 1:
                    similar_sum += (cosine_similarity(tfidf_metrics[idx], tfidf_metrics[idxx])[0,0])
                    cnt += 1
                else:
                    continue
            # print("\n---------- %d ----------"%target)
            # print(similar_sum)
            similar_avg = similar_sum / cnt
            # print(similar_avg)
            similar_tfidf.append(similar_avg)
            # print("-----------------------------\n")

        print("\n---------- Tfid-f ----------")
        print(similar_tfidf)
        print("-----------------------------\n")


        #-- fasttext --#
        '''
        [ver 1]
        vec_2 = FastText(cleaned_main_text['cleaned_main_text'], vector_size=100, window=7,min_count=5, workers=4, sg=1)
    
        print("\n---------- FastText ----------")
        print('광고O, 광고X 사이의 유사도 :',vec_2.wv.similarity(cleaned_main_text['cleaned_main_text'][1], cleaned_main_text['cleaned_main_text'][3207]))
        # print('광고O, 광고X 사이의 코사인유사도 :',vec_2.wv.cosine_similarities(cleaned_main_text['cleaned_main_text'][6], cleaned_main_text['cleaned_main_text'][30]))
        print('광고O, 광고O 사이의 유사도 :',vec_2.wv.similarity(cleaned_main_text['cleaned_main_text'][1], cleaned_main_text['cleaned_main_text'][4]))
        # print('광고O, 광고O 사이의 코사인유사도 :',vec_2.wv.cosine_similarities(cleaned_main_text['cleaned_main_text'][6], cleaned_main_text['cleaned_main_text'][7]))
        print("-----------------------------\n")
        '''
        
        vec_2 = FastText(cleaned_main_text['cleaned_main_text'], vector_size=100, window=7,min_count=5, workers=4, sg=1)
        # print(vec_2.wv.similarity(cleaned_main_text['cleaned_main_text'][6], cleaned_main_text['cleaned_main_text'][30]))
        # print(vec_2.wv.similarity(AD_data.loc[:,['cleaned_main_text']][0], target_data.loc[:,['cleaned_main_text']][0]))

        similar_ft = []
        for idx in range(len(cleaned_main_text)):
            similar_sum=0
            cnt = 0
            if total_data['AD'][idx] == 1:
                similar_ft.append('AD')
                continue
            for idxx in range(len(cleaned_main_text)):
                if total_data['AD'][idxx] == 1:
                    similar_sum += vec_2.wv.similarity(cleaned_main_text['cleaned_main_text'][idxx], cleaned_main_text['cleaned_main_text'][idx])
                    cnt += 1
                else:
                    continue
            # print("\n---------- %d ----------"%idx)
            # print(similar_sum)
            similar_avg = similar_sum / cnt
            # print(similar_avg)
            similar_ft.append(similar_avg)
            # print("-----------------------------\n")     
        print("\n---------- FastText ----------")   
        print(similar_ft)
        print("-----------------------------\n")
       
        #-- fasttext pre-trained model --#
        pre_trained_model = fasttext.load_facebook_model('Spam_Detection/cc.ko.300.bin')
        # pre_trained_model.train(cleaned_main_text['cleaned_main_text'])

        # print(pre_trained_model.wv.similarity(cleaned_main_text['cleaned_main_text'][1], cleaned_main_text['cleaned_main_text'][5]))
        # print(pre_trained_model.wv.similarity(AD_data.loc[:,['cleaned_main_text']][1], target_data.loc[:,['cleaned_main_text']][4]))
        
        similar_ft_ft = []
        for idx in range(len(cleaned_main_text)):
            similar_sum=0
            cnt = 0
            if total_data['AD'][idx] == 1:
                similar_ft_ft.append('AD')
                continue
            for idxx in range(len(cleaned_main_text)):
                if total_data['AD'][idxx] == 1:
                    similar_sum += pre_trained_model.wv.similarity(cleaned_main_text['cleaned_main_text'][idxx], cleaned_main_text['cleaned_main_text'][idx])
                    cnt += 1
                else:
                    continue
            # print("\n---------- %d ----------"%idx)
            # print(similar_sum)
            similar_avg = similar_sum / cnt
            # print(similar_avg)
            similar_ft_ft.append(similar_avg)
            # print("-----------------------------\n")
        
        print("\n---------- pre-trained FastText ----------")
        print(similar_ft_ft)
        print("-----------------------------\n")

                
        total_data['tfidf_cos'] = similar_tfidf
        total_data['ft_sim'] = similar_ft
        total_data['ft-ft_sim'] = similar_ft_ft
        
        print(total_data)
        
        total_data.to_csv(self.file_dir+'Insta_with_similarity'+'.csv',  index=False)
        
    

if __name__ == "__main__":
    '''
    Preprocessing class 실행
    '''

    # text 전처리
    cleaned_text_data = Preprocessing()