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
    """Get the static system prompt."""
    return """You are a helpful AI assistant capable of scheduling future conversations.
    
    When using the reschedule_self tool:
    - Announce your intention: "I will now schedule a continuation because [reason]"
    - Then proceed with the scheduling

    When continuing a previous conversation:
    - Acknowledge why you're continuing the conversation
    - Engage naturally with the user"""

def get_time_update() -> str:
    """Get the current time information."""
    now = datetime.now().astimezone()
    return f"[TIME UPDATE] Current time: {now.isoformat()}"

def create_agent(scheduler: AgentScheduler, thread_id: str = None):
    """Create an agent with self-scheduling capability."""
    
    # Create the base model
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0
    )
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", get_system_prompt()),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    # Create the rescheduling tool
    def agent_callback(messages, config):
        print("\nDebug: Agent callback triggered")  # Debug print
        
        # Get the continuation reason from context if available
        context = config.get("configurable", {})
        reason = context.get("reschedule_reason", "scheduled continuation")
        
        # Add time update
        time_message = AIMessage(content=get_time_update())
        messages.append(time_message)
        
        # Add a system note about the continuation
        system_note = AIMessage(content=f"[SYSTEM NOTE: You are now being activated for the previously scheduled check-in. Original reason: {reason}. This is the check-in itself, not a request to schedule one.]")
        messages.append(system_note)
        
        # Save the current state
        scheduler.save_state(config["configurable"]["thread_id"], {"messages": messages})
        
        # This will be called when the scheduled time arrives
        result = executor.invoke({"messages": messages}, config=config)
        return result
    
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
        
        # Start a conversation with initial time update
        messages = [
            AIMessage(content=get_time_update()),
            HumanMessage(content="Hi! I'm boiling water for tea. It will be ready at the next full minute. Can you check in then?")
        ]
        
        # Save initial state
        scheduler.save_state(thread_id, {"messages": messages})
        
        # Run the agent
        response = agent.invoke(
            {"messages": messages},
            config={"configurable": {"thread_id": thread_id}}
        )
        
        print("\nAgent scheduled! Waiting for continuation...")
        print("Press Ctrl+C to exit")
        
        # Block until there are no more pending jobs or Ctrl+C is pressed
        while scheduler.scheduler.get_jobs():
            try:
                # Sleep for a short time to prevent CPU spinning
                time.sleep(0.1)
            except KeyboardInterrupt:
                break
    
    finally:
        # Ensure proper shutdown
        scheduler.shutdown()

if __name__ == "__main__":
    main() 