import os
import time
import functions as fu


class Session:
	#TODO allow_delay항상 True로 변경하기
	def __init__(self, server_path, wait_time=60) -> None:
		self.request_path = {}
		self.server = server_path
		self.wait = wait_time
	
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
				if wait > self.wait:
					return False
		_, data = fu.read_pickle(self.request_path[req_id])

		return data["return"]

