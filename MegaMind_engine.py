import sock as consts
import socket
import threading
import struct
import json
from Session import Session
#from Session import debug_log
from Session import Extension
from bcolors import bcolors
from Sandbox import Sandbox
from Sandbox import Sandbox_pool
from time import sleep
import os
from mypipe import MyPipe

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
    print( "YYY "+" ".join(map(str,args))+" YYY", **kwargs)

def wait_for_start_session_notice():
	session_start_pipe.wait_on_pipe()

def wait_for_end_session_notice():
	session_end_pipe.wait_on_pipe()

def wait_for_keyword_detection():
	kwd_pipe.wait_on_pipe()
	return
	

def wait_for_payload():
	data = payload_pipe.read_from_pipe()
	return data

def wait_for_speech_recognition_done():
#	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
#		s.bind( (consts.Host,port_end_speech) )
#		s.listen()
#		conn,addr = s.accept()
#		with conn:
#			data = conn.recv(4096)
#			cmd = data.decode()
#			cmd.replace('.','')
#			cmd.replace('?','')
#			cmd.replace('!','')
#			conn.close()
#			s.close()
#			return cmd
	cmd = speech_recog_end_pipe.read_from_pipe()
	cmd.replace('.','')
	cmd.replace('?','')
	cmd.replace('!','')
	return cmd
	
def send_cmd_to_sdk(cmd):
	resp_pipe.write_to_pipe(cmd+'\0')


def start_speech_recognition():	
	speech_recog_start_pipe.write_to_pipe("s")

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
		print( ' token = ' + token_id )
		current_session.responses.insert_new(caption)
		recieved_response_signal = True
		wfr_state_end_pipe.write_to_pipe("s")
		for ext in extensions_resp_order:
			if ext not in active_extensions:
				print("evaluate: " , ext.name)
				if(ext.evaluate(current_session)):
					print("extension: " + ext.name  +" is true")
					active_extensions.append(ext)
					ext.sandbox = sandbox_pool.get_idle_sandbox()
					ext.sandbox.execute(ext.script)
		for ext in extensions_resp_order:
		#for ext in active_extensions:
			if ext in active_extensions:
				print(" RESP: we need to forward session to extenstion " + ext.name )
				session_dict = current_session.get_dictionary()
				session_dict['req_resp'] = 'resp'
				ext.sandbox.transfer_data(json.dumps(session_dict))
				#ext.sandbox.wait_for_response()
				#new_caption = ext.sandbox.get_response()
				new_caption = ext.sandbox.get_response_blocking()
				if( ext.verify_new_cmd(new_caption)):
					caption = new_caption
		print( ' new caption = ' + bcolors.OKBLUE + caption + bcolors.ENDC )
		#while (recieved_response_signal == True):
		#	pass
			



def wait_for_listenning_thread(name):
	print('wait_for_listenning_thread')
	global listen_event_signal
	while True:
		wait_for_keyword_detection()
		listen_event_signal = True
		wfl_state_end_pipe.write_to_pipe("s")
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
	first_req_of_session = True
	idle_state_end_pipe.write_to_pipe("s")
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
	wfl_state_end_pipe.write_to_pipe("s")	
	#wfr_state_end_pipe.write_to_pipe("s")	
	print(bcolors.FAIL + "*************SESSION ENDS****************"+ bcolors.ENDC)
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
	if(first_req_of_session == True):
		print( bcolors.FAIL +" first req of session call local skill_id finder" + bcolors.ENDC)
		first_req_of_session = False
		skill_id = local_skill_id_finder(cmd)
		current_session.skill_id = skill_id
	current_session.requests.insert_new(cmd)
	if (cmd != 'stop' ):
		for ext in extensions:
			if ext not in active_extensions:
				print("evaluate: " , ext.name)
				if(ext.evaluate(current_session)):
					print("extension: " + ext.name  +" is true")
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
			
		for ext in active_extensions:
			print("REQ: we need to forward session to extenstion " + ext.name )
			session_dict = current_session.get_dictionary()
			session_dict['req_resp'] = 'req'
			ext.sandbox.transfer_data(json.dumps(session_dict))
			#ext.sandbox.wait_for_response()
			#new_cmd = ext.sandbox.get_response()
			new_cmd = ext.sandbox.get_response_blocking()
			if( ext.verify_new_cmd(new_cmd)):
				cmd = new_cmd
			
		
	send_cmd_to_sdk(cmd)
		
	
	
	
	return
def main():
	print('Welcome to MegaMind Engine')
	os.system('rm -rf /tmp/MegaMind')	
	print('Initializing trigers')
	global extensions
	global extensions_resp_order
	extensions = []
	extensions_resp_order = []
	global active_extensions
	active_extensions = []
	extensions.append(Extension('parental','./JSONs/parental.json' , './scripts/parental.py'))
	extensions.append(Extension('redact','./JSONs/redact.json' , './scripts/redact.py'))
	extensions.append(Extension('secret','./JSONs/secret.json' , './scripts/secret.py'))

	extensions_resp_order.append(Extension('secret','./JSONs/secret.json' , './scripts/secret.py'))
	extensions_resp_order.append(Extension('parental','./JSONs/parental.json' , './scripts/parental.py'))
	extensions_resp_order.append(Extension('redact','./JSONs/redact.json' , './scripts/redact.py'))
	global kwd_pipe 
	kwd_pipe = MyPipe('keyword_detection')
	kwd_pipe.make()
	global resp_pipe
	resp_pipe  = MyPipe('MegaMind_engine_response')
	resp_pipe.make()
	global session_start_pipe
	session_start_pipe  = MyPipe('session_start')
	session_start_pipe.make()
	global session_end_pipe
	session_end_pipe  = MyPipe('session_end')
	session_end_pipe.make()
	global payload_pipe
	payload_pipe  = MyPipe('payload')
	payload_pipe.make()
	global speech_recog_start_pipe
	speech_recog_start_pipe = MyPipe('speech_recog_start')
	speech_recog_start_pipe.make()
	global speech_recog_end_pipe
	speech_recog_end_pipe = MyPipe('speech_recog_end')
	speech_recog_end_pipe.make()

	global idle_state_end_pipe
	idle_state_end_pipe = MyPipe('idle_state_end')
	idle_state_end_pipe.make()

	global wfl_state_end_pipe
	wfl_state_end_pipe = MyPipe('wfl_state_end')
	wfl_state_end_pipe.make()

	global wfr_state_end_pipe
	wfr_state_end_pipe = MyPipe('wfr_state_end')
	wfr_state_end_pipe.make()

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
	sandbox_pool = Sandbox_pool(10)	
	sandbox_pool.initialize()
	while True:
		while ( state == "idle" ):
			idle_state_end_pipe.wait_on_pipe()
			if( start_session_signal == True ):
				state = "wait_for_listenning"
				start_session_signal = False
				debug_log("idle -> wait_for_listenning")
				break
		while ( state == "wait_for_listenning" ):
			wfl_state_end_pipe.wait_on_pipe()
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
			wfr_state_end_pipe.wait_on_pipe()
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



