# HEARTBEAT CONTEXT

Agent: devsecops-expert
Role: devsecops-expert
Fleet: 10/10 online | Mode: full-autonomous | Phase: execution | Backend: claude

## ASSIGNED TASKS (1)

### Benchmark all target operations on LocalAI
- ID: 488cb9ae
- Status: inbox
- Priority: medium
- Agent: devsecops-expert
- Type: task
- Stage: unset
- Readiness: 0%
- Story Points: 3
- Description: Contexthermes-3b benchmarked for simple completion (1.2s warm). Need full benchmarks across all operations the inference router will handle.
Operations to BenchmarkOperation
Model
Expected Latency
Quality Gate
Simple completion
hermes-3b
&lt;2s
Follows instructions
Structured JSON output
hermes-3b
&lt;3s
Valid JSON, correct schema
HEARTBEAT_OK response
hermes-3b
&lt;2s
Correct format, no hallucination
Code completion
codellama
&lt;5s
Syntactically valid code
Multi-turn conversation
hermes
&lt;10
- Plane: dd0ee593

## ROLE DATA
### security_tasks (0)
### prs_needing_security_review (0)
