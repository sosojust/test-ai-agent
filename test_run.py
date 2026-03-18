import os
from dotenv import load_dotenv
load_dotenv()
from src.agent.graph import graph
from langchain_core.messages import HumanMessage

state = {"messages": [HumanMessage(content="你好，我想咨询一下团险")]}
result = graph.invoke(state)
print("Finished!")
