"""Pytest configuration file to make fixtures available to all tests."""
import pytest
from opentelemetry import metrics as metrics_api
from opentelemetry import trace as trace_api
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
    InMemorySpanExporter,
)

# Dependencies for mcp_server_factory fixture will be imported inside the fixture

# Try to import reset functions from opentelemetry.test, fallback to manual implementation
try:
    from opentelemetry.test.globals_test import (
        reset_metrics_globals,
        reset_trace_globals,
    )
except ImportError:
    # Fallback implementation if opentelemetry.test is not available
    from opentelemetry.util._once import Once

    def reset_trace_globals():
        """Reset trace globals."""
        trace_api._TRACER_PROVIDER = None  # type: ignore
        trace_api._TRACER_PROVIDER_SET_ONCE = Once()  # type: ignore

    def reset_metrics_globals():
        """Reset metrics globals."""
        metrics_api._METER_PROVIDER = None  # type: ignore
        # Reset metrics internal state
        if hasattr(metrics_api, "_internal"):
            metrics_api._internal._METER_PROVIDER_SET_ONCE = Once()  # type: ignore


@pytest.fixture(autouse=True)
def memory_exporter():
    return InMemorySpanExporter()


@pytest.fixture(autouse=True)
def memory_reader():
    return InMemoryMetricReader()


@pytest.fixture(autouse=True)
def meter_provider(memory_reader):
    return MeterProvider(metric_readers=[memory_reader])


@pytest.fixture(autouse=True)
def tracer_provider(memory_exporter):
    tracer_provider = TracerProvider(
        resource=Resource(
            attributes={
                "service.name": "mcp",
            }
        )
    )
    span_processor = SimpleSpanProcessor(memory_exporter)
    tracer_provider.add_span_processor(span_processor)
    return tracer_provider


@pytest.fixture(autouse=True)
def _setup_tracer_and_meter_provider(
    tracer_provider, memory_exporter, meter_provider
):
    # FIXME: ruff failed
    def callable():  # noqa: A001
        memory_exporter.clear()
        reset_trace_globals()
        trace_api.set_tracer_provider(tracer_provider)
        reset_metrics_globals()
        metrics_api.set_meter_provider(meter_provider)

    return callable


@pytest.fixture
def _teardown_tracer_and_meter_provider():
    # FIXME: ruff failed
    def callable():  # noqa: A001
        reset_trace_globals()
        reset_metrics_globals()

    return callable


@pytest.fixture
def find_span(memory_exporter):
    # FIXME: ruff failed
    def callable(  # noqa: A001
        name: str,
        type: trace_api.SpanKind = trace_api.SpanKind.CLIENT,  # noqa: A002
    ):
        spans = memory_exporter.get_finished_spans()
        for span in spans:
            if span.kind != type:
                continue
            if span.name == name:
                return span
            if span.name.startswith(name):
                return span
        return None

    return callable


@pytest.fixture
def mcp_server_factory():
    """Factory fixture for creating FastMCP server instances."""
    # Import dependencies inside fixture to avoid import errors for tests that don't need it
    from fastmcp import FastMCP
    from mcp.server.fastmcp import Image
    from PIL import Image as PILImage

    def create_fastmcp_server(name: str = "TestServer"):
        mcp = FastMCP(name)

        @mcp.tool()
        def greet(name: str) -> str:
            return f"Hello, {name}!"

        @mcp.resource("config://version")
        def get_version():
            return "2.0.1"

        @mcp.tool()
        def get_image() -> Image:
            img = PILImage.new("RGB", (100, 100), color=(155, 0, 0))
            return Image(data=img.tobytes(), format="png")

        @mcp.resource("users://{user_id}/profile")
        def get_profile(user_id: int):
            # Fetch profile for user_id...
            return {"name": f"User {user_id}", "status": "active"}

        @mcp.prompt()
        def summarize_request(text: str) -> str:
            """Generate a prompt asking for a summary."""
            return f"Please summarize the following text:\n\n{text}"

        return mcp

    return create_fastmcp_server
