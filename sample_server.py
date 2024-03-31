import sys
sys.path.append("/content/drive/MyDrive/comm")
import runtime_server

server_path = "."
server = runtime_server.RuntimeServer(server_path)
server.create_api("test_api/hello", lambda x:"hello")
server.run()
