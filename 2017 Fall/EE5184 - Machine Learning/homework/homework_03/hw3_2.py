import pandas as pd
from PIL import Image
import numpy as np
import keras
from math import floor

import random
from random import shuffle

from sklearn.model_selection import train_test_split

from keras import regularizers
from keras.callbacks import ModelCheckpoint
from keras.models import Sequential
from keras.models import Model, load_model
from keras.layers import Input, Dense, Dropout, Flatten, Activation, Reshape
from keras.layers.convolutional import Conv2D, ZeroPadding2D
from keras.layers.pooling import MaxPooling2D, AveragePooling2D
from keras.optimizers import SGD, Adam, Adadelta
from keras.preprocessing.image import ImageDataGenerator

import csv
from keras.utils import np_utils
import matplotlib.pyplot as plt

import time
import os

from keras.callbacks import EarlyStopping


os.system('echo $CUDA_VISIBLE_DEVICES')
#PATIENCE = 5 # The parameter is used for early stopping

def load(readnpy=True):
    if readnpy:
        y = np.load('./feature/DNNlabel.npy')
        X = np.load('./feature/DNNfeature.npy')
        X_test = np.load('./feature/DNNX_test.npy')
        
        X_train = np.load('./feature/DNNX_train.npy')
        X_valid = np.load('./feature/DNNX_valid.npy')
        y_train = np.load('./feature/DNNy_train.npy')
        y_valid = np.load('./feature/DNNy_valid.npy')        
    else :
        df_train = pd.read_csv('./feature/train.csv')
        
        '''train,valid data'''
        y = df_train['label'].as_matrix()
        print(df_train.groupby('label').count())
        y = y.reshape(len(y),1)
        
        X = df_train['feature'].as_matrix()
        X = np.array([np.array([*map(int, x.split())]) for x in X])
        np.save('./feature/DNNlabel.npy', y)
        np.save('./feature/DNNfeature.npy',X)
        
        X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.1, random_state=0)  
        
        np.save('./feature/DNNX_train.npy',X_train)
        np.save('./feature/DNNX_valid.npy',X_valid)
        np.save('./feature/DNNy_train.npy',y_train)
        np.save('./feature/DNNy_valid.npy',y_valid)
        
        '''testing data'''
        df_test = pd.read_csv('./feature/test.csv')
        X_test = df_test['feature'].as_matrix()
        X_test = np.array([np.array([*map(int, x.split())]) for x in X_test])
        np.save('./feature/DNNX_test.npy',X_test)
        
    return X,y,X_test,X_train,X_valid,y_train,y_valid


label_dict={0:"pissed off",1:"disgust",2:"fear",3:"happy",4:"sad",
            5:"surprised",6:"neutral"}


def plot_images_labels_prediction(images,labels,prediction,
                                  idx,num=20):
    fig = plt.gcf()
    fig.set_size_inches(12, 14)
    if num>25: num=25 
    for i in range(0, num):
        ax=plt.subplot(5,5, 1+i)
        ax.imshow(images[idx],cmap='binary')
                
        title=str(i)+','+label_dict[labels[i][0]]
        if len(prediction)>0:
            title+='=>'+label_dict[prediction[i]]
            
        ax.set_title(title,fontsize=10) 
        ax.set_xticks([]);ax.set_yticks([])        
        idx+=1 
    plt.show()

def normalize(X):
    X = X.astype('float32')
    X /=255
    return X

def OneHotEncode(y):
    #轉換label 為OneHot Encoding
    y = np_utils.to_categorical(y)
    #y = pd.get_dummies(y).values
    return y

def split_valid_set(X_all, Y_all, percentage):
    all_data_size = len(X_all)
    valid_data_size = int(floor(all_data_size * percentage))
    
    X_all, Y_all = _shuffle(X_all, Y_all)
    
    X_valid, Y_valid = X_all[0:valid_data_size], Y_all[0:valid_data_size]
    X_train, Y_train = X_all[valid_data_size:], Y_all[valid_data_size:]
    
    return X_train, Y_train, X_valid, Y_valid

def valid(X_all, Y_all):
    # Split a 10%-validation set from the training set
    valid_set_percentage = 0.1
    X_train, Y_train, X_valid, Y_valid = split_valid_set(X_all, Y_all, valid_set_percentage)
    return X_train, Y_train, X_valid, Y_valid

def _shuffle(X, Y):
    randomize = np.arange(len(X))
    np.random.shuffle(randomize)
    return (X[randomize], Y[randomize])

