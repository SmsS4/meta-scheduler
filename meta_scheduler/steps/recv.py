from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler.steps import exec
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)

logger = get_logger(NAME)


@dataclass(slots=True)
class Input:
    name: str
    strategy: bytes
    symbols: list[str]


@dataclass(slots=True)
class Output:
    ...


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: Input) -> Output:
        logger.info("hey")
        return await workflow.execute_child_workflow(
            exec.Workflow.run,
            exec.Input(
                strategy=inp.strategy,
                symbol=inp.symbols[0],
            ),
            id=stepping.get_id(),
        )


def get() -> tuple:
    return Workflow, []
