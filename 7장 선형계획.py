!pip install pulp 
!pip install ortoolpy

import numpy as np
import pandas as pd 
from itertools import product
from pulp import LpVariable, lpSum , value
from ortoolpy import model_min, addvars, addvals 


df_tc = pd.read_csv('trans_cost.csv' , index_col ='공장')
df_demand = pd.read_csv('demand.csv')
df_supply = pd.read_csv('supply.csv')


np.random.seed(1)
nw = len(df_tc.index) # 3 (W1,W2,W3 공장)
nf = len(df_tc.columns) # 4 (F1, F2, F3, F4 창고)
pr = list(product(range(nw),range(nf))) # product()는 (0, 0)같은 좌표를 만들어 낸다 


# 목적 함수 
m1 = model_min() # 최소화를 실행하는 모델 
v1 = {(i,j):LpVariable('v%d_%d'%(i,j),lowBound=0) for i,j in pr} # 변수 선언 
m1 += lpSum(df_tc.iloc[i][j]*v1[i,j] for i,j in pr) #  목적함수 (lpSum을 사용해 각 요소 곱의 합을 한다)



# 제약 조건 
for i in range(nw):
  m1 += lpSum(v1[i,j] for j in range(nf)) <= df_supply.iloc[0][i]
for j in range(nf):
  m1 += lpSum(v1[i,j] for i in range(nw)) >= df_demand.iloc[0][j]
  
  
# 변수 v1 최적화 
m1.solve()


df_tr_sol = df_tc.copy()
total_cost = 0 
for k,x in v1.items():
  i,j = k[0],k[1]
  df_tr_sol.iloc[i][j] = value(x)
  total_cost += df_tc.iloc[i][j]*value(x)
print(df_tr_sol)
print("총 운송 비용:"+str(total_cost))



# 네트워크 가시화 
import matplotlib.pyplot as plt
import networkx as nx

df_tr = df_tr_sol.copy()
df_pos = pd.read_csv('trans_route_pos.csv')

G = nx.Graph()
for i in range(len(df_pos.columns)) : 
  G.add_node(df_pos.columns[i])
num_pre = 0 
edge_weights = [] 
size = 0.1
for i in range(len(df_pos.columns)):
  for j in range(len(df_pos.columns)):
    if not (i==j):
      G.add_edge(df_pos.columns[i], df_pos.columns[j])
      if num_pre< len(G.edges):
        num_pre = len(G.edges)
        weight = 0 
        if (df_pos.columns[i] in df_tr.columns)and(df_pos.columns[j] in df_tr.index):
          if df_tr[df_pos.columns[i]][df_pos.columns[j]]:
            weight= df_tr[df_pos.columns[i]][df_pos.columns[j]]*size
        elif(df_pos.columns[j] in df_tr.columns)and(df_pos.columns[i] in df_tr.index):
          if df_tr[df_pos.columns[j]][df_pos.columns[i]]:
            weight = df_tr[df_pos.columns[j]][df_pos.columns[i]]*size
        edge_weights.append(weight)

pos={}
for i in range(len(df_pos.columns)):
  node = df_pos.columns[i]
  pos[node] = (df_pos[node][0],df_pos[node][1])

nx.draw(G, pos, with_labels = True, font_size =16, node_size = 1000, node_color ='k', font_color='w',width = edge_weights)
plt.show()



def condition_demand(df_tr, df_demand) :
  flag = np.zeros(len(df_demand.columns)) # [0., 0., 0., 0.] 생성
  for i in range(len(df_demand.columns)):
    temp_sum = sum(df_tr[df_demand.columns[i]])
    if(temp_sum>=df_demand.iloc[0][i]):
      flag[i] = 1 
  return flag

def condition_supply(df_tr, df_supply):
  flag = np.zeros(len(df_supply.columns))
  for i in range(len(df_supply.columns)):
    temp_sum = sum(df_tr.loc[df_supply.columns[i]])
    if temp_sum <= df_supply.iloc[0][i]:
      flag[i] = 1
  return flag

