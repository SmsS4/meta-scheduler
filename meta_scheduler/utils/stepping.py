import uuid


def get_name(name: str) -> str:
    return name[name.rfind(".") + 1 :]


def get_id() -> str:
    return str(uuid.uuid4())
