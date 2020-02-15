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
			  'Brockage', 'brockage', 'Official Dies', 'Æ', 'forgery', 
			  'bezel']

denominations = ['Aureus', 'Denarius', 'Sestertius']

grades = ['FDC', 'Superb EF', 'Choice EF', 'EF', 'Near EF', 'Nice VF', 
		  'Good VF', 'VF', 'Near VF', 'Good Fine', 'Fine']

mints = ['Lyon', 'Rome'] # finish this
#Spanish mint (Colonia Caesaraugusta)


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

def get_denomination(text):
	for denomination in denominations:
		if denomination in text:
			return denomination
	return None

def get_grade(text):
	for grade in grades:
		if grade in text:
			return grade
	return None

# return a pandas series to be automatically inserted into the dataframe
# https://stackoverflow.com/a/23690329/11656635
def get_size_weight_hour(text):
	result = re.search(r'\(\d+.\w+\W\s+\d+.\w+\s+\w+\W\s+\d+.\)', text)
	if result is not None:
		result = result.group(0)
		result = result[1:-1] # remove '(' and ')'
		return pd.Series(result.split(':'))
	return pd.Series([None, None, None])

#(18mm, 3.62 g, 6h)
	# result = re.search(r'\((\d+[.,]\d+|\d+)mm,\s+(\d+[\.,]\d+|\d+)\s\w+,\s+\d+h\)', text) # with 'mm', 'g/gm', 'h'
	# if result is not None:
	# 	string = result.group(0)
	# 	string = string[1:-1] # remove '(' and ')'
	# 	return tuple(string.split(','))
	# result = re.search(r'\((\d+[\.,]\d+|\d+)\s+\w+,\s+\d+h\)', text) # with 'g/gm', 'h'
	# if result is not None:
	# 	string = result.group(0)
	# 	string = string[1:-1] # remove '(' and ')'
	# 	if string[1] == ',':
	# 		string = string.replace(',','.',1) # for a,bc instead of a.bc
	# 	return (0,) + tuple(string.split(','))
	# result = re.search(r'\((\d+[\.,]\d+|\d+)\s+\w+(, |)\)', text) # with 'g/gm' only, sometimes '(x.yz gm, )'
	# if result is not None:
	# 	string = result.group(0)
	# 	string = string[1:-1] # remove '(' and ')'
	# 	return tuple([0, string, 0])
	#return None, None, None

def get_mint(text):
	for segment in text.split('.'):
		for subsegment in segment.split(';'):
			if 'mint' in subsegment:
				return subsegment
	return None






# match pattern 'RIC I/II/III 0-9/00-99/000-999'
# em-dash (—) is one of the two types of dashes used in punctuation, the other being the en-dash (–).
def get_RIC(text):
	result = re.search(r'RIC (IV|III|II|I) ([0-9][0-9][0-9]|[0-9][0-9]|[0-9])', text)
	if result is not None:
		return result.group(0)
	result = re.search(r'RIC (IV|III|II|I) (—|–|-)', text) # what is the - notation?
	if result is not None:
		return result.group(0)
	result = re.search(r'RIC (—|–|-)', text) # only the dash?
	if result is not None:
		return result.group(0)
	result = re.search(r'RIC \d+', text) # missing the numerals
	if result is not None:
		return result.group(0)
	result = re.search(r'RIC', text) # missing RIC completely
	if result is None:
		return 'NA'
	return None


########################################

def is_travel_series(text):
	if "Travel series" in text:
		return True
	return False
	
