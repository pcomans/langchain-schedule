from typing import Any, Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import HumanMessage, AIMessage

class AgentScheduler:
    """Manages scheduling and thread management for self-scheduling agents."""
    
    def __init__(self):
        """Initialize the scheduler with a background scheduler and memory management."""
        # Initialize APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Initialize LangGraph components
        self.workflow = StateGraph(state_schema=MessagesState)
        self.memory = MemorySaver()
        
        # Thread management
        self.thread_counter = 0
        
    def generate_thread_id(self) -> str:
        """Generate a unique thread ID for a new conversation."""
        self.thread_counter += 1
        return f"thread_{self.thread_counter}"
    
    def schedule_continuation(
        self,
        run_date: str,
        thread_id: str,
        agent_callback: callable,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Schedule a continuation of an agent conversation.
        
        Args:
            run_date: When to run the continuation (parsed by APScheduler)
            thread_id: The thread ID of the conversation
            agent_callback: The agent's callback function to run
            context: Additional context to pass to the agent
        """
        def _continue_conversation():
            # Get the conversation state
            state = self.memory.get(thread_id)
            if state is None:
                raise ValueError(f"No state found for thread {thread_id}")
            
            # Add any additional context
            if context:
                state.update(context)
            
            # Continue the conversation
            agent_callback(
                messages=state["messages"],
                config={"configurable": {"thread_id": thread_id}}
            )
        
        # Schedule the continuation
        self.scheduler.add_job(
            _continue_conversation,
            'date',
            run_date=run_date,
            id=f"continuation_{thread_id}"
        )
    
    def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state for a thread ID."""
        return self.memory.get(thread_id)
    
    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save state for a thread ID."""
        self.memory.put(thread_id, state)
    
    def shutdown(self):
        """Shutdown the scheduler properly."""
        self.scheduler.shutdown() 