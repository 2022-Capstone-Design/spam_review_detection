'''
    preprocessing_main_text.py :: main_text 데이터의 해시태그 & ? 제거
'''

import pandas as pd
import re
'''
# 가게 리스트
file_name = 'Data_Collection/Crawling_Instagram/Data/가게조사.csv'
csv_file = pd.read_csv(file_name)
id_list = csv_file['id'].tolist()

# 해시태그 불러오기
csv_name = "Spam_Detection/Cleaned_Data/Insta_with_similarity.csv"
data = pd.read_csv(csv_name)
data1 = data.loc[data['store_id']==101,['tag']]
print(data1.iloc[0, :].to_list())
# for idx in id_list:    
#     data1 = data.loc[data['store_id']==idx,['tag']]
#     print(data1.loc[:, ['tag']])
    # tag_list = []
    # for idxx in range(len(data1)):
    #     tag_list.append(data1['tag'][idxx])
    # print(tag_list)
'''

path = 'Data_Collection/Crawling_Instagram/Data/removed_instagram_data_AD_label.csv'
data = pd.read_csv(path)
data = data.drop(['idx'], axis = 1)

def cleaning(text):
    text = re.sub('#[^\s]*','', text)
    text = re.sub('[?]','', text)
    # print(text)
    return text
data['main_text'] = data['main_text'].apply(cleaning)

data.to_csv('Spam_Detection/Cleaned_Data/cleaned_Insta.csv', index=False)
