import sys
sys.path.append("/content/drive/MyDrive/comm")
import comm

session = comm.Session(".")
req = {
    "api_path" : "api_test/hello",
    "args" : [0]
}
res = session.request(req)
print(res)

