# G4.5 agent runtime discovery

```yaml
discovery:
  question: "Should Theo adopt the Claude Agent SDK, or is the current Anthropic client enough to study the needed agent primitives?"
  observed_facts:
    - "The repository already owns the session controller, SQLite event log, tutor schema, and replay boundary."
    - "The locked environment resolves anthropic==2.5.0."
    - "The installed Anthropic client exposes beta tool-runner primitives."
    - "The claude_agent_sdk package is not installed."
    - "The current tutor is a single structured model turn with no tool loop."
  assumptions:
    - "A direct loop or Python tool runner can be wrapped behind AgentPort without changing learner-state authority."
    - "The first useful experiment needs only concept retrieval, disambiguation, and next-activity proposal tools."
  unknowns:
    - "Whether the Claude Agent SDK adds enough replay, isolation, or lifecycle value to justify a process boundary."
    - "Whether a multi-step tutor interaction is measurably better than the direct tutor adapter."
  evidence:
    - "uv run --locked python dependency probe: anthropic_version=2.5.0, tool_runner=True, claude_agent_sdk_installed=False"
    - "G4 replay tests: advisory proposals and disambiguation requests remain outside mastery evidence."
  confidence: medium
  cheapest_next_probe: "Build one recorded AgentPort fixture with the direct loop and an optional tool-runner adapter; compare replay, authorization, latency, cost, and complexity."
  decision_owner: "project author"
  impact_if_wrong: "Choosing the SDK too early could duplicate session state and add process/runtime complexity; rejecting it too early could miss useful isolation and lifecycle primitives."
  decision: proceed
  contract_delta: "G4.5 remains a primitives lab, not an SDK adoption commitment. Keep the direct loop as baseline and make the SDK optional until measured benefits justify it."
```

The discovery closed the environment question and led to the bounded fixture
implementation. The framework choice remains intentionally conservative: one
`AgentPort`, three allow-listed tools, recorded traces, and a comparison note
were enough to study the primitives. No live provider or code execution was
required; the process-based SDK is deferred until isolation or lifecycle
evidence becomes material.
