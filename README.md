# 视频/播客音频转写工具

**[English](#english) | [中文](#中文)**

---

<a name="中文"></a>
## 中文介绍

自动批量下载 Bilibili 视频和小宇宙播客的音频，并生成带说话人标注的中文逐字稿。

### 功能特性

- **多平台支持**：自动识别 Bilibili 视频链接和小宇宙播客链接
- **高精度中文转写**：集成 FunASR，中文识别准确率 98%+，金融/经济专业术语识别效果好
- **说话人识别**：自动区分主讲人和其他说话人，支持自定义主讲人姓名
- **情感识别**：标注每段话的情感状态（NEUTRAL / HAPPY / ANGRY / SAD）
- **断点续传**：处理中断后可从上次进度继续，不重复下载
- **长音频处理**：自动对超长音频分段处理
- **结构化输出**：生成 Markdown 逐字稿 + Excel 汇总报告
- **双引擎备选**：FunASR（中文推荐）+ Whisper（多语言备用）

### 处理流程

```
输入链接文件 → 解析链接 → 下载音频 → 语音转写 → 说话人识别 → 生成逐字稿
```

### 环境要求

- Python 3.9+
- ffmpeg
- 推荐：M1/M2/M3 Mac（MPS 加速）或 NVIDIA GPU（CUDA 加速）
- 最低 8GB RAM

### 安装

```bash
# 1. 安装 ffmpeg
brew install ffmpeg          # macOS
sudo apt-get install ffmpeg  # Linux

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置
cp config.yaml.example config.yaml
# 编辑 config.yaml，填入你的 API Key
```

### 配置说明

编辑 `config.yaml`：

```yaml
# 选择 ASR 引擎（推荐 funasr 用于中文）
asr_engine: "funasr"

# DeepSeek API Key（用于说话人身份推理）
llm:
  api_key: "YOUR_DEEPSEEK_API_KEY"

# HuggingFace Token（使用 Whisper 模式时需要）
huggingface_token: "YOUR_HUGGINGFACE_TOKEN"
```

- DeepSeek API Key：[platform.deepseek.com](https://platform.deepseek.com)
- HuggingFace Token：[huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)（需同意 pyannote/speaker-diarization-3.1 协议）

### 使用方法

在链接文件（默认名为 `视频链接`）中每行放一个链接，然后运行：

```bash
cd src

# 基本运行
python main.py --input ../视频链接

# 中断后续传
python main.py --resume

# 仅重试失败的链接
python main.py --retry-failed

# 强制重新处理全部
python main.py --force
```

### 输出结果

```
data/
├── transcripts/         # Markdown 格式逐字稿，每个视频一个文件
├── downloads/           # 下载的音频文件（处理后可删除）
└── processing_result.xlsx  # 处理汇总报告
```

逐字稿格式示例：

```
[00:01:23] 主讲人：最近市场波动很大，我们来看一下...
[00:02:45] 其他：请问您怎么看待当前的通胀压力？
[00:03:10] 主讲人：这个问题很好，我认为...
```

### FunASR vs Whisper 对比

| 指标 | FunASR | Whisper |
|------|--------|---------|
| 中文准确率 | 98–99% | 92–94% |
| 说话人分离 | 内置支持 | 需 pyannote |
| 情感识别 | 支持 | 不支持 |
| 推理速度 | 快 | 中等 |
| 多语言 | 以中文为主 | 100+ 语言 |

### 注意事项

本工具仅供个人学习和研究使用。下载和转写的内容版权归原作者所有，请勿将生成内容用于商业用途或二次传播。

---

<a name="english"></a>
## English

A tool to automatically download audio from Bilibili videos and Xiaoyuzhou podcasts, then generate timestamped transcripts with speaker identification.

### Features

- **Multi-platform**: Supports Bilibili video links and Xiaoyuzhou podcast links
- **High-accuracy Chinese ASR**: Powered by FunASR with 98%+ accuracy on Chinese, including financial and economic terminology
- **Speaker diarization**: Automatically distinguishes the main speaker from others; speaker name is configurable
- **Emotion tagging**: Labels each utterance with emotion (NEUTRAL / HAPPY / ANGRY / SAD)
- **Resume support**: Picks up where it left off after interruption; no redundant downloads
- **Long audio handling**: Automatically splits audio that exceeds a configurable threshold
- **Structured output**: Generates Markdown transcripts + Excel summary report
- **Dual ASR engine**: FunASR (recommended for Chinese) + Whisper (multilingual fallback)

### Pipeline

```
Link file → Parse links → Download audio → Transcribe → Speaker ID → Generate transcript
```

### Requirements

- Python 3.9+
- ffmpeg
- Recommended: Apple Silicon Mac (MPS) or NVIDIA GPU (CUDA)
- Minimum 8GB RAM

### Installation

```bash
# 1. Install ffmpeg
brew install ffmpeg          # macOS
sudo apt-get install ffmpeg  # Linux

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp config.yaml.example config.yaml
# Edit config.yaml and fill in your API keys
```

### Configuration

Edit `config.yaml`:

```yaml
# ASR engine (funasr recommended for Chinese)
asr_engine: "funasr"

# DeepSeek API Key (used for speaker identity inference)
llm:
  api_key: "YOUR_DEEPSEEK_API_KEY"

# HuggingFace Token (required for Whisper mode)
huggingface_token: "YOUR_HUGGINGFACE_TOKEN"
```

- DeepSeek API Key: [platform.deepseek.com](https://platform.deepseek.com)
- HuggingFace Token: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — must accept the pyannote/speaker-diarization-3.1 license

### Usage

Put one link per line in your link file (default filename: `视频链接`), then run:

```bash
cd src

# Basic run
python main.py --input ../视频链接

# Resume after interruption
python main.py --resume

# Retry failed links only
python main.py --retry-failed

# Force reprocess everything
python main.py --force
```

### Output

```
data/
├── transcripts/            # One Markdown transcript per video
├── downloads/              # Downloaded audio (can be deleted after processing)
└── processing_result.xlsx  # Summary report
```

Sample transcript format:

```
[00:01:23] Speaker: The market has been volatile lately. Let's take a look...
[00:02:45] Other: How do you view the current inflationary pressure?
[00:03:10] Speaker: That's a great question. I think...
```

### FunASR vs Whisper

| Metric | FunASR | Whisper |
|--------|--------|---------|
| Chinese accuracy | 98–99% | 92–94% |
| Speaker diarization | Built-in | Requires pyannote |
| Emotion recognition | Yes | No |
| Inference speed | Fast | Moderate |
| Multilingual | Mainly Chinese | 100+ languages |

### Disclaimer

This tool is for personal learning and research only. All downloaded and transcribed content is copyrighted by the original creators. Do not use generated content for commercial purposes or redistribution.

### License

MIT
