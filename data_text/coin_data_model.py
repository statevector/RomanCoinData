
import numpy as np
import pandas as pd

import re
import glob

from sklearn import base
from sklearn.linear_model import Ridge, Lasso
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer, TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', -1)

# def identify_outliers(data):
# 	# calculate summary statistics
# 	data_mean, data_std = np.mean(data), np.std(data)
# 	# identify outliers
# 	cut_off = data_std * 3
# 	lower, upper = data_mean - cut_off, data_mean + cut_off
# 	# identify outliers
# 	outliers = [x for x in data if x < lower or x > upper]
# 	print('Identified outliers: %d' % len(outliers))
# 	# remove outliers
# 	outliers_removed = [x for x in data if x >= lower and x <= upper]
# 	print('Non-outlier observations: %d' % len(outliers_removed))
# 	return outliers_removed

def consolidate_mints(x):
	# sub greek to latin mint names for consistency
	x = re.sub(r'Ephesos', 'Ephesus', x)
	x = re.sub(r'Pergamon', 'Pergamum', x)
	for mint in mints:
		if mint in x:
			return mint
	return 'Other'

def count_unique_words(series):
	word_list = series.apply(lambda x: pd.value_counts(x.split(' '))).sum(axis = 0)
	return word_list.sort_values(ascending=False)

def consolidate_grades(text):
	#
	# Augustus
	# Near Fine      5
	# Fine          99
	# Good Fine     35
	# Near VF      128
	# VF           586
	# Good VF      354
	# Choice VF      1
	# Near EF      119
	# EF           116
	# Superb EF     17
	# Choice EF      8
	#
	# Nero
	# Near Fine     17
	# Fine         130
	# Good Fine     38
	# Near VF      146
	# VF           358
	# Good VF      180
	# Choice VF      2
	# Near EF       46
	# EF            34
	# Superb EF      4
	# Choice EF      0
	if 'Choice VF' in text:
		return 'Near EF'
	if 'Near Fine' in text:
		return 'Fine'
	if 'Superb EF' in text:
		return 'Good_EF'
	if 'Choice EF' in text:
		return 'Good_EF'
	if 'FDC' in text:
		return 'Good_EF'
	return text

