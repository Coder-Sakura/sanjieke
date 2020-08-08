## 三节课平台——课程爬虫

做个简单说明，代码供参考

+ 下载m3u8视频流，合并为mp4
+ 提取每节课内容为docx
+ 按课程目录存储
+ 简单配置存储目录，课程地址和cookie即可
+ 多线程提取docx和视频信息，再进行视频下载



## 配置

1. 存储目录：main_sjk.py——Pivot类中打的root_path

2. cookie：sjk_public.py——network_connect

3. 课程链接
   直接在main_sjk中调用即可

   ```python
   if __name__ == '__main__':
   	class_url = url
   	p = Pivot(class_url)
   	p.main()
   
   ```

   