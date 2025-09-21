#!/usr/bin/env python
# coding: utf-8

#import libraries
!pip install kaggle
import kaggle

# !kaggle datasets download ankitbansal06/retail-orders -f orders.csv

#extract file from zip file
import zipfile
zip_ref = zipfile.ZipFile('orders.csv.zip') 
zip_ref.extractall() # extract file to dir
zip_ref.close() # close file


#read data from the file and handle null values
import pandas as pd
df = pd.read_csv('orders.csv',na_values=['Not Available','unknown'])
df['Ship Mode'].unique()

#rename columns names ..make them lower case and replace space with underscore
df.rename(columns={'Order Id':'order_id', 'City':'city'})
df.columns=df.columns.str.lower()
df.columns=df.columns.str.replace(' ','_')
df.head(5)




#derive new columns discount , sale price and profit
df['discount']=df['list_price']*df['discount_percent']*.01
df['sale_price']= df['list_price']-df['discount']
df['profit']=df['sale_price']-df['cost_price']
df

#convert order date from object data type to datetime
df['order_date']=pd.to_datetime(df['order_date'],format="%Y-%m-%d")


#drop cost price list price and discount percent columns
df.drop(columns=['list_price','cost_price','discount_percent'],inplace=True)

#load the data into sql server using replace option
import urllib.parse as up
import sqlalchemy as sa

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=localhost\\SQLEXPRESS;"
    "Database=master;"
    "Trusted_Connection=yes;"
)
engine = sa.create_engine(f"mssql+pyodbc:///?odbc_connect={up.quote_plus(conn_str)}")
conn = engine.connect()



#load the data into sql server using append option
df.to_sql('df_orders', con=conn , index=False, if_exists = 'append')


