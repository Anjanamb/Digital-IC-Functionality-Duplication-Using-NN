import os
import wandb
from wandb.keras import WandbCallback
import numpy as np
import tensorflow as tf
import datetime
from sklearn.model_selection import train_test_split
from tensorflow import keras
from keras.models import Sequential
from keras import initializers, optimizers
from keras.layers import InputLayer, Dense, LSTM, Dropout, BatchNormalization, LayerNormalization #GroupNormalization
from keras.callbacks import Callback, EarlyStopping, ReduceLROnPlateau

# For the purpose of omitting "WARNING:absl:Found untraced functions"
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)


class ResetStatesCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs=None):
        self.model.reset_states()
        print(" -> Resetting model states at end of epoch ", epoch)


# Read the dataset file and seperate inputs and outputs
def readFile(file, number_of_input):
    f1 = open(file, "r")
    X = []
    Y = []
    count = 1
    for line in f1:
        if count == 1:
            pass
        else: 
            items = [int(x.strip().replace("'", "")) for x in line.strip().split()] 
            X.append(items[:number_of_input])
            Y.append(items[number_of_input:])
        count += 1
    return X,Y


# Concatanate (n-1)th output to (n)th inputs
# New input ------> [ (n)th inputs + (n-1)th output ]
def intializeDataSet(X,Y):
    X_ = []
    Y_ = []
    for i in range(len(X)):
        if i == 0 and i == 1:
            pass
        else:
            X_.append([i for i in X[i]]+[i for i in Y[i-1]])
            Y_.append([i for i in Y[i]])
    return X_,Y_


# Dataset reshaping/ converting 2D input array to 3D array
# 3D array ------> [Samples, Time steps, Features]
def reArangeDataSet(X, Y, time_steps):
    Sequential_X = []
    Sequential_Y = Y[time_steps:]
    for i in range(len(X) - time_steps):
        Sequential_X.append(X[i:i + time_steps])
    Sequential_X = np.array(Sequential_X)
    Sequential_Y = np.array(Sequential_Y)
    return Sequential_X, Sequential_Y


# creating the NN model for training
def createModel(i_shape, b_size, Outputs, k_initializer, opt):
    # Define model architecture
    model = Sequential()
    model.add(InputLayer(input_shape=i_shape,batch_size=b_size))
    model.add(LSTM(32, activation='tanh', recurrent_activation='tanh',return_sequences=False,stateful=True,kernel_initializer=k_initializer,bias_initializer ='uniform',recurrent_initializer='Zeros',dropout=0.0,recurrent_dropout=0.1))
    # model.add(LSTM(8, activation='tanh', recurrent_activation='tanh',return_sequences=False,stateful=True,kernel_initializer=k_initializer,bias_initializer ='uniform',recurrent_initializer='Zeros',dropout=0.0,recurrent_dropout=0.0))
    # model.add(GroupNormalization())
    model.add(Dense(64, activation='tanh'))
    # model.add(BatchNormalization())
    model.add(Dense(64, activation='tanh'))
    # model.add(Dropout(0.2))
    # model.add(Dense(64, activation='elu'))
    # model.add(BatchNormalization())
    model.add(Dense(Outputs,activation='sigmoid'))
    model.summary()
    model.compile(loss='binary_crossentropy',optimizer=opt, metrics=['binary_accuracy'])
    
    # Define callbacks
    # add early stopping callback
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, verbose=1, mode='min', restore_best_weights=True)
    # add Reduce learning rate when a metric has stopped improving
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=2, mode="min", min_lr=0.00001)

    return model, early_stopping, reduce_lr


# creating the NN model for testing (with batch size = 1)
def newModel(i_shape, Outputs, k_initializer, opt, b_size=1):
    # Define model architecture
    model = Sequential()
    model.add(InputLayer(input_shape=i_shape,batch_size=b_size))
    model.add(LSTM(128, activation='tanh', recurrent_activation='tanh',return_sequences=True,stateful=True,kernel_initializer=k_initializer,bias_initializer ='uniform',recurrent_initializer='Zeros',dropout=0.0,recurrent_dropout=0.0))
    model.add(LSTM(128, activation='tanh', recurrent_activation='tanh',return_sequences=False,stateful=True,kernel_initializer=k_initializer,bias_initializer ='uniform',recurrent_initializer='Zeros',dropout=0.0,recurrent_dropout=0.0))
    # model.add(BatchNormalization())
    model.add(Dense(64, activation='tanh'))
    # model.add(BatchNormalization())
    model.add(Dense(Outputs,activation='sigmoid'))
    model.summary()
    model.compile(loss='binary_crossentropy',optimizer=opt, metrics=['binary_accuracy'])
    return model


