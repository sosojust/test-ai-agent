import os
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage
from src.schema.state import AgentState
from src.skills.registry import SkillRegistry

from src.config.llm_config import agent_llm_configs
from src.utils.model_factory import ModelFactory

# 1. Define Tools
# Static tool list for ToolNode (execution needs all possible tools)
all_tools = SkillRegistry.get_all_tools()

# 2. Define Model
def get_model(tools=None):
    model = ModelFactory.create(agent_llm_configs.insurance_consultant)
    
    if tools:
        return model.bind_tools(tools)
    return model

# 3. Define Nodes

def chatbot_node(state: AgentState):
    """
    Core Agent Node with Skill Retrieval
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple Retrieval Strategy:
    # Use the content of the last user message to retrieve relevant skills
    query = ""
    is_human = False
    
    if isinstance(last_message, HumanMessage):
        is_human = True
        query = last_message.content
    elif isinstance(last_message, dict):
        msg_type = last_message.get("type")
        role = last_message.get("role")
        if msg_type == "human" or role == "user":
            is_human = True
            query = last_message.get("content", "")
            
    if not isinstance(query, str):
        query = str(query)
        
    if is_human:
        relevant_tools = SkillRegistry.retrieve_skills(query)
    else:
        # If last message is not human (e.g. tool output), keep the previous context or retrieve all?
        # For simplicity in this demo, if it's tool output, we might want to keep the same tools or re-evaluate.
        # Let's re-evaluate based on the last Human message if possible, or just bind all for safety in complex flows?
        # Better: bind all tools if in the middle of a tool chain to ensure stability, 
        # OR retrieve based on the original request.
        # Let's try to find the last human message.
        query = ""
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                query = m.content
                break
            elif isinstance(m, dict):
                msg_type = m.get("type")
                role = m.get("role")
                if msg_type == "human" or role == "user":
                    query = m.get("content", "")
                    break
        relevant_tools = SkillRegistry.retrieve_skills(query)
    
    if not relevant_tools:
        # Fallback: if no tools retrieved, maybe bind nothing? 
        # But if the user intent was ambiguous, maybe bind all?
        # Let's bind all if retrieval returns empty, or just chat.
        # Per user request "save LLM", binding nothing is better if irrelevant.
        # But for robustness, let's bind all if retrieval fails? 
        # No, SkillRegistry returns [] if no match.
        print("  -> No relevant skills found. Chat mode only.")
        model = get_model(tools=None)
    else:
        model = get_model(tools=relevant_tools)
        
    response = model.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState):
    """
    Conditional Edge Logic
    """
    messages = state['messages']
    last_message = messages[-1]
    
    tool_calls = []
    if hasattr(last_message, "tool_calls"):
        tool_calls = last_message.tool_calls
    elif isinstance(last_message, dict):
        tool_calls = last_message.get("tool_calls", [])
        
    if tool_calls:
        return "continue"
    return "end"

# 4. Build Graph

def build_insurance_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("chatbot", chatbot_node)
    workflow.add_node("tools", ToolNode(all_tools))

    # Set Entry Point
    workflow.set_entry_point("chatbot")

    # Add Edges
    workflow.add_conditional_edges(
        "chatbot",
        should_continue,
        {
            "continue": "tools",
            "end": END
        }
    )
    
    workflow.add_edge("tools", "chatbot")

    # Compile into a subgraph
    return workflow.compile()
