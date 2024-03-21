import os
import pickle as pk
import time
import random

"""
호출해서 사용할 session클래스: 이 클래스를 사용해서 서버와 pickle파일 통신
"""

"""
session클래스에서 사용할 보조적인 함수들 
"""

def create_pickle(file_path, object):
	if os.path.exists(file_path):
		return False, "File already exists"
	with open(file_path, "wb") as f:
		try:
			pk.dump(object, f)
		except Exception as e:
			return False, e
	return True, None

def read_pickle(file_path):
	with open(file_path, "rb") as f:
		try:
			loaded = pk.load(f)
		except Exception as e:
			return False, e
	return True, loaded

def random_with_time():
	stamp = str(int(time.time()) % 10000)
	rand_num = str(random.randint(0, 9999))
	stamp = stamp.zfill(4)
	rand_num = rand_num.zfill(4)
	return stamp + rand_num

class Session:
	def __init__(self, server_path, wate_time=60, allow_delay=600) -> None:
		self.request = {}
		self.server = server_path
		self.wate = wate_time
		self.delay = allow_delay
	
	def request(self, params):
		req_id = random_with_time()
		req_path = os.path.join(self.server, f"request/{req_id}.pickle")
		result, msg = create_pickle(req_path, params)
		if result:
			self.request[req_id] = os.path.join(self.server, f"response/{req_id}.pickle")
		else:
			self.request[req_id] = f"False: {msg}"
			return False
		wait = 0
		while True:
			if os.path.exists(self.request[req_id]):
				break
			else:
				time.sleep(1)
				wait += 1
				if wait > self.wate:
					return False
		_, data = read_pickle(self.request[req_id])
		if data["status"] == "delay":
			if self.delay:
				new_req_id = data["new_request_id"]
				del self.request[req_id]
				self.request[new_req_id] = os.path.join(self.join, f"response/{new_req_id}.pickle")
				req_id = new_req_id
				wait = 0
				while True:
					if os.path.exists(self.requestp[req_id]):
						break
					else:
						time.sleep(1)
						wait += 1
						if wait > self.delay:
							return False
				_, data = read_pickle(self.request[req_id])
				return data["return"]
			else:
				return False
		else: # data["status"] == "complete"
			return data["return"]


		


		#TODO 
			




