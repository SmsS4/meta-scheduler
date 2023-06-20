from dataclasses import dataclass

from temporalio import activity
from temporalio import workflow

from meta_scheduler import metrics
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
    strategy: mql.Strategy
    symbols: list[str]


@dataclass(slots=True)
class Output:
    ...


@workflow.defn(name=NAME)
class Workflow:
    @workflow.run
    async def run(self, inp: Input):
        for i, symbol in enumerate(inp.symbols):
            metrics.recived_strategy.labels(symbol).inc()
            metrics.progress.set(i / len(inp.symbols))
            base = {
                "name": inp.strategy.name,
                "symbol": symbol,
                "period": inp.strategy.period,
                "from": inp.strategy.from_date,
                "to": inp.strategy.to_date,
            }
            base["state"] = "exec"
            metrics.current_task.info(base)
            inp.strategy.symbol = symbol
            files: list[file.File] = await workflow.execute_child_workflow(
                exec.Workflow.run,
                inp.strategy,
                id=stepping.get_id("exec"),
            )
            xmls = list(filter(lambda x: x.type == file.FileType.XML, files))
            if len(xmls) >= 2:
                raise ValueError("length of xmls is more than one")
            if len(xmls) == 1:
                base["state"] = "parse"
                metrics.current_task.info(base)
                xml = await workflow.execute_child_workflow(
                    parse.Workflow.run,
                    xmls[0],
                    id=stepping.get_id("parse"),
                )
                base["state"] = "persiste"
                metrics.current_task.info(base)
                await workflow.execute_child_workflow(
                    persiste_to_db.Workflow.run,
                    args=[xml, f"{inp.strategy.name} ({symbol})"],
                    id=stepping.get_id("persiste"),
                )

            base["state"] = "done"
            metrics.current_task.info(base)

        metrics.progress.set(1)
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
