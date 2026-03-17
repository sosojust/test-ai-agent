import os
import sqlite3
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv

from src.agent.graph import build_graph

# Load env
load_dotenv()

app = FastAPI(title="团险询报价 AI Agent API")

# Initialize Checkpointer
# Note: In a production environment, you might want to use a connection pool or a more robust database.
# For demo, we create a connection per request or a shared connection (SqliteSaver handles connection internally if path provided? 
# SqliteSaver.from_conn_string is a context manager usually, but can be used with a connection).
# Let's keep it simple: Create a global variable for the graph with checkpointer.
# But SqliteSaver needs a connection. 
# Better: Initialize graph in startup or dependency.
# For this demo, let's create a fresh connection for the saver in the dependency or global scope if safe.
# SqliteSaver.from_conn_string("agent_history.db") returns a context manager.
# Let's use a simpler approach for the demo: open connection when needed.

DB_PATH = "agent_history.db"

class ChatRequest(BaseModel):
    thread_id: str
    message: str

class EventRequest(BaseModel):
    thread_id: str
    event_type: str
    payload: Dict[str, Any]

class ChatResponse(BaseModel):
    thread_id: str
    response: str
    messages: List[str]

def get_agent_executor(conn):
    checkpointer = SqliteSaver(conn)
    workflow = build_graph()
    app = workflow.compile(checkpointer=checkpointer)
    return app

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Standard chat interface.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        agent = get_agent_executor(conn)
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Invoke agent
        # We need to pass the message. The graph expects 'messages' key in state.
        # But for invoke, we can pass inputs directly.
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        # invoke returns the final state
        final_state = agent.invoke(inputs, config=config)
        
        messages = final_state["messages"]
        last_message = messages[-1]
        
        return ChatResponse(
            thread_id=request.thread_id,
            response=last_message.content if hasattr(last_message, "content") else str(last_message),
            messages=[m.content for m in messages]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/v1/event", response_model=ChatResponse)
async def event_endpoint(request: EventRequest):
    """
    External system event trigger interface.
    
    Example:
    {
        "thread_id": "sys_trigger_001",
        "event_type": "policy_expiring",
        "payload": {
            "customer_name": "ABC科技",
            "policy_id": "P12345",
            "expiry_date": "2024-06-01"
        }
    }
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        agent = get_agent_executor(conn)
        config = {"configurable": {"thread_id": request.thread_id}}
        
        # Construct a message from the event
        # Depending on how the agent is designed, we might send a SystemMessage or a ToolMessage.
        # Here we simulate a system notification as a HumanMessage to trigger the agent to act.
        
        event_desc = f"系统通知: 收到外部事件 [{request.event_type}]。\n数据: {request.payload}\n请根据此信息处理。"
        
        inputs = {"messages": [HumanMessage(content=event_desc)]}
        
        final_state = agent.invoke(inputs, config=config)
        
        messages = final_state["messages"]
        last_message = messages[-1]
        
        return ChatResponse(
            thread_id=request.thread_id,
            response=last_message.content if hasattr(last_message, "content") else str(last_message),
            messages=[m.content for m in messages]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
