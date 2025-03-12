from typing import Any, Dict, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from langgraph.store.memory import InMemoryStore
from datetime import datetime
import threading

class AgentScheduler:
    """Manages scheduling and thread management for self-scheduling agents."""
    
    def __init__(self):
        """Initialize the scheduler with a background scheduler and memory management."""
        # Initialize APScheduler
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        
        # Initialize memory store
        self.memory = InMemoryStore()
        
        # Thread management
        self.thread_counter = 0
        self._stop_event = threading.Event()
    
    def generate_thread_id(self) -> str:
        """Generate a unique thread ID for a new conversation."""
        self.thread_counter += 1
        return f"thread_{self.thread_counter}"
    
    def wait(self):
        """Wait until stop is called."""
        try:
            while not self._stop_event.is_set():
                self._stop_event.wait(1)  # Wait for 1 second between checks
        except KeyboardInterrupt:
            self._stop_event.set()
    
    def stop(self):
        """Signal to stop waiting."""
        self._stop_event.set()
    
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
            try:
                # Get the conversation state
                namespace = (thread_id, "conversation")
                memories = self.memory.search(namespace)
                if not memories:
                    raise ValueError(f"No state found for thread {thread_id}")
                
                state = memories[-1].value
                
                # Add any additional context
                if context:
                    state.update(context)
                
                # Continue the conversation
                agent_callback(
                    messages=state.get("messages", []),
                    config={"configurable": {"thread_id": thread_id}}
                )
            except Exception as e:
                print(f"Error in continuation: {str(e)}")
        
        # Schedule the continuation
        self.scheduler.add_job(
            _continue_conversation,
            'date',
            run_date=run_date,
            id=f"continuation_{thread_id}"
        )
    
    def get_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state for a thread ID."""
        namespace = (thread_id, "conversation")
        memories = self.memory.search(namespace)
        return memories[-1].value if memories else None
    
    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save state for a thread ID."""
        namespace = (thread_id, "conversation")
        self.memory.put(namespace, datetime.now().isoformat(), state)
    
    def shutdown(self):
        """Shutdown the scheduler properly."""
        self.stop()
        self.scheduler.shutdown() 