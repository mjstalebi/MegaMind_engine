import sock as consts
import socket
import threading
import struct
import json
import time
from Session import Session
#from Session import debug_log
from Session import Extension
from bcolors import bcolors
from Sandbox import Sandbox
from Sandbox import Sandbox_pool

port_start_speech = consts.PortNumber_start_speech_2
port_end_speech = consts.PortNumber_end_speech_2
session_in_progress = False


state = "idle"
start_session_signal = False
end_session_signal = False
listen_event_signal = False
recieved_response_signal = False
end_session_signal = False
first_req_of_session = False

def debug_log(*args, **kwargs):
#    print( "YYY "+" ".join(map(str,args))+" YYY", **kwargs)
	return

def wait_for_start_session_notice():
	wait_on_port(consts.PortNumber_start_session_notice)

def wait_for_end_session_notice():
	wait_on_port(consts.PortNumber_end_session_notice)

def wait_for_keyword_detection():
	wait_on_port(consts.PortNumber_start)
	return

def wait_on_port(PortNum):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind( (consts.Host,PortNum) )
		s.listen()
		conn, addr = s.accept()
		with conn:
			data= conn.recv(1024)
			conn.close()
			s.close()
			return
	

def wait_for_payload():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind( (consts.Host,consts.PortNumber_alexa_response) )
		s.listen()
		conn,addr = s.accept()
		with conn:
			#timeval = struct.pack('ll',1,0)
			#conn.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
			data = conn.recv(4096)
			conn.close()
			s.close()
			return data.decode()

def wait_for_speech_recognition_done():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
		s.bind( (consts.Host,port_end_speech) )
		s.listen()
		conn,addr = s.accept()
		with conn:
			data = conn.recv(4096)
			cmd = data.decode()
			cmd.replace('.','')
			cmd.replace('?','')
			cmd.replace('!','')
			conn.close()
			s.close()
			return cmd
def send_cmd_to_sdk(cmd):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:	
		s.connect( (consts.Host,consts.PortNumber_MegaMindEngine) )
		s.sendall(cmd.encode())
		s.close()
		return


def start_speech_recognition():	
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:	
		s.connect( (consts.Host,port_start_speech) )
		s.sendall("start".encode())
		s.close()
		return

def payload_thread(name):
	print('payload start')
	global recieved_response_signal
	global current_session
	global extensions
	global extensions_resp_order
	global active_extensions
	global sandbox_pool 
	while True:
	#	print('before wait_for_payload')
		payload = wait_for_payload()
		tokens = payload.split('"')
	#	print('after wait_for_payload')
	#	print('Payload is= ' + payload)	
	#	print('tokens = ')
	#	print(tokens)
		caption = ' caption not found'
		token_id = 'token not found'
		for i in range(1,len(tokens)):
			if(tokens[i] == 'caption'):
				caption = tokens[i+2]
			if(tokens[i] == 'token'):
				token_id = tokens[i+2]
		print( ' caption = ' + bcolors.OKBLUE + caption + bcolors.ENDC )
		#print( ' token = ' + token_id )
		current_session.responses.insert_new(caption)
		recieved_response_signal = True
		log_time('response recieved from sdk' )
		for ext in extensions_resp_order:
			if ext not in active_extensions:
				#print("evaluate: " , ext.name)
				if(ext.evaluate(current_session)):
					#print("extension: " + ext.name  +" is true")
					active_extensions.append(ext)
					ext.sandbox = sandbox_pool.get_idle_sandbox()
					ext.sandbox.execute(ext.script)
		log_time('before resp action' )
		for ext in extensions_resp_order:
		#for ext in active_extensions:
			if ext in active_extensions:
				#print(" RESP: we need to forward session to extenstion " + ext.name )
				session_dict = current_session.get_dictionary()
				session_dict['req_resp'] = 'resp'
				ext.sandbox.transfer_data(json.dumps(session_dict))
				ext.sandbox.wait_for_response()
				new_caption = ext.sandbox.get_response()
				if( ext.verify_new_cmd(new_caption)):
					caption = new_caption
		#print( ' new caption = ' + bcolors.OKBLUE + caption + bcolors.ENDC )
		log_time('+++++++++ command end+++++++++')
		#while (recieved_response_signal == True):
		#	pass
			



