
BUTTON_STYLES = {
    "primary": {
        "bg": "#1f6aa5",
        "fg": "white",
        "activebackground": "#2d82c7",
        "activeforeground": "white",
    },
    "success": {
        "bg": "#2e8b57",
        "fg": "white",
        "activebackground": "#3ca06a",
        "activeforeground": "white",
    },
    "warning": {
        "bg": "#b8860b",
        "fg": "black",
        "activebackground": "#d4a017",
        "activeforeground": "black",
    },
    "danger": {
        "bg": "#b22222",
        "fg": "white",
        "activebackground": "#d63c3c",
        "activeforeground": "white",
    },
    "neutral": {
        "bg": "#444444",
        "fg": "white",
        "activebackground": "#666666",
        "activeforeground": "white",
    },
    "purple": {
        "bg": "#5b4b8a",
        "fg": "white",
        "activebackground": "#7460aa",
        "activeforeground": "white",
    },
}


def button_style(name: str = "neutral") -> dict:
    return BUTTON_STYLES.get(name, BUTTON_STYLES["neutral"])
