import os
path = '/tmp/mysession/0/pipe_test.txt'
mode = 0o600


for j in range(0,4):
    os.mkfifo( path , mode)
    f = open(path, 'w')
    for i in range(0,3):
        a = input('write somtheing:\n')
        f.write(a)

    f.close()
    os.unlink(path)

