from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
import time

from langchain_schedule.scheduler import AgentScheduler
from langchain_schedule.tools.reschedule import RescheduleTool

# Load environment variables from .env
load_dotenv()

def get_system_prompt() -> str:
    """Get the system prompt with current time."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    timezone = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    return f"""You are a helpful AI assistant capable of scheduling future conversations.
    The current time is: {current_time} {timezone}
    
    If a task requires checking something later, use the reschedule_self tool to continue 
    the conversation after a specified number of minutes.
    
    When scheduling, always specify the delay in minutes. For example:
    - "Check in 1 minute" -> minutes=1
    - "Check in an hour" -> minutes=60
    - "Check in 2 hours" -> minutes=120
    
    When you are reactivated from a scheduled continuation, first explain why you were
    scheduled to continue this conversation, and mention how much time has passed."""

def create_agent(scheduler: AgentScheduler, thread_id: str = None):
    """Create an agent with self-scheduling capability."""
    
    # Create the base model
    model = ChatOpenAI(temperature=0)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the rescheduling tool
    def agent_callback(messages, config):
        # Update the system message with current time before continuing
        if isinstance(messages[0], SystemMessage):
            messages[0] = SystemMessage(content=get_system_prompt())
        else:
            messages.insert(0, SystemMessage(content=get_system_prompt()))
        # This will be called when the scheduled time arrives
        executor.invoke({"messages": messages}, config=config)
    
    tools = [
        RescheduleTool(
            scheduler=scheduler,
            agent_callback=agent_callback,
            current_thread_id=thread_id
        )
    ]
    
    # Create the agent
    agent = create_openai_functions_agent(model, tools, prompt)
    
    # Create the executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )
    
    return executor

def main():
    # Initialize the scheduler
    scheduler = AgentScheduler()
    
    try:
        # Generate a thread ID for this conversation
        thread_id = scheduler.generate_thread_id()
        
        # Create the agent
        agent = create_agent(scheduler, thread_id)
        
        # Start a conversation
        messages = [
            HumanMessage(content="Hi! Could you schedule a reminder to check on me in 1 minute?")
        ]
        
        # Run the agent
        response = agent.invoke(
            {"messages": messages},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        print("\nAgent scheduled! Waiting for continuation...")
        print("Press Ctrl+C to exit")
        
        # Keep the script running
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("\nShutting down...")
    
    finally:
        # Ensure proper shutdown
        scheduler.shutdown()

if __name__ == "__main__":
    main() 