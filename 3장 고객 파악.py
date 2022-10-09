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


# 최신 고객 데이터 
customer_newer = customer_join[customer_join['end_date'].isna() | (pd.to_datetime(customer_join['end_date']) >= pd.to_datetime('20190331'))]
new_gender = customer_newer.groupby('gender').count()['customer_id']
new_class_name = customer_newer.groupby('class_name').count()['customer_id']
new_campaign = customer_newer.groupby('campaign_name').count()['customer_id']
new_delete = customer_newer.groupby('is_deleted').count()['customer_id']


# 이용 이력 데이터 조회 
use_log['usedate'] = pd.to_datetime(use_log['usedate'])
use_log['연월'] = use_log['usedate'].dt.strftime("%Y-%m")
use_log_months = use_log.groupby(["연월","customer_id"] ,as_index = False).count()
use_log_months.rename(columns={"log_id":"count"}, inplace=True)
del use_log_months['usedate']
uselog_customer = use_log_months.groupby('customer_id').agg(['mean' , 'median' , 'max' , 'min'])['count']
uselog_customer = uselog_customer.reset_index(drop = False)
uselog_customer


# 정기 이용 고객 
use_log['weekday'] = use_log['usedate'].dt.weekday
uselog_weekday = use_log.groupby(['customer_id' , '연월' , 'weekday'], as_index = False).count()[['customer_id' , '연월' , 'weekday' , 'log_id']]
uselog_weekday.rename(columns= {"log_id" : "count"},inplace= True) # inplace = True 로 바뀐 값을 저장 
uselog_weekday = uselog_weekday.groupby('customer_id',as_index= False).max()[['customer_id','count']]
uselog_weekday['routine_flg'] = 0 
uselog_weekday['routine_flg'] = uselog_weekday['routine_flg'].where(uselog_weekday['count']<4, 1 ) # count가 4보다 작으면 0 크면 1 
uselog_weekday[uselog_weekday['routine_flg'] == 1].iloc[:,0]

#데이터 결합
customer_join= pd.merge(customer_join,uselog_customer , on ='customer_id' , how='left')
customer_join = pd.merge(customer_join , uselog_weekday[['customer_id','routine_flg']], on='customer_id' ,how='left')
customer_join['end_date'] = pd.to_datetime(customer_join['end_date'])


# 활동 기간 (월별)
from dateutil.relativedelta import relativedelta # 두 날짜의 년, 월, 일 차이가 나온다 

customer_join['calc_date'] = customer_join['end_date']
customer_join['calc_date'] = customer_join['calc_date'].fillna(pd.to_datetime("20190430"))
customer_join['membership_period'] = 0 
for i in range(len(customer_join)) : 
  delta = relativedelta(customer_join['calc_date'].iloc[i] , customer_join['start_date'].iloc[i])
  customer_join['membership_period'].iloc[i] = delta.years*12 + delta.months
customer_join.head()

# 활동 기간 시각화
import matplotlib.pyplot as plt
%matplotlib inline
plt.hist(customer_join['membership_period'])

# 기존 , 이탈 고객 
customer_end = customer_join.loc[customer_join['is_deleted']==1]
customer_end.describe()
customer_stay = customer_join.loc[customer_join['is_deleted']==0]
customer_stay.describe()

# 
customer_join.to_csv("customer_join.csv" , index=False)
