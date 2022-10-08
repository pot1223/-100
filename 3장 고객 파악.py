import pandas as pd 
campaign_masater = pd.read_csv('campaign_master.csv')
class_master = pd.read_csv('class_master.csv')
customer_master = pd.read_csv('customer_master.csv')
use_log = pd.read_csv('use_log.csv')
print(customer_master.head())
print(class_master.head())


print(len(campaign_masater))
print(len(class_master))
print(len(customer_master))
print(len(use_log))


# 고객 데이터 집계 
gender = customer_join.groupby('gender').count()['customer_id']
class_name = customer_join.groupby('class_name').count()['customer_id']
campaign = customer_join.groupby('campaign_name').count()['customer_id']
delete = customer_join.groupby('is_deleted').count()['customer_id']


# 특정 기간 동안의 가입 인원 
customer_join['start_date'] = pd.to_datetime(customer_join['start_date'])  
customer_start = customer_join.loc[customer_join['start_date'] > pd.to_datetime('20180401')]
print(len(customer_start))
