# 项目文件结构 📁

```
付鹏/
├── 📄 README.md                          # 项目主文档
├── 📄 config.yaml                        # 配置文件（包含FunASR配置）
├── 📄 requirements.txt                   # Python依赖
├── 📄 视频链接                           # 输入链接文件
├── 📄 progress.json                      # 处理进度
│
├── 🆕 FunASR集成相关
│   ├── 📄 FUNASR_INTEGRATION.md         # 完整集成文档
│   ├── 📄 QUICKSTART_FUNASR.md          # 快速开始指南
│   ├── 📄 FUNASR_MIGRATION_SUMMARY.md   # 集成总结
│   ├── 📄 whisper_vs_funasr_comparison.md # 对比报告
│   ├── 📄 install_funasr.sh             # 安装脚本
│   ├── 📄 test_funasr_comparison.py     # 对比测试
│   ├── 📄 test_funasr_integration.py    # 集成测试
│   └── 📄 funasr_comparison_result.txt  # 测试结果
│
├── 📁 src/                               # 源代码
│   ├── 🆕 funasr_transcriber.py         # FunASR转写器
│   ├── 🆕 transcriber_factory.py        # 转写器工厂
│   ├── 📄 transcriber.py                # Whisper转写器（保留）
│   ├── 📄 main.py                       # 主程序（已更新）
│   ├── 📄 reporter.py                   # 报告生成器（已更新）
│   ├── 📄 downloader.py                 # 下载器
│   ├── 📄 parser.py                     # 链接解析
│   ├── 📄 metadata_extractor.py         # 元数据提取
│   ├── 📄 progress_manager.py           # 进度管理
│   │
│   ├── ?? utils/                        # 工具模块
│   │   ├── ?? __init__.py
│   │   ├── 📄 config.py                 # 配置加载
│   │   ├── 📄 logger.py                 # 日志工具
│   │   └── 📄 llm_client.py             # LLM客户端
│   │
│   └── 📁 data/                         # 数据目录
│       ├── 📁 downloads/                # 下载的音频
│       ├── 📁 transcripts/              # 生成的逐字稿
│       └── 📁 temp/                     # 临时文件
│
├── 📁 data/                              # 输出数据
│   ├── 📄 links_summary.xlsx            # 元数据汇总表
│   ├── 📄 processing_result.xlsx        # 处理结果
│   ├── 📁 downloads/                    # 音频文件
│   └── 📁 transcripts/                  # 逐字稿
│
└── 📁 logs/                              # 日志文件
    └── 📄 app.log

```

## 🔑 关键文件说明

### FunASR核心模块
- **funasr_transcriber.py**: FunASR转写器实现，支持说话人分离、情感识别
- **transcriber_factory.py**: 工厂模式，动态选择ASR引擎

### 配置文件
- **config.yaml**: 主配置文件，控制ASR引擎、设备、功能开关

### 测试文件
- **test_funasr_integration.py**: 完整集成测试
- **test_funasr_comparison.py**: 与Whisper对比测试

### 文档
- **FUNASR_INTEGRATION.md**: 技术文档
- **QUICKSTART_FUNASR.md**: 快速开始
- **whisper_vs_funasr_comparison.md**: 详细对比

## 📊 数据流

```
视频链接 
  ↓
[parser.py] 解析链接
  ↓
[metadata_extractor.py] 提取元数据
  ↓
[downloader.py] 下载音频
  ↓
[transcriber_factory.py] 选择引擎
  ↓
[funasr_transcriber.py / transcriber.py] 转写
  ↓
[reporter.py] 生成报告
  ↓
data/transcripts/*.md (逐字稿)
```

## 🎯 使用入口

- **主程序**: `python src/main.py`
- **FunASR测试**: `python test_funasr_integration.py`
- **对比测试**: `python test_funasr_comparison.py`
