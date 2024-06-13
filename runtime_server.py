import os
import pk_functions as fu
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
		self.pass_files = []
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
		server_files = self.life_time_files[:]
		save_dir = os.path.join(self.server, "server_save")
		save_files = os.listdir(save_dir)
		for f in save_files:
			server_files.append(os.path.join(save_dir, f))
		if self.max_memory:
			used_size = fu.folder_size(os.path.join(self.server, "response"))
			if used_size > self.max_memory:
				target_size = used_size - self.max_memory
			files = [(p, os.path.getmtime(p), os.path.getsize(p)/1024**2) for p in server_files]
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
		for p in server_files:
			file_time = os.path.getmtime(p)
			if file_time < (now - self.file_life_time):
				try:
					os.remove(p)
					self.life_time_files.remove(p)
				except:
					continue
			else:
				break

	def is_request_valid(self, file_path):
		# pickle파일인자
		# pass_files에 존재하는지
		# 파일 수정시간
		file_time = os.path.getmtime(file_path)
		if self.start_time > file_time:
			return False
		file_name = os.path.basename(file_path)
		req_id, ext = os.path.splitext(file_name)
		if req_id in self.pass_files:
			return False
		if ext != ".pickle":
			return False
		return req_id

	def run(self):
		self.start_time = int(time.time())
		req_dir = os.path.join(self.server, "request")
		while True:
			files = os.listdir(req_dir)
			for f in files:
				# req_id, ext = os.path.splitext(f)
				# if ext != ".pickle":
				# 	continue
				file_path = os.path.join(req_dir, f)
				req_id = self.is_request_valid(file_path)
				if not req_id:
					self.pass_files.append(f[:-7])
					continue
				_, req = fu.read_pickle(os.path.join(req_dir, f))
				api_path = req["api_path"]
				# call api func
				# write pickle file
				# ^^^ add try and continue
				if not "args" in req:
					args = []
				else:
					args = req["args"]
				if not "kwargs" in req:
					kwargs = {}
				else:
					kwargs = req["kwargs"]
				res = self.call_api(api_path, *args, **kwargs)
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
