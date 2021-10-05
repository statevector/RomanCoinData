
import requests
from bs4 import BeautifulSoup
import re
from collections import OrderedDict
import pandas as pd

headers = {"User-Agent": 
	"Analyzing Roman coins for a class project. \
	If problems, please contact me at willisc9@msu.edu"}

def get_html(url):
	r = requests.get(url)
	if r.status_code != 200:
		raise Exception('Unable to Connect to {}'.format(url))
	return r.text

def get_links(html, verbose=True):
	bs = BeautifulSoup(html, 'html.parser')
	urls = bs.find_all('a', attrs={'class':'prbl'})
	if urls == []:
		raise Exception('Unable to identify relevant links in pulled HTML')
	if verbose:
		print('Pulled URLs:\n{}'.format(urls))
	urls = {url.text: 'https://cngcoins.com/'+url.get('href') for url in urls}
	if verbose:
		print('Formatted URLs:\n{}'.format(urls))
	return urls

if __name__ == '__main__':
	
	# feature auctions
	#url = 'https://cngcoins.com/PricesRealized.aspx?CONTAINER_TYPE_ID=3'
	#output = 'data_dates/feature_auction_dates.csv'
	
	# weekly auctions
	url = 'https://cngcoins.com/PricesRealized.aspx?CONTAINER_TYPE_ID=2'
	output = 'data_dates/eAuction_dates.csv'

	# grab info
	html = get_html(url)
	urls = get_links(html)
	#print(urls)
	# iterate over urls for date information
	lod=[]
	for i, (text, url) in enumerate(urls.items()):
		#if i>3: continue
		print(i)
		# ordered dict to preserve dataframe column order
		scraped = OrderedDict()
		# get the page
		html = get_html(url)
		# regex search for date pattern on page
		x = re.search(r'\w+ [\d]\d, \d{4,4}', html)
		#print(x)
		date = None
		try:
			date = x.group()
		except:
			print('error')
		# save the url
		scraped['URL'] = url
		print(' URL: {}'.format(url))
		# save the auction date
		scraped['Auction Date'] = date
		print(' Auction Date: {}'.format(date))
		# save the auction ID
		scraped['Auction ID'] = text
		print(' Auction ID: {}'.format(text))
		# append to the list
		lod.append(scraped)
	# build and save the dataframe
	df = pd.DataFrame(lod)
	df.to_csv(output, index=False)

