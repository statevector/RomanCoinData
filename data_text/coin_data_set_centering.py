import pandas as pd
import re
import glob
import cv2
from collections import OrderedDict

if __name__ == '__main__':

	import glob
	#files = glob.glob('/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero_Den_EA1/*prepared.csv')
	#files = glob.glob('/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero_Den_EA2/*prepared.csv')
	files = glob.glob('/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero_Den_PA1/*prepared.csv')
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	data = data[data['Denomination'].str.contains(r'Denarius')]
	print(data.info())

	# 1. Perfect centering:
	# - possible to see everything the celator engraved on the dies plus the framing of the border
	# - coin appears on a broad flan so that extra metal can even frame the border results in a medallic strike
	# - coins like this are rare

	# 2. Well-centered coins:
	# - have nearly complete designs and inscriptions with only the tips of a few letters cut off
	# - small part a portrait's truncation can be off
	# - border need not be complete

	# 3. Average centering:
	# - Most ancient coins
	# - some letters partly off the edge, or even minor parts of the inscription totally off... 
	# - possibily missing tip of emperor bust
	# - Emperor's name is fully on the coin so this still qualifies as average centering

	# 4. Poor Centering:
	# - 

	num_to_type = {'1':'perfect', '2':'well', '3':'average', '4':'poor'}

	lod=[]
	for idx, (index, obs) in enumerate(data.iterrows()):
		# if idx>3:
		# 	continue
		url_to_input_map = OrderedDict()
		print('coin {} of {}'.format(idx+1, data.shape[0]))
		img = cv2.imread(obs['Image Path'])
		cv2.imshow(obs['Image Path'], img) 
		cv2.waitKey(1)
		num = input('Enter the centering (1=perfect, 2=well, 3=average, 4=poor): ')
		if num == '':
			print('WARNING: missing coin\n{}'.format(obs))
			continue
		url_to_input_map['Image Path'] = obs['Image Path']
		url_to_input_map['Image URL'] = obs['Image URL']
		url_to_input_map['Centered'] = num_to_type[num]
		lod.append(url_to_input_map)

	# build and save the dataframe
	df = pd.DataFrame(lod)
	#df.to_csv('data_centered/Nero_Den_EA1_centering.csv', index=False)
	#df.to_csv('data_centered/Nero_Den_EA2_centering.csv', index=False)
	df.to_csv('data_centered/Nero_Den_PA1_centering.csv', index=False)
	#print(pd.get_dummies(df))

