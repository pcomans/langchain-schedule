from typing import Optional, Type, Callable
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from ..scheduler import AgentScheduler

class RescheduleInput(BaseModel):
    """Input for the reschedule tool."""
    minutes: int = Field(
        ...,
        description="Number of minutes to wait before continuing the conversation"
    )
    reason: str = Field(
        ...,
        description="Why you want to continue this conversation later"
    )

class RescheduleTool(BaseTool):
    """Tool for scheduling future continuations of the current conversation."""
    
    name: str = "reschedule_self"
    description: str = """Schedule the agent to continue this conversation after a specified number of minutes.
    Provide the number of minutes to wait and a reason for scheduling."""
    
    args_schema: Type[BaseModel] = RescheduleInput
    
    # Declare the fields properly
    scheduler: AgentScheduler = Field(..., description="The scheduler instance to use")
    agent_callback: Callable = Field(..., description="The function to call to continue the conversation")
    current_thread_id: Optional[str] = Field(None, description="The current thread ID if in a conversation")
    
    def _run(
        self,
        minutes: int,
        reason: str,
        **kwargs
    ) -> str:
        """Schedule a continuation of the current conversation.
        
        Args:
            minutes: Number of minutes to wait
            reason: Why the continuation is being scheduled
            
        Returns:
            A confirmation message
        """
        if not self.current_thread_id:
            raise ValueError("No thread ID available - tool must be used within a conversation")
        
        try:
            run_date = datetime.now() + timedelta(minutes=minutes)
            
            # Schedule the continuation
            self.scheduler.schedule_continuation(
                run_date=run_date.isoformat(),
                thread_id=self.current_thread_id,
                agent_callback=self.agent_callback,
                context={"reschedule_reason": reason}
            )
            
            return f"Scheduled to continue this conversation in {minutes} minutes because: {reason}"
            
        except ValueError as e:
            return f"Error scheduling continuation: {str(e)}"
    
    async def _arun(self, minutes: int, reason: str, **kwargs) -> str:
        """Async version of _run."""
        return self._run(minutes, reason, **kwargs) 