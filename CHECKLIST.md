# 使用前检查清单

## ✅ 环境准备

### 系统依赖
- [ ] 已安装 ffmpeg
  ```bash
  ffmpeg -version
  ```
  如未安装: `brew install ffmpeg` (macOS)

### Python 环境
- [ ] Python 版本 >= 3.9
  ```bash
  python3 --version
  ```

- [ ] 已创建虚拟环境（可选但推荐）
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Python 依赖
- [ ] 已安装基础依赖（必需）
  ```bash
  pip install pyyaml requests beautifulsoup4 pandas openpyxl yt-dlp ffmpeg-python
  ```

- [ ] 已安装完整依赖（转写功能）
  ```bash
  pip install -r requirements.txt
  ```

## ✅ 配置文件

### config.yaml 检查
- [ ] 文件存在
- [ ] DeepSeek API key 已填写（已提供）
  ```yaml
  llm:
    api_key: "YOUR_DEEPSEEK_API_KEY"
  ```

- [ ] HuggingFace token（可选，用于说话人分离）
  ```yaml
  huggingface_token: "hf_xxxxx"  # 从 https://huggingface.co/settings/tokens 获取
  ```

## ✅ 输入数据

- [ ] `视频链接` 文件存在
- [ ] 文件包含有效的 Bilibili 或小宇宙链接
- [ ] 检查文件编码为 UTF-8

## ✅ 输出目录

- [ ] 已运行初始化脚本
  ```bash
  python3 setup_dirs.py
  ```

- [ ] 以下目录已创建：
  - data/
  - data/downloads/
  - data/temp/
  - data/transcripts/
  - logs/

## ✅ 环境验证

- [ ] 已运行环境检查
  ```bash
  python3 check_env.py
  ```

- [ ] 已运行基础测试（可选）
  ```bash
  python3 test_basic.py
  ```

## ✅ 首次运行

### 建议流程
1. [ ] 先测试 1-2 个链接
   ```bash
   # 创建测试文件
   head -2 视频链接 > test_links.txt
   cd src
   python main.py --input ../test_links.txt
   ```

2. [ ] 检查输出结果
   - [ ] data/links_summary.xlsx 已生成
   - [ ] data/downloads/ 有音频文件
   - [ ] 日志正常（logs/app.log）

3. [ ] 确认无误后处理全部链接
   ```bash
   python main.py --input ../视频链接
   ```

## ⚠️ 预期问题

### 常见情况
- [ ] 了解首次运行 Whisper 会下载模型（~1.5GB）
- [ ] 了解完整处理 53 个链接需要数小时
- [ ] 了解某些视频可能因地区限制下载失败
- [ ] 了解可以随时 Ctrl+C 中断，下次自动继续

### 性能调优
- [ ] 如果内存不足，调小 Whisper 模型
  ```yaml
  whisper:
    model_size: "small"  # 或 "base"
  ```

- [ ] 如果速度太慢，使用 GPU/MPS
  ```yaml
  whisper:
    device: "auto"  # 自动检测最佳设备
  ```

## 📊 输出检查

处理完成后验证：

- [ ] data/links_summary.xlsx
  - 包含所有链接的元数据
  - 列包括：平台、ID、标题、作者等

- [ ] data/downloads/
  - 每个成功的链接对应一个音频文件
  - 文件大小合理（通常 20-100MB）

- [ ] data/transcripts/
  - 每个成功转写的音频对应一个 .md 文件
  - 包含时间戳和说话人标识

- [ ] data/processing_result.xlsx
  - 汇总所有链接的处理状态
  - 记录成功/失败情况

- [ ] logs/app.log
  - 详细的处理日志
  - 可用于排查问题

## 🎯 快速命令参考

```bash
# 完整流程
cd src && python main.py

# 继续中断的任务
python main.py --resume

# 重试失败的
python main.py --retry-failed

# 强制重新开始
python main.py --force

# 检查环境
python3 check_env.py

# 查看日志
tail -f logs/app.log

# 清理临时文件
rm -rf data/temp/*
```

## ✨ 完成标志

当你看到以下内容时，表示成功：

```
============================================================
处理完成！
============================================================
元数据表格: data/links_summary.xlsx
处理结果: data/processing_result.xlsx
音频文件: data/downloads/
逐字稿: data/transcripts/
```

---

**准备好了吗？运行 `cd src && python main.py` 开始吧！** 🚀