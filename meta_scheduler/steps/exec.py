from dataclasses import dataclass

from temporalio import workflow

from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)

logger = get_logger(NAME)


@dataclass(slots=True)
class Input:
    strategy: bytes
    symbol: str


@dataclass(slots=True)
class Output:
    ...


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: Input) -> Output:
        logger.info("%s", inp)


def get() -> tuple:
    return Workflow, []
