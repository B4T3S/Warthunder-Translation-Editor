# This is just a utility class to provide color output in the console

_colors_enabled = True

def disable_colors():
    _colors_enabled = False

class Colors:
    BOLDON = '\033[1m'
    BOLDOFF = '\033[22m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    END = '\033[0m'


def cls():
    if _colors_enabled:
        print("\033c", end='')


def pretty_print(message: str, color: str = Colors.BLUE, highlight: str = Colors.CYAN):
    # If colors are disabled, just print message.
    if _colors_enabled is False:
        print(message)
        return
    
    # If colors are enabled, replace < and > and wrap everything in a nice color.
    message = message.replace('<', highlight)
    message = message.replace('>', color)
    print(f"{color}{message}{Colors.END}")

def title(message: str):
    print('-'*30)
    pretty_print(message)
    print('-'*30)