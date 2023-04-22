from dataclasses import dataclass

from temporalio import workflow

from meta_scheduler.utils.logger import get_logger

logger = get_logger("recv")

NAME = "recv"


@dataclass(slots=True)
class Input:
    ...


@dataclass(slots=True)
class Output:
    ...


@workflow.defn
class Step:
    @workflow.run
    async def run(self, inp: Input) -> Output:
        ...


def get_and_check():
    return [Step], []
