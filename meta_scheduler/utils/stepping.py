import uuid


def get_name(name: str) -> str:
    return name[name.rfind(".") + 1 :]


def get_id(prefix: str = "") -> str:
    return f"{prefix} - {str(uuid.uuid4())}"
