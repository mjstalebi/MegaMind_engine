import json
import os
from Time import Time

class Trigger:
	def __init__(self , file_name="",script=""):
		self.file_name = file_name
		self.script = script

def debug_log(*args, **kwargs):
    print( "XXX "+" ".join(map(str,args))+" XXX", **kwargs)
class Items:
	def __init__(self, mydict = None):
		if(mydict is None):
			self.num_of_items = 0
			self.items = []
			self.last_item = None 
			self.dictionary = {}
		else:
			self.num_of_items = mydict.get('num_of_items')
			self.items = mydict.get('items')
			self.last_item = self.items[slef.num_of_items -1]
	def insert_new(self,new_str):
		self.items.append(new_str)
		self.last_item = new_str
		self.num_of_items += 1
	def get_dictionary(self):
		self.dictionary['num_of_items'] = self.num_of_items
		self.dictionary['items'] = self.items
		return self.dictionary
				
			
class Session:
	def __init__(self):
		self.requests = Items()
		self.responses = Items()
		self.speaker_id = "ND"
		self.skill_id = "ND"
		mytime = Time()
		mytime.set_now()
		self.time = mytime
		self.dictionary = {}
	def get_dictionary(self):
		self.dictionary['requests'] = self.requests.get_dictionary()
		self.dictionary['responses'] = self.responses.get_dictionary()
		self.dictionary['speaker_id'] = self.speaker_id
		self.dictionary['skill_id'] = self.skill_id
		self.dictionary['time'] = str(self.time)
		return self.dictionary
	
	def evaluate_filter(self, filter_dict ):
		debug_log('\n---------------')
		debug_log('evaluating filter\n')
		debug_log(filter_dict)
		debug_log('\n')
		my_session = self
		#debug_log(my_session.get_dictionary())
		last_req = my_session.requests.last_item 
		last_resp = my_session.responses.last_item
		debug_log('last request: ', last_req)
		debug_log('last response:', last_resp)
		keyword_evaluation = False
		Speaker_ID_evaluation = False
		Skill_ID_evaluation = False
		time_evaluation = False
		include_or_evaluation = False
		exclude_and_evaluation = True
		all_empty = True
		if 'keywords' in filter_dict:
			keywords = filter_dict.get('keywords')
			debug_log( 'these are keywords:')
			debug_log(keywords)
			if 'include_or' in keywords:
				all_empty = False
				include_or_evaluation = False
				debug_log('there is include or')
				include_or_items = keywords.get('include_or')
				for item in include_or_items:
					debug_log(item)
					if ((item in last_req) or (item in last_resp)):
						include_or_evaluation= True 
						break
			else:
				include_or_evaluation = True
					
			if 'exclude_and' in keywords:
				all_empty = False
				exclude_and_evaluation = True
				debug_log('there is exclude and')
				exclude_and_items = keywords.get('exclude_and')
				for item in exclude_and_items:
					debug_log(item)
					if ( (item in last_resp) or (item in last_req)):
						exclude_and_evaluation = False
						break
			else:
				exclude_and_evaluation = True

			keyword_evaluation = include_or_evaluation and exclude_and_evaluation	
			if (keyword_evaluation == False):
				return False

		if 'Speaker_ID' in filter_dict:
			Speaker_IDs = filter_dict.get('Speaker_ID')
			debug_log( 'these are Speaker_IDs:')
			debug_log(Speaker_IDs)
			if 'include_or' in Speaker_IDs:
				all_empty = False
				include_or_evaluation = False
				debug_log('there is include or')
				include_or_items = Speaker_IDs.get('include_or')
				for item in include_or_items:
					debug_log(item)
					if (my_session.speaker_id == item):
						include_or_evaluation= True 
						break
			else:
				include_or_evaluation = True
					
			if 'exclude_and' in Speaker_IDs:
				all_empty = False
				exclude_and_evaluation = True
				debug_log('there is exclude and')
				exclude_and_items = Speaker_IDs.get('exclude_and')
				for item in exclude_and_items:
					debug_log(item)
					if ( my_session.speaker_id == item):
						exclude_and_evaluation = False
						break
			else:
				exclude_and_evaluation = True

			Speaker_ID_evaluation = include_or_evaluation and exclude_and_evaluation	
			if (Speaker_ID_evaluation == False):
				return False

		if 'Skill_ID' in filter_dict:
			Skill_IDs = filter_dict.get('Skill_ID')
			debug_log( 'these are Skill_IDs:')
			debug_log(Skill_IDs)
			if 'include_or' in Skill_IDs:
				all_empty = False
				include_or_evaluation = False
				debug_log('there is include or')
				include_or_items = Skill_IDs.get('include_or')
				for item in include_or_items:
					debug_log(item)
					if (my_session.skill_id == item):
						include_or_evaluation= True 
						break
			else:
				include_or_evaluation = True
					
			if 'exclude_and' in Skill_IDs:
				all_empty = False
				exclude_and_evaluation = True
				debug_log('there is exclude and')
				exclude_and_items = Skill_IDs.get('exclude_and')
				for item in exclude_and_items:
					debug_log(item)
					if ( my_session.skill_id == item):
						exclude_and_evaluation = False
						break
			else:
				exclude_and_evaluation = True
			Skill_ID_evaluation = include_or_evaluation and exclude_and_evaluation	
			if (Skill_ID_evaluation == False):
				return False

		if 'time' in filter_dict:
			times = filter_dict.get('time')
			debug_log( 'these are times:')
			debug_log(times)
			if 'include_or' in times:
				all_empty = False
				include_or_evaluation = False
				debug_log('there is include or')
				include_or_items = times.get('include_or')
				for item_dict in include_or_items:
					debug_log(item_dict)
					start_time = Time()
					start_time.load(item_dict.get('start'))
					end_time = Time()
					end_time.load(item_dict.get('end'))
					if ( (my_session.time > start_time) and (my_session.time < end_time)):
						include_or_evaluation = True
						break
			else:
				include_or_evaluation = True

					
			if 'exclude_and' in times:
				all_empty = False
				exclude_and_evaluation = True
				debug_log('there is exclude and')
				exclude_and_items = times.get('exclude_and')
				for item_dict in exclude_and_items:
					debug_log(item_dict)
					start_time = Time()
					start_time.load(item_dict.get('start'))
					end_time = Time()
					end_time.load(item_dict.get('end'))
					if ( (my_session.time > start_time) and (my_session.time < end_time)):
						include_or_evaluation = False
						break
			else:
				exclude_and_evaluation = True
			time_evaluation = include_or_evaluation and exclude_and_evaluation	
			if (time_evaluation == False):
				return False
		if(all_empty == False):
			return True
		else:
			return False	
