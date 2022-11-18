import numpy as np
import mysql.connector

class AndGate:
    def __init__(self,NumberOfElement = 1000):
        self.NumberOfElement = NumberOfElement
        self.Xlen = 2
        self.Ylen = 1

    def And_Get(self):
        X_ = np.array(np.random.randint(0,high=2,size=(self.NumberOfElement, self.Xlen)),dtype='int')
        Y_ = np.zeros((self.NumberOfElement, self.Ylen),dtype='int')
        for count in range(len(X_)):
            if np.count_nonzero(X_[count] == 0) > 0:  
                Y_[count][0] = 0
            else:
                Y_[count][0] = 1
        return X_,Y_