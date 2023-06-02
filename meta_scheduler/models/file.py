from dataclasses import dataclass


class FileType:
    XML = 1
    CACHE = 2
    CONFIG = 3
    AGENT_LOG = 4
    TESTER_LOG = 5
    MANAGER_LOG = 6
    TERMINAL_LOG = 7
    BACKTEST_RESULT = 8
    BACKTEST_IMAGES = 9


@dataclass(frozen=True, slots=True)
class File:
    path: str
    data: bytes
    type: int
