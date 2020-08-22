import numpy as np
import pandas as pd
import cv2
import os
import glob
import sys

from matplotlib import pyplot
import ipdb

#from tensorflow import keras
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Input, concatenate
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

def consolidate_grades(text):
	if 'Choice VF' in text:
		return 'Near EF'
	if 'Near Fine' in text:
		return 'Fine'
	if 'Superb EF' in text:
		return 'Good EF'
	if 'Choice EF' in text:
		return 'Good EF'
	if 'FDC' in text:
		return 'Good EF'
	return text

def load_text_data(loc, verbose=False):
	# load files into a single dataframe
	files = glob.glob(loc)
	#print(files)
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	data.info()
	# text model data fields
	X = data[['Auction Type', 'Estimate', 'Denomination', 'Diameter', 'Weight', 'Grade']]
	y = data['Sold']
	return X, y

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

def load_data(loc):
	# load files into a single dataframe
	files = glob.glob(loc)
	#print(files)
	data = pd.concat((pd.read_csv(f) for f in files), axis=0, sort=False, ignore_index=True) 
	data.info()
	# image model data fields
	X_image = data[['Image Path']]
	# text model data fields
	X_text = data[['Auction Type', 'Estimate', 'Denomination', 'Diameter', 'Weight', 'Grade']]
	y = data['Sold']
	return X_image, X_text, y

def build_train_test_sets(X, y, train_size=0.80, random_state=42):
	# shuffle order of inputs to ensure reproducibility
	randomize = np.arange(X.shape[0])
	#print('randomized array shape: {}'.format(randomize.shape))
	np.random.seed(random_state)
	np.random.shuffle(randomize)
	#print('randomized array shape: {}'.format(randomize.shape))
	X = X.iloc[randomize]
	y = y.iloc[randomize]
	# break into training and test sets
	n_train = int(train_size * X.shape[0])
	X_train, X_test = X.iloc[:n_train, :], X.iloc[n_train:, :]
	y_train, y_test = y.iloc[:n_train], y.iloc[n_train:]
	return X_train, y_train, X_test, y_test

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

def prep_text_data(X):
	# one hot encode 'Auction Type' and drop
	X['is_Feature_Auction'] = X['Auction Type'].map(lambda x: True if 'Feature Auction' in x else False)
	X.drop(['Auction Type'], axis=1, inplace=True)
	# transform estimate to be symmetric
	X['Estimate'] = X['Estimate'].map(lambda x: np.log1p(x))
	#X.drop(['Estimate'], axis=1, inplace=True)
	# impute missing 'Diameter' measurements
	diameter_map = X.groupby('Denomination')['Diameter'].transform(np.median)
	X['Diameter'] = X['Diameter'].fillna(diameter_map)
	# impute missing 'Weight' measurements
	weight_transformer = X.groupby('Denomination')['Weight'].transform(np.median)
	X['Weight'] = X['Weight'].fillna(weight_transformer)
	# one hot encode 'Denomination' and drop
	X['is_Aureus'] = X['Denomination'].map(lambda x: True if 'Aureus' in x else False)
	X['is_Denarius'] = X['Denomination'].map(lambda x: True if 'Denarius' in x else False)
	#X['is_Cistophorus'] = X['Denomination'].map(lambda x: True if 'Cistophorus' in x else False)
	X['is_Sestertius'] = X['Denomination'].map(lambda x: True if 'Sestertius' in x else False)
	X.drop(['Denomination'], axis=1, inplace=True)
	# one hot encode 'Grade' and drop
	X['Grade'] = X['Grade'].map(consolidate_grades) # consolidate Near Fine with Fine; Superb EF, Choice EF with Good EF
	X['is_Fine'] = X['Grade'].map(lambda x: True if 'Fine' in x else False)
	X['is_Good_Fine'] = X['Grade'].map(lambda x: True if 'Good Fine' in x else False)
	X['is_Near_VF'] = X['Grade'].map(lambda x: True if 'Near VF' in x else False)
	X['is_VF'] = X['Grade'].map(lambda x: True if 'VF' in x else False)
	X['is_Near_EF'] = X['Grade'].map(lambda x: True if 'Near EF' in x else False)
	X['is_EF'] = X['Grade'].map(lambda x: True if 'EF' in x else False)
	X['is_Good_EF'] = X['Grade'].map(lambda x: True if 'Good EF' in x else False)
	X.drop(['Grade'], axis=1, inplace=True)
	# print
	X = X.astype("float32")
	X.info()
	return np.array(X)

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

