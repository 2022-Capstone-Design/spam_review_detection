import pandas as pd

csv_name = "Data_Collection/Crawling_Instagram/Data/instagram_data_AD_label.csv"
total_data = pd.read_csv(csv_name)

train_data = total_data.loc[total_data['AD']!=2, :]
test_data = total_data.loc[total_data['AD'] == 2, :]

train_data.to_csv("Data_Collection/Crawling_Instagram/Data/train.csv",index=False, encoding='utf-8')
test_data.to_csv("Data_Collection/Crawling_Instagram/Data/test.csv",index=False, encoding='utf-8')

BERT_train_data = train_data.loc[:, ['main_text', 'AD']]
BERT_test_data = test_data.loc[:, ['main_text']]

BERT_train_data.to_csv("Data_Collection/Crawling_Instagram/Data/train_bert.csv",index=False, encoding='utf-8')
BERT_test_data.to_csv("Data_Collection/Crawling_Instagram/Data/test_bert.csv",index=False, encoding='utf-8')
