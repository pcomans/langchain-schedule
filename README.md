# LangChain Schedule

A self-scheduling agent system built with LangChain that enables AI agents to schedule and manage their own follow-up conversations. This project demonstrates how to create agents that can autonomously schedule check-ins and maintain conversation state across time.

## Features

- 🕒 Precise scheduling with second-level accuracy
- 🧵 Thread-based conversation management
- 💾 State persistence across scheduled continuations
- 🔄 Automatic time zone handling
- ⚡ Easy integration with LangChain agents

## Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd langchain_schedule
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Create a `.env` file in the root directory and add your OpenAI API key:
```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage

The project includes example scripts demonstrating the self-scheduling capabilities. To run the basic example:

```bash
poetry run python examples/self_scheduling_agent.py
```

This will:
1. Start a conversation with an AI agent
2. Schedule a check-in at the next full minute
3. Continue the conversation at the scheduled time
4. Maintain conversation context across the scheduled continuation

## Example Execution

Here's a real interaction with the agent:

```
Human: Hi! I'm boiling water for tea. It will be ready at the next full minute. Can you check in then?

> Entering new AgentExecutor chain...

Invoking: `reschedule_self` with `{'seconds': 11, 'reason': 'to check back when the tea is ready at the next full minute.'}`
responded: I will now schedule a continuation because you want me to check back when your tea is ready at the next full minute. Let's make sure your tea is perfect!

Debug: RescheduleTool._run called with:
  seconds: 11
  reason: to check back when the tea is ready at the next full minute.
  thread_id: thread_1
Scheduled to continue this conversation in 11 seconds because: to check back when the tea is ready at the next full minute.

I'm back! How's the tea coming along?

> Finished chain.

Agent scheduled! Waiting for continuation...
Press Ctrl+C to exit

Debug: Agent callback triggered

> Entering new AgentExecutor chain...
I will now schedule a continuation because you asked me to check back when your tea is ready. Let me know how your tea turns out!

> Finished chain.
```

This example demonstrates:
1. Natural conversation about a real-world task (making tea)
2. Calculating the appropriate delay until the next minute
3. Scheduling and confirming the continuation
4. Maintaining conversation context when reactivated
5. Engaging naturally with the user about their task

## How It Works

### Core Components

1. **AgentScheduler**
   - Manages scheduling and thread management
   - Handles state persistence
   - Coordinates conversation continuations

2. **RescheduleTool**
   - LangChain tool for self-scheduling
   - Enables agents to schedule their own continuations
   - Maintains conversation context

3. **Thread Management**
   - Each conversation gets a unique thread ID
   - State is isolated between different conversations
   - Enables parallel conversations without interference

### Architecture

The system uses:
- `APScheduler` for reliable job scheduling
- `LangGraph` for state management
- `python-dotenv` for environment configuration
- LangChain's tools and agents system

### Flow

1. When a conversation starts:
   - A new thread ID is generated
   - Initial state is saved
   - Agent is initialized with scheduling capabilities

2. When scheduling a continuation:
   - Agent uses RescheduleTool to set a future check-in
   - Current conversation state is preserved
   - A job is scheduled with APScheduler

3. At the scheduled time:
   - Previous conversation state is restored
   - Agent continues with full context
   - New scheduling can occur if needed

## Example Use Cases

- Scheduling follow-up checks on long-running processes
- Setting reminders for future tasks
- Creating conversation chains with time gaps
- Implementing spaced repetition systems
- Managing recurring check-ins

## Development

The project structure:
```
src/langchain_schedule/
├── scheduler.py      # Core scheduling functionality
├── tools/
│   └── reschedule.py # Scheduling tool implementation
└── __init__.py      # Package initialization

examples/
└── self_scheduling_agent.py  # Usage example
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
