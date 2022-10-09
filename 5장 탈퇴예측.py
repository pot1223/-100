customer = pd.read_csv('customer_join.csv')
uselog_months = pd.read_csv('uselog_months.csv')
uselog_months


# 1달 전 이용횟수 
year_months = list(uselog_months['연월'].unique())
year_months 
uselog = pd.DataFrame()
for i in range(1, len(year_months)) :
  tmp = uselog_months.loc[uselog_months['연월'] == year_months[i]]
  tmp.rename(columns={'count' : 'count_0'}, inplace = True)
  tmp_before = uselog_months.loc[uselog_months['연월'] == year_months[i-1]] # 한달 전 
  del tmp_before['연월']
  tmp_before.rename(columns={"count" :"count_1"},inplace = True)
  tmp = pd.merge(tmp, tmp_before , on = 'customer_id' ,how ='left')
  uselog = pd.concat([uselog, tmp], ignore_index = True)
uselog.head()


from dateutil.relativedelta import relativedelta
exit_customer = customer.loc[customer['is_deleted'] == 1]
exit_customer['exit_date'] = None
exit_customer['end_date'] = pd.to_datetime(exit_customer['end_date'])
for i in range(len(exit_customer)) : 
  exit_customer['exit_date'].iloc[i] = exit_customer['end_date'].iloc[i] - relativedelta(months = 1) # 탈퇴 전월
exit_customer['연월'] = pd.to_datetime(exit_customer['exit_date']).dt.strftime("%Y-%m")
uselog['연월'] = uselog['연월'].astype(str)
exit_uselog = pd.merge(uselog, exit_customer, on = ['customer_id','연월'], how = 'left')
exit_uselog = exit_uselog.dropna(subset=['name'])
exit_uselog


conti_customer = customer.loc[customer['is_deleted'] == 0]
conti_uselog = pd.merge(uselog , conti_customer , on=['customer_id'] , how = 'left')
conti_uselog = conti_uselog.dropna(subset=['name'])
conti_uselog = conti_uselog.sample(frac=1).reset_index(drop=True) # 불균형 데이터이므로 언더 샘플링한다 
conti_uselog = conti_uselog.drop_duplicates(subset='customer_id')
conti_uselog # 데이터 수가 2842개로 줄어들어 불균형 상태가 깨졌다 


predict_data = pd.concat([conti_uselog, exit_uselog], ignore_index = True)


predict_data['period'] = 0 
predict_data['now_date'] = pd.to_datetime(predict_data['연월'], format="%Y-%m")
predict_data['start_date'] = pd.to_datetime(predict_data['start_date'])
for i in range(len(predict_data)):
  delta = relativedelta(predict_data['now_date'][i],predict_data['start_date'][i])
  predict_data['period'][i] = int(delta.years*12+delta.months)
predict_data


predict_data.isna().sum()
predict_data = predict_data.dropna(subset=['count_1'])


target_col = ['campaign_name' , 'class_name', 'gender', 'count_1', 'routine_flg', 'period', 'is_deleted']
predict_data = predict_data[target_col]
predict_data


# 더미 변수 생성 
predict_data = pd.get_dummies(predict_data)
del predict_data['campaign_name_2_일반']
del predict_data['class_name_2_야간']
del predict_data['gender_M']
predict_data.dtypes


# 의사결정 트리
from sklearn.tree import DecisionTreeClassifier
import sklearn.model_selection
exit = predict_data.loc[predict_data['is_deleted'] == 1]
conti = predict_data.loc[predict_data['is_deleted']==0].sample(len(exit)) # exit데이터와 conti 데이터를 1:1 비율로 맞춘다 
X= pd.concat([exit,conti],ignore_index= True)
y = X['is_deleted']
del X['is_deleted']
X_train , X_test , y_train , y_test = sklearn.model_selection.train_test_split(X,y)
model = DecisionTreeClassifier(random_state = 0 )
model.fit(X_train, y_train)
y_test_pred = model.predict(X_test)
results_test = pd.DataFrame({"y_test" : y_test , "y_pred" : y_test_pred})
results_test.head()


# 모델 정답률 
correct = len(results_test.loc[results_test['y_test'] == results_test['y_pred']])
data_count = len(results_test)
score_test = correct / data_count 
score_test


# 트리 깊이를 얕게 해서 과적합을 방지함 
model = DecisionTreeClassifier(random_state = 0 , max_depth =5 ) 
model.fit(X_train , y_train)
print(model.score(X_test,y_test))
print(model.score(X_train, y_train)) 


# 모델 기여 변수 측정 
importance = pd.DataFrame({"feature_names" : X.columns , "coefficient" : model.feature_importances_}) # 회귀와는 달리 feature_importances_로 중요도를 얻는다 
importance


# 모델 예측 
count_1 = 3
routine_flg = 1
period = 10
campaign_name = '입회비무료'
class_name = '종일'
gender = 'M'
if campaign_name == '입회비반액할인' :
  campaign_name_list = [1,0]
elif campaign_name == '입회비무료':
  campaign_name_list = [0,1]
elif campaign_name == '일반' :
  campaign_name_list = [0,0]
if class_name == '종일' :
  class_name_list =[1,0]
elif class_name == '주간' :
  class_name_list = [0,1] 
elif class_name == '야간' :
  class_name_list = [0,0]
if gender == 'F' :
  gender_list =[1]
elif gender == 'M' :
  gender_list = [0]
input_data = [count_1, routine_flg , period]
input_data.extend(campaign_name_list)
input_data.extend(class_name_list)
input_data.extend(gender_list)
input_data
print(model.predict([input_data]))
print(model.predict_proba([input_data]))
