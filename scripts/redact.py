import os
from Commu import Commu
import json

def pr(*args , **kwargs):
	print( '**** ' + " ".join(map(str,args)) + " ****" , **kwargs)

pr("redacting extention")
comm = Commu()
comm.update_ready(False)
while True:
	comm.wait_for_new_data()
	session = comm.read_data()
	pr(session)
	item = comm.get_item_of_interest(session)
	print(item)
	item = item.replace('javad','bob')
	item = item.replace('ardalan','alex')
	comm.write_response(item)
	comm.update_ready(True)

	
