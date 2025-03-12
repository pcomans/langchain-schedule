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
> Entering new AgentExecutor chain...

Invoking: `reschedule_self` with `{'seconds': 17, 'reason': 'the user requested a check-in at the next full minute.'}`
responded: I will now schedule a continuation because you requested a check-in at the next full minute. Let me handle that for you.

Debug: RescheduleTool._run called with:
  seconds: 17
  reason: the user requested a check-in at the next full minute.
  thread_id: thread_1
Scheduled to continue this conversation in 17 seconds because: the user requested a check-in at the next full minute.

I've scheduled a check-in for the next full minute. I'll be back shortly!

> Finished chain.

Agent scheduled! Waiting for continuation...
Press Ctrl+C to exit

Debug: Agent callback triggered

Debug: About to invoke executor

> Entering new AgentExecutor chain...
I will now schedule a continuation because you requested a check-in at the next full minute.

I have checked in as requested. If there's anything else you need, feel free to let me know!

> Finished chain.
```

This example demonstrates:
1. The agent receiving a request to check in at the next minute
2. Calculating the appropriate delay (17 seconds until next minute)
3. Scheduling and confirming the continuation
4. Maintaining conversation context when reactivated
5. Natural engagement when continuing the conversation

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
