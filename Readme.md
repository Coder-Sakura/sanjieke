## 三节课平台——课程爬虫

> **此仓库仅做学习参考使用**



### 爬虫功能

+ 下载m3u8视频流，合并为mp4
+ 提取每节课内容为docx
+ 按课程目录存储
+ 简单配置存储目录，课程地址和cookie即可
+ 多线程提取docx和视频信息，再进行视频下载



### 预览

![](https://i.loli.net/2020/08/15/zJW51VfQABTqPv2.png)

> 以“运营新人启航计划（第十期）”为参考目标，下载后的目录如图



### 如何使用

1. 填写存储路径：

   ```python
   # main_sjk.py--self.root_path
   self.root_path = r"G:\your_path"
   ```

   

2. 填写三节课平台cookie：

   ```python
   # sjk_public.py--network_connect
   headers = {
   	"cookie": your_cookie,
   	"user-agent": your_user_agent
   }
   ```

   

3. 开始使用

   ```python
   # main_sjk.py
   if __name__ == '__main__':
       class_url = your_url
       p = Pivot(class_url)
       p.main()
   ```
   
4. 安装依赖

   ```bash
   pip install -r requirements.txt
   ```

   或

   ```bash
   pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com
   ```

5. 终端运行

   ```bash
   Python main_sjk.py
   ```



### 注意事项

+ 如果遇到Crypto库安装不上的情况，以下方案仅供参考：

  + window

    ```bash
    pip install crypto pycryptodome
    pip uninstall crypto pycryptodome
    pip install pycryptodome
    ```

  + Linux

    ```bash
    pip install pycryptodome
    ```

+ 本仓库仅在Windows系统上进行过裸机测试。



### 最后

+ 本仓库建立的缘由是为了帮助某位协会成员解决缓存需求，除此之外，能帮助到其他需要帮助的人也非常开心
+ 欢迎大家 :star: Star，Pr 和 Issue