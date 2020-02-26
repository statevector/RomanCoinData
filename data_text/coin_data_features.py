# coding: utf-8

import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)

emperors = ['Augustus', 'Tiberius', 'Nero', 'Galba', 'Otho', 
			'Vespasian', 'Domitian', 'Trajan', 'Hadrian', 
			'Antoninus Pius', 'Marcus Aurelius']

denominations = ['Aureus', 'Denarius', 'Sestertius']

# order matters for search!
grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 'Nice VF', 
		  'Good VF', 'Near VF', 'VF', 'Good Fine', 'Near Fine', 'Fine']

def list_csv_files(path):
	return [path+'/'+f for f in os.listdir(path) 
		if f.split('.')[-1]=='csv']

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

def get_diameter(text):
	for segment in text.split('.'):
		if 'Diameter' in segment:
			return segment
	return None

def get_weight(text):
	for segment in text.split('.'):
		if 'Weight' in segment:
			return segment
	return text

def get_hour(text):
	for segment in text.split('.'):
		if 'Hour' in segment:
			return segment
	return text

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

# Assume for now longest segment between 'Struck' 
# and 'RIC' fields contains the coin imagery
def get_imagery(text, verbose=True):
	lower = text.find('Struck')
	upper = text.find('RIC')
	if lower>0 and upper>0:
		text = text[lower:upper]
	else:
		return None
	# identify longest segment
	segments = text.split('.')
	length = 0
	imagery = None
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
	text = text.replace('darkly', 'dark')
	text = text.replace('portraiture', 'portrait')
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
	text = text.replace('banker’s', 'banker') # standardize apostrophes?
	text = text.replace('bankers’', 'banker')
	text = text.replace('cleaned', 'clean')
	text = text.replace('cleaning', 'clean')
	text = text.replace('off center', 'off-center')
	return text

# condidate descriptions where necessary
def consolidate_descriptors(text):
	text = text.replace('scarse', 'rare')
	# maybe combine these?
	#'golden' in text or 'rose' in text or 'blue' in text or 'rainbow' in text:
	return text

def get_comments(text):
	# isolate the comments section. We know it
	# occurs AFTER the RIC number.
	comments = None
	#print('pre Isolate RIC:\n {}'.format(text))
	lower = text.find('RIC') # add ACIP; RSC as backups
	if lower>0:
		comments = text[lower:]
	else:
		quit('Error: RIC not identified')
		return None
	#print('post Isolate RIC:\n {}'.format(comments))
	# remove RIC clause
	comments = comments.split('.')
	comments = comments[1:] 
	comments = ' '.join(comments)
	#print('post Remvove RIC:\n {}'.format(comments))
	# remove grade if present
	for grade in grades:
		if grade in comments:
			comments = comments.replace(grade, '')
	#print('post Remvove Grade:\n {}'.format(comments))
	# standardize text
	comments = stem_comments(comments)
	#print('post Standardize:\n {}'.format(comments))
	return comments

if __name__ == '__main__':

	#files = list_csv_files("/Users/cwillis/GitHub/RomanCoinData/data_text/output/")
	#print(files)

	file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned/Augustus_AR_EA1.csv' # 193/193
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned/Augustus_AR_EA2.csv' # 191/192, NGC encapsulation
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned/Augustus_AR_EA3.csv' # 193/195, checks out (each null missing h)
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned/Augustus_AR_EA4.csv' # checked. good.
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned/Augustus_AR_PA1.csv' # 119/119, comments!
	
	df = pd.read_csv(file)
	print(df.info())

	# remove entries tagged as non-standard
	df = df[~df['Nonstandard Lot']]
	print(df.info())
	
	df['Emperor'] = df['Description'].apply(lambda x: get_emperor(x))
	print(df.info())

	df['Reign'] = df['Description'].apply(lambda x: get_reign(x))
	print(df.info())

	df['Denomination'] = df['Description'].apply(lambda x: get_denomination(x))
	print(df.info())

	df['Diameter'] = df['Description'].apply(lambda x: get_diameter(x))
	print(df.info())

	df['Weight'] = df['Description'].apply(lambda x: get_weight(x))
	print(df.info())

	df['Hour'] = df['Description'].apply(lambda x: get_hour(x))
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

	# data now cleaned, print rows CSV
	#df.to_csv(file.split[-1]+'_cleaned.csv')

