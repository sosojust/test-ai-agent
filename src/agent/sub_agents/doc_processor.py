from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from src.schema.state import AgentState
from src.config.llm_config import agent_llm_configs
from src.utils.model_factory import ModelFactory
import os

# Mock Doc Processing Logic
def doc_processor_node(state: AgentState):
    """
    Mock Document Processing Agent
    In a real scenario, this would handle PDF OCR, layout analysis, etc.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # We can use the configured LLM for doc analysis if needed, even in mock
    llm = ModelFactory.create(agent_llm_configs.doc_processor)
    
    # Mock processing
    # Assume the user message contains a file path or content description
    # For demo, we just reply with a mock extraction result
    
    print(f"\n[DocProcessor] Processing document request: {last_message.content[:50]}...")
    
    # Simulate extraction
    extracted_info = {
        "customer_name": "Mock Company Ltd.",
        "employee_count": 120,
        "industry": "IT Services"
    }
    
    response_content = (
        f"已完成文档解析。提取到以下关键信息：\n"
        f"- 企业名称: {extracted_info['customer_name']}\n"
        f"- 员工人数: {extracted_info['employee_count']}\n"
        f"- 行业: {extracted_info['industry']}\n\n"
        f"是否需要将这些信息用于后续的保险方案推荐？"
    )
    
    # Update customer_info in state
    # Note: State updates in subgraphs are propagated to parent graph if configured correctly
    return {
        "messages": [AIMessage(content=response_content)],
        "customer_info": extracted_info
    }

def build_doc_processor_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("doc_processor", doc_processor_node)
    workflow.set_entry_point("doc_processor")
    workflow.add_edge("doc_processor", END)
    return workflow.compile()
