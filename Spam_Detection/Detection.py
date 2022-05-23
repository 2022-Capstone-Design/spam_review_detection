'''
    Detection.py :: cleaned text data 및 similarity를 이용하여 spam detection
        [spam detection]
            1. similarity 기준으로 sorting
            2. clustering
'''

import pandas as pd
import numpy as np
from tqdm import tqdm


class Detection:
    '''
    [class]
    Detection :: Instagram 본문 데이터를 통한 
    '''
    def __init__(self):
        self.id_list = self.Load_ID()                               # 가게 Id list
        self.file_dir = 'Spam_Detection/Cleaned_Data/'               # data를 저장할 경로

        self.sorting()

    def DataLoad(self):
        '''
        DataLoad() : Insta 게시글 데이터 불러오기
            input parameter : None
            ouput : (df)total_data
        '''
        csv_name = "Spam_Detection/Cleaned_Data/Insta_with_similarity.csv"
        data = pd.read_csv(csv_name)
        
        return data

    def Load_ID(self):
        '''
        Load_ID() : 가게 ID를 list형태로 반환
            input parameter : None
            output : (list)ID
        '''
        file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
        csv_file = pd.read_csv(file_name)
        return csv_file['id'].tolist()

    def sorting(self):
        '''
        sorting() : 유사도 기반 sorting
        '''
        data = self.DataLoad()

        # 3개의 similarity 지표의 평균 계산
        similarity=[]
        for idx in range(len(data)):
            similarity.append(float(data['tfidf_cos'].iloc[idx])+float(data['ft_sim'].iloc[idx])+float(data['ft-ft_sim'].iloc[idx]))
        data['similarity'] = similarity

        # tfidf로 sorting
        sorted_data= data.sort_values(by = ['store_id', 'tfidf_cos'], ascending = True)
        sorted_data.to_csv(self.file_dir+'sorting_tfidf.csv', index = False)
        # fasttext로 sorting
        sorted_data= data.sort_values(by = ['store_id', 'ft_sim'], ascending = True)
        sorted_data.to_csv(self.file_dir+'sorting_ft.csv', index = False)
        # pre-trained fasttext로 sorting
        sorted_data= data.sort_values(by = ['store_id', 'ft-ft_sim'], ascending = True)
        sorted_data.to_csv(self.file_dir+'sorting_ptft.csv', index = False)

        
        
        


if __name__ == "__main__":
    '''
    Detection class 실행
    '''

    # text 전처리
    detect = Detection()