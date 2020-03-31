
import requests
import re
import sys
import numpy as np

from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image

# array printing
np.set_printoptions(threshold=sys.maxsize)
#np.set_printoptions(threshold=np.inf)

# eliminate observations that contain the following words
stop_words = ['CHF', 'Lot of', 'Quinarius', 'Fourrée', 'fourrée', 'Fourée',
			  'Brockage', 'brockage', 'Official Dies', 'Æ', 'Forgery', 
			  'forgery', 'bezel', 'electrotype', 'MIXED', 'imitation', 
			  'IMITATION', 'INDIA', 'NGC encapsulation', 'ANACS', 
			  'Restitution issue']

headers = {"User-Agent": 
	"Analyzing Roman coins for a class project. \
	If problems, please contact me at willisc9@msu.edu"}

def get_html(url):
	try:
		html = requests.get(url, headers=headers)
	except HTTPError as err:
		exit('unable to load page')
	return html

def url_to_image(url, gray=False): 
	res = requests.get(url, headers=headers)
	if res.ok and 'image' in res.headers['content-type']:
		image = Image.open(BytesIO(res.content))
		if gray:
			image = image.convert('L') #LA
		return image
	else: 
		raise TypeError('requests unable to process image url')
	return None

def image_to_array(img, flatten=False): 
	arr_img = np.asarray(img)
	if flatten:
		return arr_img.flatten(), arr_img.shape
	return arr_img, arr_img.shape

def array_to_string(arr): 
	arr = arr.tolist()
	arr = ' '.join([str(x) for x in arr])
	return arr

def string_to_array(x, rows, cols, chan): 
	# np.array([int(x) for x in arr if x!=' ']) # convert back to np array
	a = np.array(list(map(int, x.split(' '))), np.uint8)
	a = a.reshape(a, rows, cols, chan) #151,300,3
	return a

def get_coin_urls(html):
	try:
		bs = BeautifulSoup(html, 'html.parser')
		urls = bs.find_all('td', attrs={'align':'center'})
	except AttributeError as err:
		exit('AttributeError with bs')
	return [url.a['href'] for url in urls if url.a is not None]

def get_image_url(bs, to_small=False):
	image = bs.find('div', attrs={'class':'lot'}).img['src']
	if image is None:
		raise TypeError('bs unable to grab image url')
	if to_small:
		image = re.sub(r'big', 'small', image)
	#print(image)
	return image

# def get_image_url(bs):
# 	try:
# 		image = bs.find('div', attrs={'class':'lot'}).img['src']
# 	except TypeError as err:
# 		print('bs unable to grab image')
# 		raise
# 	#print(image)
# 	return image

