import os
import functions as fu


class RuntimeServer:
	def __init__(self, server_path, memory=1024) -> None:
		self.response_path = {}
		self.saved_files = {}
		self.memory = memory
		self.server = server_path

	def response(self, status, data):
		pass

	def make_delay(self, req_id):
		pass

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
	

