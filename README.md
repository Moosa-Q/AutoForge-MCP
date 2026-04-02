# AutoForge-MCP

The automated framework for Model Context Protocol (MCP) integration and development.

AutoForge-MCP is a streamlined toolkit designed to accelerate the creation, testing, and deployment of MCP servers. It provides a standardized architecture for connecting LLMs to local data sources, tools, and custom environments.

## 🚀 Key Features

- **Modular Server Architecture:** Easily plug in new data sources.
- **Automated Schema Generation:** Auto-sync your tools with MCP specifications.
- **Built-in Debugger:** Pre-configured environments for local testing.

## 📋 Requirements

- [UV](https://docs.astral.sh/uv/#installation)
- [OpenAI API Key](https://platform.openai.com/home)

## 🛠 Installation
```powershell
git clone https://github.com/Moosa-Q/AutoForge-MCP.git
cd AutoForge-MCP
npm install  # or pip install -r requirements.txt
```

## 📖 Usage

1. Create the MCP Server
- Run:
```
uv run main.py
```
- Select Option 1 to create an mcp server and then describe your mcp server and the tools that should be in it
- You will see a new file popup in vs code
2. Run that MCP server
- Run
```
uv run script_name.py
```
- Fill in script_name.py with the new file containing the MCP server by the AI.
3. Run the Client UI to test
- Run:
```
uv run main.py
```
- Select Option 3 to Launch Client UI