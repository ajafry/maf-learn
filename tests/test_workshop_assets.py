from __future__ import annotations

import ast
import asyncio
from collections.abc import AsyncIterable
from pathlib import Path

import nbformat
import pytest
from agent_framework import (
    AgentResponseUpdate,
    Case,
    Content,
    Default,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    WorkflowEvent,
    handler,
)

from maf_foundry_hackathon.config import WorkshopConfigurationError, WorkshopSettings
from maf_foundry_hackathon.support_tools import (
    create_refund_request,
    create_return_request,
    lookup_order,
    search_support_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
EXPECTED_NOTEBOOKS = [
    "00_setup_and_readiness.ipynb",
    "01_your_first_agent.ipynb",
    "02_agents_with_tools.ipynb",
    "03_structured_triage.ipynb",
    "04_conversations_and_sessions.ipynb",
    "05_connect_to_a_foundry_agent.ipynb",
    "06_multi_agent_handoffs.ipynb",
    "07_remote_mcp_tools.ipynb",
    "08_graph_workflow_with_edges.ipynb",
    "09_human_in_the_loop_approval.ipynb",
]
ENVIRONMENT_VARIABLES = (
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_MODEL",
    "FOUNDRY_AGENT_NAME",
    "FOUNDRY_AGENT_VERSION",
)


@pytest.fixture(autouse=True)
def clear_workshop_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for variable in ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(variable, raising=False)


def test_settings_load_valid_non_secret_configuration(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "FOUNDRY_PROJECT_ENDPOINT=https://contoso.services.ai.azure.com/",
                "FOUNDRY_MODEL=support-model",
                "FOUNDRY_AGENT_NAME=support-agent",
                "FOUNDRY_AGENT_VERSION=3",
            ]
        ),
        encoding="utf-8",
    )

    settings = WorkshopSettings.from_env(env_file, require_agent=True)

    assert settings.project_endpoint == "https://contoso.services.ai.azure.com"
    assert settings.model == "support-model"
    assert settings.agent_name == "support-agent"
    assert settings.agent_version == "3"
    assert settings.safe_summary()["authentication"].startswith("DefaultAzureCredential")


def test_settings_reject_placeholders(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "FOUNDRY_PROJECT_ENDPOINT=https://YOUR-PROJECT.services.ai.azure.com\n"
        "FOUNDRY_MODEL=YOUR_MODEL_DEPLOYMENT_NAME\n",
        encoding="utf-8",
    )

    with pytest.raises(WorkshopConfigurationError, match="FOUNDRY_PROJECT_ENDPOINT, FOUNDRY_MODEL"):
        WorkshopSettings.from_env(env_file)


def test_existing_agent_lesson_requires_agent_name(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "FOUNDRY_PROJECT_ENDPOINT=https://contoso.services.ai.azure.com\nFOUNDRY_MODEL=support-model\n",
        encoding="utf-8",
    )

    with pytest.raises(WorkshopConfigurationError, match="FOUNDRY_AGENT_NAME"):
        WorkshopSettings.from_env(env_file, require_agent=True)


@pytest.mark.parametrize(
    ("tool", "arguments", "expected"),
    [
        (lookup_order, {"order_id": "ord-1001"}, "Contoso Noise-Canceling Headphones"),
        (lookup_order, {"order_id": "ORD-9999"}, "No order was found"),
        (search_support_policy, {"topic": "returns"}, "30 days"),
        (search_support_policy, {"topic": "warranty"}, "Available topics"),
        (create_return_request, {"order_id": "ORD-1001", "reason": "damaged"}, "RT-1001"),
        (create_refund_request, {"order_id": "ORD-1001", "reason": "damaged"}, "RF-1001"),
    ],
)
def test_support_tools_are_deterministic(tool: object, arguments: dict[str, str], expected: str) -> None:
    result = tool.func(**arguments)  # type: ignore[attr-defined]
    assert expected in result


def test_progressive_notebook_set_is_valid_and_clean() -> None:
    actual_notebooks = sorted(path.name for path in NOTEBOOK_DIR.glob("*.ipynb"))
    assert actual_notebooks == EXPECTED_NOTEBOOKS

    for notebook_name in EXPECTED_NOTEBOOKS:
        notebook_path = NOTEBOOK_DIR / notebook_name
        notebook = nbformat.read(notebook_path, as_version=4)
        nbformat.validate(notebook)

        markdown_cells = [cell for cell in notebook.cells if cell.cell_type == "markdown"]
        code_cells = [cell for cell in notebook.cells if cell.cell_type == "code"]

        assert len(markdown_cells) >= 5, f"{notebook_name} needs presenter documentation"
        assert len(code_cells) >= 3, f"{notebook_name} needs runnable demo code"
        assert all(cell.execution_count is None for cell in code_cells)
        assert all(not cell.outputs for cell in code_cells)

        for cell in code_cells:
            compile(
                cell.source,
                f"{notebook_path}:{cell.id}",
                "exec",
                flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT,
            )


