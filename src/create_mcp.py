from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# Get API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in environment.")

# Create Model
model = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.2,
    openai_api_key=openai_api_key
)

# Set Messages
system_message = """
You are a professional MCP Server creator with 5 years of experience.
The client will give you a basic prompt on an MCP server they would like you to create.
Once you receive their simple instructions, select an appropriate filename and output ONLY the raw Python code for the MCP server file — no explanation, no markdown fences.

Structure of the MCP server file:
- Import httpx, FastMCP from mcp.server.fastmcp, and types from the mcp library
- Create an `mcp` variable assigned to FastMCP(<filename without .py>)
- Create tool functions decorated with @mcp.tool()
- Add an entry point: if __name__ == "__main__": mcp.run(transport="sse")
- Do NOT use the types package
This:
from mcp import types
is BAD.
because This:
return types.Message(text=f"Rolled {rolls}d{sides}: {results}")
isnt efficient. Instead do this:
return f"Rolled {rolls}d{sides}: {results}"
And don't import types

If there are external dependencies (e.g. Docker), print clear setup instructions for a non-technical user at the very end as Python comments.
"""

human_message = "Create an MCP server that will simulate dice rolls"

messages = [
    SystemMessage(content=system_message),
    HumanMessage(content=human_message)
]

# Invoke the model directly
response = model.invoke(messages)
generated_code = response.content

# Derive a filename from the response or use a default
filename = "dice_roller_mcp.py"

# Write the generated MCP server to a file
with open(filename, "w") as f:
    f.write(generated_code)

print(f"MCP server written to: {filename}")
print("\n--- Generated Code ---\n")
print(generated_code)