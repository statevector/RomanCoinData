
import requests
import re
import sys
import numpy as np
import pandas as pd
from collections import OrderedDict

from bs4 import BeautifulSoup

from io import BytesIO
from PIL import Image

# eliminate observations that contain the following words
stop_words = ['CHF', 'Lot of', 'Quinarius', 'Fourrée', 'fourrée', 'Fourée',
			  'Brockage', 'brockage', 'Official Dies', 'Forgery', 
			  'forgery', 'bezel', 'electrotype', 'MIXED', 'imitation', 
			  'IMITATION', 'INDIA', 'NGC encapsulation', 'ANACS', 
			  'Restitution issue']

headers = {"User-Agent": 
	"Analyzing Roman coins for a class project. \
	If problems, please contact me at willisc9@msu.edu"}

def get_coin_urls(html):
	try:
		bs = BeautifulSoup(html, 'html.parser')
		urls = bs.find_all('td', attrs={'align':'center'})
	except Exception as error:
		print(error)
	return ['https://cngcoins.com/'+url.a['href'] for url in urls if url.a is not None]

def get_image_url(data):
	image_url = None
	try:
		bs = BeautifulSoup(data, 'html.parser')
		image_url = bs.find('div', attrs={'class':'lot'}).img['src']
	except Exception as error:
		print(error)
	if image_url is None:
		raise TypeError('bs unable to grab image url')
	return image_url

def get_image(url): 
	r = requests.get(url, headers=headers)
	image = None
	if r.ok and 'image' in r.headers['content-type']:
		image = Image.open(BytesIO(r.content))
	else: 
		raise TypeError('requests unable to process image url')
	return image

def get_auction_type(data):
	text = None
	try:
		bs = BeautifulSoup(data, 'html.parser')
		text = bs.find('h2', attrs={'id':'coin_hCont'}).text
		text = text.replace(u'\xa0', u' ')
		#print(text)
	except Exception as error:
		print(error)
	try:
		result = re.search(r'(The Coin Shop|Electronic Auction|Feature Auction|Affiliated Auction)', text)
		if result is not None:
			auction = str(result.group())
			return auction
		raise TypeError()
	except:
		exit('unable to find auction type')

def get_auction_ID(data):
	bs = BeautifulSoup(data, 'html.parser')
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	auc = get_auction_type(data)
	try:
		if auc == 'Affiliated Auction':
			result = re.search(r'Nomos (\d|\w)+, ', text)
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

def get_auction_lot(data):
	bs = BeautifulSoup(data, 'html.parser')
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

def get_sale_estimate(data):
	bs = BeautifulSoup(data, 'html.parser')
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		result = re.search(r'Estimate (CHF|\$)\d+', text)
		if result is not None:
			price = re.search(r'\d+', result.group())
			if price is not None:
				return int(price.group())
		raise TypeError()
	except:
		exit('unable to find sale estimate')

def get_sale_price(data):
	bs = BeautifulSoup(data, 'html.parser')
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		result = re.search(r'Sold [Ff]or (CHF|\$)\d+', text)
		if result is not None:
			price = re.search(r'\d+', result.group())
			if price is not None:
				return int(price.group())
		raise TypeError()
	except:
		exit('unable to find sale price')

def get_lot_header(data):
	bs = BeautifulSoup(data, 'html.parser')
	header = bs.find('h1', attrs={'id':'coin_hHead'})
	if header is not None:
		#print(header)
		try:
			# remove commas to print to CSV
			return header.text.replace(',', '').strip()
		except TypeError as err:
			print('bs unable to grab lot header')
			raise
	return None

def get_lot_notes(data):
	bs = BeautifulSoup(data, 'html.parser')
	notes = bs.find('p', attrs={'id':'coin_pNotes'})
	if notes is not None:
		#print(notes)
		try:
			if notes.text == ' ':
				return None
			else:
				# remove commas to print to CSV
				return notes.text.replace(',', '').strip()
		except TypeError as err:
			print('bs unable to grab lot notes')
			raise
	return None

