
import requests
import re
import sys
import os

import numpy as np
import pandas as pd

from collections import OrderedDict

from bs4 import BeautifulSoup

from io import BytesIO
from PIL import Image

# remove whitespace
#import re
#pattern = re.compile(r'\s+')
#sentence = re.sub(pattern, '', sentence)

# eliminate observations that contain the following words
stop_words = ['CHF', 'Lot of', 'Quinarius', 'Fourrée', 'fourrée', 'Fourée',
			  'Brockage', 'brockage', 'Official Dies', 'Forgery', 
			  'forgery', 'bezel', 'electrotype', 'MIXED', 'imitation', 
			  'IMITATION', 'INDIA', 'NGC encapsulation', 'ANACS', 
			  'Restitution issue']

headers = {"User-Agent": 
	"Analyzing Roman coins for a class project. \
	If problems, please contact me at willisc9@msu.edu"}

def get_page_urls(html):
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
			# remove commas for print to CSV
			header = header.text.replace(',', '').strip()
			# remove whitespace
			return ' '.join(header.split())
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
				# remove commas for print to CSV
				notes = notes.text.replace(',', '').strip()
				# remove whitespace
				return ' '.join(notes.split())
		except TypeError as err:
			print('bs unable to grab lot notes')
			raise
	return None

def get_lot_description(data):
	bs = BeautifulSoup(data, 'html.parser')
	desc = bs.find('div', attrs={'class':'lot'})
	#print(desc.contents)
	# remove image link
	if desc.a is not None:
		desc.a.decompose()
	# remove special title section 
	# (e.g. "Deified and Rejuvenated Julius Caesar")
	if desc.h1 is not None:
		desc.h1.decompose()
	# remove table of lot, sale, auction info
	if desc.table is not None:
		desc.table.decompose()
	# remove special coin notes section
	if desc.p is not None:
		desc.p.decompose()
	try:
		# remove commas for print to CSV
		desc = desc.text.replace(',', '').strip()
	except TypeError as err:
		print('bs unable to grab lot description')
		raise
	# remove whitespace
	return ' '.join(desc.split())

def is_nonstandard_lot(text):
	return any(word in text for word in stop_words)


if __name__ == '__main__':

	print(' Script name: {}'.format(sys.argv[0]))
	print(' Number of arguments: {}'.format(len(sys.argv)))
	print(' Arguments include: {}'.format(str(sys.argv)))

	if len(sys.argv)!=2: 
		exit('missing input!')

	# create output directory for scraped text and image files
	input_file = sys.argv[1]
	outname = input_file.split('/')[-1].split('.')[0]+'.csv'
	print(outname)
	outdir = 'data_scraped/'+input_file.split('/')[-1].split('.')[0]
	print(outdir)
	if not os.path.exists(outdir):
		os.mkdir(outdir)
	else:
		exit('directory exists!')
	fullname = os.path.join(outdir, outname)

	# convert input to html and extract html page links
	html_page = open(input_file, 'r')
	page_urls = get_page_urls(html_page)
	print(page_urls)
	print(len(page_urls))
	
	lod=[]

	for idx, url in enumerate(page_urls):
		
		#if idx>3: continue
		print(idx)

		# ordered dict to preserve dataframe column order
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

		# grab the URL of the image on the auction page
		img_url = get_image_url(data)
		scraped['Image URL'] = img_url
		print(' Image URL: {}'.format(img_url))

		# store the image path and save the image
		img = get_image(img_url)
		img_path = outdir+'/'+img_url.split('/')[-1]
		scraped['Image Path'] = img_path
		print(' Image Path: {}'.format(img_path))
		img.save(img_path)

		lod.append(scraped)

	# build and save the dataframe
	df = pd.DataFrame(lod)
	df.to_csv(fullname, index=False)

