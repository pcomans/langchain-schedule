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

def get_seconds_to_next_minute():
    """Calculate the number of seconds until the next full minute."""
    now = datetime.now()
    seconds_to_next = 60 - now.second
    return seconds_to_next

def get_system_prompt() -> str:
    """Get the system prompt with current time."""
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    timezone = time.tzname[time.daylight] if time.daylight else time.tzname[0]
    seconds_to_next = get_seconds_to_next_minute()
    
    return f"""You are a helpful AI assistant capable of scheduling future conversations.
    The current time is: {current_time} {timezone}
    Seconds until next full minute: {seconds_to_next}
    
    SCHEDULING RULES:
    1. Only use the reschedule_self tool when EXPLICITLY asked to check something later
    2. Never automatically schedule follow-ups without being asked
    3. Before scheduling, announce your intention: "I will now schedule a continuation because [reason]"
    4. When scheduling, specify delays in seconds:
       - "Check in 30 seconds" -> seconds=30
       - "Check in a minute" -> seconds=60
       - "Check in 2 minutes" -> seconds=120
    5. For next full minute scheduling, use the seconds shown above in "Seconds until next full minute"
    
    When continuing a previous conversation:
    - Acknowledge why you're continuing the conversation
    - Engage naturally with the user
    - Wait for explicit instructions before scheduling any further continuations"""

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
        print("\nDebug: Agent callback triggered")  # Debug print
        
        # Get the continuation reason from context if available
        context = config.get("configurable", {})
        reason = context.get("reschedule_reason", "scheduled continuation")
        
        # Add a system note about the continuation
        system_note = AIMessage(content=f"[SYSTEM NOTE: You are now being activated for the previously scheduled check-in. Original reason: {reason}. This is the check-in itself, not a request to schedule one.]")
        messages.append(system_note)
        
        # Update the system message with current time
        if isinstance(messages[0], SystemMessage):
            messages[0] = SystemMessage(content=get_system_prompt())
        else:
            messages.insert(0, SystemMessage(content=get_system_prompt()))
        
        # Save the current state
        scheduler.save_state(config["configurable"]["thread_id"], {"messages": messages})
        
        # This will be called when the scheduled time arrives
        print("\nDebug: About to invoke executor")  # Debug print
        result = executor.invoke({"messages": messages}, config=config)
        print("\nDebug: Executor invocation complete")  # Debug print
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
        
        # Start a conversation
        messages = [
            HumanMessage(content="Hi! Could you do a single check-in at the next full minute? For example, if it's 2:45:30, check in once at 2:46:00.")
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