def evaluate_trigger(name, my_session):
	try:
		myfile = open(name,'r')

	except:
		debug_log('error oppenning' + name)

#	try:
	mydict = json.load(myfile)
	debug_log(mydict)
	filters = mydict.get('filters')
	debug_log('\n\n')
	debug_log(filters)
	for fil in filters:
		if( my_session.evaluate_filter(fil)):
			return True
def execute_extention(script):	
	print('we should execute',script)
	os.system('rm -rf /tmp/mysession')
	os.system('mkdir -p /tmp/mysession/scripts')
	os.system('cp ./' + script + ' /tmp/mysession/scripts')
	os.system('firejail --profile=myprof.profile python3.7 ~/' + script)
	
def trigger_functions(my_session, triggers):
	#for name in file_names:
	for trig in triggers:
		if(evaluate_trigger(trig.file_name,my_session)):
			execute_extention(trig.script)
	#	except:
	#		debug_log('error in parsing')

def main():
	file1 = open( './JSONs/session.json' , 'r')
	#session_dict = json.load(file1)
	my_session = Session()
	my_session.requests.insert_new('Open Uber')
	my_session.responses.insert_new('Hello this is uber')
	my_session.requests.insert_new('Get me a cab to airport')
	my_session.responses.insert_new('For when')
	my_session.requests.insert_new('For now buy a Taxi')
	my_session.speaker_id = 'Javadi'
	my_session.skill_id = 'Uber'
	debug_log(my_session.get_dictionary())

	triggers = []
	triggers.append(Trigger('./JSONs/parental.json','scripts/parental.py'))
	trigger_functions(my_session , triggers)

if __name__ == '__main__':
	main()
