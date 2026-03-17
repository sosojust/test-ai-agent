# 团险询报价 AI Agent Demo PRD

## 1. 项目背景

企业团体保险询报价流程通常需要：

- 人工收集企业信息

- 手工整理员工数据

- 阅读保司方案 PDF

- 人工对比方案

流程复杂、效率低。

本项目目标是开发一个 **AI Agent Demo**，通过 **对话方式**帮助用户完成：

1️⃣ 收集企业信息  
2️⃣ 上传员工或方案文件  
3️⃣ 自动生成询价请求  
4️⃣ 自动对比方案  
5️⃣ 输出结构化报价信息

---


# 2. 项目目标

Demo 版本目标：

| 目标 | 描述 |
| --- | --- |
| AI对话询价 | 用户通过聊天完成信息收集、方案选择与询价 |
| 方案推荐 | 根据信息推荐适合的 Mock 方案 |
| 方案对比 | AI 自动对比不同方案差异 |
| 询价生成 | 最终生成结构化的询价单 |
| 系统集成 | Mock MCP Tool 完整调用流程 |
| 可回放 | Agent 执行日志 |


---


# 3. 系统范围（Scope）

## In Scope

- AI 询报价 Agent (完整对话流程)

- Mock MCP Tools (客户信息、方案推荐、方案对比、询报价生成)

- 聊天记录存储 (持久化会话历史)

- Agent Loop

- 会话管理

- 日志回放

## Out of Scope（Demo阶段）

- 向量数据库 (RAG)

- PDF / Excel 解析 (文档解析模块)

- 多租户权限

- 真实支付

- 客户门户

- 保司 API 自动对接（可 mock）

---


# 4. 用户角色

| 角色 | 描述 |
| --- | --- |
| 销售 | 为企业客户做询价 |
| HR客户 | 直接询价 |
| 运营 | 查看询价结果 |


---


# 5. 核心用户流程

## 用户流程


```
进入系统  
 ↓  
AI对话 (客户名称、人数、男女比例、预算)  
 ↓  
方案推荐 (AI调用Tool)  
 ↓  
方案互动/对比 (AI调用Tool)  
 ↓  
确认方案  
 ↓  
生成询报价 (AI调用Tool)  
 ↓  
展示结果
```

---


# 6. Agent 交互示例

### 用户


```
我想给公司做团险报价
```


### Agent


```
好的，我可以帮你完成询报价。  
请问公司名称？
```


### 用户


```
ABC科技
```


### Agent


```
公司所在城市？  
员工人数？
预算大概是多少？
```


### 用户


```
上海，120人，预算人均500左右
```


### Agent


```
请提供员工概况信息（如平均年龄、男女比例等）。
```


### 用户


```
平均年龄32岁，男女比例1:1
```


### Agent


```
(调用 recommend_insurance_plans)

为您推荐以下 3 个方案：

1. **基础版** (450元/人)：意外险 + 补充医疗
2. **标准版** (520元/人)：基础版 + 重疾
3. **尊享版** (600元/人)：标准版 + 门诊

您想了解哪个方案？或者进行对比？
```

### 用户

```
对比一下标准版和尊享版
```

### Agent

```
(调用 compare_insurance_plans)

**方案对比：**

| 项目 | 标准版 | 尊享版 |
| --- | --- | --- |
| 价格 | 520元 | 600元 |
| 门诊 | 无 | 含 |
| ... | ... | ... |

请问您选择哪个方案？
```

### 用户

```
选标准版，生成报价
```

### Agent

```
(调用 generate_quotation)

已为您生成 **标准版** 询价单。
询价单号：Q20240501001
请确认信息无误后提交。
```

---


# 7. 系统架构

## 总体架构


```
Frontend  
   │  
   ▼  
Agent Gateway  
   │  
   ▼  
Agent Runtime (LangGraph)  
   │  
 ┌─┴───────────────┐  
 │                  │  
Tools            Workflow  
 │                  │  
 ▼                  ▼  
MCP API        Business System  
 │  
 ▼  
Database
```

---


# 8. 核心模块

系统主要模块：

1️⃣ Agent Runtime  
2️⃣ Session 管理  
3️⃣ MCP Tools  
4️⃣ Document Processing  
5️⃣ Workflow Engine  
6️⃣ 日志与回放

---


# 9. Agent Runtime

使用：

**LangGraph**

Agent Graph：


```
START  
 ↓  
理解用户意图  
 ↓  
信息收集  
 ↓  
是否信息完整？  
 ├─否 → 继续提问  
 └─是 → 生成询价  
 ↓  
调用询价API  
 ↓  
返回结果  
 ↓  
END
```

---


# 10. Agent State

Agent State Schema：


