import re
import sys
import os
import pandas as pd
import numpy as np

#pd.options.display.max_rows = 999
#pd.set_option('display.max_colwidth', -1)

# convert all dash types (hyphen, en-, em-, minus, others?) to a
# common dash to simplify analysis later
# https://en.wikipedia.org/wiki/Dash#Similar_Unicode_characters
# def format_dashes(text):
# 	#text = text.encode('utf-8')
# 	text = text.replace(u'\xa0', u' ')   # ???
# 	text = text.replace(u'\u2010', u'-') # hyphen
# 	text = text.replace(u'\u2012', u'-') # figure dash
# 	text = text.replace(u'\u2013', u'-') # en-dash
# 	text = text.replace(u'\u2014', u'-') # em-dash
# 	text = text.replace(u'\u2015', u'-') # horizonal bar
# 	text = text.replace(u'\u002D', u'-') # hyphen-minus
# 	text = text.replace(u'\u00AD', u'-') # soft hyphen
# 	text = text.replace(u'\u2212', u'-') # minus sign
# 	return text

# # identify textual inconsistencies
# def format_spaces(text, verbose=False):
# 	# double space
# 	result = re.search(r'  ', text)
# 	if result is not None:
# 		if(verbose): print('double space:\n{}'.format(text))
# 		text = re.sub(r'  ', r' ', text)
# 		if(verbose): print('double space:\n{}'.format(text))
# 	# space followed by period
# 	result = re.search(r' \.', text)
# 	if result is not None:
# 		if(verbose): print('space followed by period:\n{}'.format(text))
# 		text = re.sub(r' \.', r'.', text)
# 		if(verbose): print('space followed by period:\n{}'.format(text))
# 	return text

def format_abbreviations(text):
	text = re.sub(r'var\.', 'variation', text)
	text = re.sub(r'cf\.', 'confer', text)
	text = re.sub(r'Cf\.', 'Confer', text)
	# include space to avoid entries that end in e.g. 'edge chip.'
	text = re.sub(r'p\. ', 'page ', text) 
	text = re.sub(r'rev\. ', 'reverse ', text)
	text = re.sub(r'obv\. ', 'obverse ', text)
	text = re.sub(r'corr\. ', 'correction ', text)
	text = re.sub(r'pl\.', 'proof like ', text)
	# moneyer praenomen
	text = re.sub(r'L\.', 'L', text)
	text = re.sub(r'M\.', 'M', text)
	text = re.sub(r'P\.', 'P', text)
	text = re.sub(r'Q\.', 'Q', text)
	text = re.sub(r'R\.', 'R', text)
	return text

