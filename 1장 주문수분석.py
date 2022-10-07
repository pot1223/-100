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

join_data = pd.merge(transaction_detail, transaction[["transaction_id" , "payment_date" , "customer_id"]] , on = "transaction_id" , how = "left")
join_data = pd.merge(join_data , customer_master , on = "customer_id" , how = "left")
join_data = pd.merge(join_data , item_master, on = "item_id" , how = "left")
join_data["price"] = join_data["quantity"] * join_data["item_price"]
customer_purchase_price_ranking = pd.DataFrame(join_data.groupby("customer_name")["price"].sum()).sort_values("price" , ascending = False).reset_index()
# 가장 많이 매출을 발생한 고객 상위 5명은 김재이, 김로이, 김원영, 김이헌, 김시환 고객님이다  
# 큰 손 5명의 정보를 분석하여 고객을 잡아두는 방안을 세워야 한다  
