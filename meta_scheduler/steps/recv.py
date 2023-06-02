from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler.models import file
from meta_scheduler.models import mql
from meta_scheduler.steps import exec
from meta_scheduler.steps import parse
from meta_scheduler.steps import persiste_to_db
from meta_scheduler.utils import stepping
from meta_scheduler.utils.logger import get_logger

NAME = stepping.get_name(__name__)

logger = get_logger(NAME)


@dataclass(slots=True)
class Input:
    name: str
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
        files: list[file.File] = await workflow.execute_child_workflow(
            exec.Workflow.run,
            inp.strategy,
            id=stepping.get_id("exec"),
        )
        xmls = list(filter(lambda x: x.type == file.FileType.XML, files))
        if len(xmls) >= 2:
            raise ValueError("length of xmls is more than one")
        if len(xmls) == 1:
            xml = await workflow.execute_child_workflow(
                parse.Workflow.run,
                xmls[0],
                id=stepping.get_id("parse"),
            )
            await workflow.execute_child_workflow(
                persiste_to_db.Workflow.run,
                args=[xml, inp.name],
                id=stepping.get_id("persiste"),
            )

        # htms = list(
        #     filter(lambda x: x.type == file.FileType.BACKTEST_RESULT, files)
        # )
        # if len(htms) >= 2:
        #     raise ValueError("length of htms is more than one")
        # if len(htms) == 1:
        #     await workflow.execute_child_workflow(
        #         parse.Workflow.run,
        #         htms[0],
        #         id=stepping.get_id("parse"),
        #     )


def get() -> tuple:
    return Workflow, []
