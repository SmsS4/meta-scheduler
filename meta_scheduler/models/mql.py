from dataclasses import dataclass


class Period:
    M1 = "M1"
    M15 = "M15"
    H1 = "H1"


class Model:
    EVERY_TICK = 0
    OHLC = 1
    OPEN_PRICE_ONLY = 2
    MATH_CALCULATION = 3
    EVERY_TICK_BASED_ON_REAL_TICK = 4


class ExecutionMode:
    NORMAL = 0
    RANDOM = -1
    ONE_MILLISECOND = 1


class Optimization:
    DISABLED = 0
    SLOW = 1
    FAST_GENETIC = 2
    ALL_SYMBOL_IN_MARKET_WATCH = 3
    OUR_OPT = 4


class CostFunction:
    """
    OptimizationCriterion — optimization criterion:
        (0 — the maximum balance value,
         1 — the maximum value of product of the balance and profitability,
         2 — the product of the balance and expected payoff,
         3 — the maximum value of the expression (100% - Drawdown)*Balance,
         4 — the product of the balance and the recovery factor,
         5 — the product of the balance and the Sharpe Ratio,
         6 — a custom optimization criterion received from the OnTester() function in the Expert Advisor
    """

    BALANCE_MAX = 0
    CUSTOM_MAX = 6


@dataclass
class Strategy:
    """
    Attributes:
        name: name of strategy
        period: timeframe
        model: modeling (ohlc and ...)
        optimization:  optimization (genetic and ...)
        cost_function:
        cost_function_name: name of cost function (just for storing)
        execution_mode: delays defaults to NORMAL (no delay)
        leverage: N:M. defaults to 1:100
        deposit: deposit value
    """

    def get_name(self):
        return ".".join(
            [
                self.symbol,
                str(self.from_date),
                str(self.to_date),
                str(self.period),
                self.name,
            ]
        )

    ex5: bytes
    name: str
    period: str
    model: int
    optimization: int
    cost_function: int
    from_date: str  # 2020.1.2 format
    to_date: str
    set_file: str
    symbol: str | None = None
    execution_mode: int = ExecutionMode.NORMAL
    leverage: str = "1:100"
    deposit: int = 10000