# fit network / training
def trainModel(model, X_train, y_train, X_val, y_val, Epochs, b_size, early_stopping, reduce_lr):    
    model.fit(X_train, y_train, validation_data=(X_val, y_val), batch_size=b_size, epochs = Epochs, verbose=1, shuffle=False, callbacks=[WandbCallback(), ResetStatesCallback()]) # callbacks=[tensorboard_callback, early_stopping, reduce_lr, WandbCallback(), ResetStatesCallback])
    return model


# copy weights & compile the model
def copyWeights(model, newModel):
    old_weights = model.get_weights()
    newModel.set_weights(old_weights)
    newModel.compile(loss='binary_crossentropy', optimizer='rmsprop')


if __name__ == "__main__":

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'datasets/16BitShiftRegisterSIPO_random.txt')
    batch_size = 8192
    number_of_inputs = 2
    number_of_outputs = 16
    time_steps = 16
    epochs = 10
    lr = 0.01

    # optimizers
    # opt = optimizers.Adam(learning_rate=lr,weight_decay=0.0005,amsgrad=F,use_ema=True,ema_momentum=0.99)
    opt = optimizers.Adam(learning_rate=lr,decay=0.04)

    # weight initialize
    k_initializer= initializers.HeNormal(seed=20)#seed=20
    # k_initializer1=initializers.RandomUniform(minval=0.4, maxval=0.42, seed=2) 

    # Wandb
    wandb.init(project="final", entity="ic-functionality-duplication",
    config={
    "architecture": "LSTM1, Dense1, Dense2",
    "architecture_values": "32, 64, 64",
    "LSTM1": "32",
    "Dense1": "64",
    "Dense2": "64",
    "dropout": "LSTM1=(0.0, 0.1)",    
    "LSTM1_dropout": "0.0",
    "LSTM1_recurrent_dropout": "0.1",
    "Stateful": "True",
    "organized_input": "(i)th_input+(i-1)th_output",
    "organized_output": "(i)th_output",
    "organized_data": "[X(i)+Y(i-1)] & [Y(i)]",
    "Activation": "(tanh, recurrent=tanh), tanh",
    "Activation_LSTM1": "tanh, recurrent=tanh",
    "Activation_Dense": "tanh",
    "callbacks": "ResetStatesCallback",
    "dataset": "16-Bit-ShiftRegisterSIPO",
    "data_size": "train=1000000, val=100000",
    "batch_size": batch_size,
    "epochs": epochs,
    "learning_rate": lr,
    "optimizer": "Adam",
    "decay": 0.04,
    "initializer": "HeNormal",
    "time_steps": time_steps,
    })
    
    
    # Tensorboard
    # log_dir = "logs/fit/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    # tensorboard_callback = keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    # dataset preparation and then seperation for training & validation data
    X_train,Y_train = readFile(filename, number_of_inputs)
    X_train_, Y_train_ = intializeDataSet(X_train,Y_train)
    Sequential_X, Sequential_Y = reArangeDataSet(X_train_, Y_train_, time_steps)
    X_train, X_val, y_train, y_val = train_test_split(Sequential_X, Sequential_Y, test_size=0.2, random_state=42)
    X_train, X_val, y_train, y_val = X_train[len(X_train)%batch_size:], X_val[len(X_val)%batch_size:], y_train[len(y_train)%batch_size:], y_val[len(y_val)%batch_size:]
    
    # For debugging
    print("\n input_shape ",Sequential_X.shape,"\n")
    print("output_shape ",Sequential_Y.shape,"\n")

    model, early_stopping, reduce_lr = createModel(Sequential_X[0].shape, batch_size, number_of_outputs, k_initializer, opt)
    model = trainModel(model, X_train, y_train, X_val, y_val, epochs, batch_size, early_stopping, reduce_lr)

    # For wights & model
    # model.save('NN for testing/saved_model/my_model.hdf5')
    # model.save_weights('NN for testing/saved_model/my_model_weights.h5')


    # For debugging
    # print("\ninput_shape ",Sequential_X[0].shape,"\n")
    # print("output_shape ",Sequential_Y[0].shape,"\n")
    # print("inpt_3dArray_shape ",Sequential_X.shape,"\n")
    # print("output_3dArray_shape ",Sequential_Y.shape,"\n")
    # print("output_shape ",len(X_),"\n")
    # print("output_shape ",Y_.shape,"\n")Sequential_Y.shape
    # print("output_shape ",Sequential_X[0],"\n")