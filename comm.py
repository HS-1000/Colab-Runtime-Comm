import os
import time
import functions as fu


class Session:
	#TODO allow_delay항상 True로 변경하기
	def __init__(self, server_path, wate_time=60, allow_delay=600) -> None:
		self.request_path = {}
		self.server = server_path
		self.wate = wate_time
		self.delay = allow_delay
	
	def request(self, params):
		"""
		Args:
			params: <dict>, include "api_path", "args":<list>, "kwargs":<dict>
		"""
		req_id = fu.random_with_time()
		req_path = os.path.join(self.server, f"request/{req_id}.pickle")
		result, msg = fu.create_pickle(req_path, params)
		if result:
			self.request_path[req_id] = os.path.join(self.server, f"response/{req_id}.pickle")
		else:
			self.request_path[req_id] = f"False: {msg}"
			return False
		wait = 0
		while True:
			if os.path.exists(self.request_path[req_id]):
				break
			else:
				time.sleep(1)
				wait += 1
				if wait > self.wate:
					return False
		_, data = fu.read_pickle(self.request_path[req_id])
		# if data["status"] == "delay": # delay기능 삭제 예정
		# 	if self.delay:
		# 		new_req_id = data["return"]["new_request_id"]
		# 		del self.request_path[req_id]
		# 		self.request_path[new_req_id] = os.path.join(self.join, f"response/{new_req_id}.pickle")
		# 		req_id = new_req_id
		# 		wait = 0
		# 		while True:
		# 			if os.path.exists(self.request_pathp[req_id]):
		# 				break
		# 			else:
		# 				time.sleep(1)
		# 				wait += 1
		# 				if wait > self.delay:
		# 					return False
		# 		_, data = fu.read_pickle(self.request_path[req_id])
		# 		return data["return"]
		# 	else:
		# 		return False
		# else: # data["status"] == "complete"
		return data["return"]

