import numpy as np
import mysql.connector

class MysqlConfigure:
    def __init__(self,input_len = 50,output_len = 10):
        self.mydb = mysql.connector.connect(host="localhost", user="root", password="ayesh")
        self.mycursor = self.mydb.cursor(buffered=True)
        self.input_len = input_len
        self.output_len = output_len
    
    def PushData(self,X,Y,Table_name):
        self.__createDatabase()
        self.__createTabale(Table_name)
        self.__Uplode_Data(X,Y,Table_name)

    def GetData(self,Table_name):
        self.mycursor.execute(f"SELECT Input, Output FROM {Table_name}")
        myresult = self.mycursor.fetchall()
        X_ = []
        Y_ = []
        for data in myresult:
            X = [int(i) for i in data[0].split()]
            Y = [int(i) for i in data[1].split()]
            X_.append(X)
            Y_.append(Y)
        return np.array(X_),np.array(Y_)

    def __createDatabase(self):
        self.mycursor.execute("SHOW DATABASES")
        for x in self.mycursor:
            if x[0] == "digital_functionality_duplication":
                break
        else:
            self.mycursor.execute("CREATE DATABASE digital_functionality_duplication")
        self.mydb = mysql.connector.connect(host="localhost", user="root", password="ayesh", database = "digital_functionality_duplication")
        self.mycursor = self.mydb.cursor(buffered=True)

    def __createTabale(self,Table_name):
        self.mycursor.execute("SHOW TABLES")
        for x in self.mycursor:
            if x[0] == f"{Table_name}":
                self.mycursor.execute(f"DROP TABLE {Table_name}")
                break
        self.mycursor.execute(f"CREATE TABLE {Table_name} (Number INT AUTO_INCREMENT PRIMARY KEY, Input VARCHAR(255), Output VARCHAR(255))")

    def __Uplode_Data(self,X_,Y_,Table_name):
        for i in range(len(X_)):
            x = X_[i]
            y = Y_[i]
            self.mycursor.execute(f"INSERT INTO {Table_name}(Input, Output) VALUES ('{self.__ArraytoSting(x,self.input_len)}', '{self.__ArraytoSting(y,self.output_len)}')")
            self.mydb.commit()
        
    def __ArraytoSting(self, ArrayofBinary,n):
        binarystring = ""
        for i in ArrayofBinary:
            binarystring += str(i) + " "
        return (binarystring + "0 "*(n-len(ArrayofBinary)))[:-1]

