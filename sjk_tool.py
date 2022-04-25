# -*- encoding: utf-8 -*-
'''
@File    :   sjk_tool.py
@Time    :   2022/04/17 17:55:51
@Author  :   Coder-Sakura
@Version :   1.0
@Desc    :   None
'''

# here put the import lib
import os
import re
import sys
import time
import random
import requests
from loguru import logger


from thread_pool import ThreadPool


# ===== CUSTOM CONFIG ===== #
# 用户自定义下载目录
ROOT_PATH = r"your path"
# 用户自定义休眠时间 - 每门课程下载完成后的休眠时间,秒
COURSE_SLEEP = 300
# 用户自定义下载开始页数
START_PAGE = 1


# 登录方式1 - 账号&密码(推荐)
USER_PHONE = "your phone"
USER_PASSWD = "your pwd"
# 登录方式2 - COOKIE
USER_COOKIE = ""
# ===== CUSTOM CONFIG ===== #
DEBUG = False


default_headers = {
	"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
}
session = requests.session()


class Tool:
	"""配置类"""
	def __init__(self) -> None:
		self.config = Tool._config()
		self.config["cookie"] = self.user_info_handler()
		self.config["root_path"] = ROOT_PATH
		self.config["user_info"] = {
			"COURSE_SLEEP": COURSE_SLEEP,
			"USER_PHONE": USER_PHONE,
			"USER_PASSWD": USER_PASSWD,
			"USER_COOKIE": USER_COOKIE
		}

		self.pool = ThreadPool(8)

	def user_info_handler(self):
		"""
		通过用户提供的账户密码/cookie来进行cookie预处理
		"""
		if USER_COOKIE:
			cookie_dict = {}
			for i in USER_COOKIE.split(";"):
				n,v = i.strip().split("=",1)
				cookie_dict[n] = v
			# return requests.utils.cookiejar_from_dict(cookie_dict)
			return cookie_dict
		else:
			data = {
				"phone": USER_PHONE,
				"passwd": USER_PASSWD,
				"channel": "youshangjiao",
				"current_url": "https://passport.sanjieke.cn/account/sign_in?channel=youshangjiao",
				"courseid": ""
			}
			resp = network_connect(
				self.config["login"],
				"POST",
				**{"data": data}
			)
			cookiedict  = requests.utils.dict_from_cookiejar(resp.cookies)
			# self.config["cookie"] = cookiedict
			logger.info("Login Success")
			logger.debug(f"<cookies.headers> - {resp.headers}")
			logger.debug(f"<cookies.dict> - {cookiedict}")
			return cookiedict
		# return self.config["cookie"]

	@staticmethod
	def _config():
		return {
			"login": "https://passport.sanjieke.cn/login/phone/passwd",

			"root_url": "https://www.sanjieke.cn/discover",
			"discover_url": "https://web-api.sanjieke.cn/cms-agg/api/products_v3",

			"sku_url": "https://www.sanjieke.cn/course/detail/sjk/{}",
			"sku_api": "https://web-api.sanjieke.cn/cms-agg/api/vip/free_course",

			"course_tree_url": "https://class.sanjieke.cn/course/class_content_with_checkpoint",
			"section": "https://class.sanjieke.cn/course/section_content",
			"video": "https://service.sanjieke.cn/video/master/auth",
		}


def folder(name, root_path=ROOT_PATH):
	name = re.sub('[\/:*?"<>|]', '_', name)
	name = name.replace("\t","")
	name = str(name)
	# 目录,文件夹命名
	isExists = os.path.exists(root_path)
	if not isExists:
		os.mkdir(root_path)

	new_path = os.path.join(root_path,name)
	if not os.path.exists(new_path):
		os.mkdir(new_path)
	return new_path

def network_connect(u, type="GET", rty_num=3, **kwargs):
	try:
		time.sleep(random.choice([i/10 for i in range(1,6)]))
	except:
		time.sleep(0.1)

	if kwargs:
		logger.debug(f"<kwargs> - {kwargs}")

	if "headers" not in kwargs.keys():
		headers = default_headers
	else:
		headers = kwargs["headers"]

	try:
		resp = session.request(
			type,
			u,
			data = kwargs.get("data"),
			params = kwargs.get("params"),
			cookies = kwargs.get("cookies", ""),
			headers = headers,
			# verify = False,
			timeout = 10
		)

		# if type == "POST":
		# 	resp = session.post(
		# 		u, headers=headers, data=kwargs.get("data"),
		# 		cookies=kwargs.get("cookies"), timeout=10
		# 	)
		# else:
		# 	resp = session.get(
		# 		u, headers=headers, params=kwargs.get("params"),
		# 		cookies=kwargs.get("cookies"), timeout=10
		# 	)
	except Exception as e:
		if rty_num > 0:
			logger.debug(f"rty_num - {rty_num}")
			return network_connect(u, type=type, rty_num=rty_num-1, **kwargs)
		else:
			logger.warning("Error: {} {}".format(u,e))
	else:
		resp.encoding = "utf8"
		return resp

def logger_init():
	if DEBUG:
		level = "DEBUG"
	else:
		level = "INFO"

	# remove default handler
	logger.remove()
	# 控制台输出
	logger.add( 
		sys.stderr,
		level=level
	)
	log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
	# 日志写入
	logger.add( 
		os.path.join(log_path, "{time}.log"),
		encoding="utf-8",
		rotation="00:00",
		enqueue=True,
		level=level
	)
	# ERROR日志写入
	# logger.add(
	# 	os.path.join(log_path, "[ERROR video] {time}.log"),
	# 	encoding="utf-8",
	# 	rotation="00:00",
	# 	enqueue=True,
	# 	level="ERROR"
	# )
	return logger

logger = logger_init()
tool = Tool()