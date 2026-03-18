# 关于 Skills 实现方案的探讨与演进

本文档旨在探讨当前项目中 Skills (工具) 的实现方案，对比 Claude 等前沿大模型的实现机制，并深入分析为什么不推荐将所有 Skills 的描述直接全量塞入 LLM 的上下文中，最后给出基于当前方案的逐步迭代路径。

## 1. 当前项目的实现方案

目前，我们在 `src/skills` 目录下实现了一套基础的**动态技能检索与绑定机制**。核心流程如下：

1. **技能注册 (Skill Registry)**: 所有的技能（如 `CustomerSkill`, `InsuranceSkill`, `QuotationSkill`）都在 `SkillRegistry` 中集中注册。
2. **按需检索 (Retrieval)**: 当用户输入新的 Query 时，系统不会加载所有工具，而是通过简单的**关键词匹配 (Keyword Matching)**，对比用户的输入和 Skill 的 `description` / `keywords`。
3. **动态绑定 (Dynamic Binding)**: 只有命中的 Skill 才会被提取出底层的 Tools，并通过 `model.bind_tools(relevant_tools)` 动态注入到 LLM 的本次调用中。

这种方案在小规模场景下轻量且高效，但在面对复杂语义或海量技能时，基于关键词的硬匹配会显得力不从心。

---

## 2. 为什么不能直接把所有 Skills 全量作为上下文注入？

很多初学者在构建 Agent 时，会倾向于把所有工具的 `name` 和 `description` 直接写在 System Prompt 中，或者在每次 API 调用时 `bind_tools()` 全部的工具。这种做法在工具数量超过 5-10 个后，会带来严重的负面影响：

### 2.1 Context Dilution (上下文稀释) 与 "Lost in the Middle"
LLM 的注意力机制存在 "Lost in the Middle" (中间迷失) 现象。当你注入了 50 个工具的详细描述和参数结构时，LLM 的核心注意力会被这些庞杂的 API 文档分散。这会导致它无法精准理解用户真正的核心诉求，甚至忘记 System Prompt 中的关键行为准则。

### 2.2 幻觉 (Hallucination) 与错误调用
给 LLM 提供的工具越多，它的决策空间就越大。在面对模糊的输入时，LLM 极大概率会“张冠李戴”，选择了一个看似相关但实际错误的工具，或者为了使用工具而伪造 (Hallucinate) 必填参数。**限制候选工具集是降低幻觉最有效的手段之一。**

### 2.3 Token 消耗与延迟 (Latency)
每个 Tool 的 JSON Schema（包括名称、描述、参数定义）都会占用大量的 Token。
- **成本问题**：如果每次对话都携带 100 个工具的 Schema，每轮对话的 Input Token 消耗将呈指数级上升。
- **延迟问题**：Input Token 越大，首字响应时间 (TTFT) 越长，严重影响用户体验。

### 2.4 扩展性瓶颈 (Scalability)
全量注入从根本上违背了系统的可扩展性。一个成熟的 Agent 生态（如 Claude 的生态）可能拥有成百上千个工具，LLM 的上下文窗口和处理能力在物理上无法一次性承载所有工具的知识。

---

## 3. Claude 等前沿 Agent 的 Skills 实现机制

以 Claude (Anthropic) 和前沿的 Agent 框架体系（如最近推出的 **MCP - Model Context Protocol**）为例，它们在处理海量工具时采用了更为高级的架构：

1. **模型上下文协议 (MCP)**: Claude 引入了 MCP，允许 Agent 动态地连接到不同的数据源和工具服务器。工具不再是硬编码的，而是通过标准化的协议按需发现和调用。
2. **两阶段/多阶段路由 (Two-stage Routing)**:
   - **Stage 1 (粗筛)**: 类似于搜索引擎，使用轻量级、低延迟的模型（或 Embedding 向量检索）对用户的 Query 进行意图分类或语义检索，从工具库中召回 Top-K 个最相关的工具。
   - **Stage 2 (精选与执行)**: 将召回的 Top-K 工具的完整 Schema 绑定给强大的主模型（如 Claude 3.5 Sonnet），由主模型决定具体调用哪个工具以及如何构造参数。
3. **Lazy Loading (懒加载)**: 工具的执行环境、依赖包和详细文档在真正被需要时才会被加载到 Agent 的上下文中。

---

## 4. 基于当前实现的逐步迭代路径

为了让我们的 Demo 从目前的“关键词匹配”平滑过渡到工业级架构，我们可以规划以下迭代路径：

### Phase 1: 增强型规则与元数据匹配 (当前阶段优化)
- **现状**：简单的子串 `in` 判断。
- **改进**：为每个 Skill 引入更丰富的元数据（如 `intent_categories`, `required_entities`）。利用现有的 Supervisor Router 提取出的意图，更精准地过滤 Skill，而不是纯靠用户输入的字面量。

### Phase 2: 语义检索 (Semantic Search / Embedding)
- **目标**：解决关键词匹配无法理解同义词和复杂表达的问题。
- **实现**：
  1. 将所有 Skill 的 `description` 和使用场景预先向量化 (Embedding)，存入轻量级向量数据库 (如 ChromaDB 或 FAISS)。
  2. 运行时，对用户的 Query 进行向量化，计算余弦相似度，召回 Top-3 相关的 Skills。

### Phase 3: 引入 Tool Calling Agent (专门的路由模型)
- **目标**：利用小参数模型 (如 Qwen-Turbo / Llama-3-8B) 专门做工具选择。
- **实现**：
  1. 剥离主模型的负担。
  2. 每次请求先经过一个 Tool Router Agent，该 Agent 只有各个工具的极简摘要（名称+一句话描述）。
  3. Tool Router 输出需要使用的 `tool_names`，然后主系统提取完整的 Schema 并交给主模型执行。

### Phase 4: 拥抱标准协议 (如 MCP 集成)
- **目标**：实现跨平台、跨语言的工具生态。
- **实现**：重构 `src/skills`，使其暴露为符合 Model Context Protocol (MCP) 标准的 Server。Agent 通过 MCP 客户端与这些工具进行交互，实现真正的解耦和分布式工具调用。

---

## 结论

在 Agent 开发中，**“把什么交给大模型”和“把什么留给工程系统”**同样重要。通过工程化的检索机制（Retrieval）代替全量 Prompt 注入，不仅能大幅节省 Token 成本，更能显著提升 Agent 的执行准确率和稳定性。我们的项目将沿着 `关键词匹配 -> 向量检索 -> 模型路由 -> 标准协议` 的路径，持续演进我们的 Skills 架构。
