import os
import sys
import time
import re

# Platform-specific imports for raw input
if os.name == 'nt':
    import msvcrt
else:
    import termios, tty, select

_DEBUG_MODE = False

class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Foreground Palette
    RED = "\033[38;5;196m"       # Health / Damage / Hostile
    GREEN = "\033[38;5;46m"      # Success / Regeneration
    YELLOW = "\033[38;5;220m"    # Gold / Items / Quests
    BLUE = "\033[38;5;33m"       # Mana / Magic
    PURPLE = "\033[38;5;129m"    # Rare / Boss / Arcane
    CYAN = "\033[38;5;51m"       # UI Accents / Locations
    WHITE = "\033[38;5;231m"     # Main Narrative
    GRAY = "\033[38;5;244m"      # System / Secondary Info
    STAMINA = "\033[38;5;208m"   # Stamina / Energy
    PERK = "\033[38;5;201m"      # Perks / Special Abilities

def set_debug_mode(is_debug: bool):
    global _DEBUG_MODE
    _DEBUG_MODE = is_debug

def enable_ansi_support():
    """Enables VT100/ANSI color processing on Windows and UNIX shells."""
    if os.name == 'nt':
        os.system('')

enable_ansi_support()

# --- ENTITY COLOR TOKENIZERS ---
def c_item(text: str) -> str: return f"{Color.YELLOW}{text}{Color.RESET}"
def c_enemy(text: str) -> str: return f"{Color.RED}{Color.BOLD}{text}{Color.RESET}"
def c_location(text: str) -> str: return f"{Color.CYAN}{Color.BOLD}{text}{Color.RESET}"
def c_npc(text: str) -> str: return f"{Color.PURPLE}{Color.BOLD}{text}{Color.RESET}"
def c_quest(text: str) -> str: return f"{Color.YELLOW}{Color.BOLD}{text}{Color.RESET}"
def c_perk(text: str) -> str: return f"{Color.PERK}{Color.BOLD}{text}{Color.RESET}"

# --- UI BAR AND BOX DRAWING ENGINE ---
def render_bar(current: int, max_val: int, length: int = 20, fill_color: str = Color.GREEN, empty_color: str = Color.GRAY) -> str:
    """Renders a progress bar: [████████░░░░] 80/100"""
    current = max(0, min(current, max_val))
    percent = current / max_val if max_val > 0 else 0
    filled_len = int(round(length * percent))
    bar = fill_color + "█" * filled_len + empty_color + "░" * (length - filled_len) + Color.RESET
    return f"[{bar}] {current}/{max_val}"

def draw_box(title: str, lines: list[str], width: int = 60, border_color: str = Color.CYAN) -> None:
    """Renders a formatted ANSI box with a top header."""
    top = f"{border_color}╔═ {Color.BOLD}{Color.WHITE}{title}{Color.RESET}{border_color} " + "═" * (width - len(title) - 4) + f"╗{Color.RESET}"
    bottom = f"{border_color}╚" + "═" * (width - 2) + f"╝{Color.RESET}"
    
    print(top)
    for line in lines:
        # Calculate padding while stripping raw ANSI codes for alignment arithmetic
        printable_len = len(_strip_ansi(line))
        padding = max(0, width - printable_len - 4)
        print(f"{border_color}║{Color.RESET} {line}" + " " * padding + f" {border_color}║{Color.RESET}")
    print(bottom)

def _strip_ansi(text: str) -> str:
    """Internal utility to count raw character length omitting escape codes."""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_movement_input_from_arrows() -> str | None:
    """
    Checks for arrow key presses using raw input.
    Returns 'north', 'south', 'east', 'west' or None if no arrow key is pressed
    or if another key is pressed. This function is non-blocking initially.
    """
    if os.name == 'nt':
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char == b'\xe0': # Extended key prefix for arrow keys
                char = msvcrt.getch()
                if char == b'H': return 'north' # Up arrow
                if char == b'P': return 'south' # Down arrow
                if char == b'K': return 'west'  # Left arrow
                if char == b'M': return 'east'  # Right arrow
            # If it was another key, or not an arrow, consume it and return None
            # This ensures the key press doesn't interfere with subsequent `input()` calls.
            return None
        return None
    else: # Unix-like
        # Raw terminal control only works on a real TTY (not piped input)
        if not sys.stdin.isatty():
            return None
        # Check if input is available without blocking indefinitely
        if select.select([sys.stdin], [], [], 0.001)[0]: # 1ms timeout
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                char = sys.stdin.read(1) # Read first char
                if char == '\x1b': # ANSI escape sequence start
                    # Check for '['
                    if select.select([sys.stdin], [], [], 0.001)[0]:
                        char2 = sys.stdin.read(1)
                        if char2 == '[':
                            # Check for A, B, C, D
                            if select.select([sys.stdin], [], [], 0.001)[0]:
                                char3 = sys.stdin.read(1)
                                if char3 == 'A': return 'north' # Up arrow
                                if char3 == 'B': return 'south' # Down arrow
                                if char3 == 'C': return 'east'  # Right arrow
                                if char3 == 'D': return 'west'  # Left arrow
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # If it was another key, or not an arrow, it's consumed and we return None.
            # The raw mode is restored, so subsequent input() should work.
            return None
        return None


def get_input(prompt: str, valid_options: list[str] = None) -> str:
    if valid_options:
        option_map = {opt.lower(): opt.lower() for opt in valid_options}
        first_letter_map = {}
        for opt in valid_options:
            fl = opt[0].lower()
            first_letter_map.setdefault(fl, []).append(opt.lower())

    while True:
        formatted_prompt = f"\n{Color.BOLD}{Color.YELLOW}❯ {prompt}{Color.RESET} "
        user_input = input(formatted_prompt).strip().lower()

        if not valid_options:
            return user_input

        if user_input in option_map:
            return user_input

        if len(user_input) == 1 and user_input in first_letter_map:
            matches = first_letter_map[user_input]
            if len(matches) == 1:
                return matches[0]
            else:
                print(f"{Color.RED}Ambiguous input '{user_input}'. Options: {', '.join(matches)}{Color.RESET}")
                continue

        print(f"{Color.RED}Invalid command. Valid options: {', '.join(valid_options)}{Color.RESET}")

def display_message(message: str, delay: float = 0.01):
    if _DEBUG_MODE:
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    else:
        in_code = False
        buffer = ""
        for char in message:
            if char == '\033':
                in_code = True
            if in_code:
                buffer += char
                if char == 'm':
                    in_code = False
                    sys.stdout.write(buffer)
                    sys.stdout.flush()
                    buffer = ""
            else:
                sys.stdout.write(char)
                sys.stdout.flush()
                time.sleep(delay)
        sys.stdout.write('\n')

def press_enter_to_continue():
    input(f"\n{Color.GRAY}[Press Enter to continue...]{Color.RESET}")
