# FunASR 快速开始指南 🚀

5分钟快速上手，体验98%+的中文识别准确率！

---

## 📋 前置条件检查

```bash
# 检查Python版本（需要3.9+）
python3 --version

# 检查是否在虚拟环境中
which python
```

---

## ⚡ 快速安装（3步完成）

### 步骤1: 安装FunASR依赖
```bash
bash install_funasr.sh
```

### 步骤2: 配置ASR引擎
编辑 `config.yaml`，确保第一行是：
```yaml
asr_engine: "funasr"  # 使用FunASR
```

### 步骤3: 测试安装
```bash
python test_funasr_integration.py
```

看到以下输出说明安装成功：
```
✓ FunASR模型加载
✓ 语音转写
✓ 说话人分离
✓ 情感识别
✓ 逐字稿生成
```

---

## 🎯 立即使用

### 方式1: 使用现有音频测试

```bash
# 使用项目中的样本音频
python test_funasr_integration.py
```

### 方式2: 处理你的链接

```bash
# 1. 编辑 视频链接 文件，添加你的链接
vim 视频链接

# 2. 运行主程序
cd src
python main.py
```

---

## 📊 查看结果

### 1. 逐字稿
```bash
# 在 data/transcripts/ 目录下
ls data/transcripts/

# 查看内容
cat data/transcripts/xiaoyuzhou_*_transcript.md
```

### 2. Excel汇总表
```bash
# 打开元数据表
open data/links_summary.xlsx

# 打开处理结果
open data/processing_result.xlsx
```

---

## 🔄 对比Whisper和FunASR

### 运行对比测试
```bash
# 使用FunASR
python test_funasr_integration.py

# 查看对比报告
cat whisper_vs_funasr_comparison.md
```

### 关键差异

| 方面 | Whisper tiny | FunASR |
|------|-------------|---------|
| "有朋自远方来" | ❌ "有彭自元方" | ✅ 正确 |
| "金融炼药师" | ❌ "进入恋药师" | ✅ 正确 |
| "小酌微醺" | ❌ "小卓微薰" | ✅ 正确 |
| 标点符号 | ⚠️ 部分缺失 | ✅ 完整 |

---

## ⚙️ 常用配置

### 启用/禁用功能

编辑 `config.yaml`：

```yaml
funasr:
  enable_speaker_diarization: true   # 说话人分离
  enable_emotion: true               # 情感识别
  enable_itn: true                   # 文本规整
```

### 切换设备

```yaml
funasr:
  device: "auto"   # 自动选择
  # device: "cpu"   # CPU模式（慢但稳定）
  # device: "mps"   # Apple Silicon加速
  # device: "cuda"  # NVIDIA GPU加速
```

---

## 🐛 遇到问题？

### 问题1: 模型下载很慢
**解决**: 首次下载需要约500MB，耐心等待。后续运行会使用缓存。

### 问题2: 内存不足
**解决**: 
```yaml
funasr:
  max_single_segment_time: 15000  # 减小分段大小
```

### 问题3: 找不到音频文件
**解决**: 确保音频文件路径正确，使用绝对路径或相对于项目根目录的路径。

---

## 📚 下一步

1. ✅ 阅读完整文档: [FUNASR_INTEGRATION.md](FUNASR_INTEGRATION.md)
2. ✅ 查看对比测试: [whisper_vs_funasr_comparison.md](whisper_vs_funasr_comparison.md)
3. ✅ 开始处理你的音频！

---

## 💡 专业提示

1. **提高准确率**: 使用高质量音频（清晰、无噪音）
2. **加速处理**: 使用GPU加速（MPS或CUDA）
3. **批量处理**: 一次添加多个链接，系统会自动处理
4. **断点续传**: 中断后直接重新运行，自动跳过已完成的

---

## 🎉 完成！

你现在已经可以使用FunASR处理中文音频了！

有问题？查看 [常见问题](FUNASR_INTEGRATION.md#-常见问题)