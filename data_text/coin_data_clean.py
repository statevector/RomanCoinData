import re
import sys
import os
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)

def get_positions(x, character):
	return [pos for (pos, char) in enumerate(x) if char == character]

def list_csv_files(path):
	return [path+'/'+f for f in os.listdir(path) if f.split('.')[-1]=='csv']

# convert all dash types (hyphen, en-, em-, minus, others?) to a
# common dash to simplify analysis later
# https://en.wikipedia.org/wiki/Dash#Similar_Unicode_characters
def format_dashes(text):
	#text = text.encode('utf-8')
	text = text.replace(u'\xa0', u' ')   # ???
	text = text.replace(u'\u2010', u'-') # hyphen
	text = text.replace(u'\u2012', u'-') # figure dash
	text = text.replace(u'\u2013', u'-') # en-dash
	text = text.replace(u'\u2014', u'-') # em-dash
	text = text.replace(u'\u2015', u'-') # horizonal bar
	text = text.replace(u'\u002D', u'-') # hyphen-minus
	text = text.replace(u'\u00AD', u'-') # soft hyphen
	text = text.replace(u'\u2212', u'-') # minus sign
	return text

# identify textual inconsistencies
def format_spaces(text, verbose=False):
	# double space
	result = re.search(r'  ', text)
	if result is not None:
		if(verbose): print('double space:\n{}'.format(text))
		text = re.sub(r'  ', r' ', text)
		if(verbose): print('double space:\n{}'.format(text))
	# space followed by period
	result = re.search(r' \.', text)
	if result is not None:
		if(verbose): print('space followed by period:\n{}'.format(text))
		text = re.sub(r' \.', r'.', text)
		if(verbose): print('space followed by period:\n{}'.format(text))
	return text

def standardize_measurements(result):
	# consolidate measurement variations
	result = result.replace('  g', ' g')
	result = result.replace(' g', 'g')
	# variation 'gm' occasionally present
	result = result.replace('  gm', ' gm')
	result = result.replace(' gm', 'gm')
	result = result.replace('gm', 'g')
	# remove initial spaces
	result = result.replace(' mm', 'mm')
	result = result.replace(' h', 'h')
	return result

def strip_measurements(result, words):
	result = result[1:-1] # remove '(' and ')'
	result = result.split(' ')
	result_clean = []
	for r, w in zip(result, words):
		# this is ugly but helps with later parsing
		rr = r.replace('.', '*')
		result_clean.append(rr +' '+w+'.')
	result_clean = ' '.join(result_clean)
	return result_clean

def format_measurements(text):
	try:
		isClean = False
		# case 1: complete string
		regex = r'\(.+mm.+g.+h\)'
		result = re.search(regex, text)
		if result is not None:
			# format diameter, weight, orientation info
			result = standardize_measurements(result.group(0))
			words = ['Diameter', 'Weight', 'Hour']
			result = strip_measurements(result, words)
			result = result + ' Measurement Case 1'
			# substitute this reformatted info into the original text
			text = re.sub(regex, result, text)
			isClean = True
		# case 2: missing 'h' only
		regex = r'\(.+mm.+g\)'
		result = re.search(regex, text)
		if result is not None:
			# format diameter, weight, orientation info
			result = standardize_measurements(result.group(0))
			words = ['Diameter', 'Weight']
			result = regroup_measurements(result, words)
			result = result + ' Unlisted Hour.'
			result = result + ' Measurement Case 2'
			# substitute this reformatted info into the original text
			text = re.sub(regex, result, text)
			isClean = True
		# case 3: missing 'g' and 'h' (no end space)
		regex = r'\(.+mm\)'
		result = re.search(regex, text)
		if result is not None:
			# format diameter, weight, orientation info
			result = standardize_measurements(result.group(0))
			words = ['Diameter']
			result = regroup_measurements(result, words)
			result = result + ' Unlisted Weight. Unlisted Hour.'
			result = result + ' Measurement Case 3'
			# substitute this reformatted info into the original text
			text = re.sub(regex, result, text)
			isClean = True
		# case 4: missing 'mm' only
		regex = r'\(.+g.+h\)'
		result = re.search(regex, text)
		if result is not None:
			# format diameter, weight, orientation info
			result = standardize_measurements(result.group(0))
			words = ['Weight', 'Hour']
			result = regroup_measurements(result, words)
			result = ' Unlisted Diameter' + result
			result = result + ' Measurement Case 4'
			# substitute this reformatted info into the original text
			text = re.sub(regex, result, text)
			isClean = True
		# case 5: missing 'g' and 'h' (with ending space)
		regex = r'\(.+mm \)'
		result = re.search(regex, text)
		if result is not None:
			result = result.group(0)
			result = result.replace('mm ', 'mm')
			# format diameter, weight, orientation info
			result = standardize_measurements(result)
			words = ['Diameter']
			result = regroup_measurements(result, words)
			result = result + ' Unlisted Weight. Unlisted Hour.'
			result = result + ' Measurement Case 5'
			# substitute this reformatted info into the original text
			text = re.sub(regex, result, text)
			isClean = True
		if not isClean:
			raise TypeError()
		# find and replace 'AR Denarius' with 'AR Denarius.'
		result = re.search(r'AR Denarius', text)
		text = re.sub(r'AR Denarius', 'AR Denarius.', text)
		print(text)
		return text
	except:
		exit('unable to format measurements for {}'.format(text))