def get_auction_type(bs):
	text = bs.find('h2', attrs={'id':'coin_hCont'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	try:
		result = re.search(r'(The Coin Shop|Electronic Auction|Feature Auction|Affiliated Auction)', text)
		if result is not None:
			auction = str(result.group())
			return auction
		raise TypeError()
	except:
		exit('unable to find auction type')

def get_auction_ID(bs):
	text = bs.find('td', attrs={'id':'coin_coinInfo'}).text
	text = text.replace(u'\xa0', u' ')
	#print(text)
	auc = get_auction_type(bs)
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

def get_auction_lot(bs):
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

def get_sale_estimate(bs):
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

def get_sale_price(bs):
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

def get_lot_header(bs):
	header = bs.find('h1', attrs={'id':'coin_hHead'})
	if header is not None:
		#print(header)
		try:
			return header.text
		except TypeError as err:
			print('bs unable to grab lot header')
			raise
	return None

def get_lot_notes(bs):
	notes = bs.find('p', attrs={'id':'coin_pNotes'})
	if notes is not None:
		#print(notes)
		try:
			if notes.text == ' ':
				return None
			else:
				return notes.text
		except TypeError as err:
			print('bs unable to grab lot notes')
			raise
	return None

def get_lot_description(bs):
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

	# augustus, denarius, eA
	#html = get_html('https://cngcoins.com/Search.aspx?PAGE_NUM=200&PAGE=1&TABS_TYPE=2&CONTAINER_TYPE_ID=2&IS_ADVANCED=1&ITEM_DESC=Augustus.+27+BC-AD+14.+AR+Denarius&ITEM_IS_SOLD=1&SEARCH_IN_CONTAINER_TYPE_ID_1=1&SEARCH_IN_CONTAINER_TYPE_ID_3=1&SEARCH_IN_CONTAINER_TYPE_ID_2=1&SEARCH_IN_CONTAINER_TYPE_ID_4=1#')
	#urls = get_coin_urls(html.text)

	# augustus, denarius, pA
	#html = open('/Users/cwillis/GitHub/RomanCoinData/data_raw/CNG/html/Augustus_AR_PA1.html', 'r')
	#print(html)
	#urls = get_coin_urls(html)

	html = open(sys.argv[1])
	#print(html)
	urls = get_coin_urls(html)


	# # some good examples to get right
	# import cv2
	# import matplotlib.pyplot as plt	
	# urls = ['https://cngcoins.com/Coin.aspx?CoinID=376445', 
	# 		'https://cngcoins.com/Coin.aspx?CoinID=372920', 
	# 		'https://cngcoins.com/Coin.aspx?CoinID=387264']
	# for idx, url in enumerate(urls):
	# 	webpage = requests.get(url, headers=headers)
	# 	bs = BeautifulSoup(webpage.text, 'html.parser')
	# 	x = get_lot_header(bs)
	# 	print(x)
	# 	y = get_lot_notes(bs)
	# 	print(y)
	# 	z = get_image_url(bs, to_small=True)
	# 	print(z)
	# 	arr_img, (img_row, img_col, img_chan) = url_to_array(z, flatten=True, gray=False)
	# 	print(arr_img.shape, img_row, img_col, img_chan)
	# 	#for x in arr_img:
	# 	#	print(x)
	# 	arr_img2 = arr_img.reshape(img_row, img_col, img_chan)
	# 	print(arr_img2.shape)
	# 	# show image
	# 	cv2.imshow("resized", arr_img2)
	# 	cv2.waitKey(0)
	# 	# convert PIL BGR image to open cv RGB standard
	# 	im = cv2.cvtColor(arr_img2, cv2.COLOR_BGR2RGB)
	# 	cv2.imshow("resized", im)
	# 	cv2.waitKey(0)
	# quit()

	# build CSV output
	print('URL,Image,Rows,Columns,Channels,Auction Type,Auction ID,Auction Lot,Estimate,Sold,Header,Notes,Description,Nonstandard Lot')
	for idx, url in enumerate(urls):
		
		if idx>3: continue
		#print(idx, url)

		#html = urlopen(url)
		webpage = requests.get(url, headers=headers)
		bs = BeautifulSoup(webpage.text, 'html.parser')
		#print(bs)

		# grab the url of the coin image
		img_url = get_image_url(bs, to_small=True)
		#print(' Image URL: {}'.format(img_url))

		# create an image from the url
		img = url_to_image(img_url, gray=False)
		#print(' Image: {}'.format(img))

		# create a flattened array from the image
		img_arr, (img_row, img_col, img_chan) = image_to_array(img, flatten=True)
		#print(' Image Array: {}'.format(img_arr))

		# create a string from the flattened array
		img_str = array_to_string(img_arr)
		#print(' Image Str: {}'.format(img_str))

		# grab auction type (CS, EA, PS)
		auction_type = get_auction_type(bs)
		#print(' Auction Type: {}'.format(auction_type))

		# grab auction id (Triton, CNG, etc.)
		auction_id = get_auction_ID(bs)
		#print(' Auction ID: {}'.format(auction_id))

		# grab lot number
		acution_lot = get_auction_lot(bs)
		#print(' Lot Number: {}'.format(lot))

		# grab the sale estimate
		sale_estimate = get_sale_estimate(bs)
		#print(' Sale estimate: {}'.format(estimate))

		# grab the sale price
		sale_price = get_sale_price(bs)
		#print(' Sale price: {}'.format(price))

		# grab the lot header if present
		header = get_lot_header(bs)
		#print(' Lot Header: {}'.format(header))

		# grab the lot notes if present
		notes = get_lot_notes(bs)
		#print(' Lot Notes: {}'.format(notes))

		# grab the lot description
		description = get_lot_description(bs)
		#print(' Description: {}'.format(description))

		# identify nonstandard lots (i.e. those with a stop word)
		nonstandard_lot = is_nonstandard_lot(description)
		#print(' Nonstandard lot: {}'.format(nonstandard_lot))

		print('{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(img_url, \
			img_str, img_row, img_col, img_chan, auction_type, \
			auction_id, acution_lot, sale_estimate, sale_price, header, \
			notes, description, nonstandard_lot))
