# Microsoft Agent Framework + Foundry Hackathon

A presenter-ready, progressive Python workshop for building agents with
[Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/) (MAF) and
[Microsoft Foundry](https://learn.microsoft.com/azure/ai-foundry/).

The lessons use a customer-support scenario and move from secure Foundry connectivity to tools,
structured output, conversation sessions, a pre-created Foundry agent, multi-agent handoffs,
remote MCP integration, explicit graph workflows, and human approval. Every lesson is a completed
Jupyter notebook with teaching notes, diagrams, discussion prompts, and production considerations.

## Intended audience

Participants should be comfortable reading Python and should have basic familiarity with LLMs.
The workshop does not assume prior experience with MAF.

## What participants will build

```text
Microsoft Entra identity
    -> Foundry model client
        -> application-owned MAF agent
            -> deterministic tools
            -> structured support tickets
            -> multi-turn sessions
        -> existing Foundry-managed agent
        -> multi-agent handoff workflow
        -> public remote MCP tools
        -> explicit executor-and-edge workflow
        -> human approval and workflow resume
```

All order lookups, policies, returns, and refunds in the workshop are simulated. The notebooks do
not modify a real customer or commerce system.

## Lesson map

| Lesson | Level | Topic | Full demo |
|---|---|---|---:|
| [00 - Setup and readiness](./notebooks/00_setup_and_readiness.ipynb) | Introductory | Configuration, Microsoft Entra ID, and `FoundryChatClient` | 5 min |
| [01 - Your first agent](./notebooks/01_your_first_agent.ipynb) | Beginner | `Agent`, instructions, complete responses, and streaming | 7 min |
| [02 - Agents with tools](./notebooks/02_agents_with_tools.ipynb) | Beginner/intermediate | Typed Python tools and grounded answers | 10 min |
| [03 - Structured triage](./notebooks/03_structured_triage.ipynb) | Intermediate | Pydantic response formats and deterministic routing | 8 min |
| [04 - Conversations and sessions](./notebooks/04_conversations_and_sessions.ipynb) | Intermediate | Multi-turn context and session serialization | 8 min |
| [05 - Existing Foundry agent](./notebooks/05_connect_to_a_foundry_agent.ipynb) | Intermediate | `FoundryAgent` with a Prompt Agent or Hosted Agent | 8 min |
| [06 - Multi-agent handoffs](./notebooks/06_multi_agent_handoffs.ipynb) | Advanced | Specialist agents, routing topology, and human input | 15 min |
| [07 - Remote MCP tools](./notebooks/07_remote_mcp_tools.ipynb) | Advanced | Public Microsoft Learn MCP server through Foundry | 10 min |
| [08 - Graph workflow with edges](./notebooks/08_graph_workflow_with_edges.ipynb) | Advanced | Typed executors, direct edges, branching, and workflow events | 15 min |
| [09 - Human approval](./notebooks/09_human_in_the_loop_approval.ipynb) | Advanced | Pause, inspect, approve or reject, and resume | 12 min |

Lessons 07-09 are optional advanced modules. They extend the workshop without making every topic
mandatory for a single presentation.

### Suggested one-hour presentation tracks

| Track | Lessons | Emphasis |
|---|---|---|
| Core agents | 00, 01, 02, 03, 04 | Agents, tools, typed results, and sessions |
| Workflow and orchestration | 00, 02, 08, 09, 06 | Explicit graphs, approval, and agent handoffs |
| Foundry integration | 00, 01, 05, 07, 09 | Managed agents, remote MCP, and governance |

Show the readiness result from Lesson 00 rather than performing setup live. Run the main path from
the selected lessons and summarize the production discussion cells. The complete ten-lesson
curriculum is intentionally longer than one hour.

## Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/)
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- A Microsoft Foundry project with:
  - an existing model deployment that supports the Responses API
  - participant access through Microsoft Entra ID
- For Lesson 05 only: an existing Prompt Agent or Hosted Agent in that project
- For Lesson 07: a model deployment that supports hosted MCP tools and service-side access to the
  public Microsoft Learn MCP endpoint

The project is configured to resolve Python packages through the required Microsoft package feed:

```text
https://packagefeedproxy.microsoft.io/pypi/simple
```

The checked-in [uv lock file](./uv.lock) makes workshop setup reproducible. The Microsoft Learn MCP
lesson requires no additional credential or environment variable.

## Setup

### 1. Install the environment

From the repository root:

```powershell
uv sync --all-groups
```

### 2. Create local configuration

PowerShell:

```powershell
Copy-Item .env.sample .env
```

Bash:

```bash
cp .env.sample .env
```

Edit `.env`:

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://YOUR-PROJECT.services.ai.azure.com
FOUNDRY_MODEL=YOUR_MODEL_DEPLOYMENT_NAME
FOUNDRY_AGENT_NAME=
FOUNDRY_AGENT_VERSION=
```

Use the **deployment name**, which may differ from the model's catalog name.

- `FOUNDRY_AGENT_NAME` is required only for Lesson 05.
- `FOUNDRY_AGENT_VERSION` is optional for a versioned Prompt Agent and is not required for a
  Hosted Agent.

The real `.env` is ignored by Git. [.env.sample](./.env.sample) contains placeholders only and is
safe to commit. Do not add API keys or client secrets to either file.

### 3. Sign in with Microsoft Entra ID

```powershell
az login
az account show
```

The notebooks use `DefaultAzureCredential`. During local development it can use the Azure CLI
identity. No API key is required. In Azure-hosted production applications, prefer managed identity.

### 4. Register and select the notebook kernel

```powershell
uv run python -m ipykernel install --user `
  --name maf-foundry-hackathon `
  --display-name "MAF Foundry Hackathon"
```

Then either open the notebooks in VS Code and choose **MAF Foundry Hackathon**, or start JupyterLab:

```powershell
uv run jupyter lab
```

## Repository layout

```text
.
|-- notebooks/                         # Progressive, presenter-ready lessons
|-- src/maf_foundry_hackathon/
|   |-- config.py                      # Secure environment and client helpers
|   `-- support_tools.py               # Deterministic simulated support tools
|-- tests/                             # Offline asset and helper validation
|-- .env.sample                        # Safe configuration template
|-- .gitignore
|-- pyproject.toml                     # uv project and package-feed configuration
`-- uv.lock                            # Reproducible dependency resolution
```

## Presenter guide

### Before the event

1. Run `uv sync --all-groups`.
2. Complete `.env` and run `az login`.
3. Execute Lesson 00 to confirm identity and configuration.
4. Execute one model call from Lesson 01.
5. If presenting Lesson 05, verify the agent name and optional version.
6. If presenting Lesson 07, run its MCP query once to verify model support and remote availability.
7. If presenting Lesson 09, rehearse both Approve and Reject paths.
8. Confirm the model has enough quota for the audience and presentation.
9. Restart the kernel and clear notebook outputs before distributing the repository.

### Teaching rhythm

Each notebook follows the same flow:

1. Explain the mental model.
2. Show the smallest relevant code surface.
3. Run one customer-support scenario.
4. Point out the application/agent security boundary.
5. Close with production considerations and a transition to the next lesson.

The notebooks are completed demos rather than exercises, so they can be presented quickly without
waiting for participants to fill in code.

### Important safety points to emphasize

- A model is not an authorization boundary.
- Consequential tool calls need user authorization and often explicit approval.
- Session or conversation identifiers must be stored in trusted state and bound to the caller.
- Structured output validates shape, not factual truth.
- A remote MCP server is a separate trust boundary; expose only necessary tools and data.
- Use the smallest tool set and handoff graph that satisfy the task.
- The `never_require` approval mode in simulated write tools is for a reproducible demo only.
- Human approval complements authorization inside a tool; it does not replace it.

## Choosing the right composition model

| Concept | Who controls the next action? | Best use |
|---|---|---|
| Python function tool | The model selects an application-provided function | Trusted local APIs and business operations |
| Hosted remote MCP tool | The model selects a capability exposed by a remote MCP server | Reusable external tool ecosystems |
| Explicit graph workflow | Code-defined edges and conditions route typed messages | Predictable pipelines and business processes |
| Handoff orchestration | Participating agents choose allowed transfers | Interactive specialist-to-specialist conversations |
| Human approval | An authenticated person authorizes a pending action | Consequential or policy-controlled operations |

These patterns can be combined. For example, an explicit graph can contain agents that use
function or MCP tools, while an approval request pauses execution before a sensitive tool runs.

## Development and validation

Run the complete offline validation:

```powershell
uv run ruff check .
uv run pytest
```

The tests validate notebook JSON, compile all code cells with top-level `await` support, ensure
committed notebooks contain no execution output, test configuration errors, and exercise the
deterministic support tools. They do not call Azure or a model, so they are safe for CI.

Model-backed notebook cells are intentionally not executed in automated tests because they require
participant identity, Foundry access, deployed resources, quota, and may incur cost.

## Troubleshooting

| Symptom | Resolution |
|---|---|
| Placeholder/configuration error | Replace the endpoint and model values in `.env` |
| `CredentialUnavailableError` | Run `az login`, confirm the intended tenant/subscription, and restart the kernel |
| HTTP 403 | Confirm the signed-in identity has access to the Foundry project |
| Model/deployment not found | Use the deployment name from the project, not only the base model name |
| Lesson 05 cannot find an agent | Verify `FOUNDRY_AGENT_NAME`, project, agent type, and optional version |
| Lesson 07 does not call MCP | Confirm the deployment supports hosted MCP tools and rerun with the documented query |
| Lesson 07 reports an MCP connection error | Confirm the public endpoint is available and reachable from the Foundry service |
| Lesson 08 reaches the iteration limit | Inspect the edge graph for an unintended cycle or an executor that repeatedly emits |
| Lesson 09 does not request approval | Run from a fresh workflow and use the provided refund prompt without changing the tool's approval mode |
| Notebook imports fail | Select the uv-created kernel or rerun the kernel registration command |
| Handoff ends early | Rerun the workflow cells to create fresh agents and use the scripted prompts unchanged |

## Key references

- [Microsoft Agent Framework overview](https://learn.microsoft.com/agent-framework/overview/)
- [Microsoft Foundry model provider](https://learn.microsoft.com/agent-framework/integrations/by-component/model-providers/microsoft-foundry)
- [Microsoft Foundry Agent Service integration](https://learn.microsoft.com/agent-framework/integrations/by-component/agent-services/foundry)
- [Conversations and memory](https://learn.microsoft.com/agent-framework/concepts/agents/conversations/)
- [Structured outputs](https://learn.microsoft.com/agent-framework/agents/structured-outputs)
- [Hosted MCP tools](https://learn.microsoft.com/agent-framework/agents/tools/hosted-mcp-tools)
- [Workflow edges](https://learn.microsoft.com/agent-framework/concepts/workflows/edges)
- [Human-in-the-loop workflows](https://learn.microsoft.com/agent-framework/workflows/human-in-the-loop)
- [Function tool approval](https://learn.microsoft.com/agent-framework/agents/tools/tool-approval)
- [Handoff orchestration](https://learn.microsoft.com/agent-framework/workflows/orchestrations/handoff)
- [Official Agent Framework Python samples](https://github.com/microsoft/agent-framework/tree/main/python/samples)