def format_measurements(text, verbose=False):
	if verbose:
		print('------------------------------------------------------')
	# prepend measurement fields for easy extraction later
	text = re.sub(r'AV Aureus', 'AV Aureus.', text)
	text = re.sub(r'AR Denarius', 'AR Denarius.', text)
	text = re.sub(r'AR Cistophorus', 'AR Cistophorus.', text)
	text = re.sub(r'Æ Sestertius', 'Æ Sestertius.', text)
	# <--- other denomination here!
	if verbose:
		print(text)
	# scan text for the following regex patterns
	patterns = [
		r'\(.+mm.+[g|gm].+h\)\.', # case 1: complete string
		r'\(.+mm.+[g|gm]\)\.',    # case 2: missing 'h' only
		r'\(.+mm\)\.',            # case 3: missing 'g' and 'h' (no end space)
		r'\(.+[g|gm].+h\)\.',     # case 4: missing 'mm' only
		r'\(.+mm \)\.',           # case 5: missing 'g' and 'h' (with ending space)
		r'\(.+[g|gm]\)\.'         # case 6: missing 'mm' and 'h'
	]
	for case, pattern in enumerate(patterns):
		if verbose:
			print('case {}'.format(case))
			print('search pattern: {}'.format(pattern))
		result = re.search(pattern, text)
		if result is not None:
			# format diameter, weight, orientation info
			result = result.group(0)
			if verbose:
				print('match: {}'.format(result))
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
			#result = result.replace('mm ', 'mm') # in the middle!
			#result = result.replace('g ', 'g') # in the middle!
			result = result.replace('h ', 'h')
			# remove brackets and final period '.'
			result = result[1:-2]
			if verbose:
				print(result)
			# replace internal '.'s to simplify later parsing
			result = result.replace('.', '@')
			if verbose:
				print(result)
			result = result.split(' ')
			if verbose:
				print(result)
			# insert NA for missing fields based on our search case
			if case==0:
				pass
			if case==1:
				result.insert(2, 'Unlisted')
			if case==2:
				result.insert(1, 'Unlisted')
				result.insert(2, 'Unlisted')
			if case==3:
				result.insert(0, 'Unlisted')
			if verbose:
				print(result)
			# build the formatted measurement string
			new_result = [r+' '+w+'.' for r, w in \
				zip(result, ['Diameter', 'Weight', 'Hour'])]
			if verbose:
				print(new_result)
			new_result = ' '.join(new_result)
			if verbose:
				print(new_result)
			# sub the formatted string into the original text
			text = re.sub(pattern, new_result, text)
			if verbose:
				print(text)
			return text
	raise Exception('No regex match. Unable to format measurements for {}'.format(text))




	# try:
	# 	# case 1: complete string
	# 	regex = r'\(.+mm.+g.+h\)'
	# 	result = re.search(regex, text)
	# 	if result is not None:
	# 		# format diameter, weight, orientation info
	# 		result = standardize_measurements(result.group(0))
	# 		words = ['Diameter', 'Weight', 'Hour']
	# 		result = strip_measurements(result, words)
	# 		result = result + ' Measurement Case 1'
	# 		# substitute this reformatted info into the original text
	# 		text = re.sub(regex, result, text)
	# 		return text

	# 	# case 2: missing 'h' only
	# 	regex = r'\(.+mm.+g\)'
	# 	result = re.search(regex, text)
	# 	if result is not None:
	# 		# format diameter, weight, orientation info
	# 		result = standardize_measurements(result.group(0))
	# 		words = ['Diameter', 'Weight']
	# 		result = strip_measurements(result, words)
	# 		result = result + ' Unlisted Hour.'
	# 		result = result + ' Measurement Case 2'
	# 		# substitute this reformatted info into the original text
	# 		text = re.sub(regex, result, text)
	# 		return text
	# 	# case 3: missing 'g' and 'h' (no end space)
	# 	regex = r'\(.+mm\)'
	# 	result = re.search(regex, text)
	# 	if result is not None:
	# 		# format diameter, weight, orientation info
	# 		result = standardize_measurements(result.group(0))
	# 		words = ['Diameter']
	# 		result = strip_measurements(result, words)
	# 		result = result + ' Unlisted Weight. Unlisted Hour.'
	# 		result = result + ' Measurement Case 3'
	# 		# substitute this reformatted info into the original text
	# 		text = re.sub(regex, result, text)
	# 		return text
	# 	# case 4: missing 'mm' only
	# 	regex = r'\(.+g.+h\)'
	# 	result = re.search(regex, text)
	# 	if result is not None:
	# 		# format diameter, weight, orientation info
	# 		result = standardize_measurements(result.group(0))
	# 		words = ['Weight', 'Hour']
	# 		result = strip_measurements(result, words)
	# 		result = 'Unlisted Diameter. ' + result
	# 		result = result + ' Measurement Case 4'
	# 		# substitute this reformatted info into the original text
	# 		text = re.sub(regex, result, text)
	# 		return text
	# 	# case 5: missing 'g' and 'h' (with ending space)
	# 	regex = r'\(.+mm \)'
	# 	result = re.search(regex, text)
	# 	if result is not None:
	# 		result = result.group(0)
	# 		result = result.replace('mm ', 'mm')
	# 		# format diameter, weight, orientation info
	# 		result = standardize_measurements(result)
	# 		words = ['Diameter']
	# 		result = strip_measurements(result, words)
	# 		result = result + ' Unlisted Weight. Unlisted Hour.'
	# 		result = result + ' Measurement Case 5'
	# 		# substitute this reformatted info into the original text
	# 		text = re.sub(regex, result, text)
	# 		return text
	# 	raise TypeError()
	# except:
	# 	exit('unable to format measurements for {}'.format(text))






