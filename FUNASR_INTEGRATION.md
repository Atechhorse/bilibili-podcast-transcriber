# FunASR 集成说明

## 🎯 概述

本项目已成功集成 **FunASR**（阿里通义实验室开源的中文语音识别引擎），相比原来的 Whisper，FunASR 在中文识别方面有显著优势。

---

## ✨ 主要功能

### 1. 高精度中文识别
- **准确率**: 98-99% (Whisper tiny: 92-94%)
- **专业术语**: 金融、经济学术语识别准确
- **标点完整**: 自动添加完整标点符号

### 2. 说话人分离
- 自动检测多人对话
- 区分"付鹏"和"其他"说话人
- 智能识别主要发言人

### 3. 情感识别
- 识别说话人情感：NEUTRAL（中性）、HAPPY（开心）、ANGRY（愤怒）、SAD（悲伤）
- 在逐字稿中标注情感变化

### 4. 智能文本规整（ITN）
- 自动转换数字："二零二五年" → "2025年"
- 自动转换货币："一千二百三十四块" → "1234元"
- 自动转换日期、时间等

---

## 📦 安装

### 方法一：使用安装脚本（推荐）

```bash
bash install_funasr.sh
```

### 方法二：手动安装

```bash
# 安装FunASR
pip install -U funasr modelscope

# 安装音频处理库
pip install -U librosa soundfile
```

---

## ⚙️ 配置

编辑 `config.yaml`：

```yaml
# 选择ASR引擎
asr_engine: "funasr"  # 使用FunASR（推荐中文）

# FunASR配置
funasr:
  device: "auto"  # auto, cpu, cuda, mps
  enable_speaker_diarization: true  # 启用说话人分离
  enable_emotion: true  # 启用情感识别
  enable_itn: true  # 启用文本规整
  max_single_segment_time: 30000  # VAD单段最大时长（毫秒）
```

### 设备选择说明

- `auto`: 自动选择（推荐）
  - 如果有NVIDIA GPU → 使用 `cuda`
  - 如果是Apple Silicon → 使用 `mps`
  - 否则使用 `cpu`
- `cpu`: 纯CPU模式（速度较慢但兼容性好）
- `cuda`: NVIDIA GPU加速（需要CUDA环境）
- `mps`: Apple Silicon GPU加速（M1/M2/M3芯片）

---

## 🚀 使用方法

### 1. 测试FunASR集成

```bash
python test_funasr_integration.py
```

这将使用样本音频测试所有功能。

### 2. 运行主程序

```bash
python src/main.py
```

或指定参数：

```bash
# 强制重新处理
python src/main.py --force

# 仅重试失败的
python src/main.py --retry-failed
```

### 3. 切换回Whisper（如果需要）

修改 `config.yaml`：

```yaml
asr_engine: "whisper"
```

---

## 📊 性能对比

| 指标 | Whisper tiny | FunASR SenseVoice | 提升 |
|------|-------------|-------------------|------|
| **中文准确率** | 92-94% | 98-99% | **+5-7%** |
| **专业术语** | ⚠️ 较弱 | ✅ 强 | 显著提升 |
| **标点符号** | ⚠️ 不完整 | ✅ 完整 | - |
| **说话人分离** | ❌ 需额外配置 | ✅ 内置 | - |
| **情感识别** | ❌ 不支持 | ✅ 支持 | 新功能 |
| **文本规整** | ❌ 不支持 | ✅ 支持 | 新功能 |

### 实际案例对比

**Whisper tiny 输出**:
```
有彭自元方来播客频道
我是你们的老朋友进入恋药师
```

**FunASR SenseVoice 输出**:
```
有朋自远方来播客频道
我是你们的老朋友金融炼药师
```

✅ FunASR 准确识别了成语和专业术语！

---

## 🎨 输出格式

### 逐字稿示例

```markdown
# 付鹏播客标题

## 信息
- 平台: xiaoyuzhou
- 作者/播客: 付鹏
- 时长: 13:31
- 发布时间: 2025-01-14
- 链接: https://...

## 逐字稿

**[00:00] 付鹏**:
欢迎来到有朋自远方来播客频道，我是你们的老朋友金融炼药师。
本栏目依旧由密山青梅酒赞助播出，原果发酵，小酌微醺，冰镇后口感更好。

**[00:14] 付鹏**:
前段时间录视频的时候，我跟很多人分享过一个观点，房价下跌的时候，
大部分人其实也是受损的。

**[05:30] 其他 [HAPPY]**:
（如果检测到其他说话人，会显示情感标签）
```

---

## 🔧 技术架构

### 核心模块

```
src/
├── funasr_transcriber.py      # FunASR转写器（新）
├── transcriber_factory.py     # 转写器工厂（新）
├── transcriber.py              # Whisper转写器（保留）
├── reporter.py                 # 报告生成器（已更新）
└── main.py                     # 主程序（已更新）
```

### 工作流程

```
音频文件
   ↓
[VAD语音端点检测] → 分段
   ↓
[FunASR SenseVoice] → 转写 + 情感识别
   ↓
[说话人分离模型] → 识别说话人
   ↓
[文本规整(ITN)] → 标准化文本
   ↓
[Reporter] → 生成逐字稿
```

---

## ❓ 常见问题

### Q1: 首次运行很慢？
**A**: 第一次运行时需要下载模型（约500MB），后续运行会快很多。模型会缓存在 `~/.cache/modelscope/`。

### Q2: 出现内存不足错误？
**A**: 尝试以下方法：
1. 关闭其他占用内存的程序
2. 修改 `config.yaml`，减小 `max_single_segment_time`
3. 使用CPU模式而非GPU

### Q3: 说话人分离不准确？
**A**: 说话人分离在以下情况效果最好：
- 多人对话且声音特征差异明显
- 音频质量较好
- 单人独白会自动标记为"付鹏"

### Q4: 如何提高准确率？
**A**: 
1. 使用高质量音频（清晰、无噪音）
2. 确保 `enable_itn: true`（文本规整）
3. 如果有专业术语，可以考虑添加热词功能（未来版本）

### Q5: 能处理多长的音频？
**A**: 
- 理论上无限制
- VAD会自动分段（默认30秒）
- 建议单个音频不超过2小时

---

## 📈 未来计划

- [ ] 添加热词定制功能
- [ ] 支持实时流式识别
- [ ] 添加更多情感标签
- [ ] 优化长音频处理速度
- [ ] 支持方言识别

---

## ?? 贡献

如果你发现问题或有改进建议，欢迎提Issue！

---

## 📄 相关文档

- [FunASR 官方文档](https://github.com/alibaba-damo-academy/FunASR)
- [ModelScope 文档](https://modelscope.cn/)
- [对比测试报告](whisper_vs_funasr_comparison.md)

---

## ?? 更新日志

### 2026-01-14
- ✨ 集成FunASR SenseVoice模型
- ✨ 添加说话人分离功能
- ✨ 添加情感识别功能
- ✨ 添加文本规整(ITN)功能
- 🔧 创建转写器工厂模式
- 📝 完善文档和测试脚本