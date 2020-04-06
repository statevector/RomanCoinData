import numpy as np
import pandas as pd
import cv2
import os

import matplotlib.pyplot as plt
import ipdb

#import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D, MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras import backend

#from keras import losses
from keras import optimizers
#from keras.layers.normalization import BatchNormalization

def rmse(y_true, y_pred):
	return backend.sqrt(backend.mean(backend.square(y_pred - y_true), axis=-1))

if __name__ == '__main__':

	print('loading data...')
	inputs = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/'

	# make a list of CSV files present in directory
	all_files = [inputs+'/'+f for f in os.listdir(inputs) if '.csv' in f]
	print('There are {0:d} files in dir: {1:s}'.format(len(all_files), inputs))

	# load CSVs into dataframe
	data = pd.concat([pd.read_csv(f) for f in all_files], 
		axis=0, 
		ignore_index=True)

	data.dropna(axis=0, 
		subset=['Image', 'Rows', 'Columns', 'Channels'], 
		inplace=True)

	data['Rows'] = data['Rows'].astype(np.int)
	data['Columns'] = data['Columns'].astype(np.int)
	data['Channels'] = data['Channels'].astype(np.int)

	# remove non standard lots (temp)
	data = data.loc[data['Nonstandard Lot'] == False] 
	# weird shape at this index
	data[data['Rows']==197]
	
	# isolate image with most rows to define whitespace padding
	maxrows = data['Rows'].max()
	print('maxrows: {}'.format(maxrows))

	# check all image columns are the same size
	assert data['Columns'].value_counts().shape[0] == 1

	#halfcols = data['Columns'].max()//2
	#print('halfcols: {}'.format(halfcols))

	WHITE = [255, 255, 255]

	# build feature matrices for obverse and reverse images
	X1 = []
	X2 = []
	y = []
	for index, obs in data.iterrows():
		#if index > 30: continue
		print('transform image: {}'.format(index))
		# reconstruct original image array
		aaa = np.array(obs['Image'].split(), dtype=np.uint8) # uint8 for cv2
		aaa = aaa.reshape(obs['Rows'], obs['Columns'], obs['Channels'])
		print(aaa.shape)
		# convert from PIL BGR standard to open CV RGB standard
		img = cv2.cvtColor(aaa, cv2.COLOR_BGR2RGB)
		rows, cols, channels = img.shape
		print('rows {}, cols {}, channels {}'.format(rows, cols, channels))
		# pad the image to a consistent size to load into a dataframe
		#imgr = img[0:130, 0:cols, 0:channels]
		#imgr = cv2.resize(img, (130, cols), interpolation=cv2.INTER_AREA)
		top_pad = maxrows - rows # in pixels
		print(maxrows, rows, top_pad)
		imgr = cv2.copyMakeBorder(img, top_pad, 0, 0, 0, 
			cv2.BORDER_CONSTANT, 
			value=WHITE)
		#cv2.imshow('title', imgr)
		#cv2.waitKey(0)
		# grab obverse
		#ipdb.set_trace()
		imgr1 = imgr[:, :cols//2, :]
		X1.append(imgr1)
		print(imgr1.shape)
		#cv2.imshow('title', imgr1)
		#cv2.waitKey(0)
		# grab reverse
		imgr2 = imgr[:, cols//2:, :]
		X2.append(imgr2)
		print(imgr2.shape)
		#cv2.imshow('title', imgr2)
		#cv2.waitKey(0)
		y.append(obs['Sold'])
		print('-------------------------')

	# convert to numpy array and reshape for keras model

	X1 = np.stack(X1, axis=0)
	print('X1.shape: {}'.format(X1.shape))

	X2 = np.stack(X2, axis=0)
	print('X2.shape: {}'.format(X2.shape))

	y = np.array(y)
	print('y.shape: {}'.format(y.shape))



	# temp assign
	X = X1
	X2 = None


	# shuffle data ...
	randomize = np.arange(X.shape[0])
	print(randomize.shape)
	np.random.shuffle(randomize)
	X = X[randomize]
	y = y[randomize]

	# ... and break into training and test sets
	n_train = int(0.80 * X.shape[0])
	X_train, X_test = X[:n_train, :], X[n_train:, :]
	y_train, y_test = y[:n_train], y[n_train:]

	# convert to float and rescale for optimization
	X_train = X_train.astype('float32')
	X_train /= 255.

	X_test = X_test.astype('float32')
	X_test /= 255.
	
	print('x_train shape:', X_train.shape)
	print('x_test shape:', X_test.shape)
	print('y_train shape:', y_train.shape)
	print('y_test shape:', y_test.shape)

	# data augmentation
	datagen = ImageDataGenerator(
		#brightness_range=[0.9, 1.1],
		#featurewise_center=True,
	    #featurewise_std_normalization=True,
	    #zca_whitening=True,
	    rotation_range=10., # 20., # 90.,
	    width_shift_range=0.1, # 20% total width
	    height_shift_range=0.1, # 20% total height
	    horizontal_flip=True,
	    vertical_flip=False,
	    #shear_range=0.9,
	    #zoom_range=0.1, # 10%
	    fill_mode='constant'
	    #rescale=1./255)
	    )

	# compute quantities required for featurewise normalization
	train_datagen = datagen.fit(X_train)

	# plot a 3x3 grid of normalized images (sanity check)
	for i, (X_batch, y_batch) in enumerate(datagen.flow(X_train, y_train, batch_size=9)):
		#fig = plt.figure()
		print(i, X_batch.shape)
		for j, x in enumerate(X_batch):
			# subplot(nrows, ncols, index, **kwargs)
			plt.subplot(3, 3, j+1)
			plt.imshow(x)
		plt.show()
		if i>=4: 
			plt.close('all')
			break





	# flatten inputs for baseline tests
	X_train_b = X_train.reshape(len(X_train),-1)
	X_test_b = X_test.reshape(len(X_test),-1)

	# baseline model
	model = Sequential()
	model.add(Dense(32, activation='relu', input_shape = X_train_b.shape[1:]))
	model.add(Dropout(rate=0.5))
	model.add(Dense(16, activation='relu'))
	model.add(Dropout(rate=0.5))
	model.add(Dense(8, activation='relu'))
	model.add(Dropout(rate=0.5))
	model.add(Dense(4, activation='relu'))
	model.add(Dropout(rate=0.5))
	model.add(Dense(1)) # possible to add regularization
	sgd = optimizers.SGD(learning_rate=0.01, momentum=0.0, nesterov=False)

	model.compile(loss='mse', optimizer=sgd, metrics=['mae'])
	print(model.summary())
	history = model.fit(X_train_b, y_train, batch_size=128, epochs=1000, verbose=1, validation_data=(X_test_b, y_test))
	# score = model.evaluate(X_test, y_test, verbose=0)
	# print('Test loss:', score[0])
	# print('Test accuracy:', score[1])


	# CNN model
	# model = Sequential()
	# model.add(Conv2D(16, kernel_size=(5, 5), activation='relu', padding='same', 
	# 	input_shape=X.shape[1:]))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# model.add(Conv2D(16, kernel_size=(3, 3), activation='relu', padding='same'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# model.add(Conv2D(16, kernel_size=(3, 3), activation='relu', padding='same'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(Conv2D(16, kernel_size=(5, 5), activation='relu', padding='same'))
	# #model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(BatchNormalization())
	# model.add(Flatten())
	# model.add(Dense(16, activation='relu'))
	# model.add(Dropout(rate=0.5))
	# model.add(Dense(1)) # possible to add regularization

	# model.compile(loss='mse', optimizer='adam', metrics=['mae'])
	#print(model.summary())

	# # keras run parameters
	# batch_size = 64 # 1/100 the data
	# epochs = 10 # 31... seemed good

	# history = model.fit_generator(
	# 	datagen.flow(X_train, y_train, shuffle=True, batch_size=batch_size),
	# 	validation_data=(X_test, y_test),
	# 	steps_per_epoch=X_train.shape[0]//batch_size, 
	# 	epochs=epochs, 
	# 	use_multiprocessing=True, 
	# 	verbose=1)

	# score = model.evaluate(X_test, y_test, verbose=0)

	# print('Test loss:', score[0])
	# print('Test accuracy:', score[1])