def define_combined_model(input_shapeA, input_shapeB):

	# define two sets of inputs
	inputA = Input(shape=input_shapeA)
	inputB = Input(shape=input_shapeB)
	print(input_shapeA)

	# the first branch operates on the first input
	#x = Dense(1, activation='relu')(inputA)
	#x = Dropout(rate=0.10)(x)
	#x = Dense(32, activation="relu")(x)
	#x = Dense(16, activation="relu")(x)
	#x = Dense(8, activation="relu")(x)
	#x = Dense(4, activation="relu")(x)
	#print(x.shape)
	#x = Model(inputs=inputA, outputs=x)
	#print(x)

	# # the second branch opreates on the second input
	# y = Conv2D(24, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(inputB)
	# y = MaxPooling2D(pool_size=(2, 2))(y)
	# y = Conv2D(48, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	# y = MaxPooling2D(pool_size=(2, 2))(y)
	# y = Conv2D(64, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	# y = MaxPooling2D(pool_size=(2, 2))(y)
	# y = Conv2D(80, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	# y = MaxPooling2D(pool_size=(2, 2))(y)
	# y = Conv2D(96, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	# y = MaxPooling2D(pool_size=(2, 2))(y)
	# y = Conv2D(112, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	# y = MaxPooling2D(pool_size=(4, 4))(y)
	# y = Flatten()(y)
	# print(y.shape)
	# y = Model(inputs=inputB, outputs=y)
	# #print(y)

	# the second branch opreates on the second input
	y = Conv2D(64, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(inputB)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(64, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(128, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(128, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(256, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(256, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(128, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = MaxPooling2D(pool_size=(2, 2))(y)
	y = Conv2D(1, kernel_size=(5, 5), activation='relu', strides=(1, 1), padding='same')(y)
	y = Flatten()(y)
	print(y.shape)
	y = Model(inputs=inputB, outputs=y)
	#print(y)
	# combine the output of the two branches
	combined = concatenate([inputA, y.output])
	print(combined.shape)
	#print(combined.shape)
	# apply FC layer and then a regression prediction on combined outputs
	z = Dense(32, activation='relu')(combined)
	#model.add(Dropout(rate=0.10))
	z = Dense(64, activation="relu")(z)
	#z = Dense(128, activation="relu")(z)
	#model.add(Dropout(rate=0.10))
	z = Dense(1, kernel_regularizer='l1')(z) #  activation='relu'
	# accept the inputs of the two branches and output a single value
	model = Model(inputs=[inputA, y.input], outputs=z)
	#opt = optimizers.SGD(learning_rate=0.0001, momentum=0.0, nesterov=False)
	opt = optimizers.Adam(learning_rate=0.01) # way too small 0.000005)
	mse = losses.MeanSquaredError()
	model.compile(loss=mse, optimizer=opt, metrics=[r2, rmse])
	return model


def define_text_model(input_shape):
	model = Sequential()
	model.add(Dense(64, activation='relu', input_shape=input_shape))
	#model.add(Dropout(rate=0.10))
	model.add(Dense(32, activation='relu'))
	#model.add(Dropout(rate=0.10))
	model.add(Dense(1))
	#opt = optimizers.SGD(lr=0.0001, momentum=0.0, nesterov=False)
	opt = optimizers.Adam(learning_rate=0.001)
	mse = losses.MeanSquaredError()
	model.compile(loss=mse, optimizer=opt, metrics=[r2, rmse])
	return model


def define_cnn_model(input_shape):
	model = Sequential()

	# model.add(Conv2D(24, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same', input_shape=input_shape))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(Dropout(rate=0.20))
	# model.add(Conv2D(48, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(Dropout(rate=0.20))
	# model.add(Conv2D(64, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(Dropout(rate=0.20))
	# model.add(Conv2D(64, kernel_size=(5, 5), strides=(1, 1), activation='relu', padding='same'))
	# model.add(MaxPooling2D(pool_size=(2, 2)))
	# #model.add(Dropout(rate=0.20))
	# model.add(Flatten())
	# model.add(Dense(32, activation='relu'))
	# model.add(Dense(64, activation='relu'))
	# model.add(Dense(1))#, kernel_regularizer='l1'))

	model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same', input_shape=input_shape))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	#model.add(Dropout(rate=0.10))
	model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	#model.add(Dropout(rate=0.10))
	model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	#model.add(Dropout(rate=0.10))
	model.add(Conv2D(64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	#model.add(Dropout(rate=0.10))
	model.add(Flatten())
	model.add(Dense(32, activation='relu'))
	model.add(Dense(64, activation='relu'))
	model.add(Dense(128, activation='relu'))
	#model.add(Dense(256, activation='relu'))
	model.add(Dense(1))#, kernel_regularizer='l2'))

	# compile model
	#opt = optimizers.SGD(lr=0.005, momentum=0.0, nesterov=False)
	opt = optimizers.Adam(lr=0.0001)
	mse = losses.MeanSquaredError()
	model.compile(loss=mse, optimizer=opt, metrics=[r2, rmse])
	return model


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

# data augmentation
def define_generator(X_train, use_gray=False):
	datagen = ImageDataGenerator(
		#brightness_range=[0.9, 1.1],
		#featurewise_center=True,
		#featurewise_std_normalization=True,
		#zca_whitening=True,
		rotation_range=20., # 20., # 90.,
		width_shift_range=0.2, # 20% total width
		height_shift_range=0.2, # 20% total height
		horizontal_flip=True,
		#vertical_flip=True,
		#shear_range=0.9,
		zoom_range=0.2, # 10%
		fill_mode='constant'
		#rescale=1./255)
	)
	# make rank 4 tensors for datagen fit
	if use_gray:
		X_train = X_train.reshape((*X_train.shape, 1))
		X_test = X_test.reshape((*X_test.shape, 1))
	# compute quantities required for featurewise normalization
	# (std, mean, and principal components if ZCA whitening is applied)
	datagen.fit(X_train)
	return datagen

# plot a set of augmented images to check the generator
def generate_examples(X_train, y_train, use_gray=False):
	# loop over batches
	for i, (X_batch, y_batch) in enumerate(datagen.flow(X_train, y_train, batch_size=9)):
		print('i=', i, X_batch.shape)
		# loop over individual images within the batch
		for j, x in enumerate(X_batch):
			print('j=', j, x.shape)
			# fill subplot with images
			pyplot.subplot(3, 3, j+1)
			if use_gray:
				x = x.reshape(128, 128) # for plotting
				pyplot.imshow(x, cmap='gray', vmin=0, vmax=1)
			else:
				x = x.reshape(128, 128, 3)
				pyplot.imshow(x)
		pyplot.show()
		# exit the loop after the third batch is processes
		if i>3: 
			pyplot.close('all')
			break




if __name__ == '__main__':

	# run text model
	if(False):
		# load text dataset
		location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		X, y = load_text_data(location)
		# split data into train, test sets
		X_train, y_train, X_test, y_test = build_train_test_sets(X, y)
		# prepare train, test data
		X_train = prep_text_data(X_train) # this should be a transformer class
		X_test = prep_text_data(X_test)
		y_train = prep_target(y_train)
		y_test = prep_target(y_test)
		# define text model
		input_shape = X_train.shape[1:]
		model = define_text_model(input_shape)
		model.summary()
		# fit model
		history = model.fit(X_train, y_train, 
			batch_size=128, 
			epochs=200, 
			verbose=1, 
			validation_data=(X_test, y_test)
		)
		# evaluate model
		loss, r2, rmse = model.evaluate(X_test, y_test)
		print('Test loss: {}'.format(loss))
		print('Test R^2:  {}'.format(r2))
		print('Test RMSE: {}'.format(rmse))
		# print learning curves
		summarize_diagnostics(history)


	# run image model
	if(False):
		# load image dataset
		location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Aug*/*prepared.csv'
		#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		X, y = load_image_data(location)
		# split data into train, test sets
		X_train, y_train, X_test, y_test = build_train_test_sets(X, y)
		# prepare train, test data
		X_train.shape
		X_train = prep_image_data(X_train) # this should be a transformer class
		X_test = prep_image_data(X_test)
		y_train = prep_target(y_train)
		y_test = prep_target(y_test)
		print('x_train shape:', X_train.shape)
		print('x_test shape:', X_test.shape)
		print('y_train shape:', y_train.shape)
		print('y_test shape:', y_test.shape)
		# define CNN model
		input_shape = X_train.shape[1:]
		model = define_cnn_model(input_shape)
		model.summary()
		# fit model
		history = model.fit(X_train, y_train, 
			batch_size=128, 
			epochs=300, 
			verbose=1, 
			validation_data=(X_test, y_test)
		)
		# evaluate model
		loss, r2, rmse = model.evaluate(X_test, y_test)
		print('Test loss: {}'.format(loss))
		print('Test R^2:  {}'.format(r2))
		print('Test RMSE: {}'.format(rmse))
		# print learning curves
		summarize_diagnostics(history)


	# run image model using dedicated test set
	if(True):
		# load image dataset
		location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Aug*/*prepared.csv'
		#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		X, y = load_image_data(location)
		print(X.shape)
		# split data into train, test sets
		X_train, y_train, X_val, y_val, X_test, y_test = build_train_val_test_sets(X, y)
		#print(X_train.shape)
		#print(X_val.shape)
		#print(X_test.shape)
		#quit()
		# prepare train, test data
		X_train = prep_image_data(X_train) # this should be a transformer class
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
		# define CNN model
		input_shape = X_train.shape[1:]
		model = define_cnn_model(input_shape)
		model.summary()
		# fit model
		history = model.fit(X_train, y_train, 
			batch_size=96, 
			epochs=128, 
			verbose=1, 
			validation_data=(X_val, y_val)
		)
		# evaluate model
		loss, r2, rmse = model.evaluate(X_test, y_test)
		print('Test loss: {}'.format(loss))
		print('Test R^2:  {}'.format(r2))
		print('Test RMSE: {}'.format(rmse))
		# print learning curves
		summarize_diagnostics(history)


	# run image model with data augmentation
	if(False):
		# load image dataset
		location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		X, y = load_image_data(location)
		# split data into train, test sets
		X_train, y_train, X_test, y_test = build_train_test_sets(X, y)
		# prepare train, test data
		X_train.shape
		X_train = prep_image_data(X_train) # this should be a transformer class
		X_test = prep_image_data(X_test)
		y_train = prep_target(y_train)
		y_test = prep_target(y_test)
		print('x_train shape:', X_train.shape)
		print('x_test shape:', X_test.shape)
		print('y_train shape:', y_train.shape)
		print('y_test shape:', y_test.shape)
		# define CNN model
		input_shape = X_train.shape[1:]
		model = define_cnn_model(input_shape)
		# define and fit data generator
		datagen = define_generator(X_train)
		# plot augmented images
		generate_examples(X_train, y_train)
		#valgen = ImageDataGenerator()
		model.summary()
		# fit model using data generator
		history = model.fit_generator(
			datagen.flow(X_train, y_train, 
				shuffle=True, 
				batch_size=128
			),
			validation_data=(X_test, y_test),
			steps_per_epoch=X_train.shape[0]/128, 
			epochs=300, 
			verbose=1
		)
		# evaluate model
		loss, r2, rmse = model.evaluate(X_test, y_test)
		print('Test loss: {}'.format(loss))
		print('Test R^2:  {}'.format(r2))
		print('Test RMSE: {}'.format(rmse))
		# print learning curves
		summarize_diagnostics(history)


	# run combined model
	if(False):

		# load dataset
		location = '/home/cwillis/RomanCoinData/data_text/data_scraped/Augustus*/*prepared.csv'
		#location = '/Users/cwillis/GitHub/RomanCoinData/data_text/data_scraped/Nero*/*prepared.csv'
		X_image, X_text, y = load_data(location)

		assert(X_image.shape[0] == X_text.shape[0])
		assert(X_image.shape[0] == y.shape[0])

		# split data into train, test sets
		# shuffle order of inputs to ensure reproducibility
		randomize = np.arange(X_image.shape[0])
		np.random.seed(42)
		np.random.shuffle(randomize)
		# break into training and test sets
		train_size = 0.80
		n_train = int(train_size * X_image.shape[0])
		#
		X_image = X_image.iloc[randomize]
		Xi_train, Xi_test = X_image.iloc[:n_train, :], X_image.iloc[n_train:, :]
		#
		X_text = X_text.iloc[randomize]
		Xt_train, Xt_test = X_text.iloc[:n_train, :], X_text.iloc[n_train:, :]
		#
		y = y.iloc[randomize]
		y_train, y_test = y.iloc[:n_train], y.iloc[n_train:]

		# prepare train, test data
		Xi_train = prep_image_data(Xi_train)
		Xi_test = prep_image_data(Xi_test)
		
		Xt_train = prep_text_data(Xt_train)
		Xt_test = prep_text_data(Xt_test)

		y_train = prep_target(y_train)
		y_test = prep_target(y_test)

		# define text model
		input_shapeA = Xt_train.shape[1:]
		input_shapeB = Xi_train.shape[1:]
		model = define_combined_model(input_shapeA, input_shapeB)
		model.summary()

		# fit model
		history = model.fit([Xt_train, Xi_train], y_train, 
			batch_size=128, 
			epochs=100, 
			verbose=1, 
			validation_data=([Xt_test, Xi_test], y_test)
		)
		
		# evaluate model
		loss, r2, rmse = model.evaluate([Xt_test, Xi_test], y_test)
		print('Test loss: {}'.format(loss))
		print('Test R^2:  {}'.format(r2))
		print('Test RMSE: {}'.format(rmse))
		
		# print learning curves
		summarize_diagnostics(history)