def wait_for_listenning_thread(name):
	print('wait_for_listenning_thread')
	global listen_event_signal
	while True:
		wait_for_keyword_detection()
		listen_event_signal = True
		while(listen_event_signal == True):
			pass
		
def start_session_notice_thread(name):
	print("start_session_notice_thread")
	while True:
		wait_for_start_session_notice()
		print("start_session_notice recieved")
		if ( state == "idle"):
			start_session()
		else:
			end_session()
			while( state != "idle"):
				pass
			start_session()
	return

		
def end_session_notice_thread(name):
	print("end_session_notice_thread")
	while True:
		wait_for_end_session_notice()
		if (( state == "wait_for_listenning") or ( state == "wait_for_response") ):
			end_session()
		else:
			print("somthing is wrong!!")
	return

def start_session():
	global start_session_signal
	global first_req_of_session
	global current_session
	current_session = Session()
	current_session.speaker_id = 'Mohammad'
	start_session_signal = True
	print(bcolors.FAIL + "*************NEW SESSION****************"+ bcolors.ENDC)
	log_time("__________ Session Started __________")
	first_req_of_session = True
	while (start_session_signal == True):
		pass
	return

def end_session():
	global end_session_signal
	global current_session
	global active_extensions
	for ext in active_extensions:
		ext.sandbox.destroy_and_replace()
	active_extensions = []
	end_session_signal = True
	
	print(bcolors.FAIL + "*************SESSION ENDS****************"+ bcolors.ENDC)
	log_time("__________ Session End __________")
	print(current_session.get_dictionary())
	while (end_session_signal == True):
		pass
	return

def local_skill_id_finder(cmd):
	if 'open' in cmd:
		return cmd.replace('open ','')
	else:
		return "built-in"
def get_user_cmd_and_send_it():
	global first_req_of_session
	global current_session
	global extensions
	global active_extensions
	global sandbox_pool 
	start_speech_recognition()
	cmd = wait_for_speech_recognition_done()
	cmd = cmd.rstrip()
	print('=======================================')
	print(  ' Your command is:' + bcolors.OKGREEN  + cmd + '\n' + bcolors.ENDC )
	cmd = cmd.replace(',','')
	cmd = cmd.replace('.','')
	cmd = cmd.replace('!','')
	cmd = cmd.replace('?','')
	cmd = cmd.lower()
	log_time('+++++++++ command started+++++++++')
	if(first_req_of_session == True):
		#print( bcolors.FAIL +" first req of session call local skill_id finder" + bcolors.ENDC)
		first_req_of_session = False
		skill_id = local_skill_id_finder(cmd)
		current_session.skill_id = skill_id
	current_session.requests.insert_new(cmd)
	log_time('local session detection done')
	if (cmd != 'stop' ):
		for ext in extensions:
			if ext not in active_extensions:
				#print("evaluate: " , ext.name)
				if(ext.evaluate(current_session)):
					#print("extension: " + ext.name  +" is true")
					active_extensions.append(ext)
					ext.sandbox = sandbox_pool.get_idle_sandbox()
					ext.sandbox.execute(ext.script)
