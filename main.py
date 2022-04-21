import os
import re
import time
import json

from sjk_tool import tool, logger, \
	folder, network_connect, default_headers, COURSE_SLEEP
from sjk_content import SJK_CONTENT
from sjk_video import SJK_VIDEO
from thread_pool import callback
# test
# from thread_pool import ThreadPool, callback


class CourseHandler:
	def __init__(self, index, len, course_data) -> None:
		self.index = index
		self.len = len
		self.course_data = course_data
		logger.debug(self.course_data)

	def __enter__(self):
		# 创建课程根目录
		self.course_path = folder(self.course_data["course"])
		self.cid = self.get_sku()
		return self

	def __exit__(self,exc_type,exc_value,exc_trackback):
		pass

	def get_sku(self):
		# logger.debug("get_sku")
		_headers = default_headers.copy()
		_headers["sjk-apikey"] = "tSiXjbGTHnzJno0Fa1ucHJ56QQ1Xw90D"
		data = {
			"product_id": self.course_data["course_id"]
		}
		resp = network_connect(
			tool.config["sku_api"],
			type="POST",
			**{"data": data, "headers": _headers, "cookies": tool.config["cookie"]}
		)
		try:
			res = json.loads(resp.text)
		except Exception as e:
			logger.warning(f"{self.course_data['title']} 获取sku失败")
			logger.warning(f"请使用三节课vip会员账号登录 或 检查网络是否异常")
			return ""

		logger.debug(res)
		if res:
			cid = res["data"]["return_url"].split("cid/")[-1].rsplit("/")[0]
			return cid
		return ""

	# 获取每门课程的章节目录
	def course_tree(self):
		"""
		获取每个章节的数据
		:return: <exp> or []
		<exp>
		[
			{
				"node_id": node_id,
				"title": title,
				"children": [
					{
						"node_id":node_id,
						"title":title, 
						"type":type
					},{...}
				]
			}
		]
		"""
		params = {
			"cid": self.cid,
		}
		resp = network_connect(
			tool.config["course_tree_url"], 
			**{"params": params}
		)
		res = json.loads(resp.text)

		if res["info"] != "OK" or not res["data"]:
			return []

		tree_info = []
		for _ in res["data"]["tree"]:
			node_info = {}
			node_info["node_id"] = _["node_id"]
			node_info["title"] = _["title"]

			node_info["children"] = [
				{"node_id": children_info["node_id"], "title": children_info["title"],
				 "type": children_info["type"]} for children_info in _["children"]
			]
			tree_info.append(node_info)
		# logger.debug(f"<tree_info> - {tree_info}")
		return tree_info

	# 获取章节内容
	@logger.catch
	def get_section_data(self, node_path, section_data):
		"""
		:params section_data: 小章节数据
		"""
		params = {
			"cid": self.cid,
			"section_id": section_data["node_id"],
		}
		resp = network_connect(
			tool.config["section"], 
			**{"params": params}
		)
		res = json.loads(resp.text)
		if res["info"] != "OK" or resp.status_code != 200 or not res["data"]:
			logger.warning(f"小节:{section_data['title']} 获取内容出错")
			logger.debug(resp.text)
			return 
		else:
			nodes = res["data"]["nodes"]
			# 原生html代码
			text_list = [node["content"] if node["content_type"] == 1 else node["content"]["content"] if node["content_type"] == 3 else "" for node in nodes]
			# video_id列表
			video_id_list = [node["content"]["id"] for node in nodes if node["content_type"] == 2]
			# return text_list,video_id_list

		logger.debug(f"<len(text_list)> - {len(text_list)} | <len(video_id_list)> - {len(video_id_list)} ")
		# 内容处理
		if text_list != []:
			section_name = re.sub('[\/:*?"<>|]', '_', section_data["title"])
			docx_path = os.path.join(node_path, f"{section_name}.docx")
			SJK_CONTENT().main(section_name, docx_path, text_list)
			# tool.pool.put(SJK_CONTENT().main, (section_name, docx_path, text_list, ), callback)

		if video_id_list != []:
			for _ in video_id_list:
				video_data = {}
				section_name = re.sub('[\/:*?"<>|]', '_', section_data["title"])
				video_data["video_path"] = os.path.join(node_path, f"{section_name}.mp4")
				video_data["params"] = {"class_id": self.cid, "video_id": _,}
				tool.pool.put(SJK_VIDEO().main, (video_data, ), callback)
				time.sleep(0.5)

	def main(self):
		if self.cid:
			logger.debug(f"cid - {self.cid}")
		elif not self.cid:
			return

		tree = self.course_tree()
		if not tree:
			logger.warning(f"{self.course_data['course']} - Not Course Tree")

		logger.info(f"({self.index+1}/{self.len})当前下载课程: 《{self.course_data['title']}》 - 共{len(tree)}章")
		for node in tree:
			# 创建大章根目录
			node_path = folder(node["title"], self.course_path)
			for section in node["children"]:
				logger.debug(f"<section> - {section}")
				self.get_section_data(node_path, section)
				# tool.pool.put(self.get_section_data, (node_path, section, ), callback)
				time.sleep(1)


