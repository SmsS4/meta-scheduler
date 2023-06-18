import asyncio
import sys

from prometheus_client import start_http_server
from temporalio.client import Client
from temporalio.runtime import OpenTelemetryConfig
from temporalio.worker import UnsandboxedWorkflowRunner
from temporalio.worker import Worker

from meta_scheduler import metrics
from meta_scheduler import settings
from meta_scheduler import temporal_client
from meta_scheduler.steps import exec
from meta_scheduler.steps import parse
from meta_scheduler.steps import persiste_to_db
from meta_scheduler.steps import recv
from meta_scheduler.utils.logger import get_logger

logger = get_logger("main")

interrupt_event = asyncio.Event()


async def main():
    start_http_server(7070)
    workflows = []
    activities = []

    steps = [recv, exec, parse, persiste_to_db]

    for step_name in settings.scheduler.steps:
        logger.info("Add step: {}", step_name)
        for step_module in steps:
            if step_module.NAME == step_name:
                workflow, activity = step_module.get()
                workflows.append(workflow)
                activities.extend(activity)
                break
        else:  # no-break
            logger.error("Unknown step: {}", step_name)
            sys.exit(1)
    client = await temporal_client.get()
    logger.info(
        "Register worker on task queue: {} namespace: {}",
        settings.temporal.TASK_QUEUE,
        settings.temporal.NAMESPACE,
    )
    metrics.worker.info(
        {
            "task_queue": settings.temporal.TASK_QUEUE,
            "namespace": settings.temporal.NAMESPACE,
        }
    )

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