def get_coin_properties(text):
	props = [False]*27 # number of properties we're checking
	if 'broad flan' in text: 
		props[0] = True
	if 'luster' in text or 'lustre' in text or 'lustrous' in text: 
		props[1] = True
	if 'tone' in text or 'toned' in text or 'toning' in text:
		props[2] = True
	if 'attractively' in text or 'golden' in text or 'rose' in text or 'blue' in text or 'iridescent' in text or 'iridescence' in text or 'rainbow' in text:
		props[3] = True
	if 'cabinet tone' in text or 'cabinet toning' in text:
		props[4] = True
	if 'portrait' in text or 'portraiture' in text:
		props[5] = True
	if 'rare' in text or 'scarse' in text:
		props[6] = True
	if 'centered' in text:
		props[7] = True
	if 'off center' in text:
		props[8] = True
	if 'mark' in text or 'marks' in text:
		props[9] = True
	if 'deposits' in text:
		props[10] = True
	if 'flan crack' in text or 'flan flaw' in text:
		props[11] = True
	if 'hairlines' in text:
		props[12] = True	
	if 'die break' in text:
		props[13] = True	
	if 'surface flaws' in text:
		props[14] = True
	if 'rough' in text or 'roughness' in text:
		props[15] = True
	if 'tooled' in text or 'tooling' in text or 'smoothed' in text or 'smoothing' in text:
		props[16] = True
	if 'die rust' in text:
		props[17] = True
	if 'corrosion' in text:
		props[18] = True
	if 'porosity' in text or 'porous' in text or 'granular' in text:
		props[19] = True
	if 'scratch' in text or 'scratches' in text:
		props[20] = True
	if 'edge test' in text:
		props[21] = True
	if 'test cut on obverse' in text or 'test cut on reverse' in text:
		props[22] = True
	if 'splits' in text:
		props[23] = True
	if 'pvc residue' in text:
		props[24] = True
	if 'weak strike' in text:
		props[25] = True
	if 'edge chip' in text:
		props[26] = True
	return props

properties_list = ['broad flan', 'lusterous', 'toned', 'attractively toned', 
	'cabinet toning', 'quality portrait', 'rare', 'centered', 'off center', 
	'marks', 'deposits','flan flaw', 'hairlines', 'die break','surface flaws',
	'roughness', 'tooling', 'die rust', 'corrosion', 'porosity', 'scratches', 
	'edge test', 'surface test','edge splits', 'pvc residue', 'weak strike', 
	'edge chip']
	
########################################






if __name__ == '__main__':

	#files = list_csv_files("/Users/cwillis/GitHub/RomanCoinData/data_text/output/")
	#print(files)

	# print CSV header
	print('Auction Type,Auction ID,Lot Number,Estimate,Sale,Emperor,Denomination,Diameter,Weight,Orientation,Mint,RIC,Grade,Broad Flan,Lusterous,Toned,Attractively Toned,Cabinet Toning,Quality Portrait,Rare,Centered,Off Center,Marks,Deposits,Flan Flaw,Hairlines,Die Break,Surface Flaws,Roughness,Tooled,Die Rust,Corrosion,Porosity,Scratches,Edge Test,Surface Test,Edge Splits,PVC Residue,Weak Strike,Edge Chip')

	file = '/Users/cwillis/GitHub/RomanCoinData/data_text/Augustus_AR_EA1.csv'

	df = pd.read_csv(file)
	print(df.info())

	#df['Description'].apply(lambda x: x.lower())
	df['has_StopWord'] = df['Description'].apply(lambda x: has_stop_word(x))
	print(df.info())

	df['Emperor'] = df['Description'].apply(lambda x: get_emperor(x))
	print(df.info())

	df['Denomination'] = df['Description'].apply(lambda x: get_denomination(x))
	print(df.info())

	df[['size', 'weight', 'hour']] = df['Description'].apply(lambda x: get_size_weight_hour(x))
	print(df.info())

	df['Mint'] = df['Description'].apply(lambda x: get_mint(x))

	# 1. idea is to apply a bunch of methods against 'Description'
	# 2. pull out the relevant features (e.g. emperor, denomination, etc.)
	# 3. standardize 'Description' for TFIDF?

	print(df)

	quit()

	RIC = get_RIC(coin)
	#print(RIC)

	grade = get_grade(coin)
	#print(grade)

	# if any value is none, break
	inputs = [auction_type, auction_ID, lot, estimate, price, emperor, denomination, RIC, grade]
	if None in inputs:
		#print(' --> None Found')
		print("FAILURE")
		print('div text:', lot_desc)
		print('chris inputs:', inputs)
		print('A ID:',auction_ID)
		print('lot:', lot)
		print('estimate:', estimate)
		print(idx, link.a['href'])

	# get coin properties

	coin_properties = get_coin_properties(coin)

	#for prop, has_prop in zip(properties_list, coin_properties):
	#	print('{}: {}'.format(prop, has_prop))


	# print CSV rows
	print('{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
		auction_type, auction_ID, lot, estimate, price, emperor, denomination, size, weight, orientation, mint, RIC, grade), end='')
	for has_prop in coin_properties:
		print(',{}'.format(int(has_prop)), end='')
	print(' ')



