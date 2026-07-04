from __future__ import annotations

import json

from config import PERMISSIONS_FILE

ROLES = {
    "hr_manager": "HR Manager",
    "accountant": "Accountant",
    "engineer": "Engineer",
    "legal_counsel": "Legal Counsel",
    "admin": "Admin",
}


def load_permissions() -> dict[str, list[str]]:
    with open(PERMISSIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_allowed_departments(role: str) -> list[str]:
    permissions = load_permissions()
    return permissions.get(role, [])


def get_all_departments() -> list[str]:
    return ["hr", "finance", "engineering", "legal"]
