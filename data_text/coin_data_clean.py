import re
import sys
import os
import pandas as pd
import numpy as np

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

# remove whitespace
#import re
#pattern = re.compile(r'\s+')
#sentence = re.sub(pattern, '', sentence)

#def get_positions(x, character):
#	return [pos for (pos, char) in enumerate(x) if char == character]

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

# convert / ---> ,obv. rev,
def format_slash(text, verbose=False):
	if verbose:
		print('------------------------------------------------------')
		print('Input Text: {}\n'.format(text))
	pos1 = text.find('Struck')
	pos2 = text.find('RIC')
	subtext = text[pos1:pos2]
	if verbose:
		print('Input Subtext: {}'.format(subtext))
	if(len(subtext.split(' / '))==2):
		#subtext = subtext.replace('/', ', Obverse. Reverse, ')
		new_subtext = re.sub(r' / ', ', Obverse. Reverse, ', subtext)
		if verbose:
			print('New Subtext: {}'.format(new_subtext))
		text = text.replace(subtext, new_subtext)
		if verbose:
			print('New Text: {}'.format(text))
	else:
		raise Exception('more than one split in text: {}'.format(text))
	return text





def split_imagery(a, b):
	#print('---------------')
	#print('text: {}'.format(a))
	#print('imagery: {}'.format(b))
	y=[]
	try:
		y = b.split(' / ')
	except:
		raise Exception('unable to split imagery: {}'.format(a))
	#print(y)
	if len(y)!=2:
		raise Exception('more than one split in entry: {}'.format(a))
	return y




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
	# scan text for the following regex patterns
	patterns = [
		r'\(.+mm.+gm?.+h\)\.?', # case 1: complete string (sometimes final . is missing)
		r'\(.+mm.+gm?\)\.',     # case 2: missing 'h' only
		r'\(.+mm\)\.',          # case 3: missing 'g' and 'h' (no end space)
		r'\(.+gm?.+h\)\.',      # case 4: missing 'mm' only
		r'\(.+mm \)\.',         # case 5: missing 'g' and 'h' (with ending space)
		r'\(\S+\s+gm?\s?\).'    # case 6: missing 'mm' and 'h'; using \S and \s
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

def format_grade(text):
	# "Good VF toned --> Good VF. Comments: toned"
	# "EF. --> EF. Comments:"
	# use ? to grab cases where no comments exist, just the grade
	text = re.sub(r' FDC\.?', ' FDC, Grade. Comments,', text)
	text = re.sub(r' EF\.?', ' EF, Grade. Comments,', text)
	text = re.sub(r' VF\.?', ' VF, Grade. Comments,', text)
	text = re.sub(r' Fine\.?', ' Fine, Grade. Comments,', text)
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
	#print(df.info())
	print('pre-selection shape: {}'.format(df.shape))

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

	# correct edge cases 
	# ==================

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

	# Pius_Aur_EA1.htm
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'ANTONINUS PIUS', 'Antoninus Pius', x))
	# Pius_Aur_PA1.htm
	# <--- okay
	# Pius_Den_EA1.htm
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'Struck AD 143-144\. AD 138-161', 'Antoninus Pius. AD 138-161', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'in ancient gold pendant mount', '', x))
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'\(18mm 3\.\.23 g 12h\)', '(18mm 3.23 g 12h)', x))
	# Pius_Den_EA2.htm
	# <--- okay
	# Pius_Den_EA3.htm
	df['Description'] = df['Description'].apply(lambda x: re.sub(r'/ PRIMI / DECEN / COS IIII', '/ PRIMI | DECEN | COS IIII', x))
	# Pius_Den_PA1.htm
	# <--- okay
	# Pius_Ses_EA1.htm
	# <--- okay
	# Pius_Ses_EA2.htm
	# <--- okay
	# Pius_Ses_EA3.htm
	# <--- okay
	# Pius_Ses_PA1.htm
	# <--- okay

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
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_emperor(x))
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_reign(x))
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_denomination(x))
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_measurements(x))
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_mint(x))
	#print(df.info())
	# impute possible missing keywords
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='mint', tagword='Hour'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='moneyer', tagword='mint'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='Struck', tagword='moneyer'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword=' / ', tagword='Struck'))
	df['Description'] = df['Description'].apply(lambda x: impute_feature(x, keyword='RIC', tagword=' / '))
	#print(df.info())
	df['Description'] = df['Description'].apply(lambda x: format_grade(x))
	#print(df.info())

	df['Description'] = df['Description'].apply(lambda x: format_slash(x, verbose=True))


	print(df.info())

	# build and save intermediate clean dataframe
	df.to_csv(fullname, index=False)

	# do prepare stuff here
	# ----->

	# build and save final prepare dataframe
	#df.to_csv(fullname, index=False)



