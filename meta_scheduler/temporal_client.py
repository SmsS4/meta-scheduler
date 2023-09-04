from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from temporalio.client import Client
from temporalio.contrib.opentelemetry import TracingInterceptor

from meta_scheduler import settings


async def get():
    provider = TracerProvider(
        resource=Resource.create({"service.name": "meta-scheduler"})
    )
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=settings.temporal.OTEL_HOST,
                insecure=True,
            )
        ),
    )
    trace.set_tracer_provider(provider)

    client = await Client.connect(
        f"{settings.temporal.HOST}:{settings.temporal.PORT}",
        namespace=settings.temporal.NAMESPACE,
        interceptors=[TracingInterceptor()],
    )
    return client
