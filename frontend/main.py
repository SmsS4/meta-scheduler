import base64

import pandas as pd
import requests
import streamlit as st
from sqlalchemy.orm import Session

from backend import schemas
from meta_scheduler import models
from meta_scheduler.models.mql import CostFunction
from meta_scheduler.models.mql import Model
from meta_scheduler.models.mql import Optimization
from meta_scheduler.models.mql import Period
from meta_scheduler.utils import db_session

HOST = "http://localhost:8000/"

db: Session = db_session.DBSession()


def delete(strategy: str):
    db.query(models.db.OptResult).filter_by(name=strategy).delete()
    db.commit()
    st.success("Deleted")


st.set_page_config(layout="wide")
st.sidebar.title("META SCHEDULER")

opt_results: list[models.db.OptResult] = db.query(models.db.OptResult).all()
options = [result.name for result in opt_results]
strategy_name = st.sidebar.selectbox("Strategy", options)
for result in opt_results:
    if result.name == strategy_name:
        strategy = result
        break
data = pd.DataFrame(
    data={
        "sharpe_ratio": strategy.sharpe_ratio,
        "trades": strategy.trades,
        "result": strategy.result,
        "profit": strategy.profit,
        "profit_factor": strategy.profit_factor,
        "recovery_factor": strategy.recovery_factor,
        "expected_payoff": strategy.expected_payoff,
        "drawdown": strategy.drawdown,
        "custom": strategy.custom,
        "inptrailingstop": strategy.inptrailingstop,
    }
)

st.dataframe(data)
st.download_button(
    "Download csv",
    file_name=f"{strategy.name}.csv",
    data=data.to_csv(),  # to_csv(strategy)
)
st.sidebar.button("Delete", on_click=lambda: delete(strategy.name))


with st.sidebar.form("my_form"):
    # slider_val = st.slider("Form slider")
    # checkbox_val = st.checkbox("Form checkbox")
    name = st.text_input("Name")
    symbols = st.multiselect(
        "Symbols",
        [
            "EURUSD",
            "USDJPY",
            "GBPUSD",
            "USDCHF",
        ],
    )
    period = {
        1: "M1",
        15: "M15",
        60: "H1",
    }[st.select_slider("Period minutes", [1, 15, 60])]
    from_date = st.date_input("From")
    to_date = st.date_input("To")
    ex5 = st.file_uploader(
        "Strategy ex5", help="Upload your compiled strategy (ex5 file)"
    )
    set_file = st.file_uploader("Inputs", help="Upload your set file")
    submitted = st.form_submit_button("Send")
    if submitted:
        strategy = schemas.Strategy(
            ex5=base64.b64encode(ex5.getvalue()).decode(),
            name=name,
            period=period,
            model=Model.OHLC,
            optimization=Optimization.FAST_GENETIC,
            cost_function=CostFunction.BALANCE_MAX,
            from_date=str(from_date),
            to_date=str(to_date),
            set_file=set_file.read(),
            symbols=symbols,
        )
        response = requests.post(HOST, json=strategy.dict())
        if response.status_code == 200:
            st.success("Sent")
        else:
            st.error(f"Failed\n{response.status_code}\n{response.text}")
