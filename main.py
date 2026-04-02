#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        🚀 AutoForge-MCP Launcher 🚀                          ║
║              The Ultimate TUI for MCP Server Creation & Launch               ║
╚══════════════════════════════════════════════════════════════════════════════╝

Author: AutoForge-MCP Team
Version: 1.0.0
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
except ImportError:
    print("❌ Error: rich library not found!")
    print("📦 Installing rich...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.live import Live
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax

console = Console()

ASCII_ART = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║    ██╗     ███████╗██╗   ██╗███████╗██╗      ██╗ ██████╗ ███╗   ██╗███████╗   ║
    ║    ██║     ██╔════╝██║   ██║██╔════╝██║     ███║██╔═══██╗████╗  ██║██╔════╝   ║
    ║    ██║     █████╗  ██║   ██║███████╗██║     ╚██║██║   ██║██╔██╗ ██║█████╗     ║
    ║    ██║     ██╔══╝  ╚██╗ ██╔╝╚════██║██║      ██║██║   ██║██║╚██╗██║██╔══╝     ║
    ║    ███████╗███████╗ ╚████╔╝ ███████║███████╗ ██║╚██████╔╝██║ ╚████║███████╗   ║
    ║    ╚══════╝╚══════╝  ╚═══╝  ╚══════╝╚══════╝ ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ║
    ║                                                                  ║
    ║              🔥 Model Context Protocol Server Creator 🔥         ║
    ║                     Powered by AI & Streamlit                     ║
    ╚══════════════════════════════════════════════════════════════════╝
"""

MENU_ITEMS = [
    ("🎲", "1", "Create MCP Server", "Generate a new MCP server using AI 🤖"),
    ("🚀", "2", "Launch Server Terminal", "Open a terminal to run the MCP server 🖥️"),
    ("💬", "3", "Launch Client UI", "Start the Streamlit chat interface 🛠️"),
    ("🔄", "4", "Launch Both", "Run server and client together 🎯"),
    ("📁", "5", "View Generated Files", "List all MCP server files in src/ 📂"),
    ("⚙️", "6", "Configuration", "Check and configure environment settings 🔧"),
    ("❓", "7", "Help", "Show usage instructions and tips 📖"),
    ("🚪", "8", "Exit", "Quit AutoForge-MCP 👋"),
]


class AutoForgeMCP:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.src_dir = self.project_root / "src"
        self.mcp_server_process = None
        self.mcp_client_process = None

    def print_banner(self):
        console.print(ASCII_ART, style="bold cyan")
        console.print()

    def print_menu(self):
        table = Table(
            title="[bold yellow]📋 Main Menu[/bold yellow]",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan",
            box=None,
        )
        table.add_column("Icon", style="cyan", justify="center", width=4)
        table.add_column("Option", style="bold white", width=4)
        table.add_column("Action", style="bold green", width=20)
        table.add_column("Description", style="dim")

        for icon, num, action, desc in MENU_ITEMS:
            table.add_row(icon, f"[bold cyan]{num}[/bold cyan]", f"[bold yellow]{action}[/bold yellow]", desc)

        console.print(table)
        console.print()

    def check_env_file(self):
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if not env_file.exists() and env_example.exists():
            console.print("📝 [yellow]Creating .env file from example...[/yellow]")
            env_content = env_example.read_text()
            env_file.write_text(env_content)
            console.print("✅ [green].env file created! Please edit it and add your API keys.[/green]")
            return False
        elif not env_file.exists():
            console.print("❌ [red].env file not found![/red]")
            return False

        from dotenv import load_dotenv
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            console.print("⚠️  [yellow]Warning: OPENAI_API_KEY not set in .env[/yellow]")
            return False

        return True

    def create_mcp_server(self):
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🎲 MCP Server Creator[/bold cyan]",
            subtitle="[yellow]Powered by AI ✨[/yellow]",
            border_style="green"
        ))

        prompt_text = Prompt.ask(
            "[bold green]📝 Describe the MCP server you want to create[/bold green]",
            default="Create an MCP server that simulates dice rolls"
        )

        console.print()
        console.print(f"🤔 [cyan]Generating MCP server:[/cyan] {prompt_text}")
        console.print()

        create_script = self.src_dir / "create_mcp.py"

        with open(create_script, "r") as f:
            content = f.read()

        content = content.replace(
            'human_message = "Create an MCP server that will simulate dice rolls"',
            f'human_message = "{prompt_text}"'
        )

        temp_script = self.project_root / "temp_create_mcp.py"
        with open(temp_script, "w") as f:
            f.write(content)

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                task = progress.add_task("[cyan]Generating MCP server...", total=100)

                for i in range(100):
                    time.sleep(0.03)
                    progress.update(task, advance=1)

            console.print()
            result = subprocess.run(
                [sys.executable, str(temp_script)],
                capture_output=True,
                text=True,
                cwd=str(self.project_root)
            )

            if result.returncode == 0:
                console.print("✅ [bold green]MCP server created successfully![/bold green]")
                if result.stdout:
                    console.print(result.stdout)
            else:
                console.print(f"❌ [bold red]Error creating MCP server:[/bold red]")
                console.print(result.stderr, style="red")

        except Exception as e:
            console.print(f"❌ [bold red]Error:[/bold red] {e}")
        finally:
            if temp_script.exists():
                temp_script.unlink()

        console.print()
        Prompt.ask("[bold blue]Press Enter to continue...[/bold blue]")

    def get_generated_files(self):
        files = []
        for f in self.src_dir.glob("*_mcp.py"):
            if f.name not in ["create_mcp.py", "mcp_client.py"]:
                files.append(f)
        return files

    def launch_server_terminal(self):
        files = self.get_generated_files()

        if not files:
            console.print("❌ [red]No MCP server files found![/red]")
            console.print("💡 [yellow]Tip: Create an MCP server first (Option 1)[/yellow]")
            return

        console.print()
        console.print(Panel.fit(
            "[bold cyan]🚀 Launch MCP Server[/bold cyan]",
            border_style="green"
        ))

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Number", style="cyan", justify="center")
        table.add_column("File", style="green")

        for i, f in enumerate(files, 1):
            table.add_row(str(i), f.name)

        console.print(table)

        choice = Prompt.ask(
            "[bold green]Select a server file[/bold green]",
            choices=[str(i) for i in range(1, len(files) + 1)],
            default="1"
        )

        selected_file = files[int(choice) - 1]

        console.print()
        console.print(f"🖥️  [cyan]Starting MCP server:[/cyan] {selected_file.name}")

        if sys.platform == "win32":
            cmd = f'start cmd /k "cd /d {self.project_root} && python {selected_file}"'
            subprocess.Popen(cmd, shell=True)
        else:
            console.print("🌐 Server running at: http://localhost:8000")
            console.print("📡 SSE endpoint: http://localhost:8000/sse")
            console.print()
            console.print("[yellow]Starting server...[/yellow]")
            self.mcp_server_process = subprocess.Popen(
                [sys.executable, str(selected_file)],
                cwd=str(self.project_root)
            )

        console.print("✅ [bold green]Server terminal launched![/bold green]")

    def launch_client_terminal(self):
        client_file = self.src_dir / "mcp_client.py"

        if not client_file.exists():
            console.print("❌ [red]mcp_client.py not found![/red]")
            return

        console.print()
        console.print(Panel.fit(
            "[bold cyan]💬 Launch Client UI[/bold cyan]",
            subtitle="[yellow]Streamlit Chat Interface 🛠️[/yellow]",
            border_style="blue"
        ))

        console.print(f"📱 [cyan]Starting Streamlit UI...[/cyan]")

        if sys.platform == "win32":
            cmd = f'start cmd /k "cd /d {self.project_root} && streamlit run {client_file}"'
            subprocess.Popen(cmd, shell=True)
        else:
            console.print("🌐 Opening Streamlit UI in browser...")
            self.mcp_client_process = subprocess.Popen(
                ["streamlit", "run", str(client_file)],
                cwd=str(self.project_root)
            )

        console.print("✅ [bold green]Client UI launched![/bold green]")
        console.print("🌐 [cyan]Open http://localhost:8501 in your browser[/cyan]")

    def launch_both(self):
        console.print()
        console.print(Panel.fit(
            "[bold yellow]🎯 Launching Both Server & Client[/bold yellow]",
            border_style="yellow"
        ))

        console.print("🚀 [cyan]Starting MCP server...[/cyan]")
        self.launch_server_terminal()
        time.sleep(1)

        console.print()
        console.print("💬 [cyan]Starting Client UI...[/cyan]")
        self.launch_client_terminal()

        console.print()
        console.print(Panel.fit(
            "[bold green]🎉 Everything is running![/bold green]",
            border_style="green"
        ))
        console.print("📡 [cyan]Server:[/cyan] http://localhost:8000")
        console.print("🌐 [cyan]Client:[/cyan] http://localhost:8501")

    def view_generated_files(self):
        files = self.get_generated_files()

        console.print()
        console.print(Panel.fit(
            "[bold cyan]📁 Generated MCP Server Files[/bold cyan]",
            border_style="cyan"
        ))

        if not files:
            console.print("📭 [yellow]No MCP server files found in src/[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("File", style="green")
        table.add_column("Size", style="cyan", justify="right")
        table.add_column("Modified", style="yellow")

        for f in files:
            stat = f.stat()
            size = stat.st_size
            modified = time.strftime("%Y-%m-%d %H:%M", time.localtime(stat.st_mtime))

            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"

            table.add_row(f"📄 {f.name}", size_str, modified)

        console.print(table)

    def show_config(self):
        console.print()
        console.print(Panel.fit(
            "[bold cyan]⚙️ Configuration[/bold cyan]",
            border_style="yellow"
        ))

        from dotenv import load_dotenv
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY", "")
        mcp_url = os.getenv("MCP_URL", "http://localhost:8000")

        table = Table(show_header=False, border_style=None)
        table.add_column("Key", style="bold cyan")
        table.add_column("Value", style="green")

        masked_key = "***" + openai_key[-10:] if openai_key and len(openai_key) > 10 else "❌ NOT SET"
        table.add_row("OPENAI_API_KEY", masked_key)
        table.add_row("MCP_URL", mcp_url)
        table.add_row("Python", sys.executable)
        table.add_row("Platform", sys.platform)

        console.print(table)

        console.print()

        if not openai_key:
            console.print("⚠️  [yellow]Please set OPENAI_API_KEY in .env file![/yellow]")
            console.print("📝 [cyan]Edit the .env file in the project root[/cyan]")

    def show_help(self):
        console.print()
        console.print(Panel.fit(
            "[bold cyan]❓ Help & Usage[/bold cyan]",
            border_style="blue"
        ))

        help_text = """
[bold yellow]🎯 Quick Start:[/bold yellow]

1️⃣  [green]Create MCP Server[/green] - Use AI to generate a new MCP server
   • Describe your desired functionality
   • AI will generate the Python code
   • Server is saved to src/ directory

2️⃣  [green]Launch Server Terminal[/green] - Run your MCP server
   • Select from generated servers
   • Server runs on http://localhost:8000

3️⃣  [green]Launch Client UI[/green] - Open the Streamlit chat interface
   • Chat with AI powered by MCP tools
   • Access at http://localhost:8501

4️⃣  [green]Launch Both[/green] - Run server and client together

[bold yellow]📋 Requirements:[/bold yellow]
• Python 3.12+
• OpenAI API key in .env
• Required packages: mcp, streamlit, langchain-openai

[bold yellow]🐛 Troubleshooting:[/bold yellow]
• Server not starting? Check if port 8000 is available
• Client can't connect? Ensure server is running first
• API errors? Verify your OPENAI_API_KEY is valid
        """
        console.print(help_text, style="cyan")

    def run(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            self.print_banner()

            if not self.check_env_file():
                console.print()

            self.print_menu()

            choice = Prompt.ask(
                "[bold green]Select an option[/bold green]",
                choices=[item[1] for item in MENU_ITEMS],
                default="8"
            )

            if choice == "1":
                self.create_mcp_server()
            elif choice == "2":
                self.launch_server_terminal()
            elif choice == "3":
                self.launch_client_terminal()
            elif choice == "4":
                self.launch_both()
            elif choice == "5":
                self.view_generated_files()
                Prompt.ask("[bold blue]Press Enter to continue...[/bold blue]")
            elif choice == "6":
                self.show_config()
                Prompt.ask("[bold blue]Press Enter to continue...[/bold blue]")
            elif choice == "7":
                self.show_help()
                Prompt.ask("[bold blue]Press Enter to continue...[/bold blue]")
            elif choice == "8":
                console.print()
                console.print(Panel.fit(
                    "[bold magenta]👋 Thanks for using AutoForge-MCP![/bold magenta]\n"
                    "[cyan]See you next time! 🚀[/cyan]",
                    border_style="cyan"
                ))
                break


def main():
    try:
        app = AutoForgeMCP()
        app.run()
    except KeyboardInterrupt:
        console.print()
        console.print("👋 [yellow]Interrupted by user. Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"❌ [bold red]Fatal Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
