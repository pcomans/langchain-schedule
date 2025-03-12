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
