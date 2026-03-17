# LangGraph 使用场景设计 (Demo阶段)

## 1. 核心价值与设计理念

在团险询报价场景中，LangGraph 承担 **流程编排 (Workflow Orchestration)** 和 **状态管理 (State Management)** 的核心角色。

相较于传统的 Chain，LangGraph 的核心优势在于处理**非线性、循环和状态持久化**的复杂业务流程：
1.  **多轮交互状态保持**：不仅保存聊天记录，还需保存提取出的结构化业务数据（如客户人数、预算、已选方案列表）。
2.  **动态流程控制**：根据用户输入动态决定是继续追问信息、调用工具推荐方案，还是进行方案对比。
3.  **Human-in-the-loop**：支持在生成最终询价单前，引导用户确认关键信息。

---

## 2. State Schema 设计

为了支持 Demo 阶段的 5 步核心流程，我们需要定义如下 Graph State：

```python
from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # 基础对话历史 (持久化存储)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 结构化客户信息 (从对话中提取)
    customer_info: Optional[dict]  # {name, city, employee_count, budget, ...}
    
    # 业务流程状态
    current_step: str  # "info_collection" | "recommendation" | "comparison" | "quotation"
    
    # 方案数据
    recommended_plans: List[dict]  # 推荐的方案列表
    selected_plan_ids: List[str]   # 用户选中的方案ID (用于对比或生成报价)
    
    # 最终询价单信息
    quotation_id: Optional[str]
```

---

## 3. Graph 拓扑结构

Graph 的结构设计为典型的 **ReAct (Reason + Act)** 模式，包含以下核心节点：

### Nodes (节点)
1.  **`chatbot` (Agent Node)**: 
    - 核心 LLM 节点。
    - 负责理解用户意图、提取信息、决定下一步动作（调用工具或回复用户）。
2.  **`tools` (Tool Node)**:
    - 执行 Mock MCP Tools (如 `get_customer_details`, `recommend_insurance_plans` 等)。
    - 将工具执行结果返回给 Agent。

### Edges (边)
- **Conditional Edge (Start -> Chatbot)**: 根据输入进入对话节点。
- **Conditional Edge (Chatbot -> Tools)**: 如果 LLM 决定调用工具，流向 Tools 节点。
- **Conditional Edge (Chatbot -> End)**: 如果 LLM 决定直接回复用户（如追问信息），结束当前运行，等待用户输入。
- **Normal Edge (Tools -> Chatbot)**: 工具执行完毕后，结果回传给 Agent 进行下一步推理。

---

## 4. 关键场景映射 (Scenario Mapping)

基于 PRD 定义的 5 步流程，LangGraph 的执行逻辑如下：

### 场景一：信息收集循环 (Info Collection Loop)
> **目标**：通过多轮对话补全 `customer_info`。

1.  **User**: "我想给公司做团险，预算500"
2.  **Graph (Chatbot)**: 
    - LLM 分析输入，提取 `budget=500`。
    - 发现缺失 `company_name`, `employee_count`。
    - **Decision**: 不调用工具，直接生成追问回复。
3.  **Agent Reply**: "请问公司名称和员工人数是？"
4.  **User**: "ABC科技，100人"
5.  **Graph (Chatbot)**:
    - 提取 `company_name=ABC科技`, `employee_count=100`。
    - 更新 `customer_info` State。
    - **Decision**: 信息完备，准备推荐。

### 场景二：方案推荐 (Recommendation)
> **目标**：调用工具获取方案并展示。

1.  **Graph (Chatbot)**:
    - 识别到信息完备，**Decision**: 调用 `recommend_insurance_plans(customer_info)`。
2.  **Graph (Tools)**:
    - 执行 Mock Tool，返回 3 个方案 (基础版/标准版/尊享版)。
    - 更新 `recommended_plans` State。
3.  **Graph (Chatbot)**:
    - 接收工具结果。
    - 生成自然语言回复，展示方案列表。
4.  **Agent Reply**: "为您推荐以下3个方案..."

### 场景三：方案对比 (Comparison)
> **目标**：响应用户对比需求，调用对比工具。

1.  **User**: "对比一下标准版和尊享版"
2.  **Graph (Chatbot)**:
    - 识别意图 "Compare"。
    - 提取方案实体 "标准版", "尊享版"。
    - **Decision**: 调用 `compare_insurance_plans(ids=[...])`。
3.  **Graph (Tools)**:
    - 执行 Mock Tool，返回对比数据表格。
4.  **Graph (Chatbot)**:
    - 格式化输出对比表格。
5.  **Agent Reply**: "| 项目 | 标准版 | 尊享版 | ..."

### 场景四：询价单生成 (Quotation Generation)
> **目标**：确认方案并生成最终单据。

1.  **User**: "就选标准版吧，生成报价"
2.  **Graph (Chatbot)**:
    - 识别意图 "Generate Quote"。
    - 确认 `selected_plan="标准版"`。
    - **Decision**: 调用 `generate_quotation(customer_info, plan_id)`。
3.  **Graph (Tools)**:
    - 执行 Mock Tool，生成 Quote ID。
    - 更新 `quotation_id` State。
4.  **Graph (Chatbot)**:
    - 生成确认回复。
5.  **Agent Reply**: "询价单 Q2024... 已生成。"

---

## 5. 伪代码示例 (Graph Definition)

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# 1. 初始化 Graph
workflow = StateGraph(AgentState)

# 2. 添加节点
workflow.add_node("chatbot", chatbot_node) # 包含 LLM 调用逻辑
workflow.add_node("tools", ToolNode(tools=[
    get_customer_details, 
    recommend_insurance_plans, 
    compare_insurance_plans, 
    generate_quotation
]))

# 3. 定义边
workflow.set_entry_point("chatbot")

# 条件边：Chatbot -> (Tools 或 END)
workflow.add_conditional_edges(
    "chatbot",
    should_continue, # 判断函数：是否有 tool_calls
    {
        "continue": "tools",
        "end": END
    }
)

# 普通边：Tools -> Chatbot (工具执行完回环给 Agent 继续处理)
workflow.add_edge("tools", "chatbot")

# 4. 编译
app = workflow.compile(checkpointer=memory) # 绑定 Checkpointer 实现持久化
```
