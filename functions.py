import os
import pickle as pk
import time
import random

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
	stamp = str(int(time.time()) % 1000000)
	rand_num = str(random.randint(0, 999999))
	stamp = stamp.zfill(6)
	rand_num = rand_num.zfill(6)
	return stamp + rand_num

def folder_size(folder_path):
	total = 0
	for dir_path, _, files in os.walk(folder_path):
		for f in files:
			file_path = os.path.join(dir_path, f)
			total += os.path.getsize(file_path)
	total = total / 1024**2
	return total

def delete_oldest_file(folder_path):
	files = [(os.path.join(dirpath, filename), os.path.getmtime(os.path.join(dirpath, filename)), os.path.getsize(os.path.join(dirpath, filename))) 
			 for dirpath, _, filenames in os.walk(folder_path) 
			 for filename in filenames]
	files.sort(key=lambda x: x[1])
	if not files:
		return 0
	for f in files:
		oldest_file_path, _, oldest_file_size = f
		try:
			os.remove(oldest_file_path)
			return oldest_file_size
		except Exception as e:
			continue
	return 0
