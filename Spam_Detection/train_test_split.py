import pandas as pd
from sklearn.model_selection import train_test_split

csv_name = "Data_Collection/Crawling_Instagram/Data/instagram_data_AD_label.csv"
total_data = pd.read_csv(csv_name)
# label : 0(empty list, No AD), 1(AD contain '협찬'), 2(No label)
train_data = total_data.loc[total_data['AD']!=2, :]
# test_data = total_data.loc[total_data['AD'] == 2, :]

# train_data.to_csv("Data_Collection/Crawling_Instagram/Data/train.csv",index=False, encoding='utf-8')
# test_data.to_csv("Data_Collection/Crawling_Instagram/Data/test.csv",index=False, encoding='utf-8')

BERT_train_data = train_data.loc[:, ['main_text', 'AD']]
# print(BERT_train_data.head())

x_train, x_val, y_train, y_val = train_test_split(BERT_train_data['main_text'], BERT_train_data['AD'], test_size=0.2, random_state=42)

train = pd.DataFrame((zip(x_train, y_train)), columns = ['main_text', 'AD'])
val = pd.DataFrame((zip(x_val, y_val)), columns = ['main_text', 'AD'])

BERT_test_data = total_data.loc[:, ['main_text']]

train.to_csv("Data_Collection/Crawling_Instagram/Data/train.csv",index=False, header = False, encoding='utf-8')
val.to_csv("Data_Collection/Crawling_Instagram/Data/val.csv",index=False, header = False, encoding='utf-8')

# BERT_train_data.to_csv("Data_Collection/Crawling_Instagram/Data/train_bert.csv",index=False, header = False, encoding='utf-8')
BERT_test_data.to_csv("Data_Collection/Crawling_Instagram/Data/test_bert.csv",index=False, header = False, encoding='utf-8')
