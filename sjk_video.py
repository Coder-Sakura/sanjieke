import os
import json
import time
from Crypto.Cipher import AES

from sjk_public import folder,network_connect

class SJK_VIDEO:
	def __init__(self):
		# aes-128 key url
		self.key_url = ""
		self.key = None

		# ts文件列表
		self.ts_list = []

		# 加密解密对象
		self.cryptor = ""

		# 视频存储目录
		self.sv_path = ""
		# 各个视频临时文件存储目录
		self.m3u8_work_path = ""

	# 下载
	def down(self,path,content):
		with open(path,"wb") as f:
			f.write(content)

	# 获取m3u8 url
	def get_m3u8_url(self,audio_matser_url):
		resp = json.loads(network_connect(audio_matser_url).text)
		if resp.get("code",None) == 200:
			return resp["data"]["url"]
		else:
			return None

	# 多码率列表文件解析
	def parse_rate(self,media_rates_url):
		media_m3u8_name = media_rates_url.split("?")[0].split("/")[-1]
		media_m3u8_path = os.path.join(self.sv_path,media_m3u8_name)
		self.down(media_m3u8_path,network_connect(media_rates_url).content)

		with open(media_m3u8_path,"r",encoding="utf8") as f:
			r = f.readlines()
			for i in range(len(r)):
				if "#EXT-X-STREAM-INF" in r[i]:
					# 只取第一个高码率的地址
					high_rate_m3u8_url =r[i+1].replace("\n","")
					break
		# 删除多码率列表文件
		os.remove(media_m3u8_path)
		return high_rate_m3u8_url

	# 获取解密key
	def get_m3u8_key(self):
		with open(self.m3u8_path,"r",encoding="utf8") as f:
			for i in f.readlines():
				if "EXT-X-KEY" in i:
					key_url = i.split('URI="')[1].split('"')[0]
					if key_url != self.key_url:
						return self.key_url,network_connect(key_url).content

	def get_ts(self):
		with open(self.m3u8_path,"r",encoding="utf8") as f:
			r = f.readlines()
			for i in range(len(r)):
				 if "#EXTINF" in r[i]:
				 	ts_url = r[i+1].replace("\n","")
				 	ts_name = r[i+1].replace("\n","").split("?")[0].split("/")[-1]
				 	print("\rTS文件下载中...({}/{}){}".format(i,len(r),ts_name),end="")

				 	self.ts_list.append(ts_name)
				 	resp = network_connect(ts_url).content
			 		self.down_ts(ts_name,resp)

	def down_ts(self,ts_name,content):
		ts_path = os.path.join(self.m3u8_work_path,ts_name)
		with open(ts_path,"wb") as f:
			f.write(self.cryptor.decrypt(content))

	def ts2mp4(self,video_path):
		with open(video_path,"wb") as f1:
			for i in self.ts_list:
				with open(os.path.join(self.m3u8_work_path,i),"rb") as f2:
					d = f2.readlines()
					for _ in d:
						f1.write(_)
		print("\n",video_path,"下载完成")
		# 删除ts文件
		for i in self.ts_list:
			os.remove(os.path.join(self.m3u8_work_path,i))

		# 高码率m3u8文件
		os.remove(self.m3u8_path)
		# 删除目录
		os.rmdir(self.m3u8_work_path)
		time.sleep(1)

	def main(self,video_path,audio_matser_url):
		"""
		:params video_path:视频存储路径.H:\test.mp4
		:params audio_matser_url:视频地址
		"""
		# audio_matser_url-media_rates_url
		# 视频地址-码率链接列表(down)-高码率m3u8(down)-get加密key-下载ts(down)-合并ts
		# 存在则跳过SV流程
		if os.path.exists(video_path):
			print(video_path,"已存在")
			return
		self.ts_list = []
		self.sv_path = video_path.rsplit("\\",1)[0]
		video_id = audio_matser_url.split("video_id=")[-1]

		media_rates_url = self.get_m3u8_url(audio_matser_url)
		if media_rates_url == None:
			print("获取media_rates_url失败 audio_matser_url: ",audio_matser_url)
			return

		self.high_rate_m3u8_url = self.parse_rate(media_rates_url)
		if self.high_rate_m3u8_url == "":
			print("高码率视频m3u8链接获取失败 audio_matser_url: ",audio_matser_url)
			return

		# 高码率m3u8文件名称 20732994.m3u8
		self.high_rate_m3u8_name = self.high_rate_m3u8_url.split("?")[0].split("/")[-1]
		# 以m3u8文件名前缀创建临时目录 20732994
		self.m3u8_work_path = folder(self.sv_path,video_id)
		# 高码率m3u8文件存储路径
		self.m3u8_path = os.path.join(self.m3u8_work_path,self.high_rate_m3u8_name)
		# 下载高码率m3u8文件
		self.down(self.m3u8_path,network_connect(self.high_rate_m3u8_url).content)

		self.key_url,self.key = self.get_m3u8_key()
		if self.key == None:
			print("m3u8Key获取失败: ",self.key)
			return

		self.cryptor = AES.new(self.key, AES.MODE_CBC, self.key)
		self.get_ts()
		self.ts2mp4(video_path)