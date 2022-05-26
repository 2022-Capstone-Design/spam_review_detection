'''
    Detection.py :: cleaned text data 및 similarity를 이용하여 spam detection
        [spam detection]
            1. similarity 기준으로 sorting
            2. clustering
'''

from distutils.command.clean import clean
import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer         # embedding
from sklearn.metrics.pairwise import euclidean_distances            # 유클리디언 거리
from sklearn.metrics.pairwise import cosine_similarity              # 코사인 유사도
from gensim.models import FastText                                  # FastText
from gensim.models import fasttext                                  # FastText pre-trained model
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from collections import Counter


class Detection:
    '''
    [class]
    Detection :: Instagram 본문 데이터를 통한 
    '''
    def __init__(self):
        self.id_list = self.Load_ID()                               # 가게 Id list
        self.file_dir = 'Spam_Detection/Cleaned_Data/'               # data를 저장할 경로

        # self.sorting() 
        self.clustering()

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

    def plotting(self, df):

        # clustering 결과 시각화
        f, ax = plt.subplots(2, 2)
        f.set_size_inches((12, 12))

        for i in range(4):
            # epsilon을 증가시키면서 반복
            eps = 0.3 * (i + 1)
            min_samples = 5

            # 군집화 및 시각화 과정 자동화
            model = DBSCAN(eps=eps, min_samples=min_samples)
            model.fit(df)
            label = model.labels_.tolist()
            print("label describe:", Counter(label))
            pred = model.fit_predict(df)

            # 시각화를 위한 차원축소
            pca = PCA(n_components=2)
            pca_data = pca.fit_transform(df)
            p_df = pd.DataFrame(data=pca_data, columns=['main1', 'main2'])


            # eps 0.4씩 늘리며 군집화 시각화
            colors = ['red', 'blue',  'green', 'black', 'purple', 'yellow', 'pink', 'orange']
            idx = 0
            for val in np.unique(label):
                label_name = "clustering"+str(val)
                ax[i // 2, i % 2].scatter(p_df.iloc[model.labels_ == val,0],
                            p_df.iloc[model.labels_ == val, 1], s = 10, c = colors[idx], label = label_name)
                idx+=1
            ax[i // 2, i % 2].legend()
            ax[i // 2, i % 2].set_title('eps = %.1f, min_samples = %d'%(eps, min_samples), size = 15)
        plt.show()
    
    def clustering(self):
        data = self.DataLoad() # data load
        cleaned_main_text = data.loc[:, ['cleaned_main_text']]
        
        ##-- TFIDF :: embedding --##
        vec_1 = TfidfVectorizer()
        tfidf_metrics = vec_1.fit_transform(cleaned_main_text['cleaned_main_text'].values.astype('U'))
        # print(tfidf_metrics)
        tfidf_df = pd.DataFrame(tfidf_metrics.toarray(), columns=vec_1.get_feature_names_out())
        # print(tfidf_df)
        self.plotting(tfidf_df)
        
        '''
        eps = 0.4
        min_samples = 12
        model = DBSCAN(eps = eps, min_samples=min_samples)
        model.fit(tfidf_df)
        label = model.labels_.tolist()
        print(Counter(label))
        print(np.unique(label))
        pred = model.fit_predict(tfidf_df)
        print(pred)
        '''
        
        # vec_2 = FastText(cleaned_main_text['cleaned_main_text'].values.astype('U'), vector_size=100, window=7,min_count=5, workers=4, sg=1)
        # print(vec_2.wv(cleaned_main_text['cleaned_main_text'][0]))
        # pre_trained_model = fasttext.load_facebook_model('Spam_Detection/cc.ko.300.bin')
        # print(pre_trained_model(cleaned_main_text['cleaned_main_text'][1]))



        
        
    
if __name__ == "__main__":
    '''
    Detection class 실행
    '''

    # text 전처리
    detect = Detection()