#		for ext in extensions:
#			if ext  in active_extensions:
#				print("REQ: we need to forward session to extenstion " + ext.name )
#				session_dict = current_session.get_dictionary()
#				session_dict['req_resp'] = 'req'
#				ext.sandbox.transfer_data(json.dumps(session_dict))
#				ext.sandbox.wait_for_response()
#				new_cmd = ext.sandbox.get_response()
#				if( ext.verify_new_cmd(new_cmd)):
#					cmd = new_cmd
			
		log_time('trigger rule req done')
		for ext in active_extensions:
			#print("REQ: we need to forward session to extenstion " + ext.name )
			session_dict = current_session.get_dictionary()
			session_dict['req_resp'] = 'req'
			ext.sandbox.transfer_data(json.dumps(session_dict))
			ext.sandbox.wait_for_response()
			new_cmd = ext.sandbox.get_response()
			if( ext.verify_new_cmd(new_cmd)):
				cmd = new_cmd
			
		log_time('extention exec done')
		
	send_cmd_to_sdk(cmd)
	log_time('cmd_sent_to_sdk' )
		
	
	
	
	return
def log_time(mystr):
	global test_file
	milliseconds = int(round(time.time() * 1000)) 
	#test_file.write(str(milliseconds) + '\t' + mystr +'\n')
	test_file.write( mystr + '\t'+str(milliseconds)  + '\n')
	test_file.flush()
	return
def main():
	print('Welcome to MegaMind Engine')
	
	print('Initializing trigers')
	global extensions
	global extensions_resp_order
	extensions = []
	extensions_resp_order = []
	global active_extensions
	active_extensions = []
#	extensions.append(Extension('parental','./JSONs/parental.json' , './scripts/parental.py'))
#	extensions.append(Extension('redact','./JSONs/redact.json' , './scripts/redact.py'))
#	extensions.append(Extension('secret','./JSONs/secret.json' , './scripts/secret.py'))
	extensions.append(Extension('mixer','./JSONs/mixer.json' , './scripts/mixer.py'))

	extensions_resp_order.append(Extension('mixer','./JSONs/mixer.json' , './scripts/mixer.py'))
#	extensions_resp_order.append(Extension('secret','./JSONs/secret.json' , './scripts/secret.py'))
#	extensions_resp_order.append(Extension('parental','./JSONs/parental.json' , './scripts/parental.py'))
#	extensions_resp_order.append(Extension('redact','./JSONs/redact.json' , './scripts/redact.py'))
	print('Starting threads')
	th1 = threading.Thread(target=payload_thread, args=(1,), daemon=True)
	th1.start()
	th2 = threading.Thread(target=start_session_notice_thread, args=(1,), daemon=True)
	th2.start()
	th3 = threading.Thread(target=end_session_notice_thread, args=(1,), daemon=True)
	th3.start()
	th4 = threading.Thread(target=wait_for_listenning_thread, args=(1,), daemon=True)
	th4.start()
	global state
	global start_session_signal
	global end_session_signal
	global listen_event_signal
	global recieved_response_signal
	global current_session
	global sandbox_pool 
	global test_file
	test_file = open('/tmp/MegsTST.txt','w+')
	sandbox_pool = Sandbox_pool(10)	
	sandbox_pool.initialize()
	while True:
		while ( state == "idle" ):
			if( start_session_signal == True ):
				state = "wait_for_listenning"
				start_session_signal = False
				debug_log("idle -> wait_for_listenning")
				break
		while ( state == "wait_for_listenning" ):
			if ( end_session_signal == True):
				state = "idle"
				end_session_signal = False
				debug_log("wait_for_listenning -> idle")
				break
			if( listen_event_signal == True):
				state = "get_cmd"
				listen_event_signal = False
				debug_log("wait_for_listenning -> get_cmd")
				break
		while ( state == "get_cmd" ):
			get_user_cmd_and_send_it()
			state = "wait_for_response"
			debug_log("get_cmd -> wait_for_response")
			break
		while ( state == "wait_for_response"):
			if( recieved_response_signal == True):
				recieved_response_signal = False
				state = "wait_for_listenning"
				debug_log("wait_for_response -> wait_for_listenning")
				break
			if( end_session_signal == True ):
				end_session_signal = False
				debug_log("wait_for_response -> idle")
				state = "idle"
				break
			

if __name__ == '__main__':
	main()



