# coding: utf-8

import re
import sys
import os
import pandas as pd
import numpy as np

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)


# order matters; e.g., want to check for 'Superb EF' before 'EF'
grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 
		'Choice VF', 'Nice VF', 'Good VF', 'Near VF', 'VF', 
		'Good Fine', 'Near Fine', 'Fine']

def extract_feature(text, keyword):
	#print(text)
	for segment in text.split('.'):
		if keyword in segment:
			return segment
	raise Exception('{} not found in {}'.format(keyword, text))

# def get_emperor(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		if 'Emperor' in segment:
# 			return segment
# 	raise Exception('Emperor not found in {}'.format(text))

# def get_reign(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		if 'Reign' in segment:
# 			return segment
# 	raise Exception('Reign not found in {}'.format(text))

# def get_denomination(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		if 'Denomination' in segment:
# 			return segment
# 	raise Exception('Denomination not found in {}'.format(text))

# def get_mint(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'mint' in segment:
# 			return segment
# 	raise Exception('Mint not found in {}'.format(text))

# def get_strike_date(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'Struck' in segment:
# 				return segment
# 	raise Exception('Strike Date not found in {}'.format(text))

# def get_moneyer(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'moneyer' in segment:
# 				return segment
# 	raise Exception('Moneyer not found in {}'.format(text))

# def get_imagery(text, verbose=True):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if ' / ' in segment:
# 			return segment
# 	raise Exception('Imagery not found in {}'.format(text))

# def get_grade(text):
# 	#print(text)
# 	for segment in reversed(text.split('.')):
# 		#print(segment)
# 		if 'Grade' in segment:
# 			return segment
# 	raise Exception('Grade not found in {}'.format(text))

# def get_comments(text, verbose=True):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'Comments' in segment:
# 			return segment
# 	raise Exception('Comments not found in {}'.format(text))


def extract_measure(text, measure, units):
	#print(text)
	for segment in text.split('.'):
		#print(segment)
		if 'unlisted' in segment:
			return np.nan
		if measure in segment:
			#print(segment)
			segment = segment.replace('@', '.')
			segment = segment.replace(measure, '')
			segment = segment.replace(units, '')
			segment = segment.strip()
			#print(segment)
			try:
				return float(segment)
			except:
				raise Exception('Bad {} in {}'.format(measure, text))
	raise Exception('{} keyword not found in {}'.format(measure, text))

# def get_diameter(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'unlisted Diameter' in segment:
# 			return np.nan
# 		if 'Diameter' in segment:
# 			#print(segment)
# 			segment = segment.replace('@', '.')
# 			segment = segment.replace('Diameter', '')
# 			segment = segment.replace('mm', '')
# 			segment = segment.strip()
# 			#print(segment)
# 			try:
# 				return float(segment)
# 			except:
# 				raise Exception('Bad Diameter in {}'.format(text))
# 	raise Exception('Diameter keyword not found in {}'.format(text))

# def get_weight(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'unlisted Weight' in segment:
# 			return np.nan
# 		if 'Weight' in segment:
# 			#print(segment)
# 			segment = segment.replace('@', '.')
# 			segment = segment.replace('Weight', '')
# 			segment = segment.replace('g', '')
# 			segment = segment.strip()
# 			#print(segment)
# 			try:
# 				return float(segment)
# 			except:
# 				raise Exception('Bad Weight in {}'.format(text))
# 	raise Exception('Weight keyword not found in {}'.format(text))

# def get_hour(text):
# 	#print(text)
# 	for segment in text.split('.'):
# 		#print(segment)
# 		if 'unlisted Hour' in segment:
# 			return np.nan
# 		if 'Hour' in segment:
# 			#print(segment)
# 			segment = segment.replace('@', '.')
# 			segment = segment.replace('Hour', '')
# 			segment = segment.replace('h', '')
# 			segment = segment.strip()
# 			#print(segment)
# 			try:
# 				return int(segment)
# 			except:
# 				raise Exception('Bad Hour in {}'.format(text))
# 	raise Exception('Hour keyword not found in {}'.format(text))







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
	result = re.search(r'[Uu]npublished|[Uu]nique', text)
	print(result)
	if result is not None:
		return 'RIC Unique'
	raise Exception('RIC number not found in {}'.format(text))








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
	#	if len(fields)!= XXX:
	#		raise Exception('problem in length')
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
	
	df['Emperor'] = df['Description'].apply(lambda x: extract_feature(x, 'Emperor'))
	df['Reign'] = df['Description'].apply(lambda x: extract_feature(x, 'Reign'))
	df['Denomination'] = df['Description'].apply(lambda x: extract_feature(x,'Denomination'))

	df['Diameter'] = df['Description'].apply(lambda x: extract_measure(x, 'Diameter', 'mm'))
	df['Weight'] = df['Description'].apply(lambda x: extract_measure(x, 'Weight', 'g'))
	df['Hour'] = df['Description'].apply(lambda x: extract_measure(x, 'Hour', 'h'))

	df['Mint'] = df['Description'].apply(lambda x: extract_feature(x, 'mint'))

	df['Moneyer'] = df['Description'].apply(lambda x: extract_feature(x, 'moneyer'))
	df['Struck'] = df['Description'].apply(lambda x: extract_feature(x, 'Struck'))
	df['Imagery'] = df['Description'].apply(lambda x: extract_feature(x, ' / '))

	# original --->>>>>
	#df['Obverse'], df['Reverse'] = zip(*df.apply(lambda x: split_imagery(x['Description'], x['Imagery']), axis=1))
	# original --->>>>>

	# rev1 --->>>>>
	#df['Obverse'] = df.apply(lambda x: split_imagery(x['Description'], x['Imagery']), axis=1)
	#print(df.info())
	# rev1 --->>>>>

	# original --->>>>>
	#df['Obverse'], df['Reverse'] = zip(*df['Imagery'].apply(split_imagery))
	#print(df.info())
	# original --->>>>>

	#df['Inscriptions'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.isupper()]))
	#df['Inscriptions'] = df['Inscriptions'].apply(clean_inscriptions)
	#df.drop('Imagery', axis=1, inplace=True)
	#print(df.info())

	df['RIC'] = df['Description'].apply(lambda x: get_RIC_number(x))
	df['Grade'] = df['Description'].apply(lambda x: extract_feature(x, 'Grade'))
	df['Comments'] = df['Description'].apply(lambda x: extract_feature(x ,'Comments'))

	#df['Inscription'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.isupper()]))
	# select only the imagery
	#df['Imagery'] = df['Imagery'].apply(lambda x: ' '.join([word for word in x.split(' ') if word.islower()]))                                                          
	# try splitting on '/' to get obverse and reverse segmentation

	# drop the now fully parsed Description field
	df.drop(['Description'], inplace=True, axis=1)
	print(df.info())

	# build and save the dataframe
	df.to_csv(fullname, index=False)
