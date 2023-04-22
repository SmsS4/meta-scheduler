import asyncio
import sys

from temporalio.client import Client
from temporalio.worker import UnsandboxedWorkflowRunner
from temporalio.worker import Worker

from meta_scheduler import settings
from meta_scheduler.steps import recv
from meta_scheduler.utils.logger import get_logger

logger = get_logger("main")

interrupt_event = asyncio.Event()


async def main():
    # provider = TracerProvider()
    # provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    # trace.set_tracer_provider(provider)
    workflows = []
    activities = []

    steps = [recv]

    for step_name in settings.scheduler.steps:
        logger.info("Add step: %s", step_name)
        for step_module in steps:
            if step_module.Workflow.NAME == step_name:
                workflow, activity = step_module.Workflow.get_and_check()
                workflows.append(workflow)
                activities.extend(activity)
                break
        else:  # no-break
            logger.error("Unknown step: %s", step_name)
            sys.exit(1)

    client = await Client.connect(
        f"{settings.temporal.HOST}:{settings.temporal.PORT}",
        namespace=settings.temporal.NAMESPACE,
        # interceptors=[TracingInterceptor()],
        # runtime=Runtime(
        #     telemetry=TelemetryConfig(
        #         metrics=OpenTelemetryConfig(url=settings.OTEL_METRICS_ENDPOINT)
        #     )
        # ),
    )

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
