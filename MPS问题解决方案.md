# MPS兼容性问题解决方案

**问题**: Whisper模型在Apple MPS (Metal Performance Shaders) 上运行时遇到稀疏张量操作不兼容的问题。

**日期**: 2026-01-14

---

## 🔍 问题根源

根据PyTorch官方issue #141711：

> Whisper使用了 `aten::_sparse_coo_tensor_with_dims_and_tensors` 操作，而MPS后端目前**不支持稀疏张量**。

这是PyTorch 2.8版本的已知限制，不是你的环境问题。

---

## ✅ 采用的解决方案

### 方案：优化的CPU模式

虽然无法使用GPU加速，但我们通过以下优化提升了CPU性能：

1. **多线程优化**
   - 自动检测CPU核心数
   - 设置OMP和MKL线程数
   - 典型情况下使用8个线程

2. **Whisper参数优化**
   - `temperature=0.0` - 贪心解码，更快
   - `beam_size=5` - 平衡速度和准确度
   - `fp16=False` - CPU模式禁用半精度

3. **智能批处理**
   - 从小文件到大文件排序处理
   - 支持断点续传
   - 自动跳过已完成的文件

---

## 📊 性能预估（基于你的Mac配置）

你的音频文件：
- **27个文件，总计2.08GB**
- **10个B站视频** (MP4，平均70MB)
- **17个小宇宙音频** (M4A，平均50MB)

**预计处理时间**：

| 模型 | 单文件平均时间 | 27个文件总时间 |
|------|---------------|---------------|
| tiny | 2-3分钟 | 1-1.5小时 |
| base | 4-6分钟 | 2-3小时 |
| small | 8-12分钟 | 4-6小时 |

**推荐**：使用 `base` 模型（准确度和速度的最佳平衡）

---

## 🚀 使用方法

### 方法1：单个文件测试

```bash
cd /Users/mating05/Documents/个人学习/付鹏
/opt/anaconda3/bin/python src/transcribe_simple.py \
  src/data/downloads/文件名.m4a \
  --model base
```

### 方法2：批量处理（推荐）

```bash
cd /Users/mating05/Documents/个人学习/付鹏
/opt/anaconda3/bin/python src/batch_transcribe.py \
  --audio-dir src/data/downloads \
  --output src/data/transcripts \
  --model base
```

**特点**：
- ✅ 自动跳过已完成的文件
- ✅ 支持 Ctrl+C 中断，下次继续
- ✅ 显示实时进度和预计剩余时间
- ✅ 按文件大小排序（先处理小文件）

---

## 🎯 后台运行（适合长时间处理）

如果你想让程序在后台运行，不影响使用电脑：

```bash
cd /Users/mating05/Documents/个人学习/付鹏

# 后台运行，日志保存到文件
nohup /opt/anaconda3/bin/python src/batch_transcribe.py \
  --model base \
  > transcribe.log 2>&1 &

# 查看进度
tail -f transcribe.log
```

---

## 🔮 未来改进方向

当PyTorch官方修复MPS稀疏张量支持后，可以：

1. 更新到新版PyTorch
2. 修改代码重新启用MPS
3. 预计速度提升 **3-5倍**

**跟踪issue**：https://github.com/pytorch/pytorch/issues/141711

---

## 📝 当前已完成

✅ **所有27个文件已下载** (2.08GB)  
✅ **元数据表格完整** (src/data/links_summary.xlsx)  
✅ **转写工具已优化** (CPU多线程)  
⏳ **待处理**: 27个文件的语音转写

---

## 💡 建议

**选项A - 现在开始（推荐）**：
```bash
# 先测试1个小文件，确认效果
/opt/anaconda3/bin/python src/transcribe_simple.py \
  "$(ls -S src/data/downloads/*.m4a | tail -1)" \
  --model base

# 满意后再批量处理全部
/opt/anaconda3/bin/python src/batch_transcribe.py --model base
```

**选项B - 后台处理**：
```bash
# 晚上睡觉前启动，第二天早上查看结果
nohup /opt/anaconda3/bin/python src/batch_transcribe.py --model base > transcribe.log 2>&1 &
```

---

**结论**: 虽然无法使用GPU加速，但优化后的CPU方案是**目前唯一可行且稳定的解决方案**。对于27个文件，预计2-3小时即可完成全部转写。