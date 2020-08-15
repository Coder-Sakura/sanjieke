import os
import json
import re

from sjk_content import SJK_CONTENT
from sjk_video import SJK_VIDEO
from thread_pool import *	
from sjk_public import folder,network_connect

class Pivot:
	def __init__(self,class_url):
		self.host = "class.sanjieke.cn"
		# 课程存储目录
		self.root_path = r"G:\python_code"
		# 课程
		self.class_url = class_url
		self.class_name = ""
		self.class_id = self.get_class_id()
		self.class_path = ""
		self.class_api_url = "https://class.sanjieke.cn/api/class/stages?class_id={}"

		# stage
		self.stage_api_url = "https://class.sanjieke.cn/api/class/stage/cards/content?class_id={}&stage_id={}"
		
		# section
		self.section_api_url = "https://service.sanjieke.cn/section/content?class_id={}&section_id={}"

		# video_matser
		self.audio_matser_api_url = "https://service.sanjieke.cn/video/master/auth?class_id={}&video_id={}"
		
		# 文章 --> docx
		self.sc = SJK_CONTENT()
		# 视频 --> m3u8 --> mp4
		self.sv = SJK_VIDEO()
		self.video_task = []

	def get_class_id(self):
		if self.host not in self.class_url:
			print("Error url:",self.class_url)
			exit()

		return self.class_url.split("?")[0].split(r"/")[-1]

	def get_stage_data(self):
		"""
		获取每个章节的数据
		:params class_id:课程id
		:return :课程data
		[{'stage_id': 1899, 'stage_name': '课前内容'},...]
		"""
		class_id = self.class_id
		res = json.loads(network_connect(self.class_api_url.format(class_id)).text)
		code = res.get("code",None)
		if code == None or code == 0:
			return False
		else:
			study_stage_data = res.get("data",[])
			if study_stage_data == []:
				return False
			else:
				self.class_name = study_stage_data["class_name"]
				stage_data = [{"stage_id":i["stage_id"],
								"stage_name":i["stage_name"]} for i in study_stage_data["study_stage"] if i["is_lock"] == 0]
				return stage_data

	def get_section_data(self,stage_id):
		"""
		获取每个card里的文章数据
		:parmas stage_id: 章节id
		:return: 章节数据,
		"""
		u = self.stage_api_url.format(self.class_id,stage_id)
		res = json.loads(network_connect(u).text)
		code = res.get("code",None)
		if code == None or code == 0:
			return False
		else:
			study_section_data = res.get("data",[])
			if study_section_data == []:
				return False
			else:
				section_data = [{"card_name":i["card_name"],
								"section_id":j["section_id"],
								"section_name":j["section_name"]} for i in study_section_data["nodes"] for j in i["children"]]
				return section_data

	def get_content(self,section_id):
		"""
		获取章节内容
		:params section_id: 章节url
		:params u: 章节url
		"""
		resp = json.loads(network_connect(self.section_api_url.format(self.class_id,section_id)).text)
		# {'code': 403, 'data': [], 'msg': '哎呀，课程内容丢失了'}
		code = resp.get("code",None)
		if code == None or code != 200:
			return False
		else:
			content_data = resp.get("data",[])
			if content_data == []:
				return False
			else:
				nodes = content_data["nodes"]
				# 原生html代码
				text_list = [node["content"] if node["content_type"] == 1 else node["content"]["content"] if node["content_type"] == 3 else "" for node in nodes]
				# video_id列表
				video_id_list = [node["content"]["id"] for node in nodes if node["content_type"] == 2]
				return text_list,video_id_list

	def main(self):
		# class-stage-card-section
		stage_data = self.get_stage_data()
		# 创建课程文件夹
		self.class_path = folder(self.root_path,self.class_name)

		# 判断章节数据是否异常
		if stage_data == False:
			print("获取stage数据失败 ",self.class_api_url.format(self.class_id))

		pool = ThreadPool(8)

		try:
			for stage in stage_data:
				# 创建章节文件夹
				stage_path = folder(self.class_path,stage["stage_name"])
				section_data = self.get_section_data(stage["stage_id"])

				if section_data == False:
					print("获取section数据失败",u)

				for section in section_data:
					card_path = folder(stage_path,section["card_name"])
					t,v = self.get_content(section["section_id"])
					if t != []:
						section_name = re.sub('[\/:*?"<>|]','_',section["section_name"])
						docx_path = os.path.join(card_path,"{}.docx".format(section_name))
						# self.sc.main(section_name,docx_path,t)
						pool.put(self.sc.main,(section_name,docx_path,t,),callback)

					if v != []:
						for _ in v:
							audio_matser_url = self.audio_matser_api_url.format(self.class_id,_)
							section_name = re.sub('[\/:*?"<>|]','_',section["section_name"])
							video_path = os.path.join(card_path,"{}.mp4".format(section_name))
							self.video_task.append({"video_path":video_path,"audio_matser_url":audio_matser_url})
		except Exception as e:
			print(e)
			pool.close()
		finally:
			pool.close()

		print("开始下载视频...")
		for task in self.video_task:
			self.sv.main(task["video_path"],task["audio_matser_url"])


if __name__ == '__main__':
	class_url = "https://class.sanjieke.cn/stages/23134530"
	p = Pivot(class_url)
	p.main()

