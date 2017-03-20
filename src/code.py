#Loading required libraries
import json
import re
import pandas as pd
import numpy as np
from collections import OrderedDict
from datetime import datetime

NUM = int(input('Enter the no of files: \n')) #Reading the no. of input files.
X = int(input('No of desired customers in the output: \n')) #Reading the no. of top 'X' customers.

#Declaring data frames for customer,site_visits & orders.
df_customer = pd.DataFrame(OrderedDict((('customer_id', '0') , ('last_name', '0'), ('adr_city', '0'), ('adr_state', '0'))), index = [0])
df_visit = pd.DataFrame(OrderedDict((('customer_id', '0'), ('event_time', '0'), ('weeks_from_refr', '0'))), index = [0])
df_order = pd.DataFrame(OrderedDict((('customer_id', '0'), ('event_time', '0'), ('weeks_from_refr', '0'), ('total_amount', '0'))), index = [0])


#Ingest Method 
def Ingest(e, df_customer, df_visit, df_order):
	
	reference_date = datetime.now()
	
	#Reading the events file and conversion to json
	temp = open(e, 'r')
	file = temp.read()
	content = json.loads(file)
	
	row , col = df_customer.shape
	row_c = row; col_c = col
	           
	row, col = df_visit.shape
	row_v = row; col_v = col
	
	row, col = df_order.shape
	row_o = row; col_o = col
	
	for i in (range(len(content))):

                #Checking for Customer Type and reading the customers data into df_customer dataframe.
		if(content[i]['type'] == 'CUSTOMER'):
		
			df_customer.loc[row_c ,'customer_id'] = content[i]['key']
			df_customer.loc[row_c ,'last_name'] = content[i]['last_name']
			df_customer.loc[row_c ,'adr_city'] = content[i]['adr_city']
			df_customer.loc[row_c ,'adr_state'] = content[i]['adr_state']

			row_c += 1
               
		#Checking for Site_Visit Type and reading the site_visits data into df_visit dataframe.	
		if(content[i]['type'] == 'SITE_VISIT'):
		
			df_visit.loc[row_v, 'customer_id'] = content[i]['customer_id']
			df_visit.loc[row_v, 'event_time'] = datetime.strptime(content[i]['event_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
			
			temp = str(reference_date - df_visit.loc[row_v, 'event_time'])
			temp = re.findall(r'\d+', temp)[0]
			temp = int(float(temp)/7)
			df_visit.loc[row_v, 'weeks_from_refr'] = temp
			
			row_v += 1
              
	        #Checking for Order Type and reading the orders data into df_order dataframe.	
		if(content[i]['type'] == 'ORDER'):
		
			df_order.loc[row_o, 'customer_id'] = content[i]['customer_id']
			
			temp = content[i]['total_amount'].split(' ')
			df_order.loc[row_o, 'total_amount'] = float(temp[0])
			df_order.loc[row_o, 'event_time'] = datetime.strptime(content[i]['event_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
			
			temp = str(reference_date - df_order.loc[row_o, 'event_time'])
			temp = re.findall(r'\d+', temp)[0]
			temp = int(float(temp)/7)
			df_order.loc[row_o, 'weeks_from_refr'] = temp
		
			row_o += 1
			
	return(df_customer, df_visit, df_order)

#Looping through all the input event files passed.   	
for i in range(NUM):
        	
	file_name = 'events_' + str(i+1) + '.txt'
	df_customer, df_visit, df_order = Ingest(file_name, df_customer, df_visit,  df_order)
	
df_customer = df_customer.drop(df_customer.index[[0]])

df_visit = df_visit.drop(df_visit.index[[0]])

df_order = df_order.drop(df_order.index[[0]])
df_order['total_amount'] = pd.to_numeric(df_order['total_amount'])

#Declaring the Top 'X' customers method.
def TopXSimpleLTVCustomers(X, df_visit, df_order, df_customer):
	
        #Defining the dictionaries for both visits and orders.
	ltvOrder = OrderedDict()
	ltvVisit = OrderedDict()
	
	#Calculating the average orders amount for each customer at week level. 
	for name, group in df_order.groupby('customer_id'):
	
		id = name
		mean = group['total_amount'].groupby(group['weeks_from_refr']).mean()  #Calculating the average customer expenditures at week level.
		ltvOrder[id] = re.findall(r'[\d+.]+', str(mean))
		LTV_Order = pd.DataFrame(list(ltvOrder.items()), columns=['customer_id', 'Amount'])
	
        #Calculating the count of visits for each customer at week level.	
	for name, group in df_visit.groupby('customer_id'):	
	
		id = name
		count = group['event_time'].groupby(group['weeks_from_refr']).count()
		ltvVisit[id] = re.findall(r'\d+', str(count))
		LTV_Visit = pd.DataFrame(list(ltvVisit.items()), columns=['customer_id', 'Visits'])
	
	row, col = LTV_Visit.shape
	for i in range(row):
		temp = LTV_Visit.loc[i, 'Visits']
		for j in range(len(temp)):
			if j%2 == 0:
				no = temp[j]
			else:
				name = 'visitWeek' + str(no)
				LTV_Visit.loc[i,name] = temp[j]
	
	del(LTV_Visit['Visits'])
	
	row, col = LTV_Order.shape
	for i in range(row):
		temp = LTV_Order.loc[i, 'Amount']
		for j in range(len(temp)):
			if j%2 == 0:
				no = temp[j]
			else:
				name = 'amountWeek' + str(no)
				LTV_Order.loc[i,name] = temp[j]
	
	del(LTV_Order['Amount'])
	
	DF = pd.merge(LTV_Order, LTV_Visit, on='customer_id', how='outer')
	DF = DF.fillna(0)
	
	row, col = DF.shape
	col_in = col
	
	cl = int((col-1)/2)
	
	for i in range(cl):
	
		temp = re.findall(r'\d+', list(DF.columns.values)[i+1])[0]
		col_name = 'a' + str(temp)
		
		col_name1 = list(DF.columns.values)[i+1]
		DF[col_name1] = pd.to_numeric(DF[col_name1])
		
		col_name2 = list(DF.columns.values)[i+1+cl]
		DF[col_name2] = pd.to_numeric(DF[col_name2])
		
		DF[col_name] = DF[col_name1].multiply(DF[col_name2], axis = 'index')
	
	row, col = DF.shape
	col_fin = col
	
	for i in range(row):
		DF.loc[i, 'averageLTV'] = np.sum(DF.ix[i,(col_in):(col_fin)])*52*10
	
	DF = pd.merge(DF, df_customer, on='customer_id', how='outer')
	#Sorting all LTV's in descending order for all 'X' customers.
        DF = DF.sort_values('averageLTV', ascending = False)
	return(DF.head(X))
		
LTV = TopXSimpleLTVCustomers(X, df_visit, df_order, df_customer)
print(LTV)
