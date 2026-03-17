import os
import sys
import sqlite3
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from src.agent.graph import build_graph

# Load environment variables
load_dotenv()

SYSTEM_PROMPT = """你是一个专业的团险保险顾问 Agent。
你的目标是帮助企业客户完成团险询报价流程。
你需要遵循以下步骤：
1. **信息收集**：通过对话收集客户信息（公司名称、员工人数、城市、预算等）。如果信息不全，需要追问。
2. **方案推荐**：当信息足够时，调用 `recommend_insurance_plans` 工具推荐方案。
3. **方案对比**：如果用户对方案有疑问或需要对比，调用 `compare_insurance_plans` 工具。
4. **询价生成**：用户确认方案后，调用 `generate_quotation` 生成询价单。

请保持语气专业、亲切。在调用工具前，不需要向用户解释你要调用工具，直接行动即可。
"""

def main():
    print("=== 团险询报价 AI Agent Demo ===")
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("Error: DASHSCOPE_API_KEY environment variable is not set.")
        print("Please create a .env file with DASHSCOPE_API_KEY=your_key")
        return

    # Initialize Persistence
    # Use in-memory SQLite for demo simplicity, or file-based for persistence
    # conn = sqlite3.connect("agent_history.db", check_same_thread=False)
    # memory = SqliteSaver(conn)
    # For now, let's just use memory saver for the session or file based
    
    db_path = "agent_history.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    # Initialize Graph
    try:
        workflow = build_graph()
        app = workflow.compile(checkpointer=checkpointer)
    except Exception as e:
        print(f"Failed to build graph: {e}")
        return

    # Configuration for the session
    thread_id = "demo_thread_1"
    config = {"configurable": {"thread_id": thread_id}}

    # Initial State
    # Check if history exists
    current_state = app.get_state(config)
    if not current_state.values:
        print("Initializing new session...")
        # First run to set system prompt
        app.invoke({"messages": [SystemMessage(content=SYSTEM_PROMPT)]}, config=config)
    else:
        print("Resuming previous session...")

    print("Agent: 您好，我是您的团险顾问。请问有什么可以帮您？")
    
    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Bye!")
                break
            
            # Run Graph
            # The output of app.invoke is the final state
            final_state = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
            
            # Get the last message from the agent
            agent_response = final_state["messages"][-1]
            print(f"\nAgent: {agent_response.content}")
            
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()
