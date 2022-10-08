
# 데이터 정합성에 문제가 있는 데이터 불러오기 
import pandas as pd 
uriage = pd.read_csv("uriage.csv")
uriage.head()
kokyaku_daicho = pd.read_excel('kokyaku_daicho.xlsx')
kokyaku_daicho.head()


# 정합성 맞추기 
len(pd.unique(uriage['item_name']))
uriage['item_name'] = uriage['item_name'].str.upper() # 대문자
uriage['item_name'] = uriage['item_name'].str.replace(' ','') # 공백 제거 
uriage['item_name'] = uriage['item_name'].str.replace('  ','') # 공백 제거 
uriage.sort_values(by=['item_name'], ascending = True)
kokyaku_daicho['고객이름'] = kokyaku_daicho['고객이름'].str.replace(' ','')
kokyaku_daicho['고객이름'] = kokyaku_daicho['고객이름'].str.replace('  ','')
num = kokyaku_daicho['등록일'].astype("str").str.isdigit() # 숫자인 것만 따로 빼내기 위해 사용 
time = pd.to_timedelta(kokyaku_daicho.loc[num,"등록일"].astype("float"), unit="D") + pd.to_datetime("1900/01/01")
time2 = pd.to_datetime(kokyaku_daicho.loc[~num,'등록일'])
kokyaku_daicho['등록일'] = pd.concat([time,time2])
kokyaku_daicho['등록연월'] = kokyaku_daicho['등록일'].dt.strftime("%Y-%m")
uriage['purchase_month'] = pd.to_datetime(uriage['purchase_date']).dt.strftime("%Y-%m")

# 월별 고객 등록 수 
account = kokyaku_daicho.groupby('등록연월').count()['고객이름']
print(account)


# 결측치 제거 
uriage.isna().sum()

nadata = uriage['item_price'].isna() # 결측치가 있는 행만 따로 빼내기 위해 사용 
for nulldata in list(uriage.loc[nadata , "item_name"].unique()) : 
  price = uriage.loc[(~nadata) & (uriage['item_name'] == nulldata),'item_price'].max()
  uriage['item_price'].loc[(nadata) & (uriage['item_name'] == nulldata)] = price 
  
# 해당 기간 내 구매를 하지 않은 고객  
away_data = pd.merge(uriage , kokyaku_daicho , left_on = 'customer_name' , right_on='고객이름', how = 'right')
away_data[away_data['purchase_date'].isna()][['고객이름','등록일']]  
  
  
# 테이블 결합 및 csv 파일로 덤프
join_data = pd.merge(uriage,kokyaku_daicho ,left_on = 'customer_name' , right_on = '고객이름', how = 'left')
join_data.drop('customer_name' , axis=1)
dump_data = join_data[['purchase_date','purchase_month','item_name','item_price','고객이름','지역','등록일']]
dump_data.to_csv('dump_data.csv', index=False)

# 데이터 파악 
customer_data = pd.read_csv('dump_data.csv')
print(customer_data.describe())
print(customer_data['purchase_month'].min())
print(customer_data['purchase_month'].max())

# pivot 

itemsize = customer_data.pivot_table(index='purchase_month',columns='item_name' , aggfunc="size" , fill_value =0)
itemprice = customer_data.pivot_table(index='purchase_month',columns='item_name' ,values ='item_price',aggfunc="sum" , fill_value =0)
Buycustomer = customer_data.pivot_table(index='purchase_month',columns='고객이름' ,aggfunc="size" , fill_value =0)
BuyRegion = customer_data.pivot_table(index='purchase_month',columns='지역' ,aggfunc="size" , fill_value =0)



