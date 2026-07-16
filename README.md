# 情绪疏导小助手

一款基于 Python + PyQt6 开发的 Windows 桌面情绪管理应用，帮助用户记录和管理每日情绪状态，提供压力疏导对话功能。

## 设计理念

简洁实用 · 隐私优先 · 温暖陪伴

## 功能特性

- **心情记录** — 支持每日总体心情和分时段精细化记录，滑动条交互选择评分（1-10分），表情随分数实时变化
- **心情日历** — 月历视图展示每天的心情状态，点击日期可查看当日详细记录和AI情绪总结
- **历史记录** — 列表视图按时间倒序展示所有记录，支持展开/收起查看详情
- **对话助手** — AI根据用户情绪提供共情回应、引导提问和放松建议
- **情绪日报** — 基于当日记录自动生成情绪趋势分析和温馨提示
- **隐私保护** — 所有数据和AI分析均在本地完成，无需联网

## 运行方法

### 环境要求

- Windows 10/11
- Python 3.10+

### 步骤

1. 克隆或下载本项目

   `Bash
   git clone https://github.com/PaperK816/emotion-helper.git
   cd emotion-helper
   `

2. 安装依赖

   `Bash
   pip install -r requirements.txt
   `

3. 运行程序

   `Bash
   python main.py
   `

## 项目结构

`
emotion-helper/
├── main.py                    # 程序入口
├── requirements.txt           # Python依赖
├── AGENTS.md                  # AI开发指令
│
├── app/                       # 应用程序核心代码
│   ├── main_window.py         # 主窗口
│   ├── styles.qss             # 样式表（淡黄色主题）
│   ├── modules/               # 功能模块
│   │   ├── mood_record.py     # 心情记录
│   │   ├── mood_calendar.py   # 心情日历
│   │   ├── history_view.py    # 历史记录
│   │   └── chat_helper.py     # 对话助手
│   ├── models/                # 数据模型
│   ├── services/              # 业务逻辑层
│   └── utils/                 # 工具函数
│
├── data/                      # 数据目录（运行时创建）
├── docs/                      # 项目文档
└── logs/                      # 开发日志
`

## 技术栈

- **GUI框架** — PyQt6
- **数据库** — SQLite3（本地存储）
- **编程语言** — Python 3.10+
- **UI主题** — 淡黄色 #FFF9E6

## 开发日志

本项目使用 Vibe Coding 方式开发，全程由 AI 编程助手（Codex）辅助完成。详见 [docs/requirements.md](docs/requirements.md) 和 [docs/tech-spec.md](docs/tech-spec.md)。

## 许可证

本项目仅供学习交流使用。

---

*Made with ❤️ for emotional wellness*