```json
{  
 "session_id": "",  
 "user_id": "",  
 "quote_id": "",  
 "customer_name": "",  
 "city": "",  
 "employee_count": "",  
 "employee_file": "",  
 "insurance_types": [],  
 "quote_status": "",  
 "plans": []  
}
```

---


# 11. Session 管理

每次对话创建 Session。

Session 数据：

```
session_id  
user_id  
created_at  
status  
state  
messages (持久化存储)
```
存储：

```
SQLite / PostgreSQL (Demo阶段不使用 pgvector)
```

---


# 12. MCP Tools 设计

> **Demo 阶段说明**：
> 1. MCP Tools 及 Skills 工具使用 Mock 实现，但需跑通完整的工具调用流程。
> 2. 实际执行动作（如数据库操作、外部API调用）可以使用 Mock 数据返回。

Agent 不直接访问数据库。

所有业务能力通过 MCP Tool。

## 核心 Mock Tools (Demo)

为了支持完整的询报价流程，Demo 阶段需 Mock 以下工具：

### 1. 客户信息工具 (Customer)
```
get_customer_details(customer_name)
// 查询客户详情（如人员规模、行业等）
```

### 2. 方案推荐工具 (Recommendation)
```
recommend_insurance_plans(customer_info, budget)
// 根据客户信息和预算，推荐团险方案（返回多个方案选项）
```

### 3. 方案对比工具 (Comparison)
```
compare_insurance_plans(plan_ids)
// 对比用户选择的指定方案
```

### 4. 询报价生成工具 (Quotation)
```
generate_quotation(customer_info, selected_plan)
// 生成最终询报价单（包括方案信息）
```

---


## Document Tools (Out of Scope for Demo)

```
parse_pdf  
parse_excel  
extract_employee_data
```

---


# 13. Document Processing (Out of Scope for Demo)

处理：

- PDF

- Excel

- 图片

流程：


```json
Upload  
 ↓  
Document Service  
 ↓  
Parser  
 ↓  
LLM Structuring  
 ↓
```
输出：


```json
{  
 "employee_count": 120,  
 "avg_age": 32,  
 "male_ratio": 0.55  
}
```

---


# 14. Workflow Engine

Workflow 负责 **确定性业务流程**。

示例：


```
创建询价  
 ↓  
保存询价信息  
 ↓  
调用保司API  
 ↓  
生成报价
```
Agent 触发：


```
submit_quote
```

---


# 15. Prompt 管理

Prompt 模板示例：

### System Prompt


```
你是一个团险保险顾问。  
你的目标是帮助用户完成团险询报价。  
在信息不完整时，需要主动提问。
```

---


### 信息收集 Prompt


```
需要收集以下信息：  
公司名称  
城市  
员工人数  
保险类型
```

---


# 16. Agent Loop

执行逻辑：


```
User Message  
 ↓  
LLM Reason  
 ↓  
Decide Tool  
 ↓  
Call Tool  
 ↓  
Update State  
 ↓  
Next Step
```
最大 step：


```
max_steps = 20
```

---


# 17. 日志与回放

记录：


```
prompt  
tool_call  
tool_result  
state_change
```
示例：


```
step1: intent detection  
step2: ask company name  
step3: collect employee info  
step4: create quote
```
支持：


```
Replay execution
```

---


# 18. 前端接口

Agent API：

### 发送消息


```
POST /agent/chat
```
参数：


```
session_id  
message  
attachments
```
返回：


```
assistant_message  
agent_state
```

---





### 查询会话


```
GET /agent/session/{id}
```

---


# 19. 技术选型

| 模块 | 技术 |
| --- | --- |
| Agent Runtime | LangGraph |
| LLM | Aliyun DashScope (Demo阶段) |
| 向量数据库 | (Demo阶段不使用) |
| 缓存 | Redis |
| 后端 | Python / FastAPI |



---


# 20. Demo 成功标准

Demo 完成标准：

用户可以：

1️⃣ 通过聊天完成客户信息收集（含预算等）
2️⃣ AI 自动推荐 Mock 方案
3️⃣ AI 辅助对比不同方案
4️⃣ 用户确认方案后生成询价单
5️⃣ 完整展示 Tool 调用过程

---


# 21. Demo 里程碑

阶段 1：


```
Agent对话  
Session  
State
```
阶段 2：


```
MCP tools
```
阶段 3：


```
Mock Skills 验证
```
阶段 4：


```
方案对比
```

---


# 22. 未来扩展

未来版本可以增加：

- 多 Agent

- 自动谈判报价

- 客户画像

- 推荐方案

- 自动生成保险建议书

---


# 结论

这个 Demo 的核心目标是验证：


```
AI Agent 是否能成为团险询报价入口
```
技术核心：


```
LangGraph Agent  
+  
MCP Tools  
+  
Workflow
```