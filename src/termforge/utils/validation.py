

def validate_workflow_steps(steps):
    errors = []

    if not isinstance(steps, list):
        return ["Workflow must be a list."]

    ids = set()

    for index, step in enumerate(steps, start=1):
        if not isinstance(step, dict):
            errors.append(f"Step {index} must be a dictionary.")
            continue

        step_id = str(step.get("id", "")).strip()

        if not step_id:
            errors.append(f"Step {index} is missing an id.")
            continue

        if step_id in ids:
            errors.append(f"Duplicate step id: {step_id}")

        ids.add(step_id)

    for step in steps:
        if not isinstance(step, dict):
            continue

        step_id = str(step.get("id", "")).strip()
        depends_on = step.get("depends_on", [])

        if isinstance(depends_on, str):
            depends_on = [depends_on]

        for dep in depends_on:
            if dep not in ids:
                errors.append(
                    f"Step {step_id} depends on missing step: {dep}"
                )

    return errors
