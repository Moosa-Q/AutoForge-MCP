"""
MCP × OpenAI Chatbot — Streamlit
=================================
Single-file app: OpenAI agentic backend + Streamlit UI.

Run:
    streamlit run app.py

Env vars:
    OPENAI_API_KEY   your OpenAI key (or paste it in the sidebar)
    MCP_URL          defaults to http://localhost:8000
"""

import asyncio
import json
import os
import textwrap
from typing import Any

import streamlit as st
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import Tool
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MCP Chat",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,300;0,400;1,300&display=swap');

/* ── Reset & base ────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}

/* Dark canvas */
.stApp {
    background: #0d0f14;
    color: #e8e6e0;
}

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #111318 !important;
    border-right: 1px solid #1e2230;
}
[data-testid="stSidebar"] * {
    color: #c8c5bc !important;
}

/* ── Header strip ────────────────────────────────────────────── */
.app-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px 0 10px;
    border-bottom: 1px solid #1e2230;
    margin-bottom: 22px;
}
.app-header-icon {
    font-size: 2rem;
    line-height: 1;
}
.app-header-title {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #f0ede6;
    margin: 0;
}
.app-header-sub {
    font-size: 0.78rem;
    color: #555c72;
    font-family: 'DM Mono', monospace;
    margin: 0;
    letter-spacing: 0.5px;
}

