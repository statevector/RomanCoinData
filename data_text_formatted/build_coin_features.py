# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import pandas as pd

emperors = ['Augustus', 'Tiberius', 'Nero', 'Galba', 'Otho', 
			'Vespasian', 'Domitian', 'Trajan', 'Hadrian', 
			'Antoninus Pius', 'Marcus Aurelius']

stop_words = ['CHF', 'Lot of', 'Quinarius', 'Fourrée', 'fourrée', 
			  'Brockage', 'brockage', 'Official Dies', 'Æ', 'Forgery', 
			  'forgery', 'bezel', 'electrotype', 'MIXED']

denominations = ['Aureus', 'Denarius', 'Sestertius']

# order matters for search!
grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 'Nice VF', 
		  'Good VF', 'Near VF', 'VF', 'Good Fine', 'Near Fine', 'Fine']

# properties = ['broad flan', 'lusterous', 'toned', 'attractively toned', 
# 	'cabinet toning', 'quality portrait', 'rare', 'centered', 'off center', 
# 	'marks', 'deposits','flan flaw', 'flan crack', 'hairlines', 'die break','surface flaws',
# 	'roughness', 'tooling', 'die rust', 'corrosion', 'porosity', 'scratches', 
# 	'edge test', 'surface test','edge splits', 'pvc residue', 'weak strike', 
# 	'edge chip']

def list_csv_files(path):
	return [path+'/'+f for f in os.listdir(path) 
		if f.split('.')[-1]=='csv']

def has_stop_word(text):
	return any(word in text for word in stop_words)

def get_emperor(text):
	for emperor in emperors:
		if emperor in text:
			return emperor
	return None

def get_reign(text):
	for segment in text.split('.'):
		if 'BC-AD' in segment:
			return segment
	return None

def get_denomination(text):
	for denomination in denominations:
		if denomination in text:
			return denomination
	return None

# https://stackoverflow.com/a/23690329/11656635
def get_measurements(text):
	#print('I am here')
	#print(text)
	try:
		result = re.search(r'\(.+h\)', text)
		#print('result: ', result)
		#print('is none: ', result is None)
		if result is not None:
			result = result.group(0)
			#print(result)
			result = result[1:-1] # remove '(' and ')'
			#print(result)
			result = result.split(' ')
			#print(result)
			return result
		else:
			raise TypeError()
	except:
		exit('unable to extract measurements for {}'.format(text))	

def get_mint(text):
	for segment in text.split('.'):
		if 'mint' in segment:
			return segment
	return None

def get_strike_date(text):
	for segment in text.split('.'):
		if 'Struck' in segment:
				return segment
	return None

def get_RIC_number(text):
	# match pattern 'RIC I/II/III 0-9/00-99/000-999'
	result = re.search(r'RIC (IV|III|II|I) ([0-9][0-9][0-9]|[0-9][0-9]|[0-9])', text)
	if result is not None:
		return result.group(0)
	# match pattern 'RIC I/II/III -' (what is the - notation?)
	result = re.search(r'RIC (IV|III|II|I) -', text) 
	if result is not None:
		return result.group(0)
	# match pattern 'RIC -' (only the dash?)
	result = re.search(r'RIC -', text) 
	if result is not None:
		return result.group(0)
	# match pattern 'RIC 0-999...' (only the numerals?)
	result = re.search(r'RIC \d+', text) 
	if result is not None:
		return result.group(0)
	# match pattern 'RIC' (missing dash and numerals?)
	result = re.search(r'RIC', text) 
	if result is not None:
		return result.group(0)
	return None

# crudely assume the longest segment contains
# the coin imagery for this first iteration
def get_imagery(text):
	# isolate the description 
	lower = text.find('mint')
	upper = text.find('RIC')
	if lower>0 and upper>0:
		text = text[lower:upper]
	else:
		return None
	print(text)
	segments = text.split('.')
	length = 0
	imagery = ""
	for segment in segments:
		if len(segment)>length:
			imagery = segment
			length = len(segment)
	return imagery

def get_grade(text):
	segments = text.split('.')
	# iterate in reverse since we know the grade 
	# information resides in the last sentence;
	# we dont want false positives (e.g. 'fine portrait')
	for segment in reversed(segments):
		for grade in grades:
			if grade in segment:
				return grade
	return None

