
import numpy as np
import pandas as pd

from sklearn import base
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer, TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor

#from sklearn.utils import shuffle
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error

pd.options.display.max_rows = 999
pd.set_option('display.width', 1000)

def count_unique_words(series):
	word_list = series.apply(lambda x: pd.value_counts(x.split(' '))).sum(axis = 0)
	return word_list.sort_values(ascending=False)

# this added 0.1 to model R^2 value!
def consolidate_grades(text):
	# Near Fine      5
	# Fine          72
	# Good Fine     26
	# Near VF      106
	# VF           511
	# Good VF      316
	# Near EF      104
	# EF           103
	# Superb EF     17
	# Choice EF      6
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
	return text

def stem_comments(text):
	text = text.lower()
	text = text.replace('lustre', 'lust')
	text = text.replace('luster', 'lust')
	text = text.replace('lustrous', 'lust')
	text = text.replace('toned', 'tone')
	text = text.replace('toning', 'tone')
	text = text.replace('attractively', 'attractive')
	text = text.replace('iridescence', 'iridescent')
	text = text.replace('iridescently', 'iridescent')
	text = text.replace('darkly', 'dark')
	text = text.replace('grayish', 'gray')
	text = text.replace('golden', 'gold')
	text = text.replace('portraiture', 'portrait')
	text = text.replace('centered', 'center')
	# but not marks --> mark or scratches --> scratch. probably info in the plural form.
	text = text.replace('roughness', 'rough')
	text = text.replace('tooled', 'tool')
	text = text.replace('tooling', 'tool')
	text = text.replace('smoothed', 'smooth')
	text = text.replace('smoothing', 'smooth')
	text = text.replace('corroded', 'corrosion')
	text = text.replace('porosity', 'porous')
	text = text.replace('granularity', 'granular')
	text = text.replace('pitting', 'pits')
	text = text.replace('pitted', 'pits')
	# 'cut' is implicit here; want to match with e.g. 'test cut on reverse/obverse'
	text = text.replace('edge test', 'edge test cut') 
	text = text.replace('surface test', 'surface test cut')
	text = text.replace('struck', 'strike')
	text = text.replace('banker’s', 'banker') # standardize apostrophes?
	text = text.replace('bankers’', 'banker')
	text = text.replace('bankers\'', 'banker')
	text = text.replace('cleaned', 'clean')
	text = text.replace('cleaning', 'clean')
	text = text.replace('off center', 'off-center')
	text = text.replace('lightly', 'light')
	# stop word studies
	text = text.replace('recently', 'recent')
	text = text.replace('scrapes', 'scratches')
	text = text.replace('scrape', 'scratch')
	text = text.replace('scraping', 'scratch')
	text = text.replace('scratched', 'scratches')
	text = text.replace('chipped', 'chip')
	text = text.replace('weakly', 'weak')
	text = text.replace('weakness', 'weak')
	text = text.replace('graffito', 'graffiti')
	text = text.replace('deeply', 'deep')

	text = text.replace('scarse', 'rare')

	text = text.replace('planchet', 'flan')
	#text = text.replace('flan flaw', 'flan-flaw')
	#text = text.replace('flan crack', 'flan-crack')
	#text = text.replace('die rust', 'die-rust')
	#text = text.replace('die break', 'die-break')

	# slightly --> slight --> minor
	# small vs. tiny vs. minor vs. slight vs. trivial, inconsequential, thin
	# wonderful, excellent, lovely, terrific, exceptional, extremely, artistic, beautiful, gorgeous
		
	return text

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

	# min/max df tests
	# cv = CountVectorizer(min_df=2, max_df=1.0, lowercase=True) 
	# # here is just a simple list of 3 documents.
	# corpus = ['one two three everywhere', 'four five six everywhere', 'seven eight nine everywhere']
	# # below we call fit_transform on the corpus and get the feature names.
	# X = cv.fit_transform(corpus)
	# vocab = cv.get_feature_names()
	# print(vocab)
	# print(X.toarray())
	# print(cv.stop_words_)

	data = pd.read_csv('/Users/cwillis/GitHub/RomanCoinData/data_text/data_prepared/Augustus_prepared.csv')
	#data = pd.read_csv('old/xxx3.csv')
	data.info()

	# save this for later
	data_nlp = data.copy(deep=True)

	# one hot encode 'Auction Type'
	data['is_Feature_Auction'] = data['Auction Type'].map(lambda x: True if 'Feature Auction' in x else False)
	data.drop(['Auction Type'], axis=1, inplace=True)

	# one hot encode 'Auction ID'
	data['is_Triton'] = data['Auction ID'].map(lambda x: True if 'Triton' in x else False)
	data.drop(['Auction ID'], axis=1, inplace=True)

	# non predictive
	data.drop(['Auction Lot'], axis=1, inplace=True)

	# highly predictive
	#data.drop(['Estimate'], axis=1, inplace=True)

	# non predictive
	data.drop(['Nonstandard Lot', 'Emperor', 'Reign', 'Struck', 'RIC'], axis=1, inplace=True)

	# one hot encode 'Denomination'
	data['is_Aureus'] = data['Denomination'].map(lambda x: True if 'Aureus' in x else False)
	data.drop(['Denomination'], axis=1, inplace=True)

	# do manual stemming/lemmatization for now
	data['Comments'] = data['Comments'].map(lambda x: x.lower())
	data['Comments'] = data['Comments'].map(stem_comments)
	#words = count_unique_words(data['Comments'])
	#print(words)
	data.drop(columns=['Comments'], axis=1, inplace=True)

	# do manual stemming/lemmatization for now
	data['Imagery'] = data['Imagery'].map(lambda x: x.lower())
	data['Imagery'] = data['Imagery'].map(stem_imagery)
	#words = count_unique_words(data['Imagery'])
	#print(words)
	data.drop(columns=['Imagery'], axis=1, inplace=True)

	# impute missing 'Diameter' measurements (not sure why these are 'NaN' and not 'None')
	diameter_mode = data['Diameter'].mode()[0]
	data['Diameter'] = data['Diameter'].map(lambda x: diameter_mode if np.isnan(x) else x) 

	# impute missing 'Weight' measurements
	weight_mode = data['Weight'].mode()[0]
	data['Weight'] = data['Weight'].map(lambda x: weight_mode if np.isnan(x) else x) 

	# assume die axis rotate left vs. rotate right has no effect on sale price
	#print(data['Hour'].value_counts())
	data['Hour'] = data['Hour'].map({1:11, 2:10, 3:9, 4:8, 5:7, 6:12})
	#print(data['Hour'].value_counts())

	# impute missing 'Hour' measurements
	hour_mode = data['Hour'].mode()[0]
	data['Hour'] = data['Hour'].map(lambda x: hour_mode if np.isnan(x) else x).astype(np.bool)
	
	# make 'Hour' categorical
	data = pd.get_dummies(data, prefix='is_Hour', columns=['Hour'], drop_first=True, dtype=np.bool) # drop true!
	#data.drop(['Hour'], axis=1, inplace=True)

	# non predictive
	data.drop(['MCase'], axis=1, inplace=True)

	# one hot encode 'Mint'
	#data.groupby('Mint').filter(lambda x: len(x)>10)
	#print(data['Mint'].value_counts())
	#data = pd.get_dummies(data, prefix='is', columns=['Mint'], drop_first=True, dtype=np.bool) # adds 0.02 to R^2
	data.drop(['Mint'], axis=1, inplace=True)

	#one hot encode 'Grade'
	#print(data['Grade'].value_counts())
	data['Grade'] = data['Grade'].map(consolidate_grades)
	data = pd.get_dummies(data, prefix='is', columns=['Grade'], drop_first=True, dtype=np.bool)

	# define the target vectors and log transform the target
	# np.log helps a lot!
	data['Sold'] = data['Sold'].map(lambda x: np.log1p(x))
	y = data['Sold'].values

	if(False):
		import matplotlib.pyplot as plt
		n, bins, _ = plt.hist(data['Sold'], 50)
		plt.xlabel('Log(Sale Price [USD])')
		plt.ylabel('Counts')
		plt.title('Histogram of Coins')
		#plt.xlim(40, 160)
		#plt.ylim(0, 0.03)
		plt.grid(True)
		plt.show()

	if(False):
		from scipy.stats import boxcox
		data = boxcox(data['Sold'], 0)
		plt.hist(data)
		plt.show()

	data.drop(['Sold'], axis=1, inplace=True)

	data.info()
	#quit()

	# add some features from 'Comments'
	
	# # keywords: tone
	# data['is_lustrous'] = data['Comments'].apply(lambda x: 
	# 	True if 'lust' in x else False)
	# data['is_toned'] = data['Comments'].apply(lambda x: 
	# 	True if 'tone' in x else False)
	# data['is_attractive'] = data['Comments'].apply(lambda x: 
	# 	True if 'attractive' in x else False)
	# data['is_iridescent'] = data['Comments'].apply(lambda x: 
	# 	True if 'iridescent' in x else False)
	# data['is_gray'] = data['Comments'].apply(lambda x: 
	# 	True if 'gray' in x else False)
	# data['is_golden'] = data['Comments'].apply(lambda x: 
	# 	True if 'gold' in x else False)
	# data['is_cabinet_toned'] = data['Comments'].apply(lambda x: 
	# 	True if 'cabinet' in x else False)

	# # keywords: rarity
	# data['is_rare'] = data['Comments'].apply(lambda x: 
	# 	True if 'rare' in x else False)
	# data['is_very_rare'] = data['Comments'].apply(lambda x: 
	# 	True if 'extremely rare' in x or 'very rare' in x or 'unique' in x else False)

	# # keywords: portrait

	# data['has_nice_portrait'] = data['Comments'].apply(lambda x: 
	# 	True if 'portrait' in x and not 'on portrait' in x else False)

	# data['has_problem_portrait'] = data['Comments'].apply(lambda x: 
	# 	True if 'on portrait' in x else False) # exclude scratches/marks/ etc on portrait

	# data['is_centered'] = data['Comments'].apply(lambda x: 
	# 	True if 'center' in x and not 'off-center' in x else False)

	# data['is_off_center'] = data['Comments'].apply(lambda x: 
	# 	True if 'off-center' in x else False)
	
	# # keywords: die, flan

	# data['has_broad_flan'] = data['Comments'].apply(lambda x:
	# 	True if ('broad flan' in x) and not ('flanking' in x) else False)

	# data['has_flan_crack'] = data['Comments'].apply(lambda x: 
	# 	True if 'flan-crack' in x else False)

	# data['has_flan_flaw'] = data['Comments'].apply(lambda x: 
	# 	True if 'flan-flaw' in x else False)

	# data['has_hairlines'] = data['Comments'].apply(lambda x: 
	# 	True if 'hairlines' in x else False)

	# data['has_die_break'] = data['Comments'].apply(lambda x: 
	# 	True if 'die-break' in x else False)

	# # keywords: surface flaws

	# data['has_surface_flaws'] = data['Comments'].apply(lambda x: 
	# 	True if 'surface flaws' in x else False)

	# data['has_marks'] = data['Comments'].apply(lambda x: 
	# 	True if 'mark' in x or 'marks' in x else False)
	
	# data['has_banker_mark'] = data['Comments'].apply(lambda x: 
	# 	True if 'banker' in x else False)

	# data['has_deposits'] = data['Comments'].apply(lambda x: 
	# 	True if 'deposits' in x else False)

	# data['is_rough'] = data['Comments'].apply(lambda x: 
	# 	True if 'rough' in x else False)

	# data['is_tooled'] = data['Comments'].apply(lambda x: 
	# 	True if 'tool' in x else False)

	# data['is_smoothed'] = data['Comments'].apply(lambda x: 
	# 	True if 'smooth' in x else False) # only 68 in data

	# data['has_die_rust'] = data['Comments'].apply(lambda x: 
	# 	True if 'die-rust' in x else False) # only 29 entries in data

	# data['has_porosity'] = data['Comments'].apply(lambda x: 
	# 	True if 'porous' in x else False)
	
	# data['has_scratch'] = data['Comments'].apply(lambda x: 
	# 	True if 'scratch' in x or 'scratches' in x else False) # 870... focus here
	
	# data['has_edge_test'] = data['Comments'].apply(lambda x: 
	# 	True if 'edge test cut' in x else False) # 29
	
	# data['has_test_cut'] = data['Comments'].apply(lambda x: 
	# 	True if 'test cut' in x else False) # 88

	# data['has_splits'] = data['Comments'].apply(lambda x: 
	# 	True if 'split' in x else False) # 43

	# data['has_pvc_residue'] = data['Comments'].apply(lambda x: 
	# 	True if 'pvc residue' in x else False) < 10

	# data['has_strike'] = data['Comments'].apply(lambda x: 
	# 	True if 'strike' in x else False) # 86

	# data['has_chip'] = data['Comments'].apply(lambda x: 
	# 	True if 'chip' in x else False) # 28







	#extract key words from 'Description' field

	# data['is_travel_series'] = data['d2'].apply(lambda x: # highly predictive!
	# 	True if 'travel series' in x.lower() else False)

	# data['is_tribute_penny'] = data['d2'].apply(lambda x: 
	# 	True if 'tribute penny' in x.lower() else False) # same!

	# data['is_secular_games'] = data['d2'].apply(lambda x: 
	# 	True if 'secular games' in x.lower() \
	# 	or 'saeculares' in x.lower() else False) # somewhat

	# data['is_restitution'] = data['d2'].apply(lambda x: 
	# 	True if 'restitution' in x.lower() else False) # somewhat

	#extract key words from 'Imagery' field

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





	#from sklearn.utils import shuffle
	#data = shuffle(data, random_state=422)
	#print(data.columns)


	# text formatting on the input data set
	#ttransformer = TextTransformer()
	#X = cts.fit_transform(data['Comments'])
	#print(X)

	# transform the data so its good
	#cts = ColumnSelectTransformer('Description')
	#data_cst = cts.fit_transform(data)
	#print(data_cst)

	#from nltk.stem.snowball import SnowballStemmer
	#stemmer = SnowballStemmer('english')
	#data['d3'] = data['d2'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))

	#vectorizer = TfidfVectorizer(stop_words='english', min_df=30) 

	#setting min_df=10 automatically defined the stop words as those below that threshold!
	#stop_words='english' # not sure if we WANT to exclude the standard stop words!
	


	# comment_stops = ['a', 'an', 'and', 'as', 'from', 'in', 'of', 'off', 'on', 'the', 'to', 'under', 'with']
	# v1 = CountVectorizer(min_df=50, stop_words=comment_stops)
	# X1 = v1.fit_transform(data['Comments'])
	# print('shape: {}'.format(X1.shape)) # (1268, ~92)
	# #print(X1)
	# #print(X1.toarray())
	# print('features: {}'.format(v1.get_feature_names()))
	# print(v1.stop_words_)
	# X1 = X1.toarray()

	# v2 = CountVectorizer(min_df=50, stop_words=comment_stops)
	# X2 = v2.fit_transform(data['Imagery'])
	# print('shape: {}'.format(X2.shape)) # (1268, ~92)
	# #print(X2)
	# #print(X2.toarray())
	# print('features: {}'.format(v2.get_feature_names()))
	# print(v2.stop_words_)
	# X2 = X2.toarray()


	
	Xb = data.values

	#data['index'] = data.index
	#print(data.info())
	#data_ct['index'] = data_ct.index
	#print(data_ct.info())
	#data.join(data_ct, index='index')

	# combine the baseline features with the language features
	#X = np.hstack((Xb, X1))
	#X = np.hstack((Xb, X1, X2))
	X = Xb
	print(X.shape)
	print(X)

	#poly = PolynomialFeatures(degree=2, interaction_only=False)
	#X = poly.fit_transform(X)
	#print(X.shape)

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

	alphas = [0.0001, 0.001, 0.01, 0.1, 1, 5, 10, 50, 1e2, 5e2, 1e3, 5e3, 1e4, 5e4, 1e5]
	for alpha in alphas:
		est = Ridge(alpha=alpha)
		cv_score = cross_val_score(est, X_train, y_train, cv=10, scoring='r2')
		print('alpha: {}, cv score: {}'.format(alpha, cv_score.mean()))

	
	#model = RandomForestRegressor(n_estimators=200, max_depth=20, max_features='auto').fit(X_train, y_train)
	#x = pd.DataFrame(zip(X.columns, model.feature_importances_), columns=['feature', 'import'])
	#pd.set_option('display.max_rows', None)
	##print(x.sort_values(by=['coefficient']))
	#print(x.sort_values(by=['import']))

	model = Ridge(alpha=5, max_iter=1e8).fit(X_train, y_train)
	#print('coef: {}'.format(model.coef_))
	#print('intercept: {}'.format(model.intercept_))

	#model = Lasso(alpha=0.0001, max_iter=1e8).fit(X_train, y_train)
	#print('coef: {}'.format(model.coef_))
	#print('intercept: {}'.format(model.intercept_))
	#x = pd.DataFrame(zip(X.columns, model.coef_), columns=['feature', 'coefficient'])
	
	y_train_pred = model.predict(X_train)
	print('train r2: {}'.format(r2_score(y_train, y_train_pred)))
	y_test_pred = model.predict(X_test)
	print('test r2: {}'.format(r2_score(y_test, y_test_pred)))
	#print('rmse: {}'.format(np.sqrt(mean_squared_error(y_test, y_test_pred))))
	
	#print(y_test[0:10])
	#print(y_test_pred[0:10])


	#for x,y in zip(X_test, y_test):
	#	print(model.predict(x), y)

	if(True):
		import matplotlib.pyplot as plt
		plt.scatter(y_train_pred, y_train_pred - y_train, c = "blue", marker = "s", label = "Training data")
		plt.scatter(y_test_pred, y_test_pred - y_test, c = "lightgreen", marker = "s", label = "Validation data")
		plt.title("Linear Regression")
		plt.xlabel("Predicted values")
		plt.ylabel("Residuals")
		plt.legend(loc = "upper left")
		plt.hlines(y = 0, xmin = 10.5, xmax = 13.5, color = "red")
		#plt.xlim(0,5000)
		#plt.ylim(0,5000)
		plt.show()





