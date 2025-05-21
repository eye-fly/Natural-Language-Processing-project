# LLM Bomb Defusal

A text-based implementation of "Keep Talking and Nobody Explodes" with LLM-powered agents. This project demonstrates two language model agents collaborating to solve a bomb defusal puzzle—one agent acts as the Defuser (who can see the bomb but not the manual), and the other as the Expert (who has the manual but can't see the bomb). The main focus of the project is to design a communication scheme that enables efficient information exchange between agents, simulating a natural conversation as in the original game.


## Project Overview

1. **Game Server**: A text-based bomb defusal game with multiple modules (Regular Wires, Button, Simon Says, Memory)
2. **Client-Server Architecture**: Using the MCP (Message Communication Protocol) for communication/interaction with game server
3. **Agent testing Framework**: Located in the `agents/` directory. testing different LLM and how different prompts, input stucture, hypererparameeters affect model performace/ability to solve modules.
3. **Agent Communication**: Located in the `crewai_bomb/` directory. A team of two agents working together using [crewai](https://docs.crewai.com/introduction).

```
├── agents/                  # Agent testing Framework(no communication)
│   ├── models.py            # implementation of all tested LLMS SmollLLM,Cohere,etc.
│   ├── prompts.py           
│   ├── test_loop.py        # Main program for agents testing/comparison
│
├── game/                    # Core game logic
│   ├── main.py              # Manual game mode (only for debugging)
│   ├── modules/             # Different bomb modules
│   ├── bomb.py              
│
├── game_mcp/                # MCP server/client implementation
│   ├── game_server.py       # Server exposing game API via MCP
│   ├── game_client.py       # Client classes for Defuser and Expert roles
│
└── crewai_bomb/             # CrewAI implementation with communication
    ├── crew.py              # CrewAI main loop implementation of two agents
    ├── tools.py             # tools for LLM interaction with game server
    ├── agents.py           
    ├── task.py             
```

## Report
The report for the task can be found in the `report.md` file, which contains all the findings from running the tests

## Usage

For any of the programs (`game_client.py`, `agents/test_loop.py`, `crewai_bomb/crew.py`), the game server must be started first.

The Defuser has the ability to 'restart' the game state, which is useful for running multiple tests without needing to restart the server.

### Running the Game Server

Start the game server:

```bash
python -m game_mcp.game_server --host 0.0.0.0 --port 8080
```

#### MCP Server Tools

1. `game_interaction(command: str) -> str`
2. `get_manual() -> str`


## License

[MIT License](LICENSE)

## Acknowledgments

Inspired by the game "Keep Talking and Nobody Explodes" by Steel Crate Games.

forked form https://github.com/Cleo3927/Natural-Language-Processing-project-2-student-version