def stem_imagery(text):

	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('λ', 'a'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('avg', 'aug'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('vs', 'us'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).split())

	text = text.replace('/', '')
	text = text.replace('•', '')
	text = text.replace(';', '')
	text = text.replace(':', '')
	text = text.replace('·', '')
	text = text.replace('(', '')
	text = text.replace(')', '')
	text = text.replace('[', '')
	text = text.replace(']', '')
	text = text.replace('Λ', 'A')

	text = text.replace('AVGVSTVS', 'augustus')
	text = text.replace('CAESAR', 'caesar')
	text = text.replace('holding', 'hold')
	text = text.replace('inscribed', 'inscribe')
	text = text.replace('wearing', 'wear')
	text = text.replace('butting', 'butt')
	text = text.replace('galloping', 'gallop')
	text = text.replace('flanking', 'flank')
	text = text.replace('kneeling', 'kneel')
	text = text.replace('attached', 'attach')
	text = text.replace('presenting', 'present')
	text = text.replace('draped', 'drape')
	text = text.replace('ties', 'tie')
	text = text.replace('surmounted', 'surmount')
	text = text.replace('extending', 'extend')
	text = text.replace('seated', 'sit')
	text = text.replace('steps', 'step')
	text = text.replace('raised', 'raise')
	text = text.replace('lashing', 'lash')
	text = text.replace('AVGVSTO', 'augustus')
	text = text.replace('CAESARI', 'caesar')
	text = text.replace('drapery', 'drape')
	text = text.replace('resting', 'rest')
	text = text.replace('diademed', 'diadem')
	text = text.replace('facing', 'face')
	text = text.replace('CΛESΛR', 'caesar')
	text = text.replace('advancing', 'advance')
	text = text.replace('driving', 'drive')
	text = text.replace('bareheaded', 'bare-headed')
	text = text.replace('PΛTER', 'pater')
	text = text.replace('ram’s', 'ram')
	text = text.replace('PATER', 'pater')
	text = text.replace('helmeted', 'helmet')
	text = text.replace('raising', 'raise')
	#text = text.replace('Arm', 'Armenia')
	#text = text.replace('Ger', 'Germania')
	text = text.replace('ΛVGVSTI', 'augustus')
	text = text.replace('riding', 'ride')
	text = text.replace('offering', 'offer')
	text = text.replace('marked', 'mark')
	text = text.replace('buried', 'bury')
	text = text.replace('PΛTRIΛE', 'patria')
	text = text.replace('entwined', 'entwine')
	text = text.replace('PATRIAE', 'patria')
	text = text.replace('CAESARES', 'caesares')
	text = text.replace('CAES', 'caesar')
	text = text.replace('AVGVS', 'augustus')
	text = text.replace('AVGVST', 'augustus')
	text = text.replace('containing', 'contain')
	text = text.replace('consisting', 'consist')
	text = text.replace('held', 'hold')
	text = text.replace('implements', 'implement')
	text = text.replace('slightly', 'slight')
	text = text.replace('placed', 'place')
	text = text.replace('arched', 'arch')
	text = text.replace('ARMENIA', 'armenia')
	text = text.replace('MAR', 'mars')
	text = text.replace('CΛESΛRES', 'caesares')
	text = text.replace('MAR', 'mars')
	text = text.replace('AVGVSTI', 'augustus')
	text = text.lower()

	# data['has_Armenia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'armenia' in x.lower() else False) 

	# data['has_Germania'] = data['Imagery'].apply(lambda x: 
	# 	True if 'ger' in x.lower() else False) # GERMΛNICVS

	# data['has_Dacia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'dac' in x.lower() else False)

	# data['has_Egypt'] = data['Imagery'].apply(lambda x: 
	# 	True if 'egypt' in x.lower() else False)

	# data['has_Parthia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'parth' in x.lower() else False)

	# s = data['Imagery']
	# #words = s.apply(lambda x: pd.value_counts(x.split(' '))).sum(axis=0)
	# t = s.apply(lambda x: x.replace('(',''))
	# t = t.apply(lambda x: x.replace(')',''))
	# t = t.apply(lambda x: x.replace('[',''))
	# t = t.apply(lambda x: x.replace(']',''))
	# t = t.apply(lambda x: x.replace(':',''))
	# t = t.apply(lambda x: x.replace(';',''))
	# t = t.apply(lambda x: x.replace('• ',''))
	# t = t.apply(lambda x: x.replace('· ',''))
	# t = t.apply(lambda x: x.replace('bare-headed', 'bare head'))

	# words = t.apply(lambda x: pd.value_counts(x.split(' '))).sum(axis=0)
	# swords = words.sort_index(axis=0)

	return text

def correct_misspellings(x):
	x = x.replace('scracthes', 'scratches')
	x = x.replace('granualar', 'granular')
	x = x.replace('vareity', 'variety')
	x = x.replace('scarce', 'scarse')
	return x

# flan keyword analysis
def flan_function(x):
	x = x.replace('smal' ,'small')
	x = x.replace('smalll' ,'small')
	x = x.replace('waviness' ,'wavy')
	x = x.replace('planchet', 'flan')
	x = x.replace('flan flaw', 'flan-flaw') # plural included
	x = x.replace('flan imperfection', 'flan-flaw')
	x = x.replace('flan crack', 'flan-crack') # plural included
	# flan stress crack
	x = re.sub(r'flan.+crack', 'flan-crack', x)
	x = x.replace('irregular flan', 'irregular-flan')
	x = x.replace('ragged flan', 'irregular-flan')
	x = x.replace('compact flan', 'compact-flan')
	x = x.replace('tight flan', 'compact-flan')
	x = x.replace('small flan', 'compact-flan')
	x = x.replace('short flan', 'compact-flan')
	# flan a touch short
	x = re.sub('flan.+short', 'compact-flan', x)
	# flan a little bit tight
	x = re.sub(r'flan.+bit tight', 'compact-flan', x)
	x = x.replace('broad flan', 'broad-flan')
	x = x.replace('full flan', 'broad-flan')
	# broad round flan
	x = re.sub(r'broad.+flan', 'broad-flan', x)
	x = x.replace('wavy flan', 'wavy-flan')
	#flan slightly wavy, flan a bit wavy, flan a little wavy
	x = re.sub(r'flan.+wavy', 'wavy-flan', x)
	# slight wave to flan, slight bend in flan
	x = re.sub(r'(wave to|bend in) flan', 'wavy-flan', x)
	return x

def luster_function(x):
	x = x.lower()
	x = x.replace('lustre', 'luster')
	x = x.replace('luster', 'luster')
	x = x.replace('lustrous', 'luster')
	return x

# do description lemmatization and stemming here
class TextTransformer(base.BaseEstimator, base.TransformerMixin):

	def __init__(self, col_name):
		self.col_name = col_name

	# This transformer doesn't need to learn anything about the data.
	# It can just return 'self' without any further processing.
	def fit(self, X, y=None):
		return self

	# Return an array with the same number of rows as X and one column
	# for each feature defined in self.col_names
	def transform(self, X, y=None):
		#X_trans = [row[col_name] for col_name in self.col_names for row in X]
		X_trans = []
		for row in X[self.col_name]:
			X_trans.append(row)
		return X_trans


if __name__ == '__main__':

	import glob
	files = glob.glob("/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv")
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	#data = data[~data['Denomination'].str.contains(r'Sestertius')]
	#data = data[~data['Denomination'].str.contains(r'Cistophorus')]
	#data = data[~data['Denomination'].str.contains(r'Aureus')]
	#
	data = data[data['Denomination'].str.contains(r'Sestertius')]
	# shuffle dataframe here
	#data = data[0:500] # r2 of 0.87
	#data = data[501:] # r2 of 0.79
	#
	print(data.shape)
	print('INPUT DATASET: ')
	data.info()

	# nero data
	# import glob
	# files = glob.glob("/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv")
	# data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	# print(data.shape)
	# data.info()

	# =========

	# non predictive
	data.drop(['URL'], axis=1, inplace=True)

	# one hot encode 'Auction Type' and drop
	data['is_Feature_Auction'] = data['Auction Type'].map(lambda x: True if 'Feature Auction' in x else False)
	data.drop(['Auction Type'], axis=1, inplace=True)

	# one hot encode 'Auction ID' and drop
	data['Auction ID'] = data['Auction ID'].astype(str)
	data['is_Triton'] = data['Auction ID'].map(lambda x: True if 'Triton' in x else False)
	data['is_CNG'] = data['Auction ID'].apply(lambda x: True if 'CNG' in x else False)
	# <-- drop first weekly values. Double check.
	data.drop(['Auction ID'], axis=1, inplace=True)

	# non predictive
	data.drop(['Auction Lot'], axis=1, inplace=True)

	# transform to be symmetric (big model improvement!)
	data['Estimate'] = data['Estimate'].map(lambda x: np.log1p(x))

	# define the target vector
	data['Sold'] = data['Sold'].map(lambda x: np.log1p(x))
	#data = data[data['Sold']<data['Sold'].quantile(0.95)] # drop high-end outliers
	y = data['Sold'].values
	data.drop(['Sold'], axis=1, inplace=True)

	# studied and no impact
	#data['has_Header'] = data['Header'].apply(lambda x: False if x=='No Header' else True)
	#print(data['has_Header'].value_counts())	
	#data['len_Header'] = data['Header'].apply(lambda x: len(x))
	data.drop(['Header'], axis=1, inplace=True)

	# studied and no impact
	#data['has_Notes'] = data['Notes'].apply(lambda x: False if x=='No Notes' else True)
	#print(data['has_Notes'].value_counts())	
	#data['len_Notes'] = data['Notes'].apply(lambda x: len(x))
	data.drop(['Notes'], axis=1, inplace=True)

	# non predictive
	data.drop(['Nonstandard Lot'], axis=1, inplace=True)

	# non predictive
	data.drop(['Image URL'], axis=1, inplace=True)

	# non predictive
	data.drop(['Image Path'], axis=1, inplace=True)

	# predictive, but irrelevant for Augustus only dataset
	#data['is_Augustus'] = data['Emperor'].map(lambda x: True if 'Augustus' in x else False)
	data.drop(['Emperor'], axis=1, inplace=True)

	# non predictive
	data.drop(['Reign'], axis=1, inplace=True)

	# one hot encode 'Denomination'
	data['is_Aureus'] = data['Denomination'].map(lambda x: True if 'Aureus' in x else False)
	data['is_Denarius'] = data['Denomination'].map(lambda x: True if 'Denarius' in x else False)
	data['is_Cistophorus'] = data['Denomination'].map(lambda x: True if 'Cistophorus' in x else False)
	# <--- drop first sestertius. Double check.

	# impute missing 'Diameter' measurements
	diameter_map = data.groupby('Denomination')['Diameter'].transform(np.median)
	data['Diameter'] = data['Diameter'].fillna(diameter_map)

	# impute missing 'Weight' measurements
	weight_transformer = data.groupby('Denomination')['Weight'].transform(np.median)
	data['Weight'] = data['Weight'].fillna(weight_transformer)

	# impute missing 'Hour' measurements (drop now for simplicity)
	# assume die axis rotate left vs. rotate right has no effect on sale price
	#data['Hour'] = data['Hour'].map({1:11, 2:10, 3:9, 4:8, 5:7, 6:12})
	#hour_transformer = data.groupby('Denomination')['Hour'].transform(np.median)
	#data['Hour'] = data['Hour'].fillna(hour_transformer)
	#data = pd.get_dummies(data, prefix='is_Hour', columns=['Hour'], drop_first=True, dtype=np.int) # drop true!
	
	# studied and no impact
	data.drop(['Hour'], axis=1, inplace=True)

	data.drop(['Denomination'], axis=1, inplace=True)

	# studied and no impact
	# mints = ['Lugdunum', 'Rome', 'Emerita', 'Tarraco', 'Colonia Patricia', 'Caesaraugusta',
	# 	'Pergamum', 'Ephesus', 'eastern', 'Asia Minor', 'Uncertain']
	# data['Mint'] = data['Mint'].map(lambda x: consolidate_mints(x))
	# print(data['Mint'].value_counts())
	# data = pd.get_dummies(data, prefix='is', columns=['Mint'], drop_first=True, dtype=np.int)
	#
	#data['mint_Lugdunum'] = data['Mint'].map(lambda x: True if 'Lugdunum' in x else False)
	#data['mint_Rome'] = data['Mint'].map(lambda x: True if 'Rome' in x else False)
	#data['mint_Patricia'] = data['Mint'].map(lambda x: True if 'Patricia' in x else False)
	#data['mint_Pergamum'] = data['Mint'].map(lambda x: True if 'Pergam' in x else False)
	#data['mint_Tarraco'] = data['Mint'].map(lambda x: True if 'Tarraco' in x else False)
	#data['mint_Caesaraugusta'] = data['Mint'].map(lambda x: True if 'Caesaraugusta' in x else False)
	#data['mint_Ephesus'] = data['Mint'].map(lambda x: True if 'Ephes' in x else False)
	#data['mint_Emerita'] = data['Mint'].map(lambda x: True if 'Emerita' in x else False)
	#data['mint_Spanish'] = data['Mint'].map(lambda x: True if 'Spanish' in x else False)
	#
	#data['known_mint'] = data['Mint'].map(lambda x: False if '?' in x else True)
	#
	data.drop(['Mint'], axis=1, inplace=True)

	# studied and no impact. Maybe try to isolate specific moneyers. worth it?
	#data['Moneyer'] = data['Moneyer'].astype(str)
	#data['has_Moneyer'] = data['Moneyer'].apply(lambda x: False if x=='nan' else True)
	data.drop(['Moneyer'], axis=1, inplace=True)

	# drop for now, but possibly predictive?
	data.drop(['Struck'], axis=1, inplace=True)

	# figure this out
	data.drop(['Obverse'], axis=1, inplace=True)

	# figure this out
	data.drop(['Reverse'], axis=1, inplace=True)

	# figure this out
	data.drop(['Inscriptions'], axis=1, inplace=True)

	# drop for now, but possibly predictive?
	data.drop(['RIC'], axis=1, inplace=True)

	# one hot encode 'Grade'
	data['Grade'] = data['Grade'].map(consolidate_grades)
	data = pd.get_dummies(data, prefix='is', columns=['Grade'], drop_first=True, dtype=np.int)

	# figure this out
	# do manual stemming/lemmatization for now
	data['Comments'] = data['Comments'].map(lambda x: x.lower())
	data['Comments'] = data['Comments'].map(correct_misspellings)
	#words = count_unique_words(data['Comments'])
	#print(words)

	# keywords: tone
	# ==============

	data['is_toned'] = data['Comments'].apply(lambda x: True if 'toned' in x.lower() else False)

	# studied and no impact
	data['is_lustrous'] = data['Comments'].apply(lambda x: bool(re.search(r'lustre|luster|lustrous', x.lower())))

	# studied and no impact
	#data['is_attractive'] = data['Comments'].apply(lambda x: True if 'attractive' in x.lower() else False)

	# studied and no impact
	#text = text.replace('grayish', 'gray')
	#text = text.replace('golden', 'gold')
	# covers grayish, golden
	#data['has_hue'] = data['Comments'].apply(lambda x: bool(re.search(r'irides|gray|gold|cabinet',x.lower())))

	#text = text.replace('iridescence', 'iridescent')
	data['is_iridescent'] = data['Comments'].apply(lambda x: True if 'iridescent' in x.lower() else False)

	# studied and no impact
	#data['is_gray'] = data['Comments'].apply(lambda x: True if 'gray' in x else False)

	# studied and no impact
	#data['is_golden'] = data['Comments'].apply(lambda x: True if 'gold' in x else False)

	#text = text.replace('darkly', 'dark')
	#data['is_dark'] = data['Comments'].apply(lambda x: True if 'dark' in x else False)

	data['is_cabinet_toned'] = data['Comments'].apply(lambda x: True if 'cabinet' in x else False)

	positive_words = ['wonderful', 'excellent', 'lovely', 'terrific', 'exceptional', 'extremely', 'artistic', 
	 	'beautiful', 'gorgeous', 'attractive', 'bold', 'excellent', 'amazing']
	data['has_positive_word'] = data['Comments'].apply(lambda x: any(pos_word in positive_words for pos_word in x.lower().split()))
	#data['has_positive_word'] = data['Comments'].apply(lambda x: 
	#	bool(re.search(r'wonderful|excellent|lovely|terrific|exceptional|extremely|artistic|beautiful|gorgeous|attractive|bold|excellent|amazing', x.lower())))

	# keywords: rarity
	# ================

	#data['is_rare'] = data['Comments'].apply(lambda x: True if 'rare' in x.lower() else False)
	data['is_rare'] = data['Comments'].apply(lambda x: bool(re.search(r'rare|scarse|scarce', x.lower())))

	data['is_very_rare'] = data['Comments'].apply(lambda x: bool(re.search(r'extremely rare|very rare|unique|coinArchives', x.lower())))

	# keywords: portrait
	# ================

	data['Comments'] = data['Comments'].str.replace('portraiture', 'portrait')

	portrait_keywords = ['eye', 'cheek', 'eyebrow', 'head', 'chin', 'forehead', 'jaw' ,'neck', 'nose']
	data['has_facial_features'] = data['Comments'].apply(lambda x: any(word in portrait_keywords for word in x.lower().split()))
	#data['has_facial_features'] = data['Comments'].apply(lambda x: bool(re.search(r'eye|cheek|eyebrow|head|chin|forehead|jaw|neck|nose', x.lower()))) # 1 match off?

	# studied and no impact, only 53 entries
	# data['portrait'] = data['Comments'].apply(lambda x:  True if 'portrait' in x.lower() else False)

	# studied and no impact, only 36 entries
	# data['has_nice_portrait'] = data['Comments'].apply(lambda x:
	# 	bool(re.search(r'(wonderful|bold|artistic|good|excellent|amazing|terrific|high relief) portrait', x.lower())))

	# studied and no impact
	# data['has_clean_portrait'] = data['Comments'].apply(lambda x: True if 'portrait' in x and not 'on portrait' in x else False)

	# # keywords: centering
	# =====================

	data['Comments'] = data['Comments'].str.replace('off center', 'off-center')
	data['Comments'] = data['Comments'].str.replace('well centered', 'well-centered')

	# studied and no impact
	#data['is_off_center'] = data['Comments'].apply(lambda x: True if 'off-center' in x else False)

	# studied and slight negative impact
	#data['is_on_center'] = data['Comments'].apply(lambda x: True if 'well-centered' in x else False)

	# # keywords: flan
	# ================

	data['Comments'] = data['Comments'].apply(flan_function)
	
	# studied and no impact
	#data['has_broad_flan'] = data['Comments'].apply(lambda x: True if 'broad-flan' in x else False)
	#data['has_compact_flan'] = data['Comments'].apply(lambda x: True if 'compact-flan' in x else False)
	#data['has_irregular_flan'] = data['Comments'].apply(lambda x: True if 'irregular-flan' in x else False)
	#data['has_wavy_flan'] = data['Comments'].apply(lambda x: True if 'wavy-flan' in x else False)

	#data['has_flan_crack'] = data['Comments'].apply(lambda x: True if 'flan-crack' in x else False)
	#data['has_flan_flaw'] = data['Comments'].apply(lambda x: True if 'flan-flaw' in x else False)

	# # keywords: die
	# ===============

	#data['Comments'] = data['Comments'].str.replace('die break', 'die-break')
	data['Comments'] = data['Comments'].str.replace('die shift', 'die-shift')
	#data['Comments'] = data['Comments'].str.replace('die rust', 'die-rust')
	#data['Comments'] = data['Comments'].str.replace('die flaw', 'die-flaw')

	# data['has_hairlines'] = data['Comments'].apply(lambda x: 
	# 	True if 'hairlines' in x else False)

	# studied and no impact
	#data['has_die_break'] = data['Comments'].apply(lambda x: True if 'die-break' in x else False)

	data['has_die_shift'] = data['Comments'].apply(lambda x: True if 'die-shift' in x else False) 

	# studied and no impact
	#data['has_die_rust'] = data['Comments'].apply(lambda x: True if 'die-rust' in x else False)

	# studied and no impact
	#data['has_die_flaw'] = data['Comments'].apply(lambda x: True if 'die-flaw' in x else False)

	# # keywords: surface features
	# ============================

	# # studied and no impact
	#data['surface'] = data['Comments'].apply(lambda x: True if 'surface' in x.lower() else False)
	
	# # studied and no impact
	#data['has_marks'] = data['Comments'].apply(lambda x: True if 'mark' in x else False)

	# # studied and no impact
	#data['has_banker_mark'] = data['Comments'].apply(lambda x: True if 'banker' in x else False)

	# # studied and small negative impact
	#data['has_deposits'] = data['Comments'].apply(lambda x: True if 'deposits' in x else False)

	# # studied and no impact
	# data['is_rough'] = data['Comments'].apply(lambda x: True if 'rough' in x else False)

	# # studied and no impact
	# data['is_smoothed'] = data['Comments'].apply(lambda x: True if 'smooth' in x else False) # only 40 in data

	#data['is_porous'] = data['Comments'].apply(lambda x: True if 'porous' in x.lower() else False)

	# # studied and slight negative impact
	#data['is_porous'] = data['Comments'].apply(lambda x: bool(re.search(r'porous|porosity', x.lower())))

	# # studied and slight negative impact
	#data['has_porosity'] = data['Comments'].apply(lambda x: True if 'porosity' in x.lower() else False)

	# data['is_corroded'] = data['Comments'].apply(lambda x: True if 'corroded' in x.lower() else False)
	
	# # studied and no impact
	# data['has_corrosion'] = data['Comments'].apply(lambda x: True if 'corrosion' in x.lower() else False)

	# # studied and no impact
	#data['is_granular'] = data['Comments'].apply(lambda x: True if 'granular' in x.lower() else False)

	# # studied and no impact
	#data['has_granularity'] = data['Comments'].apply(lambda x: True if 'granularity' in x.lower() else False)

	# # studied and no impact
	#data['is_pitted'] = data['Comments'].apply(lambda x: True if 'pitted' in x.lower() else False)

	# # studied and no impact
	#data['has_pitting'] = data['Comments'].apply(lambda x: True if 'pitting' in x.lower() else False)

	# # studied and slight negative impact
	#data['has_scratch'] = data['Comments'].apply(lambda x: True if 'scratch' in x else False)
	#data['has_scratch'] = data['Comments'].apply(lambda x: bool(re.search(r'scratch|scratched|scratches', x.lower())))

	# # studied and slight negative impact
	#data['has_scrape'] = data['Comments'].apply(lambda x: True if 'scrape' in x else False)
	# data['has_scrape'] = data['Comments'].apply(lambda x: bool(re.search(r'scrape|scraped|scrapes|scraping', x.lower())))

	# # studied and no impact
	#data['has_edge_test'] = data['Comments'].apply(lambda x: True if 'edge test cut' in x else False)

	# # studied and no impact
	#data['has_surface_test'] = data['Comments'].apply(lambda x: True if 'surface test cut' in x else False)

	# # studied and slight negative impact
	# data['has_splits'] = data['Comments'].apply(lambda x: True if 'split' in x else False)

	# # studied and no impact
	# data['has_pvc_residue'] = data['Comments'].apply(lambda x: True if 'pvc' in x else False)

	#data['has_strike'] = data['Comments'].apply(lambda x: bool(re.search(r'struck|strike|striking', x.lower())))

	# # studied and slight negative impact
	#data['has_flat_strike'] = data['Comments'].apply(lambda x: bool(re.search(r'flat strike', x.lower())))

	#data['has_chip'] = data['Comments'].apply(lambda x: bool(re.search(r'chip|chipping|chipped', x.lower())))

	# # studied and no impact
	#data['keyword_weak'] = data['Comments'].apply(lambda x: True if 'weak' in x else False)

	# # studied and no impact
	#data['is_cleaned'] = data['Comments'].apply(lambda x: bool(re.search(r'clean|cleaned|cleaning', x.lower())))

	# # studied and no impact
	# data['has_graffiti'] = data['Comments'].apply(lambda x: bool(re.search(r'graffito|graffiti', x.lower())))

	# # studied and no impact
	#data['keyword_deep'] = data['Comments'].apply(lambda x: True if 'deep' in x else False)

	# # studied and no impact
	#data['has_crystallization'] = data['Comments'].apply(lambda x: bool(re.search(r'crystalized|crystallization|crystallized', x.lower())))

	#data['keyword_reverse'] = data['Comments'].apply(lambda x: True if 'reverse' in x else False)

	data['keyword_obverse'] = data['Comments'].apply(lambda x: True if 'obverse' in x else False)

	# # studied and no impact
	# data['keyword_cut'] = data['Comments'].apply(lambda x: True if 'cut' in x else False)

	data.drop('Comments', axis=1, inplace=True)











	#extract key words from 'Imagery' field

	# data['is_travel_series'] = data['d2'].apply(lambda x: # highly predictive!
	# 	True if 'travel series' in x.lower() else False)

	# data['is_tribute_penny'] = data['d2'].apply(lambda x: 
	# 	True if 'tribute penny' in x.lower() else False) # same!

	# data['is_secular_games'] = data['d2'].apply(lambda x: 
	# 	True if 'secular games' in x.lower() \
	# 	or 'saeculares' in x.lower() else False) # somewhat

	# data['is_restitution'] = data['d2'].apply(lambda x: 
	# 	True if 'restitution' in x.lower() else False) # somewhat

	#keywords: place

	# data['has_Armenia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'armenia' in x.lower() else False) 

	# data['has_Germania'] = data['Imagery'].apply(lambda x: 
	# 	True if 'ger' in x.lower() else False) # GERMΛNICVS

	# data['has_Dacia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'dac' in x.lower() else False)

	# data['has_Egypt'] = data['Imagery'].apply(lambda x: 
	# 	True if 'egypt' in x.lower() else False)

	# data['has_Parthia'] = data['Imagery'].apply(lambda x: 
	# 	True if 'parth' in x.lower() else False)

	# keyword: military

	# data['has_capta'] = data['Imagery'].apply(lambda x:  # nice
	# 	True if 'capta' in x.lower() else False)

	# keyword: gods

	# data['has_jupiter'] = data['Imagery'].apply(lambda x:
	# 	True if 'jupiter' in x.lower() else False)

	# keywords: Rome

	# data['has_SPQR'] = data['Imagery'].apply(lambda x: # nice
	# 	True if 's • p • q • r' in x.lower() \
	# 	or 'spqr' in x.lower() \
	# 	else False) 








	#from nltk.stem.snowball import SnowballStemmer
	#stemmer = SnowballStemmer('english')
	#data['d3'] = data['d2'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))

	#vectorizer = TfidfVectorizer(stop_words='english', min_df=30) 

	#setting min_df=10 automatically defined the stop words as those below that threshold!
	#stop_words='english' # not sure if we WANT to exclude the standard stop words!
	
	# v2 = CountVectorizer(min_df=50)#, stop_words=comment_stops)
	# X2 = v2.fit_transform(data['Imagery'])
	# print('shape: {}'.format(X2.shape)) # (1268, ~92)
	# #print(X2)
	# #print(X2.toarray())
	# print('features: {}'.format(v2.get_feature_names()))
	#print('stop words: {}'.format(v2.stop_words_))
	# X2 = X2.toarray()


	print('FEATURE MATRIX: ')
	data.info()
	
	#Xb = data.to_numpy(float)
	Xb = data.values
	#Xb = data

	#from sklearn.pipeline import FeatureUnion
	#union = FeatureUnion([("pca", PCA(n_components=1)), ("svd", TruncatedSVD(n_components=2))])
	#>>> X = [[0., 1., 3], [2., 2., 5]]
	#>>> union.fit_transform(X)

	#data['index'] = data.index
	#print(data.info())
	#data_ct['index'] = data_ct.index
	#print(data_ct.info())
	#data.join(data_ct, index='index')

	# combine the baseline features with the language features
	X = Xb
	#X = np.hstack((Xb, X2))
	#X = np.hstack((Xb, X1, X2))
	
	print(X.shape)
	#print(X)

	# poly = PolynomialFeatures(degree=2, interaction_only=False)
	# X = poly.fit_transform(X)
	# print(X.shape)

	#data.info()

	# scale the data
	#scaler = StandardScaler()
	#scaler.fit(X)
	#print(scaler.mean_)
	#print(scaler.var_)
	#X = scaler.transform(X)
	#X = scaler.fit_transform(X)
	#print(X)

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

	scaler = StandardScaler()
	X_train = scaler.fit_transform(X_train)
	X_test = scaler.transform(X_test)

	# linear regression model with L2 regularization
	ridge = Ridge(random_state=42, max_iter=100000)
	# set grid search parameters
	alphas = np.logspace(-2, 3, 100)
	param_grid = {'alpha': alphas}
	n_folds = 5
	# perform grid search
	clf = GridSearchCV(ridge, param_grid, cv=n_folds, scoring='r2', n_jobs=-1, verbose=True)
	clf.fit(X_train, y_train)
	# results
	scores = clf.cv_results_['mean_test_score']
	print('xval r2: {}'.format(clf.best_score_))
	alpha = clf.best_params_['alpha']
	print('best alpha: {}'.format(alpha))

	# test model on unseen data
	model = Ridge(alpha=alpha, max_iter=1e8).fit(X_train, y_train)
	#print('coef: {}'.format(model.coef_))
	#print('intercept: {}'.format(model.intercept_))
	y_train_pred = model.predict(X_train)
	print('train r2: {}'.format(r2_score(y_train, y_train_pred)))
	#print('train rmse: {}'.format(np.sqrt(mean_squared_error(y_train, y_train_pred))))
	y_test_pred = model.predict(X_test)
	print('test r2: {}'.format(r2_score(y_test, y_test_pred)))
	#print('test rmse: {}'.format(np.sqrt(mean_squared_error(y_test, y_test_pred))))

	# linear regression model with L1 regularization
	ridge = Lasso(random_state=42, max_iter=100000)
	# set grid search parameters
	alphas = np.logspace(-5, -2, 100)
	param_grid = {'alpha': alphas}
	n_folds = 5
	# perform grid search
	clf = GridSearchCV(ridge, param_grid, cv=n_folds, scoring='r2', n_jobs=-1, verbose=True)
	clf.fit(X_train, y_train)
	# results
	scores = clf.cv_results_['mean_test_score']
	print('xval r2: {}'.format(clf.best_score_))
	alpha = clf.best_params_['alpha']
	print('best alpha: {}'.format(alpha))

	# test model on unseen data
	model = Lasso(alpha=alpha, max_iter=1e8).fit(X_train, y_train)
	#print('coef: {}'.format(model.coef_))
	#print('intercept: {}'.format(model.intercept_))
	#x = pd.DataFrame(zip(X.columns, model.coef_), columns=['feature', 'coefficient'])
	y_train_pred = model.predict(X_train)
	print('train r2: {}'.format(r2_score(y_train, y_train_pred)))
	#print('train rmse: {}'.format(np.sqrt(mean_squared_error(y_train, y_train_pred))))
	y_test_pred = model.predict(X_test)
	print('test r2: {}'.format(r2_score(y_test, y_test_pred)))
	#print('test rmse: {}'.format(np.sqrt(mean_squared_error(y_test, y_test_pred))))

	# how do our predictions compare to the test set values?
	#for y, yp in zip(y_test, y_test_pred):
	#	print(int(np.exp(y)), int(np.exp(yp)))

	# build standardized residuals (i.e. the "pulls")
	res_train_std = (y_train_pred - y_train)/np.std(y_train_pred - y_train)
	res_test_std = (y_test_pred - y_test)/np.std(y_test_pred - y_test)

	if(False):
		import matplotlib.pyplot as plt
		plt.scatter(y_train_pred, res_train_std, c = "blue", marker = "s", label = "Training data")
		plt.scatter(y_test_pred, res_test_std, c = "lightgreen", marker = "s", label = "Validation data")
		plt.title("Linear Regression")
		plt.xlabel("Predicted values")
		plt.ylabel("Standardized Residuals")
		plt.legend(loc = "upper left")
		plt.hlines(y = 0, xmin = 4, xmax = 13.5, color = 'red', alpha = 0.5)
		plt.xlim(4,12)
		plt.ylim(-5,5)
		plt.show()

	if(False):
		import matplotlib.pyplot as plt
		n, bins, _ = plt.hist(res_test_std, 50)
		plt.xlabel('Residuals')
		plt.ylabel('Counts')
		plt.title('Residuals')
		plt.grid(True)
		plt.show()






