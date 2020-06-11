import re
import sys
import os
import pandas as pd
import numpy as np

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

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
	text = re.sub(r' C\.', ' C', text) # space to avoid BC.
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
	if verbose:
		print(text)
	# scan text for the following regex patterns
	patterns = [
		r'\(.+mm.+[g|gm].+h\)\.', # case 1: complete string
		r'\(.+mm.+[g|gm]\)\.',    # case 2: missing 'h' only
		r'\(.+mm\)\.',            # case 3: missing 'g' and 'h' (no end space)
		r'\(.+[g|gm].+h\)\.',     # case 4: missing 'mm' only
		r'\(.+mm \)\.',           # case 5: missing 'g' and 'h' (with ending space)
		r'\(.+[g|gm]\)\.',        # case 6: missing 'mm' and 'h'
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
				result.insert(2, 'unlisted')
			if case==2:
				result.insert(1, 'unlisted')
				result.insert(2, 'unlisted')
			if case==3:
				result.insert(0, 'unlisted')
			if case==4:
				result.insert(1, 'unlisted')
				result.insert(2, 'unlisted')
			if case==5:
				result.insert(0, 'unlisted')
				result.insert(2, 'unlisted')
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

def format_mint(text):
	# mint with semicolon indicates proceeding moneyer
	text = re.sub(r'mint\;', 'mint.', text)
	return text


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
	
	# remove additional non-standard cases
	# ====================================

	# remove forgeries
	df = df[~df['Description'].str.contains(r'forger')]

	# remove 'Affiliated Auctions' based on auction type
	df = df[~df['Auction Type'].str.contains(r'Affiliated Auction')]
	print(df.shape)

	# remove 'Affiliated Auctions' based on keyword
	df = df[~df['Description'].str.contains(r'\(Silver')]
	print(df.shape)
	df = df[~df['Description'].str.contains(r'\(Gold')]
	print(df.shape)

	# remove any As denomination that snuck in
	df = df[~df['Description'].str.contains(r'AE As')]
	print(df.shape)

	# *I think* these are provincial coins
	# df = df[~df['Description'].str.contains(r'ZEUGITANA')]
	#df = df[~df['Description'].str.contains(r'BYZACIUM')]
	#df = df[~df['Description'].str.contains(r'SPAIN Gades')]
	# df = df[~df['Description'].str.contains(r'THESSALY')]
	#df = df[~df['Description'].str.contains(r'LYCIAN LEAGUE')]
	# df = df[~df['Description'].str.contains(r'NUMIDIA')]
	# df = df[~df['Description'].str.contains(r'SELEUCIS')]
	# print(df.shape)

	# as far as I can tell these are non-standard (provincial?) sestertii
	df = df[~df['Description'].str.contains(r'Æ \"Sestertius\"')]
	df = df[~df['Description'].str.contains(r'Æ \“Sestertius\”')]
	print(df.shape)
	# ... as are these
	df = df[~df['Description'].str.contains(r'Dupondius\?')]
	df = df[~df['Description'].str.contains(r'Sestertius\?')]
	df = df[~df['Description'].str.contains(r'Tetrassarion')]
	print(df.shape)

	# no RIC number present? Only to isolate good Sestertii
	df = df[df['Description'].str.contains(r'RIC ')]
	print(df.shape)

	# correct edge cases 
	# ==================

	# Augustus_Aur_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'BC- AD', 'BC-AD', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Fair', 'Fine', x))
	# Augustus_Aur_PA1.csv
	# <--- okay
	# Augustus_Den_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Augustus\. Silver', 'Augustus. 27 BC-AD 14. AR Denarius', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'175mm', '17.5mm', x))
	# Augustus_Den_EA2.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'6nh', '6h', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Nice VF', 'Good VF', x))
	# Augustus_Den_EA3.csv 
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'379 g', '3.79 g', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'230mm', '20mm', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'\(9mm', '(9mm', x))
	# Augustus_Den_EA4.csv
	# <--- okay
	# Augustus_Den_PA1.csv
	# <--- okay
	# Augustus_Den_PA2.csv
	# <--- okay
	# Augustus_Den_PA3.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'3/91', '3.91', x))
	# Augustus_Ses_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'AUGUSTUS', 'Augustus', x))

	# clean and standardize the Description field
	# ====================================

	#df['Description'] = df['Description'].apply(lambda x: format_dashes(x))
	#print(df.info())

	# df['Description'] = df['Description'].apply(lambda x: format_spaces(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_mint(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_strike(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_mint(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: impute_moneyer(x))
	#print(df.info())

	print(df.info())

	# build and save the dataframe
	df.to_csv(fullname, index=False)