/* ── Chat bubbles ────────────────────────────────────────────── */
.bubble-wrap {
    display: flex;
    margin-bottom: 18px;
    gap: 12px;
    align-items: flex-start;
}
.bubble-wrap.user   { flex-direction: row-reverse; }
.bubble-wrap.assistant { flex-direction: row; }

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
}
.avatar.user      { background: #1e6bff22; border: 1px solid #1e6bff55; }
.avatar.assistant { background: #00c9862a; border: 1px solid #00c98644; }

.bubble {
    max-width: 72%;
    padding: 13px 17px;
    border-radius: 16px;
    font-size: 0.92rem;
    line-height: 1.65;
    font-family: 'Syne', sans-serif;
}
.bubble.user {
    background: #131c36;
    border: 1px solid #1e3166;
    color: #c5d4ff;
    border-top-right-radius: 4px;
}
.bubble.assistant {
    background: #0f1e1a;
    border: 1px solid #0d3328;
    color: #b8e8d8;
    border-top-left-radius: 4px;
}

/* ── Tool call pill ─────────────────────────────────────────── */
.tool-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1a1208;
    border: 1px solid #3d2a00;
    color: #e8a230;
    border-radius: 20px;
    padding: 3px 11px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    margin: 6px 4px 0 0;
}

/* ── Sidebar: tool panel ─────────────────────────────────────── */
.tool-server-label {
    font-size: 0.68rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 1.5px;
    color: #3a4060 !important;
    text-transform: uppercase;
    padding: 10px 0 4px;
}
.tool-card {
    background: #161923;
    border: 1px solid #1c2133;
    border-radius: 10px;
    padding: 11px 13px;
    margin-bottom: 9px;
    transition: border-color .2s;
}
.tool-card:hover { border-color: #2a3555; }
.tool-name {
    font-size: 0.82rem;
    font-weight: 700;
    color: #7eb8ff !important;
    margin-bottom: 4px;
}
.tool-desc {
    font-size: 0.73rem;
    color: #525c78 !important;
    line-height: 1.45;
}
.param-chip {
    display: inline-block;
    background: #0d1520;
    border: 1px solid #1a2840;
    color: #3d7aad !important;
    border-radius: 5px;
    padding: 1px 7px;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    margin: 3px 3px 0 0;
}

/* ── Status dot ─────────────────────────────────────────────── */
.status-row {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    color: #404866 !important;
    margin-bottom: 16px;
}
.dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.dot.green  { background: #00c986; box-shadow: 0 0 6px #00c98688; }
.dot.red    { background: #ff4060; box-shadow: 0 0 6px #ff406088; }
.dot.yellow { background: #f0a030; box-shadow: 0 0 6px #f0a03088; }

/* ── Input area ──────────────────────────────────────────────── */
[data-testid="stChatInput"] textarea {
    background: #111520 !important;
    border: 1px solid #1c2440 !important;
    color: #e0ddd5 !important;
    border-radius: 12px !important;
    font-family: 'Syne', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #2a4080 !important;
    box-shadow: 0 0 0 2px #1e3a6044 !important;
}

/* ── Scrollable chat column ──────────────────────────────────── */
.chat-scroll {
    max-height: 62vh;
    overflow-y: auto;
    padding-right: 8px;
    scrollbar-width: thin;
    scrollbar-color: #1e2230 transparent;
}

/* ── Misc ────────────────────────────────────────────────────── */
.stButton button {
    background: #131c36 !important;
    border: 1px solid #1e3166 !important;
    color: #7eaaff !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.8rem !important;
}
.stButton button:hover {
    background: #1a2644 !important;
    border-color: #2a4a99 !important;
}
div[data-testid="stTextInput"] input {
    background: #111520 !important;
    border: 1px solid #1c2440 !important;
    color: #e0ddd5 !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
}
.stSelectbox > div > div {
    background: #111520 !important;
    border: 1px solid #1c2440 !important;
    color: #e0ddd5 !important;
    border-radius: 8px !important;
}
hr { border-color: #1a1f2e !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND — MCP helpers
# ─────────────────────────────────────────────────────────────────────────────

def _mcp_tool_to_openai(tool: Tool) -> dict:
    """Convert MCP Tool → OpenAI function-calling schema."""
    schema = tool.inputSchema or {}
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": schema.get("properties", {}),
    }
    if "required" in schema:
        parameters["required"] = schema["required"]
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": parameters,
        },
    }


async def fetch_mcp_tools(mcp_url: str, timeout: float = 10.0) -> list[Tool]:
    """Connect to MCP server, retrieve tools, disconnect."""
    sse_url = f"{mcp_url.rstrip('/')}/sse"
    async with sse_client(sse_url, timeout=timeout) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            resp = await session.list_tools()
            return resp.tools


async def call_mcp_tool(
    mcp_url: str,
    tool_name: str,
    arguments: dict,
    timeout: float = 30.0,
) -> str:
    """Call a single MCP tool and return its text output."""
    sse_url = f"{mcp_url.rstrip('/')}/sse"
    async with sse_client(sse_url, timeout=timeout) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            parts = [
                block.text for block in result.content if hasattr(block, "text")
            ]
            return "\n".join(parts) if parts else "(no output)"


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND — OpenAI agentic loop
# ─────────────────────────────────────────────────────────────────────────────

async def run_agent(
    api_key: str,
    model: str,
    mcp_url: str,
    tools: list[Tool],
    history: list[ChatCompletionMessageParam],
    user_message: str,
    system_prompt: str,
    max_iter: int = 8,
) -> tuple[str, list[dict]]:
    """
    Run one user turn through the OpenAI agentic loop.

    Returns:
        (final_text, tool_calls_log)
        tool_calls_log: list of {"name": ..., "args": ..., "result": ...}
    """
    client = AsyncOpenAI(api_key=api_key)
    openai_tools = [_mcp_tool_to_openai(t) for t in tools] or None

    messages: list[ChatCompletionMessageParam] = [
        {"role": "system", "content": system_prompt},
        *history,
        {"role": "user", "content": user_message},
    ]
    tool_log: list[dict] = []

    for _ in range(max_iter):
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=openai_tools,          # type: ignore[arg-type]
            tool_choice="auto" if openai_tools else None,
        )
        msg = response.choices[0].message
        finish = response.choices[0].finish_reason
        messages.append(msg)             # type: ignore[arg-type]

        if finish == "tool_calls" and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                result = await call_mcp_tool(mcp_url, name, args)
                tool_log.append({"name": name, "args": args, "result": result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
            continue

        if finish == "stop":
            return msg.content or "", tool_log

    return "(Max iterations reached.)", tool_log


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS — sync wrappers & caching
# ─────────────────────────────────────────────────────────────────────────────

def run_async(coro):
    """Run an async coroutine from sync Streamlit context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@st.cache_data(show_spinner=False, ttl=30)
def get_tools_cached(mcp_url: str) -> list | None:
    """Fetch and cache MCP tools (TTL 30 s)."""
    try:
        tools = run_async(fetch_mcp_tools(mcp_url))
        return tools
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# UI — Sidebar
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar(mcp_url: str) -> tuple[str, str, str, str]:
    """Render sidebar; returns (api_key, model, mcp_url, system_prompt)."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("---")

        api_key = st.text_input(
            "OpenAI API Key",
            value=os.environ.get("OPENAI_API_KEY", ""),
            type="password",
            placeholder="sk-...",
        )
        model = st.selectbox(
            "Model",
            ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0,
        )
        mcp_url_input = st.text_input(
            "MCP Server URL",
            value=os.environ.get("MCP_URL", mcp_url),
            placeholder="http://localhost:8000",
        )
        system_prompt = st.text_area(
            "System Prompt",
            value=(
                "You are a helpful assistant with access to MCP tools. "
                "Use them proactively whenever they can help the user."
            ),
            height=90,
        )

        st.markdown("---")

        # ── Tool panel ───────────────────────────────────────────
        col1, col2 = st.columns([1, 1])
        with col1:
            show_tools = st.button("🛠️ View Tools", use_container_width=True)
        with col2:
            if st.button("↺ Refresh", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        if show_tools:
            st.session_state["show_tool_panel"] = not st.session_state.get(
                "show_tool_panel", False
            )

        if st.session_state.get("show_tool_panel", False):
            render_tool_panel(mcp_url_input)

        st.markdown("---")
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    return api_key, model, mcp_url_input, system_prompt


def render_tool_panel(mcp_url: str) -> None:
    """Render the MCP tool explorer inside the sidebar."""
    with st.spinner("Fetching tools…"):
        tools = get_tools_cached(mcp_url)

    if tools is None:
        st.markdown(
            '<div class="status-row">'
            '<div class="dot red"></div>Cannot reach MCP server</div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f'<div class="status-row">'
        f'<div class="dot green"></div>{len(tools)} tool(s) at '
        f'<code style="font-size:.65rem;color:#3d7aad">{mcp_url}</code></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="tool-server-label">🔌 localhost:8000</p>',
        unsafe_allow_html=True,
    )

    for tool in tools:
        schema = tool.inputSchema or {}
        props = schema.get("properties", {})
        required = schema.get("required", [])

        chips_html = ""
        for pname, pschema in props.items():
            req_star = "﹡" if pname in required else ""
            ptype = pschema.get("type", "any")
            chips_html += (
                f'<span class="param-chip">{pname}: {ptype}{req_star}</span>'
            )

        desc = textwrap.shorten(tool.description or "No description.", width=110)
        st.markdown(
            f"""
            <div class="tool-card">
              <div class="tool-name">🔧 {tool.name}</div>
              <div class="tool-desc">{desc}</div>
              <div style="margin-top:6px">{chips_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# UI — Chat area
# ─────────────────────────────────────────────────────────────────────────────

def render_header(mcp_url: str, tools: list | None) -> None:
    tool_count = len(tools) if tools else 0
    status_dot = "green" if tools else "red"
    status_label = f"{tool_count} tool(s) ready" if tools else "MCP offline"

    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-icon">🛠️</div>
          <div>
            <p class="app-header-title">MCP Chat</p>
            <p class="app-header-sub">
              <span class="dot {status_dot}" style="display:inline-block;
                width:7px;height:7px;border-radius:50%;margin-right:5px;
                vertical-align:middle;
                background:{'#00c986' if tools else '#ff4060'};
                box-shadow:0 0 5px {'#00c986' if tools else '#ff4060'}88"></span>
              {status_label} &nbsp;·&nbsp; {mcp_url}
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_message(role: str, content: str, tool_calls: list[dict] | None = None) -> None:
    avatar = "🧑" if role == "user" else "✦"
    bubble_class = role  # "user" or "assistant"

    tool_html = ""
    if tool_calls:
        for tc in tool_calls:
            args_str = json.dumps(tc["args"], ensure_ascii=False)
            short_args = textwrap.shorten(args_str, width=60)
            tool_html += (
                f'<span class="tool-pill">⚙ {tc["name"]}'
                f'<span style="opacity:.5;font-size:.65rem"> {short_args}</span></span>'
            )
        tool_html = f'<div style="margin-top:8px">{tool_html}</div>'

    st.markdown(
        f"""
        <div class="bubble-wrap {bubble_class}">
          <div class="avatar {bubble_class}">{avatar}</div>
          <div class="bubble {bubble_class}">
            {content.replace(chr(10), "<br>")}
            {tool_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_history() -> None:
    for msg in st.session_state.get("messages", []):
        render_message(
            msg["role"],
            msg["content"],
            msg.get("tool_calls"),
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    DEFAULT_MCP_URL = "http://localhost:8000"

    # ── Session state init ───────────────────────────────────────
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "show_tool_panel" not in st.session_state:
        st.session_state["show_tool_panel"] = False

    # ── Sidebar ──────────────────────────────────────────────────
    api_key, model, mcp_url, system_prompt = render_sidebar(DEFAULT_MCP_URL)

    # ── Fetch tools (for header + agent) ────────────────────────
    tools = get_tools_cached(mcp_url) if mcp_url else None

    # ── Header ──────────────────────────────────────────────────
    render_header(mcp_url, tools)

    # ── Chat history ─────────────────────────────────────────────
    render_chat_history()

    # ── Chat input ───────────────────────────────────────────────
    user_input = st.chat_input("Message MCP Chat…")

    if user_input:
        # Validate config
        if not api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar.")
            return
        if not mcp_url:
            st.warning("⚠️ Please enter an MCP server URL.")
            return

        # Show user bubble immediately
        render_message("user", user_input)
        st.session_state["messages"].append(
            {"role": "user", "content": user_input}
        )

        # Build conversation history for the agent (exclude current turn)
        history: list[ChatCompletionMessageParam] = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state["messages"][:-1]
        ]

        # Run agent
        with st.spinner("Thinking…"):
            try:
                final_text, tool_calls = run_async(
                    run_agent(
                        api_key=api_key,
                        model=model,
                        mcp_url=mcp_url,
                        tools=tools or [],
                        history=history,
                        user_message=user_input,
                        system_prompt=system_prompt,
                    )
                )
            except Exception as exc:
                final_text = f"❌ Error: {exc}"
                tool_calls = []

        # Render & store assistant reply
        render_message("assistant", final_text, tool_calls or None)
        st.session_state["messages"].append(
            {
                "role": "assistant",
                "content": final_text,
                "tool_calls": tool_calls or [],
            }
        )


if __name__ == "__main__":
    main()