import os

path = 'pipe_test.txt' 


while True:
    f = open(path,'r')
    a = f.read()
    print(a) 
    f.close()