def buildmodel(X, Y):

    #X = X.reshape(len(X),48,48,1)
    model = Sequential()
    model.add(Dense(4096,input_dim=X.shape[1],
                         kernel_regularizer=regularizers.l2(0.001),
                         activation='relu'))
    model.add(Dense(4096,input_dim=X.shape[1],
                         kernel_regularizer=regularizers.l2(0.001),
                         activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2048,kernel_regularizer=regularizers.l2(0.001),
                         activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(2048, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(7, activation='softmax'))

    # opt = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
    opt = Adam(lr=1e-4)
    # opt = Adadelta(lr=0.1, rho=0.95, epsilon=1e-08)
    model.compile(loss='categorical_crossentropy', optimizer=opt, metrics=['accuracy'])
    model.summary()
    return model

def show_train_history(train_history,train,validation):
    plt.plot(train_history.history[train])
    plt.plot(train_history.history[validation])
    plt.title('Train History')
    plt.ylabel(train)
    plt.xlabel('Epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.show()
    
def prediction(model,X_test):
    prediction=model.predict_classes(X_test)
    print(prediction[:10])
    
def plot_images_labels_prediction(images,labels,prediction,
                                  idx,num=10):
    fig = plt.gcf()
    fig.set_size_inches(12, 14)
    if num>25: num=25 
    for i in range(0, num):
        ax=plt.subplot(5,5, 1+i)
        ax.imshow(images[idx],cmap='binary')
                
        title=str(i)+','+label_dict[labels[i][0]]
        if len(prediction)>0:
            title+='=>'+label_dict[prediction[i]]
            
        ax.set_title(title,fontsize=10) 
        ax.set_xticks([]);ax.set_yticks([])        
        idx+=1 
    plt.show()

def show_Predicted_Probability(y,prediction,
                               x_img,Predicted_Probability,i):
    print('label:',label_dict[y[i][0]],
          'predict:',label_dict[prediction[i]])
    plt.figure(figsize=(2,2))
    plt.imshow(np.reshape(x_img_test[i],(32, 32,3)))
    plt.show()
    for j in range(10):
        print(label_dict[j]+
              ' Probability:%1.9f'%(Predicted_Probability[i][j]))

#confusion matrix
def confusionmatrix():
    print(label_dict)
    pd.crosstab(y_test.reshape(-1),prediction,
            rownames=['label'],colnames=['predict'])

def savemodel(model,json=True,yaml=True,h5=True):
    if json:
        model_json = model.to_json()
        with open("SaveModel/cifarCnnModelDNN.json", "w") as json_file:
            json_file.write(model_json)
            print("save model as json file!")
    if yaml:
        model_yaml = model.to_yaml()
        with open("SaveModel/cifarCnnModelDNN.yaml", "w") as yaml_file:
            yaml_file.write(model_yaml)
            print("save model as yaml file!")
    if h5:      
        model.save_weights("SaveModel/cifarCnnModelDNN.h5")
        model.save('SaveModel/hw3-modelDNN.h5')
        print("save weight!")

def main():
    X_all,Y_all,X_test,X_train,X_valid,Y_train,Y_valid = load(True)
    
    #plot_images_labels_prediction(X_all,Y_all,[],0)
    
    X_all = normalize(X_all)
    X_test = normalize(X_test)
    Y_all = OneHotEncode(Y_all)
    
    X_train = normalize(X_train)
    X_valid = normalize(X_valid)
    Y_train = OneHotEncode(Y_train)
    Y_valid = OneHotEncode(Y_valid)

    
    batchsize = 64
    num_epoch = 100
    
    print(X_all.shape)
    print(Y_all.shape)
    print(X_test.shape)
    
    print(X_train.shape)
    print(X_valid.shape)

    print(Y_train.shape)
    print(Y_valid.shape)

    
    model = buildmodel(X_train,Y_train)
    print(model.summary())
    savemodel(model)
    
    
    ACCearlyStopping=EarlyStopping(monitor='val_acc',patience=50, verbose=0, mode='auto')
    
    filepath="weightDNN/weights-improvement-{epoch:02d}-{val_acc:.3f}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')

    train_history = model.fit(X_train, Y_train,validation_split=0.1,epochs=num_epoch, batch_size=batchsize,
        verbose=1,callbacks=[checkpoint,ACCearlyStopping])

    
    show_train_history(train_history,'acc','val_acc')
    show_train_history(train_history,'loss','val_loss')
    
    #評估模型準確率
    scores = model.evaluate(X_valid, Y_valid, verbose=1)
    print(scores[1])
    

    proba=model.predict(X_test)
    prediction = proba.argmax(axis=-1)
    
    answer = []
    for i in range(len(prediction)):
        answer.append([str(i)])
        answer[i].append(prediction[i])

    #filename = args[0][6]
    filename = "result/predictDNN.csv"
    
    text = open(filename, "w+")
    s = csv.writer(text,delimiter=',',lineterminator='\n')
    s.writerow(["id","label"])
    for i in range(len(answer)):
        s.writerow(answer[i])
    text.close()
    
    '''
    #plot_images_labels_prediction(X_test,y_test,prediction,0,10)
    #Predicted_Probability=model.predict(x_img_test_normalize)
    
    #show_Predicted_Probability(y_label_test,prediction,x_img_test,Predicted_Probability,0)
    #show_Predicted_Probability(y_label_test,prediction,x_img_test,Predicted_Probability,3)

    '''
if __name__ == '__main__':
    main()
