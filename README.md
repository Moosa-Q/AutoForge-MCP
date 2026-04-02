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

1. Configure your tools in the `src/tools` directory.
2. Run `npm start` to initialize the MCP server.
3. Connect your favorite LLM client to the server endpoint.