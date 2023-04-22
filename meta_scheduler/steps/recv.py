from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler.steps import step
from meta_scheduler.utils.logger import get_logger


@workflow.defn
class Workflow(step.Workflow):
    NAME = step.Workflow.get_name(__name__)
    logger = get_logger(NAME)

    @dataclass(slots=True)
    class Input:
        ...

    @dataclass(slots=True)
    class Output:
        ...

    @activity.defn
    async def test():
        ...

    @workflow.run
    async def run(self, inp: Input) -> Output:
        ...
