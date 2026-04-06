# 🎉 开始使用 - 付鹏视频/播客处理系统

## 👋 欢迎

恭喜！你的视频/播客音频提取与逐字稿生成系统已经完全搭建完成。

## 📦 项目已完成

✅ **需求 1**: Bilibili 视频音频提取   
✅ **需求 2**: 小宇宙播客音频提取  
✅ **需求 3**: 音频转逐字稿 + 说话人区分（付鹏 vs 其他）  
✅ **需求 4**: 链接反向提取，生成元数据表格  

## 🚀 三步开始

### 第 1 步：安装 ffmpeg（必需）

**macOS**:
```bash
brew install ffmpeg
```

验证：
```bash
ffmpeg -version
```

### 第 2 步：安装 Python 依赖

**快速体验版**（仅元数据提取 + 音频下载，5分钟）:
```bash
pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp ffmpeg-python
```

**完整功能版**（包含语音转写，15-20分钟）:
```bash
pip install -r requirements.txt
```

### 第 3 步：运行

```bash
cd src
python main.py
```

就这么简单！系统会自动处理 `视频链接` 文件中的所有链接。

## 📊 你将得到什么

处理完成后，在 `data/` 目录下：

1. **links_summary.xlsx** ← 需求4的输出
   - 所有链接的元数据汇总表
   - 包含：平台、标题、作者、时长等

2. **downloads/** 
   - 所有下载的音频文件（mp3格式）

3. **transcripts/**
   - 每个音频的逐字稿（Markdown格式）
   - 含时间戳和说话人标识

4. **processing_result.xlsx**
   - 处理结果汇总报告

## 🎯 关键特性

### 智能说话人识别
- **单人场景**：自动识别为"付鹏"
- **多人对话**：使用 DeepSeek AI 分析前5分钟对话，智能识别付鹏

### 断点续传
- 随时可以 Ctrl+C 中断
- 再次运行自动从中断处继续
- 不会重复处理已完成的内容

### 长音频优化
- 自动分段处理超过30分钟的音频
- 避免内存溢出
- 保持时间戳连贯

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| **START_HERE.md** | ?? 本文档，快速开始指南 |
| README.md | 项目完整说明 |
| INSTALL.md | 详细安装步骤和故障排查 |
| quick_start.md | 分阶段体验指南 |
| USAGE_EXAMPLE.md | 使用场景和命令示例 |
| PROJECT_SUMMARY.md | 项目技术总结 |
| CHECKLIST.md | 使用前检查清单 |

## 🔧 重要配置

### config.yaml

已为你配置好 DeepSeek API：
```yaml
llm:
  api_key: "YOUR_DEEPSEEK_API_KEY"
```

**可选配置**（提升说话人识别准确度）:
```yaml
huggingface_token: "hf_xxxxx"
```
获取方式：https://huggingface.co/settings/tokens

## ⚡️ 快速命令

```bash
# 检查环境是否就绪
python3 check_env.py

# 初始化目录结构
python3 setup_dirs.py

# 运行主程序
cd src && python main.py

# 中断后继续
python main.py --resume

# 重试失败的链接
python main.py --retry-failed

# 查看日志
tail -f ../logs/app.log
```

## 💡 使用建议

### 第一次使用
1. 先用前 2 个链接测试
   ```bash
   head -2 视频链接 > test.txt
   python main.py --input ../test.txt
   ```

2. 查看生成的文件确认无误

3. 再处理完整的 53 个链接
   ```bash
   python main.py --input ../视频链接
   ```

### 性能优化
- **Mac M 系列**：自动使用 MPS 加速，速度很快
- **纯 CPU**：可能需要数小时，建议降低模型大小
  ```yaml
  whisper:
    model_size: "small"  # 从 medium 改为 small
  ```

## ⏱️ 预计耗时

处理 53 个链接（M1 Mac 参考）：

| 阶段 | 耗时 |
|------|------|
| 元数据提取 | ~2 分钟 |
| 音频下载 | ~1-2 小时 |
| 语音转写 | ~4-5 小时 |
| **总计** | **~5-7 小时** |

💡 **提示**：可以在后台运行，或分批处理。

## ❓ 遇到问题？

1. **运行环境检查**
   ```bash
   python3 check_env.py
   ```

2. **查看详细日志**
   ```bash
   cat logs/app.log
   ```

3. **查看故障排查指南**
   ```bash
   cat INSTALL.md
   ```

## 🎊 准备好了吗？

```bash
# 一键启动！
cd src && python main.py
```

---

**祝使用愉快！如有问题请查看文档或检查日志。** 🚀

---

## 📂 项目结构速览

```
付鹏/
├── 视频链接                    # 📥 输入：53个待处理链接
├── config.yaml                 # ⚙️ 配置文件（已配置 DeepSeek）
├── requirements.txt            # 📦 Python 依赖列表
│
├── START_HERE.md               # 👈 本文档
├── README.md                   # 📖 完整文档
├── INSTALL.md                  # 🔧 安装指南
├── quick_start.md              # ⚡️ 快速开始
│
├── src/                        # 💻 源代码
│   ├── main.py                 # 主程序入口
│   ├── parser.py               # 链接解析
│   ├── metadata_extractor.py   # 元数据提取
│   ├── downloader.py           # 音频下载
│   ├── transcriber.py          # 语音转写
│   ├── reporter.py             # 报告生成
│   └── utils/                  # 工具模块
│
└── data/                       # 📊 输出目录
    ├── links_summary.xlsx      # ✅ 需求4：元数据表格
    ├── processing_result.xlsx  # 处理结果汇总
    ├── downloads/              # 音频文件
    └── transcripts/            # 逐字稿（Markdown）
```