def get_lot_description(data):
	bs = BeautifulSoup(data, 'html.parser')
	div = bs.find('div', attrs={'class':'lot'})
	#print(div.contents)
	# remove image link
	if div.a is not None:
		div.a.decompose()
	# remove special title section 
	# (e.g. "Deified and Rejuvenated Julius Caesar")
	if div.h1 is not None:
		div.h1.decompose()
	# remove table of lot, sale, auction info
	if div.table is not None:
		div.table.decompose()
	# remove special coin notes section
	if div.p is not None:
		div.p.decompose()
	# remove white space
	try:
		text = div.text.strip()
	except TypeError as err:
		print('bs unable to grab lot description')
		raise
	# remove commas to print to CSV
	return text.replace(',', '')

def is_nonstandard_lot(text):
	return any(word in text for word in stop_words)

if __name__ == '__main__':

	html = open(sys.argv[1], 'r')

	page_urls = get_coin_urls(html)
	print(page_urls)
	print(len(page_urls))

	# need to understand header here. why NaN?
	# https://cngcoins.com/Coin.aspx?CoinID=362783

	#Auction Type,Auction ID,Auction Lot,Estimate,Sold,Header,Notes,Description,Nonstandard Lot,URL,URL Image

	lod=[]

	for idx, url in enumerate(page_urls):
		
		#if idx>3: continue
		print(idx)

		# ordered dict to preserve dataframe header order
		scraped = OrderedDict()

		r = requests.get(url, headers=headers)
		data = r.text

		# store the URL of the page on which the coin is listed
		scraped['URL'] = url
		print(' URL: {}'.format(url))

		# grab auction type
		auction_type = get_auction_type(data)
		scraped['Auction Type'] = auction_type
		print(' Auction Type: {}'.format(auction_type))

		# grab auction id (Triton, CNG, etc.)
		auction_id = get_auction_ID(data)
		scraped['Auction ID'] = auction_id
		print(' Auction ID: {}'.format(auction_id))

		# grab lot number
		acution_lot = get_auction_lot(data)
		scraped['Auction Lot'] = acution_lot
		print(' Auction Lot: {}'.format(acution_lot))

		# grab the sale estimate
		sale_estimate = get_sale_estimate(data)
		scraped['Estimate'] = sale_estimate
		print(' Estimate: {}'.format(sale_estimate))

		# grab the sale price
		sale_price = get_sale_price(data)
		scraped['Sold'] = sale_price
		print(' Sold: {}'.format(sale_price))

		# grab the lot header if present
		header = get_lot_header(data)
		scraped['Header'] = header
		print(' Header: {}'.format(header))

		# grab the lot description
		description = get_lot_description(data)
		scraped['Description'] = description
		print(' Description: {}'.format(description))

		# grab the lot notes if present
		notes = get_lot_notes(data)
		scraped['Notes'] = notes
		print(' Notes: {}'.format(notes))

		# identify nonstandard lots (i.e. those with a stop word)
		nonstandard_lot = is_nonstandard_lot(description)
		scraped['Nonstandard Lot'] = nonstandard_lot
		print(' Nonstandard Lot: {}'.format(nonstandard_lot))

		# store the URL of the auction page
		img_url = get_image_url(data)
		scraped['Image URL'] = img_url
		print(' Image URL: {}'.format(img_url))

		# store the image path and save the image of the coin locally
		img = get_image(img_url)
		img_path = 'data_scraped/images/'+img_url.split('/')[-1]
		img.save(img_path)
		scraped['Image Path'] = img_path
		print(' Image Path: {}'.format(img_path))

		lod.append(scraped)

	df = pd.DataFrame(lod)

	df.to_csv('data_scraped/text/'+sys.argv[1].split('/')[-1].split('.')[0]+'.csv', index=False)

