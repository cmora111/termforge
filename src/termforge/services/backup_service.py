import tarfile
from datetime import datetime
from pathlib import Path

from ..constants import PROJECT_BACKUP_DIR


def create_project_snapshot(project_root: Path) -> Path:
    PROJECT_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = PROJECT_BACKUP_DIR / f"termforge-project-{timestamp}.tar.gz"

    exclude_names = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
    }

    exclude_suffixes = (".pyc", ".pyo")

    def should_exclude(path: Path) -> bool:
        parts = set(path.parts)

        if parts.intersection(exclude_names):
            return True

        if path.name.endswith(exclude_suffixes):
            return True

        if path.name.endswith(".egg-info"):
            return True

        return False

    with tarfile.open(target, "w:gz") as tar:
        for path in project_root.rglob("*"):
            rel = path.relative_to(project_root)

            if should_exclude(rel):
                continue

            tar.add(path, arcname=rel, recursive=False)

    return target