def test_advanced_notebooks_cover_the_promised_patterns() -> None:
    expected_patterns = {
        "07_remote_mcp_tools.ipynb": (
            "get_mcp_tool",
            "https://learn.microsoft.com/api/mcp",
            "approval_mode",
        ),
        "08_graph_workflow_with_edges.ipynb": (
            "WorkflowBuilder",
            "add_edge",
            "add_switch_case_edge_group",
            "Case",
            "Default",
            "max_iterations",
        ),
        "09_human_in_the_loop_approval.ipynb": (
            'approval_mode="always_require"',
            "request_info",
            "function_approval_request",
            "to_function_approval_response",
            "responses=",
        ),
    }

    for notebook_name, patterns in expected_patterns.items():
        notebook = nbformat.read(NOTEBOOK_DIR / notebook_name, as_version=4)
        source = "\n".join(cell.source for cell in notebook.cells)
        missing = [pattern for pattern in patterns if pattern not in source]
        assert not missing, f"{notebook_name} is missing required patterns: {missing}"


def test_human_approval_notebook_handles_streaming_agent_updates(
    capsys: pytest.CaptureFixture[str],
) -> None:
    notebook = nbformat.read(NOTEBOOK_DIR / "09_human_in_the_loop_approval.ipynb", as_version=4)
    approval_cell = next(cell for cell in notebook.cells if cell.id == "approval-loop")
    namespace = {
        "AgentResponseUpdate": AgentResponseUpdate,
        "AsyncIterable": AsyncIterable,
        "Content": Content,
        "WorkflowEvent": WorkflowEvent,
    }
    exec(approval_cell.source, namespace)

    async def stream() -> AsyncIterable[WorkflowEvent[AgentResponseUpdate]]:
        yield WorkflowEvent(
            "output",
            AgentResponseUpdate(
                contents=[Content.from_text(text="Refund not issued.")],
                role="assistant",
            ),
        )

    responses = asyncio.run(namespace["inspect_workflow_events"](stream()))

    assert responses is None
    assert "[assistant]: Refund not issued." in capsys.readouterr().out


def test_explicit_workflow_graph_routes_and_completes() -> None:
    class Router(Executor):
        def __init__(self) -> None:
            super().__init__("router")

        @handler
        async def route(self, value: int, ctx: WorkflowContext[int]) -> None:
            await ctx.send_message(value)

    class EvenPath(Executor):
        def __init__(self) -> None:
            super().__init__("even")

        @handler
        async def finish(self, value: int, ctx: WorkflowContext[str]) -> None:
            await ctx.yield_output(f"even:{value}")

    class OddPath(Executor):
        def __init__(self) -> None:
            super().__init__("odd")

        @handler
        async def finish(self, value: int, ctx: WorkflowContext[str]) -> None:
            await ctx.yield_output(f"odd:{value}")

    async def run_workflow(value: int) -> list[str]:
        router = Router()
        even = EvenPath()
        odd = OddPath()
        workflow = (
            WorkflowBuilder(
                start_executor=router,
                name="offline-routing-test",
                max_iterations=5,
            )
            .add_switch_case_edge_group(
                router,
                [
                    Case(condition=lambda candidate: candidate % 2 == 0, target=even),
                    Default(target=odd),
                ],
            )
            .build()
        )

        return [
            event.data
            async for event in workflow.run(value, stream=True)
            if event.type == "output" and isinstance(event.data, str)
        ]

    assert asyncio.run(run_workflow(2)) == ["even:2"]
    assert asyncio.run(run_workflow(3)) == ["odd:3"]


def test_sample_environment_contains_no_credentials() -> None:
    sample = (PROJECT_ROOT / ".env.sample").read_text(encoding="utf-8")
    forbidden_names = ("API_KEY=", "CLIENT_SECRET=", "PASSWORD=", "ACCESS_TOKEN=")

    assert all(name not in sample.upper() for name in forbidden_names)
    assert "YOUR-PROJECT" in sample
    assert "YOUR_MODEL_DEPLOYMENT_NAME" in sample
