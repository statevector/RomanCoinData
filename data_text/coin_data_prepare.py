# coding: utf-8

import re
import sys
import os
import pandas as pd

# order matters; e.g., want to check for 'Superb EF' before 'EF'
grades = ['FDC', 'Superb EF', 'Choice EF', 'Near EF', 'EF', 
		'Choice VF', 'Nice VF', 'Good VF', 'Near VF', 'VF', 
		'Good Fine', 'Near Fine', 'Fine']

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
	df.to_csv(fullname, index=False)
