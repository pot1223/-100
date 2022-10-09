import pandas as pd 
factories = pd.read_csv('tbl_factory.csv' , index_col=0)
warehouse = pd.read_csv('tbl_warehouse.csv' , index_col =0)
cost = pd.read_csv('rel_cost.csv' , index_col = 0)
trans = pd.read_csv('tbl_transaction.csv' , index_col = 0)


join_data = pd.merge(trans,cost , left_on = ['ToFC','FromWH'] , right_on = ['FCID','WHID'] , how = 'left')
join_data = pd.merge(join_data , factories , left_on='ToFC' , right_on="FCID" , how = 'left')
join_data = pd.merge(join_data , warehouse , left_on = 'FromWH' , right_on = 'WHID' , how ='left')
join_data = join_data[['TransactionDate','Quantity','Cost','ToFC','FCName','FCDemand','FromWH','WHName','WHSupply','WHRegion']]
join_data.head()


north = join_data[join_data['WHRegion'] == '북부']
south = join_data[join_data['WHRegion'] == '남부']


print(f"북부 지사 총비용 : {north['Cost'].sum()}만원 , 남부 지사 총비용 : {south['Cost'].sum()}만원")


print(f"북부 지사 총부품 운송개수 : {north['Quantity'].sum()} , 남부 지사 총부품 운송개수 : {south['Quantity'].sum()}")


print(f"북부 지사 부품 1회당 운송 비용 : {int((north['Cost'].sum() / north['Quantity'].sum()) *10000)}원 , 남부 지사 부품 1회당 운송 비용 : {int((south['Cost'].sum() / south['Quantity'].sum())*10000)}원")


cost_chk = pd.merge(cost, factories , on = "FCID" , how ="left")
print(f"북부지사의 평균 운송 비용 : {str(cost_chk['Cost'].loc[cost_chk['FCRegion'] == '북부'].mean())} , 남부지사의 평균 운송 비용 : {str(cost_chk['Cost'].loc[cost_chk['FCRegion'] == '남부'].mean())} ")


# 네트워크 시각화 
import networkx as nx
import matplotlib.pyplot as plt
G = nx.Graph()
G.add_node("nodeA")
G.add_node("nodeB")
G.add_node("nodeC")
G.add_edge("nodeA","nodeB") # edge는 arc라고 생각하면 된다 
G.add_edge("nodeA","nodeC")
G.add_edge("nodeB","nodeC")
pos = {}
pos["nodeA"]=(0,0)
pos["nodeB"]=(1,1)
pos["nodeC"]=(0,1)
nx.draw(G,pos)
plt.show()

G.add_node("nodeD")
G.add_edge("nodeA","nodeD")
pos["nodeD"]=(1,0)
nx.draw(G,pos,with_labels=True)



# 경로에 가중치 부여 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx 

df_w = pd.read_csv("network_weight.csv")
df_p = pd.read_csv("network_pos.csv")

size = 10
edge_weights = []
for i in range(len(df_w)) : 
  for j in range(len(df_w.columns)) : 
    edge_weights.append(df_w.iloc[i][j]*size)

G = nx.Graph()

for i in range(len(df_w.columns)):
  G.add_node(df_w.columns[i])

for i in range(len(df_w.columns)):
  for j in range(len(df_w.columns)):
    G.add_edge(df_w.columns[i], df_w.columns[j])

pos = {}
for i in range(len(df_w.columns)):
  node = df_w.columns[i]
  pos[node] = (df_p[node][0], df_p[node][1])

nx.draw(G, pos, with_labels = True , font_size =16 , node_size = 1000 , node_color ='k', font_color='w' , width = edge_weights)
plt.show()




df_tr = pd.read_csv("trans_route.csv" , index_col = '공장')
df_tr.head()


import pandas as pd 
import matplotlib.pyplot as plt
import networkx as nx 

df_pos = pd.read_csv("trans_route_pos.csv")

G = nx.Graph()

