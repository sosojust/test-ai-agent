from typing import Literal, Annotated, TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from src.schema.state import AgentState
import operator

# Output Schema for Router
class RouteOutcome(TypedDict):
    next_agent: Literal["insurance_consultant", "doc_processor", "end"]

def get_router_model():
    # Use a lightweight model or same model with structured output
    # For simplicity, we use qwen-max and function calling/structured output
    llm = ChatTongyi(model="qwen-max")
    
    # Define routing options
    options = ["insurance_consultant", "doc_processor", "end"]
    
    system_prompt = (
        "你是一个智能路由助手 (Supervisor)。\n"
        "根据用户的输入，决定下一步应该交给哪个专家 Agent 处理，或者直接结束。\n"
        "1. 如果用户正在询问保险方案、报价、客户信息查询等业务问题 -> 'insurance_consultant'\n"
        "2. 如果用户上传了文件、要求解析文档、提取PDF信息 -> 'doc_processor'\n"
        "3. 如果是简单的寒暄、或者用户表示结束 -> 'end' (注意：通常我们希望尽可能保持在 insurance_consultant 中，除非明确是文档处理)\n"
        "如果拿不准，默认转给 'insurance_consultant'。\n"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{input}")
    ])
    
    # We can use simple prompt or structured output.
    # Let's use bind_tools for robust classification or just prompt engineering.
    # Given we just need a string classification, prompt is easier for this demo.
    
    return prompt | llm

from src.config.llm_config import agent_llm_configs
from src.utils.model_factory import ModelFactory

def router_node(state: AgentState):
    """
    Supervisor Node
    Decides which sub-agent to call next.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # Handle both object and dict (serialization) formats
    if isinstance(last_message, dict):
        content = last_message.get("content")
    else:
        content = last_message.content
        
    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)
    
    print(f"\n[Router] Analyzing intent for: {content[:50]}...")
    
    # Simple rule-based shortcut for obvious file handling (optional)
    if "pdf" in content.lower() or "文档" in content or "解析" in content:
        print("  -> Rule Match: doc_processor")
        return {"current_step": "doc_processor"}
    
    # LLM-based routing
    llm = ModelFactory.create(agent_llm_configs.supervisor)
    prompt = (
        f"请判断用户意图并返回以下关键词之一：\n"
        f"- 'INSURANCE': 询价、方案推荐、保险业务咨询\n"
        f"- 'DOC': 文档解析、PDF处理\n"
        f"- 'CHAT': 闲聊\n\n"
        f"用户输入: {content}\n"
        f"只返回关键词，不要其他内容。"
    )
    
    response = llm.invoke(prompt).content.strip().upper()
    
    if "DOC" in response:
        route = "doc_processor"
    elif "INSURANCE" in response:
        route = "insurance_consultant"
    else:
        # Default to insurance consultant for chat to keep context, or handle chat here?
        # Let's route chat to insurance_consultant too as it has the persona.
        route = "insurance_consultant"
        
    print(f"  -> LLM Decision: {route}")
    
    # We store the decision in a temporary key in state or just return it for the conditional edge
    # LangGraph conditional edges read from state, so we might need to add a 'next' key to state 
    # OR the conditional edge function can re-run logic (wasteful).
    # Ideally, we return an update to state.
    # Let's add a 'next_agent' field to AgentState? 
    # Or, we can just use the last message content in the conditional edge function? 
    # No, that's what we are doing here.
    # 
    # **Correction**: In LangGraph, a node returns state updates. 
    # The conditional edge function then reads the state to decide.
    # So we need to store the decision in state.
    
    return {"current_step": route} # Re-using current_step to store the routing decision temporarily? Or add a new field.
    # Let's use 'current_step' as it fits "business process state".
