import numpy as np
import pandas as pd
import cv2
import os
import glob

import matplotlib.pyplot as plt
import ipdb

#from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import backend as K
from tensorflow.keras import losses
from tensorflow.keras import optimizers

# gpu run
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpu_devices[0], True)

def rmse(y_true, y_pred):
	return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))

def r2(y_true, y_pred):
	SS_res = K.sum(K.square(y_true - y_pred))
	SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
	return 1 - SS_res/(SS_tot + K.epsilon())

if __name__ == '__main__':


	files = glob.glob("/home/cwillis/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv")
	print(files)
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	#data = data[['Image Path', 'Sold']]
	#data.info()
	paths = data['Image Path'].values

	
	X = []
	y = []
	for idx, path in enumerate(paths):

		#if index > 30: continue
		print(path)

		# load image
		img = cv2.imread(path)
		rows, cols, channels = img.shape
		print('original   ', img.shape)

		# convert to gray scale
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		print('gray       ', img.shape)
		#cv2.imshow('gray', img)
		#cv2.waitKey(0)

		# resize image to consistent row-shape
		maxrows = 128
		scale_percent = float(maxrows/rows) # percent of original size
		#print(scale_percent)
		width = int(img.shape[1] * scale_percent)
		height = int(img.shape[0] * scale_percent)
		dim = (width, height)

		# resize image
		img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
		print('resized    ', img.shape)
		#cv2.imshow('resized', img)
		#cv2.waitKey(0)

		# grab obverse
		img1 = img[:, :img.shape[1]//2]
		print('obverse    ', img1.shape)
		#cv2.imshow('obverse', img1)
		#cv2.waitKey(0)

		# resize obverse image
		img1 = cv2.resize(img1, (128, 128), interpolation=cv2.INTER_AREA)
		print('resized    ', img1.shape)
		#cv2.imshow('resized', img1)
		#cv2.waitKey(0)

		X.append(img1)
		y.append(data['Sold'].iloc[idx])


	X = np.stack(X, axis=0)
	print('X.shape: {}'.format(X.shape))

	y = np.array(y)
	print('y.shape: {}'.format(y.shape))

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

	# NORMALIZE Y
	y_train = np.log(y_train)
	y_test = np.log(y_test)

	
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

	# make rank 4 tensors for datagen
	X_train = X_train.reshape((*X_train.shape,1))
	X_test = X_test.reshape((*X_test.shape,1))

	# compute quantities required for featurewise normalization
	train_datagen = datagen.fit(X_train)

	# plot a 3x3 grid of normalized images (sanity check)
	test_generator = False
	if(test_generator):
		for i, (X_batch, y_batch) in enumerate(datagen.flow(X_train, y_train, batch_size=9)):
			print('i=', i, X_batch.shape)
			for j, x in enumerate(X_batch):
				print('j=', j, x.shape)
				# subplot(nrows, ncols, index, **kwargs)
				plt.subplot(3, 3, j+1)
				x = x.reshape(128, 128)
				plt.imshow(x, cmap='gray', vmin=0, vmax=1)
			plt.show()
			if i>=4: 
				plt.close('all')
				break

	#quit()
	
	# flatten inputs for baseline tests
	# X_train_b = X_train.reshape(len(X_train),-1)
	# X_test_b = X_test.reshape(len(X_test),-1)

	# # baseline model
	# model = Sequential()
	# model.add(Dense(64, activation='relu', input_shape = X_train_b.shape[1:]))
	# #model.add(Dropout(rate=0.5))
	# model.add(Dense(32, activation='relu'))
	# #model.add(Dropout(rate=0.5))
	# model.add(Dense(16, activation='relu'))
	# #model.add(Dropout(rate=0.5))
	# model.add(Dense(8, activation='relu'))
	# #model.add(Dropout(rate=0.5))
	# model.add(Dense(4, activation='relu'))
	# model.add(Dense(1)) # possible to add regularization
	# sgd = optimizers.SGD(learning_rate=0.001, momentum=0.0, nesterov=False)
	# model.compile(loss='mae', optimizer=sgd, metrics=[r2, 'mae'])
	# print(model.summary())
	# history = model.fit(X_train_b, y_train, batch_size=128, epochs=1000, verbose=1, 
	# 	validation_data=(X_test_b, y_test))
	# score = model.evaluate(X_test_b, y_test, verbose=0)
	# print('Test loss:', score[0])
	# print('Test accuracy:', score[1])

	# CNN model
	model = Sequential()
	model.add(Conv2D(64, kernel_size=(3, 3), activation='relu', padding='same', 
	 	input_shape=X_train.shape[1:]))
	model.add(MaxPooling2D(pool_size=(3, 3)))
	model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', padding='same'))
	model.add(MaxPooling2D(pool_size=(3, 3)))
	#model.add(Conv2D(4, kernel_size=(3, 3), activation='relu', padding='same'))
	#model.add(MaxPooling2D(pool_size=(3, 3)))
	model.add(Flatten())
	model.add(Dense(64, activation='relu'))
	model.add(Dense(32, activation='relu'))
	#model.add(Dense(16, activation='relu'))
	#model.add(Dense(8, activation='relu'))
	#model.add(Dense(4, activation='relu'))
	model.add(Dense(1)) # possible to add regularization
	sgd = optimizers.SGD(learning_rate=0.0001, momentum=0.0, nesterov=False)
	adam = optimizers.Adam(learning_rate=0.0005)
	mse = losses.MeanSquaredError()
	print(adam)
	model.compile(loss=mse, optimizer=adam, metrics=[r2, rmse])
	print(model.summary())

	history = model.fit(X_train, y_train, batch_size=256, epochs=100, verbose=1, 
		validation_data=(X_test, y_test))

	# # keras run parameters
	# batch_size = 64 # 1/100 the data
	# epochs = 10 # 31... seemed good

	#history = model.fit_generator(
	#	datagen.flow(X_train, y_train, shuffle=True, batch_size=256),
	#	validation_data=(X_test, y_test),
	#	steps_per_epoch=X_train.shape[0]/32, 
	#	epochs=100, 
	#	use_multiprocessing=True, 
	#	verbose=1)

	# score = model.evaluate(X_test, y_test, verbose=0)
	# print('Test loss:', score[0])
	# print('Test accuracy:', score[1])
