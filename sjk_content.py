import re
import os
import time
from docx import Document
# 修改段前 段后间距
from docx.shared import Pt
# 居中
from docx.enum.text import WD_ALIGN_PARAGRAPH
# 修改字体
from docx.oxml.ns import qn

class SJK_CONTENT:
	def remove_label(self,text_content):
		"""
		过滤文本
		:params text_content:待替换文本列表
		:return :list
		"""
		# 取出图片链接
		img_regular = re.compile(r""".*?src=['"](.*?)['"].*?""")
		# 去除转义字符,\n \a \t
		escape_regular = re.compile(r"[\a\b\f\n\t\r\v\\]")
		# 去除html标签
		html_regular = re.compile(r"<[^>]+>",re.S)
		# 去除utf编码保存文件导致出现的\ufeff
		bom_regular = re.compile(u"[\ufeff]+",re.S)

		res = []
		for text in text_content:
			# 匹配src链接
			if "src" in text and "img" in text:
				img = re.findall(img_regular,text.replace(" ",""))
				for i in img:
					res.append(i)
			# 去除转义字符
			text = re.sub(escape_regular,"",text)
			# 去除html标签
			text = re.sub(html_regular,"",text)
			# 去除utf编码保存文件导致出现的\ufeff
			text = re.sub(bom_regular,"",text)
			if text != "":
				res.append(text)

		return res

	def write_docx(self,section_name,docx_path,new_text_content):
		"""
		章节文档写入docx
		:params docx_path: docx存储路径
		:params new_text_content: 过滤过的内容
		:return : None
		"""
		# 解决了写入标题都是同一个标题的Bug
		document = Document()
		# 添加标题0,居中
		head = document.add_heading(section_name,0)
		head.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER

		# 更改Normal样式,正文
		document.styles['Normal'].font.name = u'仿宋'
		document.styles['Normal']._element.rPr.rFonts.set(qn('w:eastAsia'), u'仿宋')

		for _ in new_text_content:
			paragraph = document.add_paragraph(_,'Normal')
			paragraph.paragraph_format.space_before = Pt(20)
		document.save(docx_path)
		print(docx_path,"下载完成")
		time.sleep(1)

	def main(self,section_name,docx_path,text_content):
		# 先正则过滤,再写入
		# 不存在则进行SC流程
		if os.path.exists(docx_path):
			print(docx_path,"已存在")
			return

		new_text_content = self.remove_label(text_content)
		self.write_docx(section_name,docx_path,new_text_content)