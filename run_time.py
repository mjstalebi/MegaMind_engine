import os
print('MegaMind extention runtime')

f = open('/home/megamind/testfile.txt' , 'w')
f.write(' It is a test from runtime')

f = open ('in_use.txt' , 'r')
lines = f.readlines()
line = lines[0]

print("line = " + line)

while line == 'False' :			
	f.seek(0, 0)
	lines = f.readlines()
	if( len(lines) == 1):
		line = lines[0]

os.system('/bin/python3.7 action.py')
