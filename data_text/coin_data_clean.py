import re
import sys
import os
import pandas as pd
import numpy as np
import json

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

# remove whitespace
#import re
#pattern = re.compile(r'\s+')
#sentence = re.sub(pattern, '', sentence)

#def get_positions(x, character):
#	return [pos for (pos, char) in enumerate(x) if char == character]

def write_output(input_file, keyword):
	output_name = input_file.split('/')[1]+'_'+keyword+'.csv'
	output_dir = 'data_scraped/'+input_file.split('/')[1]
	output_path = os.path.join(output_dir, output_name)
	print('output path: {}'.format(output_path))
	return output_path

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
	text = re.sub(r'Mn\.', 'Mn', text) # Manius
	text = re.sub(r'P\.', 'P', text)
	text = re.sub(r'Q\.', 'Q', text)
	text = re.sub(r'R\.', 'R', text)
	return text

def format_slash(text, verbose=False):
	if verbose:
		print('------------------------------------------------------')
		print('Input Text:\n {}'.format(text))
	# relies on these existing
	pos1 = text.find('Struck')
	pos2 = text.find('RIC')
	subtext = text[pos1:pos2]
	if verbose:
		print('Input Subtext:\n {}'.format(subtext))
	if(len(subtext.split(' / '))==2):
		#subtext = subtext.replace('/', ', Obverse. Reverse, ')
		new_subtext = re.sub(r' / ', ', Obverse. Reverse, ', subtext)
		if verbose:
			print('New Subtext:\n {}'.format(new_subtext))
		text = text.replace(subtext, new_subtext)
		if verbose:
			print('New Text:\n {}'.format(text))
	else:
		raise Exception('more than one split in text: {}'.format(text))
	return text

def format_emperor(text, verbose=False):
	#print(text)
	emperors = [
		'Augustus', 
		'Nero', 
		'Antoninus Pius', 
		'Faustina Senior'
	]
	#print('----------')
	for emperor in emperors:
		if emperor in text.split('.')[0]:
			text = re.sub(emperor, 'Emperor, '+emperor, text)
			return text
	raise Exception('No emperor match in text: {}'.format(text))

def format_reign(text, verbose=False):
	regexps = [
		r'\d+\sBC-AD\s\d+',
		r'AD\s\d+-\d+',
		r'\d+-\d+\sAD' # alternative AD scheme
	]
	#print('----------')
	for regexp in regexps:
		result = re.search(regexp, text) # just the first occurance
		if result is not None:
			result = result.group()
			#print(text, result)
			text = re.sub(result, 'Reign, '+result, text)
			#print(text)
			return text
	raise Exception('No regex match for reign in text: {}'.format(text))

# def format_denomination(text, verbose=False):
# 	# add separation period
# 	regexps = [
# 		{r'AV Aureus': 'Denomination, AV Aureus.'},
# 		{r'AR Denarius', 'Denomination, AR Denarius.'},
# 		{r'AR Cistophorus': 'Denomination, AR Cistophorus.'},
# 		{r'(Æ|AE) Sestertius': 'Denomination, AE Sestertius.'}
# 	]
# 	for regexp, subsitution in regexps:
# 		result = re.search(regexp, text)
# 		if result is not None:
# 			result = result.group()
# 			#print(text, result)
# 			text = re.sub(result, subsitution, text)
# 			#print(text)
# 			return text
# 	raise Exception('No regex match for reign in text: {}'.format(text))

def format_denomination(text, verbose=False):
	# add separation period
	text = re.sub(r'AV Aureus', 'Denomination, AV Aureus.', text)
	text = re.sub(r'AR Denarius', 'Denomination, AR Denarius.', text)
	text = re.sub(r'AR Cistophorus', 'Denomination, AR Cistophorus.', text)
	text = re.sub(r'(Æ|AE) Sestertius', 'Denomination, AE Sestertius.', text)
	return text

