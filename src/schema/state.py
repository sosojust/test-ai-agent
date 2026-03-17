from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    """
    Agent State Definition based on PRD
    """
    # 基础对话历史 (持久化存储)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # 结构化客户信息 (从对话中提取)
    # 包含字段: customer_name, city, employee_count, budget, etc.
    customer_info: Optional[dict]
    
    # 业务流程状态
    # "info_collection" | "recommendation" | "comparison" | "quotation"
    current_step: str
    
    # 方案数据
    recommended_plans: Optional[List[dict]]  # 推荐的方案列表
    selected_plan_ids: Optional[List[str]]   # 用户选中的方案ID
    
    # 最终询价单信息
    quotation_id: Optional[str]
