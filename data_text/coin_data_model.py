
import numpy as np
import pandas as pd

from sklearn import base
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.feature_extraction.text import HashingVectorizer, CountVectorizer, TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error

#from sklearn.utils import shuffle
#from sklearn.model_selection import train_test_split
#from sklearn.metrics import mean_squared_error
#from sklearn.preprocessing import StandardScaler

import matplotlib.pyplot as plt

def count_unique_words(series):
	word_list = series.apply(lambda x: pd.value_counts(x.split(' '))).sum(axis = 0)
	return word_list.sort_values(ascending=False)

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

	data = pd.read_csv('/Users/cwillis/GitHub/RomanCoinData/data_text/data_prepared/Augustus.csv')
	print('data shape: {}'.format(data.shape))

	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('λ', 'a'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('avg', 'aug'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).replace('vs', 'us'))
	#data['d2'] = data['d2'].apply(lambda x: str(x).split())

	words = count_unique_words(data['Comments'])
	#print(words)

	# text formatting on the input data set
	#ttransformer = TextTransformer()
	#X = cts.fit_transform(data['Comments'])
	#print(X)

	# transform the data so its good
	#cts = ColumnSelectTransformer('Description')
	#data_cst = cts.fit_transform(data)
	#print(data_cst)

	#descriptions = data['Comments']
	#print(descriptions)
	#print(price)

	#from nltk.stem.snowball import SnowballStemmer
	#stemmer = SnowballStemmer('english')
	#data['d3'] = data['d2'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))

	#vectorizer = TfidfVectorizer(stop_words='english', min_df=30) 

	#vectorizer = CountVectorizer(stop_words='english')
	#vectorizer = CountVectorizer(min_df=30)
	vectorizer = CountVectorizer(min_df=10, stop_words='english')
	#vectorizer = CountVectorizer()

	X = vectorizer.fit_transform(data['Comments'])
	print(X.shape) # (1268, 88)
	#print(X)
	#print(X.toarray())
	print('feature names: {}'.format(vectorizer.get_feature_names()))
	# print(vectorizer.stop_words_)
	#quit()

	y = data['Sold']

	#clf = Ridge(alpha=1.0).fit(X, y)
	#print(clf)

	alphas = [0.0001, 0.001, 0.01, 0.1, 1, 5, 10, 50, 1e2, 5e2, 1e3, 5e3, 1e4, 5e4, 1e5]
	for alpha in alphas:
		est = Ridge(alpha=alpha)
		cv_score = cross_val_score(est, X, y, cv=5, scoring='r2')
		print('alpha: {}, cv score: {}'.format(alpha, cv_score.mean()))


	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

	#scaler = StandardScaler()
	#X_train = scaler.fit_transform(X_train)
	#X_test = scaler.transform(X_test)

	model = Ridge(alpha=100, max_iter=1e8).fit(X_train, y_train)
	#print('coef: {}'.format(model.coef_))
	#print('intercept: {}'.format(model.intercept_))

	y_train_pred = model.predict(X_train)
	y_test_pred = model.predict(X_test)
	print('mse: {}'.format(np.sqrt(mean_squared_error(y_test, y_test_pred))))

	#for x,y in zip(X_test, y_test):
	#	print(model.predict(x), y)

	plt.scatter(y_train_pred - y_train, y_train, c = "blue", marker = "s", label = "Training data")
	plt.scatter(y_test_pred - y_test, y_test, c = "lightgreen", marker = "s", label = "Validation data")
	plt.title("Linear Regression")
	plt.xlabel("Predicted values")
	plt.ylabel("Residuals")
	plt.legend(loc = "upper left")
	plt.hlines(y = 0, xmin = 10.5, xmax = 13.5, color = "red")
	plt.xlim(0,5000)
	plt.ylim(0,5000)
	plt.show()
















