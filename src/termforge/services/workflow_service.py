from datetime import datetime


def start_workflow_state(name: str, total: int, mode: str = "sequential") -> None:
    current_workflow_state = {
        "name": name,
        "mode": mode,
        "total": total,
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": "",
        "status": "running",
        "steps": {},
        "output_vars": {},
    }

def update_workflow_step_state(
    state: dict,
    step_id: str,
    status: str,
    message: str = "",
    output: str = "",
) -> None:

    if not current_workflow_state:
        return

    steps = current_workflow_state.setdefault("steps", {})

    row = steps.setdefault(
        step_id,
        {
            "id": step_id,
            "status": "",
            "started_at": "",
            "finished_at": "",
            "message": "",
            "output": "",
        },
    )

    row["status"] = status
    row["message"] = message
    if output:
        row["output"] = output

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if status == "running" and not row.get("started_at"):
        row["started_at"] = now

    if status in ("success", "failed", "skipped"):
        row["finished_at"] = now


def finish_workflow_state(status: str = "finished") -> None:
    if not current_workflow_state:
        return

    current_workflow_state["status"] = status
    current_workflow_state["finished_at"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    workflow_history.insert(0, dict(current_workflow_state))
    del workflow_history[50:]

