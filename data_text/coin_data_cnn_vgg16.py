import numpy as np
import pandas as pd
import cv2
import os
import glob
import sys
from matplotlib import pyplot

import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Input, concatenate
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras import backend as K
from tensorflow.keras import losses
from tensorflow.keras import optimizers
from tensorflow.keras.applications.vgg16 import VGG16
#from tensorflow.keras.applications.resnet import ResNet50

# gpu run
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpu_devices[0], True)

def rmse(y_true, y_pred):
	return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))

def r2(y_true, y_pred):
	SS_res = K.sum(K.square(y_true - y_pred))
	SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
	return 1 - SS_res/(SS_tot + K.epsilon())

def load_image_data(loc, verbose=False):
	# load files into a single dataframe
	files = glob.glob(loc)
	#print(files)
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	data.info()
	# image model data fields
	X = data[['Image Path']]
	y = data['Sold']
	return X, y

def build_train_val_test_sets(X, y, train_size=0.60, val_size=0.20, random_state=42):
	# shuffle order of inputs to ensure reproducibility
	randomize = np.arange(X.shape[0])
	#print('randomized array shape: {}'.format(randomize.shape))
	np.random.seed(random_state)
	np.random.shuffle(randomize)
	#print('randomized array shape: {}'.format(randomize.shape))
	X = X.iloc[randomize]
	y = y.iloc[randomize]
	# break into training, validation, and test sets
	n_train = int(train_size * X.shape[0])
	#print(n_train)
	n_val = int(val_size * X.shape[0])
	#print(n_val)
	#n_test = int((1 - train_size - val_size) * X.shape[0])
	X_train, X_val, X_test = X.iloc[:n_train], X.iloc[n_train:n_train+n_val], X.iloc[n_train+n_val:]
	y_train, y_val, y_test = y.iloc[:n_train], y.iloc[n_train:n_train+n_val], y.iloc[n_train+n_val:]
	#print(n_train + n_val + n_test)
	return X_train, y_train, X_val, y_val, X_test, y_test

def prep_image_data(X, use_gray=False):
	# build feature matrix from image paths
	image_array = []
	for index, row in X.iterrows():
		print('reading image: {}'.format(index))
		# load image and get dimension
		img = cv2.imread(row['Image Path'])
		rows, cols, channels = img.shape
		print('original   ', img.shape)
		# convert to gray scale
		if use_gray:
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			print('gray       ', img.shape)
			#cv2.imshow('gray', img)
			#cv2.waitKey(0)
		else:
			# images are saved in RGB format, but cv2 reads them as BRG
			img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
			#cv2.imshow('RGB', img)
			#cv2.waitKey(0)
		# compute new dimensions for resized image
		maxrows = 128
		scale_percent = float(maxrows/rows) # percent of original size
		#print(scale_percent)
		width = int(img.shape[1] * scale_percent)
		height = int(img.shape[0] * scale_percent)
		dim = (width, height)
		# resize image
		img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
		print('resized    ', img.shape)
		#cv2.imshow('resized', img)
		#cv2.waitKey(0)
		# grab only obverse
		if use_gray:
			img1 = img[:, :img.shape[1]//2]
		else:
			img1 = img[:, :img.shape[1]//2, :]
		print('obverse    ', img1.shape)
		#cv2.imshow('obverse', img1)
		#cv2.waitKey(0)
		# resize obverse image
		img1 = cv2.resize(img1, (128, 128), interpolation=cv2.INTER_AREA)
		print('resized    ', img1.shape)
		#cv2.imshow('resized', img1)
		#cv2.waitKey(0)
		image_array.append(img1)
	# stack image array by row
	X = np.stack(image_array, axis=0)
	#print('X.shape: {}'.format(X.shape))
	# convert from integers to floats
	X = X.astype('float32')
	# normalize to range 0-1
	X = X / 255.0
	# return normalized images
	return np.array(X)

def prep_target(y):
	# transform target to be symmetric
	y = y.apply(lambda x: np.log1p(x))
	return np.array(y)

def summarize_diagnostics(history):
	# plot loss
	pyplot.subplot(211)
	pyplot.title('Mean Square Error Loss')
	pyplot.plot(history.history['loss'], color='blue', label='train')
	pyplot.plot(history.history['val_loss'], color='orange', label='test')
	pyplot.ylim(0, 2)
	# plot accuracy
	pyplot.subplot(212)
	pyplot.title('R-squared')
	pyplot.plot(history.history['r2'], color='blue', label='train')
	pyplot.plot(history.history['val_r2'], color='orange', label='test')
	pyplot.ylim(0, 1)
	# save plot to file
	filename = sys.argv[0].split('/')[-1]
	pyplot.savefig(filename + '_plot.png')
	pyplot.show()
	pyplot.close()

if __name__ == '__main__':


	# load image dataset
	location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Aug*/*prepared.csv'
	#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
	X, y = load_image_data(location)
	# split data into train, test sets
	X_train, y_train, X_val, y_val, X_test, y_test = build_train_val_test_sets(X, y)
	# prepare train, test data
	X_train = prep_image_data(X_train)
	X_val = prep_image_data(X_val)
	X_test = prep_image_data(X_test)
	y_train = prep_target(y_train)
	y_val = prep_target(y_val)
	y_test = prep_target(y_test)
	print('x_train shape:', X_train.shape)
	print('x_val shape:', X_val.shape)
	print('x_test shape:', X_test.shape)
	print('y_train shape:', y_train.shape)
	print('y_val shape:', y_val.shape)
	print('y_test shape:', y_test.shape)
	# init model without top classifier layers
	base_model = VGG16(include_top=False, input_shape=X_train.shape[1:])
	# mark loaded layers as not trainable
	for layer in base_model.layers:
		layer.trainable = False
	#base_model.summary()
	#print(base_model.layers[-1].output)
	# add new classifier layers
	x = Flatten()(base_model.layers[-1].output)
	#x = Dense(32, activation='relu')(x)
	#x = Dense(1024, activation='relu')(x)
	x = Dense(1, activation='linear')(x)
	# define new model
	model = Model(inputs=base_model.inputs, outputs=x)
	# compile new model
	#opt = optimizers.SGD(lr=0.005, momentum=0.0, nesterov=False)
	opt = optimizers.Adam(lr=0.0001)
	mse = losses.MeanSquaredError()
	model.compile(loss=mse, optimizer=opt, metrics=[r2, rmse])
	model.summary()
	# fit
	history = model.fit(X_train, y_train, 
		batch_size=32, 
		epochs=128, 
		verbose=1, 
		validation_data=(X_val, y_val)
	)
	# evaluate
	loss, r2, rmse = model.evaluate(X_test, y_test)
	print('Test loss: {}'.format(loss))
	print('Test R^2:  {}'.format(r2))
	print('Test RMSE: {}'.format(rmse))
	# learning curves
	summarize_diagnostics(history)