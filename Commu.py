import json
class Commu:
	def __init__(self):
		pass
		return
	def update_new_data(self, b):
		f = open ('new_data.txt' , 'w+')
		f.write(str(b))
		f.close()
		return
	def update_ready(self,b):
		f = open( 'ready.txt' , 'w+')
		print('setting ready to ' + str(b))
		f.write(str(b))
		f.close()
		return
	def wait_for_new_data(self):
		f = open ('new_data.txt' , 'r')
		lines = f.readlines()
		line = lines[0]
		while line == 'False':
			f.seek(0,0)
			lines = f.readlines()
			if (len(lines) == 1):
				line = lines[0]
			#sleep(1)
			#print('.')
			#print(line)
		self.update_new_data(False)
		f.close()
		return
	def read_data(self):
		f = open( 'data.txt')
		return json.load(f)
	def write_response(self,item):
		f = open( 'response.txt' ,'w+')
		f.write(item)
		f.close()
		return
	def get_item_of_interest(self,session):
		req_res = session['req_resp']
		if (req_res == 'req'):
			req_dict = session['requests']
			num = req_dict['num_of_items']
			if (num >0):
				items = req_dict['items']
				last_item = items[num-1]
				return last_item
		else:
			pass
			return ""
	def get_num_of_requests(self,session):
		req_res = session['req_resp']
		if (req_res == 'req'):
			req_dict = session['requests']
			num = req_dict['num_of_items']
			return num
