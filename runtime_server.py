import os
import functions as fu
import time

class RuntimeServer:
	def __init__(self, server_path, file_life_time=600, max_memory=False) -> None:
		"""
		Args:
			server_path: 클라이언트와 통신할 파일을 저장하는 폴더
			file_life_time: 생성된 파일은 일정시간뒤에 삭제
			max_memory: False | <int>, mb단위, 초과되면 오래된 파일삭제 
		"""
		self.life_time_files = []
		self.saved_files = {}
		self.file_life_time = file_life_time
		self.max_memory = max_memory
		self.server = server_path
		self.server_api = NestedDict()
		self.start_time = None
		if not os.path.exists(os.path.join(server_path, "request")):
			os.mkdir(os.path.join(server_path, "request"))
		if not os.path.exists(os.path.join(server_path, "response")):
			os.mkdir(os.path.join(server_path, "response"))
		if not os.path.exists(os.path.join(server_path, "server_save")):
			os.mkdir(os.path.join(server_path, "server_save"))

	def response(self, req_id, status, data):
		res_path = os.path.join(self.server, f"response/{req_id}.pickle")
		res = {}
		res["status"] = status
		res["return"] = data
		result, err = fu.create_pickle(res_path, res)
		if result:
			req_path = os.path.join(self.server, f"request/{req_id}.pickle")
			# self.life_time_files[req_id] = res_path
			self.life_time_files.append(res_path)
			if os.path.exists(req_path):
				os.remove(req_path)
		return result, err

	# def make_delay(self, req_id):
	# 	new_req_id = fu.random_with_time()
	# 	return self.response(
	# 		req_id,
	# 		"delay",
	# 		{"new_request_id" : new_req_id}
	# 	)

	def create_api(self, api_path:str, func:callable):
		"""
		Args:
			api_path: <str>, "/" 기준으로 분리
			func: api에 실행될 함수, 반환값을 클라이언트에 응답
		"""
		path_list = api_path.split("/")
		self.server_api.path_write(func, path_list)

	def remove_api(self, api_path):
		"""
		Args:
			api_path: <str>, "/" 기준으로 분리
		"""
		path_list = api_path.split("/")
		self.server_api.remove(*path_list)

	def call_api(self, api_path, *args, **kwargs):
		path_list = api_path.split("/")
		api_func = self.server_api.path_read(*path_list)
		if not callable(api_func):
			return False
		else:
			return api_func(*args, **kwargs)

	def clean_file(self):
		if self.max_memory:
			used_size = fu.folder_size(os.path.join(self.server, "response"))
			if used_size > self.max_memory:
				target_size = used_size - self.max_memory
			files = [(p, os.path.getmtime(p), os.path.getsize(p)/1024**2) for p in self.life_time_files]
			files.sort(key=lambda x: x[1])
			deleted_size = 0
			for file_path, _, file_size in files:
				try:
					os.remove(file_path)
					self.life_time_files.remove(file_path)
					deleted_size += file_size
				except:
					continue
				if deleted_size > target_size:
					break
			if target_size > deleted_size:
				print("\nWARNING: 서버 메모리 초과됨")
				print(f"Used: {int(used_size-deleted_size)}/{self.max_memory}")
		now = time.time()
		for p in self.life_time_files:
			file_time = os.path.getmtime(p)
			if file_time < (now - self.file_life_time):
				try:
					os.remove(p)
					self.life_time_files.remove(p)
				except:
					continue
			else:
				break

	def run(self):
		pass
		#TODO response 폴더 확인
		# ^^^ 요청 파일 반복문
		# ^^^ 	요청파일 내용확인
		# ^^^ 	응답파일 생성, 처리된 요청파일 삭제
		# ^^^ 	사용중인 저장공간 확인
		# ^^^ 요청이 없었다면 잠시 time.sleep(5)
		# ^^^ 
		# ^^^ 
		self.start_time = int(time.time())
		req_dir = os.path.join(self.server, "request")
		while True:
			files = os.listdir(req_dir)
			for f in files:
				req_id, ext = os.path.splitext(f)
				if ext != ".pickle":
					continue
				req = fu.read_pickle(os.path.join(req_dir, f))
				api_path = req["api_path"]
				# call api func
				# write pickle file
				# ^^^ add try and continue
				res = self.call_api(api_path, *req["args"], **req["kwargs"])
				self.response(req_id, "complete", res) # delay기능 삭제 예정
			self.clean_file()
			time.sleep(5)

class NestedDict(dict): # api 저장에 사용할 중첩하기 쉬운 dict
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		keys_  = self.keys()
		for key in keys_:
			if isinstance(self[key], dict):
				super().__setitem__(key, NestedDict(self[key]))

	def __setitem__(self, key, value):
		if isinstance(value, dict):
			if not isinstance(value, NestedDict):
				value = NestedDict(value)
			if key in self:
				if isinstance(self[key], dict):
					for key_ in value:
						self[key][key_] = value[key_]
				else:
					super().__setitem__(key, value)
			else:
				super().__setitem__(key, value)
		else:
			super().__setitem__(key, value)

	def path_read(self, *keys):
		current = self
		if isinstance(keys[0], list):
			keys = keys[0]
		for key in keys:
			if isinstance(key, dict):
				if key in current:
					current = current[key]
				else:
					return None
			elif hasattr(current, "__iter__"):
				try:
					current = current[key]
				except:
					return None
			else:
				return None
		return current

	def path_write(self, write, keys):
		"""
		Args:
			write: object
			keys: <list>
		"""
		current = self
		for key in keys[:-1]:
			if not key in current:
				current[key] = NestedDict()
			current = current[key]
		current[keys[-1]] = write

	def remove(self, *keys):
		for key in keys:
			if key in self:
				del self[key]
