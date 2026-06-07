import re


def resolve_dict_variables(text: str, variables: dict, pattern: str) -> str:
    if not isinstance(text, str):
        return text

    if not isinstance(variables, dict):
        variables = {}

    def replace_var(match):
        key = match.group(1)
        return str(variables.get(key, match.group(0)))

    return re.sub(pattern, replace_var, text)


def resolve_shared_variables(text: str, variables: dict) -> str:
    return resolve_dict_variables(
        text,
        variables,
        r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}",
    )


def resolve_workflow_variables(text: str, variables: dict) -> str:
    return resolve_dict_variables(
        text,
        variables,
        r"\{\{([A-Za-z_][A-Za-z0-9_]*)\}\}",
    )
