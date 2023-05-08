from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler.models import mql
from meta_scheduler.steps import exec
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)

logger = get_logger(NAME)


@dataclass(slots=True)
class Input:
    strategy: mql.Strategy
    symbols: list[str]


@dataclass(slots=True)
class Output:
    ...


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: Input) -> Output:
        inp.strategy.symbol = inp.symbols[0]
        return await workflow.execute_child_workflow(
            exec.Workflow.run,
            inp.strategy,
            id=stepping.get_id(),
        )


def get() -> tuple:
    return Workflow, []
