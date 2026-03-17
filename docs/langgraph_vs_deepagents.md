# LangGraph vs DeepAgents 技术对比分析

## 1. 概述
在当前的保险咨询 Demo 中，我们使用了 **LangGraph** 作为底层的 Agent 编排框架。最近，LangChain 官方推出了 **DeepAgents**（深度 Agent），这是一个构建在 LangChain 和 LangGraph 之上的“开箱即用”的 Agent Harness（脚手架）。

本文档将对比这两种方案在实现该保险业务 Demo 时的优劣势，以便于技术选型。

## 2. 核心定位对比

| 特性 | LangGraph | DeepAgents |
| :--- | :--- | :--- |
| **定位** | 底层编排框架 (Runtime/Framework) | 高层脚手架 (Agent Harness) |
| **架构** | 基于状态图 (StateGraph)，节点和边高度可定制 | 开箱即用的预设架构，内置了规划(Planning)、子代理(Subagents)、文件系统(Filesystem)等能力 |
| **开发方式** | 需要手动连线、定义状态 (State)、编写路由逻辑和条件边 | 通过 `create_deep_agent` 一键生成，提供 `tools` 和 `system_prompt` 即可 |
| **控制力** | 极高，适合实现严格的业务流转和复杂的定制化路由 | 中等，更多依赖大模型自身的规划和决策能力 |

## 3. 在本 Demo 中的优劣势分析

我们的 Demo 包含以下核心特性：
1. 多 Agent 架构：Supervisor 路由、Doc Processor 处理文档、Insurance Consultant 处理业务。
2. 保险核心流程：收集信息 -> 推荐方案 -> 方案对比 -> 生成报价。
3. 技能挂载 (Skills) 和本地持久化 (SqliteSaver)。

### 方案 A：继续使用当前 LangGraph 架构
*   **优势**：
    *   **业务流转精准**：我们可以精确控制 Supervisor 如何根据关键词或大模型意图将用户分发到对应的子 Agent。
    *   **状态可控**：我们可以清晰地定义 `AgentState`，在其中专门开辟 `customer_info` 字段用于跨多轮保存结构化数据，这对业务系统对接非常关键。
    *   **定制化强**：更容易无缝接入我们自己实现的 `ModelFactory` (支持随意切换 Aliyun / OpenAI)。
*   **劣势**：
    *   **开发成本高**：需要编写大量样板代码（如节点函数、状态图定义、边条件判断等）。

### 方案 B：重构为使用 DeepAgents
*   **优势**：
    *   **极简代码**：无需手动构建图。通过 `create_deep_agent` 可以快速创建 Agent。
    *   **原生多 Agent 支持**：DeepAgents 原生支持 Subagent-spawning（子代理生成），它可以自动将 Doc Processor 作为子 Agent 调用，无需我们手动写 Supervisor 路由节点。
    *   **内置高级能力**：内置了任务规划、总结等中间件，处理极其复杂、开放式的任务（如需要自己编写代码解决问题）时非常强大。
*   **劣势**：
    *   **流程不可控 (黑盒化风险)**：它高度依赖模型的自主规划（Planning），可能偏离我们预设的“五步保险销售法”，这违反了“No Black Box”的团队编码原则。
    *   **模型能力要求极高**：DeepAgents 这种高度自主的框架通常需要 GPT-4o 或 Claude-3.5-Sonnet 级别的推理能力，如果我们切换到较弱的国产模型，可能会出现“规划死循环”或“工具调用混乱”。
    *   **生态太新**：作为刚推出的库，API 变动频繁，遇到问题难以排查。

## 4. 结论与建议

*   **对于当前阶段的 Demo**：**推荐保留 LangGraph**。因为保险咨询是一个相对有结构化业务要求的场景（需要准确获取客户信息、推荐、报价），LangGraph 的状态机模式能让我们对业务状态拥有 100% 的掌控力。
*   **对于 DeepAgents 的应用场景**：DeepAgents 更适合做**完全开放式的任务**（例如：“帮我爬取过去十年的财报，分析后写一个总结文档存到本地”），在这种场景下它的规划和文件系统能力能发挥巨大价值。
*   **探索尝试**：为了验证新技术的潜力，我们将使用 DeepAgents 额外实现一版 Demo 逻辑，以供体验和对比。