for i in range(len(df_pos.columns)) : 
  G.add_node(df_pos.columns[i])

num_pre = 0 
edge_weights = [] 
size = 0.1
for i in range(len(df_pos.columns)):
  for j in range(len(df_pos.columns)):
    if not (i == j) :
      G.add_edge(df_pos.columns[i],df_pos.columns[j])
      if num_pre < len(G.edges) : 
        num_pre = len(G.edges)
        weight = 0 
        if (df_pos.columns[i] in df_tr.columns)and(df_pos.columns[j] in df_tr.index) : 
          if df_tr[df_pos.columns[i]][df_pos.columns[j]]:
            weight = df_tr[df_pos.columns[i]][df_pos.columns[j]]*size
        elif (df_pos.columns[j] in df_tr.columns)and(df_pos.columns[i] in df_tr.index):
          if df_tr[df_pos.columns[j]][df_pos.columns[i]] : 
            weight  = df_tr[df_pos.columns[j]][df_pos.columns[i]]*size
        edge_weights.append(weight)

pos = {}
for i in range(len(df_pos.columns)) : 
  node = df_pos.columns[i]
  pos[node] = (df_pos[node][0],df_pos[node][1])

nx.draw(G , pos, with_labels = True , font_size =16 , node_size =1000 , node_color = 'k' , font_color='w' , width=edge_weights)
plt.show()


# 목적 함수 생성 

df_tr = pd.read_csv("trans_route.csv" , index_col = '공장')
df_tc = pd.read_csv("trans_cost.csv" , index_col = '공장')

def trans_cost(df_tr , df_tc) :
  cost = 0  
  for i in range(len(df_tr.index)):
    for j in range(len(df_tr.columns)):
      cost += df_tr.iloc[i][j] * df_tc.iloc[i][j]
  return cost 

print(f"총 운송 비용: {str(trans_cost(df_tr,df_tc))}") 



df_demand = pd.read_csv('demand.csv')
df_supply = pd.read_csv('supply.csv')
for i in range(len(df_demand.columns)) : 
  temp_sum = sum(df_tr[df_demand.columns[i]])
  print(str(df_demand.columns[i])+"으로 운송량 :"+str(temp_sum)+" (수요량:"+str(df_demand.iloc[0][i])+")")
  if temp_sum >= df_demand.iloc[0][i]:
    print("수요량을 만족시킨다")
  else : 
    print("수요량을 만족시키지 못함. 운송경로 재계산 필요")

for i in range(len(df_supply.columns)):
  temp_sum = sum(df_tr.loc[df_supply.columns[i]])
  print(str(df_supply.columns[i])+"으로 부터의 운송량 :"+str(temp_sum)+" (공급한계:"+str(df_supply.iloc[0][i])+")")
  if temp_sum >= df_supply.iloc[0][i]:
    print("공급한계 범위내")
  else:
    print("공급한계 초과. 운송경로 재계산 필요")
    
    
    
df_tr_new = pd.read_csv('trans_route_new.csv',index_col = '공장')
print("총 운송 비용(변경 후) :"+str(trans_cost(df_tr_new, df_tc)))

def condition_demand(df_tr , df_demand) :
  flag = np.zeros(len(df_demand.columns))
  for i in range(len(df_demand.columns)) : 
    temp_sum = sum(df_tr[df_demand.columns[i]])
    if (temp_sum >= df_demand.iloc[0][i]):
      flag[i] = 1 
  return flag 

def condition_supply(df_tr , df_supply) : 
  flag = np.zeros(len(df_supply.columns))
  for i in range(len(df_supply.columns)) : 
    temp_sum = sum(df_tr.loc[df_supply.columns[i]])
    if (temp_sum >= df_supply.iloc[0][i]):
      flag[i] = 1 
  return flag 

print("수요조건 계산결과:" + str(condition_demand(df_tr_new, df_demand)))

print("공급조건 계산결과:" + str(condition_supply(df_tr_new, df_supply)))

