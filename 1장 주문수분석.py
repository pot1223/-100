import pandas as pd 
customer_master = pd.read_csv("customer_master.csv")
customer_master.head()

item_master = pd.read_csv("item_master.csv")
item_master.head()

transaction_1 = pd.read_csv("transaction_1.csv")
transaction_2 = pd.read_csv("transaction_2.csv")
transaction = pd.concat([transaction_1 , transaction_2], ignore_index = True)
transaction

transaction_detail_1 = pd.read_csv("transaction_detail_1.csv")
transaction_detail_2 = pd.read_csv("transaction_detail_2.csv")
transaction_detail = pd.concat([transaction_detail_1, transaction_detail_2] , ignore_index = True)
transaction_detail.head()


# 가장 많이 매출을 발생한 고객 상위 5명은 김재이, 김로이, 김원영, 김이헌, 김시환 고객님이다  
# 큰 손 5명의 정보를 분석하여 고객을 잡아두는 방안을 세워야 한다  
join_data = pd.merge(transaction_detail, transaction[["transaction_id" , "payment_date" , "customer_id"]] , on = "transaction_id" , how = "left")
join_data = pd.merge(join_data , customer_master , on = "customer_id" , how = "left")
join_data = pd.merge(join_data , item_master, on = "item_id" , how = "left")
join_data["price"] = join_data["quantity"] * join_data["item_price"]
customer_purchase_price_ranking = pd.DataFrame(join_data.groupby("customer_name")["price"].sum()).sort_values("price" , ascending = False).reset_index()


# 데이터 검증 
print(customer_purchase_price_ranking.iloc[:,1].sum())
print(transaction.iloc[:,1].sum())


# 데이터 파악 
print(join_data.describe())
print(join_data["payment_date"].min())
print(join_data["payment_date"].max())


# 시계열 파악 
join_data.dtypes
join_data["payment_date"] = pd.to_datetime(join_data["payment_date"])
join_data["payment_month"] = join_data["payment_date"].dt.strftime("%Y-%m")
join_data[["payment_date","payment_month"]].head()
join_data.groupby("payment_month").sum()["price"] # price 칼럼만 추출 


#피벗 테이블 생성 
join_data.groupby(['payment_month','item_name']).sum()[['price','quantity']]
pd.pivot_table(join_data, index = 'item_name' , columns='payment_month', values =['price','quantity'], aggfunc='sum')


# 월별 매출 추이 시각화
graph_data = pd.pivot_table(join_data, index = 'payment_month' , columns='item_name', values ='price', aggfunc='sum')
import matplotlib.pyplot as plt
%matplotlib inline
plt.plot(list(graph_data.index) , graph_data["PC-A"], label='PC-A')
plt.plot(list(graph_data.index) , graph_data["PC-B"], label='PC-B')
plt.plot(list(graph_data.index) , graph_data["PC-C"], label='PC-C')
plt.plot(list(graph_data.index) , graph_data["PC-D"], label='PC-D')
plt.plot(list(graph_data.index) , graph_data["PC-E"], label='PC-E')
plt.legend()


# 월별 주문량 추이 시각화
graph_data2 = pd.pivot_table(join_data, index = 'payment_month' , columns='item_name', values ='quantity', aggfunc='sum')
plt.plot(list(graph_data2.index) , graph_data2["PC-A"], label='PC-A')
plt.plot(list(graph_data2.index) , graph_data2["PC-B"], label='PC-B')
plt.plot(list(graph_data2.index) , graph_data2["PC-C"], label='PC-C')
plt.plot(list(graph_data2.index) , graph_data2["PC-D"], label='PC-D')
plt.plot(list(graph_data2.index) , graph_data2["PC-E"], label='PC-E')
plt.legend()


