from typing import Optional, Type, Callable
from datetime import datetime
from dateutil.parser import parse as parse_date
from pydantic import BaseModel, Field

from langchain.tools import BaseTool
from ..scheduler import AgentScheduler

class RescheduleInput(BaseModel):
    """Input for the reschedule tool."""
    when: str = Field(
        ...,
        description="When to schedule the continuation (e.g. 'in 2 hours', 'tomorrow at 9am')"
    )
    reason: str = Field(
        ...,
        description="Why you want to continue this conversation later"
    )

class RescheduleTool(BaseTool):
    """Tool for scheduling future continuations of the current conversation."""
    
    name: str = "reschedule_self"
    description: str = """Schedule the agent to continue this conversation at a later time.
    Use this when you need to check something again later or wait for a specific time.
    Provide a time (e.g. 'in 2 hours', 'tomorrow at 9am') and a reason for scheduling."""
    
    args_schema: Type[BaseModel] = RescheduleInput
    
    # Declare the fields properly
    scheduler: AgentScheduler = Field(..., description="The scheduler instance to use")
    agent_callback: Callable = Field(..., description="The function to call to continue the conversation")
    current_thread_id: Optional[str] = Field(None, description="The current thread ID if in a conversation")
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse a time string into a datetime object."""
        try:
            # First try parsing as an absolute date/time
            return parse_date(time_str, fuzzy=True)
        except ValueError:
            # If that fails, try parsing relative time
            # This is a simplified version - you might want to add more sophisticated parsing
            now = datetime.now()
            if "in" in time_str.lower():
                # Handle "in X hours/minutes"
                parts = time_str.lower().split()
                if "hour" in parts[-1]:
                    hours = int(parts[1])
                    return now.replace(hour=now.hour + hours)
                elif "minute" in parts[-1]:
                    minutes = int(parts[1])
                    return now.replace(minute=now.minute + minutes)
            raise ValueError(f"Could not parse time string: {time_str}")
    
    def _run(
        self,
        when: str,
        reason: str,
        **kwargs
    ) -> str:
        """Schedule a continuation of the current conversation.
        
        Args:
            when: When to schedule the continuation
            reason: Why the continuation is being scheduled
            
        Returns:
            A confirmation message
        """
        if not self.current_thread_id:
            raise ValueError("No thread ID available - tool must be used within a conversation")
        
        try:
            run_date = self._parse_time(when)
            
            # Schedule the continuation
            self.scheduler.schedule_continuation(
                run_date=run_date.isoformat(),
                thread_id=self.current_thread_id,
                agent_callback=self.agent_callback,
                context={"reschedule_reason": reason}
            )
            
            return f"Scheduled to continue this conversation at {run_date.strftime('%Y-%m-%d %H:%M:%S')} because: {reason}"
            
        except ValueError as e:
            return f"Error scheduling continuation: {str(e)}"
    
    async def _arun(self, when: str, reason: str, **kwargs) -> str:
        """Async version of _run."""
        return self._run(when, reason, **kwargs) 