from dataclasses import dataclass
from datetime import timedelta

import xmltodict
from temporalio import activity
from temporalio import workflow
from temporalio.common import RetryPolicy

from meta_scheduler import models
from meta_scheduler.models import file
from meta_scheduler.models import opt
from meta_scheduler.utils import db_session
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, xml: opt.OptResult, name: str):
        with db_session.DBContextManager() as db:
            db.add(
                models.db.OptResult(
                    name=name,
                    create_time=xml.create_time,
                    version=xml.version,
                    sharpe_ratio=xml.sharpe_ratio,
                    trades=xml.trades,
                    result=xml.result,
                    profit=xml.profit,
                    profit_factor=xml.profit_factor,
                    recovery_factor=xml.recovery_factor,
                    expected_payoff=xml.expected_payoff,
                    drawdown=xml.drawdown,
                    custom=xml.custom,
                    inptrailingstop=xml.inptrailingstop,
                )
            )
            db.commit()


def get() -> tuple:
    return Workflow, []
