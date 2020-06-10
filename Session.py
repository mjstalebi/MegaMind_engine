import json
import os
from Time import Time
from MegaNLP import MegaNLP

class Extension:
	def __init__(self , name="", rule_file_name="",script=""):
		self.name = name
		self.rule_file_name = rule_file_name
		self.script = script

	def evaluate(self, my_session):
		try:
			myfile = open(self.rule_file_name,'r')

		except:
			debug_log('error oppenning' + rule_file_name)

	#	try:
		mydict = json.load(myfile)
		debug_log(mydict)
		filters = mydict.get('filters')
		debug_log('\n\n')
		debug_log(filters)
		for fil in filters:
			if( my_session.evaluate_filter(fil)):
				return True
	def verify_new_cmd(self,cmd):
		pass
		return True
	def execute(self, mysession):	
		print('we should execute',self.script)
		os.system('rm -rf /tmp/mysession')
		os.system('mkdir -p /tmp/mysession/scripts')
		os.system('cp ./' + self.script + ' /tmp/mysession/scripts')
		os.system('firejail --profile=myprof.profile python3.7 ~/' + self.script)
	

def debug_log(*args, **kwargs):
#	print( "XXX "+" ".join(map(str,args))+" XXX", **kwargs)
	pass
	return
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
	def update_last(self,new_str):
		self.items[self.num_of_items-1] = new_str
		self.last_item = new_str
	def get_dictionary(self):
		self.dictionary['num_of_items'] = self.num_of_items
		self.dictionary['items'] = self.items
		return self.dictionary
				
			
class Session:
	def __init__(self,mynlp):
		self.requests = Items()
		self.responses = Items()
		self.speaker_id = "ND"
		self.skill_id = "ND"
		mytime = Time()
		mytime.set_now()
		self.time = mytime
		self.dictionary = {}
		self.nlp = mynlp
	def get_dictionary(self):
		self.dictionary['requests'] = self.requests.get_dictionary()
		self.dictionary['responses'] = self.responses.get_dictionary()
		self.dictionary['speaker_id'] = self.speaker_id
		self.dictionary['skill_id'] = self.skill_id
		self.dictionary['time'] = str(self.time)
		return self.dictionary
	
	def parse_nlp_function(self,item):
		index_start = item.find('(')
		index_end = item.find(')')
		substr1 = item[0:int(index_start)]
		substr2 = item[int(index_start)+1:int(index_end)]
		words = substr2.split()
		outwords = []
		outwords.append(substr1)
		for word in words:
			outwords.append(word)
		return outwords

	def evaluate_NLP(self,last_req,item):
		nlp_parts = self.parse_nlp_function(item)
		ret = []
		if( nlp_parts[0] == 'contain' ):
			if nlp_parts[1] in last_req:
				ret.append(nlp_parts[1])
				return ret
		if( nlp_parts[0] == 'contain_first_name'):
			return self.nlp.find_first_names(last_req)
		if( nlp_parts[0] == 'contain_last_name'):
			return self.nlp.find_last_names(last_req)
		if( nlp_parts[0] == 'contain_similar'):
			return self.nlp.find_similar(nlp_parts[1],last_req)
		if( nlp_parts[0] == 'contain_synonym'):
			return self.nlp.find_synonym(nlp_parts[1],last_req)
		if( nlp_parts[0] == 'contain_antonym'):
			return self.nlp.find_antonyms(nlp_parts[1],last_req)
		if( nlp_parts[0] == 'contain_profanity'):
			return self.nlp.find_profane_words(last_req)
		return ret 
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
					if ( last_req != None ):
					#	if (item in last_req):
						if (len(self.evaluate_NLP(last_req,item))>0):
							include_or_evaluation = True
							break
					if ( last_resp != None):
					#	if (item in last_resp):
						if (len(self.evaluate_NLP(last_resp,item))>0):
							include_or_evaluation = True
							break
					#if ((item in last_req) or (item in last_resp)):
					#	include_or_evaluation= True 
					#	break
			else:
				include_or_evaluation = True
					
			if 'exclude_and' in keywords:
				all_empty = False
				exclude_and_evaluation = True
				debug_log('there is exclude and')
				exclude_and_items = keywords.get('exclude_and')
				for item in exclude_and_items:
					debug_log(item)
					if ( last_req != None ):
						if (item in last_req):
							exclude_and_evaluation = False
							break
					if ( last_resp != None):
						if (item in last_resp):
							exclude_and_evaluation = False
							break
					#if ( (item in last_resp) or (item in last_req)):
					#	exclude_and_evaluation = False
					#	break
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
					debug_log(my_session.skill_id)
					if (my_session.skill_id == item):
						include_or_evaluation= True 
						debug_log("[1]")
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
			print("it evaluates to True")
			return True
		else:
			return False	
