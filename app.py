from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import numpy as np

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data?start_date=2022-06-01&end_date=2022-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'card-block'})

#find the row length
row = table.find_all('th', attrs={'class':'font-semibold text-center'})
row_length = len(row)

#Since all the column's values have the same class (text-center), we will create its own length for later looping
val = table.find_all('td', attrs={'class':'text-center'})
val_length = len(val)

temp_p = []#initiating a list for period
temp_v = []#initiating a list for volume
temp_o = []#initiating a list for open

#scrapping process
for i in range(0, row_length):

    #get period
    period = table.find_all('th', attrs={'class':'font-semibold text-center'})[i].text
        
    temp_p.append(period)
    
for v in range(1, val_length, 4):
    
    #get volume
    volume = table.find_all('td', attrs={'class':'text-center'})[v].text
    volume = volume.strip()
    
    temp_v.append(volume)

for o in range(2, val_length, 4):
    
    #get open
    op = table.find_all('td', attrs={'class':'text-center'})[o].text
    op = op.strip()
    
    temp_o.append(op)


tempv = list(zip(temp_p,temp_v))
tempv = tempv[::-1]

tempo = list(zip(temp_p,temp_o))
tempo = tempo[::-1]

#change into dataframe(volume)
df = pd.DataFrame(tempv, columns=('Date','Volume($)'))

#insert data wrangling here(volume)
df['Date'] = pd.to_datetime(df['Date'])
df['Volume($)'] = df['Volume($)'].str.replace(",","")
df['Volume($)'] = df['Volume($)'].str.replace("$","")
df['Volume($)'] = df['Volume($)'].astype('int64')
df['Month Day'] = df['Date'].dt.strftime('%B %d')
df = df.set_index('Month Day')
df.drop('Date',inplace=True, axis=1)

#change into dataframe(open)
df_o = pd.DataFrame(tempo, columns=('Date','Open($)'))

#insert data wrangling here(volume)
df_o['Date'] = pd.to_datetime(df_o['Date'])
df_o['Open($)'] = df_o['Open($)'].str.replace(",","")
df_o['Open($)'] = df_o['Open($)'].str.replace("$","")
df_o['Open($)'] = df_o['Open($)'].astype('float64')
df_o['Month Day'] = df_o['Date'].dt.strftime('%B %d')
df_o = df_o.set_index('Month Day')
df_o.drop('Date',inplace=True, axis=1)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Volume($)"].mean()}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	ax.plot(df.index.values,
        df['Volume($)'],
       color='red')

	plt.xlabel("2022 DATE", fontweight='bold')                           
	plt.ylabel("VOLUME", fontweight='bold')                          
	plt.xticks(np.array(df.index),np.array(df.index),rotation=45)
	plt.yticks(rotation=45)
	plt.legend(fontsize=12)

	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# generate plot open
	ax_o = df_o.plot(figsize = (20,9)) 
	ax_o.plot(df_o.index.values,
        df_o['Open($)'],
       color='blue')

	plt.xlabel("2022 DATE", fontweight='bold')                           
	plt.ylabel("OPEN($)", fontweight='bold')                          
	plt.xticks(np.array(df_o.index),np.array(df_o.index),rotation=45)
	plt.yticks(rotation=45)
	plt.legend(fontsize=12)

	# Rendering plot open
	# Do not change this
	figfile_o = BytesIO()
	plt.savefig(figfile_o, format='png', transparent=True)
	figfile_o.seek(0)
	figdata_pngo = base64.b64encode(figfile_o.getvalue())
	plot_resulto = str(figdata_pngo)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_resulto = plot_resulto
		)

#@app.route("/")
#def index1(): 
	
#	card_data = f'{df_o["Open($)"].mean()}' #be careful with the " and ' 

#	# generate plot
#	ax_o = df_o.plot(figsize = (20,9)) 
#	ax_o.plot(df_o.index.values,
#        df_o['Open($)'],
#      color='blue')

#	plt.xlabel("2022 DATE", fontweight='bold')                           
#	plt.ylabel("OPEN($)", fontweight='bold')                          
#	plt.xticks(np.array(df_o.index),np.array(df_o.index),rotation=45)
#	plt.yticks(rotation=45)
#	plt.legend(fontsize=12)

#	# Rendering plot
#	# Do not change this
#	figfile = BytesIO()
#	plt.savefig(figfile, format='png', transparent=True)
#	figfile.seek(0)
#	figdata_png = base64.b64encode(figfile.getvalue())
#	plot_result = str(figdata_png)[2:-1]

#	# render to html
#	return render_template('index.html',
#		card_data = card_data, 
#		plot_result1=plot_result
#		)

if __name__ == "__main__": 
    app.run(debug=True)