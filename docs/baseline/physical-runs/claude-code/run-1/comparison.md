# Claude Code Physical Run Comparison

The physical invocation used the fixed HEAD `a371abbe75ffa0d0a3c92290e2bbf56a7ef54367` and `standard` mode. The source tree was clean before and after the run.

The physical report narrowed the core story to startup/command boundary, interactive session orchestration, and tools/MCP, with 28,495/31,323 declared lines (91.0%). The committed reference snapshot covers more peripheral modules and therefore reports a lower weighted result. The difference is an explicit bounded-scope choice; neither run claims full-repository coverage or runtime validation.

P2: pass. P4: not evaluated because this project received one physical invocation in this extension.
