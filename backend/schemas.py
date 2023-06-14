from pydantic import BaseModel

from meta_scheduler.models import mql


class Strategy(BaseModel):
    symbols: list[str]
    ex5: str
    name: str
    period: str
    model: int
    optimization: int
    cost_function: int
    from_date: str
    to_date: str
    set_file: str
    execution_mode: int = mql.ExecutionMode.NORMAL
    leverage: str = "1:100"
    deposit: int = 10000