def format_measurements(text, verbose=False):
	if verbose:
		print('------------------------------------------------------')
		print(text)
	regexps = [
		r'\(.+mm.+gm?.+h\)\.?', # case 0: complete string (sometimes final . is missing)
		r'\(.+mm.+gm?\)\.',     # case 1: missing 'h' only
		r'\(.+mm\)\.',          # case 2: missing 'g' and 'h' (no end space)
		r'\(.+gm?.+h\)\.',      # case 3: missing 'mm' only
		r'\(.+mm \)\.',         # case 4: missing 'g' and 'h' (with ending space)
		r'\(\S+\s+gm?\s?\)\.'   # case 5: missing 'mm' and 'h'; using \S and \s
	]
	for case, regexp in enumerate(regexps):
		if verbose:
			print('case {}'.format(case))
			print('regexp: {}'.format(regexp))
		result = re.search(regexp, text)
		if result is not None:			
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
			result = result.replace('h ', 'h')
			# remove brackets and final period '.'
			result = result[1:-2]
			if verbose:
				print(result)
			# replace internal '.'s to simplify later feature extraction
			result = result.replace('.', '@')
			if verbose:
				print(result)
			# split match into individual measurements
			result = result.split(' ')
			if verbose:
				print(result)
			# denote missing fields as unlisted
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
			# insert keyword for each measurement type
			result[0] = result[0].replace(result[0], 'Diameter, '+result[0]+'.')
			result[1] = result[1].replace(result[1], 'Weight, '+result[1]+'.')
			result[2] = result[2].replace(result[2], 'Hour, '+result[2]+'.')
			# rejoin the list intro a string
			new_result = ' '.join(result)
			if verbose:
				print(new_result)
			# substitute the formatted string into the original text
			text = re.sub(regexp, new_result, text)
			if verbose:
				print(text)
			return text
	raise Exception('No regex match for measurements in text: {}'.format(text))

def format_mint(text):
	# mint with semicolon indicates proceeding moneyer
	# e.g. Rome mint; C. Marius C. f. moneyer.
	text = re.sub(r'mint;', 'mint.', text)
	return text

def impute_feature(text, keyword, tagword, verbose=False):
	if re.search(keyword, text) is None:
		if(verbose): 
			print('before {} insert:\n{}'.format(keyword, text))
		pos = -1
		segments = text.split('. ')
		for index, segment in enumerate(segments):
			if tagword in segment:
				pos = index + 1
				# exit on first match
				break 
		segments.insert(pos, 'unlisted'+' '+keyword)
		text = '. '.join(segments)
		if(verbose): 
			print('after {} insert:\n{}'.format(keyword, text))
	return text

# grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 
# 		'Choice VF', 'Nice VF', 'Good VF', 'Near VF', 'VF', 
# 		'Good Fine', 'Near Fine', 'Fine']

def format_grade(text):
	# "Good VF toned --> Good VF. Comments: toned"
	# "EF. --> EF. Comments:"
	# use ? to grab cases where no comments exist, just the grade
	text = re.sub(r' FDC\.?', ' FDC, Grade. Comments,', text)
	text = re.sub(r' EF\.?', ' EF, Grade. Comments,', text)
	text = re.sub(r' VF\.?', ' VF, Grade. Comments,', text)
	text = re.sub(r' Fine\.?', ' Fine, Grade. Comments,', text)
	return text

# use get_RIC_number to build this
def format_RIC(text):
	text = re.sub(r'RIC', 'RN, RIC', text)
	return text

def extract_feature(text, keyword):
	#print(text)
	for segment in text.split('.'):
		if keyword in segment:
			# remove keyword and clean up
			segment = segment.replace(keyword+', ', '')
			segment = segment.replace(', '+keyword, '')
			segment = segment.replace('@', '.') # hack for measure fields
			segment = segment.strip()
			return segment
	raise Exception('{} not found in {}'.format(keyword, text))