# do manual stemming/lemmatization for now
def stem_comments(text):
	text = text.lower()
	text = text.replace('lustre', 'lust')
	text = text.replace('luster', 'lust')
	text = text.replace('lustrous', 'lust')
	text = text.replace('toned', 'tone')
	text = text.replace('toning', 'tone')
	text = text.replace('attractively', 'attractive')
	text = text.replace('iridescence', 'iridescent')
	text = text.replace('portraiture', 'portrait')
	text = text.replace('scarse', 'rare')
	text = text.replace('centered', 'center')
	# but not marks --> mark or scratches --> scratch. probably info in the plural form.
	text = text.replace('roughness', 'rough')
	text = text.replace('tooled', 'tool')
	text = text.replace('tooling', 'tool')
	text = text.replace('smoothed', 'smooth')
	text = text.replace('smoothing', 'smooth')
	text = text.replace('corroded', 'corrosion')
	text = text.replace('porosity', 'porous')
	text = text.replace('granularity', 'granular')
	text = text.replace('pitting', 'pits')
	text = text.replace('pitted', 'pits')
	# 'cut' is implicit here; want to match with e.g. 'test cut on reverse/obverse'
	text = text.replace('edge test', 'edge test cut') 
	text = text.replace('surface test', 'surface test cut')
	text = text.replace('struck', 'strike')

	text = text.replace('banker’s', 'banker') # unicode encoding?
	text = text.replace('bankers’', 'banker')

	# maybe combine these?
	#'golden' in text or 'rose' in text or 'blue' in text or 'rainbow' in text:
	return text

def get_comments(text):
	# isolate the comments section. We know it
	# occurs after the RIC number is presented.
	comments = ""
	lower = text.find('RIC') # add ACIP; RSC as backups
	if lower>0:
		comments = text[lower:]
	else:
		return None
	print('post Isolate RIC:\n {}'.format(comments))
	# remove RIC clause
	comments = comments.split('.')
	comments = comments[1:] 
	comments = ' '.join(comments)
	print('post Remvove RIC:\n {}'.format(comments))
	# remove grade
	for grade in grades:
		if grade in comments:
			comments = comments.replace(grade, '')
	print('post Remvove Grade:\n {}'.format(comments))
	# standardize text
	comments = stem_comments(comments)
	print('post Standardize:\n {}'.format(comments))
	return comments


# def is_travel_series(text):
# 	if "Travel series" in text:
# 		return True
# 	return False








if __name__ == '__main__':

	#files = list_csv_files("/Users/cwillis/GitHub/RomanCoinData/data_text/output/")
	#print(files)

	file = '/Users/cwillis/GitHub/RomanCoinData/data_text/Augustus_AR_EA1.csv'
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/test.csv'

	df = pd.read_csv(file)
	print(df.info())

	df['StopWord'] = df['Description'].apply(lambda x: has_stop_word(x))
	print(df.info())

	df['Emperor'] = df['Description'].apply(lambda x: get_emperor(x))
	print(df.info())

	df['Reign'] = df['Description'].apply(lambda x: get_reign(x))
	print(df.info())

	df['Denomination'] = df['Description'].apply(lambda x: get_denomination(x))
	print(df.info())

	# what is going on here...
	df['Size'], df['Weight'], df['Hour'] = df['Description'].apply(lambda x: get_measurements(x))[0]
	print(df.info())

	df['Mint'] = df['Description'].apply(lambda x: get_mint(x))
	print(df.info())

	#df['Moneyer'] = df['Description'].apply(lambda x: get_moneyer(x))
	#print(df.info())
 	#mescinius rufus: moneyer

	df['Struck'] = df['Description'].apply(lambda x: get_strike_date(x))
	print(df.info())

	df['Imagery'] = df['Description'].apply(lambda x: get_imagery(x))
	print(df.info())

	df['RIC'] = df['Description'].apply(lambda x: get_RIC_number(x))
	print(df.info())

	#df['RIC_Length'].apply(lambda x: len(x) if x is not None else x)
	# print(df.info())

	df['Grade'] = df['Description'].apply(lambda x: get_grade(x))
	print(df.info())

	df['Comments'] = df['Description'].apply(lambda x: get_comments(x))
	print(df.info())

	print(df)

	# finally remove the 'Description' column?
	# df.drop(['Description'], inplace=True)

	# 1. idea is to apply a bunch of methods against 'Description'
	# 2. pull out the relevant features (e.g. emperor, denomination, etc.)
	# 3. standardize 'Description' for TFIDF?

	# check for None results!!!
	# -->

	# # print CSV rows
	# print('{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
	# 	auction_type, auction_ID, lot, estimate, price, emperor, \
	# denomination, size, weight, orientation, mint, RIC, grade), end='')
	# for has_prop in coin_properties:
	# 	print(',{}'.format(int(has_prop)), end='')
	# print(' ')



