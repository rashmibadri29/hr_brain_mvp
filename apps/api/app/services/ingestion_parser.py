import csv
import json
from pathlib import Path


SUPPORTED_EXTENSIONS = [".txt", ".md", ".csv", ".json"]


class UnsupportedFileTypeError(ValueError):
    pass


def parse_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".csv":
        return _parse_csv(path)
    if suffix == ".json":
        return _parse_json(path)
    raise UnsupportedFileTypeError(
        f"Unsupported file type '{suffix}'. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
    )


def _parse_csv(path: Path) -> str:
    rows: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            for index, row in enumerate(reader, start=1):
                fields = [f"{key}: {value}" for key, value in row.items() if value not in (None, "")]
                if fields:
                    rows.append(f"Row {index}\n" + "\n".join(fields))
        else:
            handle.seek(0)
            plain_reader = csv.reader(handle)
            for index, row in enumerate(plain_reader, start=1):
                if row:
                    rows.append(f"Row {index}: " + " | ".join(row))
    return "\n\n".join(rows)


def _parse_json(path: Path) -> str:
    data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    return _flatten_json(data)


def _flatten_json(value: object, prefix: str = "") -> str:
    if isinstance(value, dict):
        lines: list[str] = []
        for key, nested in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            lines.append(_flatten_json(nested, next_prefix))
        return "\n".join(line for line in lines if line)
    if isinstance(value, list):
        lines = []
        for index, nested in enumerate(value, start=1):
            next_prefix = f"{prefix}[{index}]" if prefix else f"item[{index}]"
            lines.append(_flatten_json(nested, next_prefix))
        return "\n".join(line for line in lines if line)
    return f"{prefix}: {value}" if prefix else str(value)
