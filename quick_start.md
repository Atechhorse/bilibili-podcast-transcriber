# 快速开始指南

## 🚀 最快 5 分钟开始使用

如果你想快速验证项目是否可用，按以下步骤操作：

### 步骤 1: 安装系统依赖（必需）

```bash
# macOS
brew install ffmpeg

# 验证
ffmpeg -version
```

### 步骤 2: 安装 Python 依赖

**选项 A - 完整安装（实际使用）**
```bash
pip install -r requirements.txt
```
⚠️ 这需要 10-20 分钟，需要下载大量依赖

**选项 B - 快速体验（仅测试下载）**
```bash
pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp ffmpeg-python
```
✅ 只需 1-2 分钟，可以完成链接解析、元数据提取和音频下载

### 步骤 3: 配置 API Key

编辑 `config.yaml`，确保 DeepSeek API key 已填写：

```yaml
llm:
  api_key: "YOUR_DEEPSEEK_API_KEY"
```

### 步骤 4: 运行

```bash
cd src
python main.py
```

## ?? 你将得到什么

### 立即可用（选项 B）
- ✅ `data/links_summary.xlsx` - 所有链接的元数据表格（需求4）
- ✅ `data/downloads/` - 下载的音频文件
- ⏸️  转写功能将被跳过（因为没安装 Whisper 和 Pyannote）

### 完整功能（选项 A）
- ✅ 所有上述功能
- ✅ `data/transcripts/` - 完整的逐字稿（含说话人识别）
- ✅ `data/processing_result.xlsx` - 处理结果汇总

## 🎯 分阶段体验

### 阶段 1: 链接管理（5分钟）
安装: `pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp`

可以做:
- 解析和规范化链接
- 提取元数据
- 生成链接汇总表格

### 阶段 2: 音频下载（+5分钟）
再安装: `pip install ffmpeg-python`

可以做:
- 上述所有功能
- 下载 Bilibili 和小宇宙音频

### 阶段 3: 语音转写（+15分钟安装）
再安装: `pip install torch torchaudio openai-whisper`

可以做:
- 上述所有功能
- Whisper 语音转文字
- 生成基础逐字稿（无说话人分离）

### 阶段 4: 说话人识别（+10分钟安装 + 配置）
再安装: `pip install pyannote.audio`
配置: HuggingFace Token

可以做:
- **完整功能**
- 自动识别付鹏和其他说话人
- 生成完整的结构化逐字稿

## 💡 推荐流程

### 新手
1. 先运行阶段 1-2，验证下载功能
2. 查看 `data/links_summary.xlsx` 和音频文件
3. 如果满意，再逐步安装 Whisper 等重量级组件

### 熟练用户
1. 直接 `pip install -r requirements.txt`
2. 配置所有 tokens
3. 运行完整流程

## ⚠️ 注意事项

1. **Mac M 系列芯片**: torch 会自动支持 MPS 加速，无需额外配置
2. **Windows 用户**: 部分依赖可能需要 Visual C++ Build Tools
3. **网络问题**: 使用镜像源加速
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple [包名]
   ```
4. **首次运行 Whisper**: 会自动下载模型（约 1.5GB），需要等待

## 🆘 遇到问题？

运行环境检查:
```bash
python3 check_env.py
```

查看详细安装指南:
```bash
cat INSTALL.md
```

联系开发者或查看日志:
```bash
cat logs/app.log
```