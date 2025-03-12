from typing import Optional, Type, Callable
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from ..scheduler import AgentScheduler

class RescheduleInput(BaseModel):
    """Input for the reschedule tool."""
    seconds: int = Field(
        ...,
        description="Number of seconds to wait before continuing the conversation"
    )
    reason: str = Field(
        ...,
        description="Why you want to continue this conversation later"
    )

class RescheduleTool(BaseTool):
    """Tool for scheduling future continuations of the current conversation."""
    
    name: str = "reschedule_self"
    description: str = """Schedule the agent to continue this conversation after a specified number of seconds.
    ONLY use this when explicitly asked to check back later.
    Provide the number of seconds to wait and a reason for scheduling."""
    
    args_schema: Type[BaseModel] = RescheduleInput
    
    # Declare the fields properly
    scheduler: AgentScheduler = Field(..., description="The scheduler instance to use")
    agent_callback: Callable = Field(..., description="The function to call to continue the conversation")
    current_thread_id: Optional[str] = Field(None, description="The current thread ID if in a conversation")
    
    def _run(
        self,
        seconds: int,
        reason: str,
        **kwargs
    ) -> str:
        """Schedule a continuation of the current conversation.
        
        Args:
            seconds: Number of seconds to wait
            reason: Why the continuation is being scheduled
            
        Returns:
            A confirmation message
        """
        print("\nDebug: RescheduleTool._run called with:")
        print(f"  seconds: {seconds}")
        print(f"  reason: {reason}")
        print(f"  thread_id: {self.current_thread_id}")
        
        if not self.current_thread_id:
            raise ValueError("No thread ID available - tool must be used within a conversation")
        
        try:
            run_date = datetime.now() + timedelta(seconds=seconds)
            
            # Schedule the continuation
            self.scheduler.schedule_continuation(
                run_date=run_date.isoformat(),
                thread_id=self.current_thread_id,
                agent_callback=self.agent_callback,
                context={"reschedule_reason": reason}
            )
            
            return f"Scheduled to continue this conversation in {seconds} seconds because: {reason}"
            
        except ValueError as e:
            return f"Error scheduling continuation: {str(e)}"
    
    async def _arun(self, seconds: int, reason: str, **kwargs) -> str:
        """Async version of _run."""
        return self._run(seconds, reason, **kwargs) 