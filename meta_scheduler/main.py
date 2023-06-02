import asyncio
import sys

from temporalio.client import Client
from temporalio.worker import UnsandboxedWorkflowRunner
from temporalio.worker import Worker

from meta_scheduler import settings
from meta_scheduler.steps import exec
from meta_scheduler.steps import parse
from meta_scheduler.steps import persiste_to_db
from meta_scheduler.steps import recv
from meta_scheduler.utils.logger import get_logger

logger = get_logger("main")

interrupt_event = asyncio.Event()


async def main():
    workflows = []
    activities = []

    steps = [recv, exec, parse, persiste_to_db]

    for step_name in settings.scheduler.steps:
        logger.info("Add step: %s", step_name)
        for step_module in steps:
            if step_module.NAME == step_name:
                workflow, activity = step_module.get()
                workflows.append(workflow)
                activities.extend(activity)
                break
        else:  # no-break
            logger.error("Unknown step: %s", step_name)
            sys.exit(1)

    client = await Client.connect(
        f"{settings.temporal.HOST}:{settings.temporal.PORT}",
        namespace=settings.temporal.NAMESPACE,
    )

    from datetime import date

    from meta_scheduler.models.mql import (
        CostFunction,
        Model,
        Optimization,
        Period,
        Strategy,
    )

    with open("strategy_examples/macd.ex5", "rb") as f:
        ex5 = f.read()
    with open("strategy_examples/macd.set") as f:
        set_file = f.read()

    try:
        if True:
            await client.start_workflow(
                recv.Workflow.run,
                recv.Input(
                    "test",
                    Strategy(
                        ex5=ex5,
                        name="test",
                        period=Period.M15,
                        model=Model.OHLC,
                        optimization=(
                            Optimization.DISABLED,
                            Optimization.FAST_GENETIC,
                        )[1],
                        cost_function=CostFunction.BALANCE_MAX,
                        from_date=str(date(2020, 1, 2)),
                        to_date=str(date(2021, 1, 1)),
                        set_file=set_file,
                    ),
                    ["EURUSD"],
                ),
                id="sag",  # str(uuid4()),
                task_queue=settings.temporal.task_queue,
            )
    except:
        pass

    logger.info(
        "Register worker on task queue: %s namespace: %s",
        settings.temporal.TASK_QUEUE,
        settings.temporal.NAMESPACE,
    )
    # Run a worker for the workflow
    async with Worker(
        client,
        task_queue=settings.temporal.TASK_QUEUE,
        workflows=workflows,
        activities=activities,
        workflow_runner=UnsandboxedWorkflowRunner(),
    ):
        await interrupt_event.wait()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
