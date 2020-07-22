# coding: utf-8

import re
import sys
import os
import pandas as pd

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

emperors = ['Augustus', 'Tiberius', 'Nero', 'Galba', 'Otho', 
			'Vespasian', 'Domitian', 'Trajan', 'Hadrian', 
			'Antoninus Pius', 'Marcus Aurelius']

denominations = ['Aureus', 'Denarius', 'Cistophorus', 'Sestertius']

# order matters; e.g., want to check for 'Superb EF' before 'EF'
grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 
		'Choice VF', 'Nice VF', 'Good VF', 'Near VF', 'VF', 
		'Good Fine', 'Near Fine', 'Fine']

def get_emperor(text):
	#print(text)
	for emperor in emperors:
		if emperor in text.split('.')[0]:
			return emperor
	raise Exception('Emperor not found in {}'.format(text))

def get_reign(text):
	#print(text)
	for segment in text.split('.'):
		if 'BC-AD' in segment:
			return segment
		if 'AD' in segment:
			return segment
	raise Exception('Reign not found in {}'.format(text))

def get_denomination(text):
	#print(text)
	for denomination in denominations:
		if denomination in text:
			return denomination
	raise Exception('Denomination not found in {}'.format(text))

def get_diameter(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted Diameter' in segment:
			return None
		if 'Diameter' in segment:
			#print(segment)
			segment = segment.replace('@', '.')
			segment = segment.replace('Diameter', '')
			segment = segment.replace('mm', '')
			segment = segment.strip()
			#print(segment)
			try:
				return float(segment)
			except:
				raise Exception('Bad Diameter in {}'.format(text))
	raise Exception('Diameter keyword not found in {}'.format(text))

def get_weight(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted Weight' in segment:
			return None
		if 'Weight' in segment:
			#print(segment)
			segment = segment.replace('@', '.')
			segment = segment.replace('Weight', '')
			segment = segment.replace('g', '')
			segment = segment.strip()
			#print(segment)
			try:
				return float(segment)
			except:
				raise Exception('Bad Weight in {}'.format(text))
	raise Exception('Weight keyword not found in {}'.format(text))

def get_hour(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted Hour' in segment:
			return None
		if 'Hour' in segment:
			#print(segment)
			segment = segment.replace('@', '.')
			segment = segment.replace('Hour', '')
			segment = segment.replace('h', '')
			segment = segment.strip()
			#print(segment)
			try:
				return int(segment)
			except:
				raise Exception('Bad Hour in {}'.format(text))
	raise Exception('Hour keyword not found in {}'.format(text))

# def get_mcase(text):
# 	for segment in text.split('.'):
# 		if 'Measurement Case' in segment:
# 			return segment
# 	return None

def get_mint(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted Mint' in segment:
			return None
		if 'mint' in segment:
			return segment
	raise Exception('Mint not found in {}'.format(text))

def get_strike_date(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted Struck' in segment:
			return None
		if 'Struck' in segment:
				return segment
	raise Exception('Strike Date not found in {}'.format(text))

def get_moneyer(text):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted moneyer' in segment:
			return None
		if 'moneyer' in segment:
				return segment
	raise Exception('Moneyer not found in {}'.format(text))

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
	raise Exception('RIC number not found in {}'.format(text))

def get_imagery(text, verbose=True):
	#print(text)
	lower = text.find('Struck')
	upper = text.find('RIC')
	if upper<0:
		upper = text.find('BMCRE') # backup
	# isolate text
	if lower>0 and upper>0:
		text = text[lower:upper]
	else:
		raise Exception('Unable to isolate \"imagery\" field in {}'.format(text))
	# assume the longest segment between 'Struck' and 'RIC' 
	# fields contains the coin imagery content
	segments = text.split('.')
	length = 0
	imagery = None
	for segment in segments:
		if len(segment)>length:
			imagery = segment
			length = len(segment)
	#print(' imagery: ', imagery)
	if imagery == None:
		raise Exception('Imagery Missing {}'.format(text))
	return imagery

def get_grade(text):
	#print(text)
	segments = text.split('.')
	# iterate in reverse since we know the grade 
	# information resides in the last sentence;
	# we dont want false positives (e.g. 'fine portrait')
	for segment in reversed(segments):
		#print(segment)
		for grade in grades:
			if grade in segment:
				return grade
	raise Exception('Grade not found in {}'.format(text))

def get_comments(text):
	# isolate the comments section. We know it
	# occurs AFTER the RIC number.
	comments = None
	#print('pre Isolate RIC:\n {}'.format(text))
	lower = text.find('RIC') # add ACIP; RSC; BMCRE as backups
	if lower<0:
		lower = text.find('BMCRE')		
	if lower>0:
		comments = text[lower:]
	else:
		exit('Error: RIC not identified in {}'.format(text))
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
	return comments

def split_imagery(x):
	#print('imagery: {}'.format(x))
	try:
		x.split(' / ')
	except:
		raise Exception('unable to split imagery: {}'.format(x))
	x = x.split(' / ')
	if len(x)!=2:
		raise Exception('more than one split in entry: {}'.format(x))
	return x

def clean_inscriptions(x):
	symbols = ['-', ';', '•','“','”' ,'[', ']', '(', ')']
	for symbol in symbols:
		x = x.replace(symbol, '')
	x = x.replace('Λ', 'A')
	x = x.replace('/ ', ' ')
	x = x.replace(' /', ' ')
	return x


if __name__ == '__main__':

	# this is the right way to do it, but it will take time to validate and catch edge cases
	# fields = ['Emperor', 'Reign', 'Denomination', 'Mint-Moneyer', 'Struck', 'Imagery', 'RIC', 'Grade-Comments-Other']
	# for idx, field in enumerate(fields):
	# 	q = df['Description'].apply(lambda x: x.split('. ')[idx])
	# 	print(q)

	# lof = []
	# for desc in df['Description']:
	# 	fields = desc.split('. ')
	# 	woah = OrderedDict()
	# 	for field, item in zip(fields, field_map):
	# 		# if any(emp in field for emp in emps)
	# 		# 	woah['Emperor'] = emp
	# 		# if re.match(r'\d+ BC-AD \d+', field):
	# 		# 	woah['Reign'] = reign
	# 		# if 'mint' in field:
	# 		# 	woah['Mint'] = field
	# 		# if any(denom in field for denom in denoms)
	# 		# 	woah['Denomination'] = denom
	# 		woah[item] = field
	# 	lof.append(woah)
	# df2 = pd.DataFrame(lof)

	print(' Script name: {}'.format(sys.argv[0]))
	print(' Number of arguments: {}'.format(len(sys.argv)))
	print(' Arguments include: {}'.format(str(sys.argv)))

	if len(sys.argv)!=2: 
		exit('missing input!')

	input_file = sys.argv[1]
	outname = input_file.split('/')[1]+'_prepared.csv'
	outdir = 'data_scraped/'+input_file.split('/')[1]
	fullname = os.path.join(outdir, outname)

	df = pd.read_csv(input_file)
	#print(df.info())
	
	df['Auction ID'] = df['Auction ID'].astype(str)

	df['Emperor'] = df['Description'].apply(lambda x: get_emperor(x))
	#print(df.info())

	df['Reign'] = df['Description'].apply(lambda x: get_reign(x))
	#print(df.info())

	df['Denomination'] = df['Description'].apply(lambda x: get_denomination(x))
	#print(df.info())

	df['Diameter'] = df['Description'].apply(lambda x: get_diameter(x))
	df['Diameter'] = df['Diameter'].astype(float)
	#print(df.info())

	df['Weight'] = df['Description'].apply(lambda x: get_weight(x))
	#print(df.info())

	df['Hour'] = df['Description'].apply(lambda x: get_hour(x))
	#print(df.info())

	#df['MCase'] = df['Description'].apply(lambda x: get_mcase(x)) # for debug
	#print(df.info())

	df['Mint'] = df['Description'].apply(lambda x: get_mint(x))
	#print(df.info())

	df['Moneyer'] = df['Description'].apply(lambda x: get_moneyer(x))
	#print(df.info())

	df['Struck'] = df['Description'].apply(lambda x: get_strike_date(x))
	#print(df.info())

	df['Imagery'] = df['Description'].apply(lambda x: get_imagery(x))
	#print(df.info())

	df['Obverse'], df['Reverse'] = zip(*df['Imagery'].apply(split_imagery))
	#print(df.info())

	df['Inscriptions'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.isupper()]))
	df['Inscriptions'] = df['Inscriptions'].apply(clean_inscriptions)
	df.drop('Imagery', axis=1, inplace=True)
	#print(df.info())

	df['RIC'] = df['Description'].apply(lambda x: get_RIC_number(x))
	#print(df.info())

	df['Grade'] = df['Description'].apply(lambda x: get_grade(x))
	#print(df.info())

	df['Comments'] = df['Description'].apply(lambda x: get_comments(x))
	#print(df.info())

	# woah!!!
	#df['Inscription'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.isupper()]))
	# select only the imagery
	#df['Imagery'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.islower()]))                                                          
	# try splitting on '/' to get obverse and reverse segmentation

	# finally remove the 'Description' column!
	df.drop(['Description'], inplace=True, axis=1)
	print(df.info())

	# build and save the dataframe
	df.to_csv(fullname, index=False)
