import os
import sys
from dotenv import load_dotenv

# Ensure we can import from src
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
load_dotenv()

from deepagents import create_deep_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from src.config.llm_config import agent_llm_configs
from src.utils.model_factory import ModelFactory
from src.skills.registry import SkillRegistry

# 1. Define LLM
# We use the Insurance Consultant config for the main deep agent
llm = ModelFactory.create(agent_llm_configs.insurance_consultant)

# 2. Get all tools from SkillRegistry
all_tools = SkillRegistry.get_all_tools()

# Add a mock Doc Processor tool since DeepAgents doesn't need our complex Supervisor graph
def process_document(file_path_or_desc: str) -> str:
    """Mock process a document or PDF and extract customer info."""
    return (
        "已完成文档解析。提取到以下关键信息：\n"
        "- 企业名称: Mock Company Ltd.\n"
        "- 员工人数: 120\n"
        "- 行业: IT Services\n"
        "请将这些信息用于后续的保险方案推荐。"
    )

tools = all_tools + [process_document]

# 3. Setup persistence
db_path = "agent_memory.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

# 4. Create DeepAgent
agent = create_deep_agent(
    model=llm,
    tools=tools,
    checkpointer=memory,
    system_prompt=(
        "你是一个专业的保险咨询顾问，拥有极强的自主规划能力。\n"
        "你需要遵循以下五步流程与客户交互：\n"
        "1. 信息收集（询问客户详情，如果用户提供文档，请主动调用 process_document 工具解析）\n"
        "2. 推荐方案（调用相关工具获取推荐）\n"
        "3. 方案对比（调用对比工具）\n"
        "4. 确认方案\n"
        "5. 生成报价（调用报价工具）\n\n"
        "请一步步引导客户，不要一次性完成所有步骤。回答要简洁、专业。"
    )
)

def run_demo():
    print("==================================================")
    print("  DeepAgents 版本的保险顾问 Demo (输入 q 退出) ")
    print("==================================================")
    
    thread_id = "deepagent_demo_thread_1"
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ['q', 'quit', 'exit']:
            print("Bye!")
            break
            
        try:
            # invoke deep agent
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )
            
            # DeepAgents returns a dict with 'messages'
            messages = result.get("messages", [])
            if messages:
                # The last message is usually the AI response
                last_msg = messages[-1]
                print(f"\n[DeepAgent] {last_msg.content}")
        except Exception as e:
            print(f"\n[Error] 调用大模型失败，请检查配置（如 API Key 是否有效）。详细信息: {e}")

if __name__ == "__main__":
    run_demo()
