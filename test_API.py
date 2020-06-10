import sock as consts
import socket
import threading
import struct
from mypipe import MyPipe
from DeepSpeech import DeepSpeech
import os
import sys
import time
test_try = sys.argv[1]
 
listen_event_signal = False
def send_cmd_to_sdk(cmd):
	speech_recog_end_pipe.write_to_pipe(cmd)
	return
def wait_for_keyword_detection():
	speech_recog_start_pipe.wait_on_pipe()
	return
		
def send_start_request():
#	print("Sendign start request from Megamind Text API")
#	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:	
#		s.connect( (consts.Host,consts.PortNumber_text_start_req) )
#		s.sendall("start".encode())
#		s.close()
#		return
	global pipe_start
	pipe_start.write_to_pipe('s')
	
def wait_for_listenning_thread(name):
	print('wait_for_listenning_thread')
	global listen_event_signal
	while True:
		wait_for_keyword_detection()
		listen_event_signal = True
		print("or type your cmd")
	#	while(listen_event_signal == True):
	#		pass

def record_cpu_usage(stat):
	f = open('/proc/stat','r')
	fout = open('/tmp/MegaCPU.txt','a')
	line = f.readline()
	print(line)
	words = line.split()
	if( stat == 'before'):	
		fout.write('stat, ')
		fout.write('user, ')
		fout.write('system, ')
		fout.write('idle \n')
	
	fout.write(stat)
	fout.write(', ')
	fout.write(words[1])
	fout.write(', ')
	fout.write(words[3])
	fout.write(', ')
	fout.write(words[4])
	fout.write('\n ')
	fout.close()
	f.close()


def main():
	print('Welcome to MegaMind Text API')
	global pipe_start 
	pipe_start =  MyPipe('text_start_request')
	pipe_start.make()
	global speech_recog_start_pipe
	speech_recog_start_pipe = MyPipe('speech_recog_start')
	global speech_recog_end_pipe
	speech_recog_end_pipe = MyPipe('speech_recog_end')
	os.system('rm /tmp/MegaCPU.txt')

	th1 = threading.Thread(target=wait_for_listenning_thread, args=(1,), daemon=True)
	th1.start()
	ds = DeepSpeech()
	testid = 'mixer'
	testno = 1
	total_tests = 3
	test_path_base = '/home/megamind/MegaMind/experiments/single_extention/'
	test_path = test_path_base + testid
	test_file_time = test_path + '/' + 'time_' + test_try + '.txt'
	test_file_cpu = test_path + '/' + 'cpu_' + test_try + '.txt'
	
	session_started = False
	global listen_event_signal
	while True:
#for blockers only
		if (testno > total_tests):
			time.sleep(7)
			record_cpu_usage('after')
			os.system('cp /tmp/MegsTST.txt ' + test_file_time)
			os.system('cp /tmp/MegaCPU.txt ' + test_file_cpu)
			os.system('python3.7 ' + test_path_base + 'parse.py ' + test_file_time)

		if( session_started == False):
			a = input("press 's' to start a new session...")
			if ( a == 's' and (len(a) == 1)):
				record_cpu_usage('before')
				send_start_request()
				session_started = True
		else:
			if( listen_event_signal == True):
			#	cmd = cmd.rstrip()
				if (testno > total_tests):
					cmd = 'stop'
					record_cpu_usage('after')
					os.system('cp /tmp/MegsTST.txt ' + test_file_time)
					os.system('cp /tmp/MegaCPU.txt ' + test_file_cpu)
					os.system('python3.7 ' + test_path_base + 'parse.py ' + test_file_time)
				else:
                                        time.sleep(3)
                                        cmd = ds.convert(testid , str(testno))
                                        if( testid == 'redact' or testid == 'multi'):
                                            if ('repeat'  not in cmd):
                                                 cmd = 'repeat ' + cmd
				testno += 1
				#cmd = a
				print('=======================================')
				print('Your command is:' + cmd + '\n')
				send_cmd_to_sdk(cmd)
				listen_event_signal = False

if __name__ == '__main__':
	main()
