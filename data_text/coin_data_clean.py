import re
import sys
import os
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)

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

# probably want to fold this into the format_measurements function
def clean_measurements(result):
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
	# remove final spaces
	return result

def get_positions(x, character):
	return [pos for (pos, char) in enumerate(x) if char == character]

# format size, weight, orientation information
def format_measurements(text):
	try:
		# case 1: complete string
		regex = r'\(.+mm.+g.+h\)'
		result = re.search(regex, text)
		if result is not None:
			result = result.group(0)
			result = clean_measurements(result)
			result = result[1:-1] # remove '(' and ')'
			# cleaner way to do this?
			spaces = get_positions(result, ' ')
			result = 'Diameter '+result[0:spaces[0]] +\
				'. Weight '+result[spaces[0]+1:spaces[1]] +\
				'. Hour '+result[spaces[1]+1:]  # no '.' at the end!
			print('case1: ', result)
			text = re.sub(regex, result, text)
			return text
		# case 2: missing 'h' only
		regex = r'\(.+mm.+g\)'
		result = re.search(regex, text)
		if result is not None:
			result = result.group(0)
			result = clean_measurements(result)
			print('case2: ', result)
			text = re.sub(regex, result, text)
			return text
		# case 3: missing 'g' and 'h' (no end space)
		regex = r'\(.+mm\)'
		result = re.search(regex, text)
		if result is not None:
			result = result.group(0)
			result = clean_measurements(result)
			print('case3: ', result)
			text = re.sub(regex, result, text)
			return text
		# case 4: missing 'mm' only
		regex = r'\(.+g.+h\)'
		result = re.search(regex, text)
		if result is not None:
			result = result.group(0)
			result = clean_measurements(result)
			print('case4: ', result)			
			text = re.sub(regex, result, text)
			return text
		# case 5: missing 'g' and 'h' (with ending space)
		# regex = r'\(.+mm \)'
		# result = re.search(regex, text)
		# if result is not None:
		# 	result = result.group(0)
		# 	result = result.replace('mm ', 'mm')
		# 	text = re.sub(regex, result, text)
		# 	print(text)
		# 	return text
		# case 6, 7, 8, ...
		raise TypeError()
	except:
		exit('unable to format measurements for {}'.format(text))

# consolidate similar grades;
# e.g. 'Near EF', 'Good VF', 'Nice VF', etc.
def format_grade(text):
	# ...
	return text

def format_mint(text):
	# Rome
	text = re.sub(r'Rome mint;', 'Rome mint.', text)
	#text = re.sub(r' Rome mint\.', 'Rome mint.', text) # Augustus EA4
	# Emerita
	text = re.sub(r'Emerita mint\.', 
		'Emerita (Mérida) mint.', text)
	text = re.sub(r'Emerita mint;', 
		'Emerita (Mérida) mint;', text)
	text = re.sub(r'Spanish mint - Emerita', 
		'Emerita (Mérida) mint', text) # Augustus EA4
	# Colonia Patricia
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







def get_measurements(text):
	# see https://regexr.com/4ucqs for example
	try:
		# case 1: complete string
		result = re.search(r'\(.+mm.+g.+h\)', text)
		if result is not None:
			result = result.group(0)
			result = result[1:-1] # remove '(' and ')'
			#print(result)
			size, weight, hour = result.split(' ')
			return pd.Series([size, weight, hour])
		# case 2: missing 'h' only
		result = re.search(r'\(.+mm.+g\)', text)
		if result is not None:
			result = result.group(0)
			result = result[1:-1] # remove '(' and ')'
			#print(result)
			size, weight = result.split(' ')
			hour = None
			#print("warning hour is none")
			return pd.Series([size, weight, hour])
		# case 3: missing 'g' and 'h' (no space at end)
		result = re.search(r'\(.+mm\)', text)
		if result is not None:
			result = result.group(0)
			result = result[1:-1] # remove '(' and ')'
			#print(result)
			size = result.split(' ')
			weight = None
			hour = None
			return pd.Series([size, weight, hour])
		# case 4: missing 'mm' only
		result = re.search(r'\(.+g.+h\)', text)
		if result is not None:
			result = result.group(0)
			result = result[1:-1] # remove '(' and ')'
			#print(result)
			size = None
			weight, hour = result.split(' ')
			return pd.Series([size, weight, hour])
		# case 5: missing 'g' and 'h' (with space at end)
		# result = re.search(r'\(.+mm \)', text)
		# if result is not None:
		# 	result = result.group(0)
		# 	result = result[1:-1] # remove '(' and ')'
		# 	print(result)
		# 	size = result.split(' ')
		# 	print(size)
		# 	quit()
		# 	weight = None
		# 	hour = None
		# 	return pd.Series([size, weight, hour])
		raise TypeError()
	except:
		exit('unable to extract measurements for {}'.format(text))







if __name__ == '__main__':

	#files = list_csv_files("/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/")
	#print(files)

	file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA1.csv' # 193/193
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA2.csv' # 191/192, NGC encapsulation
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA3.csv' # 193/195, checks out (each null missing h)
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_EA4.csv' # checked. good.
	#file = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Augustus_AR_PA1.csv' # 119/119, comments!
	
	df = pd.read_csv(file)
	print(df.info())

	# remove entries tagged as non-standard
	df = df[~df['Nonstandard Lot']]
	print(df.info())
	
	# do some light cleaning and standardization of the 'Description' field
	df['Description'] = df['Description'].apply(lambda x: format_dashes(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_spaces(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	#print(df.info())

	#df['Description'] = df['Description'].apply(lambda x: format_grade(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_mint(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_strike(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_mint(x))
	#print(df.info())

	print(df)




