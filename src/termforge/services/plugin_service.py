from pathlib import Path


def discover_plugins(plugin_dir: Path) -> list[str]:
    plugin_dir.mkdir(parents=True, exist_ok=True)
    return sorted(p.stem for p in plugin_dir.glob("*.py") if p.name != "__init__.py")


def plugin_path(plugin_dir: Path, name: str) -> Path:
    return plugin_dir / f"{name}.py"
