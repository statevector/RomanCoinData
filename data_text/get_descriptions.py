
import requests
#from urllib.request import urlopen
#from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import re
import sys

headers = {"User-Agent": 
	"Analyzing Roman coins for a class project. \
	If problems, please contact me at willisc9@msu.edu"}

def get_html(url):
	try:
		html = requests.get(url, headers=headers)
	except HTTPError as e:
		exit('unable to load page')
	return html

def get_coin_urls(html):
	try:
		bs = BeautifulSoup(html, 'html.parser')
		urls = bs.find_all('td', attrs={'align':'center'})
	except AttributeError as e:
		exit('AttributeError with bs')	
	return [url.a['href'] for url in urls if url.a is not None]

def get_auction_type(bs):
	text = bs.find('h2', attrs={'id':'coin_hCont'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		result = re.search(r'(The Coin Shop|Electronic Auction|Feature Auction)', text)
		if result is not None:
			auction = str(result.group())
			return auction
		raise TypeError()
	except:
		exit('unable to find auction type')

def get_auction_ID(bs, auc):
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		if auc == 'Feature Auction':
			result = re.search(r'(CNG|Nomos|Triton) (\d|\w)+, ', text)
		if auc == 'Electronic Auction':
			result = re.search(r'\d+, ', text)
		if auc == 'The Coin Shop':
			result = 'CS'
		if result is not None:
			return str(result.group(0)[:-2]) # remove the ', '
		raise TypeError()
	except:
		exit('unable to find auction id')

def get_lot_number(bs):
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		result = re.search(r'Lot: \d+.', text)
		if result is not None:
			number = re.search(r'\d+.', result.group())
			if number is not None:
				return str(number.group(0)[:-1]) # remove the '.'
		raise TypeError()
	except:
		exit('unable to find lot number')

def get_lot_description(bs):
	div = bs.find('div', attrs={'class':'lot'})
	#print(div.contents)
	div.a.decompose() # remove image...?
	if div.h1 is not None:
		div.h1.decompose() # remove special title section (e.g. Deified and Rejuvenated Julius Caesar)
	div.table.decompose() # remove table of lot, sale, auction info
	if div.p is not None:
		div.p.decompose() # remove special coin notes section
	text = div.text
	description = text.replace(u'\xa0', u' ') # unicode formatting
	#description = description.split('\r') # split on line break
	description = description.strip()
	description = description.replace(',', '-')
	return description
	#re.sub('\s+',' ',lot_desc)
	#lot_desc = lot_desc.splitlines() # split on line breaks
	#lot_desc = list(filter(None, lot_desc)) # remove ''
	#print(lot_desc)

def get_sale_price(bs):
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	#text = text.replace('&nbsp;', ' ')
	text = text.replace(u'\xa0', u' ')
	try:
		result = re.search(r'Sold [Ff]or \$\d+', text)
		if result is not None:
			price = re.search(r'\d+', result.group())
			if price is not None:
				return int(price.group())
		raise TypeError()
	except:
		exit('unable to find sale price')

def get_sale_estimate(bs):
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	try:
		result = re.search(r'Estimate \$\d+', text)
		if result is not None:
			price = re.search(r'\d+', result.group())
			if price is not None:
				return int(price.group())
		raise TypeError()
	except:
		exit('unable to find sale estimate')


#<_io.TextIOWrapper name='/Users/cwillis/GitHub/RomanCoinModel/raw_data/CNG/html/Augustus_AR_PA1.html' mode='r' encoding='UTF-8'>
#urls loaded



if __name__ == '__main__':

	# augustus, denarius, eA
	#html = get_html('https://cngcoins.com/Search.aspx?PAGE_NUM=200&PAGE=1&TABS_TYPE=2&CONTAINER_TYPE_ID=2&IS_ADVANCED=1&ITEM_DESC=Augustus.+27+BC-AD+14.+AR+Denarius&ITEM_IS_SOLD=1&SEARCH_IN_CONTAINER_TYPE_ID_1=1&SEARCH_IN_CONTAINER_TYPE_ID_3=1&SEARCH_IN_CONTAINER_TYPE_ID_2=1&SEARCH_IN_CONTAINER_TYPE_ID_4=1#')
	#urls = get_coin_urls(html.text)

	# augustus, denarius, pA
	#html = open('/Users/cwillis/GitHub/RomanCoinData/data_raw/CNG/html/Augustus_AR_PA1.html', 'r')
	#print(html)
	#urls = get_coin_urls(html)

	html = open(sys.argv[1])
	print(html)
	urls = get_coin_urls(html)

	#urls = ["https://cngcoins.com/Coin.aspx?CoinID=388133"]

	#for idx, url in enumerate(urls):
	#	print(idx, url)
	
	print('Auction Type,Auction ID,Lot Number,Description,Estimate,Sale')

	for idx, url in enumerate(urls):
		
		#if idx>10: continue
		#print(idx, url)

		#html = urlopen(url)
		html = requests.get(url, headers=headers)
		bs = BeautifulSoup(html.text, 'html.parser')
		
		if 'CHF' in bs.text:
			continue

		if 'brockage' in bs.text:
			continue

		# grab auction type (CS, EA, PS)
		auction_type = get_auction_type(bs)
		#print(' Auction Type: {}'.format(auction_type))

		# grab auction id (Triton, CNG, etc.)
		auction_id = get_auction_ID(bs, auction_type)
		#print(' Auction ID: {}'.format(auction_id))

		# grab lot number
		lot = get_lot_number(bs)
		#print(' Lot Number: {}'.format(lot))

		# grab sale price
		price = get_sale_price(bs)
		#print(' Sale price: {}'.format(price))

		# grab estimate
		estimate = get_sale_estimate(bs)
		#print(' Sale estimate: {}'.format(estimate))

		# grab lot description
		description = get_lot_description(bs)
		#print(' Description: {}'.format(description))

		print('{},{},{},{},{},{}'.format(auction_type, \
			auction_id, lot, description, estimate, price))




