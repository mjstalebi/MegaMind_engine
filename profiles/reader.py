import os

path = '/tmp/mysession/0/pipe_test.txt'


while True:
    f = open(path,'r')
    a = f.read()
    print(a) 
    f.close()

