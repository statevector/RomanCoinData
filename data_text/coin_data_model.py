
import numpy as np
import pandas as pd

from sklearn import base
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.model_selection import cross_val_score

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

	data = pd.read_csv('/Users/cwillis/GitHub/RomanCoinData/data_text/data_prepared/Augustus.csv')
	print(data.shape)

	#ttransformer = TextTransformer('Description')
	#data_cst = cts.fit_transform(data)
	#print(data_cst)

	descriptions = data['Description']
	#print(descriptions)
	#print(price)

	hashing_vectorizer = HashingVectorizer()
	desc_hashed = hashing_vectorizer.fit_transform(descriptions)
	print(desc_hashed.shape)

	clf = Ridge(alpha=1.0).fit(desc_hashed, price)
	print(clf)

	alphas = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
	for alpha in alphas:
	    est = Ridge(alpha=alpha)
	    cv_score = cross_val_score(est, desc_hashed, price, cv=5)
	    print('alpha: {}, cv score: {}'.format(alpha, cv_score.mean())) 

	alphas = [0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1]
	for alpha in alphas:
	    est = Lasso(alpha=alpha)
	    cv_score = cross_val_score(est, desc_hashed, price, cv=5)
	    print('alpha: {}, cv score: {}'.format(alpha, cv_score.mean()))










