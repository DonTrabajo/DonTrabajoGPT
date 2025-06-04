import time
from rich.live import Live
from rich.console import Console
from rich.text import Text

console = Console()

SWOOSH = [
    "⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⣿⣿⣿⡿⠋⠉⢹⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⣿⣿⠋   ⠀⠹⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⣿⠋      ⠘⣿⣿⣿⣿⣿",
    "⣿⣿⣿⣿⠏         ⠷⣿⣿⣿⣿",
    "⣿⣿⣿⡟            ⠛⣿⣿⣿",
    "⣿⣿⣿               ⠙⣿⣿",
    "⣿⣿⣿                ⠛⣿",
    "⣿⣿⣿                 ⠉ ",
]

def swoosh_transition(delay=0.05):
    """Scrolls the SWOOSH art upward in a live panel."""
    height = len(SWOOSH)
    with Live(console=console, refresh_per_second=10) as live:
        for i in range(height):
            # Slice the array so it appears moving upward
            frame = "\n".join(SWOOSH[i:]) 
            live.update(Text(frame, style="green"))
            time.sleep(delay)
    console.clear()
