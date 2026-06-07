import re


def clean_captured_output(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.replace("\x00", "")
    text = text.replace("\\N", "")

    lines = []
    for line in text.splitlines():
        line = line.rstrip()
        if line:
            lines.append(line)

    return "\n".join(lines)

def extract_termforge_capture(output: str) -> str:
    if not output:
        return ""

    start = "__TF_CAPTURE_START__"
    end = "__TF_CAPTURE_END__"

    if start in output and end in output:
        before_end = output.rsplit(end, 1)[0]
        chunk = before_end.rsplit(start, 1)[-1]
    else:
        chunk = output

    lines = []

    for line in chunk.splitlines():
        line = line.strip()

        if not line:
            continue

        # Ignore echoed commands
        if start in line or end in line:
            continue

        # Ignore shell prompts like:
        # mora@spectrix:~(12:26:25)$
        if re.search(r"^[^@\s]+@[^:\s]+:.*\([0-9:]+\)\$", line):
            continue

        # Ignore job-control messages
        if line.startswith("["):
            continue

        if line.startswith("(wd "):
            continue

        # Ignore bash errors/prompts
        if "syntax error near unexpected token" in line:
            continue

        lines.append(line)

    return lines[-1] if lines else ""

