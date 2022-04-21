## 三节课平台——课程爬虫

> **此仓库仅做学习交流参考使用**



### 功能/Feat

---

- [x] 发现课程页下载（`vip`视频需要登录`vip`账号）
- [x] 支持账号密码形式登录（推荐）
- [x] 支持cookie登录
- [x] 支持下载`m3u8`视频流合并为`mp4`输出
- [x] 支持课程文档内容生成为`docx`（图片插入）
- [x] 多线程下载

</br>

### TODO

---

- [ ] 指定课程下载

</br>

### 如何使用/Usage

---

#### 安装Python

略

</br>

#### 安装第三方依赖

```bash
# 更新pip 可选
pip install --upgrade pip
# 安装第三方库
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```

</br>

#### 填写配置

---

打开`sanjieke/sjk_tool.py`

**ROOT_PATH**
填写课程下载目录

```python
# LINE - 24
# 用户自定义下载目录
ROOT_PATH = r"your path"
```

</br>

**START_PAGE** (可选)
用户自定义下载开始页数

```python
# LINE - 27
# 用户自定义下载开始页数
START_PAGE = 1
```

</br>

**登录方式**  (重要)
支持账号密码 (推荐) 或cookie

```python
# 登录方式1 - 账号&密码(推荐)
USER_PHONE = "your phone"
USER_PASSWD = "your pwd"

# 登录方式2 - COOKIE
USER_COOKIE = ""
```

</br>

**终端运行**

```bash
python main.py
```

</br>

### 预览/Preview

+ 下图为<产品经理进阶课>该门课程下载完毕后的目录结构
+ https://www.sanjieke.cn/course/detail/sjk/8000028

![](https://s2.loli.net/2022/04/21/dYfWuTHbaemzSZr.png)



### 注意事项/Tips

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

+ 该`repo`仅在`Windows`系统进行虚拟环境测试



### 最后/Last

+ 该`repo`仅用于学习交流使用
+ 欢迎 :star: `Star`，提`Pr `和` Issue`，共勉！