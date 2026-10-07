"""Nạp config/bottle_500_params.toml thành dict phẳng 'section.key' -> value, kèm class nguồn."""
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT = ROOT / "config" / "bottle_500_params.toml"

CLASS_LABEL = {
    "image": "Thông số từ ảnh",
    "assumption": "Giả định dựng concept",
    "factory": "Cần nhà máy xác nhận",
}


class Params:
    def __init__(self, path=DEFAULT):
        with open(path, "rb") as f:
            raw = tomllib.load(f)
        self.entries = {}
        for sec, items in raw.items():
            for key, spec in items.items():
                self.entries[f"{sec}.{key}"] = spec

    def __getitem__(self, name):
        return self.entries[name]["value"]

    def cls(self, name):
        return self.entries[name]["class"]

    def rows(self):
        for name, spec in self.entries.items():
            yield name, spec["value"], spec["class"], spec["note"]
