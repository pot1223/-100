customer_join = pd.read_csv('customer_join.csv')
customer_join
customer_clustering = customer_join[['mean','median' ,'max','min','membership_period']]
customer_clustering.head()


# K-means clustering
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
sc = StandardScaler()
customer_clustering_sc = sc.fit_transform(customer_clustering) # 표준화 (membership_period 때문에 시행) 
kmeans = KMeans(n_clusters=4 , random_state=0) 
clusters = kmeans.fit(customer_clustering_sc)
customer_clustering['cluster'] = clusters.labels_
print(customer_clustering['cluster'].unique())
customer_clustering.head()


customer_clustering.columns=['월평균값','월중앙값','월최댓값','월최솟값','회원기간','cluster']
customer_clustering.groupby('cluster').count()
customer_clustering.groupby('cluster').mean()


# 주성분 분석 (변수 5개를 2차원으로 축소)
from sklearn.decomposition import PCA
X = customer_clustering_sc
pca = PCA(n_components=2)
pca.fit(X)
x_pca = pca.transform(X)
pca_df = pd.DataFrame(x_pca)
pca_df['cluster'] = customer_clustering['cluster']
pca_df


# 시각화 
import matplotlib.pyplot as plt
%matplotlib inline
for i in customer_clustering['cluster'].unique():
  tmp = pca_df.loc[pca_df['cluster']==i]
  plt.scatter(tmp[0],tmp[1])
  
  
customer_clustering = pd.concat([customer_clustering , customer_join], axis =1)
customer_clustering['is_deleted'] =customer_clustering['is_deleted'].astype('object')


# 클러스터링으로 고객 집단 특징 파악 
customer_clustering.groupby(['cluster','is_deleted'],as_index = False).count()[['cluster','is_deleted','customer_id']]

# 클러스터링으로 고객 집단 특징 파악 
customer_clustering.groupby(['cluster','routine_flg'],as_index=False).count()[['cluster','routine_flg','customer_id']]


use_log['usedate'] = pd.to_datetime(use_log['usedate'])
use_log['연월'] = use_log['usedate'].dt.strftime('%Y-%m')
use_log_months = use_log.groupby(['연월','customer_id'],as_index= False).count()
use_log_months.rename(columns={'log_id' : 'count'},inplace = True)
del use_log_months['usedate']
use_log_months.head()
  
  
# 5개월 전 고객 이용 데이터 
year_months = list(use_log_months['연월'].unique())
predict_data = pd.DataFrame()
for i in range(6, len(year_months)):
  tmp = use_log_months.loc[use_log_months['연월'] == year_months[i]]
  tmp.rename(columns={'count' : 'count_pred'}, inplace= True)
  for j in range(1,7) : 
    tmp_before = use_log_months.loc[use_log_months['연월'] == year_months[i-j]]
    del tmp_before['연월']
    tmp_before.rename(columns={'count':'count_{}'.format(j-1)},inplace= True)
    tmp = pd.merge(tmp, tmp_before, on = 'customer_id',how = 'left')
  predict_data = pd.concat([predict_data, tmp], ignore_index = True)
predict_data = predict_data.dropna()
predict_data = predict_data.reset_index(drop = True)
predict_data


predict_data = pd.merge(predict_data , customer_join[['customer_id','start_date']], on = 'customer_id' , how = 'left')


predict_data['now_date']= pd.to_datetime(predict_data['연월'],format="%Y-%m")
predict_data['start_date'] = pd.to_datetime(predict_data['start_date'])
from dateutil.relativedelta import relativedelta
predict_data['period'] = None
for i in range(len(predict_data)) :
  delta = relativedelta(predict_data['now_date'][i] , predict_data['start_date'][i])
  predict_data['period'][i] = delta.years*12 + delta.months
predict_data.head()


# 선형회귀모델  
predict_data = predict_data.loc[predict_data['start_date'] >= pd.to_datetime("20180401")]
from sklearn import linear_model 
import sklearn.model_selection
model = linear_model.LinearRegression()
X = predict_data[['count_0','count_1','count_2','count_3','count_4','count_5','period']]
y= predict_data['count_pred']
X_train , X_test , y_train, y_test = sklearn.model_selection.train_test_split(X,y) # train data 75% , test data 25% (학습에 이용된 데이터를 완벽히 학습하는 과적합 방지)
model.fit(X_train, y_train)


# 정확도 검증 
print(model.score(X_train, y_train))
print(model.score(X_test,y_test))


# feature별 기여도 파악 
coef = pd.DataFrame({"feature_names" : X.columns , "coefficient" : model.coef_})
coef


# 다음달 이용 횟수 예측 
x1 = [3, 4, 4, 6, 8, 7, 8]
x2 = [2, 2, 3, 3, 4, 6, 8]
x_pred=[x1,x2]
model.predict(x_pred)

# 덤핑
use_log_months.to_csv("uselog_months.csv", index = False)
