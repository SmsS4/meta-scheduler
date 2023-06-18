import base64
from datetime import date

import requests

from backend import schemas
from meta_scheduler.models.mql import CostFunction
from meta_scheduler.models.mql import Model
from meta_scheduler.models.mql import Optimization
from meta_scheduler.models.mql import Period

with open("strategy_examples/macd.ex5", "rb") as f:
    ex5 = f.read()
with open("strategy_examples/macd.set") as f:
    set_file = f.read()

strategy = schemas.Strategy(
    ex5=base64.b64encode(ex5).decode(),
    name="test",
    period=Period.M15,
    model=Model.OHLC,
    optimization=Optimization.FAST_GENETIC,
    cost_function=CostFunction.BALANCE_MAX,
    from_date=str(date(2020, 1, 2)),
    to_date=str(date(2021, 1, 1)),
    set_file=set_file,
    symbols=["EURUSD"],
)

# response = requests.post(
#     "http://localhost:8000",
#     json=strategy.dict(),
# )
response = requests.get("http://localhost:8000/results")
# requests.delete(
#     "http://localhost:8000/results", params={"uid": response.json()[0]["id"]}
# )
print(response.text)
