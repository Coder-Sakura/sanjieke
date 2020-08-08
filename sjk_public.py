import os
import requests


def folder(path,name):
	# 目录,文件夹命名
	isExists = os.path.exists(path)
	if not isExists:
		os.mkdir(path)

	new_path = os.path.join(path,name)
	if not os.path.exists(new_path):
		os.mkdir(new_path)
		return new_path
	return new_path

def network_connect(u,rty_num=3):
	headers = {
			"cookie":"",
			"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
	}
	try:
		resp = requests.get(u,headers=headers,timeout=10)
	except Exception as e:
		if rty_num > 0:
			return network_connect(u,rty_num-1)
		else:
			print("Error: {} {}".format(u,e))
	else:
		resp.encoding = "utf8"
		return resp