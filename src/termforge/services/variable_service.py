def get_shared_variables(cfg) -> dict:
    variables = getattr(cfg, "SharedVariables", None)

    if not isinstance(variables, dict):
        variables = {}
        setattr(cfg, "SharedVariables", variables)

    return variables


def set_shared_variable(cfg, name: str, value: str) -> dict:
    name = str(name).strip()

    if not name:
        raise ValueError("Shared variable name is required.")

    variables = get_shared_variables(cfg)
    variables[name] = str(value)
    setattr(cfg, "SharedVariables", variables)

    return variables


def delete_shared_variable(cfg, name: str) -> dict:
    variables = get_shared_variables(cfg)
    variables.pop(str(name).strip(), None)
    setattr(cfg, "SharedVariables", variables)

    return variables