# impute 'Stuck' keyword if missing (goes after 'mint')
def impute_strike(text, verbose=False):
	if re.search(r'Struck ', text) is None:
		if(verbose): 
			print('pre-strike text: {}'.format(text))
		pos = -1
		segments = text.split('. ')
		for index, segment in enumerate(segments):
			if 'mint' in segment:
				pos = index + 1
		segments.insert(pos, 'unlisted Struck')
		text = '. '.join(segments)
		if(verbose): 
			print('post-strike text: {}'.format(text))
	return text

# impute 'mint' keyword if missing (goes before 'Stuck')
def impute_mint(text, verbose=False):
	if re.search(r'mint', text) is None:
		if(verbose): 
			print('pre-mint text: {}'.format(text))
		pos = -1
		segments = text.split('. ')
		for index, segment in enumerate(segments):
			if 'Struck' in segment:
				pos = index + 1
		segments.insert(pos, 'unlisted mint')
		text = '. '.join(segments)
		if(verbose): 
			print('post-mint text: {}'.format(text))
	return text

# impute 'moneyer' if missing (goes after 'mint' and before 'Struck')
def impute_moneyer(text, verbose=False):
	if re.search(r'moneyer', text) is None:
		if(verbose): 
			print('pre-moneyer text: {}'.format(text))
		pos = -1
		segments = text.split('. ')
		for index, segment in enumerate(segments):
			if 'mint' in segment:
				pos = index + 1
		segments.insert(pos, 'unlisted moneyer')
		text = '. '.join(segments)
		if(verbose): 
			print('post-strike text: {}'.format(text))
	return text





if __name__ == '__main__':

	print(' Script name: {}'.format(sys.argv[0]))
	print(' Number of arguments: {}'.format(len(sys.argv)))
	print(' Arguments include: {}'.format(str(sys.argv)))

	if len(sys.argv)!=2: 
		exit('missing input!')

	input_file = sys.argv[1]
	outname = input_file.split('/')[1]+'_cleaned.csv'
	outdir = 'data_scraped/'+input_file.split('/')[1]
	fullname = os.path.join(outdir, outname)

	df = pd.read_csv(input_file)
	print(df.shape)
	#print(df.info())

	# replace missing entries with an explicit None
	df['Header'] = df['Header'].apply(lambda x: 'No Header' if pd.isnull(x) else x)
	df['Notes'] = df['Notes'].apply(lambda x: 'No Notes' if pd.isnull(x) else x)
	#print(df.info())

	# remove entries tagged as non-standard
	df = df[~df['Nonstandard Lot']]
	print(df.shape)
	
	# remove Affiliated Auctions based on auction type
	df = df[~df['Auction Type'].str.contains(r'Affiliated Auction')]
	print(df.shape)

	# remove Affiliated Auctions based on keyword
	df = df[~df['Description'].str.contains(r'\(Silver')]
	print(df.shape)
	df = df[~df['Description'].str.contains(r'\(Gold')]
	print(df.shape)

	# clean and standardize the 'Description' field for subsequent feature engineering

	# correct hyphenations
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'BC- AD', 'BC-AD', x))
	
	# consolidate Rare keyword with comments section so we don't have to mark everything as not rare
	#df['Description'] = df['Description'].apply(lambda x: re.sub(r'\. Rare\.', ' Rare.', x))
	
	# replace 'Fair' with 'Fine' for consistent grading
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Fair', 'Fine', x))

	#df['Description'] = df['Description'].apply(lambda x: format_dashes(x))
	#print(df.info())

	# df['Description'] = df['Description'].apply(lambda x: format_spaces(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_strike(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_mint(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_moneyer(x))
	#print(df.info())

	print(df.shape)
	print(df.info())

	# build and save the dataframe
	df.to_csv(fullname, index=False)
