from rich import print

print("[red]Red[/]")
print("[orange1]range[/]")
print("[gold1]Gold[/]")
print("[#FF6B35]Custom Orange[/]")
print("[rgb(255,100,0)]RGB Orange[/]")


color_map: dict[str, int] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",

    # Bright ANSI
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_purple": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",

    # Extended 256-color palette
    "orange": "\033[38;5;208m",
    "brown": "\033[38;5;94m",
    "maroon": "\033[38;5;52m",
    "gold": "\033[38;5;220m",
    "darkred": "\033[38;5;88m",
    "crimson": "\033[38;5;161m",
    "violet": "\033[38;5;135m",
    "gray": "\033[38;5;245m",
    "pink": "\033[38;5;213m",
    "teal": "\033[38;5;36m",
    "lime": "\033[38;5;154m",
    "indigo": "\033[38;5;54m",
    "lavender": "\033[38;5;183m",
    "salmon": "\033[38;5;209m",
    "coral": "\033[38;5;203m",
    "mint": "\033[38;5;121m",
    'rainbow': "\033[38;5;213m",
    "magenta":       "\033[38;5;201m",
    "dark_magenta":  "\033[38;5;90m",
    "hot_pink":      "\033[38;5;205m",
    "fuchsia":       "\033[38;5;13m",
    "orchid":        "\033[38;5;170m",
    "plum":          "\033[38;5;176m",
}