# consolidate similar grades;
# e.g. 'Near EF', 'Good VF', 'Nice VF', etc.
def format_grade(text):
	# ...
	return text

def format_mint(text):
	# account for moneyer situations
	text = re.sub(r'mint;', 'mint.', text)
	# Rome
	text = re.sub(r'Rome mint;', 'Rome mint.', text)
	#text = re.sub(r' Rome mint\.', 'Rome mint.', text) # Augustus EA4
	# Emerita
	text = re.sub(r'Emerita mint\.', 
		'Emerita (Mérida) mint.', text)
	#text = re.sub(r'Emerita mint;', 
	#	'Emerita (Mérida) mint;', text)	# delete after check.
	text = re.sub(r'Spanish mint - Emerita', 
		'Emerita (Mérida) mint', text) # Augustus EA4
	# Colonia Patricia
	text = re.sub(r'Spanish mint possibly Colonia Patricia', 
		'Spanish mint (Colonia Patricia?)', text) # Augustus EA1
	text = re.sub(r'Uncertain Spanish mint \(Colonia Patricia\?\)', 
		'Spanish mint (Colonia Patricia?)', text)
	text = re.sub(r'Colonia Patricia\(\?\) mint', 
		'Spanish mint (Colonia Patricia?)', text)
	text = re.sub(r'Colonia Patricia mint', 
		'Spanish mint (Colonia Patricia)', text) # Augustus EA4
	# Colonia Caesaraugusta
	text = re.sub(r'Uncertain Spanish mint \(Colonia Caesaraugusta\?\)', 
		'Spanish mint (Colonia Caesaraugusta?)', text)
	text = re.sub(r'Spanish mint \(Caesaraugusta\?\)', 
		'Spanish mint (Colonia Caesaraugusta?)', text) # Augustus EA4
	text = re.sub(r'Caesaraugusta mint', 
		'Spanish mint (Colonia Caesaraugusta)', text) # Augustus EA4
	text = re.sub(r'Spanish mint \(Colonia Caesaraugusta\?\)', 
		'Spanish mint (Colonia Caesaraugusta?)', text) # Augustus EA4
	text = re.sub(r'Spanish mint \(Caesaraugusta\?\)', 
		'Spanish mint (Colonia Caesaraugusta?)', text) # Augustus EA4
	# Tarraco
	text = re.sub(r'Spanish mint - Tarraco', 
		'Tarraco mint', text) # Augustus EA4
	# Lugdunum (Lyon) mint
	text = re.sub(r'Lugdunum \(Lyons\) mint', 
		'Lugdunum (Lyon) mint', text) # Augustus EA4
	# Spain
	text = re.sub(r'Uncertain Spanish mint', 
		'Spanish mint', text) # Augustus EA4
	# ...
	return text

# check for existence of 'moneyer' keyword
# search between mint and struck
def impute_moneyer(text):
	#
	return text

def format_abbreviations(text):
	text = re.sub(r'var\.', 'variation', text)
	text = re.sub(r'cf\.', 'confer', text)
	text = re.sub(r'Cf\.', 'Confer', text)
	# include space to avoid those obs. that end in 'edge chip.'
	text = re.sub(r'p\. ', 'page ', text) 
	text = re.sub(r'rev\. ', 'reverse ', text)
	text = re.sub(r'obv\. ', 'obverse ', text)
	text = re.sub(r'corr\. ', 'correction ', text)
	return text

# check for existence of 'Stuck' keyword and append
# after the 'mint' field if not present
def impute_strike(text, verbose=False):
	result = re.search(r'Struck ', text)
	if result is None:
		if(verbose): print('before strike: {}'.format(text))
		text = re.sub(r'mint.', 'mint. Struck unlisted.', text)
		if(verbose): print('after strike: {}'.format(text))
	return text

# check for existence of 'mint' keyword and append
# before the 'Stuck' field if not present
def impute_mint(text, verbose=False):
	result = re.search(r'mint', text)
	if result is None:
		if(verbose): print('before mint: {}'.format(text))
		idx = -1
		segments = text.split('.')
		for index, segment in enumerate(segments):
			if 'Struck' in segment:
				# get the index following where
				# 'Struck' was found
				idx = index + 1
		# remember the space
		segments.insert(idx, ' Unlisted mint')
		text = '.'.join(segments)
		if(verbose): print('after mint: {}'.format(text))
	return text


if __name__ == '__main__':

	#files = list_csv_files("/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/")
	#print(files)

	file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA1.csv'
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA2.csv'
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA3.csv'
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA4.csv'
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_PA1.csv'
	
	df = pd.read_csv(file)
	print(df.info())

	# remove entries tagged as non-standard
	df = df[~df['Nonstandard Lot']]
	print(df.info())
	
	# do some light cleaning and standardization of the 'Description' field
	# for subsequent feature engineering

	df['Description'] = df['Description'].apply(lambda x: format_dashes(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_spaces(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	#print(df.info())

	#df['Description'] = df['Description'].apply(lambda x: format_grade(x))
	##print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_mint(x))
	#print(df.info())

	#df['Description'] = df['Description'].apply(lambda x: format_moneyer(x))
	##print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_strike(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_mint(x))
	#print(df.info())

	print(df)

	# write output	
	directory = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_cleaned'
	output = file.split('/')[-1].split('.')[0]+'_cleaned.csv'
	df.to_csv(directory+'/'+output, index=False)

