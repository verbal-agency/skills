# G4.5 agent runtime decision

## Comparison

| Dimension | Direct Messages loop | Anthropic Python tool runner | Claude Agent SDK |
|---|---|---|---|
| Replay boundary | Explicit trace and final response; easiest to persist | Works when tool calls/results are wrapped and captured | Not probed; process/session transcript would need an adapter |
| Tool authorization | Controller validates every call | Registry validates calls before execution | Requires a process gateway and controller validation |
| Local complexity | Low; baseline implementation | Moderate; SDK owns the loop but custom trace hooks remain | Higher; separate process and lifecycle boundary |
| Latency/cost | Not measured offline | Not measured offline | Not measured |
| Learning value | Makes the loop and authority boundary explicit | Exposes typed tools, loop, errors, and SDK behavior | Would add process isolation/lifecycle primitives |

## Decision

Keep `AgentPort` and the direct Messages loop as Theo's core runtime. Keep the
Anthropic Python tool-runner adapter as an optional, fixture-backed learning
implementation. Defer the process-based Claude Agent SDK and do not add it as a
dependency unless a later goal requires process isolation, long-running agent
lifecycle, or a separate code-execution worker.

This is a deliberate defer, not a claim that the SDK is ineffective. The local
fixture proves replay and authorization behavior but cannot measure live latency,
cost, or teaching lift. Those are required before making the SDK a production
choice.
