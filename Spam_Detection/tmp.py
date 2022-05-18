from os import name
from turtle import pd
import pandas as pd
from konlpy.tag import Mecab


def Candidate_Stopwords_list_Load():

    korean_stopwords100 = pd.read_csv('Data_Preprocessing/한국어불용어100.txt', 
                                            sep = '\t', header = None, names=['word', 'morph', 'rate'])
    return korean_stopwords100['word'].tolist()



# one_stop_words = ['은','는','이','가','하','아','것','들','의','있','되','수', '감성',
#                             '보','주','등','한','과','랑','건대','강남','성수', '서울'
#                             '강남역', '성수역', '건대입구역','건대입구', '입구', '맛집']                       # 조사 불용어

one_stop_words = ['은','는','이','가','하','아','것','들','의','있','되','수', '감성',
                            '보','주','등','한','과','랑']   
candidate_stop_words = Candidate_Stopwords_list_Load() 

file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
csv_file = pd.read_csv(file_name)
name_list = list(csv_file['name'][idx].split() for idx in range(len(csv_file['name'])))
name_list = list(set(sum(name_list, [])))
print(name_list)


stop_words = list(set(one_stop_words + candidate_stop_words)) + name_list

print(stop_words)