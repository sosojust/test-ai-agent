import os
from langgraph.graph import StateGraph, END
from src.schema.state import AgentState
from src.agent.supervisor import router_node
from src.agent.sub_agents.insurance_consultant import build_insurance_graph
from src.agent.sub_agents.doc_processor import build_doc_processor_graph

# Build Subgraphs
insurance_graph = build_insurance_graph()
doc_processor_graph = build_doc_processor_graph()

def build_graph():
    """
    Build the Supergraph (Main Graph) with Router and Sub-Agents
    """
    workflow = StateGraph(AgentState)

    # 1. Add Router Node
    workflow.add_node("router", router_node)

    # 2. Add Sub-Agent Nodes (as compiled graphs)
    workflow.add_node("insurance_consultant", insurance_graph)
    workflow.add_node("doc_processor", doc_processor_graph)

    # 3. Set Entry Point
    workflow.set_entry_point("router")

    # 4. Add Conditional Edges from Router
    workflow.add_conditional_edges(
        "router",
        lambda x: x.get("current_step", "insurance_consultant"), # Read decision from state
        {
            "insurance_consultant": "insurance_consultant",
            "doc_processor": "doc_processor",
            "end": END
        }
    )

    # 5. Add Return Edges
    # After a sub-agent finishes, where do we go?
    # Option A: Go back to Router (Loop) - allows multi-turn handling
    # Option B: End the turn - let user respond
    
    # For a chat application, usually we return to END after the agent responds, 
    # and wait for next user input. 
    # But wait, if we go to END, the graph execution stops.
    # The next user message triggers a new run.
    
    workflow.add_edge("insurance_consultant", END)
    workflow.add_edge("doc_processor", END)
    
    return workflow

# Export Compiled Graph for LangGraph Server
graph = build_graph().compile()
