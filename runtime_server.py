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
		self.server_api = {}
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

	def make_delay(self, req_id):
		new_req_id = fu.random_with_time()
		return self.response(
			req_id,
			"delay",
			{"new_request_id" : new_req_id}
		)

	def create_api(self, api_path, func:callable):
		pass

	def remove_api(self, api_path):
		pass

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
	

