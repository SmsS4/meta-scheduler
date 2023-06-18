import pydantic


class OptResult(pydantic.BaseModel):
    """
    Result of optimization
    """

    create_time: str
    version: str
    sharpe_ratio: list[float]
    trades: list[int]
    result: list[float | int]
    profit: list[float]
    profit_factor: list[float]
    recovery_factor: list[float]
    expected_payoff: list[float]
    drawdown: list[float]
    custom: list[float]
    inptrailingstop: list[float]
