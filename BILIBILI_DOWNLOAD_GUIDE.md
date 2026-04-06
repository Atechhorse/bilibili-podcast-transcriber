# B站视频下载问题解决指南

## 问题说明

B站有严格的反爬虫机制，直接使用 yt-dlp 会遇到 **HTTP 412 错误**。

## 解决方案

### 方案1：使用 Cookies（推荐，最有效）

#### 步骤1：导出 Cookies

1. **安装浏览器扩展**
   - Chrome/Edge: 搜索 "Get cookies.txt LOCALLY" 扩展并安装
   - Firefox: 搜索 "cookies.txt" 扩展并安装

2. **导出 Cookies**
   - 在浏览器中登录 bilibili.com
   - 点击扩展图标
   - 选择"Export" 导出 cookies.txt
   - 将文件保存到项目根目录（与 config.yaml 同级）

#### 步骤2：运行下载程序

```bash
cd /Users/mating05/Documents/个人学习/付鹏/src
/opt/anaconda3/bin/python main_simple.py --input ../视频链接
```

程序会自动检测并使用 cookies.txt 文件。

---

### 方案2：手动下载（最简单，但需要手动操作）

如果方案1不work，可以手动下载：

#### 使用 BBDown（推荐）

```bash
# 安装 BBDown
brew install nilaoda/homebrew-tap/BBDown

# 登录
BBDown login

# 下载音频
BBDown -ia https://www.bilibili.com/video/BV14RrKBNEdH/
```

#### 使用浏览器直接下载

1. 打开浏览器，登录 B站
2. 播放视频
3. 打开开发者工具（F12）→ Network 标签
4. 筛选 m4s 或 mp4 文件
5. 找到音频流，右键复制链接
6. 使用下载工具下载
7. 将文件重命名并放到 `data/downloads/` 目录

---

### 方案3：使用小宇宙链接（B站链接的替代）

小宇宙播客通常不需要登录，下载成功率更高。

当前你的 27 个链接中：
- 10 个 B站链接（可能失败）
- 17 个小宇宙链接（成功率高）

建议：
1. 先处理小宇宙链接
2. 对于B站链接，使用方案1或2

---

## 当前项目状态

### ✅ 已完成
- 完整的项目代码
- 所有Python依赖
- ffmpeg 安装
- 视频链接文件（27个链接）

### ⏸️ 待解决
- B站 cookies 配置（用于下载）
- 或使用替代方案手动下载

### 📊 下一步

**如果你有B站账号：**
1. 导出 cookies.txt 到项目根目录
2. 运行程序即可

**如果暂时不想处理B站：**
```bash
# 只处理小宇宙链接
grep xiaoyuzhou 视频链接 > xiaoyuzhou_only.txt
cd src
/opt/anaconda3/bin/python main_simple.py --input ../xiaoyuzhou_only.txt
```

---

## 测试单个链接

```bash
# 测试小宇宙链接（应该能成功）
echo "https://www.xiaoyuzhoufm.com/episode/69377c0c3fec3166cfff72fd" > test_xiaoyuzhou.txt
cd src
/opt/anaconda3/bin/python main_simple.py --input ../test_xiaoyuzhou.txt
```

---

## 需要帮助？

查看日志文件：
```bash
tail -f logs/app.log
```

---

**提示**：小宇宙链接不需要 cookies，建议先测试小宇宙链接来验证系统正常工作。