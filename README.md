<p align="center">
  <img src="logo.png" width="200">
</p>

# LLM Bomb Defusal

A text-based implementation of "Keep Talking and Nobody Explodes" with LLM-powered agents. This project demonstrates two language model agents collaborating to solve a bomb defusal puzzle - one agent acts as the Defuser (who can see the bomb but not the manual) and the other as the Expert (who has the manual but can't see the bomb).

## Project Overview

The system consists of:

1. **Game Server**: A text-based bomb defusal game with multiple modules (Regular Wires, Button, Simon Says, Memory)
2. **Agent Framework**: LLM-powered agents that can interact with the game
3. **Client-Server Architecture**: Using the MCP (Message Communication Protocol) for communication

## Architecture

```
├── agents/                  # LLM agent implementation
│   ├── models.py            # Base HFModel class and SmollLLM implementation
│   ├── prompts.py           # System prompts for Defuser and Expert roles
│   ├── two_agents.py        # Main orchestration of the two LLM agents
│
├── game/                    # Core game logic
│   ├── bomb.py              # Main Bomb class
│   ├── main.py              # Manual game mode for human players
│   ├── modules/             # Different bomb modules
│       ├── module.py        # Base Module class and ActionResult enum
│       ├── regular_wires_module.py
│       ├── button_module.py
│       ├── simon_says_module.py
│       ├── memory_module.py
│
├── game_mcp/                # MCP server/client implementation
│   ├── game_server.py       # Server exposing game API via MCP
│   ├── game_client.py       # Client classes for Defuser and Expert roles
│
└── crewai_bomb/             # CrewAI-specific implementation
    ├── crew.py              # CrewAI implementation of two_agents.py
    ├── tools.py             # CrewAI tools for LLM interaction
```

## Usage

### Running the Game Server

Start the game server:

```bash
python -m game_mcp.game_server --host 0.0.0.0 --port 8080
```

#### MCP Server Tools

1. `game_interaction(command: str) -> str`
2. `get_manual() -> str`



These tools are exposed via SSE (Server-Sent Events) and designed to support real-time collaboration between players using the MCP protocol. Each tool acts like an interactive function that handles game logic or provides helpful context to players.



## License

[MIT License](LICENSE)

## Acknowledgments

Inspired by the game "Keep Talking and Nobody Explodes" by Steel Crate Games.