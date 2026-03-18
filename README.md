# 团险询报价 AI Agent Demo

> **🎯 核心目标声明**
> 该项目的**核心目的是为了学习和理解 LangGraph 框架**（包括 StateGraph、多 Agent 架构、状态管理和持久化）。
> 在此基础上，我们结合保险业务场景搭建了此 Demo。同时，为了更全面地理解 Agent 框架生态，本项目也引入并对比了 LangChain 官方新推出的开箱即用脚手架 **DeepAgents**。

这是一个基于 **LangGraph** 和 **Aliyun DashScope (通义千问) / OpenAI** 开发的团险询报价 AI Agent Demo。

## 1. 项目背景

本项目旨在验证 AI Agent 在团险询报价场景中的应用，通过对话交互实现信息收集、方案推荐、方案对比和询价单生成。

## 2. 核心功能

- **多轮对话**：通过自然语言与用户交互，引导用户完成询价流程。
- **信息收集**：自动提取客户名称、人数、预算等关键信息。
- **方案推荐**：根据客户画像推荐合适的团险方案。
- **方案对比**：支持对不同方案进行横向对比。
- **询价生成**：最终生成结构化的询报价单。

## 3. 技术架构

- **Agent Runtime**: [LangGraph](https://github.com/langchain-ai/langgraph) (主线实现：StateGraph, Supervisor/Router 模式, 本地 Sqlite 持久化)
- **Agent Harness (对比)**: [DeepAgents](https://github.com/langchain-ai/deepagents) (用于探索和对比开箱即用型 Agent 框架)
- **LLM**: Aliyun DashScope / OpenAI (支持通过 `ModelFactory` 灵活切换)
- **Framework**: LangChain Community
- **Tools / Skills**: 基于 Registry 的模块化技能挂载

## 4. 项目结构

```
.
├── src/
│   ├── agent/          # Agent 核心逻辑 (包含 LangGraph 实现和 DeepAgents 实现)
│   ├── api/            # FastAPI 接口暴露
│   ├── schema/         # State 定义
│   ├── skills/         # 技能注册与实现 (Tools)
│   ├── config/         # LLM 等配置
│   └── utils/          # 模型工厂等工具类
├── docs/               # 文档目录
│   ├── PRD.md                                # 产品需求文档
│   ├── langgraph_vs_deepagents.md            # 框架对比分析
│   ├── skills_implementation_discussion.md   # Skills 工程化实现深度探讨
│   └── blog_building_ai_agent_from_scratch.md # 技术博客：从零实现 AI Agent 的架构演进与思考
├── main.py             # 命令行启动入口 (LangGraph 版本)
├── run_server.py       # API 服务启动入口
├── requirements.txt    # 依赖列表
└── .env.example        # 环境变量示例
```

## 5. 快速开始

### 5.1 环境准备

确保已安装 Python 3.10+。

```bash
# 1. 创建虚拟环境 (推荐)
conda create -n agents python=3.10
conda activate agents

# 2. 安装依赖
pip install -r requirements.txt
```

### 5.2 配置 API Key

1. 复制 `.env.example` 为 `.env`：
   ```bash
   cp .env.example .env
   ```
2. 在 `.env` 文件中填入您的阿里云 DashScope API Key：
   ```
   DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 5.3 运行 Demo

**方式一：运行核心 LangGraph 版本 (推荐)**
通过多 Agent 协作 (Supervisor, Insurance Consultant, Doc Processor) 实现业务流程。
```bash
python main.py
```

**方式二：运行 DeepAgents 对比版本**
体验开箱即用的 Agent Harness 框架，具体对比分析请参考 [`docs/langgraph_vs_deepagents.md`](docs/langgraph_vs_deepagents.md)。
```bash
python src/agent/deepagents_demo.py
```

**方式三：启动 FastAPI 服务**
```bash
python run_server.py
```

**方式四：运行 LangGraph Server (Built-in)**
使用 LangGraph 官方命令行工具启动本地服务器 (需安装 Docker)。
```bash
# 1. 安装 LangGraph CLI
pip install langgraph-cli

# 2. 启动服务器 (Docker Compose)
langgraph dev
```
启动后，访问 `http://localhost:2024` 查看 LangGraph Studio。

## 6. 交互示例

```text
Agent: 您好，我是您的团险顾问。请问有什么可以帮您？

User: 我想给公司买团险，预算500左右。
Agent: 好的。请问贵公司名称是什么？有多少员工？

User: ABC科技，120人，在上海。
Agent: (调用工具推荐方案...) 为您推荐以下方案：
1. 基础版 (450元)
2. 标准版 (520元)
...
```