print("수요 조건 계산 결과:"+str(condition_demand(df_tr,df_demand)))
print("공급 조건 계산 결과:"+str(condition_supply(df_tr, df_supply)))



df_material = pd.read_csv('product_plan_material.csv', index_col = "제품")
df_profit = pd.read_csv('product_plan_profit.csv',index_col = "제품")
df_stock = pd.read_csv('product_plan_stock.csv',index_col = "항목")
df_plan = pd.read_csv('product_plan.csv',index_col = "제품")


def product_plan(df_profit, df_plan):
  profit = 0
  for i in range(len(df_profit.index)):
    for j in range(len(df_plan.columns)):
      profit += df_profit.iloc[i][j]*df_plan.iloc[i][j]
    return profit
print("총 이익:"+str(product_plan(df_profit,df_plan)))



from ortoolpy import model_max
df = df_material.copy()
inv = df_stock

m = model_max()
v1 = {(i):LpVariable('v%d'%(i),lowBound=0)for i in range(len(df_profit))}
m += lpSum(df_profit.iloc[i]*v1[i] for i in range(len(df_profit)))
for i in range(len(df_material.columns)):
  m += lpSum(df_material.iloc[j,i]*v1[j] for j in range(len(df_profit))) <= df_stock.iloc[:,i]
m.solve()

df_plan_sol = df_plan.copy()
for k,x in v1.items():
  df_plan_sol.iloc[k] = value(x)
print(df_plan_sol)
print("총 이익:"+str(value(m.objective)))


def condition_stock(df_plan, df_material, df_stock):
  flag = np.zeros(len(df_material.columns))
  for i in range(len(df_material.columns)):
    temp_sum = 0
    for j in range(len(df_material.index)):
      temp_sum = temp_sum + df_material.iloc[j][i]*float(df_plan.iloc[j])
    if (temp_sum <= float(df_stock.iloc[0][i])):
      flag[i] =1 
    print(df_material.columns[i] + "사용량:"+str(temp_sum)+", 재고:"+ str(float(df_stock.iloc[0][i])))
  return flag
print("제약 조건 계산 결과:"+str(condition_stock(df_plan_sol,df_material,df_stock)))


제품 = list('AB')
수요지 = list('PQ')
공장 = list('XY')
레인 = (2,2)

tbdi = pd.DataFrame(((j,k)for j in 수요지 for k in 공장) , columns =['대리점','공장'])
tbdi['운송비'] = [1,2,3,1]
print(tbdi)
tbde = pd.DataFrame(((j,i)for j in 수요지 for i in 제품),columns=['대리점','제품'])
tbde['수요'] = [10,10,20,20]
print(tbde)
tbfa = pd.DataFrame(((k, l, i , 0 , np.inf) for k,nl in zip (공장,레인) for l in range(nl) for i in 제품), columns=['공장','레인','제품','하한','상한'])
tbfa['생산비'] = [1,np.nan,np.nan,1,3,np.nan,5,3]
tbfa.dropna(inplace=True)
tbfa.loc[4,'상한'] = 10
print(tbfa)
from ortoolpy import logistics_network
_, tbdi2, _ = logistics_network(tbde, tbdi, tbfa, dep = '대리점', dem = '수요', fac = '공장', prd = '제품', tcs = '운송비' , pcs ='생산비', lwb = '하한', upb='상한')
print(tbfa)
print(tbdi2)


tbdi2 = tbdi2[['공장','대리점','운송비','제품','VarX','ValX']]
trans_cost = 0 
for i in range(len(tbdi2.index)):
  trans_cost += tbdi2['운송비'].iloc[i]*tbdi2['ValX'].iloc[i]
print("총 운송비:"+str(trans_cost))


product_cost = 0
for i in range(len(tbfa.index)):
  product_cost += tbfa['생산비'].iloc[i]*tbfa['ValY'].iloc[i]
print("총 생산비:"+str(product_cost))
