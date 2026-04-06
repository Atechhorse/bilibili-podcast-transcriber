# 安装指南

## 前置要求

### 1. 安装 ffmpeg

**macOS**:
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

验证安装:
```bash
ffmpeg -version
```

### 2. 安装 Python 依赖

#### 方法一：完整安装（推荐用于实际使用）

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 升级 pip
pip install --upgrade pip

# 安装依赖（这可能需要 10-20 分钟）
pip install -r requirements.txt
```

#### 方法二：快速验证（仅测试链接解析等基础功能）

```bash
# 最小依赖集
pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp
```

### 3. 配置 API 和 Token

编辑 `config.yaml`:

```yaml
# HuggingFace Token
# 1. 访问 https://huggingface.co/settings/tokens
# 2. 创建新 token
# 3. 访问 https://huggingface.co/pyannote/speaker-diarization-3.1
# 4. 点击 "Agree and access repository"
huggingface_token: "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# LLM API (已配置 DeepSeek)
llm:
  provider: "deepseek"
  model: "deepseek-chat"
  api_key: "YOUR_DEEPSEEK_API_KEY"
  base_url: "https://api.deepseek.com"

# Whisper 配置
whisper:
  model_size: "medium"  # 可选: tiny, base, small, medium, large
  device: "auto"  # auto 会自动检测 CUDA/MPS/CPU
```

### 4. 验证安装

```bash
# 检查环境
python3 check_env.py

# 运行基础测试
python3 test_basic.py
```

## 常见问题

### Q1: torch 安装失败或太慢

**解决方案**：使用清华镜像源

```bash
pip install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
```

对于 Mac M 系列芯片:
```bash
pip install torch torchaudio
```

### Q2: pyannote.audio 安装失败

**解决方案**：
```bash
# 先安装 torch
pip install torch torchaudio

# 再安装 pyannote
pip install pyannote.audio
```

### Q3: whisper 下载模型失败

**解决方案**：手动下载模型
```bash
# 模型会自动下载到 ~/.cache/whisper/
# 如果网络问题，可以手动下载后放到该目录
```

### Q4: yt-dlp 下载失败

**可能原因**：
- 网络问题
- 视频有地区限制
- 需要登录 (B站某些视频)

**解决方案**：
```bash
# 使用代理
export ALL_PROXY=socks5://127.0.0.1:1080

# 或使用 cookies (需要登录 B站后导出 cookies)
yt-dlp --cookies cookies.txt [URL]
```

## 分步骤安装（如果完整安装失败）

### 第一步：基础依赖

```bash
pip install pyyaml requests beautifulsoup4 pandas openpyxl
```

### 第二步：下载工具

```bash
pip install yt-dlp
```

### 第三步：音频处理

```bash
pip install ffmpeg-python
```

### 第四步：深度学习框架

```bash
# Mac M 系列
pip install torch torchaudio

# NVIDIA GPU
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CPU only
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### 第五步：语音识别

```bash
pip install openai-whisper
```

### 第六步：说话人分离

```bash
pip install pyannote.audio
```

## 快速开始（最小功能）

如果只想测试链接解析和元数据提取（不做转写）:

```bash
# 最小依赖
pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp

# 修改 config.yaml，将 huggingface_token 设为 null
# 这样会跳过说话人分离，但仍可以下载音频
```

然后运行:
```bash
cd src
python main.py
```

程序会下载音频，但会跳过转写步骤。