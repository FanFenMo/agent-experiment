# Architecture

The project is a small offline agent system built around a fixed rubric context and a deterministic tool registry.

```mermaid
flowchart LR
    UserTask["User task"] --> Agent["ExperimentAgent"]
    Prompt["prompts/system_prompt.md"] --> Agent
    Context["context/experiment2_rubric.md"] --> ReadContext["read_context"]
    Agent --> ReadContext
    ReadContext --> Extract["extract_rubric"]
    Extract --> Plan["plan_report"]
    Plan --> Reflect["draft_reflection"]
    Reflect --> Validate["validate_repository"]
    Validate --> Trace["JSON execution trace"]
    Trace --> Screens["report screenshots"]
```

The important design point is that the Agent does not hide its reasoning in an external service. Each step is represented as a tool call with explicit arguments and results, so the execution can be inspected in the terminal, in JSON, and in the final report screenshots.
