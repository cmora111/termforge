

def parse_command_entry(entry):
    if isinstance(entry, (list, tuple)):
        if len(entry) == 2:
            return entry[0], entry[1], {}
        if len(entry) >= 3:
            options = entry[2] if isinstance(entry[2], dict) else {}
            return entry[0], entry[1], options
    raise ValueError(f"Invalid command entry format: {entry!r}")

