
ROLE_PERMISSIONS = {
    "employee": {"public"},
    "hr": {"public", "hr"},
    "it": {"public", "it"},
    "admin": {"public", "hr", "it"},
}


def get_allowed_departments(role: str) -> list[str]:
    role = role.lower().strip()

    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Unknown role: {role}")

    return sorted(ROLE_PERMISSIONS[role])


def can_access(role: str, department: str) -> bool:
    allowed = get_allowed_departments(role)
    return department in allowed


if __name__ == "__main__":
    test_cases = [
        ("employee", "public"),
        ("employee", "hr"),
        ("hr", "hr"),
        ("it", "hr"),
        ("admin", "it"),
    ]

    for role, department in test_cases:
        result = can_access(role, department)
        print(f"{role} -> {department}: {result}")