def get_RIC_number(text):
	regexps = [
		# match pattern 'RIC I/II/III 0-9/00-99/000-999'
		r'RIC (IV|III|II|I) ([0-9][0-9][0-9]|[0-9][0-9]|[0-9])',
		# match pattern 'RIC I/II/III -' (what is the - notation?)
		r'RIC (IV|III|II|I) -', 
		# match pattern 'RIC -' (only the dash?)
		r'RIC -',
		# match pattern 'RIC 0-999...' (only the numerals?)
		r'RIC \d+',
		# match cases where RIC number is absent
		r'[Uu]nlisted|[Uu]npublished|[Uu]nique'
	]
	for regexp in regexps:
		result = re.search(regexp, text)
		#print(result)
		if result is not None:
			return result.group(0)
	raise Exception('RIC keyword not found in {}'.format(text))


if __name__ == '__main__':

	# Load Data
	# =========

	print(' Script name: {}'.format(sys.argv[0]))
	print(' Number of arguments: {}'.format(len(sys.argv)))
	print(' Arguments include: {}'.format(str(sys.argv)))
	if len(sys.argv)!=2: 
		exit('missing input!')

	df = pd.read_csv(sys.argv[1])
	#print(df.info())
	print('pre-selection shape: {}'.format(df.shape))

	# Data Selection
	# ==============

	# load stop words
	stop_words = []
	with open('config/stop_words.txt', mode='r', encoding='utf-8') as f:
		# drop trailing \n for each line and skip lines that start with #
		stop_words = [re.compile(line[:-1]) for line in f if '#' not in line]

	# remove non-standard coins from data
	for stop in stop_words:
		df = df[~df['Description'].str.contains(stop, regex=True)]
		#print(stop, df.shape)
	print('post-selection shape: {}'.format(df.shape))

	# remove Affiliated Auctions (these non-standard formatting)
	df = df[~df['Auction Type'].str.contains(r'Affiliated Auction')]
	print('post-selection shape: {}'.format(df.shape))

	# Data Formatting
	# ===============

	# AUGUSTUS

	# Augustus_Aur_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'BC- AD', 'BC-AD', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Fair', 'Fine', x))
	# Augustus_Aur_PA1.csv
	# <--- okay
	# Augustus_Den_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Augustus\. Silver', 'Augustus. 27 BC-AD 14. AR Denarius', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'175mm', '17.5mm', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'OB / CIVIS / SERVATOS', 'OB | CIVIS | SERVATOS', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'AMP /', 'AMP/', x)) # EA1, PA1, PA2
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
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'PAREN\[T\] /', 'PAREN[T]/', x)) # Triton XI, 767, 500
	# Augustus_Den_PA3.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'3/91', '3.91', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'M[\.] DVRMIVS III\. VIR', 'M • DVRMIVS/ • III • VIR', x)) # FA, Triton X, 559
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'S•P•Q•R /', 'S•P•Q•R/', x)) # FA, CNG 75, 964
	# Augustus_Ses_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'AUGUSTUS', 'Augustus', x)) # <--- should this be AUGUSTUS\.

	# NERO

	# Nero_Aur_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'\(19mm 7\.13\)', '(19mm 7.13 g)', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'NERO\.', 'Nero.', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'/  / PONTIF • MAX', '/ PONTIF • MAX •', x))
	# Nero_Aur_PA1.csv
	# <--- okay
	# Nero_Den_EA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'\(18mm 328 g 5h\)', '(18mm 3.28 g 5h)', x))
	# Nero_Den_EA2.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'NERO\,? with Agrippina', 'Nero with Agrippina', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'NERO and AGRIPPINA JR', 'Nero and Agrippina Jr', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'RIC I 7; BMCRE 8; RSC 4\.', 'RIC I 7; BMCRE 8; RSC 4. Good Fine', x)) # <-- missing grade!
	# Nero_Den_PA1.csv 
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Struck AD 60-61. PONTIF • MAX', 'Struck AD 60-61. NERO CAESAR AUG IMP / PONTIF • MAX', x)) # missing obv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'\(352 g 5h\)', '(3.52 g 5h)', x))
	# Nero_Ses_EA1.csv
	# <--- okay
	# Nero_Ses_EA2.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'RIC I 388\. green patina', 'RIC I 7; RIC I 388. Fine, green patina', x)) # <-- missing grade!
	# Nero_Ses_PA1.csv
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Superb virtually as struck', 'Superb EF, virtually as struck', x)) # <-- missing grade!

	# PIUS

	with open('config/replace_pius.json') as f: 
		data = json.load(f)
		for r in data['replacement']:
			if r['replace']:
				#print(' --> replacing [{}] with [{}] from {}'.format(r['regex'], r['sub'], r['file']))
				df['Description'] = df['Description'].apply(lambda x: re.sub(r['regex'], r['sub'], x))

	# Specify data types
	# ==================

	df['Auction ID'] = df['Auction ID'].astype(str)

	# Impute Missing Values
	# =====================

	df['Header'] = df['Header'].apply(lambda x: 'No Header' if pd.isnull(x) else x)
	df['Notes'] = df['Notes'].apply(lambda x: 'No Notes' if pd.isnull(x) else x)
	#print(df.info())

	# Standardize the Description field
	# =================================

	df['Description'] = df['Description'].apply(lambda x: format_abbreviations(x))
	df['Description'] = df['Description'].apply(lambda x: format_emperor(x))
	df['Description'] = df['Description'].apply(lambda x: format_reign(x))
	df['Description'] = df['Description'].apply(lambda x: format_denomination(x))
	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	df['Description'] = df['Description'].apply(lambda x: format_mint(x))

	# impute possible missing keywords
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='mint', tagword='Hour'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='moneyer', tagword='mint'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='Struck', tagword='moneyer'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword=' / ', tagword='Struck'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='RIC', tagword=' / '))

	df['Description'] = df['Description'].apply(lambda x: format_grade(x))
	df['Description'] = df['Description'].apply(lambda x: format_slash(x))
	print(df.info())

	# build and save intermediate clean dataframe
	df.to_csv(write_output(sys.argv[1], 'cleaned'), index=False)

	# Extract Fields from Description
	# ===============================

	df['Emperor'] = df['Description'].apply(lambda x: extract_feature(x, 'Emperor'))
	df['Reign'] = df['Description'].apply(lambda x: extract_feature(x, 'Reign'))
	df['Denomination'] = df['Description'].apply(lambda x: extract_feature(x, 'Denomination'))
	df['Diameter'] = df['Description'].apply(lambda x: extract_feature(x, 'Diameter'))
	df['Weight'] = df['Description'].apply(lambda x: extract_feature(x, 'Weight'))
	df['Hour'] = df['Description'].apply(lambda x: extract_feature(x, 'Hour'))
	df['Mint'] = df['Description'].apply(lambda x: extract_feature(x, 'mint'))
	df['Moneyer'] = df['Description'].apply(lambda x: extract_feature(x, 'moneyer'))
	df['Struck'] = df['Description'].apply(lambda x: extract_feature(x, 'Struck'))
	df['Obverse'] = df['Description'].apply(lambda x: extract_feature(x, 'Obverse'))
	df['Reverse'] = df['Description'].apply(lambda x: extract_feature(x, 'Reverse'))
	df['RIC'] = df['Description'].apply(lambda x: get_RIC_number(x))
	df['Grade'] = df['Description'].apply(lambda x: extract_feature(x, 'Grade'))
	df['Comments'] = df['Description'].apply(lambda x: extract_feature(x ,'Comments'))

	#df['Inscription'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.isupper()]))
	#df['Inscription'] = df['Inscription'].apply(clean_inscriptions)
	# select only the imagery
	#df['Imagery'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.islower()]))                                                          

	# drop the now fully parsed Description field
	df.drop(['Description'], inplace=True, axis=1)
	print(df.info())

	# build and save the dataframe
	df.to_csv(write_output(sys.argv[1], 'prepared'), index=False)







