# B站视频下载方案总结

**更新时间**: 2026-01-13  
**当前状态**: 已集成多种备用方案

---

## 📊 当前系统能力

### ✅ 已实现
1. **小宇宙播客下载** - 100% 成功（17/17）
2. **B站下载器（多层备用）**:
   - 主方案：yt-dlp + cookies
   - 备用方案1：在线API下载器
   - 备用方案2：B站公开API（部分视频）

---

## 🔧 B站下载方案对比

### 方案1：yt-dlp + Cookies（主方案）

**优点**：
- 高质量、支持1080P+
- 稳定可靠
- 已集成到系统

**缺点**：
- 需要手动导出cookies
- 需要B站账号

**使用方法**：
1. 导出cookies.txt到项目根目录
2. 正常运行程序即可

详见：`BILIBILI_DOWNLOAD_GUIDE.md`

---

### 方案2：在线下载器（新增备用）

**优点**：
- 无需cookies
- 自动备用，yt-dlp失败时自动切换
- 适合部分公开视频

**缺点**：
- 画质可能较低
- 成功率不如cookies方案
- 依赖第三方API稳定性

**实现代码**：
- `src/bilibili_online_downloader.py`
- 已自动集成到 `src/downloader.py`

---

### 方案3：BBDown（外部工具）

**优点**：
- 专为B站设计
- 功能强大
- 支持4K、杜比音效

**缺点**：
- 需要单独安装
- 命令行操作
- 未集成到自动化流程

**手动使用**：
```bash
# 安装（如果brew install失败，可以从GitHub下载）
brew install nilaoda/homebrew-tap/BBDown

# 登录
BBDown login

# 下载音频
BBDown -ia https://www.bilibili.com/video/BV14RrKBNEdH/
```

---

### 方案4：在线网站下载

**推荐网站**：
- https://weibomiaopai.com/online-video-downloader/bilibili
- https://www.videofk.com/

**优点**：
- 完全不需要安装
- 浏览器直接操作
- 零技术门槛

**缺点**：
- 需要手动操作每个视频
- 无法批量处理
- 画质可能受限

---

## 🎯 推荐使用策略

### 策略A：追求质量和效率（推荐）
1. 导出一次cookies.txt
2. 运行程序，全自动处理
3. 适合：批量下载、长期使用

### 策略B：快速尝试
1. 直接运行程序
2. 让系统自动尝试在线下载器
3. 适合：少量视频、临时需求

### 策略C：手动控制
1. 使用BBDown或在线网站
2. 逐个下载后放入 `data/downloads/`
3. 适合：对画质有特殊要求

---

## 💡 实际操作建议

### 对于你的27个链接

**小宇宙（17个）** ✅
- 已全部下载成功
- 无需额外操作

**B站（10个）** ⏸️

**选项1 - 自动化（推荐）**：
```bash
# 1. 导出cookies（一次性）
# 使用浏览器扩展导出到项目根目录

# 2. 运行程序
cd src
/opt/anaconda3/bin/python main_simple.py --input ../视频链接
```

**选项2 - 无cookies尝试**：
```bash
# 直接运行，系统会自动尝试备用方案
cd src
/opt/anaconda3/bin/python main_simple.py --input ../视频链接
```
注：成功率可能较低，但无需cookies

**选项3 - 手动下载**：
- 使用在线网站逐个下载
- 或使用BBDown工具

---

## 🔍 故障排查

### 问题1：yt-dlp返回412错误
**原因**：B站反爬虫  
**解决**：导出cookies.txt

### 问题2：在线下载器也失败
**原因**：视频需要会员或有地区限制  
**解决**：使用手动方案或BBDown

### 问题3：cookies过期
**解决**：重新登录B站并导出新的cookies

---

## 📈 当前进度

```
总链接: 27个
├─ 小宇宙: 17个 ✅ (100% 完成)
└─ B站: 10个 ⏸️ (等待处理)
```

**已生成文件**：
- ✅ `src/data/links_summary.xlsx` - 元数据表格
- ✅ `src/data/downloads/` - 17个小宇宙音频（790MB）

---

## 🚀 下一步行动

**立即可做**：
1. 尝试运行程序，让系统自动尝试在线下载B站视频
2. 或参考`BILIBILI_DOWNLOAD_GUIDE.md`配置cookies

**长期建议**：
- 保存一份cookies.txt以备后用
- 定期更新（cookies会过期）

---

**提示**：目前17个小宇宙播客已经包含了大量付鹏的内容，可以先从这些开始！