class Handler:
	"""
	默认下载'发现课程页面'中第一页的所有课程
	vip课程请使用vip账号进行下载,否则将忽略
	"""
	def __init__(self):
		pass

	def discoverInfo(self, page=1):
		"""
		获取<发现课程>页面的课程信息
		:paramas page: 页数
		:return: <exp> or []
		<exp>
		[
			{
				# "href": href,			# 课程链接
				"course_id": course_id,	# 课程id
				"title": title,			# 课程标题
				"nums": nums,			# 课程节数
				"duration": duration,	# 课程时长
				"teacher": teacher,		# 课程讲师
				"course": course		# 课程信息汇总
			}
			...
		]
		"""
		params = {
			"sort": "sold_count",
			"sort_direction": "desc",
			"vip_free_flag": 0,
			"page": page,
			"per_page": 20,
		}
		_headers = default_headers.copy()
		_headers["sjk-apikey"] = "tSiXjbGTHnzJno0Fa1ucHJ56QQ1Xw90D"

		resp = network_connect(
			tool.config["discover_url"], 
			**{"params": params, "headers": _headers}
		)
		data = json.loads(resp.text)
		# logger.debug(f"<json data> - {data}")

		course_list = data["data"]["list"]
		if data["msg"] != "ok" or not course_list:
			logger.warning(f"<course_list> - {course_list} NOT DATA.")
			return []
		else:
			exp = []
			for _ in course_list:
				# href = _.xpath("""./@href""")[0]
				course_id = _["id"]
				title = _["title"]
				nums = _["section_count"]
				duration = _["video_duration"]
				teacher = _["teachers"][0]["name"]
				course = f"{title}-{course_id}-{teacher}-共{nums}节-{duration}"

				_info = {
					"course_id":course_id, "title":title, "nums":nums, 
					"duration":duration, "teacher":teacher, "course":course
				}
				exp.append(_info)
			return exp

	def main(self):
		page = 1
		while True:
			course_list = self.discoverInfo(page=page)
			# test
			course_list = course_list[:2]
			# course_list = course_list[1:2]
			logger.info(f"当前下载第{page}页, 共{len(course_list)}门课程.")
			for i, _ in enumerate(course_list):
				with CourseHandler(i, len(course_list), _) as h:
					h.main()
				# test
				# break
				logger.info(f"每下载完一门课程,将休眠{COURSE_SLEEP}秒 zzz....")
				if i+1 != len(course_list):
					# test
					time.sleep(7)
					# time.sleep(COURSE_SLEEP)

			if len(course_list) < 20 or not course_list:
				break
			else:
				time.sleep(5)
				# test
				if page == 2:
					break
				page += 1
			

if __name__ == '__main__':
	p = Handler()
	p.main()